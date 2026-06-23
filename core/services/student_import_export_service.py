"""Excel import/export for students.

Holds the workbook parsing/validation and workbook-building logic that used to
live inline in ``StudentViewSet``. Behavior is unchanged: the same column map,
the same Hebrew validation messages, and the same result shape are produced.
HTTP concerns (status codes, file responses) stay in the view.
"""

import io
import openpyxl

from core.models import ClassLevel, SchoolYear
from core.services.student_service import StudentService


class ExcelImportError(Exception):
    """Raised for whole-file problems the view should surface as HTTP 400."""


COL_MAP = {
    "שם מלא": "full_name",
    "מספר זהות": "id_number",
    "כיתה": "class_level_name",
    "מספר כיתה": "class_number",
    "שנת לימודים": "school_year_name",
    "שם אם": "mother_name",
    "טלפון אם": "mother_phone",
    "שם אב": "father_name",
    "טלפון אב": "father_phone",
    "כתובת": "address",
}
REQUIRED_COLS = {
    "full_name",
    "id_number",
    "class_level_name",
    "class_number",
    "school_year_name",
}
REQUIRED_HEB = {
    "full_name": "שם מלא",
    "id_number": "מספר זהות",
    "class_level_name": "כיתה",
    "class_number": "מספר כיתה",
    "school_year_name": "שנת לימודים",
}

EXPORT_HEADERS = [
    "שם מלא",
    "מספר זהות",
    "כיתה",
    "מספר כיתה",
    "שנת לימודים",
    "שם אם",
    "טלפון אם",
    "שם אב",
    "טלפון אב",
    "כתובת",
]


class StudentImportExportService:
    @staticmethod
    def import_students(user, file):
        """Parse an uploaded .xlsx and bulk-create students.

        Returns a ``{'created': int, 'errors': [...]}`` dict on success.
        Raises ``ExcelImportError`` for an unreadable file or missing
        required columns (the view turns these into HTTP 400).
        """
        try:
            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            ws = wb.active
        except Exception:
            raise ExcelImportError("קובץ Excel לא תקין. ודא שהקובץ הוא מסוג .xlsx")

        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            return {"created": 0, "errors": []}

        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        col_indices = {COL_MAP[h]: idx for idx, h in enumerate(headers) if h in COL_MAP}

        # Fail fast if any required column is absent from the header row
        missing_cols = [REQUIRED_HEB[f] for f in REQUIRED_COLS if f not in col_indices]
        if missing_cols:
            raise ExcelImportError(
                f"עמודות חסרות בקובץ: {', '.join(missing_cols)}. "
                "עמודות חובה בשורת הכותרת: שם מלא, מספר זהות, כיתה, מספר כיתה, שנת לימודים"
            )

        class_levels = {cl.name: cl for cl in ClassLevel.objects.all()}
        school_years = {sy.name: sy for sy in SchoolYear.objects.all()}

        def cell(row, field):
            idx = col_indices.get(field)
            if idx is None or idx >= len(row) or row[idx] is None:
                return None
            val = row[idx]
            return (
                str(int(val))
                if isinstance(val, float) and val.is_integer()
                else str(val).strip()
            )

        parsed = []
        pre_errors = []

        for row_num, row in enumerate(rows[1:], start=2):
            # Skip fully empty rows (trailing blank lines in Excel)
            if all(c is None for c in row):
                continue

            cl_name = cell(row, "class_level_name")
            sy_name = cell(row, "school_year_name")
            cn_raw = cell(row, "class_number")
            try:
                class_number = int(float(cn_raw)) if cn_raw else 0
            except (ValueError, TypeError):
                class_number = 0

            full_name = cell(row, "full_name") or ""
            id_number = cell(row, "id_number") or ""
            class_level = class_levels.get(cl_name) if cl_name else None
            school_year = school_years.get(sy_name) if sy_name else None

            # Per-row structural validation with specific Hebrew messages
            row_errors = []
            if not full_name:
                row_errors.append("שם מלא חסר")
            if not id_number:
                row_errors.append("מספר זהות חסר")
            if not school_year:
                label = f'"{sy_name}"' if sy_name else "ריק"
                row_errors.append(f"שנת לימודים {label} לא קיימת במערכת")
            if not class_level:
                label = f'"{cl_name}"' if cl_name else "ריק"
                row_errors.append(f"כיתה {label} לא קיימת במערכת (ערכים אפשריים: א–ח)")
            if not class_number:
                row_errors.append("מספר כיתה חסר או לא תקין")

            if row_errors:
                pre_errors.append({"row": row_num, "message": " | ".join(row_errors)})
                continue

            data = {
                "full_name": full_name,
                "id_number": id_number,
                "address": cell(row, "address"),
                "mother_name": cell(row, "mother_name"),
                "mother_phone": cell(row, "mother_phone"),
                "father_name": cell(row, "father_name"),
                "father_phone": cell(row, "father_phone"),
                "class_number": class_number,
                "class_level": class_level,
                "school_year": school_year,
            }
            parsed.append((row_num, data))

        result = StudentService.bulk_create_students(user, parsed)
        result["errors"] = pre_errors + result["errors"]
        return result

    @staticmethod
    def export_students(queryset):
        """Build an .xlsx of the given students and return its bytes."""
        students = queryset.prefetch_related(
            "enrollments__class_level", "enrollments__school_year"
        ).order_by("full_name")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "תלמידים"
        ws.sheet_view.rightToLeft = True
        ws.append(EXPORT_HEADERS)

        for student in students:
            enrollment = student.enrollments.order_by("-created_at").first()
            ws.append(
                [
                    student.full_name,
                    student.id_number,
                    enrollment.class_level.name
                    if enrollment and enrollment.class_level
                    else "",
                    enrollment.class_number if enrollment else "",
                    enrollment.school_year.name
                    if enrollment and enrollment.school_year
                    else "",
                    student.mother_name or "",
                    student.mother_phone or "",
                    student.father_name or "",
                    student.father_phone or "",
                    student.address or "",
                ]
            )

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()
