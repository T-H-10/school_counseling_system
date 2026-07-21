from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ClassLevel, SchoolYear
from core.services.school_year_service import SchoolYearService

class Command(BaseCommand):
    help = "Initializes the database with mandatory infrastructure data for production"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- מתחיל אתחול נתוני תשתית למערכת ---"))

        levels_to_create = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח"]
        created_levels_count = 0
        
        for letter in levels_to_create:
            obj, created = ClassLevel.objects.get_or_create(name=letter)
            if created:
                created_levels_count += 1
                
        self.stdout.write(f"  נוצרו {created_levels_count} שכבות כיתה חדשות (סך הכל קיימות: {ClassLevel.objects.count()}) ✓")

        active_year = SchoolYear.objects.filter(is_active=True).first()
        if active_year is None:
            today = timezone.localdate()
            start_year = today.year if today.month >= 8 else today.year - 1
            name = f"{start_year}-{start_year + 1}"
            year, _ = SchoolYear.objects.get_or_create(name=name)
            SchoolYearService.activate_year(year.id)
            self.stdout.write(f"  שנת לימודים פעילה נוצרה: {name} ✓")
        else:
            self.stdout.write(f"  שנת לימודים פעילה קיימת: {active_year.name} ✓")

        self.stdout.write(self.style.SUCCESS("--- האתחול הסתיים בהצלחה! המערכת מוכנה לעבודה ---"))