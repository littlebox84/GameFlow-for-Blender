import bpy
from bpy.types import Operator, Panel

from . import state
from .preferences import get_prefs
from .navigation import start_navigation
from .keymap import apply_gameflow_keymap, restore_saved_controls, save_preferences


class WM_OT_gameflow_enter_safe_mode(Operator):
    bl_idname = "wm.gameflow_enter_safe_mode"
    bl_label = "Enter Safe Mode"
    bl_description = "Restore Blender controls and pause GameFlow navigation while keeping Creator tools available"

    def execute(self, context):
        try:
            restore_saved_controls(delete_backup=False)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not restore Blender controls: {exc}")
            return {'CANCELLED'}

        state.safe_mode = True
        state.stop_requested = True
        state.clear_running()
        save_preferences()
        self.report({'INFO'}, "GameFlow Safe Mode ON: Blender controls restored")
        return {'FINISHED'}


class WM_OT_gameflow_exit_safe_mode(Operator):
    bl_idname = "wm.gameflow_exit_safe_mode"
    bl_label = "Exit Safe Mode"
    bl_description = "Reapply GameFlow controls and restart navigation"

    def execute(self, context):
        prefs = get_prefs(context)
        if prefs is None:
            self.report({'ERROR'}, "GameFlow preferences unavailable")
            return {'CANCELLED'}

        state.safe_mode = False
        if prefs.enabled:
            try:
                apply_gameflow_keymap(prefs.keymap_mode)
            except Exception as exc:
                self.report({'ERROR'}, f"Could not reapply GameFlow controls: {exc}")
                state.safe_mode = True
                return {'CANCELLED'}
            state.stop_requested = False
            start_navigation()
        save_preferences()
        self.report({'INFO'}, "GameFlow Safe Mode OFF")
        return {'FINISHED'}


class VIEW3D_PT_gameflow_safe_mode(Panel):
    bl_label = "Safety"
    bl_idname = "VIEW3D_PT_gameflow_safe_mode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GameFlow"
    bl_parent_id = "VIEW3D_PT_gameflow"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        if state.safe_mode:
            box = layout.box()
            box.label(text="SAFE MODE", icon='SHIELD')
            box.label(text="Blender controls are active.")
            box.label(text="GameFlow Creator tools remain available.")
            box.operator("wm.gameflow_exit_safe_mode", text="Exit Safe Mode", icon='PLAY')
        else:
            layout.label(text="Recovery mode for control conflicts.", icon='INFO')
            layout.operator("wm.gameflow_enter_safe_mode", text="Enter Safe Mode", icon='SHIELD')


classes = (
    WM_OT_gameflow_enter_safe_mode,
    WM_OT_gameflow_exit_safe_mode,
    VIEW3D_PT_gameflow_safe_mode,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    state.safe_mode = False
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
