import bpy
from bpy.types import Operator

from . import state
from .preferences import get_prefs
from .keymap import backup_path


MIN_BLENDER_VERSION = (4, 2, 0)


def build_health_report(context):
    """Build a read-only GameFlow health report.

    This function intentionally does not modify keymaps, scene data, handlers,
    workspaces, or GameFlow runtime state. It only reads state after the user
    explicitly runs the operator.
    """
    prefs = get_prefs(context)

    try:
        has_view3d = any(
            area.type == 'VIEW_3D'
            for window in context.window_manager.windows
            if window.screen is not None
            for area in window.screen.areas
        )
    except Exception:
        has_view3d = False

    try:
        backup_exists = backup_path().exists()
    except Exception:
        backup_exists = False

    version_ok = bpy.app.version >= MIN_BLENDER_VERSION
    navigation_alive = state.is_alive()

    lines = [
        "GameFlow Health Check",
        "---------------------",
        f"Blender: {bpy.app.version_string}",
        f"Supported version: {'OK' if version_ok else 'CHECK'}",
        f"GameFlow preferences: {'OK' if prefs is not None else 'MISSING'}",
        f"3D Viewport available: {'YES' if has_view3d else 'NO'}",
        f"Navigation: {'RUNNING' if navigation_alive else 'PAUSED'}",
        f"Keymap backup: {'FOUND' if backup_exists else 'NOT CREATED'}",
    ]

    if prefs is not None:
        lines.extend([
            f"GameFlow enabled: {'YES' if prefs.enabled else 'NO'}",
            f"Creator mode: {prefs.creator_mode}",
            f"HUD mode: {prefs.hud_mode}",
            f"Preset: {prefs.preset}",
            f"Keymap mode: {prefs.keymap_mode}",
        ])

    return "\n".join(lines)


class GAMEFLOW_OT_health_check(Operator):
    bl_idname = "gameflow.health_check"
    bl_label = "GameFlow Health Check"
    bl_description = "Run a read-only GameFlow compatibility and runtime check"

    def execute(self, context):
        report = build_health_report(context)
        context.window_manager.clipboard = report

        prefs = get_prefs(context)
        if prefs is None:
            self.report({'WARNING'}, "GameFlow preferences missing; report copied to clipboard")
        else:
            self.report({'INFO'}, "GameFlow health report copied to clipboard")
        return {'FINISHED'}


classes = (GAMEFLOW_OT_health_check,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
