import datetime

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import Student, Course, Announcement, Assignment, Submission, Material, Faculty, Department
from django.template.defaulttags import register
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from .forms import AnnouncementForm, AssignmentForm, MaterialForm, CourseForm, FacultyForm, StudentForm
from django import forms
from django.core import validators

from django import forms


def is_student_authorised(request, code):
    course = Course.objects.get(code=code)
    if request.session.get('student_id') and course in Student.objects.get(
            student_id=request.session['student_id']).course.all():
        return True
    else:
        return False


def is_faculty_authorised(request, code):
    if request.session.get('faculty_id') and code in Course.objects.filter(
            faculty_id=request.session['faculty_id']).values_list('code', flat=True):
        return True
    else:
        return False


def std_logout(request):
    request.session.flush()
    return redirect('std_login')


# Display all courses (student view)
def myCourses(request):
    try:
        if request.session.get('student_id'):
            student = Student.objects.get(
                student_id=request.session['student_id'])
            coursess = student.course.all()
            faculty = student.course.all().values_list('faculty_id', flat=True)

            context = {
                'courses': courses,
                'student': student,
                'faculty': faculty
            }

            return render(request, 'main/myCourses.html', context)
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Display all courses (faculty view)
def facultyCourses(request):
    try:
        if request.session['faculty_id']:
            faculty = Faculty.objects.get(
                faculty_id=request.session['faculty_id'])
            coursess = Course.objects.filter(
                faculty_id=request.session['faculty_id'])
            # Student count of each course to show on the faculty page
            studentCount = Course.objects.all().annotate(student_count=Count('students'))

            studentCountDict = {}

            for course in studentCount:
                studentCountDict[course.code] = course.student_count

            @register.filter
            def get_item(dictionary, course_code):
                return dictionary.get(course_code)

            context = {
                'courses': coursess,
                'faculty': faculty,
                'studentCount': studentCountDict
            }

            return render(request, 'main/facultyCourses.html', context)

        else:
            return redirect('std_login')
    except:

        return redirect('std_login')


# Particular course page (student view)
def course_page(request, code):
    try:
        course = Course.objects.get(code=code)
        if is_student_authorised(request, code):
            try:
                announcements = Announcement.objects.filter(course_code=course)
                assignments = Assignment.objects.filter(
                    course_code=course.code)
                materials = Material.objects.filter(course_code=course.code)

            except:
                announcements = None
                assignments = None
                materials = None

            context = {
                'course': course,
                'announcements': announcements,
                'assignments': assignments[:3],
                'materials': materials,
                'student': Student.objects.get(student_id=request.session['student_id'])
            }

            return render(request, 'main/course.html', context)

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Particular course page (faculty view)
def course_page_faculty(request, code):
    course = Course.objects.get(code=code)
    if request.session.get('faculty_id'):
        try:
            announcements = Announcement.objects.filter(course_code=course)
            assignments = Assignment.objects.filter(
                course_code=course.code)
            materials = Material.objects.filter(course_code=course.code)
            studentCount = Student.objects.filter(course=course).count()

        except:
            announcements = None
            assignments = None
            materials = None

        context = {
            'course': course,
            'announcements': announcements,
            'assignments': assignments[:3],
            'materials': materials,
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
            'studentCount': studentCount
        }

        return render(request, 'main/faculty_course.html', context)
    else:
        return redirect('std_login')


def error(request):
    return render(request, 'error.html')


# Display user profile(student & faculty)
def profile(request, id):
    try:
        if request.session['student_id'] == id:
            student = Student.objects.get(student_id=id)
            return render(request, 'main/profile.html', {'student': student})
        else:
            return redirect('std_login')
    except:
        try:
            if request.session['faculty_id'] == id:
                faculty = Faculty.objects.get(faculty_id=id)
                return render(request, 'main/faculty_profile.html', {'faculty': faculty})
            else:
                return redirect('std_login')
        except:
            return render(request, 'error.html')


