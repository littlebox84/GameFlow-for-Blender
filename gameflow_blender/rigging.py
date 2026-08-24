import bpy
from bpy.types import Operator, Panel
from mathutils import Vector

from .preferences import get_prefs

GUIDE_PREFIX = "GF_RIG_"
ARMATURE_NAME = "GameFlow_Rig"

GUIDE_NAMES = (
    "HIPS", "CHEST", "NECK", "HEAD",
    "SHOULDER_L", "ELBOW_L", "HAND_L",
    "SHOULDER_R", "ELBOW_R", "HAND_R",
    "KNEE_L", "FOOT_L", "KNEE_R", "FOOT_R",
)


def _active_mesh(context):
    obj = context.active_object
    return obj if obj and obj.type == 'MESH' else None


def _world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [v.x for v in corners]
    ys = [v.y for v in corners]
    zs = [v.z for v in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _guide(name):
    return bpy.data.objects.get(GUIDE_PREFIX + name)


def _guide_pos(name):
    obj = _guide(name)
    return obj.matrix_world.translation.copy() if obj else None


def _clear_guides():
    for name in GUIDE_NAMES:
        obj = _guide(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)


def _make_guide(context, name, location, size):
    obj = bpy.data.objects.new(GUIDE_PREFIX + name, None)
    obj.empty_display_type = 'SPHERE'
    obj.empty_display_size = size
    obj.location = location
    obj.show_name = True
    obj["gameflow_rig_guide"] = True
    context.collection.objects.link(obj)
    return obj


def _add_bone(edit_bones, name, head, tail, parent=None):
    bone = edit_bones.new(name)
    bone.head = head
    bone.tail = tail
    if (bone.tail - bone.head).length < 0.001:
        bone.tail.z += 0.05
    if parent:
        bone.parent = parent
    return bone


class GAMEFLOW_OT_create_rig_guides(Operator):
    bl_idname = "gameflow.create_rig_guides"
    bl_label = "Create Snap Rig Guides"
    bl_description = "Place beginner-friendly body markers around the selected character"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'INFO'}, "Select one mesh character first")
            return {'CANCELLED'}

        _clear_guides()
        min_x, max_x, min_y, max_y, min_z, max_z = _world_bounds(obj)
        cx = (min_x + max_x) * 0.5
        cy = (min_y + max_y) * 0.5
        h = max(max_z - min_z, 0.001)
        w = max(max_x - min_x, 0.001)
        size = max(h * 0.025, w * 0.025, 0.03)

        z = lambda f: min_z + h * f
        sx = w * 0.23
        ex = w * 0.42
        hx = w * 0.54
        leg_x = w * 0.15

        positions = {
            "HIPS": (cx, cy, z(0.47)),
            "CHEST": (cx, cy, z(0.68)),
            "NECK": (cx, cy, z(0.82)),
            "HEAD": (cx, cy, z(0.94)),
            "SHOULDER_L": (cx + sx, cy, z(0.76)),
            "ELBOW_L": (cx + ex, cy, z(0.64)),
            "HAND_L": (cx + hx, cy, z(0.53)),
            "SHOULDER_R": (cx - sx, cy, z(0.76)),
            "ELBOW_R": (cx - ex, cy, z(0.64)),
            "HAND_R": (cx - hx, cy, z(0.53)),
            "KNEE_L": (cx + leg_x, cy, z(0.25)),
            "FOOT_L": (cx + leg_x, cy - h * 0.03, z(0.03)),
            "KNEE_R": (cx - leg_x, cy, z(0.25)),
            "FOOT_R": (cx - leg_x, cy - h * 0.03, z(0.03)),
        }

        for name, location in positions.items():
            _make_guide(context, name, location, size)

        obj["gameflow_rig_target"] = True
        self.report({'INFO'}, "Rig guides created — move the markers onto the joints, then Build Rig")
        return {'FINISHED'}


