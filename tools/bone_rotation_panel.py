import bpy
from .. import shared_functions
import math
import mathutils

def rotate_bone_local_axis_edit_mode(armature_data, bone_name, axis, angle_degrees):
    # 获取骨骼编辑数据
    edit_bones = armature_data.edit_bones
    bone = edit_bones.get(bone_name)
    if bone is not None:
        # 将角度转换为弧度
        angle_radians = math.radians(angle_degrees)
        # 打印骨骼的变换矩阵
        print("骨骼 %s 的变换矩阵：" % bone_name)
        for row in bone.matrix:
            print(row)
        else:
            print("找不到指定的骨骼：%s" % bone_name)
        # 根据指定的轴进行旋转
        if axis == 'X':
            rotation_matrix = mathutils.Matrix.Rotation(angle_radians, 4, 'X')
        elif axis == 'Y':
            rotation_matrix = mathutils.Matrix.Rotation(angle_radians, 4, 'Y')
        elif axis == 'Z':
            rotation_matrix = mathutils.Matrix.Rotation(angle_radians, 4, 'Z')

        # Apply the rotation to the bone's matrix
        bone.matrix = bone.matrix @ rotation_matrix
        # 打印骨骼的变换矩阵
        print("骨骼 %s 的变换矩阵：" % bone_name)
        for row in rotation_matrix:
            print(row)
        else:
            print("找不到指定的骨骼：%s" % bone_name)

class CDTOOLS_PT_bone_rotation_panel(bpy.types.Panel):
    bl_label = "Edit Bones"
    bl_idname = "VIEW3D_PT_bone_rotation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        box = col.box()
        box.label(text="Rotate Bones", icon="BONE_DATA")

        row = col.row(align=True)
        box = row.box()

        row = box.row(align=True)
        row.label(icon="EVENT_X")
        row.separator()
        operator2 = row.operator('cdtools.bone_rotate_operator', text='Rotate -90', icon="LOOP_BACK")
        operator1 = row.operator('cdtools.bone_rotate_operator', text='Rotate 90', icon="LOOP_FORWARDS")
        
        row = box.row(align=True)
        row.label(icon="EVENT_Y")
        row.separator()
        operator4 = row.operator('cdtools.bone_rotate_operator', text='Rotate -90', icon="LOOP_BACK")
        operator3 = row.operator('cdtools.bone_rotate_operator', text='Rotate 90', icon="LOOP_FORWARDS")
        
        row = box.row(align=True)
        row.label(icon="EVENT_Z")
        row.separator()
        operator6 = row.operator('cdtools.bone_rotate_operator', text='Rotate -90', icon="LOOP_BACK")
        operator5 = row.operator('cdtools.bone_rotate_operator', text='Rotate 90', icon="LOOP_FORWARDS")

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

        col.separator()
        box = col.box()
        box.label(text="Description", icon="QUESTION")
        box = col.box()
        shared_functions.label_multiline(context=context, 
                        text="This tool is useful for editing bone's facing, TIPS: You should look towards the positive direction of a axis", 
                        parent=box)

class CDTOOLS_OT_bone_rotate_operator(bpy.types.Operator):
    bl_label = "Rotate Bones"
    bl_idname = "cdtools.bone_rotate_operator"

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
                if self.axis != "Y":
                    bone.use_connect = False
                rotate_bone_local_axis_edit_mode(obj.data, bone.name, self.axis, self.degree)
        else:
            print("当前对象不是一个骨骼或者不在编辑模式下。")

        bpy.ops.wm.redraw_timer()
        return{'FINISHED'}
    
classes = (
    CDTOOLS_PT_bone_rotation_panel,
    CDTOOLS_OT_bone_rotate_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