def addAnnouncement(request, code):
    if is_faculty_authorised(request, code):
        if request.method == 'POST':
            form = AnnouncementForm(request.POST)
            form.instance.course_code = Course.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Announcement added successfully.')
                return redirect('/faculty/' + str(code))
        else:
            form = AnnouncementForm()
        return render(request, 'main/announcement.html', {'course': Course.objects.get(code=code),
                                                          'faculty': Faculty.objects.get(
                                                              faculty_id=request.session['faculty_id']), 'form': form})
    else:
        return redirect('std_login')


def deleteAnnouncement(request, code, id):
    if is_faculty_authorised(request, code):
        try:
            announcement = Announcement.objects.get(course_code=code, id=id)
            announcement.delete()
            messages.warning(request, 'Announcement deleted successfully.')
            return redirect('/faculty/' + str(code))
        except:
            return redirect('/faculty/' + str(code))
    else:
        return redirect('std_login')


def editAnnouncement(request, code, id):
    if is_faculty_authorised(request, code):
        announcement = Announcement.objects.get(course_code_id=code, id=id)
        form = AnnouncementForm(instance=announcement)
        context = {
            'announcement': announcement,
            'course': Course.objects.get(code=code),
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
            'form': form
        }
        return render(request, 'main/update-announcement.html', context)
    else:
        return redirect('std_login')


def updateAnnouncement(request, code, id):
    if is_faculty_authorised(request, code):
        try:
            announcement = Announcement.objects.get(course_code_id=code, id=id)
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                messages.info(request, 'Announcement updated successfully.')
                return redirect('/faculty/' + str(code))
        except:
            return redirect('/faculty/' + str(code))

    else:
        return redirect('std_login')


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AssignmentForm
from .models import Course, Faculty



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AssignmentForm
from .models import Course

def addAssignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            course_code = form.cleaned_data.get('course_code')
            try:
                course = Course.objects.get(code=course_code)
                form.instance.course_code = course
                form.save()
                messages.success(request, 'Assignment added successfully.')
                return redirect('/faculty/' + str(course_code))
            except Course.DoesNotExist:
                messages.error(request, 'Course with code {} does not exist.'.format(course_code))
                # Handle the error appropriately, such as displaying a message or redirecting to another page
                # For now, let's render the form again with the same form data
                return render(request, 'assignment.html', {'form': form})
    else:
        form = AssignmentForm()

    return render(request, 'assignment.html', {'form': form})


def assignmentPage(request, code, id):
    course = Course.objects.get(code=code)
    if is_student_authorised(request, code):
        assignment = Assignment.objects.get(course_code=course.code, id=id)
        try:

            submission = Submission.objects.get(assignment=assignment, student=Student.objects.get(
                student_id=request.session['student_id']))

            context = {
                'assignment': assignment,
                'course': course,
                'submission': submission,
                'time': datetime.datetime.now(),
                'student': Student.objects.get(student_id=request.session['student_id']),
                'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
            }

            return render(request, 'main/assignment-portal.html', context)

        except:
            submission = None

        context = {
            'assignment': assignment,
            'course': course,
            'submission': submission,
            'time': datetime.datetime.now(),
            'student': Student.objects.get(student_id=request.session['student_id']),
            'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
        }

        return render(request, 'main/assignment-portal.html', context)
    else:

        return redirect('std_login')


def allAssignments(request, code):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        assignments = Assignment.objects.filter(course_code=course)
        studentCount = Student.objects.filter(course=course).count()

        context = {
            'assignments': assignments,
            'course': course,
            'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
            'studentCount': studentCount

        }
        return render(request, 'main/all-assignments.html', context)
    else:
        return redirect('std_login')


from django.shortcuts import render, redirect
from .models import Course, Assignment, Student


