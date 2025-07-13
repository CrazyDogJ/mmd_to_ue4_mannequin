import bpy
from . import shared_functions
from . import lists

class bone_name_mapping(bpy.types.PropertyGroup):
    bone1: bpy.props.StringProperty(
    ) # type: ignore
    bone2: bpy.props.StringProperty(
    ) # type: ignore

class VIEW3D_PT_bone_name_mapping_panel(bpy.types.Panel):
    bl_label = "Bones Rename Mapping"
    bl_idname = "VIEW3D_PT_bones_rename_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        main_col = layout.column(align=True)
        
        box = main_col.box()
        box.label(text="Main Rename Tools", icon="SORTALPHA")
        box = main_col.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.template_list("RENAME_MAPPING_UL_items", "rename_mapping", scene, "mapping_items", scene, "mapping_index", rows=7)
        col = row.column(align=True)
        col.operator("rename_mapping.add_item", icon="ADD", text="")
        col.operator("rename_mapping.remove_item", icon="REMOVE", text="")
        col.separator()
        col.operator("rename_mapping.load_from_default", icon="FILE_REFRESH", text="")
        col.operator("rename_mapping.import_from_file", icon="IMPORT", text="")
        col.operator("rename_mapping.clear_mappings", icon="X", text="")
        col.separator()
        col.operator("rename_mapping.rename", icon="EVENT_RIGHT_ARROW", text="").bone1_to_bone2 = True
        col.operator("rename_mapping.rename", icon="EVENT_LEFT_ARROW", text="").bone1_to_bone2 = False

        main_col.separator()
        box = main_col.box()
        box.label(text="Additional Tools", icon="TOOL_SETTINGS")
        box = main_col.box()
        box.operator("rename_mapping.align_bones", icon="FILE_REFRESH", text="Align Bones Between Skeleton")

        if scene.mapping_items and scene.mapping_index < len(scene.mapping_items):
            item = scene.mapping_items[scene.mapping_index]
            layout.prop(item, "bone1", text="Bone 1")
            layout.prop(item, "bone2", text="Bone 2")

        main_col.separator()
        box = main_col.box()
        box.label(text="Description", icon="QUESTION")
        box = main_col.box()
        shared_functions.label_multiline(context=context, 
                        text="A useful tool for batch rename, you can make your own rename txt file",
                        parent=box)

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

class clear_mappings(bpy.types.Operator):
    bl_idname = "rename_mapping.clear_mappings"
    bl_label = "Clear current mappings"

    def execute(self, context):
        scene = context.scene
        scene.mapping_items.clear()

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

classes = {
    VIEW3D_PT_bone_name_mapping_panel,
    bone_name_mapping,
    RENAME_MAPPING_OT_AddItem,
    RENAME_MAPPING_OT_RemoveItem,
    RENAME_MAPPING_UL_items,
    load_from_default,
    clear_mappings,
    RENAME_MAPPING_OT_ImportFromFile,
    RENAME_BY_MAPPING,
    ALIGN_BONES,
}

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mapping_items = bpy.props.CollectionProperty(type=bone_name_mapping)
    bpy.types.Scene.mapping_index = bpy.props.IntProperty(default=0)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.mapping_items
    del bpy.types.Scene.mapping_index