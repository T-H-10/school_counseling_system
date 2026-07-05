from django.core.management.base import BaseCommand
from core.models import ClassLevel, SchoolYear

class Command(BaseCommand):
    help = "Initializes the database with mandatory infrastructure data for production"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- מתחיל אתחול נתוני תשתית למערכת ---"))

        # 1. יצירת שכבות כיתה א' עד ח' בצורה בטוחה
        levels_to_create = ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח"]
        created_levels_count = 0
        
        for letter in levels_to_create:
            obj, created = ClassLevel.objects.get_or_create(name=letter)
            if created:
                created_levels_count += 1
                
        self.stdout.write(f"  נוצרו {created_levels_count} שכבות כיתה חדשות (סך הכל קיימות: {ClassLevel.objects.count()}) ✓")
        self.stdout.write(self.style.SUCCESS("--- האתחול הסתיים בהצלחה! המערכת מוכנה לעבודה ---"))