import math

import bpy
from bpy.props import EnumProperty, FloatProperty
from bpy.types import Operator
from mathutils import Vector

from .preferences import get_prefs


def _view3d_override(context):
    area = context.area
    if area is None or area.type != 'VIEW_3D' or context.window is None or context.window.screen is None:
        return None

    region = context.region if context.region and context.region.type == 'WINDOW' else None
    if region is None:
        region = next((candidate for candidate in area.regions if candidate.type == 'WINDOW'), None)
    if region is None:
        return None

    return context.temp_override(
        window=context.window,
        screen=context.window.screen,
        area=area,
        region=region,
        space_data=area.spaces.active,
    )


def _selected_objects(context):
    return [obj for obj in context.selected_objects if obj is not None]


def _active_object(context):
    return context.view_layer.objects.active


def _grid_step(context):
    prefs = get_prefs(context)
    return prefs.build_grid_step if prefs else 1.0


def _rotation_step(context):
    prefs = get_prefs(context)
    return math.radians(prefs.build_rotation_step if prefs else 45.0)


class GAMEFLOW_OT_add_primitive(Operator):
    bl_idname = "gameflow.add_primitive"
    bl_label = "Add GameFlow Primitive"
    bl_description = "Create a common object at the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    primitive: EnumProperty(
        items=[
            ('CUBE', "Cube", "Add a cube"),
            ('CYLINDER', "Cylinder", "Add a cylinder"),
            ('SPHERE', "Sphere", "Add a UV sphere"),
            ('PLANE', "Plane", "Add a plane"),
            ('CONE', "Cone", "Add a cone"),
        ],
        default='CUBE',
    )

    def execute(self, context):
        ops = {
            'CUBE': bpy.ops.mesh.primitive_cube_add,
            'CYLINDER': bpy.ops.mesh.primitive_cylinder_add,
            'SPHERE': bpy.ops.mesh.primitive_uv_sphere_add,
            'PLANE': bpy.ops.mesh.primitive_plane_add,
            'CONE': bpy.ops.mesh.primitive_cone_add,
        }
        ops[self.primitive](location=context.scene.cursor.location)
        obj = context.active_object
        if obj:
            obj.name = f"GF_{self.primitive.title()}"
        return {'FINISHED'}


class GAMEFLOW_OT_set_tool(Operator):
    bl_idname = "gameflow.set_tool"
    bl_label = "Set GameFlow Tool"
    bl_description = "Switch to a familiar Blender transform tool"

    tool: EnumProperty(
        items=[
            ('SELECT', "Select", "Select tool"),
            ('MOVE', "Move", "Move tool"),
            ('ROTATE', "Rotate", "Rotate tool"),
            ('SCALE', "Scale", "Scale tool"),
        ],
        default='SELECT',
    )

    def execute(self, context):
        names = {'SELECT': 'builtin.select_box', 'MOVE': 'builtin.move', 'ROTATE': 'builtin.rotate', 'SCALE': 'builtin.scale'}
        override = _view3d_override(context)
        if override is None:
            self.report({'WARNING'}, "Open GameFlow from a 3D Viewport")
            return {'CANCELLED'}
        try:
            with override:
                bpy.ops.wm.tool_set_by_id(name=names[self.tool])
        except RuntimeError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class GAMEFLOW_OT_nudge(Operator):
    bl_idname = "gameflow.nudge"
    bl_label = "Nudge Selection"
    bl_description = "Move selected objects by one GameFlow grid step"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(items=[('X', "X", "X axis"), ('Y', "Y", "Y axis"), ('Z', "Z", "Z axis")], default='X')
    direction: FloatProperty(default=1.0)

    def execute(self, context):
        objects = _selected_objects(context)
        if not objects:
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        amount = _grid_step(context) * (1.0 if self.direction >= 0 else -1.0)
        index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        for obj in objects:
            obj.location[index] += amount
        return {'FINISHED'}


class GAMEFLOW_OT_rotate_step(Operator):
    bl_idname = "gameflow.rotate_step"
    bl_label = "Rotate Selection"
    bl_description = "Rotate selected objects by the configured GameFlow angle"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(items=[('X', "X", "X axis"), ('Y', "Y", "Y axis"), ('Z', "Z", "Z axis")], default='Z')
    direction: FloatProperty(default=1.0)

    def execute(self, context):
        objects = _selected_objects(context)
        if not objects:
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        amount = _rotation_step(context) * (1.0 if self.direction >= 0 else -1.0)
        index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        for obj in objects:
            obj.rotation_euler[index] += amount
        return {'FINISHED'}


