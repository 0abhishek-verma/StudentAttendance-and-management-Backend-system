import csv
from django.http import HttpResponse



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
# Create your views here.
class CustomUserRegisterView(APIView):
    def get(self,request):
        user = CustomUser.objects.all()
        serializer = CustomUserSerializer(user, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        if data.get('role').lower() == 'admin':
            data['is_staff'] = True
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            return Response({'message':'User Created Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User Updated Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        user.delete()
        return Response({'message': 'User Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)

class CustomUserLoginView(APIView):
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
class CustomUserLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
class StudentProfileView(APIView):
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]  # Any logged-in user can GET
        return [IsAdminUser()]  # Only admin can POST


    def get(self, request):
        students = StudentProfile.objects.all()
        serializer = StudentProfileSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data.copy()
        user_id = data.get('user')
        user = get_object_or_404(CustomUser, id=user_id)
        if user.role.lower() == 'admin':
            return Response({'error': 'admin cannot be created in student profiles'}, status=status.HTTP_403_FORBIDDEN)
        serializers = StudentProfileSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message': 'User Created Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskView(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]  # Any logged-in user can GET
        return [IsAdminUser()]  # Only admin can POST

    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Task Created Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Task Updated Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        task.delete()
        return Response({'message': 'Task Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)

class MyTaskView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role.lower() != 'student':
            return Response({'error': 'Only Student can view tasks'}, status=status.HTTP_403_FORBIDDEN)
        try:
            student = user.studentprofile
        except StudentProfile.DoesNotExist:
            return Response({'error': 'User is not a student'}, status=status.HTTP_400_BAD_REQUEST)
        task = student.task.all().order_by('-due_date')
        serializer = TaskSerializer(task, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TaskAssignedToStudentView(APIView):  
    permission_classes = [IsAdminUser]
    
    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        student_ids = request.data.get('assigned_to', [])
        students = StudentProfile.objects.filter(id__in=student_ids)
        
        if not students.exists():
            return Response({'error': 'No valid students provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.assigned_to.set(students)
        task.save()
        return Response({'message': 'Task assigned to students successfully'}, status=status.HTTP_200_OK)

class SubmitTaskView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # for file uploads

    def post(self, request, task_id):
        user = request.user
        if user.role.lower() != 'student':
            return Response({'error': 'Only students can submit tasks.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            student = user.studentprofile
        except StudentProfile.DoesNotExist:
            return Response({'error': 'Student profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, pk=task_id)

        # Prevent duplicate submission
        if TaskSubmission.objects.filter(task=task, student=student).exists():
            return Response({'error': 'You have already submitted this task.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract file and comment
        file = request.FILES.get('file')
        comment = request.data.get('comment', '')

        submission = TaskSubmission.objects.create(
            task=task,
            student=student,
            file=file,
            comment=comment
        )

        serializer = TaskSubmissionSerializer(submission)
        return Response({'message': 'Task submitted successfully.', 'submission': serializer.data}, status=status.HTTP_201_CREATED)
    
   

class ReviewSubmissionView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAdminUser]

    def post(self, request, id):
        submission = get_object_or_404(TaskSubmission, pk=id)
        feedback = request.data.get('feedback')
        status_value = request.data.get('status')

        if status_value not in dict(TaskSubmission.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        submission.feedback = feedback
        submission.status = status_value
        submission.save()

        return Response({'message': 'Submission reviewed successfully'}, status=status.HTTP_200_OK)

class MyAttendanceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = Attendance.objects.filter(student__user=request.user).order_by('-date')
        serializers = AttendanceSerializer(student, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
class MarkAttendanceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role.lower() != 'student':
            return Response({'error': 'Only Student can mark attendance'}, status=status.HTTP_403_FORBIDDEN)
        try:
            student = user.studentprofile
        except StudentProfile.DoesNotExist:
            return Response({'error': 'User is not a student'}, status=status.HTTP_400_BAD_REQUEST)
        date = request.data.get('date')
        if not date:
            return Response({'error': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Attendance.objects.filter(student=student, date=date).exists():
            return Response({'error': 'Attendance for this student on this date already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializers_data = AttendanceSerializer(data={'student': student.id, 'date': date, 'status': 'present'})
        if serializers_data.is_valid():
            serializers_data.save()
            return Response({'message': 'Attendance marked successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializers_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        attendance = Attendance.objects.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
class AttendanceView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        if request.user.role.lower() != 'admin':
            return Response({'error': 'Only Admin can view attendance'}, status=status.HTTP_403_FORBIDDEN)
        attendance = Attendance.objects.all().order_by('-date')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

        writer = csv.writer(response)
        
        # Header row (adjust as per your Attendance model)
        writer.writerow(['ID', 'Student Name', 'Date', 'Status'])

        # Data rows
        for record in attendance:
            writer.writerow([
                record.id,
                record.student.user.get_full_name(),  # adjust if different
                record.date.strftime('%Y-%m-%d'),
                record.status
            ])

        return response
    
    
    def post(self, request):
        user = request.user
        student = request.data.get('student')
        date = request.data.get('date')
        if not student.objects.filter(id=student).exists():
            return Response({'error': 'Student does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        if not date:
            return Response({'error': 'Date is required'}, status=status.HTTP_400_BAD_REQUEST)
        if Attendance.objects.filter(student=student, date=date).exists():
            return Response({'error': 'Attendance for this student on this date already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AttendanceSerializer(data={'student': student, 'date': date, 'status': 'present'})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Attendance marked successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    