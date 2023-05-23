from django.urls import path
from . import views


urlpatterns = [
    path('',views.login, name='login'),
    path('about',views.about, name='about'),
    path('signup',views.signup,name='signup'),
    path('result',views.result,name='result')
]

