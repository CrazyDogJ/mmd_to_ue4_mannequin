import bpy
import os

# 创建骨架的操作
class AddCustomArmature(bpy.types.Operator):
    bl_idname = "object.add_custom_armature"
    bl_label = "Add UE4 Mannequin"
    bl_description = "Creates a ue4 mannequin armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        blend_file = os.path.join(addon_dir, "mannequin_ref_skeleton.blend")
        armature_path = "Object/root"  # 你的骨架名称
        bpy.ops.wm.append(
        filepath=os.path.join(blend_file, armature_path),
        directory=os.path.join(blend_file, "Object"),
        filename="root"
        )

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(AddCustomArmature.bl_idname, icon='OUTLINER_OB_ARMATURE')

classList = {
    AddCustomArmature,
}

def register():
    for classSingle in classList :
        bpy.utils.register_class(classSingle)

    bpy.types.VIEW3D_MT_armature_add.append(menu_func)

def unregister():
    for classSingle in classList :
        bpy.utils.unregister_class(classSingle)

    bpy.types.VIEW3D_MT_armature_add.remove(menu_func)