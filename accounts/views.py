# C:\Users\GATARA-BJTU\school_a_project\accounts\views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .forms import LoginForm
from school_messages.models import Notification
from marks.models import Mark
from students.models import Student
from teachers.models import Teacher

def login_view(request):
    """Handle user login"""
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        # Redirect based on user role for better UX
        if request.user.is_admin():
            messages.info(request, 'Welcome back, Administrator!')
        elif request.user.is_teacher():
            messages.info(request, 'Welcome back, Teacher!')
        elif request.user.is_student():
            messages.info(request, 'Welcome back, Student!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Custom welcome messages based on role
                    if user.is_admin():
                        messages.success(request, f'Welcome Administrator {user.username}!')
                    elif user.is_teacher():
                        messages.success(request, f'Welcome Teacher {user.username}!')
                    elif user.is_student():
                        messages.success(request, f'Welcome Student {user.username}!')
                    else:
                        messages.success(request, f'Welcome back, {user.username}!')
                    
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Your account is inactive. Please contact administration.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Handle user logout"""
    username = request.user.username
    logout(request)
    messages.info(request, f'Goodbye {username}! You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    """Main dashboard view - shows different content based on user role"""
    user = request.user
    
    # Get unread notifications count with error handling
    unread_count = 0
    try:
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
    except Exception as e:
        print(f"Notification error: {e}")  # This will log to Render console
    
    # Initialize context variables with defaults
    context = {
        'user': user,
        'unread_count': unread_count,
        'has_student_profile': False,
        'has_teacher_profile': False,
        'dashboard_title': 'Dashboard',
        # Admin dashboard variables - ALL with defaults
        'student_count': 0,
        'teacher_count': 0,
        'total_balance': 0,
        'pending_payments': 0,
        'total_users': 0,
        'active_users': 0,
        'student_users': 0,
        'teacher_users': 0,
        'admin_users': 0,
        'recent_students': [],
        'recent_teachers': [],
        'system_alerts': [],
        # Teacher dashboard variables
        'department': '',
        'employee_id': '',
        'qualification': '',
        'experience': '',
        'assigned_subjects': [],
        'assigned_subjects_count': 0,
        'classes_taught': [],
        'classes_count': 0,
        'subjects_taught': [],
        'subjects_taught_count': 0,
        'marks_given_count': 0,
        'recent_marks': [],
        # Student dashboard variables
        'student_profile': None,
        'student_id': None,
        'grade_section': '',
        'admission_number': '',
        'subjects_list': [],
        'subjects_count': 0,
        'overall_average': 'N/A',
        'latest_term': '',
        'latest_term_average': 0,
        'subjects_with_marks': 0,
        'grade_counts': {},
        'pass_rate': 0,
        'no_marks_message': '',
        'error_message': '',
        'warning_message': '',
        'info_message': '',
    }
    
    # STUDENT DASHBOARD DATA
    if user.is_student():
        context['dashboard_title'] = 'Student Dashboard'
        
        if user.has_student_profile():
            try:
                student_profile = user.get_student_profile()
                context['has_student_profile'] = True
                context['student_profile'] = student_profile
                context['student_id'] = student_profile.id
                
                # Student's class information
                context['grade_section'] = f"{student_profile.grade}{student_profile.section}"
                context['admission_number'] = student_profile.admission_number
                
                # Get student's subjects
                if student_profile.subjects:
                    subjects_list = [s.strip() for s in student_profile.subjects.split(',')]
                    context['subjects_list'] = subjects_list
                    context['subjects_count'] = len(subjects_list)
                
                # Get academic performance data
                try:
                    marks = Mark.objects.filter(student=student_profile)
                    
                    if marks.exists():
                        # Calculate overall average
                        total_score = sum(mark.total_score for mark in marks)
                        average_score = total_score / marks.count()
                        context['overall_average'] = round(average_score, 2)
                        
                        # Get latest term marks
                        latest_marks = marks.order_by('-academic_year', '-term')
                        if latest_marks.exists():
                            latest_term = latest_marks.first()
                            context['latest_term'] = f"{latest_term.term} {latest_term.academic_year}"
                            
                            # Calculate latest term average
                            term_marks = marks.filter(
                                term=latest_term.term, 
                                academic_year=latest_term.academic_year
                            )
                            if term_marks.exists():
                                term_total = sum(mark.total_score for mark in term_marks)
                                term_average = term_total / term_marks.count()
                                context['latest_term_average'] = round(term_average, 2)
                        
                        # Count subjects with marks
                        subjects_with_marks = marks.values('subject').distinct().count()
                        context['subjects_with_marks'] = subjects_with_marks
                        
                        # Get grade distribution
                        context['grade_counts'] = {
                            'A': marks.filter(grade='A').count(),
                            'B': marks.filter(grade='B').count(),
                            'C': marks.filter(grade='C').count(),
                            'D': marks.filter(grade='D').count(),
                            'E': marks.filter(grade='E').count(),
                            'F': marks.filter(grade='F').count(),
                        }
                        
                        # Calculate pass rate (A-E are passing grades)
                        total_marks = marks.count()
                        passing_marks = marks.filter(grade__in=['A', 'B', 'C', 'D', 'E']).count()
                        if total_marks > 0:
                            context['pass_rate'] = round((passing_marks / total_marks) * 100, 1)
                    else:
                        context['no_marks_message'] = 'No academic records available yet.'
                        
                except Exception as e:
                    print(f"Marks error: {e}")
                    
            except Exception as e:
                context['error_message'] = 'Error loading student data.'
                print(f"Student error: {e}")
        else:
            context['warning_message'] = 'Student profile not found.'
    
    # TEACHER DASHBOARD DATA
    elif user.is_teacher():
        context['dashboard_title'] = 'Teacher Dashboard'
        
        if user.has_teacher_profile():
            try:
                teacher_profile = user.get_teacher_profile()
                context['has_teacher_profile'] = True
                context['teacher_profile'] = teacher_profile
                
                # Teacher's professional information
                context['department'] = teacher_profile.department or ''
                context['employee_id'] = teacher_profile.employee_id or ''
                context['qualification'] = teacher_profile.qualification or ''
                context['experience'] = teacher_profile.experience or ''
                
                # Get assigned subjects
                try:
                    context['assigned_subjects'] = teacher_profile.assigned_subjects.all()
                    context['assigned_subjects_count'] = context['assigned_subjects'].count()
                except:
                    context['assigned_subjects'] = []
                    context['assigned_subjects_count'] = 0
                
                # Get classes taught
                if teacher_profile.classes:
                    classes_list = [c.strip() for c in teacher_profile.classes.split(',')]
                    context['classes_taught'] = classes_list
                    context['classes_count'] = len(classes_list)
                
                # Get subjects taught
                if teacher_profile.subjects:
                    subjects_list = [s.strip() for s in teacher_profile.subjects.split(',')]
                    context['subjects_taught'] = subjects_list
                    context['subjects_taught_count'] = len(subjects_list)
                
                # Get teacher's marks given
                try:
                    marks_given = teacher_profile.marks_given.all()
                    context['marks_given_count'] = marks_given.count()
                    context['recent_marks'] = marks_given.order_by('-date_entered')[:10]
                except:
                    context['marks_given_count'] = 0
                    context['recent_marks'] = []
                
            except Exception as e:
                context['error_message'] = 'Error loading teacher data.'
                print(f"Teacher error: {e}")
        else:
            context['warning_message'] = 'Teacher profile not found.'
    
    # ADMIN DASHBOARD DATA - CRITICAL FIX
    elif user.is_admin():
        context['dashboard_title'] = 'Admin Dashboard'
        
        try:
            # System statistics - using EXACT variable names from template
            context['student_count'] = Student.objects.count()
            context['teacher_count'] = Teacher.objects.count()
            context['total_users'] = user.__class__.objects.count()
            context['active_users'] = user.__class__.objects.filter(is_active=True).count()
            
            # Get users by role
            context['student_users'] = user.__class__.objects.filter(role='student').count()
            context['teacher_users'] = user.__class__.objects.filter(role='teacher').count()
            context['admin_users'] = user.__class__.objects.filter(role='admin').count()
            
            # Get recent student registrations
            context['recent_students'] = Student.objects.select_related('user').order_by('-created_at')[:5]
            
            # Get recent teacher registrations
            context['recent_teachers'] = Teacher.objects.select_related('user').order_by('-created_at')[:5]
            
            # Finance-related variables
            context['total_balance'] = 0  # Default, update with your calculation
            context['pending_payments'] = 0  # Default, update with your calculation
            
            # System alerts
            context['system_alerts'] = []
            
        except Exception as e:
            context['error_message'] = 'Error loading system statistics.'
            print(f"Admin error: {e}")
    
    # Determine template based on user role
    if user.is_admin():
        template = 'accounts/admin_dashboard.html'
    elif user.is_teacher():
        template = 'accounts/teacher_dashboard.html'
    elif user.is_student():
        template = 'accounts/student_dashboard.html'
    else:
        template = 'accounts/dashboard.html'
    
    return render(request, template, context)