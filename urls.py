from django.urls import path, reverse_lazy
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MyPasswordChangeForm

urlpatterns = [
    path('', views.home, name="t_home"),
    path('profile/', views.ProfileView.as_view(), name="t_profile"),
    path('registration/', views.RegistrationView.as_view(), name="t_registration"),
    path('activate/<str:uidb64>/<str:token>/', views.AccountActivationView.as_view(), name='t_activate'),
    path('login/', views.TeacherLoginView.as_view(template_name='teacher_app/login.html', authentication_form=LoginForm), name='t_login'),
    path('email-confirmed', views.email_confirmed_view, name='t_email_confirmed'),
    path('forgot_password/', views.CustomPasswordResetView.as_view(), name='t_forgot_password'),
    path('reset_password/<str:uidb64>/<str:token>/', views.CustomPasswordResetConfirmView.as_view(), name='t_reset_password'),
    path('logout/', auth_views.LogoutView.as_view(next_page='t_login'), name='t_logout'),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='teacher_app/changepassword.html', form_class=MyPasswordChangeForm, success_url='/teacher/passwordchangedone/'), name = 't_passwordchange'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='teacher_app/passwordchangedone.html'), name='t_passwordchangedone'),
    path('calendar/', views.CalendarView.as_view(), name='t_calendar'),
    path('teaching/', views.TeachingView.as_view(), name='teaching'),
    path('access_denied/', views.DeniedView.as_view(), name='t_access_denied'),
    path('create-course/', views.create_course, name='create_course'),
    path('course-structure/<int:pk>', views.CourseStructureView.as_view(), name='course_structure'),
    path('enroll-student/<int:pk>', views.CourseStructureView.as_view(), name='enroll_student'),
    path('unenroll-student/<int:pk>', views.CourseStructureView.as_view(), name='unenroll_student'),
    path('add-module/<int:course_id>/', views.add_module, name='add_module'),
    path('delete-course/<int:pk>/', views.delete_course, name='delete_course'),
    path('edit-course/<int:pk>/', views.edit_course, name='edit_course'),
    path('edit-module/<int:module_id>/', views.edit_module, name='edit_module'),
    path('delete-module/<int:module_id>/', views.delete_module, name='delete_module'),
    path('add-topic/<int:module_id>/', views.add_topic, name='add_topic'),
    path('edit-topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('course/<int:course_pk>/topic/<int:pk>/', views.TopicStructureView.as_view(), name='topic_structure'),
    path('add-unit/<int:topic_id>/', views.add_unit, name='add_unit'),
    path('delete-unit/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    path('edit-unit/<int:unit_id>/', views.edit_unit, name='edit_unit'),
    path('unit/<int:unit_id>/upload-file/', views.upload_file, name='upload_file'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('submissions/<int:unit_id>/', views.AssignmentSubmissionView.as_view(), name='submissions'),
    path('submissions/set_grade/<int:submission_id>/', views.SetGradeView.as_view(), name='set_grade')


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

LOGIN_REDIRECT_URL = reverse_lazy('t_calendar')