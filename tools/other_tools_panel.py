import bpy
from .. import shared_functions

class CDTOOLS_PT_UsefulToolsPanel(bpy.types.Panel):
    bl_label = "Useful tools"
    bl_idname = "VIEW3D_PT_useful_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('cdtools.add_vertex_groups_from_bones', text='Add Vertex Groups By Bones', icon="POSE_HLT")
        box = col.box()
        box.label(text="Description", icon="QUESTION")
        shared_functions.label_multiline(context=context,
                         text="Select object you want to add, select bones you want to add in pose mode and press it",
                         parent=box)
        
        col.separator()
        col.operator("cdtools.align_bones", icon="FILE_REFRESH", text="Align Bones Between Skeleton")
        box = col.box()
        box.label(text="Description", icon="QUESTION")
        shared_functions.label_multiline(context, text="mmd_skel is active, ref_skel is other selcted", parent=box)

class CDTOOLS_OT_AddVertexGroupsFromBones(bpy.types.Operator):
    """从选中的骨骼向目标网格添加对应的顶点组"""
    bl_idname = "cdtools.add_vertex_groups_from_bones"
    bl_label = "Add Vertex Groups from Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object:
            armature = context.object
            if armature.type != 'ARMATURE':
                self.report({'WARNING'}, "请选中一个骨骼对象")
                return {'CANCELLED'}

        # 获取选中的骨骼名字
        selected_bones = [bone.name for bone in context.selected_pose_bones]
        if not selected_bones:
            self.report({'WARNING'}, "请在姿势模式下选中骨骼")
            return {'CANCELLED'}

        # 假设目标网格是选中的另一个对象
        target_mesh = None
        for obj in context.selected_objects:
            if obj.type == 'MESH' and obj != armature:
                target_mesh = obj
                break

        if not target_mesh:
            self.report({'WARNING'}, "请同时选中一个网格对象")
            return {'CANCELLED'}

        # 添加对应的顶点组
        existing_groups = {vg.name for vg in target_mesh.vertex_groups}
        for bone_name in selected_bones:
            if bone_name not in existing_groups:
                target_mesh.vertex_groups.new(name=bone_name)

        self.report({'INFO'}, f"添加 {len(selected_bones)} 个顶点组")
        return {'FINISHED'}

class CDTOOLS_OT_AlignBonesOperator(bpy.types.Operator):
    bl_label = "Align bones"
    bl_idname = "cdtools.align_bones"

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

classes = {
    CDTOOLS_PT_UsefulToolsPanel,
    CDTOOLS_OT_AddVertexGroupsFromBones,
    CDTOOLS_OT_AlignBonesOperator,
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)