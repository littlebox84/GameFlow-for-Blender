import bpy
from bpy.types import Operator

from . import state
from .preferences import get_prefs
from .keymap import backup_path, apply_gameflow_keymap, restore_saved_controls, save_preferences
from .navigation import start_navigation


SUPPORTED_MIN = (4, 2, 0)


def health_snapshot(context=None):
    context = context or bpy.context
    prefs = get_prefs(context)
    has_view3d = any(
        area.type == 'VIEW_3D'
        for window in context.window_manager.windows
        if window.screen
        for area in window.screen.areas
    )
    backup_exists = backup_path().exists()
    version_ok = bpy.app.version >= SUPPORTED_MIN
    return {
        'version_ok': version_ok,
        'has_view3d': has_view3d,
        'preferences': prefs is not None,
        'enabled': bool(prefs and prefs.enabled),
        'navigation': state.is_alive(),
        'backup': backup_exists,
        'safe_mode': bool(prefs and prefs.safe_mode),
        'hud': bool(prefs and prefs.hud_mode != 'OFF'),
    }


def health_text(context=None):
    data = health_snapshot(context)

    def mark(value):
        return 'OK' if value else 'CHECK'

    return '\n'.join([
        f"Blender version: {mark(data['version_ok'])}",
        f"3D Viewport: {mark(data['has_view3d'])}",
        f"Preferences: {mark(data['preferences'])}",
        f"GameFlow enabled: {'YES' if data['enabled'] else 'NO'}",
        f"Navigation: {'OK' if data['navigation'] else 'PAUSED'}",
        f"Keymap backup: {'FOUND' if data['backup'] else 'NOT YET CREATED'}",
        f"Safe Mode: {'ON' if data['safe_mode'] else 'OFF'}",
        f"Viewport HUD: {'ON' if data['hud'] else 'OFF'}",
    ])


class GAMEFLOW_OT_health_check(Operator):
    bl_idname = 'gameflow.health_check'
    bl_label = 'Run GameFlow Health Check'
    bl_description = 'Check GameFlow runtime, viewport, backup, and compatibility state'

    def execute(self, context):
        text = health_text(context)
        context.window_manager.clipboard = text
        snapshot = health_snapshot(context)
        problems = sum(1 for key in ('version_ok', 'has_view3d', 'preferences') if not snapshot[key])
        self.report(
            {'WARNING'} if problems else {'INFO'},
            'Health check found items to review; details copied' if problems else 'GameFlow health check OK; details copied',
        )
        return {'FINISHED'}


class GAMEFLOW_OT_safe_mode(Operator):
    bl_idname = 'gameflow.safe_mode'
    bl_label = 'Toggle GameFlow Safe Mode'
    bl_description = 'Keep GameFlow creator tools while restoring normal Blender key bindings'

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}

        if not prefs.safe_mode:
            if prefs.enabled and backup_path().exists():
                try:
                    restore_saved_controls(delete_backup=False)
                except Exception as exc:
                    self.report({'ERROR'}, f'Could not restore Blender controls: {exc}')
                    return {'CANCELLED'}
            prefs.safe_mode = True
            state.stop_requested = True
            save_preferences()
            self.report({'INFO'}, 'Safe Mode ON: Blender controls active; Creator tools remain available')
            return {'FINISHED'}

        prefs.safe_mode = False
        if prefs.enabled:
            try:
                apply_gameflow_keymap(prefs.keymap_mode)
            except Exception as exc:
                self.report({'ERROR'}, f'Could not reapply GameFlow controls: {exc}')
                return {'CANCELLED'}
            state.stop_requested = False
            start_navigation()
        save_preferences()
        self.report({'INFO'}, 'Safe Mode OFF: GameFlow controls restored')
        return {'FINISHED'}


classes = (GAMEFLOW_OT_health_check, GAMEFLOW_OT_safe_mode)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
