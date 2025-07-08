from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    def __str__(self):
        return self.username
    
class StudentProfile(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,limit_choices_to={'role': 'student'},related_name='studentprofile')
    roll_no=models.CharField(max_length=20,unique=True)
    course=models.CharField(max_length=50)
    batch=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} | {self.course}"

class Task(models.Model):
    title=models.CharField(max_length=100)
    description =models.TextField()
    due_date=models.DateField()
    created_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE,limit_choices_to={'role':'admin'})
    assigned_to=models.ManyToManyField(StudentProfile,related_name='task')
    
    def __str__(self):
        return self.title

class TaskSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('rejected', 'Rejected'),
    )

    task = models.ForeignKey(Task,on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE, related_name='submissions')
    comment = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} | {self.task.title}"
    

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
