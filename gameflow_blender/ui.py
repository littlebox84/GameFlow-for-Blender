import bpy
import platform
from bpy.types import Operator, Panel

from . import state
from .preferences import get_prefs, PRESETS
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls, backup_path, save_preferences

GAMEFLOW_VERSION = "0.2.1"

STEAM_MAPPING = """GameFlow for Blender — Steam Input mapping
Left Stick: W / A / S / D
Right Stick: Mouse
Left Trigger: Right Mouse
Right Trigger: Left Mouse
Left Bumper: Q
Right Bumper: E
Left Stick Click: Shift
A: Enter
B: Esc
X: F3
Y: F
D-pad: Ctrl+1 / Ctrl+2 / Ctrl+3 / Ctrl+4
Menu/Start: F8
"""


class WM_OT_gameflow_enable(Operator):
    bl_idname = "wm.gameflow_enable"
    bl_label = "Enable Full GameFlow Controls"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}
        try:
            changed = apply_gameflow_keymap(prefs.keymap_mode)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        prefs.enabled = True
        state.stop_requested = False
        started = start_navigation()
        save_preferences()
        self.report({'INFO'}, f"GameFlow enabled; {changed} conflicting shortcuts disabled")
        if not started:
            self.report({'WARNING'}, "Open a 3D Viewport and press F8 to start navigation")
        return {'FINISHED'}


class WM_OT_gameflow_disable(Operator):
    bl_idname = "wm.gameflow_disable"
    bl_label = "Disable GameFlow + Restore Controls"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs:
            prefs.enabled = False
        state.stop_requested = True
        try:
            count = restore_saved_controls(delete_backup=False)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        save_preferences()
        self.report({'INFO'}, f"Restored {count} saved shortcut states")
        return {'FINISHED'}


class WM_OT_gameflow_toggle_navigation(Operator):
    bl_idname = "wm.gameflow_toggle_navigation"
    bl_label = "Pause / Resume GameFlow Navigation"

    def execute(self, context):
        prefs = get_prefs(context)
        if state.is_alive():
            state.stop_requested = True
            return {'FINISHED'}
        if prefs and not prefs.enabled:
            self.report({'INFO'}, "Enable Full GameFlow Controls first")
            return {'CANCELLED'}
        return {'FINISHED'} if start_navigation() else {'CANCELLED'}


class WM_OT_gameflow_reapply_keymap(Operator):
    bl_idname = "wm.gameflow_reapply_keymap"
    bl_label = "Reapply GameFlow Keymap"

    def execute(self, context):
        prefs = get_prefs(context)
        changed = apply_gameflow_keymap(prefs.keymap_mode if prefs else 'MINIMAL')
        save_preferences()
        self.report({'INFO'}, f"GameFlow keymap applied; {changed} shortcuts disabled")
        return {'FINISHED'}


class WM_OT_gameflow_restore_saved(Operator):
    bl_idname = "wm.gameflow_restore_saved"
    bl_label = "Restore Saved Blender Controls"

    def execute(self, context):
        count = restore_saved_controls(delete_backup=False)
        save_preferences()
        self.report({'INFO'}, f"Restored {count} shortcut states")
        return {'FINISHED'}


class WM_OT_gameflow_reset_settings(Operator):
    bl_idname = "wm.gameflow_reset_settings"
    bl_label = "Reset GameFlow Settings"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}
        prefs.preset = 'GAMEFLOW'
        for name, value in PRESETS['GAMEFLOW'].items():
            setattr(prefs, name, value)
        prefs.keymap_mode = 'MINIMAL'
        prefs.smooth_movement = True
        prefs.invert_zoom = False
        prefs.double_click_time = 0.32
        prefs.edge_wrap_look = True
        prefs.edge_wrap_margin = 42
        prefs.restore_cursor_after_look = True
        prefs.auto_start = True
        prefs.restart_after_file_load = True
        save_preferences()
        self.report({'INFO'}, "GameFlow settings reset")
        return {'FINISHED'}


class WM_OT_gameflow_copy_steam_mapping(Operator):
    bl_idname = "wm.gameflow_copy_steam_mapping"
    bl_label = "Copy Steam Input Mapping"

    def execute(self, context):
        context.window_manager.clipboard = STEAM_MAPPING
        self.report({'INFO'}, "Steam Input mapping copied")
        return {'FINISHED'}


