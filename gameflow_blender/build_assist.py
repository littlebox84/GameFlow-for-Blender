import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel
from mathutils import Vector

from .preferences import get_prefs


def _selected(context):
    return [obj for obj in context.selected_objects if obj is not None]


def _active(context):
    return context.view_layer.objects.active


def _step(context):
    prefs = get_prefs(context)
    return prefs.build_grid_step if prefs else 1.0


def _bbox_world(obj):
    if not getattr(obj, 'bound_box', None):
        return []
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


class GAMEFLOW_OT_smart_duplicate(Operator):
    bl_idname = "gameflow.smart_duplicate"
    bl_label = "Smart Duplicate"
    bl_description = "Duplicate selection by one GameFlow build step"
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(items=[
        ('LEFT', 'Left', 'Duplicate left'), ('RIGHT', 'Right', 'Duplicate right'),
        ('BACK', 'Back', 'Duplicate backward'), ('FORWARD', 'Forward', 'Duplicate forward'),
        ('DOWN', 'Down', 'Duplicate down'), ('UP', 'Up', 'Duplicate up'),
    ], default='RIGHT')

    def execute(self, context):
        if not _selected(context):
            self.report({'INFO'}, 'Select an object first')
            return {'CANCELLED'}
        vectors = {
            'LEFT': (-1, 0, 0), 'RIGHT': (1, 0, 0),
            'BACK': (0, -1, 0), 'FORWARD': (0, 1, 0),
            'DOWN': (0, 0, -1), 'UP': (0, 0, 1),
        }
        step = _step(context)
        delta = Vector(vectors[self.direction]) * step
        bpy.ops.object.duplicate(linked=False)
        for obj in _selected(context):
            obj.location += delta
        return {'FINISHED'}


class GAMEFLOW_OT_align_selection(Operator):
    bl_idname = "gameflow.align_selection"
    bl_label = "Align Selection"
    bl_description = "Align selected objects to the active object"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(items=[('X', 'X', 'Align X'), ('Y', 'Y', 'Align Y'), ('Z', 'Z', 'Align Z')], default='X')

    def execute(self, context):
        active = _active(context)
        objects = _selected(context)
        if active is None or len(objects) < 2:
            self.report({'INFO'}, 'Select two or more objects; active object is the target')
            return {'CANCELLED'}
        index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        target = active.location[index]
        for obj in objects:
            if obj != active and not obj.lock_location[index]:
                obj.location[index] = target
        return {'FINISHED'}


class GAMEFLOW_OT_place_relative(Operator):
    bl_idname = "gameflow.place_relative"
    bl_label = "Place Relative"
    bl_description = "Place selected objects beside or on top of the active object"
    bl_options = {'REGISTER', 'UNDO'}

    relation: EnumProperty(items=[
        ('LEFT', 'Left', 'Place left of active'), ('RIGHT', 'Right', 'Place right of active'),
        ('BACK', 'Back', 'Place behind active'), ('FRONT', 'Front', 'Place in front of active'),
        ('TOP', 'On Top', 'Place on top of active'),
    ], default='TOP')

    def execute(self, context):
        active = _active(context)
        objects = [obj for obj in _selected(context) if obj != active]
        if active is None or not objects:
            self.report({'INFO'}, 'Select a target as active plus one or more objects to place')
            return {'CANCELLED'}
        target_box = _bbox_world(active)
        if not target_box:
            return {'CANCELLED'}
        tmin = Vector((min(p.x for p in target_box), min(p.y for p in target_box), min(p.z for p in target_box)))
        tmax = Vector((max(p.x for p in target_box), max(p.y for p in target_box), max(p.z for p in target_box)))
        for obj in objects:
            box = _bbox_world(obj)
            if not box:
                continue
            omin = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
            omax = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
            if self.relation == 'TOP':
                obj.location.z += tmax.z - omin.z
            elif self.relation == 'LEFT':
                obj.location.x += tmin.x - omax.x
            elif self.relation == 'RIGHT':
                obj.location.x += tmax.x - omin.x
            elif self.relation == 'BACK':
                obj.location.y += tmin.y - omax.y
            elif self.relation == 'FRONT':
                obj.location.y += tmax.y - omin.y
        return {'FINISHED'}


class GAMEFLOW_OT_reset_transform(Operator):
    bl_idname = "gameflow.reset_transform"
    bl_label = "Reset Transform"
    bl_description = "Reset selected object transforms"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(items=[
        ('LOCATION', 'Location', 'Reset location'), ('ROTATION', 'Rotation', 'Reset rotation'),
        ('SCALE', 'Scale', 'Reset scale'), ('ALL', 'All', 'Reset all transforms'),
    ], default='ALL')

    def execute(self, context):
        objects = _selected(context)
        if not objects:
            self.report({'INFO'}, 'Select an object first')
            return {'CANCELLED'}
        for obj in objects:
            if self.mode in {'LOCATION', 'ALL'}:
                for i in range(3):
                    if not obj.lock_location[i]: obj.location[i] = 0.0
            if self.mode in {'ROTATION', 'ALL'}:
                for i in range(3):
                    if not obj.lock_rotation[i]: obj.rotation_euler[i] = 0.0
            if self.mode in {'SCALE', 'ALL'}:
                for i in range(3):
                    if not obj.lock_scale[i]: obj.scale[i] = 1.0
        return {'FINISHED'}


