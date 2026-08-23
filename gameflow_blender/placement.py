import math

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from bpy_extras import view3d_utils

from .preferences import get_prefs


def _find_view3d(context, event=None):
    window = context.window
    if window is None or window.screen is None:
        return None
    if event is not None:
        mx, my = event.mouse_x, event.mouse_y
        for area in window.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for region in area.regions:
                if region.type == 'WINDOW' and region.x <= mx < region.x + region.width and region.y <= my < region.y + region.height:
                    return area, region, area.spaces.active, area.spaces.active.region_3d
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    return area, region, area.spaces.active, area.spaces.active.region_3d
    return None


def _make_primitive(context, primitive, location):
    ops = {
        'CUBE': bpy.ops.mesh.primitive_cube_add,
        'CYLINDER': bpy.ops.mesh.primitive_cylinder_add,
        'SPHERE': bpy.ops.mesh.primitive_uv_sphere_add,
        'PLANE': bpy.ops.mesh.primitive_plane_add,
        'CONE': bpy.ops.mesh.primitive_cone_add,
    }
    ops[primitive](location=location)
    obj = context.active_object
    if obj:
        obj.name = f'GF_{primitive.title()}'
    return obj


def _snap_value(value, step):
    if step <= 0:
        return value
    return round(value / step) * step


def _fallback_floor(origin, direction):
    if abs(direction.z) < 1e-7:
        return origin + direction.normalized() * 8.0
    t = -origin.z / direction.z
    if t <= 0:
        return origin + direction.normalized() * 8.0
    return origin + direction * t


class GAMEFLOW_OT_place_primitive(Operator):
    bl_idname = 'gameflow.place_primitive'
    bl_label = 'Place Object'
    bl_description = 'Preview an object under the mouse, then click to place it'
    bl_options = {'REGISTER', 'UNDO'}

    primitive: EnumProperty(
        items=[
            ('CUBE', 'Cube', 'Place cubes'),
            ('CYLINDER', 'Cylinder', 'Place cylinders'),
            ('SPHERE', 'Sphere', 'Place spheres'),
            ('PLANE', 'Plane', 'Place planes'),
            ('CONE', 'Cone', 'Place cones'),
        ],
        default='CUBE',
    )
    continuous: BoolProperty(name='Continuous Placement', default=True)

    _preview = None
    _target = None

    def _remove_preview(self):
        if self._preview is not None:
            try:
                bpy.data.objects.remove(self._preview, do_unlink=True)
            except (ReferenceError, RuntimeError):
                pass
            self._preview = None

    def _new_preview(self, context):
        obj = _make_primitive(context, self.primitive, context.scene.cursor.location)
        if obj is None:
            return False
        obj.display_type = 'WIRE'
        obj.show_in_front = True
        obj.hide_render = True
        obj['gameflow_preview'] = True
        self._preview = obj
        return True

    def _mouse_world(self, context, event):
        target = _find_view3d(context, event)
        if target is None:
            return None
        _area, region, _space, rv3d = target
        coord = (event.mouse_x - region.x, event.mouse_y - region.y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord).normalized()

        hit = False
        hit_location = None
        preview = self._preview
        hidden = False
        try:
            if preview is not None:
                preview.hide_viewport = True
                hidden = True
                context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()
            hit, hit_location, _normal, _face, _obj, _matrix = context.scene.ray_cast(depsgraph, origin, direction)
        except (ReferenceError, RuntimeError):
            hit = False
        finally:
            if preview is not None and hidden:
                try:
                    preview.hide_viewport = False
                    context.view_layer.update()
                except (ReferenceError, RuntimeError):
                    pass

        point = hit_location.copy() if hit and hit_location is not None else _fallback_floor(origin, direction)
        prefs = get_prefs(context)
        if prefs and prefs.placement_grid_snap:
            step = max(0.001, prefs.build_grid_step)
            point.x = _snap_value(point.x, step)
            point.y = _snap_value(point.y, step)
            point.z = _snap_value(point.z, step)
        return point

    def _confirm_preview(self, context):
        if self._preview is None:
            return False
        self._preview.display_type = 'TEXTURED'
        self._preview.show_in_front = False
        self._preview.hide_render = False
        if 'gameflow_preview' in self._preview:
            del self._preview['gameflow_preview']
        self._preview.name = f'GF_{self.primitive.title()}'
        self._preview = None
        if self.continuous:
            return self._new_preview(context)
        return True

    def invoke(self, context, event):
        self._target = _find_view3d(context, event)
        if self._target is None:
            self.report({'WARNING'}, 'Open a 3D Viewport to use placement mode')
            return {'CANCELLED'}
        if not self._new_preview(context):
            return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, 'Placement mode: move mouse, Left Click places, R rotates, Esc/Right Click exits')
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._preview is None:
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._remove_preview()
            return {'CANCELLED'}

        if event.type == 'MOUSEMOVE':
            point = self._mouse_world(context, event)
            if point is not None and self._preview is not None:
                self._preview.location = point
            return {'RUNNING_MODAL'}

        if event.type == 'R' and event.value == 'PRESS':
            prefs = get_prefs(context)
            degrees = prefs.build_rotation_step if prefs else 45.0
            self._preview.rotation_euler.z += math.radians(degrees)
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self._confirm_preview(context) and not self.continuous:
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        self._remove_preview()


classes = (GAMEFLOW_OT_place_primitive,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
