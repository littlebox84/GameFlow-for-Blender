bl_info = {
    "name": "GameFlow for Blender",
    "author": "Jared + OpenAI",
    "version": (0, 5, 2),
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


def register():
    # AddonPreferences needs a stronger Blender 5.x cleanup path because a
    # stale preferences RNA class may remain registered without being exposed
    # as bpy.types.GAMEFLOW_Preferences.
    registration.register_preferences(preferences)

    # Other GameFlow RNA types are usually discoverable through bpy.types.
    _cleanup_stale_registered_classes()
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
