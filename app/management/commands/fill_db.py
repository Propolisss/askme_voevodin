import time
import random
from itertools import product

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from app.models import Profile, Tag, Question, Answer, AnswerLike, QuestionLike
from faker import Faker
from django.core.files import File

from app.views import question
from askme_voevodin.settings import BASE_DIR


def custom_boolean(true_probability=0.5):
    return random.random() < true_probability


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options.get('ratio', 1)
        fake = Faker()
        image_path = BASE_DIR / 'static/img/200img.png'
        total_time = 0

        self.stdout.write(self.style.WARNING(f'Started filling db...'))

        start_time = time.time()

        self.create_users(fake, ratio, image_path)
        delta = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Users created in {delta:.2f} seconds'))
        total_time += delta
        start_time = time.time()

        self.create_tags(fake, ratio)
        delta = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Tags created in {delta:.2f} seconds'))
        total_time += delta
        start_time = time.time()

        self.create_questions(fake, ratio)
        delta = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Questions created in {delta:.2f} seconds'))
        total_time += delta
        start_time = time.time()

        self.create_answers(fake, ratio)
        delta = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Answers created in {delta:.2f} seconds'))
        total_time += delta
        start_time = time.time()

        self.create_likes(fake, ratio)
        delta = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Likes created in {delta:.2f} seconds'))
        total_time += delta

        self.stdout.write(self.style.SUCCESS(f'Total time: {total_time:.2f} seconds'))

        self.stdout.write(self.style.WARNING(f'DB successfully filled!...'))

    def create_users(self, fake, ratio, image_path):
        self.stdout.write(self.style.WARNING(f'Creating users...'))

        users = []
        profiles = []
        usernames = set()

        for _ in range(ratio):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()

            while username in usernames:
                username = fake.user_name()

            usernames.add(username)

            user = User(username=username, email=email)
            user.set_password(password)
            users.append(user)

            profiles.append(Profile(user=user))

        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)

        for profile in profiles:
            with open(image_path, 'rb') as f:
                profile.avatar.save('200img.jpg', File(f), save=True)

        self.stdout.write(self.style.SUCCESS(f'Users have been created successfully!'))

    def create_tags(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating tags...'))

        tags = []
        unique_tags = set()

        for _ in range(ratio):
            tag = fake.word()

            while tag in unique_tags:
                tag = fake.word()
            tags.append(Tag(name=tag))
            unique_tags.add(tag)

        Tag.objects.bulk_create(tags)
        self.stdout.write(self.style.SUCCESS(f'Tags have been created successfully!'))

        return Tag.objects.all()

    def create_questions(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating questions...'))

        profiles = list(Profile.objects.all().values_list('id', flat=True))
        tags = list(Tag.objects.all().values_list('id', flat=True))

        questions = [
            Question(profile_id=fake.random_element(elements=profiles),
                     title=fake.sentence(nb_words=10),
                     text=fake.text(max_nb_chars=500)) for _ in range(ratio * 10)
        ]

        Question.objects.bulk_create(questions)

        question_tag_links = [
            Question.tags.through(question_id=question.id, tag_id=tag_id)
            for question in questions for tag_id in
            fake.random_elements(elements=tags, unique=True,
                                 length=fake.random_int(min=1, max=min(5, len(tags))))
        ]

        Question.tags.through.objects.bulk_create(question_tag_links)

        self.stdout.write(self.style.SUCCESS(f'Questions have been created successfully!'))

    def create_answers(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating Answers...'))

        questions = list(Question.objects.all().values_list('id', flat=True))
        profiles = list(Profile.objects.all().values_list('id', flat=True))

        answers = [Answer(question_id=fake.random_element(elements=questions),
                          profile_id=fake.random_element(elements=profiles),
                          text=fake.text(max_nb_chars=500),
                          correct=fake.boolean()) for _ in range(ratio * 100)]

        Answer.objects.bulk_create(answers)

        self.stdout.write(self.style.SUCCESS(f'Answers have been created successfully!'))

    def create_likes(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating likes...'))

        answers = list(Answer.objects.all().values_list('id', flat=True))
        questions = list(Question.objects.all().values_list('id', flat=True))
        profiles = list(Profile.objects.all().values_list('id', flat=True))
        # unique_answers = set()
        # answers_likes = []
        # unique_questions = set()
        # question_likes = []
        #
        # for _ in range(ratio * 100):
        #     answer = Answer.objects.get(id=fake.random_element(elements=answers))
        #     profile = Profile.objects.get(id=fake.random_element(elements=profiles))
        #     is_liked = fake.boolean()
        #     while (profile, answer) in unique_answers:
        #         answer = Answer.objects.get(id=fake.random_element(elements=answers))
        #         profile = Profile.objects.get(id=fake.random_element(elements=profiles))
        #     unique_answers.add((profile, answer))
        #     answers_likes.append(AnswerLike(profile=profile, answer=answer, is_liked=is_liked))
        # AnswerLike.objects.bulk_create(answers_likes)
        #
        # for _ in range(ratio * 100):
        #     question = Question.objects.get(id=fake.random_element(elements=questions))
        #     profile = Profile.objects.get(id=fake.random_element(elements=profiles))
        #     is_liked = fake.boolean()
        #     while (profile, question) in unique_questions:
        #         question = Question.objects.get(id=fake.random_element(elements=questions))
        #         profile = Profile.objects.get(id=fake.random_element(elements=profiles))
        #     unique_questions.add((profile, question))
        #     question_likes.append(QuestionLike(profile=profile, question=question, is_liked=is_liked))
        # QuestionLike.objects.bulk_create(question_likes)

        # count_answer_likes = 0
        # answers_likes = []
        # flag = False
        # for i, answer_id in enumerate(answers):
        #     for j, profile_id in enumerate(profiles):
        #         answers_likes.append(
        #             AnswerLike(profile=Profile.objects.get(id=profile_id), answer=Answer.objects.get(id=answer_id),
        #                        is_liked=custom_boolean(0.2)))
        #         count_answer_likes += 1
        #         if count_answer_likes >= ratio * 200:
        #             flag = True
        #             break
        #     if flag:
        #         break
        # AnswerLike.objects.bulk_create(answers_likes)
        #
        # count_question_likes = 0
        # question_likes = []
        # flag = False
        # for i, question_id in enumerate(questions):
        #     for j, profile_id in enumerate(profiles):
        #         question_likes.append(
        #             QuestionLike(profile=Profile.objects.get(id=profile_id),
        #                          question=Question.objects.get(id=question_id),
        #                          is_liked=custom_boolean(0.2)))
        #         count_question_likes += 1
        #         if count_question_likes >= ratio * 200:
        #             flag = True
        #             break
        #     if flag:
        #         break
        # QuestionLike.objects.bulk_create(question_likes)

        answer_pairs = list(product(profiles, answers))
        random.shuffle(answer_pairs)
        answer_pairs = answer_pairs[:ratio * 200]

        answer_likes = [
            AnswerLike(profile_id=profile_id, answer_id=answer_id, is_liked=custom_boolean(0.2))
            for profile_id, answer_id in answer_pairs
        ]

        question_pairs = list(product(profiles, questions))
        random.shuffle(question_pairs)
        question_pairs = question_pairs[:ratio * 200]

        question_likes = [
            QuestionLike(profile_id=profile_id, question_id=question_id, is_liked=custom_boolean(0.2))
            for profile_id, question_id in question_pairs
        ]

        AnswerLike.objects.bulk_create(answer_likes)
        QuestionLike.objects.bulk_create(question_likes)

        self.stdout.write(self.style.SUCCESS(f'Likes have been created successfully!'))
