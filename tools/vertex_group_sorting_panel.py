import bpy
from .. import shared_functions

def export_list_to_txt(filepath, string_list):
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in string_list:
            f.write(item + '\n')  # 每个字符串占一行

def import_list_from_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]  # 去除换行和空行

# 每项的数据结构
class CDTOOLS_VertexGroupGroupProperty(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name") # type: ignore
    selected: bpy.props.BoolProperty(name="selected", default=False) # type: ignore

# 列表UI
class CDTOOLS_UL_VertexGroupItemList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "selected", text="")
            split = layout.split(factor=0.1)
            split.label(text=str(index))
            split.label(icon="GROUP_VERTEX", text=item.name)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

# 面板
class CDTOOLS_PT_VertexGroupListPanel(bpy.types.Panel):
    bl_label = "Vertex Groups Sort List"
    bl_idname = "VIEW3D_PT_VertexGroupListPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        main_col = layout.column(align=True)
        box = main_col.box()
        box.label(text="Recorded Vertex Groups", icon="GROUP_VERTEX")
        box = main_col.box()
        row = box.row(align=True)
        col = row.column(align=True)
        col.operator("cdtool_vertex_group_list.clear_selected", icon="X", text="")
        row.template_list("CDTOOLS_UL_VertexGroupItemList", "", scn, "cdtools_vertex_groups_selected", scn, "cdtools_vertex_groups_selected_index")

        col = row.column(align=True)
        col.operator("cdtools_vertex_group_list.copy_groups", icon='FILE_REFRESH', text="").refresh_or_not = True
        col.operator("cdtools_vertex_group_list.copy_groups", icon='X', text="").refresh_or_not = False
        col.separator()
        col.operator("cdtools_vertex_group_list.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("cdtools_vertex_group_list.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'
        col.separator()
        col.operator("cdtools_vertex_group_list.apply_vertex_groups_order", icon="CHECKMARK", text="")

        main_col.separator()
        box = main_col.box()
        box.label(text="External Editing", icon="FILE")
        box = main_col.box()
        row = box.row()
        row.operator("cdtools_vertex_group_list.export", text="Export to txt", icon="EXPORT")
        row.operator("cdtools_vertex_group_list.import", text="Import from txt", icon="IMPORT")

        main_col.separator()
        box = main_col.box()
        box.label(text="Description", icon="QUESTION")
        box = main_col.box()
        shared_functions.label_multiline(context=context, 
                        text="This tool is useful when sorting MMD bones order", 
                        parent=box)

# 操作符：录入顶点组
class CDTOOLS_VGLIST_OT_CopyGroups(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.copy_groups"
    bl_label = "Copy Or Clear Vertex Groups"
    refresh_or_not: bpy.props.BoolProperty() # type: ignore

    def execute(self, context):
        if self.refresh_or_not:
            context.scene.cdtools_vertex_groups_selected.clear()
            for item in context.active_object.vertex_groups:
                new_item = context.scene.cdtools_vertex_groups_selected.add()
                new_item.name = item.name
                new_item.selected = False
        else:
            context.scene.cdtools_vertex_groups_selected.clear()
        return {'FINISHED'}

# 操作符：上下移动
class CDTOOLS_VGLIST_OT_MoveItem(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.move_item"
    bl_label = "Move Item"
    direction: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        scn = context.scene
        items = scn.cdtools_vertex_groups_selected
        total = len(items)

        if self.direction == 'UP':
            for i in range(1, total):
                if items[i].selected and not items[i-1].selected:
                    items.move(i, i - 1)
        elif self.direction == 'DOWN':
            for i in reversed(range(total - 1)):
                if items[i].selected and not items[i+1].selected:
                    items.move(i, i + 1)

        return {'FINISHED'}

# 操作符：应用顶点组顺序
class CDTOOLS_VGLIST_OT_ApplyToSelectedObject(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.apply_vertex_groups_order"
    bl_label = "Apply"

    def execute(self, context):
        scn = context.scene
        vg_data = {}
        obj = context.active_object

        # 保存原始顶点权重
        for vg in obj.vertex_groups:
            weights = {}
            for v in obj.data.vertices:
                for g in v.groups:
                    if g.group == vg.index:
                        weights[v.index] = g.weight
            vg_data[vg.name] = weights

        # 清除原顶点组
        while obj.vertex_groups:
            obj.vertex_groups.remove(obj.vertex_groups[0])

        # 按照列表新顺序添加
        for item in scn.cdtools_vertex_groups_selected:
            new_vg = obj.vertex_groups.new(name=item.name)
            weights = vg_data.get(item.name, {})
            for v_idx, w in weights.items():
                new_vg.add([v_idx], w, 'REPLACE')

        return {'FINISHED'}

# 操作符：Clear selected
class CDTOOLS_VGLIST_OT_ClearSelected(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.clear_selected"
    bl_label = "Clear Selected"

    def execute(self, context):
        scn = context.scene
        for item in scn.cdtools_vertex_groups_selected:
            item.selected = False
        return {'FINISHED'}

# Op : Export or Import file
class CDTOOLS_VGLIST_OT_ExportFile(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.export"
    bl_label = "Export list to txt file"

    filepath: bpy.props.StringProperty(
        name="Export",
        description="Export file path",
        subtype='FILE_PATH'  # 使其成为一个文件路径
    ) # type: ignore
    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,
    ) # type: ignore

    def execute(self, context):
        export_set = []
        for item in context.scene.cdtools_vertex_groups_selected:
            export_set.append(item.name)
        export_list_to_txt(self.filepath, export_set)
        return {'FINISHED'}
    
    # 打开文件浏览器
    def invoke(self, context, event):
        # 弹出文件浏览器，选择文件
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Op : Import file to vertex groups order
class CDTOOLS_VGLIST_OT_ImportFile(bpy.types.Operator):
    bl_idname = "cdtools_vertex_group_list.import"
    bl_label = "Import txt file to list"

    filepath: bpy.props.StringProperty(
        name="Import",
        description="Import file path",
        subtype='FILE_PATH'  # 使其成为一个文件路径
    ) # type: ignore
    filename_ext = ".txt"
    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,
    ) # type: ignore

    def execute(self, context):
        imported_set = import_list_from_txt(self.filepath)
        context.scene.cdtools_vertex_groups_selected.clear()
        for item in imported_set:
            new_item = context.scene.cdtools_vertex_groups_selected.add()
            new_item.name = item
            new_item.selected = False
        return {'FINISHED'}
    
    # 打开文件浏览器
    def invoke(self, context, event):
        # 弹出文件浏览器，选择文件
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Op : Update selected object active vertex group
def SelectVertexGroupUpdateFunction(self, context):
    target_name = context.scene.cdtools_vertex_groups_selected[context.scene.cdtools_vertex_groups_selected_index].name
    if context.active_object:
        obj = context.active_object
        for i, vg in enumerate(obj.vertex_groups):
            if vg.name == target_name:
                obj.vertex_groups.active_index = i
                break

# 注册类
classes = (
    CDTOOLS_VertexGroupGroupProperty,
    CDTOOLS_UL_VertexGroupItemList,
    CDTOOLS_PT_VertexGroupListPanel,
    CDTOOLS_VGLIST_OT_CopyGroups,
    CDTOOLS_VGLIST_OT_MoveItem,
    CDTOOLS_VGLIST_OT_ApplyToSelectedObject,
    CDTOOLS_VGLIST_OT_ClearSelected,
    CDTOOLS_VGLIST_OT_ExportFile,
    CDTOOLS_VGLIST_OT_ImportFile
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cdtools_vertex_groups_selected = bpy.props.CollectionProperty(type=CDTOOLS_VertexGroupGroupProperty)
    bpy.types.Scene.cdtools_vertex_groups_selected_index = bpy.props.IntProperty(update=SelectVertexGroupUpdateFunction)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cdtools_vertex_groups_selected
    del bpy.types.Scene.cdtools_vertex_groups_selected_index