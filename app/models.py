from django.contrib.auth.models import User
from django.db import models

# Create your models here.

from django.db import models
from django.db.models import Q, Count, F


class QuestionManager(models.Manager):
    def get_hot(self):
        self.prefetch_related('answers', 'likes')
        return self.annotate(
            rating=Count('likes', filter=Q(likes__is_liked=True), distinct=True) -
                   Count('likes', filter=Q(likes__is_liked=False), distinct=True),
            answer_count=Count('answers', distinct=True)
        ).order_by('-rating', '-answer_count')

    def get_new(self):
        return self.order_by('-created_at')

    def get_answers_by_id(self, id):
        return self.get(id=id).answers.sort_answers()


class AnswerManager(models.Manager):
    def sort_answers(self):
        return self.annotate(
            like_count=Count('likes', filter=Q(likes__is_liked=True)) -
                       Count('likes', filter=Q(likes__is_liked=False))
        ).order_by('-correct', '-like_count')


class ProfileManager(models.Manager):
    def get_top(self):
        # return self.annotate(
        #     rating=Count('questions__likes', filter=Q(questions__likes__is_liked=True)) +
        #            Count('answers__likes', filter=Q(answers__likes__is_liked=True))
        # ).order_by('-rating')[:10]
        return self.all()[:10]


class TagManager(models.Manager):
    def get_top(self):
        return self.annotate(
            rating=Count('questions')
        ).order_by('-rating')[:10]

    def get_questions_by_tag(self, name):
        return self.get(name=name).questions.all()


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

    objects = AnswerManager()


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
