import time
import random
from itertools import product

from django.contrib.auth.hashers import make_password
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
        image_path = BASE_DIR / 'static/img'
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
        users = [
            User(username=fake.unique.user_name(), email=fake.email(),
                 password=make_password(fake.password()))
            for _ in range(ratio)
        ]
        profiles = [
            Profile(user=user) for user in users
        ]

        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)

        for profile in Profile.objects.all():
            with open(image_path / f'img_{random.randint(0, 19)}.png', 'rb') as f:
                profile.avatar.save(f'{profile.user.username}_avatar.png', File(f), save=True)

        self.stdout.write(self.style.SUCCESS(f'Users have been created successfully!'))

    def create_tags(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating tags...'))

        base_tags = [fake.unique.word() for _ in range(int(ratio ** 0.5) + 1)]
        tag_pairs = [f"{tag1}_{tag2}" for tag1, tag2 in list(product(base_tags, repeat=2))]
        tags = base_tags + tag_pairs
        random.shuffle(tags)
        tags = tags[:ratio]

        tags = [Tag(name=tag) for tag in tags]
        Tag.objects.bulk_create(tags)

        self.stdout.write(self.style.SUCCESS(f'Tags have been created successfully!'))

    def create_questions(self, fake, ratio):
        self.stdout.write(self.style.WARNING(f'Creating questions...'))

        profiles = list(Profile.objects.all().values_list('id', flat=True))
        tags = list(Tag.objects.all().values_list('id', flat=True))

        for i in range(10):
            questions = [
                Question(profile_id=fake.random_element(elements=profiles),
                         title=fake.sentence(nb_words=10),
                         text=fake.text(max_nb_chars=500)) for _ in range(ratio)
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

        for i in range(100):
            answers = [Answer(question_id=fake.random_element(elements=questions),
                              profile_id=fake.random_element(elements=profiles),
                              text=fake.text(max_nb_chars=500),
                              correct=fake.boolean()) for _ in range(ratio)]

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

        # answer_pairs = list(product(profiles, answers))
        # random.shuffle(answer_pairs)
        # answer_pairs = answer_pairs[:ratio * 200]
        #
        # answer_likes = [
        #     AnswerLike(profile_id=profile_id, answer_id=answer_id, is_liked=custom_boolean(random.random()))
        #     for profile_id, answer_id in answer_pairs
        # ]
        # answer_likes.clear()
        #
        # question_pairs = list(product(profiles, questions))
        # random.shuffle(question_pairs)
        # question_pairs = question_pairs[:ratio * 200]
        #
        # question_likes = [
        #     QuestionLike(profile_id=profile_id, question_id=question_id, is_liked=custom_boolean(random.random()))
        #     for profile_id, question_id in question_pairs
        # ]
        answer_likes = []
        question_likes = []

        for profile in profiles:
            answer_likes += [
                AnswerLike(answer_id=answer, profile_id=profile, is_liked=custom_boolean(random.random()))
                for answer in fake.random_elements(elements=answers, length=200, unique=True)
            ]
            if len(answer_likes) >= ratio:
                AnswerLike.objects.bulk_create(answer_likes)
                answer_likes.clear()
        if len(answer_likes):
            AnswerLike.objects.bulk_create(answer_likes)

        for profile in profiles:
            question_likes += [
                QuestionLike(question_id=question, profile_id=profile, is_liked=custom_boolean(random.random()))
                for question in fake.random_elements(elements=questions, length=200, unique=True)
            ]
            if len(question_likes) >= ratio:
                QuestionLike.objects.bulk_create(question_likes)
                question_likes.clear()
        if len(question_likes):
            QuestionLike.objects.bulk_create(question_likes)

        self.stdout.write(self.style.SUCCESS(f'Likes have been created successfully!'))
