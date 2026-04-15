def ensure_same_school(user, obj):
    school = user.counselor.school

    if hasattr(obj, "school"):
        obj_school = obj.school
    elif hasattr(obj, "student"):
        obj_school = obj.student.school
    else:
        raise PermissionError("No school relation")

    if obj_school != school:
        raise PermissionError("No access")