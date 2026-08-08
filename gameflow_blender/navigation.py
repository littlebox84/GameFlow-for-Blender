import bpy
import math
import time
from mathutils import Vector, Quaternion
from bpy.types import Operator

from . import state
from .preferences import get_prefs


def region_under_mouse(context, event):
    window = context.window
    if window is None or window.screen is None:
        return None

    mx, my = event.mouse_x, event.mouse_y
    for area in window.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        for region in area.regions:
            if region.type != 'WINDOW':
                continue
            if region.x <= mx < region.x + region.width and region.y <= my < region.y + region.height:
                space = area.spaces.active
                return area, region, space, space.region_3d
    return None


def find_any_view3d():
    wm = bpy.context.window_manager
    if wm is None:
        return None
    for window in wm.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for region in area.regions:
                if region.type == 'WINDOW':
                    return window, screen, area, region, area.spaces.active
    return None


def start_navigation():
    if state.is_alive():
        return True
    if state.running and not state.is_alive():
        state.clear_running()

    target = find_any_view3d()
    if target is None:
        return False

    window, screen, area, region, space = target
    try:
        with bpy.context.temp_override(
            window=window,
            screen=screen,
            area=area,
            region=region,
            space_data=space,
        ):
            bpy.ops.view3d.gameflow_navigation('INVOKE_DEFAULT')
        return True
    except RuntimeError:
        return False