class GAMEFLOW_OT_duplicate_offset(Operator):
    bl_idname = "gameflow.duplicate_offset"
    bl_label = "Duplicate + Offset"
    bl_description = "Duplicate selected objects and move the copies by one build step"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(items=[('X', "X", "X axis"), ('Y', "Y", "Y axis"), ('Z', "Z", "Z axis")], default='X')

    def execute(self, context):
        if not _selected_objects(context):
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        step = _grid_step(context)
        index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        bpy.ops.object.duplicate(linked=False)
        for obj in _selected_objects(context):
            obj.location[index] += step
        return {'FINISHED'}


class GAMEFLOW_OT_drop_to_floor(Operator):
    bl_idname = "gameflow.drop_to_floor"
    bl_label = "Drop to Floor"
    bl_description = "Move selected objects so the bottom of each object rests on world Z = 0"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = _selected_objects(context)
        if not objects:
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        for obj in objects:
            if not getattr(obj, 'bound_box', None):
                continue
            world_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            obj.location.z -= min(corner.z for corner in world_corners)
        return {'FINISHED'}


class GAMEFLOW_OT_toggle_snap(Operator):
    bl_idname = "gameflow.toggle_snap"
    bl_label = "Toggle Build Snap"
    bl_description = "Turn Blender increment snapping on or off for GameFlow building"

    def execute(self, context):
        tools = context.scene.tool_settings
        tools.use_snap = not tools.use_snap
        if tools.use_snap:
            try:
                tools.snap_elements = {'INCREMENT'}
            except (TypeError, AttributeError):
                pass
        self.report({'INFO'}, "Build snapping ON" if tools.use_snap else "Build snapping OFF")
        return {'FINISHED'}


class GAMEFLOW_OT_focus_selected(Operator):
    bl_idname = "gameflow.focus_selected"
    bl_label = "Focus Selected"
    bl_description = "Frame the selected object in the current 3D viewport"

    def execute(self, context):
        if not _selected_objects(context):
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        override = _view3d_override(context)
        if override is None:
            return {'CANCELLED'}
        try:
            with override:
                bpy.ops.view3d.view_selected(use_all_regions=False)
        except RuntimeError:
            return {'CANCELLED'}
        return {'FINISHED'}


class GAMEFLOW_OT_quick_material(Operator):
    bl_idname = "gameflow.quick_material"
    bl_label = "GameFlow Quick Material"
    bl_description = "Apply a simple beginner-friendly material preset"
    bl_options = {'REGISTER', 'UNDO'}

    material: EnumProperty(
        items=[
            ('PLASTIC', "Plastic", "Smooth plastic"),
            ('METAL', "Metal", "Metallic material"),
            ('MATTE', "Matte", "Rough matte material"),
            ('GLASS', "Glass", "Transparent glass-like material"),
            ('GLOW', "Glow", "Emission material"),
        ],
        default='PLASTIC',
    )

    def execute(self, context):
        obj = _active_object(context)
        if obj is None or not hasattr(obj.data, 'materials'):
            self.report({'INFO'}, "Select a mesh object first")
            return {'CANCELLED'}

        name = f"GameFlow_{self.material.title()}"
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.18, 0.42, 0.8, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.0
            bsdf.inputs['Roughness'].default_value = 0.4
            if self.material == 'METAL':
                bsdf.inputs['Metallic'].default_value = 0.9
                bsdf.inputs['Roughness'].default_value = 0.25
            elif self.material == 'MATTE':
                bsdf.inputs['Roughness'].default_value = 0.85
            elif self.material == 'GLASS':
                bsdf.inputs['Roughness'].default_value = 0.08
                if 'Transmission Weight' in bsdf.inputs:
                    bsdf.inputs['Transmission Weight'].default_value = 0.9
            elif self.material == 'GLOW':
                if 'Emission Color' in bsdf.inputs:
                    bsdf.inputs['Emission Color'].default_value = (0.08, 0.4, 1.0, 1.0)
                if 'Emission Strength' in bsdf.inputs:
                    bsdf.inputs['Emission Strength'].default_value = 3.0

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        return {'FINISHED'}


classes = (
    GAMEFLOW_OT_add_primitive,
    GAMEFLOW_OT_set_tool,
    GAMEFLOW_OT_nudge,
    GAMEFLOW_OT_rotate_step,
    GAMEFLOW_OT_duplicate_offset,
    GAMEFLOW_OT_drop_to_floor,
    GAMEFLOW_OT_toggle_snap,
    GAMEFLOW_OT_focus_selected,
    GAMEFLOW_OT_quick_material,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
