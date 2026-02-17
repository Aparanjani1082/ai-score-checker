from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('guest/', views.guest_login, name='guest'),
    path('home/', views.home, name='home'),
    path('answer/', views.answer_page, name='answer_page'),  
    path("history/", views.history, name="history"), 
    path("history/clear/", views.clear_history, name="clear_history"),
    path('check-score/', views.check_score, name='check_score'),
    path('logout/', views.logout_view, name='logout'),
]