def allAssignmentsSTD(request):
    if 'student_id' in request.session:  # Assuming you store student_id in the session
        student = Student.objects.get(student_id=request.session['student_id'])
        courses_enrolled = student.courses.all()  # Assuming there's a ManyToManyField linking students to courses
        assignments = Assignment.objects.filter(course_code__in=courses_enrolled)
        context = {
            'assignments': assignments,
            'student': student,
        }
        return render(request, 'main/all-assignments-std.html', context)
    else:
        return redirect('std_login')


def addSubmission(request, code, id):
    try:
        course = Course.objects.get(code=code)
        if is_student_authorised(request, code):
            # check if assignment is open
            assignment = Assignment.objects.get(course_code=course.code, id=id)
            if assignment.deadline < datetime.datetime.now():
                return redirect('/assignment/' + str(code) + '/' + str(id))

            if request.method == 'POST' and request.FILES['file']:
                assignment = Assignment.objects.get(
                    course_code=course.code, id=id)
                submission = Submission(assignment=assignment, student=Student.objects.get(
                    student_id=request.session['student_id']), file=request.FILES['file'], )
                submission.status = 'Submitted'
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                assignment = Assignment.objects.get(
                    course_code=course.code, id=id)
                submission = Submission.objects.get(assignment=assignment, student=Student.objects.get(
                    student_id=request.session['student_id']))
                context = {
                    'assignment': assignment,
                    'course': course,
                    'submission': submission,
                    'time': datetime.datetime.now(),
                    'student': Student.objects.get(student_id=request.session['student_id']),
                    'courses': Student.objects.get(student_id=request.session['student_id']).course.all()
                }

                return render(request, 'main/assignment-portal.html', context)
        else:
            return redirect('std_login')
    except:
        return HttpResponseRedirect(request.path_info)


def viewSubmission(request, code, id):
    course = Course.objects.get(code=code)
    if is_faculty_authorised(request, code):
        try:
            assignment = Assignment.objects.get(course_code_id=code, id=id)
            submissions = Submission.objects.filter(
                assignment_id=assignment.id)

            context = {
                'course': course,
                'submissions': submissions,
                'assignment': assignment,
                'totalStudents': len(Student.objects.filter(course=course)),
                'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
                'courses': Course.objects.filter(faculty_id=request.session['faculty_id'])
            }

            return render(request, 'main/assignment-view.html', context)

        except:
            return redirect('/faculty/' + str(code))
    else:
        return redirect('std_login')


def gradeSubmission(request, code, id, sub_id):
    try:
        course = Course.objects.get(code=code)
        if is_faculty_authorised(request, code):
            if request.method == 'POST':
                assignment = Assignment.objects.get(course_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    assignment_id=assignment.id)
                submission = Submission.objects.get(
                    assignment_id=id, id=sub_id)
                submission.marks = request.POST['marks']
                if request.POST['marks'] == 0:
                    submission.marks = 0
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                assignment = Assignment.objects.get(course_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    assignment_id=assignment.id)
                submission = Submission.objects.get(
                    assignment_id=id, id=sub_id)

                context = {
                    'course': course,
                    'submissions': submissions,
                    'assignment': assignment,
                    'totalStudents': len(Student.objects.filter(course=course)),
                    'faculty': Faculty.objects.get(faculty_id=request.session['faculty_id']),
                    'courses': Course.objects.filter(faculty_id=request.session['faculty_id'])
                }

                return render(request, 'main/assignment-view.html', context)

        else:
            return redirect('std_login')
    except:
        return redirect('/error/')


def addCourseMaterial(request, code):
    if is_faculty_authorised(request, code):
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            form.instance.course_code = Course.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(request, 'New course material added')
                return redirect('/faculty/' + str(code))
            else:
                return render(request, 'main/course-material.html', {'course': Course.objects.get(code=code),
                                                                     'faculty': Faculty.objects.get(
                                                                         faculty_id=request.session['faculty_id']),
                                                                     'form': form})
        else:
            form = MaterialForm()
            return render(request, 'main/course-material.html', {'course': Course.objects.get(code=code),
                                                                 'faculty': Faculty.objects.get(
                                                                     faculty_id=request.session['faculty_id']),
                                                                 'form': form})
    else:
        return redirect('std_login')


