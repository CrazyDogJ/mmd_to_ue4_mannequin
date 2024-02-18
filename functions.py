import bpy
import math
import mathutils

# Functions
def bind_bone_to_parent(armature_data, child_bone_name, parent_bone_name):
    # 查找子级骨骼和父级骨骼
    child_bone = armature_data.edit_bones.get(child_bone_name)
    parent_bone = armature_data.edit_bones.get(parent_bone_name)
    
    if child_bone:
        if parent_bone_name is "root":
            child_bone.parent = None
        elif parent_bone:
            # 设置子级骨骼的父级骨骼
            child_bone.parent = parent_bone
    else:
        print("未找到指定名称的骨骼")

def rename_bones(armature_data, name_list):
    for name, newname in name_list:
        idx = armature_data.edit_bones.find(name)
        if idx != -1:
            bo = armature_data.edit_bones[idx]
            bo.name = newname
        else: #Not found
            #Do something
            pass

def rename_vertex_groups(mesh_obj, name_list):
    vertex_groups = mesh_obj.vertex_groups
    for name, newname in name_list:
        idx = vertex_groups.find(name)
        if idx != -1:
            vg = vertex_groups[idx]
            vg.name = newname
        else: #Not found
            #Do something
            pass

def add_new_bone(armature_data, name, new_bone_head, new_bone_tail):
    new_bone = armature_data.edit_bones.new(name)
    new_bone.head = new_bone_head
    new_bone.tail = new_bone_tail

    bpy.context.view_layer.update()

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

def set_bone_direction(armature_data, bone_name, direction_vector):
 
    # 获取指定名称的骨骼
    bone = armature_data.edit_bones.get(bone_name)
    if bone is None:
        return
    
    # 获取骨骼的当前位置
    bone_head = bone.head
    bone_tail = bone.tail
    
    # 计算骨骼当前的方向向量
    current_direction = (bone_tail - bone_head).normalized()
    
    # 计算旋转矩阵，将当前方向转换为目标方向
    rotation_matrix = current_direction.rotation_difference(direction_vector).to_matrix().to_4x4()
    
    # 更新骨骼的方向
    new_tail = bone_head + rotation_matrix @ (bone_tail - bone_head)
    bone.tail = new_tail

def delete_empty_vertex_groups(armature_object, mesh_object, bones_ignore):
    maxWeight = survey(mesh_object)
    # fix bug pointed out by user2859
    ka = []
    ka.extend(maxWeight.keys())
    ka.sort(key=lambda gn: -gn)
    print (ka)

    bpy.ops.object.mode_set(mode='OBJECT')
    armature_object.select_set(True)
    bpy.context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode='EDIT')
    for gn in ka:
        if maxWeight[gn]<=0:
            print ("delete %d"%gn)
            vg = mesh_object.vertex_groups[gn]
            if vg.name not in bones_ignore:
                if vg.name in armature_object.data.edit_bones:
                    bone = armature_object.data.edit_bones[vg.name]
                    armature_object.data.edit_bones.remove(bone)
            mesh_object.vertex_groups.remove(vg) # actually remove the group
    bpy.ops.object.mode_set(mode='OBJECT')

def survey(obj):
    maxWeight = {}
    for i in obj.vertex_groups:
        maxWeight[i.index] = 0

    for v in obj.data.vertices:
        for g in v.groups:
            gn = g.group
            w = obj.vertex_groups[g.group].weight(v.index)
            if (maxWeight.get(gn) is None or w>maxWeight[gn]):
                maxWeight[gn] = w
    return maxWeight

def merge_vg(vgroup_A_name, vgroup_B_name, vgroup_new_name, ob):
    if (vgroup_A_name in ob.vertex_groups and
    vgroup_B_name in ob.vertex_groups):

        vgroup = ob.vertex_groups.new(name=vgroup_A_name+"+"+vgroup_B_name)

        for id, vert in enumerate(ob.data.vertices):
            available_groups = [v_group_elem.group for v_group_elem in vert.groups]
            A = B = 0
            if ob.vertex_groups[vgroup_A_name].index in available_groups:
                A = ob.vertex_groups[vgroup_A_name].weight(id)
            if ob.vertex_groups[vgroup_B_name].index in available_groups:
                B = ob.vertex_groups[vgroup_B_name].weight(id)

            # only add to vertex group is weight is > 0
            sum = A + B
            if sum > 0:
                vgroup.add([id], sum ,'REPLACE')

        ob.vertex_groups.remove(ob.vertex_groups[vgroup_A_name])
        ob.vertex_groups.remove(ob.vertex_groups[vgroup_B_name])
        vgroup.name = vgroup_new_name
        vgroup = ob.vertex_groups.new(name=vgroup_A_name)