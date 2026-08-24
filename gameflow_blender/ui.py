import bpy
import platform
from bpy.types import Operator, Panel

from . import state
from .preferences import get_prefs, PRESETS
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls, backup_path, save_preferences

GAMEFLOW_VERSION = "0.5.2-step5"

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
    bl_label = "Start GameFlow"
    bl_description = "Turn on GameFlow controls and start game-style navigation"

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
        state.safe_mode = False
        state.stop_requested = False
        started = start_navigation()
        save_preferences()
        self.report({'INFO'}, f"GameFlow started; {changed} shortcut conflicts handled")
        if not started:
            self.report({'WARNING'}, "Open a 3D Viewport and press F8")
        return {'FINISHED'}


class WM_OT_gameflow_disable(Operator):
    bl_idname = "wm.gameflow_disable"
    bl_label = "Turn Off GameFlow"

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
        self.report({'INFO'}, f"Blender controls restored ({count} shortcut states)")
        return {'FINISHED'}


class WM_OT_gameflow_toggle_navigation(Operator):
    bl_idname = "wm.gameflow_toggle_navigation"
    bl_label = "Pause / Resume GameFlow"

    def execute(self, context):
        prefs = get_prefs(context)
        if state.is_alive():
            state.stop_requested = True
            return {'FINISHED'}
        if prefs and not prefs.enabled:
            self.report({'INFO'}, "Start GameFlow first")
            return {'CANCELLED'}
        return {'FINISHED'} if start_navigation() else {'CANCELLED'}


class WM_OT_gameflow_reapply_keymap(Operator):
    bl_idname = "wm.gameflow_reapply_keymap"
    bl_label = "Repair GameFlow Controls"

    def execute(self, context):
        prefs = get_prefs(context)
        try:
            changed = apply_gameflow_keymap(prefs.keymap_mode if prefs else 'MINIMAL')
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        save_preferences()
        self.report({'INFO'}, f"GameFlow controls repaired; {changed} conflicts handled")
        return {'FINISHED'}


class WM_OT_gameflow_restore_saved(Operator):
    bl_idname = "wm.gameflow_restore_saved"
    bl_label = "Restore Standard Blender Controls"

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
    bl_label = "Fix GameFlow"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}
        try:
            prefs.enabled = True
            state.safe_mode = False
            apply_gameflow_keymap(prefs.keymap_mode)
            if state.running and not state.is_alive():
                state.clear_running()
            state.stop_requested = False
            started = start_navigation()
            save_preferences()
        except Exception as exc:
            self.report({'ERROR'}, f"Repair failed: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, "GameFlow fixed" if started else "Controls fixed; press F8 in the 3D Viewport")
        return {'FINISHED'}


class WM_OT_gameflow_reset_settings(Operator):
    bl_idname = "wm.gameflow_reset_settings"
    bl_label = "Reset GameFlow"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            return {'CANCELLED'}
        prefs.creator_mode = 'NAVIGATE'
        prefs.hud_mode = 'FULL'
        prefs.hud_corner = 'BOTTOM_CENTER'
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
        prefs.show_controls = False
        prefs.show_advanced = False
        save_preferences()
        self.report({'INFO'}, "GameFlow reset to beginner defaults")
        return {'FINISHED'}


class WM_OT_gameflow_copy_steam_mapping(Operator):
    bl_idname = "wm.gameflow_copy_steam_mapping"
    bl_label = "Copy Controller Setup"

    def execute(self, context):
        context.window_manager.clipboard = STEAM_MAPPING
        self.report({'INFO'}, "Controller mapping copied")
        return {'FINISHED'}


class WM_OT_gameflow_copy_diagnostics(Operator):
    bl_idname = "wm.gameflow_copy_diagnostics"
    bl_label = "Copy Technical Info"

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
            f"HUD position: {prefs.hud_corner if prefs else 'unavailable'}",
            f"Preset: {prefs.preset if prefs else 'unavailable'}",
            f"Keymap mode: {prefs.keymap_mode if prefs else 'unavailable'}",
        ]
        context.window_manager.clipboard = "\n".join(lines)
        self.report({'INFO'}, "Technical info copied")
        return {'FINISHED'}