def deleteCourseMaterial(request, code, id):
    if is_faculty_authorised(request, code):
        course = Course.objects.get(code=code)
        course_material = Material.objects.get(course_code=course, id=id)
        course_material.delete()
        messages.warning(request, 'Course material deleted')
        return redirect('/faculty/' + str(code))
    else:
        return redirect('std_login')


def courses(request):
    if request.session.get('student_id') or request.session.get('faculty_id'):

        courses = Course.objects.all()
        if request.session.get('student_id'):
            student = Student.objects.get(
                student_id=request.session['student_id'])
        else:
            student = None
        if request.session.get('faculty_id'):
            faculty = Faculty.objects.get(
                faculty_id=request.session['faculty_id'])
        else:
            faculty = None

        enrolled = student.course.all() if student else None
        accessed = Course.objects.filter(
            faculty_id=faculty.faculty_id) if faculty else None

        context = {
            'faculty': faculty,
            'courses': courses,
            'student': student,
            'enrolled': enrolled,
            'accessed': accessed
        }

        return render(request, 'main/all-courses.html', context)

    else:
        return redirect('std_login')


def departments(request):
    if request.session.get('student_id') or request.session.get('faculty_id'):
        departments = Department.objects.all()
        if request.session.get('student_id'):
            student = Student.objects.get(
                student_id=request.session['student_id'])
        else:
            student = None
        if request.session.get('faculty_id'):
            faculty = Faculty.objects.get(
                faculty_id=request.session['faculty_id'])
        else:
            faculty = None
        context = {
            'faculty': faculty,
            'student': student,
            'deps': departments
        }

        return render(request, 'main/departments.html', context)

    else:
        return redirect('std_login')


def access(request, code):
    if request.session.get('student_id'):
        course = Course.objects.get(code=code)
        student = Student.objects.get(student_id=request.session['student_id'])
        if request.method == 'POST':
            if (request.POST['key']) == str(course.studentKey):
                student.course.add(course)
                student.save()
                return redirect('/my/')
            else:
                messages.error(request, 'Invalid key')
                return HttpResponseRedirect(request.path_info)
        else:
            return render(request, 'main/access.html', {'course': course, 'student': student})

    else:
        return redirect('std_login')


def search(request):
    if request.session.get('student_id') or request.session.get('faculty_id'):
        if request.method == 'GET' and request.GET['q']:
            q = request.GET['q']
            courses = Course.objects.filter(Q(code__icontains=q) | Q(
                name__icontains=q) | Q(faculty__name__icontains=q))

            if request.session.get('student_id'):
                student = Student.objects.get(
                    student_id=request.session['student_id'])
            else:
                student = None
            if request.session.get('faculty_id'):
                faculty = Faculty.objects.get(
                    faculty_id=request.session['faculty_id'])
            else:
                faculty = None
            enrolled = student.course.all() if student else None
            accessed = Course.objects.filter(
                faculty_id=faculty.faculty_id) if faculty else None

            context = {
                'courses': courses,
                'faculty': faculty,
                'student': student,
                'enrolled': enrolled,
                'accessed': accessed,
                'q': q
            }
            return render(request, 'main/search.html', context)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('std_login')


def changePasswordPrompt(request):
    if request.session.get('student_id'):
        student = Student.objects.get(student_id=request.session['student_id'])
        return render(request, 'main/changePassword.html', {'student': student})
    elif request.session.get('faculty_id'):
        faculty = Faculty.objects.get(faculty_id=request.session['faculty_id'])
        return render(request, 'main/changePasswordFaculty.html', {'faculty': faculty})
    else:
        return redirect('std_login')


