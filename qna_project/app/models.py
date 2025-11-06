from django.contrib.auth.models import User
from django.db import models

class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')
    
    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    
    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    
    def __str__(self):
        return self.name
    
class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    tag = models.ManyToManyField(Tag, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = QuestionManager()
    
    def __str__(self):
        return self.title
     
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False, null=True)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.text[:50]