def _creator_modes(layout, prefs):
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.prop(prefs, "creator_mode", expand=True)


def _add_shapes(layout):
    row = layout.row(align=True)
    for primitive, label in [('CUBE', 'Cube'), ('PLANE', 'Plane'), ('SPHERE', 'Sphere')]:
        op = row.operator("gameflow.add_primitive", text=label)
        op.primitive = primitive
    row = layout.row(align=True)
    for primitive, label in [('CYLINDER', 'Cylinder'), ('CONE', 'Cone')]:
        op = row.operator("gameflow.add_primitive", text=label)
        op.primitive = primitive


def _quick_actions(layout, context):
    obj = context.active_object
    box = layout.box()
    if obj is None:
        box.label(text="Make Something", icon='ADD')
        box.label(text="Pick a shape to get started.")
        _add_shapes(box)
        return

    box.label(text=f"Selected: {obj.name}", icon='OBJECT_DATA')
    row = box.row(align=True)
    row.operator("gameflow.focus_selected", text="Focus", icon='VIEWZOOM')
    row.operator("object.duplicate_move", text="Duplicate", icon='DUPLICATE')
    row = box.row(align=True)
    row.operator("gameflow.drop_to_floor", text="Drop to Floor", icon='TRIA_DOWN')
    row.operator("ed.undo", text="Undo", icon='LOOP_BACK')
    box.prop(obj, "name", text="Name")


def _build_tools(layout, prefs):
    box = layout.box()
    box.label(text="Build", icon='MOD_BUILD')
    row = box.row(align=True)
    for tool, label in [('SELECT', 'Select'), ('MOVE', 'Move'), ('ROTATE', 'Rotate'), ('SCALE', 'Scale')]:
        op = row.operator("gameflow.set_tool", text=label)
        op.tool = tool
    row = box.row(align=True)
    row.prop(prefs, "build_grid_step", text="Move Step")
    row.prop(prefs, "build_rotation_step", text="Turn Step")
    box.operator("gameflow.toggle_snap", text="Snap to Grid", icon='SNAP_INCREMENT')
    row = box.row(align=True)
    for axis in ('X', 'Y', 'Z'):
        op = row.operator("gameflow.duplicate_offset", text=f"Copy +{axis}")
        op.axis = axis


def _paint_tools(layout):
    box = layout.box()
    box.label(text="Paint", icon='MATERIAL')
    box.label(text="Choose a simple look for the selected object.")
    row = box.row(align=True)
    for material in ('PLASTIC', 'METAL', 'MATTE'):
        op = row.operator("gameflow.quick_material", text=material.title())
        op.material = material
    row = box.row(align=True)
    for material in ('GLASS', 'GLOW'):
        op = row.operator("gameflow.quick_material", text=material.title())
        op.material = material


def _help_me(layout, prefs):
    box = layout.box()
    box.prop(prefs, "show_controls", text="Help Me", toggle=True, icon='QUESTION')
    if not prefs.show_controls:
        return
    box.label(text="Move around like a game:")
    grid = box.grid_flow(columns=2, even_columns=True, align=True)
    for key, action in [
        ('W A S D', 'Move'),
        ('Q / E', 'Down / Up'),
        ('Hold RMB', 'Look around'),
        ('Shift', 'Move faster'),
        ('Scroll', 'Zoom'),
        ('Left Click', 'Select'),
        ('F', 'Focus selected'),
        ('F8', 'Pause / Resume'),
    ]:
        grid.label(text=key)
        grid.label(text=action)


