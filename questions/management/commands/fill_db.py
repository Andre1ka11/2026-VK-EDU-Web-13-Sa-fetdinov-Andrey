import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker('ru_RU')  # русскоязычные данные

class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Множитель для количества сущностей')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f'Начинаем наполнение БД с ratio={ratio}')

        # 1. Пользователи (≈ ratio)
        users_count = ratio
        users = []
        for i in range(users_count):
            username = fake.unique.user_name()
            email = fake.email()
            user = User(username=username, email=email)
            user.set_password('password123')
            users.append(user)
        User.objects.bulk_create(users, ignore_conflicts=True)
        # Получаем всех пользователей (включая существующих)
        all_users = list(User.objects.all())
        self.stdout.write(f'Создано/найдено пользователей: {len(all_users)}')

        # 2. Теги (≈ ratio)
        tags_count = ratio
        tags = []
        for i in range(tags_count):
            tag = Tag(name=fake.unique.word())
            tags.append(tag)
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        all_tags = list(Tag.objects.all())
        self.stdout.write(f'Создано/найдено тегов: {len(all_tags)}')

        # 3. Вопросы (≈ ratio * 10)
        questions_count = ratio * 10
        questions = []
        for i in range(questions_count):
            author = random.choice(all_users)
            title = fake.sentence(nb_words=8)
            text = fake.paragraph(nb_sentences=5)
            q = Question(author=author, title=title, text=text)
            questions.append(q)
        # bulk_create не возвращает id, поэтому после сохранения обновим списки
        Question.objects.bulk_create(questions)
        all_questions = list(Question.objects.all())
        # Добавляем теги к вопросам (ManyToMany – нужно добавлять через промежуточную таблицу)
        # Это можно сделать после создания вопросов
        for q in all_questions:
            random_tags = random.sample(all_tags, k=random.randint(1, 5))
            q.tags.add(*random_tags)
        self.stdout.write(f'Создано вопросов: {len(all_questions)}')

        # 4. Ответы (≈ ratio * 100)
        answers_count = ratio * 100
        answers = []
        for i in range(answers_count):
            author = random.choice(all_users)
            question = random.choice(all_questions)
            text = fake.paragraph(nb_sentences=3)
            answer = Answer(author=author, question=question, text=text)
            answers.append(answer)
        Answer.objects.bulk_create(answers)
        all_answers = list(Answer.objects.all())
        self.stdout.write(f'Создано ответов: {len(all_answers)}')

        # 5. Лайки вопросов (≈ ratio * 100) – чтобы общее количество лайков было ratio*200
        question_likes_count = ratio * 100
        q_likes = []
        existing_pairs = set()
        for i in range(question_likes_count):
            user = random.choice(all_users)
            question = random.choice(all_questions)
            # уникальность user+question
            if (user.id, question.id) in existing_pairs:
                continue
            existing_pairs.add((user.id, question.id))
            q_likes.append(QuestionLike(user=user, question=question))
        QuestionLike.objects.bulk_create(q_likes, ignore_conflicts=True)
        self.stdout.write(f'Создано лайков вопросов: {len(q_likes)}')

        # 6. Лайки ответов (≈ ratio * 100)
        answer_likes_count = ratio * 100
        a_likes = []
        existing_pairs = set()
        for i in range(answer_likes_count):
            user = random.choice(all_users)
            answer = random.choice(all_answers)
            if (user.id, answer.id) in existing_pairs:
                continue
            existing_pairs.add((user.id, answer.id))
            a_likes.append(AnswerLike(user=user, answer=answer))
        AnswerLike.objects.bulk_create(a_likes, ignore_conflicts=True)
        self.stdout.write(f'Создано лайков ответов: {len(a_likes)}')

        # 7. Обновляем рейтинг вопросов и ответов (на основе лайков)
        # Простой способ: подсчитать количество лайков и присвоить рейтинг
        # Можно сделать через raw SQL или агрегацию, но для краткости здесь не будем.
        # Это можно сделать отдельной командой.
        self.stdout.write(self.style.SUCCESS('Наполнение БД завершено!'))