class GAMEFLOW_OT_build_rig_from_guides(Operator):
    bl_idname = "gameflow.build_rig_from_guides"
    bl_label = "Build Rig From Guides"
    bl_description = "Create a humanoid armature through the GameFlow snap markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        missing = [name for name in GUIDE_NAMES if _guide(name) is None]
        if missing:
            self.report({'WARNING'}, "Create Rig Guides first")
            return {'CANCELLED'}

        old = bpy.data.objects.get(ARMATURE_NAME)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)

        arm_data = bpy.data.armatures.new(ARMATURE_NAME)
        arm_obj = bpy.data.objects.new(ARMATURE_NAME, arm_data)
        context.collection.objects.link(arm_obj)
        arm_obj["gameflow_quick_rig"] = True
        arm_obj.show_in_front = True

        bpy.ops.object.select_all(action='DESELECT')
        arm_obj.select_set(True)
        context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='EDIT')
        eb = arm_data.edit_bones

        hips = _guide_pos("HIPS")
        chest = _guide_pos("CHEST")
        neck = _guide_pos("NECK")
        head = _guide_pos("HEAD")

        spine = _add_bone(eb, "spine", hips, chest)
        chest_b = _add_bone(eb, "chest", chest, neck, spine)
        neck_b = _add_bone(eb, "neck", neck, head, chest_b)
        head_tail = head + Vector((0.0, 0.0, max((head - neck).length * 0.55, 0.08)))
        _add_bone(eb, "head", head, head_tail, neck_b)

        for side, suffix in (("L", ".L"), ("R", ".R")):
            shoulder = _guide_pos(f"SHOULDER_{side}")
            elbow = _guide_pos(f"ELBOW_{side}")
            hand = _guide_pos(f"HAND_{side}")
            knee = _guide_pos(f"KNEE_{side}")
            foot = _guide_pos(f"FOOT_{side}")

            clav = _add_bone(eb, "shoulder" + suffix, chest, shoulder, chest_b)
            upper = _add_bone(eb, "upper_arm" + suffix, shoulder, elbow, clav)
            fore = _add_bone(eb, "forearm" + suffix, elbow, hand, upper)
            hand_tail = hand + (hand - elbow).normalized() * max((hand - elbow).length * 0.35, 0.05)
            _add_bone(eb, "hand" + suffix, hand, hand_tail, fore)

            thigh = _add_bone(eb, "thigh" + suffix, hips, knee, spine)
            shin = _add_bone(eb, "shin" + suffix, knee, foot, thigh)
            foot_tail = foot + Vector((0.0, -max((knee - foot).length * 0.25, 0.08), 0.0))
            _add_bone(eb, "foot" + suffix, foot, foot_tail, shin)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "GameFlow rig built — use Bind Model when the skeleton looks right")
        return {'FINISHED'}


class GAMEFLOW_OT_bind_quick_rig(Operator):
    bl_idname = "gameflow.bind_quick_rig"
    bl_label = "Bind Model"
    bl_description = "Parent the selected mesh to the GameFlow rig using Blender automatic weights"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = bpy.data.objects.get(ARMATURE_NAME)
        mesh = _active_mesh(context)
        if rig is None:
            self.report({'WARNING'}, "Build the rig first")
            return {'CANCELLED'}
        if mesh is None:
            targets = [o for o in context.scene.objects if o.type == 'MESH' and o.get("gameflow_rig_target")]
            mesh = targets[0] if targets else None
        if mesh is None:
            self.report({'WARNING'}, "Select the mesh you want to bind")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT') if context.object and context.object.mode != 'OBJECT' else None
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        rig.select_set(True)
        context.view_layer.objects.active = rig
        try:
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        except RuntimeError as exc:
            self.report({'ERROR'}, f"Auto weights failed: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Model bound to GameFlow rig with automatic weights")
        return {'FINISHED'}


class GAMEFLOW_OT_clear_rig_guides(Operator):
    bl_idname = "gameflow.clear_rig_guides"
    bl_label = "Clear Rig Guides"
    bl_description = "Remove the visible GameFlow snap markers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _clear_guides()
        return {'FINISHED'}


class VIEW3D_PT_gameflow_quick_rig(Panel):
    bl_label = "Quick Rig"
    bl_idname = "VIEW3D_PT_gameflow_quick_rig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GameFlow"
    bl_parent_id = "VIEW3D_PT_gameflow"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = get_prefs(context)
        return prefs is not None and prefs.creator_mode == 'BUILD'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Rig a character without bone-editing first.", icon='ARMATURE_DATA')
        layout.label(text="1. Select your character mesh")
        layout.operator("gameflow.create_rig_guides", text="1  Create Snap Guides", icon='EMPTY_AXIS')
        layout.label(text="2. Move the labeled dots onto the joints")
        layout.operator("gameflow.build_rig_from_guides", text="2  Build Rig", icon='ARMATURE_DATA')
        layout.label(text="3. Select the mesh and bind it")
        layout.operator("gameflow.bind_quick_rig", text="3  Bind Model", icon='LINKED')
        layout.separator()
        layout.operator("gameflow.clear_rig_guides", text="Clear Guides", icon='TRASH')
        layout.label(text="Best for simple humanoid characters. Complex creatures still need manual rigging.", icon='INFO')


classes = (
    GAMEFLOW_OT_create_rig_guides,
    GAMEFLOW_OT_build_rig_from_guides,
    GAMEFLOW_OT_bind_quick_rig,
    GAMEFLOW_OT_clear_rig_guides,
    VIEW3D_PT_gameflow_quick_rig,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
