from django.core.management.base import BaseCommand
from django.core.cache import cache

from app.models import Tag, Profile, Question


class Command(BaseCommand):
    def handle(self, *args, **options):
        tags = Tag.objects.get_top()
        cache.set('tags', tags, 600)

        hot_question = Question.objects.get_hot(calculate=True)
        cache.set('hot_questions', hot_question, 600)

        members = Profile.objects.get_top()
        cache.set('members', members, 600)
