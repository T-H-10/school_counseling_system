"""Shared helpers for the service layer.

These factor out the field-assignment boilerplate that repeats across the
CRUD services. Behavior is identical to the inline versions they replace:
keys in ``exclude`` are skipped, the rest are assigned and the instance saved.
"""


def apply_fields(instance, data, exclude=("id",)):
    """Assign ``data`` onto ``instance`` (skipping ``exclude``), save, return it."""
    for attr, value in data.items():
        if attr not in exclude:
            setattr(instance, attr, value)
    instance.save()
    return instance


def create_excluding(model, data, exclude=("id",)):
    """Create a ``model`` instance from ``data``, dropping any ``exclude`` keys."""
    clean_data = {k: v for k, v in data.items() if k not in exclude}
    return model.objects.create(**clean_data)
