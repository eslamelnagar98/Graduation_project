from . import views
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as authviews

# rest = routers.DefaultRouter()
# rest.register('register', views.CreateUserView)


urlpatterns = [
    # path('', include(rest.urls)),
    url(r'^register/$', views.Register.as_view(), name='register'),
    # /api/v1/rest-auth/password/change/     Change password
    # /api/v1/rest-auth/login/                 login
    # /api/v1/rest-auth/logout/                logout
    # path('api-token-auth/', views.LoginView.as_view(), name='api-token-auth'),
    # path('api-token-auth/logout', views.LogoutView.as_view(), name='api-token-auth'),
    # path('api/v1/auth/login/',views.LoginView.as_view()),
    # path('api/v1/auth/logout/',views.LogoutView.as_view()),
    # path('api-token-auth/', authviews.obtain_auth_token, name='api-token-auth'),
    path('accept/<doctor_id>/<patient_id>/', views.accept_request.as_view(), name='accept'),
    path('new/<doctor_id>/<patient_id>/', views.accept_request_2.as_view(), name='acceptt'),
    path('accepttt/<patient_id>/', views.accept_request_3.as_view(), name='accepttt'),
    path('retrieve/<doctor_id>/', views.retrieve_doctor.as_view(), name='retrieve'),
    path('search/', views.send_request.as_view(), name='search'),
    path('add_request/', views.add_request.as_view(), name='add_request'),
    path('cancel_request/<pk>/', views.cancel_request.as_view(), name='cancel_request'),
    path('add_record/', views.recieve_records.as_view(), name='add_records'),
    path('comments/<patient_id>/', views.recieve_doctor_comment.as_view(), name='comments'),
    path('heartbeat/<patient_id>/', views.recieve_heart_beat.as_view(), name='heartbeat'),
    url(r'^(?P<slug>[\w-]+)/$', views.retrieve_user.as_view(), name='retrieve'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.update_user.as_view(), name='update'),
]
