from django.urls import path
from . import views

urlpatterns = [
    path('student_login/', views.student_login, name='student_login'),
    path('faculty_login/', views.faculty_login, name='faculty_login'),

    path("admin_login/", views.admin_login, name="admin_login"),
    path("admin_homepage/", views.homepage, name="admin_homepage"),
    path('create_department/', views.create_department, name='create_department'),
    path('departments/', views.all_departments, name='all_departments'),
    path('departments/create/',views.create_department, name='create_department'),
    path('departments/<int:pk>/update/', views.update_department, name='update_department'),
    path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),
    path('all_courses/', views.all_courses, name='all_courses'),
    path('student-assignments/', views.allAssignmentsSTD, name='student-assignments'),
    path('courses/create/', views.create_course, name='create_course'),
    path('create_faculty/', views.create_faculty, name='create_faculty'),
    path('faculty_list/', views.faculty_list, name='faculty_list'),
    path('faculty_home/', views.faculty_home, name='faculty_home'),
    path('create_student/', views.create_student, name='create_student'),
    path('student_list/', views.student_list, name='student_list'),
    path('student_home/', views.student_home, name='student_home'),
    path('mycourses/', views.mycourses, name='mycourses'),
    path('logout/', views.std_logout, name='std_logout'),
    path('faculty-courses/',views.faculty_courses, name='faculty_courses'),
    path('enter-faculty-key/',views.enter_faculty_key, name='enter_faculty_key'),
    path('student_courses/',views.student_courses, name='student_courses'),
    path('enter-student-key/',views.enter_student_key, name='enter_student_key'),
    path('addAssignment/', views.addAssignment, name='addAssignment'),


    path('', views.std_login, name='std_login'),
]