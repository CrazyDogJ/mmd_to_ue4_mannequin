import bpy
from .. import shared_functions

# 获取多个对象中公共的Shape Key名字
def get_common_shapekeys(object_list):
    names_sets = []
    for item in object_list:
        obj = item.obj
        if obj and obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            key_blocks = obj.data.shape_keys.key_blocks
            for key in key_blocks:
                if key.name not in names_sets:
                    names_sets.append(key.name)
    if not names_sets:
        return []
    return sorted(names_sets)

# 添加动态属性来控制滑块
def update_common_key_values(context):
    scene = context.scene
    cleanup_key_properties(context)
    common_keys = get_common_shapekeys(scene.cdtools_batchshape_objects)

    scene.cdtools_batchshape_shapekeys.clear()
    for key_name in common_keys:
        new_shape_key = scene.cdtools_batchshape_shapekeys.add()
        new_shape_key.key = key_name
        prop_id = f"sk_val_{key_name}"
        if not hasattr(scene, prop_id):
            def make_update(kname):
                def updater(self, context):
                    for item in context.scene.cdtools_batchshape_objects:
                        obj = item.obj
                        if obj and obj.data.shape_keys and kname in obj.data.shape_keys.key_blocks:
                            obj.data.shape_keys.key_blocks[kname].value = getattr(context.scene, f"sk_val_{kname}")
                return updater
            setattr(bpy.types.Scene, prop_id,
                bpy.props.FloatProperty(name=key_name, default=0.0, min=0.0, max=1.0, update=make_update(key_name)))
            setattr(scene, prop_id, 0.0)

# 清除动态添加的属性
def cleanup_key_properties(context):
    scene = context.scene
    keys_to_remove = [k for k in dir(scene) if k.startswith("sk_val_")]
    for k in keys_to_remove:
        if hasattr(bpy.types.Scene, k):
            delattr(bpy.types.Scene, k)
        if hasattr(scene, k):
            delattr(scene, k)

# Shape key group section
class CDTOOLS_ShapeKeyObjectGroupProperty(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore

class CDTOOLS_ShapeKeyNameGroupProperty(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty() # type: ignore

class CDTOOLS_UL_ShapeKeyObjectList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.obj.name, icon='OBJECT_DATA')
        op = row.operator("cdtools.batchshape_remove_object", icon="PANEL_CLOSE", text="")
        op.obj_index = index

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = []
        flt_neworder = []

        for i, item in enumerate(items):
            if self.filter_name in item.obj.name.lower():
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)

        return flt_flags, flt_neworder

class CDTOOLS_UL_ShapeKeyList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(icon="SHAPEKEY_DATA")
        if index >= 1:
            row.prop(context.scene, f"sk_val_{item.key}", text=item.key)
        else:
            row.label(text="Reference Shape Key")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = []
        flt_neworder = []

        for i, item in enumerate(items):
            if self.filter_name in item.key:
                flt_flags.append(self.bitflag_filter_item)
            else:
                flt_flags.append(0)

        return flt_flags, flt_neworder

class CDTOOLS_PT_BatchShapeKeyPanel(bpy.types.Panel):
    bl_label = "Batch Shape Key Controller"
    bl_idname = "VIEW3D_PT_batch_shapekey_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.grid_flow(row_major=True)
        scene = context.scene

        box = col.box()
        box.label(text="Selected Objects", icon="OBJECT_DATA")
        
        col.template_list("CDTOOLS_UL_ShapeKeyObjectList", 
                          "batch_shape_key_objects", 
                          scene, "cdtools_batchshape_objects", 
                          scene, "cdtools_batchshape_object_index")
        
        box = col.box()
        row = box.row()
        row.operator("cdtools.batchshape_add_object", text="Add Selected Objects", icon="ADD")
        row.operator("cdtools.batchshape_clear_objects", text="Clear", icon="X")

        col.separator()

        box = col.box()
        box.label(text="Shape Keys in Selected Objects", icon="SHAPEKEY_DATA")
        
        col.template_list("CDTOOLS_UL_ShapeKeyList",
                          "batch_shape_key_keys",
                          scene, "cdtools_batchshape_shapekeys",
                          scene, "cdtools_batchshape_shapekey_index")
        
        box = col.box()
        row = box.row()
        row.operator("cdtools.batchshape_refresh_keys", text="Refresh Shape Keys", icon="FILE_REFRESH")

        col.separator()
        box = col.box()
        box.label(text="Description", icon="QUESTION")
        box = col.box()
        shared_functions.label_multiline(context=context, 
                        text="This tool is useful when making multi-object's shape keys", 
                        parent=box)

