import bpy
from .. import shared_functions
from .. import lists
from . import functions
from ..tools import bones_mapping_panel
from ..tools import bone_rotation_panel
from ..tools import other_tools_panel

class VIEW3D_PT_main_panel(bpy.types.Panel):
    bl_label = "To UE4 Execute"
    bl_idname = "VIEW3D_PT_To_UE4_Execute"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "To UE4"

    def draw(self, context):
        layout = self.layout
        main_col = layout.column(align=True)
        box = main_col.box()
        col = box.column()

        shared_functions.label_multiline(context=context,
                        text='Click button after selecting MMD mesh',
                        parent=col)
        
        col.operator("cd_ue4_functions.translate_execute", text='Execute', icon="ARMATURE_DATA")

        shared_functions.label_multiline(context=context,
                         text='If arm bones are reverse, just make below true.',
                         parent=col)

        col.prop(context.scene, "arms_reverse", text="Reverse Arm Roll")

        box = main_col.box()
        col = box.column()

        shared_functions.label_multiline(context=context,
                         text="The button below says:'I can help you pose the model to ue4 mannequin after you finishing adjust bones in edit mode, but you can adjust them manully later'",
                         parent=col)
        col.operator('cd_ue4_functions.pose_model', text='Pose Model', icon="POSE_HLT")
        main_col.separator()

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
                other_tools_panel.merge_vg(name, newname, newname, selected_obj)

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
                bones_mapping_panel.rename_bones(armature, lists.namelist, bone1_to_bone2=True)
                # Remove empty weight vertex groups
                functions.delete_empty_vertex_groups(selected_obj.parent, selected_obj, lists.bones_ignore)

                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')

                # 将所有骨骼的连接属性设为false
                for bone in armature.edit_bones:
                    bone.use_connect = False

                # Rotate spine bones
                for name, axis, degree in list.spine_rot_list:
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, axis, degree)

                # Execute arm reverse
                mul = 1
                mul_2 = 1
                if bpy.context.scene.arms_reverse:
                    mul = -1
                    mul_2 = 0

                for name in lists.bones_arm_l:
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Z', -90 * mul)
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Y', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "hand_l", 'Z', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "hand_l", 'X', 90 * mul)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_01_l", 'Z', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_01_l", 'X', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_02_l", 'Z', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_02_l", 'X', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_03_l", 'Z', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_03_l", 'X', 180 * mul_2)

                for name in lists.namelist_finger_l:
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Z', 90)
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'X', 90 * mul)

                for name in lists.bones_arm_r:
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Z', 90 * mul)
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Y', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "hand_r", 'Z', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "hand_r", 'X', 90 * mul)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_01_r", 'Z', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_01_r", 'X', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_02_r", 'Z', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_02_r", 'X', 180 * mul_2)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_03_r", 'Z', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thumb_03_r", 'X', 180 * mul_2)

                for name in lists.namelist_finger_r:
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'Z', -90)
                    bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, name, 'X', 90 * mul)

                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thigh_l", 'X', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thigh_l", 'Y', -90)
    
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "calf_l", 'X', 90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "calf_l", 'Y', -90)
                
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thigh_r", 'X', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "thigh_r", 'Y', -90)
                
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "calf_r", 'X', -90)
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "calf_r", 'Y', -90)
                
                functions.set_bone_direction(armature, "foot_l", (0,1,0))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "foot_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "foot_r", (0,-1,0))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "foot_r", 'Y', 90)
                
                functions.set_bone_direction(armature, "ik_foot_l", (0,1,0))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "ik_foot_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "ik_foot_r", (0,-1,0))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "ik_foot_r", 'Y', 90)
                
                functions.set_bone_direction(armature, "ball_l", (0,0,1))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "ball_l", 'Y', -90)
                
                functions.set_bone_direction(armature, "ball_r", (0,0,-1))
                bone_rotation_panel.rotate_bone_local_axis_edit_mode(armature, "ball_r", 'Y', -90)

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
                    bones_mapping_panel.reparent_bones(armature, child_name, parent_name)
                
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
    
classList = {
    execute_functions,
    pose_model,
    VIEW3D_PT_main_panel,
}

def register():
    for classSingle in classList :
        bpy.utils.register_class(classSingle)

    bpy.types.Scene.arms_reverse = bpy.props.BoolProperty(name="Arm Reverse", default=False)

def unregister():
    for classSingle in classList :
        bpy.utils.unregister_class(classSingle)

    del bpy.types.Scene.arms_reverse