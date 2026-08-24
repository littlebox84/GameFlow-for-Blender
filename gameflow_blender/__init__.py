bl_info = {
    "name": "GameFlow for Blender",
    "author": "Jared + OpenAI",
    "version": (0, 6, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar > GameFlow",
    "description": "From player to creator — game-style navigation, beginner Paint Studio, Quick Rig snap guides, creator tools, viewport HUD, health diagnostics, Safe Mode, and Build Assist",
    "category": "3D View",
}

import bpy

from . import state
from . import preferences
from . import navigation
from . import build_tools
from . import build_assist
from . import health
from . import safe_mode
from . import hud
from . import ui
from . import paint_tools
from . import rigging
from . import keymap
from . import lifecycle


def register():
    preferences.register()
    navigation.register()
    build_tools.register()
    health.register()
    hud.register()
    ui.register()
    # Child panels must register after their parent GameFlow panel.
    safe_mode.register()
    build_assist.register()
    paint_tools.register()
    rigging.register()
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

    rigging.unregister()
    paint_tools.unregister()
    build_assist.unregister()
    safe_mode.unregister()
    ui.unregister()
    hud.unregister()
    health.unregister()
    build_tools.unregister()
    navigation.unregister()
    preferences.unregister()