def changePhotoPrompt(request):
    if request.session.get('student_id'):
        student = Student.objects.get(student_id=request.session['student_id'])
        return render(request, 'main/changePhoto.html', {'student': student})
    elif request.session.get('faculty_id'):
        faculty = Faculty.objects.get(faculty_id=request.session['faculty_id'])
        return render(request, 'main/changePhotoFaculty.html', {'faculty': faculty})
    else:
        return redirect('std_login')


def changePassword(request):
    if request.session.get('student_id'):
        student = Student.objects.get(
            student_id=request.session['student_id'])
        if request.method == 'POST':
            if student.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                student.password = request.POST['newPassword']
                student.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/profile/' + str(student.student_id))
            else:
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePassword/')
        else:
            return render(request, 'main/changePassword.html', {'student': student})
    else:
        return redirect('std_login')


def changePasswordFaculty(request):
    if request.session.get('faculty_id'):
        faculty = Faculty.objects.get(
            faculty_id=request.session['faculty_id'])
        if request.method == 'POST':
            if faculty.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                faculty.password = request.POST['newPassword']
                faculty.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/facultyProfile/' + str(faculty.faculty_id))
            else:
                print('error')
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePasswordFaculty/')
        else:
            print(faculty)
            return render(request, 'main/changePasswordFaculty.html', {'faculty': faculty})
    else:
        return redirect('std_login')


