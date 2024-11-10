import os
import shutil

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.apps import apps

from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from askme_voevodin.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        models_to_delete = [Profile, Tag, Question, Answer, QuestionLike, AnswerLike, User]

        for model in models_to_delete:
            self.stdout.write(self.style.WARNING(f'Deleting all objects from {model.__name__}'))
            model.objects.all().delete()

        media_root = BASE_DIR / 'uploads' / 'avatars'
        shutil.rmtree(media_root)
        os.makedirs(media_root)
