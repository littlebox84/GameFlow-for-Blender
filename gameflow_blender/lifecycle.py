import bpy
from bpy.app.handlers import persistent

from . import state
from .preferences import get_prefs
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls


def _delayed_start():
    prefs = get_prefs()
    if not prefs or not prefs.enabled or state.safe_mode or not prefs.auto_start:
        return None
    if start_navigation():
        return None
    return 0.35


def _delayed_restart_after_load():
    prefs = get_prefs()
    if not prefs or not prefs.enabled or state.safe_mode or not prefs.restart_after_file_load:
        state.restart_after_load = False
        return None
    if start_navigation():
        state.restart_after_load = False
        return None
    return 0.35


@persistent
def gameflow_load_pre(_dummy):
    prefs = get_prefs()
    state.restart_after_load = bool(
        prefs and prefs.enabled and not state.safe_mode and prefs.restart_after_file_load
    )
    state.clear_running()


@persistent
def gameflow_load_post(_dummy):
    prefs = get_prefs()
    if prefs and prefs.enabled:
        if state.safe_mode:
            try:
                restore_saved_controls(delete_backup=False)
            except Exception:
                pass
        else:
            try:
                apply_gameflow_keymap(prefs.keymap_mode)
            except Exception:
                pass

    if state.restart_after_load and not bpy.app.timers.is_registered(_delayed_restart_after_load):
        bpy.app.timers.register(_delayed_restart_after_load, first_interval=0.45)


def register_handlers():
    if gameflow_load_pre not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(gameflow_load_pre)
    if gameflow_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(gameflow_load_post)

    prefs = get_prefs()
    if prefs and prefs.enabled and not state.safe_mode and prefs.auto_start and not bpy.app.timers.is_registered(_delayed_start):
        bpy.app.timers.register(_delayed_start, first_interval=0.5)


def unregister_handlers():
    if gameflow_load_pre in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(gameflow_load_pre)
    if gameflow_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(gameflow_load_post)
    if bpy.app.timers.is_registered(_delayed_start):
        bpy.app.timers.unregister(_delayed_start)
    if bpy.app.timers.is_registered(_delayed_restart_after_load):
        bpy.app.timers.unregister(_delayed_restart_after_load)