class WM_OT_gameflow_copy_diagnostics(Operator):
    bl_idname = "wm.gameflow_copy_diagnostics"
    bl_label = "Copy Diagnostics"
    bl_description = "Copy useful GameFlow and Blender version details for bug reports"

    def execute(self, context):
        prefs = get_prefs(context)
        lines = [
            f"GameFlow: {GAMEFLOW_VERSION}",
            f"Blender: {bpy.app.version_string}",
            f"OS: {platform.system()} {platform.release()}",
            f"GameFlow enabled: {bool(prefs and prefs.enabled)}",
            f"Navigation alive: {state.is_alive()}",
            f"Preset: {prefs.preset if prefs else 'unavailable'}",
            f"Keymap mode: {prefs.keymap_mode if prefs else 'unavailable'}",
            f"Unlimited RMB look: {bool(prefs and prefs.edge_wrap_look)}",
            f"Reconnect after file load: {bool(prefs and prefs.restart_after_file_load)}",
        ]
        context.window_manager.clipboard = "\n".join(lines)
        self.report({'INFO'}, "GameFlow diagnostics copied")
        return {'FINISHED'}


class VIEW3D_PT_gameflow(Panel):
    bl_label = "GameFlow"
    bl_idname = "VIEW3D_PT_gameflow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GameFlow"

    def draw(self, context):
        layout = self.layout
        prefs = get_prefs(context)
        if prefs is None:
            layout.label(text="GameFlow preferences unavailable")
            return

        hero = layout.box()
        hero.label(text="GameFlow for Blender", icon='PLAY')
        hero.label(text="From player to creator.")
        hero.label(text=f"v{GAMEFLOW_VERSION} Public Alpha")

        status = layout.box()
        if prefs.enabled:
            alive = state.is_alive()
            status.label(text="GameFlow: ON", icon='CHECKMARK')
            status.label(text="Navigation: RUNNING" if alive else "Navigation: PAUSED")
            status.operator("wm.gameflow_toggle_navigation", text="Pause / Resume Navigation (F8)")
            status.operator("wm.gameflow_disable", text="Disable + Restore Blender Controls")
        else:
            status.label(text="One click enables the complete control layer.")
            status.operator("wm.gameflow_enable", text="Enable Full GameFlow Controls", icon='PLAY')

        controls = layout.box()
        controls.label(text="The basics", icon='INFO')
        controls.label(text="WASD  Move")
        controls.label(text="Q / E  Down / Up")
        controls.label(text="Hold RMB  Look + faster movement")
        controls.label(text="Shift  Sprint")
        controls.label(text="Scroll  Zoom")
        controls.label(text="Double RMB  Context menu")
        controls.label(text="F  Frame selected")

        feel = layout.box()
        feel.label(text="Feel")
        feel.prop(prefs, "preset", text="Preset")
        feel.prop(prefs, "movement_speed")
        feel.prop(prefs, "look_sensitivity")

        controller = layout.box()
        controller.prop(prefs, "show_controller", text="Controller / Steam Input", toggle=True)
        if prefs.show_controller:
            controller.label(text="Use Steam Input to map a controller")
            controller.operator("wm.gameflow_copy_steam_mapping")

        advanced = layout.box()
        advanced.prop(prefs, "show_advanced", text="Advanced Settings", toggle=True)
        if prefs.show_advanced:
            for prop in (
                "keymap_mode", "rmb_speed_multiplier", "sprint_multiplier",
                "smooth_movement", "wheel_zoom_factor", "vertical_mode",
                "invert_x", "invert_y", "invert_zoom", "double_click_time",
                "edge_wrap_look", "auto_start", "restart_after_file_load",
            ):
                advanced.prop(prefs, prop)
            if prefs.smooth_movement:
                advanced.prop(prefs, "acceleration")
                advanced.prop(prefs, "deceleration")
            if prefs.edge_wrap_look:
                advanced.prop(prefs, "edge_wrap_margin")
                advanced.prop(prefs, "restore_cursor_after_look")
            advanced.separator()
            advanced.operator("wm.gameflow_reapply_keymap")
            advanced.operator("wm.gameflow_restore_saved")
            advanced.operator("wm.gameflow_reset_settings")
            advanced.operator("wm.gameflow_copy_diagnostics", icon='COPYDOWN')
            advanced.label(text=f"Backup: {backup_path().name}")


classes = (
    WM_OT_gameflow_enable,
    WM_OT_gameflow_disable,
    WM_OT_gameflow_toggle_navigation,
    WM_OT_gameflow_reapply_keymap,
    WM_OT_gameflow_restore_saved,
    WM_OT_gameflow_reset_settings,
    WM_OT_gameflow_copy_steam_mapping,
    WM_OT_gameflow_copy_diagnostics,
    VIEW3D_PT_gameflow,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
