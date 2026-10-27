"""Apply a Mirror modifier with internal _L_ / _R_ vertex-group names."""

import re
import uuid

import bpy
from bpy.props import StringProperty


MARKER = re.compile(r"_([LRlr])(?=_)")


def counterpart(name):
    """Return (opposite name, side), or None; reject ambiguous names."""
    matches = list(MARKER.finditer(name))
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError("名称包含多个左右标记，请先明确命名：" + name)
    match = matches[0]
    side = match.group(1)
    other = {"L": "R", "R": "L", "l": "r", "r": "l"}[side]
    index = match.start(1)
    return name[:index] + other + name[index + 1:], side.upper()


def prepare(obj, modifier_name):
    if obj is None or obj.type != 'MESH':
        raise ValueError("请选中网格物体")
    if obj.mode != 'OBJECT':
        raise ValueError("请切换到物体模式后操作")
    if not obj.is_editable or not obj.data.is_editable:
        raise ValueError("物体和网格必须可编辑")
    if obj.override_library or obj.data.override_library:
        raise ValueError("请使用本地物体与网格，不支持库覆盖")
    if obj.data.users > 1:
        raise ValueError("网格被多个物体共用，请先将网格设为单用户")
    if obj.data.shape_keys:
        raise ValueError("存在形态键，Blender 无法直接应用此镜像修改器")
    mod = obj.modifiers.get(modifier_name)
    if mod is None or mod.type != 'MIRROR':
        raise ValueError("找不到指定的镜像修改器")
    if obj.modifiers[0] != mod:
        raise ValueError("请先将要应用的镜像修改器移到修改器列表第一位")
    if sum(mod.use_axis) != 1:
        raise ValueError("此操作要求镜像修改器只启用一个镜像轴")
    if not mod.show_viewport:
        raise ValueError("请先启用此修改器的视口显示")

    pairs = []
    seen = set()
    for group in obj.vertex_groups:
        result = counterpart(group.name)
        if result is None:
            continue
        opposite, side = result
        if group.name in seen:
            continue
        left, right = (group.name, opposite) if side == 'L' else (opposite, group.name)
        # Blender vertex-group names have a 63-byte payload. Never accept truncation.
        if max(len(left.encode('utf-8')), len(right.encode('utf-8'))) > 63:
            raise ValueError("顶点组名称过长：" + group.name)
        pairs.append((left, right))
        seen.update((left, right))
    if not pairs:
        raise ValueError("未找到包含 _L_ / _R_ 或 _l_ / _r_ 的顶点组")
    return mod, pairs


def apply_mapped_mirror(context, obj, modifier_name):
    """Validate first, then temporarily alias groups and use native Mirror.

    Keep group indices stable: rename existing groups, append missing ones.
    Restore names even when the native operator fails. Do not rename bones.
    """
    mod, pairs = prepare(obj, modifier_name)
    old_mirror_groups = mod.use_mirror_vertex_groups
    old_active = obj.vertex_groups.active_index
    created = []
    renamed = []
    applied = False
    nonce = uuid.uuid4().hex[:16]
    # Avoid collisions with both existing names and names that will be created.
    reserved = set(obj.vertex_groups.keys()) | {n for pair in pairs for n in pair}
    aliases = []
    for i, pair in enumerate(pairs):
        alias = (f"vwm_{nonce}_{i}.L", f"vwm_{nonce}_{i}.R")
        if any(n in reserved for n in alias):
            raise ValueError("临时名称冲突，请重试")
        aliases.append(alias)

    try:
        for pair, alias in zip(pairs, aliases):
            for original, temporary in zip(pair, alias):
                group = obj.vertex_groups.get(original)
                if group is None:
                    group = obj.vertex_groups.new(name=original)
                    created.append(group.name)
                    if group.name != original:
                        raise RuntimeError("无法创建精确名称的顶点组：" + original)
                renamed.append((temporary, original))
                group.name = temporary
                if group.name != temporary:
                    raise RuntimeError("无法设置临时顶点组名称")
        mod.use_mirror_vertex_groups = True
        obj.data.update()
        context.view_layer.update()
        with context.temp_override(object=obj, active_object=obj,
                                   selected_objects=[obj], selected_editable_objects=[obj]):
            result = bpy.ops.object.modifier_apply(modifier=modifier_name)
        if 'FINISHED' not in result:
            raise RuntimeError("Blender 未能应用镜像修改器")
        applied = True
    finally:
        # Never access the modifier after successful application: its RNA is gone.
        # Applying replaces mesh-owned group data in Blender 5.1. Re-fetch by
        # alias instead of retaining stale VertexGroup RNA references.
        for temporary, original in renamed:
            group = obj.vertex_groups.get(temporary)
            if group is not None:
                group.name = original
        if not applied:
            for name in reversed(created):
                group = obj.vertex_groups.get(name)
                if group is not None:
                    obj.vertex_groups.remove(group)
            remaining = obj.modifiers.get(modifier_name)
            if remaining is not None:
                remaining.use_mirror_vertex_groups = old_mirror_groups
        if obj.vertex_groups:
            obj.vertex_groups.active_index = min(old_active, len(obj.vertex_groups) - 1)
        obj.data.update()
        context.view_layer.update()
    return len(pairs), len(created)


class VWM_OT_apply(bpy.types.Operator):
    bl_idname = "object.valve_weight_mirror_apply"
    bl_label = "应用镜像并映射权重"
    bl_description = "识别中间的 _L_ / _R_，应用镜像并恢复原始组名；自动创建缺少的对侧组"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: bpy.props.StringProperty(name="镜像修改器", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        obj = context.object
        name = self.modifier_name
        if not name:
            mirrors = [m for m in obj.modifiers if m.type == 'MIRROR']
            if len(mirrors) != 1:
                self.report({'ERROR'}, "请在 N 面板的权重镜像页中选择要应用的修改器")
                return {'CANCELLED'}
            name = mirrors[0].name
        try:
            pairs, created = apply_mapped_mirror(context, obj, name)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f"镜像已应用：{pairs} 对自定义组，新增 {created} 个组；名称已恢复")
        return {'FINISHED'}


class VWM_PT_panel(bpy.types.Panel):
    bl_label = "Valve 顶点组权重镜像"
    bl_idname = "VWM_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cd Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="支持 _L_ / _R_ 和 _l_ / _r_")
        layout.label(text="应用完成后保留原始组名")
        if obj is None or obj.type != 'MESH':
            layout.label(text="请选中网格物体", icon='INFO')
            return
        mirrors = [m for m in obj.modifiers if m.type == 'MIRROR']
        if not mirrors:
            layout.label(text="此物体没有镜像修改器", icon='INFO')
            layout.label(text="用于应用修改器前的半边模型")
            return
        for mod in mirrors:
            box = layout.box()
            box.label(text=mod.name, icon='MOD_MIRROR')
            try:
                _, pairs = prepare(obj, mod.name)
                box.label(text=f"识别到 {len(pairs)} 对自定义组")
                ready = True
            except ValueError as exc:
                box.label(text=str(exc), icon='INFO')
                ready = False
            row = box.row()
            row.enabled = ready
            row.operator(VWM_OT_apply.bl_idname, icon='CHECKMARK').modifier_name = mod.name
        layout.separator()
        layout.label(text="先绘制原始半边，再用此按钮应用")
        layout.label(text="合并、切分、UV 使用修改器原设置")


CLASSES = (VWM_OT_apply, VWM_PT_panel)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)