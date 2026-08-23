bl_info = {
    "name": "GameFlow for Blender",
    "author": "Jared + OpenAI",
    "version": (0, 5, 1),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > GameFlow",
    "description": "From player to creator — game-style navigation, ghost placement, creator tools, health checks, and a dark viewport HUD",
    "category": "3D View",
}

import bpy

from . import state
from . import preferences
from . import navigation
from . import build_tools
from . import placement
from . import health
from . import hud
from . import ui
from . import keymap
from . import lifecycle


_CLASS_MODULES = (
    preferences,
    navigation,
    build_tools,
    placement,
    health,
    ui,
)


def _cleanup_stale_registered_classes():
    """Best-effort cleanup for Blender add-on reload/update cycles.

    Blender 5.x can leave RNA subclasses registered when a legacy add-on is
    reinstalled or reloaded before its previous module instance fully
    unregisters. Registering the replacement class then raises:
    "already registered as a subclass".

    We only touch class names owned by GameFlow's own module-level `classes`
    tuples. Normal first-time registration finds nothing and is a no-op.
    """
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
    # Repair stale RNA classes before registering this module generation.
    # This makes install/update/reload behavior much safer on Blender 5.x.
    _cleanup_stale_registered_classes()

    preferences.register()
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
