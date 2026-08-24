import bpy
import platform
from bpy.types import Operator, Panel

from . import state
from .preferences import get_prefs, PRESETS
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls, backup_path, save_preferences

GAMEFLOW_VERSION = "0.5.0-step5"

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
            self.report({'INFO'}, "Enable GameFlow first")
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

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
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
        self.report({'INFO'}, "GameFlow repaired" if started else "Controls repaired; press F8 in a 3D Viewport")
        return {'FINISHED'}


class WM_OT_gameflow_reset_settings(Operator):
    bl_idname = "wm.gameflow_reset_settings"
    bl_label = "Reset GameFlow Settings"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}
        prefs.creator_mode = 'NAVIGATE'
        prefs.hud_mode = 'FULL'
        prefs.hud_corner = 'TOP_RIGHT'
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
        prefs.build_grid_step = 1.0
        prefs.build_rotation_step = 45.0
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
        return {'FINISHED'}


class WM_OT_gameflow_copy_diagnostics(Operator):
    bl_idname = "wm.gameflow_copy_diagnostics"
    bl_label = "Copy Diagnostics"

    def execute(self, context):
        prefs = get_prefs(context)
        lines = [
            f"GameFlow: {GAMEFLOW_VERSION}",
            f"Blender: {bpy.app.version_string}",
            f"OS: {platform.system()} {platform.release()}",
            f"GameFlow enabled: {bool(prefs and prefs.enabled)}",
            f"Navigation alive: {state.is_alive()}",
            f"Safe Mode: {state.safe_mode}",
            f"Creator mode: {prefs.creator_mode if prefs else 'unavailable'}",
            f"HUD mode: {prefs.hud_mode if prefs else 'unavailable'}",
            f"HUD corner: {prefs.hud_corner if prefs else 'unavailable'}",
            f"Preset: {prefs.preset if prefs else 'unavailable'}",
            f"Keymap mode: {prefs.keymap_mode if prefs else 'unavailable'}",
        ]
        context.window_manager.clipboard = "\n".join(lines)
        return {'FINISHED'}


def _mode_buttons(layout, prefs):
    row = layout.row(align=True)
    row.scale_y = 1.35
    row.prop(prefs, "creator_mode", expand=True)


def _add_buttons(layout):
    row = layout.row(align=True)
    for primitive, label in [('CUBE', 'Cube'), ('PLANE', 'Plane'), ('SPHERE', 'Sphere')]:
        op = row.operator("gameflow.add_primitive", text=label)
        op.primitive = primitive
    row = layout.row(align=True)
    for primitive, label in [('CYLINDER', 'Cylinder'), ('CONE', 'Cone')]:
        op = row.operator("gameflow.add_primitive", text=label)
        op.primitive = primitive


def _quick_actions(layout, context):
    box = layout.box()
    box.label(text="Quick Actions", icon='TOOL_SETTINGS')
    obj = context.active_object
    row = box.row(align=True)
    row.operator("gameflow.focus_selected", text="Focus", icon='VIEWZOOM')
    row.operator("object.duplicate_move", text="Duplicate", icon='DUPLICATE')
    row = box.row(align=True)
    row.operator("gameflow.drop_to_floor", text="Drop to Floor", icon='TRIA_DOWN')
    row.operator("ed.undo", text="Undo", icon='LOOP_BACK')
    if obj:
        box.prop(obj, "name", text="Rename")


def _object_context(layout, context):
    obj = context.active_object
    box = layout.box()
    if obj is None:
        box.label(text="Start Creating", icon='ADD')
        box.label(text="Nothing selected — add something to the scene.")
        _add_buttons(box)
        return

    box.label(text="Selected Object", icon='OBJECT_DATA')
    box.prop(obj, "name", text="Name")
    box.prop(obj, "location", text="Position")
    box.prop(obj, "rotation_euler", text="Rotation")
    box.prop(obj, "scale", text="Scale")

    if obj.type == 'LIGHT' and getattr(obj, 'data', None):
        box.separator()
        box.label(text="Light", icon='LIGHT')
        if hasattr(obj.data, 'energy'):
            box.prop(obj.data, "energy", text="Brightness")
        if hasattr(obj.data, 'color'):
            box.prop(obj.data, "color", text="Color")


def _build_section(layout, prefs):
    box = layout.box()
    box.label(text="Build Assist", icon='MOD_BUILD')

    row = box.row(align=True)
    for tool, label in [('SELECT', 'Select'), ('MOVE', 'Move'), ('ROTATE', 'Rotate'), ('SCALE', 'Scale')]:
        op = row.operator("gameflow.set_tool", text=label)
        op.tool = tool

    row = box.row(align=True)
    row.prop(prefs, "build_grid_step", text="Step")
    row.prop(prefs, "build_rotation_step", text="Rotate")
    box.operator("gameflow.toggle_snap", text="Toggle Grid Snap", icon='SNAP_INCREMENT')

    box.label(text="Nudge")
    for axis in ('X', 'Y', 'Z'):
        row = box.row(align=True)
        op = row.operator("gameflow.nudge", text=f"-{axis}")
        op.axis, op.direction = axis, -1
        op = row.operator("gameflow.nudge", text=f"+{axis}")
        op.axis, op.direction = axis, 1

    box.label(text="Rotate Step")
    for axis in ('X', 'Y', 'Z'):
        row = box.row(align=True)
        op = row.operator("gameflow.rotate_step", text=f"{axis}-")
        op.axis, op.direction = axis, -1
        op = row.operator("gameflow.rotate_step", text=f"{axis}+")
        op.axis, op.direction = axis, 1

    box.label(text="Duplicate")
    row = box.row(align=True)
    for axis in ('X', 'Y', 'Z'):
        op = row.operator("gameflow.duplicate_offset", text=f"Copy +{axis}")
        op.axis = axis


