import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Panel


def _active_mesh(context):
    obj = context.active_object
    return obj if obj is not None and obj.type == 'MESH' else None


def _ensure_material(obj):
    mat = obj.active_material
    if mat is None:
        mat = bpy.data.materials.new(name=f"GF_Paint_{obj.name}")
        mat.use_nodes = True
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    else:
        mat.use_nodes = True
    return mat


def _bsdf_for(mat):
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return None
    return mat.node_tree.nodes.get('Principled BSDF')


def _active_image_node(mat):
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return None
    nodes = mat.node_tree.nodes
    active = nodes.active
    if active is not None and active.type == 'TEX_IMAGE' and active.image is not None:
        return active
    for node in nodes:
        if node.type == 'TEX_IMAGE' and node.image is not None and node.label == 'GameFlow Paint Canvas':
            return node
    return None


def _ensure_uv(context, obj):
    if obj.data.uv_layers:
        return True
    try:
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        return bool(obj.data.uv_layers)
    except RuntimeError:
        try:
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass
        return False


class GAMEFLOW_OT_paint_create_material(Operator):
    bl_idname = 'gameflow.paint_create_material'
    bl_label = 'Create Paint Material'
    bl_description = 'Create a material on the selected object so its color and surface can be edited'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'INFO'}, 'Select a mesh object first')
            return {'CANCELLED'}
        _ensure_material(obj)
        self.report({'INFO'}, 'Paint material ready')
        return {'FINISHED'}


class GAMEFLOW_OT_paint_new_canvas(Operator):
    bl_idname = 'gameflow.paint_new_canvas'
    bl_label = 'Start Texture Painting'
    bl_description = 'Create a paintable image, UVs, and material, then enter Blender Texture Paint mode'
    bl_options = {'REGISTER', 'UNDO'}

    size: EnumProperty(
        name='Canvas Size',
        items=[
            ('512', '512', 'Fast small texture'),
            ('1024', '1024', 'Recommended beginner texture size'),
            ('2048', '2048', 'Higher-detail texture'),
        ],
        default='1024',
    )

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            self.report({'INFO'}, 'Select a mesh object first')
            return {'CANCELLED'}

        if not _ensure_uv(context, obj):
            self.report({'ERROR'}, 'GameFlow could not create UVs for this object')
            return {'CANCELLED'}

        mat = _ensure_material(obj)
        tree = mat.node_tree
        bsdf = _bsdf_for(mat)
        if tree is None or bsdf is None:
            self.report({'ERROR'}, 'Could not prepare the material for painting')
            return {'CANCELLED'}

        size = int(self.size)
        base_name = f"GF_Paint_{obj.name}"
        image = bpy.data.images.new(base_name, width=size, height=size, alpha=True)
        image.generated_color = (0.8, 0.8, 0.8, 1.0)
        try:
            image.pack()
        except RuntimeError:
            pass

        nodes = tree.nodes
        node = nodes.get('GameFlow Paint Canvas')
        if node is None or node.type != 'TEX_IMAGE':
            node = nodes.new('ShaderNodeTexImage')
            node.name = 'GameFlow Paint Canvas'
        node.label = 'GameFlow Paint Canvas'
        node.image = image
        node.location = (bsdf.location.x - 300, bsdf.location.y)
        nodes.active = node
        node.select = True

        base_input = bsdf.inputs.get('Base Color')
        if base_input is not None:
            for link in list(base_input.links):
                tree.links.remove(link)
            tree.links.new(node.outputs['Color'], base_input)

        context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
        except RuntimeError as exc:
            self.report({'WARNING'}, f'Canvas created, but Texture Paint could not start: {exc}')
            return {'FINISHED'}

        if context.area is not None and context.area.type == 'VIEW_3D':
            try:
                context.area.spaces.active.shading.type = 'MATERIAL'
            except (AttributeError, TypeError):
                pass

        self.report({'INFO'}, f'Texture painting ready: {size} x {size}')
        return {'FINISHED'}


class GAMEFLOW_OT_paint_finish(Operator):
    bl_idname = 'gameflow.paint_finish'
    bl_label = 'Finish Painting'
    bl_description = 'Pack the current paint image into the blend file and return to Object Mode'

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            return {'CANCELLED'}
        node = _active_image_node(obj.active_material)
        if node is not None and node.image is not None:
            try:
                node.image.pack()
            except RuntimeError:
                pass
        try:
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass
        self.report({'INFO'}, 'Painting packed into the Blender file')
        return {'FINISHED'}


