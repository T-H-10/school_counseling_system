from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from core.models import (
    School, Counselor, ClassLevel, SchoolYear,
    Student, StudentEnrollment, StudentEvent, ClassSession
)


class Command(BaseCommand):
    help = "Seed the database with realistic Hebrew mock data for development"

    def handle(self, *args, **options):
        self.stdout.write("--- מתחיל טעינת נתוני דמה ---\n")

        # 1. Class levels א–ח
        levels = []
        for letter in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
            obj, created = ClassLevel.objects.get_or_create(name=letter)
            levels.append(obj)
        self.stdout.write(f"  רמות כיתה: {len(levels)} ✓")

        # 2. School year
        school_year, _ = SchoolYear.objects.get_or_create(
            name="2024-2025",
            defaults={"is_active": True}
        )
        self.stdout.write(f"  שנת לימודים: {school_year.name} ✓")

        # 3. School
        school, _ = School.objects.get_or_create(
            institution_code="510123",
            defaults={
                "name": "בית ספר יסודי הדר",
                "address": "רחוב הרצל 12, תל אביב",
                "phone": "0391234567",
            }
        )
        self.stdout.write(f"  בית ספר: {school.name} ✓")

        # 4. Counselor user
        user, user_created = User.objects.get_or_create(
            username="counselor1",
            defaults={"first_name": "רחל", "last_name": "גולדברג"}
        )
        if user_created:
            user.set_password("Test1234!")
            user.save()

        counselor, _ = Counselor.objects.get_or_create(
            user=user,
            defaults={"school": school, "full_name": "רחל גולדברג"}
        )
        self.stdout.write(f"  יועצת: {counselor.full_name} ✓")

        # 5. Students
        students_data = [
            {"full_name": "דנה כהן",    "id_number": "123456789", "address": "רחוב אלנבי 5, תל אביב",
             "mother_name": "מרים כהן",  "mother_phone": "0501234561",
             "father_name": "משה כהן",   "father_phone": "0521234561"},
            {"full_name": "אבי לוי",    "id_number": "234567891", "address": "שדרות בן גוריון 20, חיפה",
             "mother_name": "רות לוי",   "mother_phone": "0501234562",
             "father_name": "יעקב לוי",  "father_phone": "0521234562"},
            {"full_name": "נועה מזרחי", "id_number": "345678912", "address": "רחוב יפו 8, ירושלים",
             "mother_name": "שרה מזרחי", "mother_phone": "0531234563",
             "father_name": "דוד מזרחי", "father_phone": "0541234563"},
            {"full_name": "יוסי פרץ",   "id_number": "456789123", "address": "רחוב הנביאים 3, באר שבע",
             "mother_name": "לאה פרץ",   "mother_phone": "0531234564",
             "father_name": "אברהם פרץ", "father_phone": "0541234564"},
            {"full_name": "מיה אברהם",  "id_number": "567891234", "address": "רחוב ויצמן 15, רחובות",
             "mother_name": "חנה אברהם", "mother_phone": "0501234565",
             "father_name": "יצחק אברהם","father_phone": "0521234565"},
            {"full_name": "גל שמש",     "id_number": "678912345", "address": "רחוב דיזנגוף 44, תל אביב",
             "mother_name": "דינה שמש",  "mother_phone": "0531234566",
             "father_name": "עמי שמש",   "father_phone": "0541234566"},
            {"full_name": "רועי גולן",  "id_number": "789123456", "address": "שדרות רוטשילד 2, פתח תקווה",
             "mother_name": "תמר גולן",  "mother_phone": "0501234567",
             "father_name": "ניר גולן",  "father_phone": "0521234567"},
            {"full_name": "שירה ברק",   "id_number": "891234567", "address": "רחוב הגפן 7, הרצליה",
             "mother_name": "ורד ברק",   "mother_phone": "0531234568",
             "father_name": "אלון ברק",  "father_phone": "0541234568"},
        ]

        students = []
        for data in students_data:
            student, _ = Student.objects.get_or_create(
                id_number=data["id_number"],
                defaults={**data, "school": school}
            )
            students.append(student)
        self.stdout.write(f"  תלמידים: {len(students)} ✓")

        # 6. Enrollments (one per student, spread across class levels)
        class_assignments = [
            (levels[0], 1), (levels[1], 2), (levels[2], 1),
            (levels[3], 3), (levels[4], 2), (levels[5], 1),
            (levels[6], 4), (levels[7], 2),
        ]
        enrollment_count = 0
        for student, (level, class_num) in zip(students, class_assignments):
            _, created = StudentEnrollment.objects.get_or_create(
                student=student,
                school_year=school_year,
                defaults={
                    "school": school,
                    "class_level": level,
                    "class_number": class_num,
                }
            )
            if created:
                enrollment_count += 1
        self.stdout.write(f"  רישומים: {enrollment_count} חדשים ✓")

        # 7. Student events (12 spread across students and types)
        now = timezone.now()
        events_data = [
            (students[0], "meeting",        "שיחת היכרות",                  "שיחה ראשונית עם התלמידה לבירור צרכים אישיים ולימודיים.", -30),
            (students[0], "call",           "שיחת מעקב",                    "שיחת טלפון לבדיקת התקדמות לאחר השיחה הראשונית.",          -15),
            (students[1], "teacher_report", "דיווח מורה על קשיים בקריאה",   "המורה דיווחה על קשיים בהבנת הנקרא בשיעורי עברית.",        -45),
            (students[1], "meeting",        "פגישה עם הורים",               "פגישה משותפת עם הורי התלמיד לדיון בתוכנית סיוע.",          -20),
            (students[2], "other",          "תיעוד אירוע בשעת הפסקה",       "אירוע חברתי בין תלמידים בשעת הפסקה, טופל במקום.",           -10),
            (students[3], "meeting",        "ייעוץ אישי",                   "שיחה פרטית על לחץ לפני מבחנים ואסטרטגיות התמודדות.",       -5),
            (students[3], "call",           "תיאום עם פסיכולוג חינוכי",     "תיאום הפניה לפסיכולוג חינוכי לאחר שיחה עם ההורים.",        -3),
            (students[4], "teacher_report", "דיווח על שיפור בהתנהגות",      "המורה ציינה שיפור משמעותי בהתנהגות ובמעורבות בשיעור.",     -7),
            (students[5], "meeting",        "פגישת קבוצת שיח",             "פגישה קבוצתית של תלמידים לעיבוד קשיים חברתיים.",          -14),
            (students[6], "other",          "תיעוד יציאה מוקדמת",          "התלמיד יצא מוקדם מהכיתה לצורך טיפול רפואי.",               -2),
            (students[7], "meeting",        "שיחת ייעוץ קריירה",            "שיחה על תחומי עניין ואפשרויות לחוגים העשרה.",              -1),
            (students[7], "call",           "מעקב לאחר מחלה",              "שיחת טלפון לבדיקת שובו של התלמיד לאחר היעדרות.",           0),
        ]

        event_count = 0
        for student, etype, title, desc, days_offset in events_data:
            exists = StudentEvent.objects.filter(
                student=student, title=title
            ).exists()
            if not exists:
                StudentEvent.objects.create(
                    student=student,
                    counselor=counselor,
                    school=school,
                    event_type=etype,
                    title=title,
                    description=desc,
                    date=now + timedelta(days=days_offset),
                )
                event_count += 1
        self.stdout.write(f"  אירועים: {event_count} חדשים ✓")

        # 8. Class sessions (6 sessions across different levels)
        sessions_data = [
            (levels[0], "שיעור מניעת אלימות כיתה א",      "הצגת כלים להתמודדות עם סיטואציות של קונפליקט בגן ובבית הספר.", -60),
            (levels[1], "פיתוח מיומנויות חברתיות",         "תרגול כישורי תקשורת ושיתוף פעולה דרך משחקים קבוצתיים.",       -45),
            (levels[2], "שיחה על גבולות ובטיחות ברשת",     "חשיפה לסכנות הרשת ולמה חשוב לשמור על מידע אישי.",            -30),
            (levels[4], "ניהול רגשות וויסות עצמי",          "כלים פרקטיים לזיהוי רגשות ולהתמודדות עם כעס ותסכול.",       -20),
            (levels[6], "הכנה למעבר לחטיבת הביניים",        "שיחה על השינויים הצפויים וכיצד להיערך אליהם נפשית ולימודית.", -10),
            (levels[7], "חינוך מיני ומניעת הטרדה",          "מפגש ייחודי לכיתה ח לדיון פתוח ומוגן בנושאים רגישים.",       -5),
        ]

        session_count = 0
        for level, title, summary, days_offset in sessions_data:
            exists = ClassSession.objects.filter(title=title).exists()
            if not exists:
                ClassSession.objects.create(
                    school=school,
                    counselor=counselor,
                    school_year=school_year,
                    class_level=level,
                    title=title,
                    summary=summary,
                    date=now + timedelta(days=days_offset),
                )
                session_count += 1
        self.stdout.write(f"  שיעורים: {session_count} חדשים ✓")

        self.stdout.write("\n--- נתוני דמה נטענו בהצלחה! ---")
        self.stdout.write("\nפרטי התחברות לסוואגר:")
        self.stdout.write("  שם משתמש : counselor1")
        self.stdout.write("  סיסמה    : Test1234!")
        self.stdout.write("\nשלבים:")
        self.stdout.write("  1. POST /token/ עם הפרטים לעיל → העתק את access token")
        self.stdout.write('  2. בסוואגר לחץ "Authorize" → הדבק: Bearer <token>')
        self.stdout.write("  3. GET /students/ → אמור להחזיר 8 תלמידים\n")
