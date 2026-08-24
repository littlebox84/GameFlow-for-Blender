import bpy
import blf
import gpu
from bpy.types import SpaceView3D
from gpu_extras.batch import batch_for_shader

from . import state
from .preferences import get_prefs

_draw_handle = None

MODE_COLORS = {
    'NAVIGATE': (0.16, 0.50, 1.00, 0.96),
    'BUILD': (1.00, 0.47, 0.12, 0.96),
    'PAINT': (0.68, 0.30, 1.00, 0.96),
}


def _draw_rect(x, y, width, height, color):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    vertices = ((x, y), (x + width, y), (x + width, y + height), (x, y + height))
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
    return {'NAVIGATE': 'EXPLORE', 'BUILD': 'BUILD', 'PAINT': 'PAINT'}.get(mode, mode)


def _position(region, width, height, corner, margin=18):
    if corner == 'TOP_LEFT':
        return margin, region.height - height - margin
    if corner == 'BOTTOM_LEFT':
        return margin, margin
    if corner == 'BOTTOM_RIGHT':
        return max(margin, region.width - width - margin), margin
    return max(margin, region.width - width - margin), region.height - height - margin


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
    width = 300 if full else 236
    height = 118 if full else 48
    x, y = _position(region, width, height, prefs.hud_corner)

    accent = MODE_COLORS.get(prefs.creator_mode, MODE_COLORS['NAVIGATE'])
    if state.safe_mode:
        accent = (0.45, 0.48, 0.54, 0.96)

    _draw_rect(x, y, width, height, (0.018, 0.022, 0.030, 0.84))
    _draw_rect(x, y + height - 3, width, 3, accent)

    if state.safe_mode:
        status = 'SAFE'
        status_color = (0.72, 0.76, 0.82, 1.0)
    elif state.is_alive():
        status = 'READY'
        status_color = (0.45, 1.0, 0.62, 1.0)
    else:
        status = 'PAUSED'
        status_color = (1.0, 0.72, 0.35, 1.0)

    mode = _mode_label(prefs.creator_mode)
    _text(f"GAMEFLOW · {mode}", x + 13, y + height - 24, 13)
    _text(status, x + width - 62, y + height - 24, 11, status_color)

    if not full:
        return

    obj = context.view_layer.objects.active if context.view_layer else None
    selected_name = obj.name if obj and obj.select_get() else 'Nothing selected'
    _text(selected_name, x + 13, y + height - 48, 11, (0.78, 0.82, 0.90, 1.0))

    if prefs.creator_mode == 'BUILD':
        snap = 'ON' if context.scene.tool_settings.use_snap else 'OFF'
        detail = f"Step {prefs.build_grid_step:g} · Rotate {prefs.build_rotation_step:g}° · Snap {snap}"
    elif prefs.creator_mode == 'PAINT':
        detail = "Pick a material from the GameFlow panel"
    else:
        detail = f"Speed {prefs.movement_speed:g} · Look {prefs.look_sensitivity:.4f}"
    _text(detail, x + 13, y + height - 70, 10, (0.70, 0.76, 0.86, 1.0))

    _text("WASD Move · RMB Look · Shift Sprint · Scroll Zoom", x + 13, y + 25, 9,
          (0.58, 0.64, 0.74, 1.0))
    _text("F Focus · F8 Pause/Resume", x + 13, y + 10, 9,
          (0.58, 0.64, 0.74, 1.0))


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
