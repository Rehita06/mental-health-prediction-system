# inference/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('predict/<int:assessment_id>/', views.PredictAssessmentView.as_view(), name="predict_assessment"),
    path('assessment/create/', views.AssessmentCreateView.as_view(), name="create_assessment"),
    path('results/', views.UserResultsView.as_view(), name="user_results"),
    path('', views.demo_page, name='demo'),

    path('health/', views.health, name="health"),
    path('results/', views.UserResultsView.as_view(), name="user_results"),
    path('dashboard/', views.admin_dashboard, name="admin_dashboard"),
    # new auth urls
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