def _paint_section(layout):
    box = layout.box()
    box.label(text="Quick Materials", icon='MATERIAL')
    row = box.row(align=True)
    for material in ('PLASTIC', 'METAL', 'MATTE'):
        op = row.operator("gameflow.quick_material", text=material.title())
        op.material = material
    row = box.row(align=True)
    for material in ('GLASS', 'GLOW'):
        op = row.operator("gameflow.quick_material", text=material.title())
        op.material = material


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
        row = hero.row(align=True)
        row.label(text="GameFlow", icon='PLAY')
        row.label(text="From player to creator.")

        status = layout.box()
        if state.safe_mode:
            status.label(text="SAFE MODE", icon='SHIELD')
            status.operator("wm.gameflow_exit_safe_mode", text="Exit Safe Mode", icon='PLAY')
        elif prefs.enabled:
            alive = state.is_alive()
            row = status.row(align=True)
            row.label(text="READY" if alive else "PAUSED", icon='CHECKMARK' if alive else 'PAUSE')
            row.label(text=prefs.preset.title())
            status.operator("wm.gameflow_toggle_navigation", text="Pause (F8)" if alive else "Resume (F8)", icon='PAUSE' if alive else 'PLAY')
        else:
            status.label(text="Make Blender feel familiar in one click.")
            status.operator("wm.gameflow_enable", text="Enable Full GameFlow Controls", icon='PLAY')

        modes = layout.box()
        modes.label(text="Creator Mode", icon='WORKSPACE')
        _mode_buttons(modes, prefs)

        _quick_actions(layout, context)

        if prefs.creator_mode == 'NAVIGATE':
            explore = layout.box()
            explore.label(text="Explore", icon='ORIENTATION_GLOBAL')
            explore.prop(prefs, "preset", text="Feel")
            row = explore.row(align=True)
            row.prop(prefs, "movement_speed", text="Speed")
            row.prop(prefs, "look_sensitivity", text="Look")
        elif prefs.creator_mode == 'BUILD':
            _build_section(layout, prefs)
        else:
            _paint_section(layout)

        _object_context(layout, context)

        hud = layout.box()
        hud.label(text="Viewport HUD", icon='OVERLAY')
        hud.prop(prefs, "hud_mode", expand=True)
        if prefs.hud_mode != 'OFF':
            hud.prop(prefs, "hud_corner", text="Position")

        settings = layout.box()
        settings.prop(prefs, "show_advanced", text="Settings", toggle=True, icon='SETTINGS')
        if prefs.show_advanced:
            settings.prop(prefs, "keymap_mode")
            settings.prop(prefs, "vertical_mode")
            settings.prop(prefs, "rmb_speed_multiplier")
            settings.prop(prefs, "sprint_multiplier")
            settings.prop(prefs, "smooth_movement")
            if prefs.smooth_movement:
                settings.prop(prefs, "acceleration")
                settings.prop(prefs, "deceleration")
            settings.prop(prefs, "wheel_zoom_factor")
            settings.prop(prefs, "invert_x")
            settings.prop(prefs, "invert_y")
            settings.prop(prefs, "invert_zoom")
            settings.prop(prefs, "double_click_time")
            settings.prop(prefs, "edge_wrap_look")
            settings.prop(prefs, "auto_start")
            settings.prop(prefs, "restart_after_file_load")

        controller = layout.box()
        controller.prop(prefs, "show_controller", text="Controller / Steam Input", toggle=True, icon='GAME')
        if prefs.show_controller:
            controller.label(text="Map your controller to GameFlow keys with Steam Input.")
            controller.operator("wm.gameflow_copy_steam_mapping", icon='COPYDOWN')

        recovery = layout.box()
        recovery.prop(prefs, "show_support", text="Safety & Recovery", toggle=True, icon='SHIELD')
        if prefs.show_support:
            recovery.operator("gameflow.health_check", text="Health Check", icon='CHECKMARK')
            if state.safe_mode:
                recovery.operator("wm.gameflow_exit_safe_mode", text="Exit Safe Mode", icon='PLAY')
            else:
                recovery.operator("wm.gameflow_enter_safe_mode", text="Enter Safe Mode", icon='SHIELD')
            recovery.operator("wm.gameflow_repair", icon='FILE_REFRESH')
            recovery.operator("wm.gameflow_reapply_keymap")
            recovery.operator("wm.gameflow_restore_saved")
            recovery.operator("wm.gameflow_copy_diagnostics", icon='COPYDOWN')
            recovery.operator("wm.gameflow_reset_settings")
            if prefs.enabled:
                recovery.operator("wm.gameflow_disable", text="Disable + Restore Blender Controls", icon='LOOP_BACK')
            recovery.label(text=f"Backup: {backup_path().name}")


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
