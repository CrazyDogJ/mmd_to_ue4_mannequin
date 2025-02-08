bl_info = {
    "name": "MMD to UE4 mannequin",
    "author": "CrazyDog",
    "version": (1, 0),
    "blender": (4, 0, 2),
    "location": "View3D > Tool Shelf > MMD to UE4",
    "description": "用于转换MMD模型到UE4小白人骨架标准",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

from typing import Set
import bpy
from bpy.types import Context
import mathutils
from . import functions
from . import lists
import textwrap

def _label_multiline(context, text, parent):
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)

bpy.types.Scene.arms_reverse = bpy.props.BoolProperty(name="Arm Reverse", default=False)

class bone_name_mapping(bpy.types.PropertyGroup):
    bone1: bpy.props.StringProperty(
    ) # type: ignore
    bone2: bpy.props.StringProperty(
    ) # type: ignore

class main_panel(bpy.types.Panel):
    bl_label = "To UE4 Execute"
    bl_idname = "To UE4 Execute"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        grid = col.grid_flow(row_major=True)
        row = grid.row(align=True)

        _label_multiline(context=context,
                        text='Click button after selecting MMD mesh',
                        parent=col)
        
        col.operator("cd_ue4_functions.translate_execute", text='Execute', icon="ARMATURE_DATA")

        _label_multiline(context=context,
                         text='If arm bones are reverse, just make below true.',
                         parent=col)

        col.prop(context.scene, "arms_reverse", text="Reverse Arm Roll")

class bone_edit_panel(bpy.types.Panel):
    bl_label = "Edit Bones"
    bl_idname = "Edit Bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        grid = col.grid_flow(row_major=True)
        row = grid.row(align=True)

        _label_multiline(context=context,
                         text="If some bones still not face correctly, use buttons below to adjust by yourself. These operation will set seletected bones's use_connect parameter to FALSE!",
                         parent=col)

        operator1 = col.operator('cd_ue4_functions.rotate', text='X Rotate 90')
        operator2 = col.operator('cd_ue4_functions.rotate', text='X Rotate -90')
        operator3 = col.operator('cd_ue4_functions.rotate', text='Y Rotate 90')
        operator4 = col.operator('cd_ue4_functions.rotate', text='Y Rotate -90')
        operator5 = col.operator('cd_ue4_functions.rotate', text='Z Rotate 90')
        operator6 = col.operator('cd_ue4_functions.rotate', text='Z Rotate -90')

        operator1.axis = "X"
        operator1.degree = 90
        
        operator2.axis = "X"
        operator2.degree = -90
        
        operator3.axis = "Y"
        operator3.degree = 90
        
        operator4.axis = "Y"
        operator4.degree = -90
        
        operator5.axis = "Z"
        operator5.degree = 90
        
        operator6.axis = "Z"
        operator6.degree = -90

class bone_pose_panel(bpy.types.Panel):
    bl_label = "Pose Bones"
    bl_idname = "Pose Bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        grid = col.grid_flow(row_major=True)
        row = grid.row(align=True)

        _label_multiline(context=context,
                         text="The button below says:'I can help you pose the model to ue4 mannequin after you finishing adjust bones in edit mode, but you can adjust them manully later'",
                         parent=col)
        col.operator('cd_ue4_functions.pose_model', text='Pose Model', icon="POSE_HLT")

