"""Blender 4.x/5.x: build a connected Y-axis control rig for an X-axis rig.

Integration: register DCC_OT_build_blender_rig and add
layout.operator('dcc.build_blender_rig') to your own panel.
Builds from REST data, not the current pose. Ctrl-Z undoes the operation.
"""

import bpy
from mathutils import Matrix, Vector

TAG = '_dcc_y_control_rig'

# Exact, case-sensitive bone names. Edit these lists for your skeleton.
# Preserve REST orientation; these controls can still be rotated manually.
KEEP_ORIENTATION_BLACKLIST = [
    'ValveBiped.Bip01_Pelvis'
    ]
# Keep parenting, but never enable Connected for these children.
DISCONNECT_BLACKLIST = [
    'ValveBiped.Bip01_L_Thigh', 
    'ValveBiped.Bip01_R_Thigh', 
    'ValveBiped.Bip01_L_Clavicle', 
    'ValveBiped.Bip01_R_Clavicle',
    ]
DISCONNECT_PARENT_BLACKLIST = [
    "ValveBiped.Bip01_Head1",
    "ValveBiped.Bip01_R_Hand",
    "ValveBiped.Bip01_L_Hand"
]


def build_blender_rig(context, source, keep_orientation=None, disconnect=None):
    """Return a new control object. Requires Object mode and a local armature.

    Original bone rest matrices and mesh bindings are preserved. Original
    connected flags are disabled so Copy Location can place every joint.
    Existing pose constraints are muted, not removed. No animation is baked.
    """
    if context.mode != 'OBJECT':
        raise ValueError('请在物体模式调用构建函数。')
    if source.library or source.data.library or source.override_library:
        raise ValueError('请先将骨架转为本地可编辑对象。')
    if source.data.users > 1:
        raise ValueError('骨架数据被多个对象共享，请先将骨架数据设为单用户。')
    if source.get(TAG):
        raise ValueError('请选择原始骨架，不要选择生成的控制骨架。')
    for pb in source.pose.bones:
        if any(getattr(c, 'target', None) and c.target.get(TAG)
               for c in pb.constraints):
            raise ValueError('该骨架已绑定控制骨架；请撤销上次构建后重试。')

    keep_orientation = set(KEEP_ORIENTATION_BLACKLIST if keep_orientation is None else keep_orientation)
    disconnect = set(DISCONNECT_BLACKLIST if disconnect is None else disconnect)
    # Preserve the exact count. Isolated bones are copied without processing.
    bones = list(source.data.bones)
    isolated = {b.name for b in bones if not b.parent and not b.children}
    keep_orientation |= isolated
    if not bones:
        raise ValueError('原骨架没有骨骼。')
    if source.data.pose_position != 'POSE':
        raise ValueError('请先将原骨架切换为 Pose Position（姿态位置）。')
    world = source.matrix_world.copy()
    axes = world.to_3x3()
    lengths = [axes.col[i].length for i in range(3)]
    if (min(lengths) < 1e-8 or axes.determinant() <= 0 or
            max(lengths) - min(lengths) > max(lengths) * 1e-5 or
            any(abs(axes.col[i].dot(axes.col[j])) > max(lengths)**2 * 1e-5
                for i, j in ((0, 1), (0, 2), (1, 2)))):
        raise ValueError('原骨架存在非均匀缩放、负缩放或剪切；请先规范物体变换。')
    bone_names = {b.name for b in bones}
    if any((pb.scale - Vector((1, 1, 1))).length > 1e-5
           for pb in source.pose.bones if pb.name in bone_names):
        raise ValueError('此工具用于旋转骨架，请先清除原骨骼的姿态缩放。')

    info = {b.name: {
        'head': b.head_local.copy(),
        'tail': b.tail_local.copy(),
        'matrix': b.matrix_local.copy(),
        'x': b.matrix_local.to_3x3().col[0].normalized(),
        'z': b.matrix_local.to_3x3().col[2].normalized(),
        'length': b.length,
        'parent': b.parent.name if b.parent else None,
        'children': [c.name for c in b.children],
        'connected': b.use_connect,
    } for b in bones}
    extent = max((d['head'].length for d in info.values()), default=1.0)
    eps = max(1e-7, extent * 1e-8)
    primary = {}
    for name, d in info.items():
        if name in keep_orientation:
            primary[name] = None
            continue
        candidates = [n for n in d['children']
                      if n not in disconnect
                      and info[n]['parent'] not in DISCONNECT_PARENT_BLACKLIST
                      and (info[n]['head'] - d['head']).length > eps]
        # Optional explicit override on ORIGINAL bone custom properties.
        override = source.data.bones[name].get('dcc_primary_child', '')
        if override and override not in candidates:
            raise ValueError(f'{name}: dcc_primary_child 必须是不同位置、且不在断连黑名单中的直接子骨骼。')
        primary[name] = override or (min(
            candidates,
            key=lambda n: (-(info[n]['head'] - d['head']).normalized().dot(d['x']),
                           -(info[n]['head'] - d['head']).length, n),
        ) if candidates else None)

    data = bpy.data.armatures.new(source.name + '_Blender')
    rig = bpy.data.objects.new(source.name + '_Blender', data)
    collection = source.users_collection[0] if source.users_collection else context.collection
    collection.objects.link(rig)
    rig.matrix_world = world
    rig.show_in_front = True
    rig[TAG] = True
    rig['dcc_source_name'] = source.name
    created_constraints, muted = [], []
    old_selected = list(context.selected_objects)
    try:
        for obj in old_selected:
            obj.select_set(False)
        rig.select_set(True)
        context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        eb = data.edit_bones
        # Create all user-facing bones first to preserve original names.
        for name, d in info.items():
            bone = eb.new(name)
            bone.head = d['head']
            child = primary[name]
            if name in keep_orientation:
                bone.tail = d['tail']
                bone.matrix = d['matrix']
                bone.length = d['length']
            else:
                bone.tail = (info[child]['head'] if child else
                             d['head'] + d['x'] * max(d['length'], eps * 100))
                bone.align_roll(d['z'])
            bone.use_deform = False
            bone['dcc_source_bone'] = name
            bone['dcc_primary_child'] = child or ''
        for name, d in info.items():
            if not d['parent']:
                continue
            bone, parent = eb[name], eb[d['parent']]
            bone.parent = parent
            bone.use_connect = (bone.parent.name not in DISCONNECT_PARENT_BLACKLIST and
                                name not in disconnect and
                                (bone.head - parent.tail).length <= eps)
        bpy.ops.object.mode_set(mode='OBJECT')
        assert len(data.bones) == len(source.data.bones), '骨骼数量不一致'
        for name in info:
            pb = rig.pose.bones[name]
            pb.rotation_mode = 'QUATERNION'
            pb.lock_scale = (True, True, True)
            if data.bones[name].use_connect:
                pb.lock_location = (True, True, True)

        # Copy Location cannot reposition connected bones. Disconnect flags
        # only; head/tail/rest matrices and original parenting remain intact.
        context.view_layer.objects.active = source
        source.select_set(True)
        rig.select_set(False)
        bpy.ops.object.mode_set(mode='EDIT')
        for name in info:
            if name not in isolated:
                source.data.edit_bones[name].use_connect = False
        bpy.ops.object.mode_set(mode='OBJECT')

        def constraint(pb, kind, target_bone, label):
            c = pb.constraints.new(kind)
            created_constraints.append((pb, c))
            c.name = 'DCC Blender | ' + label
            c.target, c.subtarget = rig, target_bone
            c.owner_space = c.target_space = 'WORLD'
            return c

        for name in info:
            if name in isolated:
                continue
            pb = source.pose.bones[name]
            for c in pb.constraints:
                muted.append((c, c.mute))
                c.mute = True
            constraint(pb, 'COPY_LOCATION', name, 'Joint')
            if name in keep_orientation:
                c = constraint(pb, 'COPY_ROTATION', name, 'Preserve Rest Orientation')
                c.mix_mode = 'REPLACE'
            else:
                # Same-bone tail supplies +Y; its Z supplies twist. No helper
                # bones or objects, and no dependency on source child bones.
                c = constraint(pb, 'TRACK_TO', name, 'Y to X + Twist')
                c.track_axis = 'TRACK_X'
                c.up_axis = 'UP_Z'
                c.use_target_z = True
                c.head_tail = 1.0
        source.select_set(False)
        rig.select_set(True)
        context.view_layer.objects.active = rig
        context.view_layer.update()
        bpy.ops.object.mode_set(mode='POSE')
        return rig
    except Exception:
        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for pb, c in reversed(created_constraints):
            pb.constraints.remove(c)
        for c, mute in muted:
            c.mute = mute
        context.view_layer.objects.active = source
        source.select_set(True)
        rig.select_set(False)
        bpy.ops.object.mode_set(mode='EDIT')
        for name, d in info.items():
            source.data.edit_bones[name].use_connect = d['connected']
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.data.objects.remove(rig, do_unlink=True)
        bpy.data.armatures.remove(data)
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in old_selected:
            obj.select_set(True)
        context.view_layer.objects.active = source
        raise


class DCC_OT_build_blender_rig(bpy.types.Operator):
    bl_idname = 'dcc.build_blender_rig'
    bl_label = '生成 Blender 控制骨架'
    bl_description = '从静止骨架生成连通的 Y 轴控制骨架，并约束原骨架的 X 轴'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'ARMATURE'
                and context.mode in {'OBJECT', 'POSE'})

    def execute(self, context):
        source = context.object
        old_mode = source.mode
        try:
            if old_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            rig = build_blender_rig(context, source)
        except Exception as exc:
            if context.object == source and source.mode != old_mode:
                bpy.ops.object.mode_set(mode=old_mode)
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f'已生成 {rig.name}；原约束已静音；Ctrl-Z 可撤销')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(DCC_OT_build_blender_rig)

def unregister():
    bpy.utils.unregister_class(DCC_OT_build_blender_rig)
