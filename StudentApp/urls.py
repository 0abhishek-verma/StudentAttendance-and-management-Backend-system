from django.urls import path
from .views import *
urlpatterns = [
    #Authentication
    path('register/', CustomUserRegisterView.as_view(), name='register'),
    path('login/',CustomUserLoginView.as_view(), name='login'),
    path('logout/', CustomUserLogoutView.as_view(), name='logout'),
    
    #Admin APIs
    path('student/', StudentProfileView.as_view(), name='profile'),
    path('task/', TaskView.as_view(), name='task'),
    path('task-submission/', TaskAssignedToStudentView.as_view(), name='tasksubmission'),
    path('task-submissions/<int:id>/review/', ReviewSubmissionView.as_view(), name='reviewtasksubmission'),
    path('attendance/record/', AttendanceView.as_view(), name='attendance'),

    
    #Student APIs
    path('my-tasks/',MyTaskView.as_view(), name='mytasks'),
    path('submit-task/<int:task_id>/', SubmitTaskView.as_view(), name='submittask'),
    path('attendance/mark/',MarkAttendanceView.as_view(), name='markattendance'),
    path('attendance/me/', MyAttendanceView.as_view(), name='myattendance'),

]