class bone_name_mapping_panel(bpy.types.Panel):
    bl_label = "Bones Mapping"
    bl_idname = "Bones Mapping"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        grid = col.grid_flow(row_major=True)

        _label_multiline(context=context,
                         text="Bones rename mapping",
                         parent=col)
        
        scene = context.scene

        row = layout.row(align=True)
        row.template_list("RENAME_MAPPING_UL_items", "rename_mapping", scene, "mapping_items", scene, "mapping_index")

        col = row.column(align=True)
        col.operator("rename_mapping.add_item", icon="ADD", text="")
        col.operator("rename_mapping.remove_item", icon="REMOVE", text="")
        col.operator("rename_mapping.load_from_default", icon="FILE_REFRESH", text="")
        col.operator("rename_mapping.import_from_file", icon="IMPORT", text="")
        operator_1to2 = col.operator("rename_mapping.rename", icon="EVENT_RIGHT_ARROW", text="")
        operator_1to2.bone1_to_bone2 = True
        operator_2to1 = col.operator("rename_mapping.rename", icon="EVENT_LEFT_ARROW", text="")
        operator_2to1.bone1_to_bone2 = False

        col.operator("rename_mapping.align_bones", icon="FILE_REFRESH", text="")

        if scene.mapping_items and scene.mapping_index < len(scene.mapping_items):
            item = scene.mapping_items[scene.mapping_index]
            layout.prop(item, "bone1", text="Bone 1")
            layout.prop(item, "bone2", text="Bone 2")

class RENAME_MAPPING_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.bone1, icon='BONE_DATA')
            row.label(icon="ARROW_LEFTRIGHT")
            row.label(text=item.bone2, icon='BONE_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class RENAME_MAPPING_OT_AddItem(bpy.types.Operator):
    bl_idname = "rename_mapping.add_item"
    bl_label = "Add mapping"

    def execute(self, context):
        scene = context.scene
        scene.mapping_items.add()
        scene.mapping_index = len(scene.mapping_items) - 1
        return {'FINISHED'}
    
class RENAME_MAPPING_OT_RemoveItem(bpy.types.Operator):
    bl_idname = "rename_mapping.remove_item"
    bl_label = "Remove mapping"

    def execute(self, context):
        scene = context.scene
        index = scene.mapping_index

        if scene.mapping_items:
            scene.mapping_items.remove(index)
            scene.mapping_index = max(0, index - 1)
        return {'FINISHED'}

class load_from_default(bpy.types.Operator):
    bl_idname = "rename_mapping.load_from_default"
    bl_label = "Load default mapping"

    def execute(self, context):
        scene = context.scene

        scene.mapping_items.clear()
        for bone1, bone2 in lists.namelist:
            item = scene.mapping_items.add()
            item.bone1 = bone1
            item.bone2 = bone2

        scene.mapping_index = len(scene.mapping_items) - 1
            
        return {'FINISHED'}

class RENAME_MAPPING_OT_ImportFromFile(bpy.types.Operator):
    bl_idname = "rename_mapping.import_from_file"
    bl_label = "Import from file"

    # 声明一个字符串属性，用于存储文件路径
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="选择要导入的文件",
        subtype='FILE_PATH'  # 使其成为一个文件路径
    ) # type: ignore

    def execute(self, context):
        scene = context.scene

        # 获取文件路径
        file_path = self.filepath

        # 如果文件路径为空，直接返回
        if not file_path:
            self.report({'ERROR'}, "未选择文件")
            return {'CANCELLED'}

        # 假设文件格式为：每行 "original_name,target_name"
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if line.strip() and not line.startswith("#"):
                        name, target = line.strip().split(',')
                        item = scene.mapping_items.add()
                        item.bone1 = name
                        item.bone2 = target

            scene.mapping_index = len(scene.mapping_items) - 1
            self.report({'INFO'}, "文件导入成功")
        except Exception as e:
            self.report({'ERROR'}, f"文件导入失败: {e}")
        
        return {'FINISHED'}

    # 打开文件浏览器
    def invoke(self, context, event):
        # 弹出文件浏览器，选择文件
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENAME_BY_MAPPING(bpy.types.Operator):
    bl_idname = "rename_mapping.rename"
    bl_label = "Rename bones"

    bone1_to_bone2: bpy.props.BoolProperty() # type: ignore
    def execute(self, context):
        scene = context.scene
        selected_obj = bpy.context.active_object

        if selected_obj.type == 'ARMATURE':
            selected_armature = selected_obj
            selected_armature.select_set(True)
            bpy.context.view_layer.objects.active = selected_armature
            bpy.ops.object.mode_set(mode='EDIT')
            armature = selected_armature.data
            for item in scene.mapping_items:
                if self.bone1_to_bone2:
                    name = item.bone1
                    newname = item.bone2
                else:
                    name = item.bone2
                    newname = item.bone1

                idx = armature.edit_bones.find(name)
                if idx != -1:
                    bo = armature.edit_bones[idx]
                    bo.name = newname
                else: #Not found
                    #Do something
                    pass
        return{'FINISHED'}