def _advanced(layout, prefs):
    box = layout.box()
    box.prop(prefs, "show_advanced", text="Advanced", toggle=True, icon='SETTINGS')
    if not prefs.show_advanced:
        return

    box.label(text="Control Feel")
    box.prop(prefs, "preset", text="Style")
    row = box.row(align=True)
    row.prop(prefs, "movement_speed", text="Move Speed")
    row.prop(prefs, "look_sensitivity", text="Look Speed")

    box.separator()
    box.label(text="On-screen Helper")
    box.prop(prefs, "hud_mode", text="Helper")
    if prefs.hud_mode != 'OFF':
        box.prop(prefs, "hud_corner", text="Position")

    box.separator()
    box.label(text="Movement")
    box.prop(prefs, "vertical_mode")
    box.prop(prefs, "rmb_speed_multiplier")
    box.prop(prefs, "sprint_multiplier")
    box.prop(prefs, "smooth_movement")
    if prefs.smooth_movement:
        box.prop(prefs, "acceleration")
        box.prop(prefs, "deceleration")
    box.prop(prefs, "wheel_zoom_factor")
    box.prop(prefs, "invert_x")
    box.prop(prefs, "invert_y")
    box.prop(prefs, "invert_zoom")

    box.separator()
    box.label(text="Controller")
    box.operator("wm.gameflow_copy_steam_mapping", text="Copy Steam Input Setup", icon='GAME')

    box.separator()
    box.label(text="Startup")
    box.prop(prefs, "auto_start")
    box.prop(prefs, "restart_after_file_load")

    box.separator()
    box.label(text="Recovery")
    box.operator("gameflow.health_check", text="Check GameFlow", icon='CHECKMARK')
    if state.safe_mode:
        box.operator("wm.gameflow_exit_safe_mode", text="Leave Safe Mode", icon='PLAY')
    else:
        box.operator("wm.gameflow_enter_safe_mode", text="Safe Mode", icon='SHIELD')
    box.operator("wm.gameflow_repair", text="Fix GameFlow", icon='FILE_REFRESH')
    box.operator("wm.gameflow_restore_saved", text="Restore Standard Blender Controls")
    box.operator("wm.gameflow_copy_diagnostics", text="Copy Technical Info", icon='COPYDOWN')
    box.operator("wm.gameflow_reset_settings", text="Reset GameFlow")
    if prefs.enabled:
        box.operator("wm.gameflow_disable", text="Turn Off GameFlow", icon='LOOP_BACK')
    box.label(text=f"Backup: {backup_path().name}")


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
            layout.label(text="GameFlow could not load", icon='ERROR')
            return

        hero = layout.box()
        hero.label(text="GameFlow", icon='PLAY')
        hero.label(text="From player to creator.")

        status = layout.box()
        if state.safe_mode:
            status.label(text="SAFE MODE", icon='SHIELD')
            status.label(text="Standard Blender controls are active.")
            status.operator("wm.gameflow_exit_safe_mode", text="Return to GameFlow", icon='PLAY')
        elif not prefs.enabled:
            status.label(text="Ready when you are.")
            button = status.row()
            button.scale_y = 1.5
            button.operator("wm.gameflow_enable", text="Start GameFlow", icon='PLAY')
        else:
            alive = state.is_alive()
            row = status.row(align=True)
            row.label(text="READY" if alive else "PAUSED", icon='CHECKMARK' if alive else 'PAUSE')
            row.operator("wm.gameflow_toggle_navigation", text="Pause" if alive else "Resume", icon='PAUSE' if alive else 'PLAY')

        modes = layout.box()
        modes.label(text="What do you want to do?")
        _creator_modes(modes, prefs)

        _quick_actions(layout, context)

        if prefs.creator_mode == 'BUILD':
            _build_tools(layout, prefs)
        elif prefs.creator_mode == 'PAINT':
            _paint_tools(layout)

        _help_me(layout, prefs)
        _advanced(layout, prefs)


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