class VIEW3D_OT_gameflow_navigation(Operator):
    bl_idname = "view3d.gameflow_navigation"
    bl_label = "GameFlow Navigation"
    bl_description = "Persistent game-style viewport navigation"
    bl_options = {'REGISTER'}

    _timer = None
    _keys = None
    _rmb_down = False
    _rmb_origin = None
    _last_mouse = None
    _last_tick = None
    _last_rmb_press = 0.0
    _target = None
    _velocity = None
    _ignore_warp_event = False

    def invoke(self, context, event):
        if state.is_alive():
            self.report({'INFO'}, "GameFlow navigation is already running")
            return {'CANCELLED'}

        state.mark_alive()
        state.stop_requested = False
        self._keys = set()
        self._rmb_down = False
        self._rmb_origin = None
        self._last_mouse = Vector((event.mouse_x, event.mouse_y))
        self._last_tick = time.perf_counter()
        self._last_rmb_press = 0.0
        self._target = region_under_mouse(context, event)
        self._velocity = Vector((0.0, 0.0, 0.0))
        self._ignore_warp_event = False

        self._timer = context.window_manager.event_timer_add(1.0 / 120.0, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, "GameFlow navigation started")
        return {'RUNNING_MODAL'}

    def finish(self, context, message="GameFlow navigation paused"):
        if self._timer is not None:
            try:
                context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError, RuntimeError):
                pass
            self._timer = None

        state.clear_running()
        if self._keys is not None:
            self._keys.clear()
        self._rmb_down = False
        self._rmb_origin = None
        self._target = None
        self._velocity = Vector((0.0, 0.0, 0.0))
        self._ignore_warp_event = False
        self.report({'INFO'}, message)

    def update_target(self, context, event):
        target = region_under_mouse(context, event)
        if target is not None:
            self._target = target
        return target

    def open_context_menu(self, context, target):
        if target is None:
            return
        area, region, space, _rv3d = target
        try:
            with context.temp_override(
                window=context.window,
                screen=context.window.screen,
                area=area,
                region=region,
                space_data=space,
            ):
                bpy.ops.wm.call_menu(name='VIEW3D_MT_object_context_menu')
        except RuntimeError:
            pass

    def _warp_pointer_if_needed(self, context, event, target):
        prefs = get_prefs(context)
        if not prefs or not prefs.edge_wrap_look or target is None or context.window is None:
            return

        _area, region, _space, _rv3d = target
        margin = min(prefs.edge_wrap_margin, max(10, min(region.width, region.height) // 4))
        left = region.x + margin
        right = region.x + region.width - margin
        bottom = region.y + margin
        top = region.y + region.height - margin

        if left <= event.mouse_x <= right and bottom <= event.mouse_y <= top:
            return

        center_x = region.x + region.width // 2
        center_y = region.y + region.height // 2
        try:
            context.window.cursor_warp(center_x, center_y)
            self._last_mouse = Vector((center_x, center_y))
            self._ignore_warp_event = True
        except (ReferenceError, RuntimeError):
            pass

    def _restore_pointer(self, context):
        prefs = get_prefs(context)
        if not prefs or not prefs.restore_cursor_after_look or self._rmb_origin is None or context.window is None:
            return
        try:
            context.window.cursor_warp(int(self._rmb_origin.x), int(self._rmb_origin.y))
            self._last_mouse = self._rmb_origin.copy()
            self._ignore_warp_event = True
        except (ReferenceError, RuntimeError):
            pass

    def update_look(self, context, event, target):
        if not self._rmb_down or target is None:
            self._last_mouse = Vector((event.mouse_x, event.mouse_y))
            return

        if self._ignore_warp_event:
            self._ignore_warp_event = False
            self._last_mouse = Vector((event.mouse_x, event.mouse_y))
            return

        current = Vector((event.mouse_x, event.mouse_y))
        delta = current - self._last_mouse
        self._last_mouse = current
        if delta.length_squared == 0:
            return

        prefs = get_prefs(context)
        sensitivity = prefs.look_sensitivity if prefs else 0.003
        x_sign = 1.0 if (prefs and prefs.invert_x) else -1.0
        y_sign = 1.0 if (prefs and prefs.invert_y) else -1.0

        area, _region, _space, rv3d = target
        rotation = rv3d.view_rotation.copy()

        yaw = Quaternion((0.0, 0.0, 1.0), delta.x * sensitivity * x_sign)
        yawed = yaw @ rotation
        right_axis = yawed @ Vector((1.0, 0.0, 0.0))
        pitch = Quaternion(right_axis, delta.y * sensitivity * y_sign)
        candidate = (pitch @ yawed).normalized()

        up_direction = candidate @ Vector((0.0, 1.0, 0.0))
        rv3d.view_rotation = candidate if up_direction.z > 0.02 else yawed.normalized()
        area.tag_redraw()
        self._warp_pointer_if_needed(context, event, target)

    def handle_key(self, event):
        mapping = {
            'W': 'W', 'A': 'A', 'S': 'S', 'D': 'D', 'Q': 'Q', 'E': 'E',
            'LEFT_SHIFT': 'SHIFT', 'RIGHT_SHIFT': 'SHIFT',
        }
        key = mapping.get(event.type)
        if key is None:
            return False
        if event.value == 'PRESS':
            self._keys.add(key)
        elif event.value == 'RELEASE':
            self._keys.discard(key)
        return True

    def update_movement(self, context):
        now = time.perf_counter()
        dt = min(now - self._last_tick, 0.05)
        self._last_tick = now

        if self._target is None:
            return

        area, _region, _space, rv3d = self._target
        if context.window is None or context.window.screen is None:
            self._target = None
            return

        if not any(current_area == area for current_area in context.window.screen.areas):
            self._target = None
            self._keys.clear()
            self._rmb_down = False
            self._rmb_origin = None
            self._velocity = Vector((0.0, 0.0, 0.0))
            return

        prefs = get_prefs(context)
        rotation = rv3d.view_rotation
        forward = rotation @ Vector((0.0, 0.0, -1.0))
        right = rotation @ Vector((1.0, 0.0, 0.0))
        if prefs and prefs.vertical_mode == 'VIEW':
            up = rotation @ Vector((0.0, 1.0, 0.0))
        else:
            up = Vector((0.0, 0.0, 1.0))

        direction = Vector((0.0, 0.0, 0.0))
        if 'W' in self._keys: direction += forward
        if 'S' in self._keys: direction -= forward
        if 'A' in self._keys: direction -= right
        if 'D' in self._keys: direction += right
        if 'Q' in self._keys: direction -= up
        if 'E' in self._keys: direction += up

        speed = prefs.movement_speed if prefs else 4.0
        if self._rmb_down:
            speed *= prefs.rmb_speed_multiplier if prefs else 2.5
        if 'SHIFT' in self._keys:
            speed *= prefs.sprint_multiplier if prefs else 2.0

        scene_scale = max(0.15, min(rv3d.view_distance * 0.18, 8.0))
        target_velocity = Vector((0.0, 0.0, 0.0))
        if direction.length_squared > 0:
            direction.normalize()
            target_velocity = direction * speed * scene_scale

        if prefs and prefs.smooth_movement:
            rate = prefs.acceleration if target_velocity.length_squared > 0 else prefs.deceleration
            alpha = 1.0 - math.exp(-rate * dt)
            self._velocity = self._velocity.lerp(target_velocity, alpha)
        else:
            self._velocity = target_velocity

        if self._velocity.length_squared > 1e-8:
            rv3d.view_location += self._velocity * dt
            area.tag_redraw()

    def modal(self, context, event):
        if state.stop_requested:
            self.finish(context)
            return {'FINISHED'}

        if context.window is None or context.window.screen is None:
            self.finish(context, "GameFlow paused during file load")
            return {'CANCELLED'}

        if event.type == 'F8' and event.value == 'PRESS':
            self.finish(context)
            return {'FINISHED'}

        target_now = self.update_target(context, event)

        if target_now is None and event.type != 'TIMER':
            if self._rmb_down:
                self._restore_pointer(context)
            self._rmb_down = False
            self._rmb_origin = None
            self._keys.clear()
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE':
            return {'PASS_THROUGH'}

        if self.handle_key(event):
            return {'RUNNING_MODAL'}

        if event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                now = time.perf_counter()
                prefs = get_prefs(context)
                double_time = prefs.double_click_time if prefs else 0.32
                if now - self._last_rmb_press <= double_time:
                    self._rmb_down = False
                    self._rmb_origin = None
                    self._last_rmb_press = 0.0
                    self.open_context_menu(context, target_now or self._target)
                    return {'RUNNING_MODAL'}

                self._last_rmb_press = now
                self._rmb_down = True
                self._rmb_origin = Vector((event.mouse_x, event.mouse_y))
                self._last_mouse = self._rmb_origin.copy()
                self._ignore_warp_event = False
                return {'RUNNING_MODAL'}

            if event.value == 'RELEASE':
                self._rmb_down = False
                self._restore_pointer(context)
                self._rmb_origin = None
                return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            if self._rmb_down:
                self.update_look(context, event, target_now or self._target)
                return {'RUNNING_MODAL'}
            self._last_mouse = Vector((event.mouse_x, event.mouse_y))
            return {'PASS_THROUGH'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} and event.value == 'PRESS':
            target = target_now or self._target
            if target is None:
                return {'PASS_THROUGH'}

            prefs = get_prefs(context)
            factor = prefs.wheel_zoom_factor if prefs else 0.88
            zoom_in = event.type == 'WHEELUPMOUSE'
            if prefs and prefs.invert_zoom:
                zoom_in = not zoom_in

            area, _region, _space, rv3d = target
            if zoom_in:
                rv3d.view_distance = max(0.01, rv3d.view_distance * factor)
            else:
                rv3d.view_distance = min(1_000_000.0, rv3d.view_distance / factor)
            area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'TIMER':
            state.mark_alive()
            self.update_movement(context)
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}


classes = (VIEW3D_OT_gameflow_navigation,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    state.stop_requested = True
    state.running = False
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
