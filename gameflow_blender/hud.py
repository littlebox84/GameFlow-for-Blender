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


def _text(text, x, y, size=13, color=(0.94, 0.96, 1.0, 1.0)):
    font_id = 0
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, str(text))


def _mode_label(mode):
    return {'NAVIGATE': 'EXPLORE', 'BUILD': 'BUILD', 'PAINT': 'PAINT'}.get(mode, mode)


def _position(region, width, height, location, margin=24):
    if location == 'BOTTOM_CENTER':
        return max(margin, (region.width - width) / 2), margin + 22
    if location == 'TOP_LEFT':
        return margin, region.height - height - margin
    if location == 'BOTTOM_LEFT':
        return margin, margin + 22
    if location == 'BOTTOM_RIGHT':
        return max(margin, region.width - width - margin), margin + 22
    return max(margin, region.width - width - margin), region.height - height - margin


def _context_hint(context, prefs):
    obj = context.view_layer.objects.active if context.view_layer else None
    selected = obj if obj and obj.select_get() else None

    if prefs.creator_mode == 'BUILD':
        if selected:
            return f"{selected.name} selected  ·  Move, rotate, duplicate, or drop it to the floor"
        return "Select something to build with, or add a new shape from the GameFlow panel"
    if prefs.creator_mode == 'PAINT':
        if selected:
            return f"{selected.name} selected  ·  Pick a material in the GameFlow panel"
        return "Select an object, then choose a material"
    if selected:
        return f"{selected.name} selected  ·  F Focus  ·  G Move  ·  R Rotate"
    return "WASD Move  ·  Hold RMB Look  ·  Shift Sprint  ·  Scroll Zoom"


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
    width = min(620, max(420, region.width - 120)) if full else min(390, max(280, region.width - 120))
    height = 76 if full else 42
    x, y = _position(region, width, height, prefs.hud_corner)

    accent = MODE_COLORS.get(prefs.creator_mode, MODE_COLORS['NAVIGATE'])
    if state.safe_mode:
        accent = (0.45, 0.48, 0.54, 0.96)

    _draw_rect(x, y, width, height, (0.018, 0.022, 0.030, 0.82))
    _draw_rect(x, y + height - 3, width, 3, accent)

    if state.safe_mode:
        status = 'SAFE MODE'
        status_color = (0.76, 0.80, 0.86, 1.0)
    elif state.is_alive():
        status = 'READY'
        status_color = (0.45, 1.0, 0.62, 1.0)
    else:
        status = 'PAUSED'
        status_color = (1.0, 0.72, 0.35, 1.0)

    mode = _mode_label(prefs.creator_mode)
    _text(f"GAMEFLOW  ·  {mode}", x + 16, y + height - 26, 14)
    _text(status, x + width - (92 if status == 'SAFE MODE' else 62), y + height - 26, 12, status_color)

    if full:
        _text(_context_hint(context, prefs), x + 16, y + 18, 12, (0.76, 0.82, 0.92, 1.0))


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
