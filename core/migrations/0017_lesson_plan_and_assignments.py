import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def copy_class_sessions(apps, schema_editor):
    """Migrate each ClassSession into a LessonPlan + one LessonClassAssignment."""
    ClassSession = apps.get_model('core', 'ClassSession')
    LessonPlan = apps.get_model('core', 'LessonPlan')
    LessonClassAssignment = apps.get_model('core', 'LessonClassAssignment')

    for session in ClassSession.objects.all():
        lesson = LessonPlan.objects.create(
            school_id=session.school_id,
            counselor_id=session.counselor_id,
            school_year_id=session.school_year_id,
            title=session.title,
            description=None,
            presentation_url=None,
            deleted_at=session.deleted_at,
        )
        has_summary = bool(session.summary and session.summary.strip())
        LessonClassAssignment.objects.create(
            lesson=lesson,
            school_id=session.school_id,
            class_level_id=session.class_level_id,
            class_number=None,
            status='completed' if has_summary else 'planned',
            planned_date=None if has_summary else session.date,
            completed_date=session.date if has_summary else None,
            summary=session.summary,
            deleted_at=session.deleted_at,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_remove_classroom_add_teacher_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('presentation_url', models.URLField(blank=True, null=True)),
                ('counselor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='core.counselor')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='core.school')),
                ('school_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.schoolyear')),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='LessonClassAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_number', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('planned', 'מתוכנן'), ('completed', 'הושלם')], default='planned', max_length=20)),
                ('planned_date', models.DateTimeField(blank=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.classlevel')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='core.lessonplan')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_assignments', to='core.school')),
            ],
            options={'abstract': False},
        ),
        migrations.RunPython(copy_class_sessions, noop),
        migrations.DeleteModel(name='ClassSession'),
    ]
