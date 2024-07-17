from django.db import models
from django.contrib.auth.models import AbstractUser
from posts.models import Post
from django.conf import settings
import os

class User(AbstractUser):
    MEMBERSHIP_CHOICES=[
        ('c','candidate'),
        ('r','recruiter'),
        ('a','admin'),
    ]
    GENDER_CHOICES=[
        ('f','female'),
        ('m','male'),
    ]
    is_active=models.BooleanField(default=False)
    email= models.EmailField(unique=True)
    role= models.CharField(max_length=1, choices= MEMBERSHIP_CHOICES, default='c')
    gender=models.CharField(max_length=1, choices= GENDER_CHOICES)
    in_call=models.BooleanField(default=False)


class Candidate(User):
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='candidate_img', blank=True, null=True)

    def save(self, *args, **kwargs):
        self.role = 'c'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or "Candidate"


class Recruiter(User):
    company = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)


    image = models.CharField(max_length=200, blank=True, null=True)
    comp_industry=models.CharField(max_length=100, blank=True, null=True)
    comp_description=models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.role = 'r'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or "Recruiter"


# class Application(models.Model):
#     STATUS_CHOICES = [
#         ('p', 'Pending'),
#         ('a', 'Accepted'),
#         ('r', 'Rejected'),
#     ]
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='applications')
#     candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='p')
#     resume = models.FileField(upload_to='resumes/', null=True, blank=True)
#     cover_letter = models.FileField(upload_to='cover_letters/', null=True, blank=True)
#     date = models.DateTimeField(auto_now_add=True)
#     score_matching = models.IntegerField(default=0)

#     def __str__(self):
#         return f"Application by {self.candidate} for {self.post}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('p', 'Pending'),
        ('a', 'Accepted'),
        ('r', 'Rejected'),
    ]
    step = models.CharField(max_length=20, default='Application Review')

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='p')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_path = models.CharField(max_length=255, null=True, blank=True)
    cover_letter = models.FileField(upload_to='cover_letters/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    score_matching = models.IntegerField(default=0)

    def _str_(self):
        return f"Application by {self.candidate} for {self.post}"

    def get_resume_path(self):
        if self.resume_path:
            # Convert relative path to absolute path
            return os.path.join(settings.MEDIA_ROOT, self.resume_path)
        elif self.resume:
            return self.resume.path
        return None
class CustomToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    expiration_date = models.DateTimeField()


class Event(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    event_title= models.CharField(max_length=200)
    event_start_date= models.DateTimeField()
    # event_end_date= models.DateTimeField()

# Saved posts class models.py file, authentification app
class SavedPost(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

# chatt
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    file_data = models.TextField(blank=True, null=True)
    
    
class Clients(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=255, unique=True)

    def _str_(self):
        return f"{self.user.username} - {self.channel_name}"

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('available', 'Available'), ('busy', 'Busy')], default='available')

    def _str_(self):
        return f"{self.user.username} - {self.status}"
