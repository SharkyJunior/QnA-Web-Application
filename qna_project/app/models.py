from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')
    
    def recent(self):
        return self.get_queryset().order_by('-created_at')
    
    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name)
    
    def most_upvoted(self):
        return (
            self.get_queryset()
            .annotate(
                total_votes=Coalesce(
                    Sum('votes__value'),
                    Value(0)
                )
            )
            .order_by('-total_votes', '-created_at')
        )
        
class TagManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')
    
    def most_popular(self):
        return self.get_queryset().annotate(total_questions=Count('question')).order_by('-total_questions')
    
class ProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('user__username')
    
    def most_active(self):
        return self.get_queryset().annotate(total_questions=Count('question')).order_by('-total_questions')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    nickname = models.CharField(default='unnamed user', max_length=32)
    
    avatar_url = models.URLField(blank=True, null=True)
    avatar_image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    
    objects = ProfileManager()
    
    @property
    def avatar(self):
        """
        Returns the final URL to use in templates.
        Priority:
        1) local image if uploaded
        2) external URL if provided
        3) default placeholder
        """
        if self.avatar_image:
            return self.avatar_image.url
        if self.avatar_url:
            return self.avatar_url
        return '../static/img/avatar_default.svg'
    
    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(null=True,auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    
    objects = TagManager()
    
    def __str__(self):
        return self.name
    
class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)
    
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    
    objects = QuestionManager()
    
    def vote_sum(self):
        result = self.votes.aggregate(total=Sum('value'))['total']
        return result or 0
    
    def answer_count(self):
        return self.answers.count()
    
    def __str__(self):
        return self.title
    
class QuestionVote(models.Model):
    question = models.ForeignKey(Question, related_name='votes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('question', 'profile')
    
    def __str__(self) -> str:
        return f"{'👍' if self.value == 1 else '👎'} {self.profile} → {self.question.title}"
     
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def vote_sum(self):
        result = self.votes.aggregate(total=Sum('value'))['total']
        return result or 0
    
    def __str__(self):
        return self.text[:50] + '...'
    
class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer, related_name='votes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('answer', 'profile')
    
    def __str__(self) -> str:
        return f"{'👍' if self.value == 1 else '👎'} {self.profile} → {self.answer.text[:50]}..."

