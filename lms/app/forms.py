from django import forms
from django.core import validators
from froala_editor.widgets import FroalaEditor
from .models import Announcement, Assignment, Material


from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']


class FacultyLoginForm(forms.Form):
    faculty_id = forms.IntegerField(label='Faculty ID')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

# forms.py
from django import forms
from .models import Course, Department

class CourseForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'studentKey', 'facultyKey']

from django import forms
from .models import Faculty, Department

class FacultyForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Faculty
        fields = ['faculty_id', 'name', 'email', 'password', 'department', 'role', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['photo'].widget.attrs.update({'class': 'form-control'})

from django import forms
from .models import Student, Department, Course

from django import forms
from .models import Student, Department, Course

class CourseCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render_option(self, selected_choices, option_value, option_label, attrs):
        option_value = str(option_value)
        if option_value in selected_choices:
            attrs['checked'] = True
        return super().render_option(selected_choices, option_value, option_label, attrs)

from django import forms
from .models import Course, Department, Student

from django import forms
from .models import Course, Department, Student

# views.py

from django import forms
from .models import Student, Department

class StudentForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email', 'password', 'role', 'department', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['photo'].widget.attrs.update({'class': 'form-control'})
# forms.py
from django import forms

class StudentLoginForm(forms.Form):
    student_id = forms.CharField(label='Student ID', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['description'].label = ''

    class Meta:
        model = Announcement
        fields = ['description']
        widgets = {
            'description': FroalaEditor(),
        }


class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.label = ''
        self.fields['file'].required = False

    class Meta:
        model = Assignment
        fields = ('title', 'description', 'deadline', 'marks', 'file')
        widgets = {
            'description': FroalaEditor(),
            'title': forms.TextInput(attrs={'class': 'form-control mt-1', 'id': 'title', 'name': 'title', 'placeholder': 'Title'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control mt-1', 'id': 'deadline', 'name': 'deadline', 'type': 'datetime-local'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control mt-1', 'id': 'marks', 'name': 'marks', 'placeholder': 'Marks'}),
            'file': forms.FileInput(attrs={'class': 'form-control mt-1', 'id': 'file', 'name': 'file', 'aria-describedby': 'file', 'aria-label': 'Upload'}),
        }

from django import forms
from .models import Course

from django import forms

class FacultyKeyForm(forms.Form):
    course_id = forms.IntegerField(label='Course ID')
    faculty_key = forms.IntegerField(label='Faculty Key')

    def clean(self):
        cleaned_data = super().clean()
        course_id = cleaned_data.get('course_id')
        faculty_key = cleaned_data.get('faculty_key')

        # Validate faculty key against the faculty keys associated with the course ID
        if course_id and faculty_key:
            try:
                course = Course.objects.get(code=course_id)
                if course.facultyKey != faculty_key:
                    raise forms.ValidationError('Invalid Faculty Key for the selected course.')
            except Course.DoesNotExist:
                raise forms.ValidationError('Invalid Course ID')

        return cleaned_data


class MaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            field.label = ""
        self.fields['file'].required = False

    class Meta:
        model = Material
        fields = ('description', 'file')
        widgets = {
            'description': FroalaEditor(),
            'file': forms.FileInput(attrs={'class': 'form-control', 'id': 'file', 'name': 'file', 'aria-describedby': 'file', 'aria-label': 'Upload'}),
        }


class StudentKeyForm:
    course_id = forms.IntegerField(label='Course ID')
    student_key = forms.IntegerField(label='Student Key')

    def clean(self):
        cleaned_data = super().clean()
        course_id = cleaned_data.get('course_id')
        student_key = cleaned_data.get('student_key')

        # Validate student key against the student keys associated with the course ID
        if course_id and student_key:
            try:
                course = Course.objects.get(code=course_id)
                if course.studentkey != student_key:
                    raise forms.ValidationError('Invalid Student Key for the selected course.')
            except Course.DoesNotExist:
                raise forms.ValidationError('Invalid Course ID')

        return cleaned_data