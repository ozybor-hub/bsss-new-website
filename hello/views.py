from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
import copy
import calendar as cal_module


# Sample data (stands in for database)
SAMPLE_UNITS = [
    {
        'id': 1,
        'name': 'Digital Solutions - Year 12',
        'code': '12001',
        'status': 'DRAFT',
        'last_modified': date(2026, 2, 15),
        'due_dates_info': 'items pending',
    },
    {
        'id': 2,
        'name': 'Robotics - Year 12',
        'code': '12003',
        'status': 'PUBLISHED',
        'last_modified': date(2026, 2, 10),
        'due_dates_info': '20 Feb 2026',
        'live_status': 'Live for students',
    },
]

_next_id = 3


def _get_units():
    return SAMPLE_UNITS


# Dashboard view
def dashboard(request):
    recent_units = _get_units()

    upcoming_deadlines = [
        {
            'assessment_item': 'Design Document',
            'unit': 'Digital Solutions Y12',
            'due_date': date(2026, 2, 20),
            'status': 'Outline Pending',
        },
        {
            'assessment_item': 'Build 1',
            'unit': 'Digital Solutions Y12',
            'due_date': date(2026, 3, 20),
            'status': 'Outline Pending',
        },
    ]

    context = {
        'user_name': request.user.first_name if request.user.is_authenticated else 'Teacher',
        'recent_units': recent_units,
        'upcoming_deadlines': upcoming_deadlines,
        'active_nav': 'dashboard',
    }

    return render(request, 'dashboard.html', context)


# Unit outline editor view
def unit_outline(request):
    unit = {
        'code': '12001 (Read-only)',
        'title': 'Digital Solutions',
        'year_level': 'Year 12 (Read-only)',
    }

    assessment_items = [
        {'name': 'Design Document', 'weighting': '30%', 'start_date': '27/01/2026', 'due_date': '26/02/2026'},
        {'name': 'Build 1', 'weighting': '20%', 'start_date': '21/02/2026', 'due_date': '20/03/2026'},
        {'name': 'Build 2', 'weighting': '30%', 'start_date': '30/03/2026', 'due_date': '22/05/2026'},
        {'name': 'Reflection', 'weighting': '20%', 'start_date': '25/05/2026', 'due_date': '12/06/2026'},
    ]

    context = {
        'unit': unit,
        'assessment_items': assessment_items,
        'active_nav': 'unit_outlines',
    }

    return render(request, 'unit_outline.html', context)


# ---------------------------------------------------------------------------
# Grade Auto-Calculation System
# Automatically computes final percentage and letter grade from weighted
# assessment scores so teachers see up-to-date results without manual entry.
# ---------------------------------------------------------------------------

# Assessment weightings – each tuple is (score_key, max_marks, weight_fraction)
ASSESSMENT_WEIGHTS = [
    ('design_doc', 20, 0.20),   # Design Document – 20%
    ('build1',     20, 0.20),   # Build 1         – 20%
    ('build2',     30, 0.30),   # Build 2         – 30%
    ('reflection', 20, 0.20),   # Reflection      – 20%
]


def calculate_final_percentage(student):
    """Return the weighted final percentage for a student, or None if
    any assessment score is missing (i.e. still pending).
    Weights are normalised so they always sum to 100%."""
    for key, _max, _w in ASSESSMENT_WEIGHTS:
        if student.get(key) is None:
            return None  # can't calculate until all marks are in

    # Normalise weights so they sum to 1.0 (handles specs that don't total 100%)
    weight_sum = sum(w for _, _, w in ASSESSMENT_WEIGHTS)

    total = 0.0
    for key, max_marks, weight in ASSESSMENT_WEIGHTS:
        # Score as a fraction of max, scaled by normalised weight
        total += (student[key] / max_marks) * (weight / weight_sum) * 100
    return round(total)


def determine_letter_grade(percentage):
    """Map a numeric percentage to a letter grade and CSS class.
    Returns a (letter, css_class) tuple."""
    if percentage is None:
        return (None, 'pending')
    if percentage >= 85:
        return ('A', 'a')
    if percentage >= 70:
        return ('B', 'b')
    if percentage >= 55:
        return ('C', 'c')
    if percentage >= 40:
        return ('D', 'd')
    return ('F', 'f')


def auto_calculate_grades(students):
    """Iterate over every student dict and populate grade_pct,
    grade_letter, and grade_class using the calculation helpers."""
    for student in students:
        pct = calculate_final_percentage(student)
        letter, css_class = determine_letter_grade(pct)
        student['grade_pct'] = pct
        student['grade_letter'] = letter
        student['grade_class'] = css_class
    return students


def compute_class_average(students):
    """Return the rounded class average from students who have a
    calculated grade. Returns 0 when no grades are available yet."""
    graded = [s['grade_pct'] for s in students if s['grade_pct'] is not None]
    if not graded:
        return 0
    return round(sum(graded) / len(graded))


