from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if self.deleted_at:
            return
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
 

class BaseQuerySet(models.QuerySet):

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    # def for_school(self, school):
    #     return self.filter(school=school)
    

class BaseManager(models.Manager):

    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).alive()


    # def for_school(self, school):        
    #     return self.get_queryset().for_school(school)


class BaseModel(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class School(models.Model):
    name = models.CharField(max_length=150)
    institution_code = models.CharField(max_length=20, unique=True)  # סמל מוסד

    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.institution_code})"


class Counselor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="counselors"
    )

    full_name = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class ClassLevel(models.Model):

    LEVEL_CHOICES = [
        ('א', 'א'),
        ('ב', 'ב'),
        ('ג', 'ג'),
        ('ד', 'ד'),
        ('ה', 'ה'),
        ('ו', 'ו'),
        ('ז', 'ז'),
        ('ח', 'ח'),
    ]
        
    name = models.CharField(max_length=1, choices=LEVEL_CHOICES, unique=True)  

    def __str__(self):
        return self.name


class SchoolYear(models.Model):
    name = models.CharField(max_length=20)  # example: 2025-2026
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Student(BaseModel):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="students"
    )

    full_name = models.CharField(max_length=150)
    id_number = models.CharField(max_length=9, unique=True)

    address = models.CharField(max_length=255, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)

    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return self.full_name

    class Meta:
        indexes = [
            models.Index(fields=["school"]),
            models.Index(fields=["id_number"]),
        ]
        

class StudentEnrollment(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name="enrollments")

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True)
    class_number = models.PositiveIntegerField()

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.student.full_name} - {self.school_year}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "school_year"],
                name="unique_enrollment_per_year"
            )
        ]


class StudentEvent(BaseModel):
    EVENT_TYPES = [
        ('meeting', 'פגישה'),
        ('call', 'שיחה'),
        ('teacher_report', 'דיווח מורה'),
        ('other', 'אחר'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="events")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="events")

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)

    title = models.CharField(max_length=200)
    description = models.TextField()


    def __str__(self):
        return f"{self.student.full_name} - {self.event_type}"


class ClassSession(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sessions")
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name="sessions")

    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    summary = models.TextField()

    date = models.DateTimeField()

    def __str__(self):
        return self.title
    
