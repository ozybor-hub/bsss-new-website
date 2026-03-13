from django.shortcuts import render
from datetime import date

# TODO: Import your actual models here
# from .models import UnitOutline, AssessmentDeadline


def dashboard(request):
    """
    Render the teacher dashboard with recent unit outlines and upcoming deadlines.
    
    TODO: Replace the hardcoded sample data below with actual database queries.
    """
    
    # =========================================================================
    # SAMPLE DATA - Replace with actual database queries
    # =========================================================================
    
    # Example: recent_units = UnitOutline.objects.filter(teacher=request.user).order_by('-modified_date')[:5]
    recent_units = [
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
    
    # Example: upcoming_deadlines = AssessmentDeadline.objects.filter(
    #     unit__teacher=request.user,
    #     due_date__gte=date.today()
    # ).order_by('due_date')[:10]
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
    
    # =========================================================================
    # END SAMPLE DATA
    # =========================================================================
    
    context = {
        'user_name': request.user.first_name if request.user.is_authenticated else 'Teacher',
        'recent_units': recent_units,
        'upcoming_deadlines': upcoming_deadlines,
    }
    
    return render(request, 'dashboard.html', context)


def new_unit_outline(request):
    """
    Create a new unit outline.
    TODO: Implement the view logic.
    """
    # Placeholder - implement your logic here
    pass


def clone_unit_outline(request):
    """
    Clone an existing unit outline.
    TODO: Implement the view logic.
    """
    # Placeholder - implement your logic here
    pass
