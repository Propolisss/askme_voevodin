from django.contrib.auth.models import User
from django.db import models

# Create your models here.

from django.db import models
from django.db.models import Q, Count, F


class QuestionManager(models.Manager):
    def get_hot(self):
        return self.annotate(
            rating=Count('likes', filter=Q(likes__is_liked=True)) -
                   Count('likes', filter=Q(likes__is_liked=False))
        ).order_by('-rating')

    def get_new(self):
        return self.order_by('-created_at')


class ProfileManager(models.Manager):
    def get_top(self):
        return self.annotate(
            rating=Count('question_likes', filter=Q(question_likes__is_liked=True)) -
                   Count('answer_likes', filter=Q(answer_likes__is_liked=True))
        ).order_by('-rating')[:10]


class TagManager(models.Manager):
    def get_top(self):
        return self.annotate(
            rating=Count('questions')
        ).order_by('-rating')[:10]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')

    def __str__(self):
        return self.user.username

    objects = ProfileManager()


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    objects = TagManager()


class Question(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_rating(self):
        likes = self.likes.filter(is_liked=True).count()
        dislikes = self.likes.filter(is_liked=False).count()
        return likes - dislikes


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer to {self.question.title}"

    def get_rating(self):
        likes = self.likes.filter(is_liked=True).count()
        dislikes = self.likes.filter(is_liked=False).count()
        return likes - dislikes


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='question_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('profile', 'question')


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='answer_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_liked = models.BooleanField(default=True)

    class Meta:
        unique_together = ('profile', 'answer')