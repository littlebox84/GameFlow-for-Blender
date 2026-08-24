import math

import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel


def _active_object(context):
    return getattr(context.view_layer.objects, 'active', None)


def _fmt(value):
    return f"{value:.3f}".rstrip('0').rstrip('.')


def _vec_text(vec):
    return f"X {_fmt(vec.x)}   Y {_fmt(vec.y)}   Z {_fmt(vec.z)}"


def _rotation_text(rotation):
    return (
        f"X {_fmt(math.degrees(rotation.x))}°   "
        f"Y {_fmt(math.degrees(rotation.y))}°   "
        f"Z {_fmt(math.degrees(rotation.z))}°"
    )


def _material_name(obj):
    try:
        mat = obj.active_material
        return mat.name if mat else "None"
    except Exception:
        return "None"


def _collection_name(obj):
    try:
        collections = list(obj.users_collection)
        return collections[0].name if collections else "None"
    except Exception:
        return "None"


class GAMEFLOW_OT_quick_rename(Operator):
    bl_idname = "gameflow.quick_rename"
    bl_label = "Rename Object"
    bl_description = "Give the active object a clear name"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: StringProperty(name="Name", default="Object")

    def invoke(self, context, event):
        obj = _active_object(context)
        if obj is None:
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        self.new_name = obj.name
        return context.window_manager.invoke_props_dialog(self, width=320)

    def execute(self, context):
        obj = _active_object(context)
        if obj is None:
            return {'CANCELLED'}
        name = self.new_name.strip()
        if not name:
            self.report({'WARNING'}, "Name cannot be empty")
            return {'CANCELLED'}
        obj.name = name
        return {'FINISHED'}


class GAMEFLOW_OT_number_selected(Operator):
    bl_idname = "gameflow.number_selected"
    bl_label = "Number Selected"
    bl_description = "Rename selected objects with a shared base name and sequential numbers"
    bl_options = {'REGISTER', 'UNDO'}

    base_name: StringProperty(name="Base Name", default="Object")

    def invoke(self, context, event):
        objects = list(context.selected_objects)
        if not objects:
            self.report({'INFO'}, "Select one or more objects first")
            return {'CANCELLED'}
        active = _active_object(context)
        if active:
            stem = active.name.rsplit('_', 1)[0]
            self.base_name = stem or "Object"
        return context.window_manager.invoke_props_dialog(self, width=320)

    def execute(self, context):
        objects = list(context.selected_objects)
        if not objects:
            return {'CANCELLED'}
        base = self.base_name.strip() or "Object"
        objects.sort(key=lambda obj: obj.name.lower())
        for index, obj in enumerate(objects, start=1):
            obj.name = f"{base}_{index:02d}"
        return {'FINISHED'}


class GAMEFLOW_OT_copy_object_info(Operator):
    bl_idname = "gameflow.copy_object_info"
    bl_label = "Copy Object Info"
    bl_description = "Copy the active object's GameFlow info to the clipboard"

    def execute(self, context):
        obj = _active_object(context)
        if obj is None:
            self.report({'INFO'}, "Select an object first")
            return {'CANCELLED'}
        lines = [
            f"Name: {obj.name}",
            f"Type: {obj.type.title()}",
            f"Dimensions: {_vec_text(obj.dimensions)}",
            f"Position: {_vec_text(obj.location)}",
            f"Rotation: {_rotation_text(obj.rotation_euler)}",
            f"Scale: {_vec_text(obj.scale)}",
            f"Material: {_material_name(obj)}",
            f"Parent: {obj.parent.name if obj.parent else 'None'}",
            f"Collection: {_collection_name(obj)}",
        ]
        context.window_manager.clipboard = "\n".join(lines)
        self.report({'INFO'}, "Object info copied")
        return {'FINISHED'}


class VIEW3D_PT_gameflow_object_info(Panel):
    bl_label = "Object Info"
    bl_idname = "VIEW3D_PT_gameflow_object_info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "GameFlow"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = _active_object(context)

        if obj is None:
            box = layout.box()
            box.label(text="Select an object to inspect it.", icon='INFO')
            return

        hero = layout.box()
        hero.label(text=obj.name, icon='OBJECT_DATA')
        hero.label(text=f"Type: {obj.type.title()}")

        measure = layout.box()
        measure.label(text="Measurements", icon='DRIVER_DISTANCE')
        measure.label(text=f"Size: {_vec_text(obj.dimensions)}")
        measure.label(text=f"Position: {_vec_text(obj.location)}")
        measure.label(text=f"Rotation: {_rotation_text(obj.rotation_euler)}")
        measure.label(text=f"Scale: {_vec_text(obj.scale)}")

        details = layout.box()
        details.label(text="Object Details", icon='OUTLINER_OB_MESH')
        details.label(text=f"Material: {_material_name(obj)}")
        details.label(text=f"Parent: {obj.parent.name if obj.parent else 'None'}")
        details.label(text=f"Collection: {_collection_name(obj)}")

        rename = layout.box()
        rename.label(text="Quick Rename", icon='GREASEPENCIL')
        rename.operator("gameflow.quick_rename", text="Rename Active")
        rename.operator("gameflow.number_selected", text="Number Selected")

        layout.operator("gameflow.copy_object_info", text="Copy Object Info", icon='COPYDOWN')


classes = (
    GAMEFLOW_OT_quick_rename,
    GAMEFLOW_OT_number_selected,
    GAMEFLOW_OT_copy_object_info,
    VIEW3D_PT_gameflow_object_info,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