class CDTOOLS_OT_AddObjectOperator(bpy.types.Operator):
    bl_idname = "cdtools.batchshape_add_object"
    bl_label = "Add selected objects"

    def execute(self, context):
        for obj in context.selected_objects:
            if not any(item.obj == obj for item in context.scene.cdtools_batchshape_objects):
                item = context.scene.cdtools_batchshape_objects.add()
                item.obj = obj

        update_common_key_values(context)
        return {'FINISHED'}

class CDTOOLS_OT_RemoveObejctOperator(bpy.types.Operator):
    bl_idname = "cdtools.batchshape_remove_object"
    bl_label = "Remove this object"

    obj_index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        context.scene.cdtools_batchshape_objects.remove(self.obj_index)
        update_common_key_values(context)
        return {'FINISHED'}

class CDTOOLS_OT_ClearObjectsOperator(bpy.types.Operator):
    bl_idname = "cdtools.batchshape_clear_objects"
    bl_label = "Clear objects"

    def execute(self, context):
        context.scene.cdtools_batchshape_objects.clear()
        cleanup_key_properties(context)
        update_common_key_values(context)
        return {'FINISHED'}
    
class CDTOOLS_OT_RefreshObjectsShapeKeys(bpy.types.Operator):
    bl_idname = "cdtools.batchshape_refresh_keys"
    bl_label = "Refresh shape keys"

    def execute(self, context):
        update_common_key_values(context)
        return {'FINISHED'}

def ShapeKeySelectObjectUpdateFunction(self, context): 
    batch_shape_obj = context.scene.cdtools_batchshape_objects[context.scene.cdtools_batchshape_object_index]
    if batch_shape_obj:
        batch_shape_obj.obj.select_set(True)
        context.view_layer.objects.active = batch_shape_obj.obj
    
def ShapeKeySelectKeyUpdateFunction(self, context): 
    for item in context.scene.cdtools_batchshape_objects:
        if item.obj.data.shape_keys:
            key_blocks = item.obj.data.shape_keys.key_blocks
            shape_key_name = context.scene.cdtools_batchshape_shapekeys[context.scene.cdtools_batchshape_shapekey_index].key
            if shape_key_name in key_blocks:
                # 找到索引
                index = list(key_blocks.keys()).index(shape_key_name)
                item.obj.active_shape_key_index = index
    
classes = (

    CDTOOLS_ShapeKeyObjectGroupProperty,
    CDTOOLS_ShapeKeyNameGroupProperty,

    CDTOOLS_UL_ShapeKeyObjectList,
    CDTOOLS_UL_ShapeKeyList,

    CDTOOLS_PT_BatchShapeKeyPanel,
    CDTOOLS_OT_AddObjectOperator,
    CDTOOLS_OT_RemoveObejctOperator,
    CDTOOLS_OT_ClearObjectsOperator,
    CDTOOLS_OT_RefreshObjectsShapeKeys,
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cdtools_batchshape_objects = bpy.props.CollectionProperty(type=CDTOOLS_ShapeKeyObjectGroupProperty)
    bpy.types.Scene.cdtools_batchshape_object_index = bpy.props.IntProperty(default=0, update=ShapeKeySelectObjectUpdateFunction)

    bpy.types.Scene.cdtools_batchshape_shapekeys = bpy.props.CollectionProperty(type=CDTOOLS_ShapeKeyNameGroupProperty)
    bpy.types.Scene.cdtools_batchshape_shapekey_index = bpy.props.IntProperty(default=0, update=ShapeKeySelectKeyUpdateFunction)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.cdtools_batchshape_objects
    del bpy.types.Scene.cdtools_batchshape_object_index

    del bpy.types.Scene.cdtools_batchshape_shapekeys
    del bpy.types.Scene.cdtools_batchshape_shapekey_index