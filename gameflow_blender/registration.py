import bpy
from bpy.types import AddonPreferences


def is_registered_class(cls):
    """Return True only when Blender registered this exact Python class.

    Do not use getattr(cls, 'bl_rna'): AddonPreferences subclasses can inherit
    Blender RNA attributes from the base class before the subclass itself has
    been registered. Blender adds the subclass RNA metadata directly to the
    class dictionary when registration succeeds.
    """
    try:
        direct_rna = cls.__dict__.get('bl_rna')
        if direct_rna is not None:
            return True
    except Exception:
        pass

    # Secondary exact-object check for normal Blender RNA types.
    try:
        return getattr(bpy.types, cls.__name__, None) is cls
    except Exception:
        return False


def _matching_stale_preferences(current_cls, addon_id):
    matches = []
    try:
        subclasses = list(AddonPreferences.__subclasses__())
    except Exception:
        subclasses = []

    for candidate in subclasses:
        if candidate is current_cls:
            continue
        try:
            same_name = candidate.__name__ == current_cls.__name__
            same_id = getattr(candidate, 'bl_idname', None) == addon_id
            module_name = str(getattr(candidate, '__module__', ''))
            same_module = module_name.endswith('.preferences') and 'gameflow' in module_name.lower()
            if same_name or same_id or same_module:
                matches.append(candidate)
        except Exception:
            continue
    return matches


def cleanup_stale_preferences(current_cls, addon_id):
    """Remove stale AddonPreferences classes left alive by Blender reloads."""
    removed = 0
    for candidate in reversed(_matching_stale_preferences(current_cls, addon_id)):
        try:
            bpy.utils.unregister_class(candidate)
            removed += 1
        except (RuntimeError, ValueError, ReferenceError):
            pass
    return removed


def register_preferences(preferences_module):
    """Register GameFlow preferences safely across Blender install/reload cycles."""
    classes = tuple(getattr(preferences_module, 'classes', ()))
    if not classes:
        return

    current_cls = classes[0]
    addon_id = getattr(preferences_module, 'ADDON_ID', current_cls.__module__.split('.')[0])

    # Only skip when the current subclass itself is registered, not merely
    # because it inherits RNA metadata from bpy.types.AddonPreferences.
    if is_registered_class(current_cls):
        return

    cleanup_stale_preferences(current_cls, addon_id)

    if is_registered_class(current_cls):
        return

    try:
        preferences_module.register()
        return
    except RuntimeError as exc:
        if 'already registered as a subclass' not in str(exc):
            raise

    # A duplicate error can mean Blender finished registering this exact class
    # during the operation. Verify directly before touching stale generations.
    if is_registered_class(current_cls):
        return

    cleanup_stale_preferences(current_cls, addon_id)
    if is_registered_class(current_cls):
        return

    preferences_module.register()