class GAMEFLOW_OT_lock_transform(Operator):
    bl_idname = "gameflow.lock_transform"
    bl_label = "Lock Transform"
    bl_description = "Lock or unlock position, rotation, or scale for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    channel: EnumProperty(items=[('LOCATION', 'Position', 'Position locks'), ('ROTATION', 'Rotation', 'Rotation locks'), ('SCALE', 'Scale', 'Scale locks')], default='LOCATION')
    action: EnumProperty(items=[('LOCK', 'Lock', 'Lock transform'), ('UNLOCK', 'Unlock', 'Unlock transform')], default='LOCK')

    def execute(self, context):
        objects = _selected(context)
        if not objects:
            return {'CANCELLED'}
        value = self.action == 'LOCK'
        attr = {'LOCATION': 'lock_location', 'ROTATION': 'lock_rotation', 'SCALE': 'lock_scale'}[self.channel]
        for obj in objects:
            setattr(obj, attr, (value, value, value))
        return {'FINISHED'}


class GAMEFLOW_OT_selection_helper(Operator):
    bl_idname = "gameflow.selection_helper"
    bl_label = "Selection Helper"
    bl_description = "Common beginner-friendly selection actions"
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(items=[
        ('ISOLATE', 'Isolate', 'Hide everything except selection'),
        ('REVEAL', 'Reveal All', 'Reveal hidden objects'),
        ('PARENT', 'Select Parent', 'Select parent of active object'),
        ('CHILDREN', 'Select Children', 'Select children of active object'),
    ], default='ISOLATE')

    def execute(self, context):
        active = _active(context)
        if self.action == 'REVEAL':
            bpy.ops.object.hide_view_clear(select=False)
            return {'FINISHED'}
        if active is None:
            self.report({'INFO'}, 'Select an object first')
            return {'CANCELLED'}
        if self.action == 'ISOLATE':
            selected = set(_selected(context))
            for obj in context.view_layer.objects:
                obj.hide_set(obj not in selected)
        elif self.action == 'PARENT':
            if active.parent is None:
                self.report({'INFO'}, 'Active object has no parent')
                return {'CANCELLED'}
            bpy.ops.object.select_all(action='DESELECT')
            active.parent.select_set(True)
            context.view_layer.objects.active = active.parent
        elif self.action == 'CHILDREN':
            bpy.ops.object.select_all(action='DESELECT')
            for child in active.children:
                child.select_set(True)
            if active.children:
                context.view_layer.objects.active = active.children[0]
        return {'FINISHED'}


class VIEW3D_PT_gameflow_build_assist(Panel):
    bl_label = "Build Assist"
    bl_idname = "VIEW3D_PT_gameflow_build_assist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameFlow'
    bl_parent_id = 'VIEW3D_PT_gameflow'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        prefs = get_prefs(context)
        if prefs is None:
            layout.label(text='GameFlow preferences unavailable')
            return

        box = layout.box()
        box.label(text='Smart Duplicate')
        row = box.row(align=True)
        for direction, label in [('LEFT','← X'), ('RIGHT','X →'), ('BACK','← Y'), ('FORWARD','Y →')]:
            op = row.operator('gameflow.smart_duplicate', text=label)
            op.direction = direction
        row = box.row(align=True)
        for direction, label in [('DOWN','↓ Z'), ('UP','Z ↑')]:
            op = row.operator('gameflow.smart_duplicate', text=label)
            op.direction = direction

        box = layout.box(); box.label(text='Align to Active')
        row = box.row(align=True)
        for axis in ('X','Y','Z'):
            op = row.operator('gameflow.align_selection', text=f'Align {axis}'); op.axis = axis

        box = layout.box(); box.label(text='Place Relative to Active')
        row = box.row(align=True)
        for relation, label in [('LEFT','Left'), ('RIGHT','Right'), ('BACK','Back'), ('FRONT','Front'), ('TOP','On Top')]:
            op = row.operator('gameflow.place_relative', text=label); op.relation = relation

        box = layout.box(); box.label(text='Reset Transform')
        row = box.row(align=True)
        for mode, label in [('LOCATION','Position'), ('ROTATION','Rotation'), ('SCALE','Scale'), ('ALL','All')]:
            op = row.operator('gameflow.reset_transform', text=label); op.mode = mode

        box = layout.box(); box.label(text='Lock / Unlock')
        for channel, label in [('LOCATION','Position'), ('ROTATION','Rotation'), ('SCALE','Scale')]:
            row = box.row(align=True)
            lock = row.operator('gameflow.lock_transform', text=f'Lock {label}'); lock.channel = channel; lock.action = 'LOCK'
            unlock = row.operator('gameflow.lock_transform', text='Unlock'); unlock.channel = channel; unlock.action = 'UNLOCK'

        box = layout.box(); box.label(text='Selection Helpers')
        row = box.row(align=True)
        for action, label in [('ISOLATE','Isolate'), ('REVEAL','Reveal All'), ('PARENT','Parent'), ('CHILDREN','Children')]:
            op = row.operator('gameflow.selection_helper', text=label); op.action = action


classes = (
    GAMEFLOW_OT_smart_duplicate,
    GAMEFLOW_OT_align_selection,
    GAMEFLOW_OT_place_relative,
    GAMEFLOW_OT_reset_transform,
    GAMEFLOW_OT_lock_transform,
    GAMEFLOW_OT_selection_helper,
    VIEW3D_PT_gameflow_build_assist,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
