import bpy
import blf
import gpu
from bpy.types import SpaceView3D
from gpu_extras.batch import batch_for_shader

from . import state
from .preferences import get_prefs

_draw_handle = None


def _draw_rect(x, y, width, height, color):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    vertices = (
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
    )
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float('color', color)
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _text(text, x, y, size=13, color=(0.92, 0.94, 0.98, 1.0)):
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, str(text))


def _mode_label(mode):
    return {
        'NAVIGATE': 'EXPLORE',
        'BUILD': 'BUILD',
        'PAINT': 'PAINT',
    }.get(mode, mode)


def draw_hud():
    context = bpy.context
    prefs = get_prefs(context)
    if prefs is None or not prefs.enabled or prefs.hud_mode == 'OFF':
        return
    if context.area is None or context.area.type != 'VIEW_3D':
        return

    region = context.region
    if region is None or region.type != 'WINDOW':
        return

    full = prefs.hud_mode == 'FULL'
    width = 285 if full else 220
    height = 150 if full else 78
    x = 18
    y = region.height - height - 18

    _draw_rect(x, y, width, height, (0.018, 0.022, 0.030, 0.86))
    _draw_rect(x, y + height - 4, width, 4, (0.16, 0.50, 1.0, 0.95))

    status = 'READY' if state.is_alive() else 'PAUSED'
    mode = _mode_label(prefs.creator_mode)
    _text(f"GAMEFLOW  ·  {mode}", x + 14, y + height - 27, 14)
    _text(status, x + width - 66, y + height - 27, 12,
          (0.45, 1.0, 0.62, 1.0) if status == 'READY' else (1.0, 0.72, 0.35, 1.0))

    obj = context.view_layer.objects.active if context.view_layer else None
    selected_name = obj.name if obj and obj.select_get() else 'None'
    _text(f"Selected: {selected_name}", x + 14, y + height - 52, 12, (0.78, 0.82, 0.90, 1.0))

    if not full:
        return

    line_y = y + height - 76
    if prefs.creator_mode == 'BUILD':
        snap = 'ON' if context.scene.tool_settings.use_snap else 'OFF'
        _text(
            f"Grid: {prefs.build_grid_step:g}  ·  Rotate: {prefs.build_rotation_step:g}°  ·  Snap: {snap}",
            x + 14, line_y, 11, (0.72, 0.78, 0.88, 1.0)
        )
    elif prefs.creator_mode == 'PAINT':
        _text("Choose a material preset from the GameFlow panel", x + 14, line_y, 11,
              (0.72, 0.78, 0.88, 1.0))
    else:
        _text(f"Speed: {prefs.movement_speed:g}  ·  Look: {prefs.look_sensitivity:.4f}", x + 14, line_y, 11,
              (0.72, 0.78, 0.88, 1.0))

    _text("WASD Move   RMB Look   Shift Sprint   Scroll Zoom", x + 14, y + 34, 10,
          (0.60, 0.66, 0.76, 1.0))
    _text("F Focus   F8 Pause/Resume", x + 14, y + 17, 10,
          (0.60, 0.66, 0.76, 1.0))


def enable_hud():
    global _draw_handle
    if _draw_handle is None:
        _draw_handle = SpaceView3D.draw_handler_add(draw_hud, (), 'WINDOW', 'POST_PIXEL')


def disable_hud():
    global _draw_handle
    if _draw_handle is not None:
        try:
            SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except (ReferenceError, RuntimeError):
            pass
        _draw_handle = None


def register():
    enable_hud()


def unregister():
    disable_hud()
