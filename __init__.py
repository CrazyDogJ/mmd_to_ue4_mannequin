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

class main_panel(bpy.types.Panel):
    bl_label = "To UE4"
    bl_idname = "CD_UE4_layout"
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

        _label_multiline(context=context,
                         text="The button below says:'I can help you pose the model to ue4 mannequin after you finishing adjust bones in edit mode'",
                         parent=col)
        col.operator('cd_ue4_functions.pose_model', text='Pose Model')

class execute_functions(bpy.types.Operator):
    bl_label = "Execute Functions"
    bl_idname = "cd_ue4_functions.translate_execute"

    def execute(self, context):

        selected_obj = bpy.context.active_object

        if selected_obj.type == 'MESH':
            # Merge **D.L/R vertex groups
            for name, newname in lists.namelist_1:
                pb_new = selected_obj.vertex_groups.get(newname)
                pb_old = selected_obj.vertex_groups.get(name)
                if pb_new is None or pb_old is None:
                    continue
                functions.merge_vg(name, newname, newname, selected_obj)

            if selected_obj.parent.type == 'ARMATURE':
                selected_armature = selected_obj.parent
                selected_armature.select_set(True)
                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')
                armature = selected_armature.data
                selected_armature.name = "root"
                armature.name = "root"

                functions.rename_bones(armature, lists.namelist)
                functions.delete_empty_vertex_groups(selected_obj.parent, selected_obj, lists.bones_ignore)

                bpy.context.view_layer.objects.active = selected_armature
                bpy.ops.object.mode_set(mode='EDIT')

                # 将所有骨骼的连接属性设为false
                for bone in armature.edit_bones:
                    bone.use_connect = False

                functions.rotate_bone_local_axis_edit_mode(armature, "pelvis", 'X', 90)
                functions.rotate_bone_local_axis_edit_mode(armature, "pelvis", 'Y', -90)

                functions.rotate_bone_local_axis_edit_mode(armature, "spine_01", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "spine_01", 'Y', -90)

                functions.rotate_bone_local_axis_edit_mode(armature, "spine_02", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "spine_02", 'Y', -90)

                functions.rotate_bone_local_axis_edit_mode(armature, "neck_01", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "neck_01", 'Y', -90)

                functions.rotate_bone_local_axis_edit_mode(armature, "head", 'X', -90)
                functions.rotate_bone_local_axis_edit_mode(armature, "head", 'Y', -90)

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

                namelist1 = {"index_01_l","index_02_l","index_03_l",
                             "middle_01_l","middle_02_l","middle_03_l",
                             "ring_01_l","ring_02_l","ring_03_l",
                             "pinky_01_l","pinky_02_l","pinky_03_l",}
                for name in namelist1:
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

                namelist2 = {"index_01_r","index_02_r","index_03_r",
                             "middle_01_r","middle_02_r","middle_03_r",
                             "ring_01_r","ring_02_r","ring_03_r",
                             "pinky_01_r","pinky_02_r","pinky_03_r",}
                for name in namelist2:
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
def unregister():
    bpy.utils.unregister_class(main_panel)
    bpy.utils.unregister_class(execute_functions)
    bpy.utils.unregister_class(bone_rotate_execute)
    bpy.utils.unregister_class(pose_model)

if __name__ == "__main__":
    register()