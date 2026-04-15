def ensure_same_school(user, obj):
    school = user.counselor.school

    from core.models import Student, StudentEnrollment, StudentEvent, ClassSession

    if isinstance(obj, Student):
        obj_school = obj.school

    elif isinstance(obj, StudentEnrollment):
        obj_school = obj.school

    elif isinstance(obj, StudentEvent):
        obj_school = obj.school

    elif isinstance(obj, ClassSession):
        obj_school = obj.school

    else:
        raise PermissionError("Unsupported object type")

    if obj_school != school:
        raise PermissionError("No access")