import bpy
from .. import shared_functions
from .. import lists

mapping_type = [
    ('MODE_Bone_Rename', "Bone Rename Mode", "Bone Rename Mode"),
    ('MODE_Vertex_Group_Rename', "Vertex Group Rename Mode", "Vertex Group Rename Mode"),
    ('MODE_Bone_Reparent', "Bone Reparent Mode", "Bone Reparent Mode"),
]

def rename_vertex_groups(mesh_obj, name_list, bone1_to_bone2):
    vertex_groups = mesh_obj.vertex_groups
    for item in name_list:
        if bone1_to_bone2:
            name = item.bone1
            newname = item.bone2
        else:
            name = item.bone2
            newname = item.bone1
        idx = vertex_groups.find(name)
        if idx != -1:
            vg = vertex_groups[idx]
            vg.name = newname
        else: #Not found
            #Do something
            pass

def rename_bones(armature_data, name_list, bone1_to_bone2):
    bpy.ops.object.mode_set(mode='EDIT')
    for item in name_list:
        if bone1_to_bone2:
            name = item.bone1
            newname = item.bone2
        else:
            name = item.bone2
            newname = item.bone1
        idx = armature_data.edit_bones.find(name)
        if idx != -1:
            bo = armature_data.edit_bones[idx]
            bo.name = newname
        else: #Not found
            #Do something
            pass

def reparent_bones(armature_data, name_list, bone1_to_bone2):
    for item in name_list:
        child_bone_name = item.bone1 if bone1_to_bone2 else item.bone2
        parent_bone_name = item.bone2 if bone1_to_bone2 else item.bone1

        child_bone = armature_data.edit_bones.get(child_bone_name)
        parent_bone = armature_data.edit_bones.get(parent_bone_name)
        
        if child_bone:
            if parent_bone:
                child_bone.parent = parent_bone
            else:
                child_bone.parent = None

class CDTOOLS_PairBonesGroupProperty(bpy.types.PropertyGroup):
    bone1: bpy.props.StringProperty(
    ) # type: ignore
    bone2: bpy.props.StringProperty(
    ) # type: ignore

