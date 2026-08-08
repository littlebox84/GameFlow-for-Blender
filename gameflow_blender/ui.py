import bpy
import platform
from bpy.types import Operator, Panel

from . import state
from .preferences import get_prefs, PRESETS
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls, backup_path, save_preferences

GAMEFLOW_VERSION = "0.3.0"

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
    bl_description = "Back up conflicting shortcuts, apply GameFlow controls, and start navigation"

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
        try:
            changed = apply_gameflow_keymap(prefs.keymap_mode if prefs else 'MINIMAL')
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        save_preferences()
        self.report({'INFO'}, f"GameFlow keymap applied; {changed} shortcuts disabled")
        return {'FINISHED'}


class WM_OT_gameflow_restore_saved(Operator):
    bl_idname = "wm.gameflow_restore_saved"
    bl_label = "Restore Saved Blender Controls"

    def execute(self, context):
        try:
            count = restore_saved_controls(delete_backup=False)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        save_preferences()
        self.report({'INFO'}, f"Restored {count} shortcut states")
        return {'FINISHED'}


class WM_OT_gameflow_repair(Operator):
    bl_idname = "wm.gameflow_repair"
    bl_label = "Repair GameFlow"
    bl_description = "Repair stale runtime state, reapply the GameFlow keymap, and restart navigation if needed"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            self.report({'ERROR'}, "GameFlow preferences are unavailable")
            return {'CANCELLED'}

        try:
            prefs.enabled = True
            apply_gameflow_keymap(prefs.keymap_mode)
            if state.running and not state.is_alive():
                state.clear_running()
            state.stop_requested = False
            started = start_navigation()
            save_preferences()
        except Exception as exc:
            self.report({'ERROR'}, f"Repair failed: {exc}")
            return {'CANCELLED'}

        if started:
            self.report({'INFO'}, "GameFlow repaired and navigation is ready")
            return {'FINISHED'}

        self.report({'WARNING'}, "Controls repaired. Open a 3D Viewport and press F8 to resume navigation")
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
            f"Auto-start: {bool(prefs and prefs.auto_start)}",
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
            layout.label(text="GameFlow preferences unavailable", icon='ERROR')
            return

        hero = layout.box()
        row = hero.row()
        row.label(text="GameFlow for Blender", icon='PLAY')
        row.label(text=f"v{GAMEFLOW_VERSION}")
        hero.label(text="From player to creator.")

        status = layout.box()
        if prefs.enabled:
            alive = state.is_alive()
            row = status.row(align=True)
            row.label(text="READY" if alive else "PAUSED", icon='CHECKMARK' if alive else 'PAUSE')
            row.label(text=prefs.preset.title())
            status.operator(
                "wm.gameflow_toggle_navigation",
                text="Pause Navigation (F8)" if alive else "Resume Navigation (F8)",
                icon='PAUSE' if alive else 'PLAY',
            )
        else:
            status.label(text="Make Blender feel familiar in one click.", icon='INFO')
            status.operator("wm.gameflow_enable", text="Enable GameFlow", icon='PLAY')

        quick = layout.box()
        quick.label(text="Quick Feel", icon='PREFERENCES')
        quick.prop(prefs, "preset", text="")
        row = quick.row(align=True)
        row.prop(prefs, "movement_speed", text="Speed")
        row.prop(prefs, "look_sensitivity", text="Look")

        controls = layout.box()
        controls.prop(prefs, "show_controls", text="Controls", toggle=True, icon='EVENT_W')
        if prefs.show_controls:
            grid = controls.grid_flow(columns=2, even_columns=True, align=True)
            grid.label(text="WASD")
            grid.label(text="Move")
            grid.label(text="Q / E")
            grid.label(text="Down / Up")
            grid.label(text="Hold RMB")
            grid.label(text="Look + Boost")
            grid.label(text="Shift")
            grid.label(text="Sprint")
            grid.label(text="Scroll")
            grid.label(text="Zoom")
            grid.label(text="Double RMB")
            grid.label(text="Context")
            grid.label(text="F")
            grid.label(text="Frame Selected")
            grid.label(text="F8")
            grid.label(text="Pause / Resume")

        controller = layout.box()
        controller.prop(prefs, "show_controller", text="Controller / Steam Input", toggle=True, icon='GAME')
        if prefs.show_controller:
            controller.label(text="Map a controller to the same GameFlow inputs.")
            controller.operator("wm.gameflow_copy_steam_mapping", icon='COPYDOWN')

        advanced = layout.box()
        advanced.prop(prefs, "show_advanced", text="Advanced Settings", toggle=True, icon='SETTINGS')
        if prefs.show_advanced:
            advanced.label(text="Input")
            advanced.prop(prefs, "keymap_mode")
            advanced.prop(prefs, "vertical_mode")
            advanced.prop(prefs, "rmb_speed_multiplier")
            advanced.prop(prefs, "sprint_multiplier")

            advanced.separator()
            advanced.label(text="Motion")
            advanced.prop(prefs, "smooth_movement")
            if prefs.smooth_movement:
                advanced.prop(prefs, "acceleration")
                advanced.prop(prefs, "deceleration")
            advanced.prop(prefs, "wheel_zoom_factor")

            advanced.separator()
            advanced.label(text="Look")
            advanced.prop(prefs, "invert_x")
            advanced.prop(prefs, "invert_y")
            advanced.prop(prefs, "invert_zoom")
            advanced.prop(prefs, "double_click_time")
            advanced.prop(prefs, "edge_wrap_look")
            if prefs.edge_wrap_look:
                advanced.prop(prefs, "edge_wrap_margin")
                advanced.prop(prefs, "restore_cursor_after_look")

            advanced.separator()
            advanced.label(text="Startup")
            advanced.prop(prefs, "auto_start")
            advanced.prop(prefs, "restart_after_file_load")

        support = layout.box()
        support.prop(prefs, "show_support", text="Support & Recovery", toggle=True, icon='TOOL_SETTINGS')
        if prefs.show_support:
            if prefs.enabled and not state.is_alive():
                warning = support.box()
                warning.label(text="Navigation is not currently running.", icon='ERROR')
                warning.operator("wm.gameflow_repair", text="Repair GameFlow", icon='FILE_REFRESH')
            else:
                support.operator("wm.gameflow_repair", text="Repair GameFlow", icon='FILE_REFRESH')

            support.operator("wm.gameflow_copy_diagnostics", icon='COPYDOWN')
            support.separator()
            support.operator("wm.gameflow_reapply_keymap")
            support.operator("wm.gameflow_restore_saved")
            support.operator("wm.gameflow_reset_settings")
            if prefs.enabled:
                support.separator()
                support.operator("wm.gameflow_disable", text="Disable + Restore Blender Controls", icon='LOOP_BACK')
            support.label(text=f"Backup: {backup_path().name}")


classes = (
    WM_OT_gameflow_enable,
    WM_OT_gameflow_disable,
    WM_OT_gameflow_toggle_navigation,
    WM_OT_gameflow_reapply_keymap,
    WM_OT_gameflow_restore_saved,
    WM_OT_gameflow_repair,
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
