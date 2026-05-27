import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from faker import Faker
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Множитель для количества сущностей')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f'Начинаем наполнение БД с ratio={ratio}')

        # 1. Пользователи — один раз хешируем пароль для всех (быстро)
        hashed_password = make_password('password123')
        users = []
        fake.unique.clear()
        for _ in range(ratio):
            users.append(User(
                username=fake.unique.user_name(),
                email=fake.email(),
                password=hashed_password,
            ))
        User.objects.bulk_create(users, ignore_conflicts=True)
        all_users = list(User.objects.all())
        self.stdout.write(f'Пользователей: {len(all_users)}')

        # 2. Теги — генерируем уникальные slug-имена через set
        tag_names = set()
        attempts = 0
        fake.unique.clear()
        while len(tag_names) < ratio and attempts < ratio * 10:
            attempts += 1
            word = fake.word()[:50]
            tag_names.add(word)
        tags = [Tag(name=name) for name in tag_names]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        all_tags = list(Tag.objects.all())
        self.stdout.write(f'Тегов: {len(all_tags)}')

        # 3. Вопросы
        questions = [
            Question(
                author=random.choice(all_users),
                title=fake.sentence(nb_words=8)[:255],
                text=fake.paragraph(nb_sentences=5),
            )
            for _ in range(ratio * 10)
        ]
        Question.objects.bulk_create(questions)
        all_questions = list(Question.objects.all())
        for q in all_questions:
            q.tags.add(*random.sample(all_tags, k=min(random.randint(1, 5), len(all_tags))))
        self.stdout.write(f'Вопросов: {len(all_questions)}')

        # 4. Ответы
        answers = [
            Answer(
                author=random.choice(all_users),
                question=random.choice(all_questions),
                text=fake.paragraph(nb_sentences=3),
            )
            for _ in range(ratio * 100)
        ]
        Answer.objects.bulk_create(answers)
        all_answers = list(Answer.objects.all())
        self.stdout.write(f'Ответов: {len(all_answers)}')

        # 5. Лайки вопросов
        existing_q_pairs = set(
            QuestionLike.objects.values_list('user_id', 'question_id')
        )
        q_likes = []
        for _ in range(ratio * 100):
            user = random.choice(all_users)
            question = random.choice(all_questions)
            if (user.id, question.id) not in existing_q_pairs:
                existing_q_pairs.add((user.id, question.id))
                q_likes.append(QuestionLike(
                    user=user,
                    question=question,
                    value=random.choice([1, -1]),
                ))
        QuestionLike.objects.bulk_create(q_likes, ignore_conflicts=True)
        self.stdout.write(f'Лайков вопросов: {len(q_likes)}')

        # 6. Лайки ответов
        existing_a_pairs = set(
            AnswerLike.objects.values_list('user_id', 'answer_id')
        )
        a_likes = []
        for _ in range(ratio * 100):
            user = random.choice(all_users)
            answer = random.choice(all_answers)
            if (user.id, answer.id) not in existing_a_pairs:
                existing_a_pairs.add((user.id, answer.id))
                a_likes.append(AnswerLike(
                    user=user,
                    answer=answer,
                    value=random.choice([1, -1]),
                ))
        AnswerLike.objects.bulk_create(a_likes, ignore_conflicts=True)
        self.stdout.write(f'Лайков ответов: {len(a_likes)}')

        # 7. Пересчёт денормализаций
        self.stdout.write('Пересчитываем рейтинги и количество ответов...')
        for q in Question.objects.all():
            q.update_rating()
            q.update_answers_count()
        for a in Answer.objects.all():
            a.update_rating()

        self.stdout.write(self.style.SUCCESS('Наполнение БД завершено!'))