class ALIGN_BONES(bpy.types.Operator):
    bl_label = "Align bones"
    bl_idname = "rename_mapping.align_bones"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        
        if len(selected_objects) == 2:
            try:
                other_obj = next(obj for obj in selected_objects if obj != active_object)
            except StopIteration:
                other_obj = None  # 处理未找到的情况
            
            if active_object.type == 'ARMATURE' and other_obj.type == 'ARMATURE':
                mmd_skeleton = active_object
                ref_skeleton = other_obj

                ##self.report({'INFO'}, str(mmd_skeleton))

                bpy.ops.object.mode_set(mode='EDIT')
                for item in context.scene.mapping_items:
                    find_bone1 = mmd_skeleton.data.edit_bones.get(item.bone1)
                    find_bone2 = ref_skeleton.data.edit_bones.get(item.bone2)
                    
                    if find_bone1 is not None and find_bone2 is not None:
                        find_bone1.head = find_bone2.head
                        if len(find_bone2.children) > 0:
                            find_bone2_child = find_bone2.children[0]
                            if find_bone2_child is not None:
                                find_bone1.tail = find_bone2_child.head
                        else:
                            find_bone1.matrix = find_bone2.matrix
                            find_bone1.length = 1.0
        
        return {'FINISHED'}

class execute_functions(bpy.types.Operator):
    bl_label = "Execute Functions"
    bl_idname = "cd_ue4_functions.translate_execute"

    def execute(self, context):

        selected_obj = bpy.context.active_object

        if selected_obj.type == 'MESH':
            # 首先将D骨骼顶点组权重合并到原骨骼中
            for name, newname in lists.namelist_1:
                pb_new = selected_obj.vertex_groups.get(newname)
                pb_old = selected_obj.vertex_groups.get(name)
                # Invalid
                if pb_new is None or pb_old is None:
                    continue
                # Valid
                functions.merge_vg(name, newname, newname, selected_obj)

            if selected_obj.parent.type == 'ARMATURE':
                selected_armature = selected_obj.parent
                selected_armature.select_set(True)
                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')
                armature = selected_armature.data
                # Set root bone name
                selected_armature.name = "root"
                armature.name = "root"

                # Execute rename
                functions.rename_bones(armature, lists.namelist)
                # Remove empty weight vertex groups
                functions.delete_empty_vertex_groups(selected_obj.parent, selected_obj, lists.bones_ignore)

                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')

                # 将所有骨骼的连接属性设为false
                for bone in armature.edit_bones:
                    bone.use_connect = False

                # Rotate spine bones
                for name, axis, degree in list.spine_rot_list:
                    functions.rotate_bone_local_axis_edit_mode(armature, name, axis, degree)

                # Execute arm reverse
                mul = 1
                mul_2 = 1
                if bpy.context.scene.arms_reverse:
                    mul = -1
                    mul_2 = 0

                for name in lists.bones_arm_l:
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Z', -90 * mul)
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Y', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "hand_l", 'Z', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "hand_l", 'X', 90 * mul)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_01_l", 'Z', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_01_l", 'X', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_02_l", 'Z', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_02_l", 'X', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_03_l", 'Z', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_03_l", 'X', 180 * mul_2)

                for name in lists.namelist_finger_l:
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Z', 90)
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'X', 90 * mul)

                for name in lists.bones_arm_r:
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Z', 90 * mul)
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Y', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "hand_r", 'Z', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "hand_r", 'X', 90 * mul)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_01_r", 'Z', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_01_r", 'X', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_02_r", 'Z', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_02_r", 'X', 180 * mul_2)

                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_03_r", 'Z', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thumb_03_r", 'X', 180 * mul_2)

                for name in lists.namelist_finger_r:
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'Z', -90)
                    functions.rotate_bone_local_axis_edit_mode(armature, name, 'X', 90 * mul)

                functions.rotate_bone_local_axis_edit_mode(armature, "thigh_l", 'X', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thigh_l", 'Y', -90)
    
                functions.rotate_bone_local_axis_edit_mode(armature, "calf_l", 'X', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "calf_l", 'Y', -90)
                
                functions.rotate_bone_local_axis_edit_mode(armature, "thigh_r", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "thigh_r", 'Y', -90)
                
                functions.rotate_bone_local_axis_edit_mode(armature, "calf_r", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "calf_r", 'Y', -90)
                
                functions.set_bone_direction(armature, "foot_l", (0,1,0))
                functions.rotate_bone_local_axis_edit_mode(armature, "foot_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "foot_r", (0,-1,0))
                functions.rotate_bone_local_axis_edit_mode(armature, "foot_r", 'Y', 90)
                
                functions.set_bone_direction(armature, "ik_foot_l", (0,1,0))
                functions.rotate_bone_local_axis_edit_mode(armature, "ik_foot_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "ik_foot_r", (0,-1,0))
                functions.rotate_bone_local_axis_edit_mode(armature, "ik_foot_r", 'Y', 90)
                
                functions.set_bone_direction(armature, "ball_l", (0,0,1))
                functions.rotate_bone_local_axis_edit_mode(armature, "ball_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "ball_r", (0,0,-1))
                functions.rotate_bone_local_axis_edit_mode(armature, "ball_r", 'Y', -90)

                # Add new ik bones
                functions.add_new_bone(armature, "ik_foot_root", (0,0,0), (0,1,0))
                functions.add_new_bone(armature, "ik_hand_root", (0,0,0), (0,1,0))

                functions.add_new_bone(armature, "ik_hand_gun", armature.edit_bones["hand_r"].head, armature.edit_bones["hand_r"].tail)
                functions.add_new_bone(armature, "ik_hand_l", armature.edit_bones["hand_l"].head, armature.edit_bones["hand_l"].tail)
                functions.add_new_bone(armature, "ik_hand_r", armature.edit_bones["hand_r"].head, armature.edit_bones["hand_r"].tail)
                armature.edit_bones["ik_hand_gun"].roll = armature.edit_bones["hand_r"].roll
                armature.edit_bones["ik_hand_l"].roll = armature.edit_bones["hand_l"].roll
                armature.edit_bones["ik_hand_r"].roll = armature.edit_bones["hand_r"].roll

                for child_name , parent_name in lists.reparent_list:
                    functions.bind_bone_to_parent(armature, child_name, parent_name)
                
        return{'FINISHED'}

class bone_rotate_execute(bpy.types.Operator):
    bl_label = "Rotate Bones"
    bl_idname = "cd_ue4_functions.rotate"

    axis: bpy.props.StringProperty() # type: ignore
    degree: bpy.props.FloatProperty() # type: ignore

    def execute(self, context):
        # 检查当前编辑的对象是否是一个骨骼
        if bpy.context.object and bpy.context.object.type == 'ARMATURE':
            # 获取当前编辑的对象（应该是一个armature）
            obj = bpy.context.edit_object

            # 获取选中的骨骼
            selected_bones = [bone for bone in obj.data.edit_bones if bone.select]

            # 输出选中的骨骼名称
            for bone in selected_bones:
                bone.use_connect = False
                functions.rotate_bone_local_axis_edit_mode(obj.data, bone.name, self.axis, self.degree)
        else:
            print("当前对象不是一个骨骼或者不在编辑模式下。")

        bpy.ops.wm.redraw_timer()
        return{'FINISHED'}

class pose_model(bpy.types.Operator):
    bl_label = "Pose Model"
    bl_idname = "cd_ue4_functions.pose_model"

    def execute(self, context):
        # 检查当前编辑的对象是否是一个骨骼
        if bpy.context.object and bpy.context.object.type == 'ARMATURE':
            # 获取当前编辑的对象（应该是一个armature）
            obj = bpy.context.object
            bpy.ops.object.mode_set(mode='POSE')

            constraint_list = {
                ("ik_foot_l", "foot_l"),
                ("ik_foot_r", "foot_r"),
                ("ik_hand_l", "hand_l"),
                ("ik_hand_r", "hand_r"),
                ("ik_hand_gun", "hand_r"),
            }
            for ik_name, bone_name in constraint_list:
                bone = obj.pose.bones.get(ik_name)
                if (bone):
                    constraint = bone.constraints.new(type='COPY_TRANSFORMS')
                    # 在修饰器属性中设置目标和目标空间等属性
                    constraint.target = bpy.data.objects[obj.name]  # 替换成你要复制变换的目标对象的名称
                    constraint.subtarget = bone_name  # 替换成你要复制变换的目标骨骼的名称
                    constraint.target_space = 'WORLD'
                    constraint.owner_space = 'WORLD'
                    constraint.influence = 1.0  # 设置影响度

            for name, axis, angle in lists.pose_rot_list:
                functions.rotate_bone_local_axis_pose_mode(obj, name, axis, angle)
        return{'FINISHED'}

def register():
    bpy.utils.register_class(execute_functions)
    bpy.utils.register_class(bone_rotate_execute)
    bpy.utils.register_class(pose_model)
    bpy.utils.register_class(main_panel)
    bpy.utils.register_class(bone_edit_panel)
    bpy.utils.register_class(bone_pose_panel)
    bpy.utils.register_class(bone_name_mapping_panel)
    bpy.utils.register_class(bone_name_mapping)
    bpy.utils.register_class(RENAME_MAPPING_OT_AddItem)
    bpy.utils.register_class(RENAME_MAPPING_OT_RemoveItem)
    bpy.utils.register_class(RENAME_MAPPING_UL_items)
    bpy.utils.register_class(load_from_default)
    bpy.utils.register_class(RENAME_MAPPING_OT_ImportFromFile)
    bpy.utils.register_class(RENAME_BY_MAPPING)
    bpy.utils.register_class(ALIGN_BONES)
    bpy.types.Scene.mapping_items = bpy.props.CollectionProperty(type=bone_name_mapping)
    bpy.types.Scene.mapping_index = bpy.props.IntProperty(default=0)
def unregister():
    bpy.utils.unregister_class(main_panel)
    bpy.utils.unregister_class(bone_edit_panel)
    bpy.utils.unregister_class(bone_pose_panel)
    bpy.utils.unregister_class(execute_functions)
    bpy.utils.unregister_class(bone_rotate_execute)
    bpy.utils.unregister_class(pose_model)
    bpy.utils.unregister_class(bone_name_mapping_panel)
    bpy.utils.unregister_class(bone_name_mapping)
    bpy.utils.unregister_class(RENAME_MAPPING_OT_AddItem)
    bpy.utils.unregister_class(RENAME_MAPPING_OT_RemoveItem)
    bpy.utils.unregister_class(RENAME_MAPPING_UL_items)
    bpy.utils.unregister_class(load_from_default)
    bpy.utils.unregister_class(RENAME_MAPPING_OT_ImportFromFile)
    bpy.utils.unregister_class(RENAME_BY_MAPPING)
    bpy.utils.unregister_class(ALIGN_BONES)
    del bpy.types.Scene.mapping_items
    del bpy.types.Scene.mapping_index

if __name__ == "__main__":
    register()