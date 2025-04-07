from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from .models import Course, Lesson, Student
from .forms import CourseForm, LessonForm, StudentForm, UserUpdateForm
from django.contrib import messages
from django.conf import settings
# from django.views.generic import ListView, DetailView
# from django.views.generic.edit import CreateView
# from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer

# Home Page
def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        subject = f'Contact Form from {email}'
        body = message
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = ['fantasyfalcoon91@gmail.com']
        
        # Add sender's email to the reply_to list
        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_email,
            reply_to=[email],  # <-- This is important!
        )
        email_message.send(fail_silently=False)
        
        messages.success(request, "Your message has been sent!")
        
    return render(request, 'courses/home.html')

# Course List
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/index.html', {'courses': courses})

# class CourseListView(ListView):
#     model = Course
#     template_name = 'courses/index.html'
#     context_object_name = 'courses'

# API for Course List
class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Course Detail
@login_required
def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    return render(request, 'courses/description.html', {'course': course, 'lessons': lessons})

# class CourseDetailView(DetailView):
#     model = Course
#     template_name = 'courses/description.html'
#     context_object_name = 'course'

# API for Course Detail
class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error':'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Create Course
@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

# class CourseCreateView(CreateView):
#     model = Course
#     fields = ['title', 'description', 'duration', 'thumbnail']
#     template_name = 'courses/course_form.html'
#     success_url = reverse_lazy('course_list')

# Update Course
@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})

# Delete Course
@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Create Lesson
@login_required
def lesson_create(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('course_list')
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form})

# Update Lesson
@login_required
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})

# Delete Lesson
@login_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

# Student Enrollment
@login_required
def enroll_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.course = course  # Automatically assign the course
            student.save()
            student.enrolled_courses.add(course)  # Add course to the student's ManyToMany field
            # return redirect("student_list", course_id=course.id)
            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
    else:
        form = StudentForm()
    return render(request, "courses/enroll_student.html", {"form": form, "course": course})

# API for Student Enrollment
class EnrollStudentAPI(APIView):
    def post(self, request):
        student_email = request.data.get('email')
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        student, created = Student.objects.get_or_create(email=student_email)
        student.enrolled_courses.add(course)
        return Response({'message': f'{student.email} has been enrolled in {course.title} successfully!'}, status=status.HTTP_201_CREATED)

# View Enrolled Students
@login_required
def student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(enrolled_courses=course)  # Fetch students enrolled in this course
    return render(request, 'courses/student_list.html', {'course': course, 'students': students})

# Edit Student
@login_required
def edit_student(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated successfully!")
            return redirect("student_list", course_id=course_id)  # Redirect to student's course
    else:
        form = StudentForm(instance=student)

    return render(request, "courses/edit_student.html", {"form": form, "student": student})

# Delete Student
@login_required
def delete_student(request, student_id, course_id):
    student = get_object_or_404(Student, id=student_id)
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("student_list", course_id=course_id)  # Redirect after deletion

    return render(request, "courses/student_confirm_delete.html", {"student": student})


# User Registration
def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "courses/register.html", {"form": form})

# User Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('course_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'courses/login.html', {'form': form})

# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# @login_required
# def course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'courses/index.html', {'courses': courses})

@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'courses/profile.html', {'form': form})

@login_required
def student_lesson_progress(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, id=student_id)
    lessons = course.lessons.all()
    completed_lessons = student.completed_lessons.filter(course=course)

    total_lessons = lessons.count()
    completed_count = completed_lessons.count()
    progress = (completed_count / total_lessons) * 100 if total_lessons > 0 else 0

    context = {
        'course': course,
        'student': student,
        'lessons': lessons,
        'completed_lessons': completed_lessons,
        'progress': progress,
    }
    return render(request, 'courses/student_lesson_progress.html', context)