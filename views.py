from django.shortcuts import render
from app.models import *
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView
from django.conf import settings
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm
from django.utils.safestring import mark_safe
from datetime import datetime
from django.utils import timezone
from django.urls import reverse
import json


def home(request):
    news = News.objects.all()
    return render(request, "teacher_app/home.html", locals())


def send_verification_email(user, token):
    domain = 'http://127.0.0.1:8000/teacher'

    mail_subject = "Activate your account"
    message = render_to_string(
        "teacher_app/verification_email.html",
        {
            "user": user,
            "domain": domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": token,
        },
    )
    send_mail(mail_subject, message, "noreplylmskz@gmail.com", [user.email])


def email_confirmed_view(request):
    return render(request, 'teacher_app/email_confirmed.html')


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "teacher_app/registration.html", locals())

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_staff = True
            user.save()

            token_generator = default_token_generator
            token = token_generator.make_token(user)
            send_verification_email(user, token)

            messages.success(request, "Please check your email to complete the registration.",
                             extra_tags="registration")

        else:
            messages.warning(request, "Invalid information", extra_tags="registration")
        return render(request, "teacher_app/registration.html", locals())


class AccountActivationView(View):
    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        token_generator = default_token_generator
        if token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated. You can now log in.", extra_tags="activation")
            return redirect('t_email_confirmed')

        messages.error(request, "Invalid activation link.", extra_tags="activation")
        return redirect('t_email_confirmed')


class TeacherLoginView(LoginView):
    template_name = 'teacher_app/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return str(settings.LOGIN_REDIRECT_URL_TEACHER)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'teacher_app/forgot_password.html'
    email_template_name = 'teacher_app/reset_password_email.html'
    success_url = '/teacher/login/'
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, "This email address does not exist.", extra_tags="email_not_exist")
            return self.form_invalid(form)
        elif not User.objects.filter(email=email, is_staff=True).exists():
            messages.error(self.request, "Password reset is not allowed.", extra_tags="email_not_exist")
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'teacher_app/reset_password.html'
    success_url = '/teacher/login/'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, "teacher_app/profile.html", {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, "teacher_app/profile.html", {'form': form, 'saved': True})
        return render(request, "teacher_app/profile.html", {'form': form})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class CalendarView(View):
    def get(self, request):
        events = []
        event_data = mark_safe(json.dumps(events))
        return render(request, "teacher_app/calendar.html")


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class TeachingView(View):
    def get(self, request):
        return render(request, "teacher_app/teaching.html", locals())