def changePhoto(request):
    if request.session.get('student_id'):
        student = Student.objects.get(
            student_id=request.session['student_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                student.photo = request.FILES['photo']
                student.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/profile/' + str(student.student_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhoto/')
        else:
            return render(request, 'main/changePhoto.html', {'student': student})
    else:
        return redirect('std_login')


def changePhotoFaculty(request):
    if request.session.get('faculty_id'):
        faculty = Faculty.objects.get(
            faculty_id=request.session['faculty_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                faculty.photo = request.FILES['photo']
                faculty.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/facultyProfile/' + str(faculty.faculty_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhotoFaculty/')
        else:
            return render(request, 'main/changePhotoFaculty.html', {'faculty': faculty})
    else:
        return redirect('std_login')


def guestStudent(request):
    request.session.flush()
    try:
        student = Student.objects.get(name='Guest Student')
        request.session['student_id'] = str(student.student_id)
        return redirect('myCourses')
    except:
        return redirect('std_login')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages


def faculty_login(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        password = request.POST.get('password')
        faculty = authenticate(request, faculty_id=faculty_id, password=password)
        if faculty is not None:
            login(request, faculty)
            return redirect('faculty_home')  # Redirect to the home page after successful login
        else:
            error_message = "Invalid credentials. Please try again."
            return render(request, 'faculty_login.html', {'error_message': error_message})
    else:
        return render(request, 'faculty_login.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if user exists and is a superuser
        if user is not None and user.is_superuser:
            # Login the user
            login(request, user)
            # Redirect to admin homepage
            return redirect("admin_homepage")
        else:
            # If authentication fails or user is not a superuser, render login page with alert
            alert = True
            return render(request, "admin_login.html", {"alert": alert})

    # If GET request, render the login page
    return render(request, "admin_login.html")


def homepage(request):
    return render(request, "admin_homepage.html")


from .forms import DepartmentForm

from django.shortcuts import render, redirect
from .forms import DepartmentForm  # Import your DepartmentForm


def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to create a new department
            # Redirect to the same page after successful form submission
            return redirect('all_departments')
    else:
        form = DepartmentForm()

    return render(request, 'create_department.html', {'form': form})


def all_departments(request):
    departments = Department.objects.all()
    return render(request, 'all_departments.html', {'departments': departments})


def update_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('all_departments')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'update_department.html', {'form': form})


def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('all_departments')
    return render(request, 'delete_department.html', {'department': department})


from django.shortcuts import render, redirect
from .forms import CourseForm
from .models import Course, Department

# views.py

from django.shortcuts import render, redirect
from .forms import CourseForm  # Import the CourseForm
from .models import Course, Department  # Import the Course and Department models


def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_courses')  # Redirect to the URL name 'all_courses'
    else:
        form = CourseForm()

    departments = Department.objects.all()

    return render(request, 'create_course.html', {'form': form, 'departments': departments})


def all_courses(request):
    courses = Course.objects.all()
    return render(request, 'all_courses.html', {'courses': courses})


from django.contrib.auth.hashers import make_password
from .models import Faculty


def create_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new Faculty object
            faculty = form.save(commit=False)
            # Hash the password before saving
            faculty.password = make_password(form.cleaned_data['password'])
            # Save the faculty instance with hashed password
            faculty.save()
            return redirect('faculty_list')  # Redirect to faculty list page
    else:
        form = FacultyForm()
    return render(request, 'create_faculty.html', {'form': form})


def faculty_list(request):
    # Fetch all faculty members from the database
    faculties = Faculty.objects.all()
    # Render the faculty list template with the list of faculties
    return render(request, 'faculty_list.html', {'faculties': faculties})


import pandas as pd
from django.shortcuts import render
from .forms import StudentForm
import openpyxl


def create_student(request):
    if request.method == 'POST':
        print("Processing POST request...")
        form = StudentForm(request.POST)
        if form.is_valid():
            # Create a new Faculty object
            student = form.save(commit=False)
            # Hash the password before saving
            student.password = make_password(form.cleaned_data['password'])
            # Save the faculty instance with hashed password
            student.save()
            print("Student created successfully!")
            return redirect('student_list')  # Redirect to faculty list page
        else:
            # views.py

            excel_file = request.FILES['file']

            # Load the Excel file
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active

            for row in sheet.iter_rows(values_only=True):
                student_id, name, email, password, role, department, photo = row
                # Create a dictionary to hold the data
                student_data = {
                    'student_id': student_id,
                    'name': name,
                    'email': email,
                    'password': password,
                    'role': role,
                    'department': department,
                    'photo': photo
                }
                # Create a form instance and populate it with data from the request:
                form = StudentForm(student_data)
                if form.is_valid():
                    # Save the student object to the database
                    form.save()
                    return redirect('student_list')
                else:
                    print("Invalid form data:", form.errors)


    else:
        print("Request method is not POST.")
        form = StudentForm()
    return render(request, 'create_student.html', {'form': form})


def std_login(request):
    return render(request, 'login_page.html', )


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import FacultyLoginForm
from .models import Faculty

# views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import FacultyLoginForm
from .models import Faculty

from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from .models import Faculty
from .forms import FacultyLoginForm

from django.contrib.auth.hashers import check_password

from django.contrib.auth.hashers import check_password

from django.contrib.auth.hashers import check_password


def faculty_login(request):
    if request.method == 'POST':
        form = FacultyLoginForm(request.POST)
        if form.is_valid():
            faculty_id = form.cleaned_data['faculty_id']
            password = form.cleaned_data['password']

            # Get the faculty object corresponding to the entered faculty_id
            try:
                faculty = Faculty.objects.get(faculty_id=faculty_id)
            except Faculty.DoesNotExist:
                error_message = 'Invalid faculty ID.'
                return render(request, 'faculty_login.html', {'form': form, 'error_message': error_message})

            # Check if the entered password matches the password stored in the database
            if check_password(password, faculty.password):
                # Set session variables to indicate the user is logged in
                request.session['faculty_id'] = faculty.faculty_id
                request.session['faculty_name'] = faculty.name
                return redirect('faculty_home')
            else:
                error_message = 'Invalid password.'

            return render(request, 'faculty_login.html', {'form': form, 'error_message': error_message})

    else:
        form = FacultyLoginForm()

    return render(request, 'faculty_login.html', {'form': form})


# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def student_login(request):
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            password = form.cleaned_data['password']

            # Get the faculty object corresponding to the entered faculty_id
            try:
                student = Student.objects.get(student_id=student_id)
            except Student.DoesNotExist:
                error_message = 'Invalid faculty ID.'
                return render(request, 'student_login.html', {'form': form, 'error_message': error_message})

            # Check if the entered password matches the password stored in the database
            if check_password(password, student.password):
                # Set session variables to indicate the user is logged in
                request.session['student_id'] = student.student_id
                request.session['student_name'] = student.name
                return redirect('student_home')
            else:
                error_message = 'Invalid password.'

            return render(request, 'student_login.html', {'form': form, 'error_message': error_message})

    else:
        form = StudentLoginForm()

    return render(request, 'student_login.html', {'form': form})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import StudentLoginForm
from .models import Student


def faculty_home(request):
    return render(request, 'faculty_home.html')


def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})


def student_home(request):
    return render(request, 'student_home.html')


def mycourses(request):
    try:
        if request.session.get('student_id'):
            student = Student.objects.get(
                student_id=request.session['student_id'])
            courses = student.course.all()
            faculty = student.course.all().values_list('faculty_id', flat=True)

            context = {
                'courses': courses,
                'student': student,
                'faculty': faculty
            }

            return render(request, 'myCourses.html', context)
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def std_logout(request):
    request.session.flush()
    return redirect('std_login')


from django.shortcuts import render, redirect, HttpResponse
from .models import Course, Faculty

from django.shortcuts import render, redirect, HttpResponse
from .models import Course  # Import the Course model


def access_course(request, course_code):
    if request.method == 'POST':
        course = Course.objects.get(code=course_code)
        faculty_key = request.POST.get('faculty_key', None)
        if course.facultyKey == faculty_key:
            # Perform any action you need, such as redirecting to the course page
            return HttpResponse("Access granted!")  # Replace with your logic
        else:
            return HttpResponse("Access denied!")  # Replace with your logic
    else:
        course = Course.objects.get(code=course_code)
        return render(request, 'access_course.html', {'course': course})


# views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # Import the login_required decorator
from .models import Course
from django.shortcuts import render
from django.http import HttpResponse
from .forms import FacultyKeyForm
from .models import Course

from django.shortcuts import render
from .forms import FacultyKeyForm
from .models import Course

def faculty_courses(request):
    if request.method == 'POST':
        form = FacultyKeyForm(request.POST)
        if form.is_valid():
            faculty_key = form.cleaned_data['faculty_key']
            courses = Course.objects.filter(facultyKey=faculty_key)
            return render(request, 'faculty_courses.html', {'courses': courses})
    else:
        form = FacultyKeyForm()

    return render(request, 'enter_faculty_key.html', {'form': form})
def student_courses(request):
    if request.method == 'POST':
        form = FacultyKeyForm(request.POST)
        if form.is_valid():
            student_key = form.cleaned_data['student_key']
            courses = Course.objects.filter(studentKey=student_key)
            return render(request, 'student_courses.html', {'courses': courses})
    else:
        form = FacultyKeyForm()

    return render(request, 'enter_student_key.html', {'form': form})



from django.shortcuts import render
from django.http import HttpResponse
from .forms import FacultyKeyForm
from .models import Course

from django.shortcuts import render
from django.http import HttpResponse
from .forms import FacultyKeyForm

def enter_faculty_key(request):
    if request.method == 'POST':
        form = FacultyKeyForm(request.POST)
        if form.is_valid():
            # Handle the valid form submission here
            return HttpResponse("Faculty key validated successfully.")
    else:
        form = FacultyKeyForm()

    return render(request, 'enter_faculty_key.html', {'form': form})

from .forms import StudentKeyForm
def enter_student_key(request):
    if request.method == 'POST':
        form = StudentKeyForm(request.POST)
        if form.is_valid():
            # Handle the valid form submission here
            return HttpResponse("student key validated successfully.")
    else:
        form = StudentKeyForm()

    return render(request, 'student_courses.html', {'form': form})