class GAMEFLOW_OT_paint_pack(Operator):
    bl_idname = 'gameflow.paint_pack'
    bl_label = 'Save Paint Into Project'
    bl_description = 'Pack the active paint image into the current Blender project'

    def execute(self, context):
        obj = _active_mesh(context)
        if obj is None:
            return {'CANCELLED'}
        node = _active_image_node(obj.active_material)
        if node is None or node.image is None:
            self.report({'INFO'}, 'No GameFlow paint canvas is active')
            return {'CANCELLED'}
        try:
            node.image.pack()
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Paint image saved inside this Blender project')
        return {'FINISHED'}


class VIEW3D_PT_gameflow_paint_studio(Panel):
    bl_label = 'Paint Studio'
    bl_idname = 'VIEW3D_PT_gameflow_paint_studio'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameFlow'
    bl_parent_id = 'VIEW3D_PT_gameflow'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        try:
            from .preferences import get_prefs
            prefs = get_prefs(context)
            return prefs is not None and prefs.creator_mode == 'PAINT'
        except Exception:
            return False

    def draw(self, context):
        layout = self.layout
        obj = _active_mesh(context)

        if obj is None:
            box = layout.box()
            box.label(text='Select a mesh object to paint.', icon='INFO')
            op = box.operator('gameflow.add_primitive', text='Add a Cube to Paint', icon='MESH_CUBE')
            op.primitive = 'CUBE'
            return

        mat = obj.active_material
        if mat is None:
            box = layout.box()
            box.label(text=f'Paint {obj.name}', icon='BRUSH_DATA')
            box.label(text='This object needs a material first.')
            box.operator('gameflow.paint_create_material', text='Create Paint Material', icon='MATERIAL')
            return

        bsdf = _bsdf_for(mat)
        surface = layout.box()
        surface.label(text='Color & Surface', icon='MATERIAL')
        surface.prop(mat, 'name', text='Material')
        if bsdf is not None:
            base = bsdf.inputs.get('Base Color')
            rough = bsdf.inputs.get('Roughness')
            metal = bsdf.inputs.get('Metallic')
            if base is not None and not base.is_linked:
                surface.prop(base, 'default_value', text='Color')
            elif base is not None and base.is_linked:
                surface.label(text='Color is coming from your painted texture.', icon='IMAGE_DATA')
            if rough is not None:
                surface.prop(rough, 'default_value', text='Roughness', slider=True)
            if metal is not None:
                surface.prop(metal, 'default_value', text='Metal', slider=True)

        styles = layout.box()
        styles.label(text='Quick Looks')
        row = styles.row(align=True)
        for material in ('PLASTIC', 'METAL', 'MATTE'):
            op = row.operator('gameflow.quick_material', text=material.title())
            op.material = material
        row = styles.row(align=True)
        for material in ('GLASS', 'GLOW'):
            op = row.operator('gameflow.quick_material', text=material.title())
            op.material = material

        painting = layout.box()
        painting.label(text='Brush Painting', icon='BRUSH_DATA')
        node = _active_image_node(mat)

        if obj.mode == 'TEXTURE_PAINT':
            painting.label(text='PAINTING — draw directly on the object', icon='CHECKMARK')
            ups = context.scene.tool_settings.unified_paint_settings
            if hasattr(ups, 'size'):
                painting.prop(ups, 'size', text='Brush Size')
            if hasattr(ups, 'strength'):
                painting.prop(ups, 'strength', text='Strength', slider=True)
            row = painting.row(align=True)
            row.operator('gameflow.paint_pack', text='Save Paint', icon='PACKAGE')
            row.operator('gameflow.paint_finish', text='Done', icon='CHECKMARK')
        else:
            painting.label(text='Paint colors and details directly onto the model.')
            if node is not None and node.image is not None:
                painting.label(text=f'Canvas: {node.image.name}')
            row = painting.row(align=True)
            op = row.operator('gameflow.paint_new_canvas', text='Start Painting', icon='BRUSH_DATA')
            op.size = '1024'
            painting.label(text='GameFlow creates UVs + a 1024px paint canvas automatically.')


classes = (
    GAMEFLOW_OT_paint_create_material,
    GAMEFLOW_OT_paint_new_canvas,
    GAMEFLOW_OT_paint_finish,
    GAMEFLOW_OT_paint_pack,
    VIEW3D_PT_gameflow_paint_studio,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