class CDTOOLS_UL_MappingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            icon = 'GROUP_VERTEX' if context.scene.cdtools_mapping_mode == "MODE_Vertex_Group_Rename" else 'BONE_DATA'
            row = layout.row(align=True)
            row.prop(item, "bone1", icon=icon, text="")
            row.label(icon="ARROW_LEFTRIGHT")
            row.prop(item, "bone2", icon=icon, text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class CDTOOLS_PT_BoneMappingRenamePanel(bpy.types.Panel):
    bl_label = "Bones Rename Mapping"
    bl_idname = "VIEW3D_PT_bones_rename_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        main_col = layout.column(align=True)
        
        box = main_col.box()
        box.label(text="Bones Rename Tools", icon="SORTALPHA")
        box = main_col.box()
        box_main_col = box.column(align=True)
        box_main_col.prop(scene, "cdtools_mapping_mode", text="Mode")
        box_main_col.separator()
        row = box_main_col.row(align=True)
        temp_col = row.column(align=True)
        temp_col.template_list("CDTOOLS_UL_MappingList", "rename_mapping", scene, "cdtools_mapping_items", scene, "cdtools_mapping_index", rows=7)

        col = row.column(align=True)
        add_item_op = col.operator("cdtools_bones_pair.add_item", icon="ADD", text="")
        add_item_op.target_var = "cdtools_mapping_items"
        add_item_op.target_index = "cdtools_mapping_index"

        remove_item_op = col.operator("cdtools_bones_pair.remove_item", icon="REMOVE", text="")
        remove_item_op.target_var = "cdtools_mapping_items"
        remove_item_op.target_index = "cdtools_mapping_index"

        col.separator()

        default_op = col.operator("cdtools_bones_pair.load_from_default", icon="FILE_REFRESH", text="")
        default_op.target_var = "cdtools_mapping_items"
        default_op.target_index = "cdtools_mapping_index"
        default_op.target_default_list = "namelist"

        import_op = col.operator("cdtools_bones_pair.import_from_file", icon="IMPORT", text="")
        import_op.target_var = "cdtools_mapping_items"
        import_op.target_index = "cdtools_mapping_index"

        col.operator("cdtools_bones_pair.clear_mapping", icon="X", text="").target_var = "cdtools_mapping_items"

        col.separator()

        col.operator("cdtools_bones_pair.rename", icon="EVENT_RIGHT_ARROW", text="").bone1_to_bone2 = True
        col.operator("cdtools_bones_pair.rename", icon="EVENT_LEFT_ARROW", text="").bone1_to_bone2 = False

        box_main_col.prop(scene, "cdtools_rename_vertex_group_mode", text="Rename Vertex Group Mode")

        main_col.separator()
        box = main_col.box()
        box.label(text="Description", icon="QUESTION")
        box = main_col.box()
        shared_functions.label_multiline(context=context, 
                        text="A useful tool for batch bones rename, you can make your own txt file",
                        parent=box)

class CDTOOLS_OT_AddBonePairItem(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.add_item"
    bl_label = "Add mapping"
    target_var: bpy.props.StringProperty() # type: ignore
    target_index: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        target = getattr(scene, self.target_var, None)

        if target is not None and isinstance(target, bpy.types.bpy_prop_collection):
            target.add()
            if hasattr(scene, self.target_index):
                setattr(scene, self.target_index, len(target) - 1)

        return {'FINISHED'}
    
class CDTOOLS_OT_RemoveBonePairItem(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.remove_item"
    bl_label = "Remove mapping"
    target_var: bpy.props.StringProperty() # type: ignore
    target_index: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        target = getattr(scene, self.target_var, None)

        if target is not None and isinstance(target, bpy.types.bpy_prop_collection):
            if hasattr(scene, self.target_index):
                index = getattr(scene, self.target_index)
                target.remove(index)
                setattr(scene, self.target_index, max(0, index - 1))

        return {'FINISHED'}
    
class CDTOOLS_OT_LoadFromDefault(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.load_from_default"
    bl_label = "Load default mapping"
    target_var: bpy.props.StringProperty() # type: ignore
    target_index: bpy.props.StringProperty() # type: ignore
    target_default_list: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        target = getattr(scene, self.target_var, None)

        if target is not None and isinstance(target, bpy.types.bpy_prop_collection):
            target.clear()
            for bone1, bone2 in getattr(lists, self.target_default_list, None):
                item = target.add()
                item.bone1 = bone1
                item.bone2 = bone2
            if hasattr(scene, self.target_index):
                setattr(scene, self.target_index, len(scene.cdtools_mapping_items) - 1)

        return {'FINISHED'}

class CDTOOLS_OT_ClearMapping(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.clear_mapping"
    bl_label = "Clear current mappings"
    target_var: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        target = getattr(scene, self.target_var, None)

        if target is not None and isinstance(target, bpy.types.bpy_prop_collection):
            target.clear()

        return {'FINISHED'}

class CDTOOLS_OT_ImportFromFile(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.import_from_file"
    bl_label = "Import from file"

    target_var: bpy.props.StringProperty() # type: ignore
    target_index: bpy.props.StringProperty() # type: ignore

    # 声明一个字符串属性，用于存储文件路径
    filepath: bpy.props.StringProperty(
        name="File Path",
        description="选择要导入的文件",
        subtype='FILE_PATH'  # 使其成为一个文件路径
    ) # type: ignore

    def execute(self, context):
        scene = context.scene
        target_getVar = getattr(scene, self.target_var, None)
        if target_getVar is not None and isinstance(target_getVar, bpy.types.bpy_prop_collection):
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
                            item = target_getVar.add()
                            item.bone1 = name
                            item.bone2 = target

                if hasattr(scene, self.target_index):
                    setattr(scene, self.target_index, len(scene.cdtools_mapping_items) - 1)
                self.report({'INFO'}, "文件导入成功")
            except Exception as e:
                self.report({'ERROR'}, f"文件导入失败: {e}")

        return {'FINISHED'}
    
    # 打开文件浏览器
    def invoke(self, context, event):
        # 弹出文件浏览器，选择文件
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class CDTOOLS_OT_MappingOperation(bpy.types.Operator):
    bl_idname = "cdtools_bones_pair.rename"
    bl_label = "Rename bones"

    bone1_to_bone2: bpy.props.BoolProperty() # type: ignore
    def execute(self, context):
        scene = context.scene
        selected_obj = bpy.context.active_object

        if context.scene.cdtools_mapping_mode == "MODE_Bone_Rename":
            if selected_obj.type == 'ARMATURE':
                selected_armature = selected_obj
                selected_armature.select_set(True)
                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')
                armature = selected_armature.data
                rename_bones(armature_data=armature, name_list=scene.cdtools_mapping_items, bone1_to_bone2=self.bone1_to_bone2)
        elif context.scene.cdtools_mapping_mode == "MODE_Vertex_Group_Rename":
            rename_vertex_groups(mesh_obj=selected_obj, name_list=scene.cdtools_mapping_items, bone1_to_bone2=self.bone1_to_bone2)  
        elif context.scene.cdtools_mapping_mode == "MODE_Bone_Reparent":
            if selected_obj.type == 'ARMATURE':
                selected_armature = selected_obj
                selected_armature.select_set(True)
                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')
                armature = selected_armature.data
                for item in scene.cdtools_mapping_items:
                    reparent_bones(armature_data=armature, name_list=scene.cdtools_mapping_items, bone1_to_bone2=self.bone1_to_bone2)
        return{'FINISHED'}

# Op : Update selected object active vertex group
def SelectBoneUpdateFunction(self, context):
    if context.scene.cdtools_mapping_index < 0 or len(context.scene.cdtools_mapping_items) <= 0:
        return
    bone1_name = context.scene.cdtools_mapping_items[context.scene.cdtools_mapping_index].bone1
    bone2_name = context.scene.cdtools_mapping_items[context.scene.cdtools_mapping_index].bone2
    armature = bpy.context.object

    active_object = context.active_object
    if active_object and active_object.type == 'ARMATURE':
        if armature.mode == 'EDIT':
            eb = armature.data.edit_bones.get(bone1_name)
            if eb:
                armature.data.edit_bones.active = eb
            else:
                eb = armature.data.edit_bones.get(bone2_name)
                if eb:
                    armature.data.edit_bones.active = eb

        elif armature.mode == 'POSE':
            pb = armature.pose.bones.get(bone1_name)
            if pb:
                bpy.context.view_layer.objects.active = armature
                armature.data.bones.active = pb.bone
            else:
                pb = armature.pose.bones.get(bone2_name)
                if pb:
                    bpy.context.view_layer.objects.active = armature
                    armature.data.bones.active = pb.bone

classes = {
    CDTOOLS_PairBonesGroupProperty,

    CDTOOLS_UL_MappingList,

    CDTOOLS_PT_BoneMappingRenamePanel,

    CDTOOLS_OT_AddBonePairItem,
    CDTOOLS_OT_RemoveBonePairItem,
    CDTOOLS_OT_LoadFromDefault,
    CDTOOLS_OT_ClearMapping,
    CDTOOLS_OT_ImportFromFile,

    CDTOOLS_OT_MappingOperation,
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cdtools_mapping_mode = bpy.props.EnumProperty(name="Mapping Mode", description="Select mapping mode", items=mapping_type, default='MODE_Bone_Rename')

    bpy.types.Scene.cdtools_mapping_items = bpy.props.CollectionProperty(type=CDTOOLS_PairBonesGroupProperty)
    bpy.types.Scene.cdtools_mapping_index = bpy.props.IntProperty(default=0, update=SelectBoneUpdateFunction)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cdtools_mapping_mode

    del bpy.types.Scene.cdtools_mapping_items
    del bpy.types.Scene.cdtools_mapping_index