# Persistent student data (module-level so edits survive across requests)
SAMPLE_STUDENTS = [
    {'name': 'Emma Wilson',     'student_id': 'S12345', 'design_doc': 18, 'build1': 17, 'build2': 26, 'reflection': 18},
    {'name': 'Liam Chen',       'student_id': 'S12346', 'design_doc': 16, 'build1': 15, 'build2': 24, 'reflection': 16},
    {'name': 'Olivia Martinez', 'student_id': 'S12347', 'design_doc': 19, 'build1': 18, 'build2': 28, 'reflection': 19},
    {'name': 'Noah Thompson',   'student_id': 'S12348', 'design_doc': 14, 'build1': 13, 'build2': 20, 'reflection': 14},
    {'name': 'Sophia Anderson', 'student_id': 'S12349', 'design_doc': 17, 'build1': 16, 'build2': 25, 'reflection': None},
    {'name': 'Jackson Lee',     'student_id': 'S12350', 'design_doc': 15, 'build1': 14, 'build2': 22, 'reflection': 15},
    {'name': 'Ava Patel',       'student_id': 'S12351', 'design_doc': 18, 'build1': 17, 'build2': None, 'reflection': None},
    {'name': 'Ethan Brown',     'student_id': 'S12352', 'design_doc': 16, 'build1': 15, 'build2': 23, 'reflection': 16},
]

# Maps assessment form values to (score_key, max_marks)
ASSESSMENT_FIELD_MAP = {
    'design_doc': ('design_doc', 20),
    'build1':     ('build1', 20),
    'build2':     ('build2', 30),
    'reflection': ('reflection', 20),
}


# Markbook view
def markbook(request):
    unit = {
        'code': '12001',
        'title': 'Digital Solutions',
        'year_level': 'Year 12',
        'teacher': 'Ms. Johnson',
        'semester': 'Semester 1, 2026',
        'last_updated': '18 Feb 2026, 3:45 PM',
    }

    students = copy.deepcopy(SAMPLE_STUDENTS)
    auto_calculate_grades(students)

    completed = sum(1 for s in students if s['grade_pct'] is not None)
    pending = len(students) - completed
    class_avg = compute_class_average(students)

    stats = {
        'total_students': 24,
        'completed_assessments': completed,
        'pending_marks': pending,
        'class_average': class_avg,
    }

    context = {
        'unit': unit,
        'stats': stats,
        'students': students,
        'active_nav': 'markbook',
    }

    return render(request, 'markbook.html', context)


# Update a single student grade via Quick Edit (POST only)
def update_grade(request):
    if request.method != 'POST':
        return redirect('teacher_portal:markbook')

    student_id = request.POST.get('student_id', '')
    assessment = request.POST.get('assessment', '')
    mark_raw = request.POST.get('mark', '').strip()

    if not student_id or assessment not in ASSESSMENT_FIELD_MAP:
        messages.error(request, 'Invalid student or assessment.')
        return redirect('teacher_portal:markbook')

    field_key, max_marks = ASSESSMENT_FIELD_MAP[assessment]

    # Parse the mark value
    try:
        mark = int(mark_raw)
    except (ValueError, TypeError):
        messages.error(request, 'Mark must be a whole number.')
        return redirect('teacher_portal:markbook')

    if mark < 0 or mark > max_marks:
        messages.error(request, f'Mark must be between 0 and {max_marks}.')
        return redirect('teacher_portal:markbook')

    # Find and update the student
    student = None
    for s in SAMPLE_STUDENTS:
        if s['student_id'] == student_id:
            student = s
            break

    if student is None:
        messages.error(request, 'Student not found.')
        return redirect('teacher_portal:markbook')

    student[field_key] = mark
    messages.success(request, f'Updated {student["name"]}\'s {assessment.replace("_", " ").title()} to {mark}/{max_marks}. Final grade recalculated.')

    return redirect('teacher_portal:markbook')


# Calendar view
def calendar_view(request):
    year = 2026
    month = 3
    month_name = 'March'

    events_map = {
        20: [{'label': 'Build 1 Due', 'type': 'deadline'}],
        27: [{'label': 'Term 1 Ends', 'type': 'term'}],
        30: [{'label': 'Build 2 Start', 'type': 'start'}],
    }

    # Build calendar weeks (Monday start)
    cal = cal_module.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    calendar_weeks = []
    today = date.today()
    for week in month_days:
        week_data = []
        for day_num in week:
            if day_num == 0:
                week_data.append({'number': '', 'other_month': True, 'is_today': False, 'events': []})
            else:
                week_data.append({
                    'number': day_num,
                    'other_month': False,
                    'is_today': (today.year == year and today.month == month and today.day == day_num),
                    'events': events_map.get(day_num, []),
                })
        calendar_weeks.append(week_data)

    context = {
        'month_name': month_name,
        'year': year,
        'calendar_weeks': calendar_weeks,
        'active_nav': 'calendar',
    }

    return render(request, 'calendar.html', context)


# New unit outline placeholder
def new_unit_outline(request):
    pass


# Clone unit action (POST only)
def clone_unit_action(request):
    global _next_id

    if request.method != 'POST':
        return redirect('teacher_portal:dashboard')

    unit_id = request.POST.get('unit_id')

    original = None
    for u in SAMPLE_UNITS:
        if str(u['id']) == str(unit_id):
            original = u
            break

    if original is None:
        messages.error(request, 'Unit not found.')
        return redirect('teacher_portal:dashboard')

    cloned = copy.deepcopy(original)
    cloned['id'] = _next_id
    _next_id += 1
    cloned['name'] = f"Copy of {original['name']}"
    cloned['status'] = 'DRAFT'
    cloned['last_modified'] = date.today()
    cloned['due_dates_info'] = 'items pending'
    cloned.pop('live_status', None)

    SAMPLE_UNITS.insert(0, cloned)

    messages.success(request, f'Successfully cloned "{original["name"]}" → "{cloned["name"]}" (DRAFT).')

    return redirect('teacher_portal:dashboard')
