bl_info = {
    "name": "GameFlow for Blender",
    "author": "Jared + OpenAI",
    "version": (0, 5, 5),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > GameFlow",
    "description": "From player to creator — game-style navigation, ghost placement, creator tools, health checks, and a dark viewport HUD",
    "category": "3D View",
}

import bpy

from . import state
from . import preferences
from . import registration
from . import navigation
from . import build_tools
from . import placement
from . import health
from . import hud
from . import ui
from . import keymap
from . import lifecycle


_CLASS_MODULES = (
    navigation,
    build_tools,
    placement,
    health,
    ui,
)


def _cleanup_stale_registered_classes():
    """Best-effort cleanup for Blender add-on reload/update cycles."""
    for module in reversed(_CLASS_MODULES):
        for cls in reversed(getattr(module, "classes", ())):
            registered = getattr(bpy.types, cls.__name__, None)
            if registered is None:
                continue
            try:
                bpy.utils.unregister_class(registered)
            except (RuntimeError, ValueError, ReferenceError):
                pass


def _safe_cleanup_preview_objects():
    """Remove orphan placement previews only when Blender exposes scene data.

    Blender 5.x temporarily replaces bpy.data with _RestrictData while an
    add-on is registering. Accessing bpy.data.objects during that window raises
    an exception. Returning early here lets registration finish; later timer,
    file-load, placement, and unregister calls perform normal cleanup once
    bpy.data is available again.
    """
    try:
        objects = bpy.data.objects
    except (AttributeError, RuntimeError, ReferenceError):
        return 0

    removed = 0
    for obj in list(objects):
        try:
            if obj.get('gameflow_preview', False):
                objects.remove(obj, do_unlink=True)
                removed += 1
        except (ReferenceError, RuntimeError):
            pass
    return removed


def register():
    registration.register_preferences(preferences)
    _cleanup_stale_registered_classes()

    # Route every early preview-cleanup path through a Blender-5-safe guard
    # before placement/lifecycle registration can touch bpy.data.objects.
    placement.cleanup_preview_objects = _safe_cleanup_preview_objects
    lifecycle.cleanup_preview_objects = _safe_cleanup_preview_objects

    navigation.register()
    build_tools.register()
    placement.register()
    health.register()
    hud.register()
    ui.register()
    keymap.register_addon_keymaps()
    lifecycle.register_handlers()


def unregister():
    prefs = preferences.get_prefs()
    state.stop_requested = True
    state.clear_running()

    lifecycle.unregister_handlers()
    keymap.unregister_addon_keymaps()

    if prefs and prefs.restore_controls_on_disable:
        try:
            keymap.restore_saved_controls(delete_backup=False)
            keymap.save_preferences()
        except Exception:
            pass

    ui.unregister()
    hud.unregister()
    health.unregister()
    placement.unregister()
    build_tools.unregister()
    navigation.unregister()
    preferences.unregister()