def create_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('courseName')
        teacher = request.user
        course = Course.objects.create(name=course_name, creator=teacher)

        return redirect('teaching')

    return render(request, 'teacher_app/create_course.html')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class DeniedView(View):
    def get(self, request):
        return render(request, "teacher_app/access_denied.html", locals())


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class CourseStructureView(View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        all_students = User.objects.filter(is_staff=False).exclude(enrollment__course=course)
        all_enrolled_students = User.objects.filter(enrollment__course=course, is_staff=False)
        if course.creator != request.user:
            return redirect('http://127.0.0.1:8000/teacher/access_denied/')
        return render(request, "teacher_app/course_structure.html",
                      {'course': course, 'all_students': all_students, 'all_enrolled_students': all_enrolled_students})

    def post(self, request, pk):
        course = Course.objects.get(pk=pk)
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        if 'enroll' in request.POST:
            Enrollment.objects.create(user=user, course=course)

        elif 'unenroll' in request.POST:
            Enrollment.objects.filter(user=user, course=course).delete()

        return redirect('course_structure', pk=pk)


def delete_course(request, pk):
    if request.method == 'POST':
        course = Course.objects.get(pk=pk)
        course.delete()
        return redirect('teaching')
    else:
        return redirect('course_structure', pk=pk)


def edit_course(request, pk):
    course = Course.objects.get(pk=pk)

    if request.method == 'POST':
        course_name = request.POST['course_name']
        course.name = course_name
        course.save()
        return redirect('course_structure', pk=pk)

    return render(request, 'teacher_app/edit_course.html', {'course': course})


def enroll(request, course_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('http://127.0.0.1:8000/teacher/access_denied/')

    if request.method == 'POST':
        user_id = request.POST.get('student')
        user = User.objects.get(pk=user_id)
        course = Course.objects.get(pk=course_id)
        Enrollment.objects.create(user=user, course=course)

    return redirect('course_structure', pk=course_id)


def add_module(request, course_id):
    if request.method == 'POST':
        course = Course.objects.get(pk=course_id)
        module_name = request.POST['module_name']
        module = Module.objects.create(name=module_name, course=course)
        return redirect('course_structure', pk=course_id)
    else:
        course = Course.objects.get(pk=course_id)
        return render(request, 'teacher_app/add_module.html', {'course': course})


def delete_module(request, module_id):
    if request.method == 'POST':
        module = Module.objects.get(pk=module_id)
        course_pk = module.course.pk
        module.delete()
        return redirect('course_structure', pk=course_pk)
    else:
        return redirect('teaching')


def edit_module(request, module_id):
    module = Module.objects.get(pk=module_id)

    if request.method == 'POST':
        module_name = request.POST['module_name']
        module.name = module_name
        module.save()
        return redirect('course_structure', pk=module.course.pk)

    return render(request, 'teacher_app/edit_module.html', {'module': module})


def add_topic(request, module_id):
    if request.method == 'POST':
        module = Module.objects.get(pk=module_id)
        topic_name = request.POST['topic_name']
        topic = Topic.objects.create(name=topic_name, module=module)
        return redirect('course_structure', pk=module.course.pk)
    else:
        module = Module.objects.get(pk=module_id)
        return render(request, 'teacher_app/add_topic.html', {'module': module})


def delete_topic(request, topic_id):
    if request.method == 'POST':
        topic = Topic.objects.get(pk=topic_id)
        course_pk = topic.module.course.pk
        topic.delete()
        return redirect('course_structure', pk=course_pk)
    else:
        return redirect('teaching')


def edit_topic(request, topic_id):
    topic = Topic.objects.get(pk=topic_id)

    if request.method == 'POST':
        topic_name = request.POST['topic_name']
        topic.name = topic_name
        topic.save()
        return redirect('course_structure', pk=topic.module.course.pk)

    return render(request, 'teacher_app/edit_topic.html', {'topic': topic})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class TopicStructureView(View):
    def get(self, request, course_pk, pk):
        course = Course.objects.get(pk=course_pk)
        if course.creator != request.user:
            return redirect('http://127.0.0.1:8000/teacher/access_denied/')

        topic = Topic.objects.get(pk=pk)
        units = topic.unit_set.all()

        return render(request, 'teacher_app/topic_structure.html', {'topic': topic, 'units': units, 'course': course})


def add_unit(request, topic_id):
    unit_types = Unit.UNIT_TYPES

    if request.method == 'POST':
        topic = Topic.objects.get(pk=topic_id)
        course_pk = topic.module.course.pk
        unit_name = request.POST['unit_name']
        unit_type = request.POST['unit_type']
        unit = Unit.objects.create(name=unit_name, unit_type=unit_type, topic=topic)
        return redirect('topic_structure', course_pk=course_pk, pk=topic.pk)
    else:
        topic = Topic.objects.get(pk=topic_id)
        return render(request, 'teacher_app/add_unit.html', {'topic': topic, 'unit_types': unit_types})


def delete_unit(request, unit_id):
    if request.method == 'POST':
        unit = Unit.objects.get(pk=unit_id)
        topic = unit.topic
        course_pk = topic.module.course.pk
        unit.delete()
        return redirect('topic_structure', course_pk=course_pk, pk=topic.pk)
    else:
        return redirect('teaching')


def edit_unit(request, unit_id):
    unit = Unit.objects.get(pk=unit_id)
    unit_files = UnitFile.objects.filter(unit=unit)

    if unit.unit_type == 'C':
        if request.method == 'POST':
            unit_name = request.POST['unit_name']
            unit.name = unit_name
            unit.save()
            messages.success(request, 'Content name updated successfully.', extra_tags='edit_content')

        return render(request, 'teacher_app/edit_content_unit.html', {'unit': unit, 'unit_files': unit_files})

    elif unit.unit_type == 'A':
        assignment, created = Assignment.objects.get_or_create(unit=unit)

        if request.method == 'POST':
            unit_name = request.POST['unit_name']
            description = request.POST['description']
            deadline_date = request.POST['deadline_date']
            deadline_time = request.POST['deadline_time']
            max_grade = request.POST['max_grade']

            unit.name = unit_name
            unit.save()

            assignment.description = description
            if deadline_date and deadline_time:
                deadline = datetime.strptime(deadline_date + ' ' + deadline_time, '%Y-%m-%d %H:%M')
                assignment.deadline = deadline
            assignment.max_grade = max_grade
            assignment.save()

            messages.success(request, 'Assignment details updated successfully.', extra_tags='edit_assignment')

        return render(request, 'teacher_app/edit_assignment_unit.html',
                      {'unit': unit, 'assignment': assignment, 'unit_files': unit_files})


def upload_file(request, unit_id):
    unit = Unit.objects.get(pk=unit_id)

    if request.method == 'POST':
        form = UnitFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            UnitFile.objects.create(unit=unit, file=file)
            messages.success(request, 'File added successfully.', extra_tags='file_upload')

    return redirect('edit_unit', unit_id=unit_id)


def delete_file(request, file_id):
    file = UnitFile.objects.get(pk=file_id)
    unit_id = file.unit_id
    file.delete()
    return redirect('edit_unit', unit_id=unit_id)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda user: user.is_staff), name='dispatch')
@method_decorator(user_passes_test(lambda user: not user.is_superuser), name='dispatch')
class AssignmentSubmissionView(View):
    def get(self, request, unit_id):
        unit = Unit.objects.get(pk=unit_id)
        course = unit.topic.module.course
        if course.creator != request.user:
            return redirect('http://127.0.0.1:8000/teacher/access_denied/')
        submissions = AssignmentSubmission.objects.filter(assignment__unit=unit)
        return render(request, 'teacher_app/submission.html', {'unit': unit, 'submissions': submissions})


class SetGradeView(View):
    def get(self, request, submission_id):
        submission = AssignmentSubmission.objects.get(pk=submission_id)
        return render(request, 'teacher_app/set_grade.html', {'submission': submission})

    def post(self, request, submission_id):
        submission = AssignmentSubmission.objects.get(pk=submission_id)
        grade = request.POST.get('grade')
        max_grade = submission.assignment.max_grade

        try:
            grade = float(grade)
            if grade > max_grade:
                messages.error(request, "The grade cannot exceed the maximum allowed grade.")
                return redirect('set_grade', submission_id=submission_id)  # Stay on the set grade page
            else:
                if submission.grade:
                    submission.grade = grade
                else:
                    submission.grade = grade

                submission.save()
                return redirect('submissions', unit_id=submission.assignment.unit_id)  # Return to submissions page
        except ValueError:
            messages.error(request, "Invalid grade value.")
            return redirect('set_grade', submission_id=submission_id)
