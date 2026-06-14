def ensure_same_school(user, obj):
    school = user.counselor.school

    from core.models import Student, StudentEnrollment, StudentEvent, LessonPlan, LessonClassAssignment

    if isinstance(obj, (Student, StudentEnrollment, StudentEvent, LessonPlan, LessonClassAssignment)):
        obj_school = obj.school
    else:
        raise PermissionError("Unsupported object type")

    if obj_school != school:
        raise PermissionError("No access")