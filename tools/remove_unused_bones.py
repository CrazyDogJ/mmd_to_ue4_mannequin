import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty
    
class RUB_OP_RemoveBones(Operator):
    bl_idname = "rub.removebones"
    bl_label = "Remove Unused Bones"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.type == 'ARMATURE'
                        and context.mode in {'OBJECT', 'POSE'})
    
    def execute(self, context):
        scene = context.scene
        armature_obj = context.object
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected armature not found")
            return {'CANCELLED'}
        
        # 1. Collect bones used for deformation (Vertex Groups)
        bones_to_keep = set()
        meshes_with_armature = [
            obj for obj in scene.objects 
            if obj.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == armature_obj for m in obj.modifiers)
        ]
        
        for mesh_obj in meshes_with_armature:
            weighted_groups = {g.group for v in mesh_obj.data.vertices for g in v.groups if g.weight > 0}
            print(weighted_groups)
            for vg in list(mesh_obj.vertex_groups):
                if vg.index in weighted_groups:
                    bones_to_keep.add(vg.name)

        # 3. Identify bones to remove
        bones_to_remove = [bone.name for bone in armature_obj.data.bones if bone.name not in bones_to_keep]
        
        if not bones_to_remove:
            self.report({'WARNING'}, "No unused bones found")
            return {'FINISHED'}
        
        # 4. Perform Deletion
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        count = 0
        for b_name in bones_to_remove:
            edit_bone = armature_obj.data.edit_bones.get(b_name)
            if edit_bone:
                armature_obj.data.edit_bones.remove(edit_bone)
                count += 1
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, f"Removed {count} unused bones from {context.object.name}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RUB_OP_RemoveBones)

def unregister():
    bpy.utils.unregister_class(RUB_OP_RemoveBones)
