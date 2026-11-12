
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('COLLEGE_ADMIN', 'College Admin'),
        ('SUPER_ADMIN', 'AptiPro Admin'),
    ]

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='STUDENT'
    )

    def __str__(self):
        return f"{self.username} - {self.role}"
class Role(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    FACULTY = "FACULTY", "Faculty"
    COLLEGE_ADMIN = "COLLEGE_ADMIN", "College Admin"