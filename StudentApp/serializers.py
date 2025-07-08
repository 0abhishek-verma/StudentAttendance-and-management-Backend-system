from rest_framework import serializers
from .models import *

# write your serializers here

class CustomUserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(write_only=True, required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role','is_staff']
    
class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    user_details = CustomUserSerializer(source='user', read_only=True)
    class Meta:
        model = StudentProfile
        fields = ['id', 'user_details','user', 'roll_no', 'course', 'batch']
        
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=StudentProfile.objects.all(),
        write_only=True  
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'assigned_to', 'created_by']
        read_only_fields = ['created_by']
        
        
class TaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSubmission
        fields = '__all__'
        read_only_fields = ['status', 'submitted_at'] 
        
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Attendance
        fields='__all__'         