from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('about_us/', views.about_us, name='about_us'),
    path('subcribe/', views.subscribe, name='subcribe'),
    path('sign-up/', views.SignUp.as_view(), name='signup'),
    path('sign-in/', views.LoginView.as_view(), name='sign-in'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('updateprofile/', views.update_profile, name='updateprofile'),
    path('requests/', views.get_requests, name='requests'),
    path('accept/', views.accept_button, name='accept'),
    path('reject/', views.reject_button, name='reject'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
         name='password_change'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
         name="reset_password"),
    path('password-reset-sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"),
         name="password_reset_confirm"),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"),
         name="password_reset_complete"),
    path('patient/', views.patientsearch, name='patient'),
    # path('<slug>/', views.patient_detail, name='patient_detail'),
    path('<slug>/', views.patient_pulse_detail, name='patient_pulse_detail'),
    path('patient/<slug>/', views.patient_detail, name='patient_detail'),
]
