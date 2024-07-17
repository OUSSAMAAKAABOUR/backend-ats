from django.db import models

class Post(models.Model):
    recruiter = models.ForeignKey('authentication.Recruiter', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.JSONField()  
    deadline = models.DateField()
    image = models.CharField(max_length=100,blank=True)
    mode = models.CharField(max_length=100,blank=True)
    localisation = models.CharField(max_length=100,blank=True, null=True)
    number_of_people_to_hire=models.CharField(max_length=100,blank=True, null=True)
    salary=models.FloatField(max_length=100,blank=True, null=True)
    def str(self):
        return self.title