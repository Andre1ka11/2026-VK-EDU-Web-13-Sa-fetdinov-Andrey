import logging
import requests
from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

POPULAR_TAGS_CACHE_KEY = 'sidebar:popular_tags'
BEST_MEMBERS_CACHE_KEY = 'sidebar:best_members'
CACHE_TIMEOUT = 60 * 60  # 1 час


# ── Кеш: популярные теги ──────────────────────────────────────────────────

@shared_task(name='questions.tasks.update_popular_tags')
def update_popular_tags():
    from django.db.models import Count
    from .models import Tag

    three_months_ago = timezone.now() - timedelta(days=90)
    tags = list(
        Tag.objects.annotate(q_count=Count('question'))
        .filter(q_count__gt=0, question__created_at__gte=three_months_ago)
        .order_by('-q_count')
        .distinct()
        .values('name', 'q_count')[:10]
    )
    cache.set(POPULAR_TAGS_CACHE_KEY, tags, CACHE_TIMEOUT)
    logger.info('Popular tags cache updated: %d tags', len(tags))
    return len(tags)


# ── Кеш: лучшие пользователи ─────────────────────────────────────────────

@shared_task(name='questions.tasks.update_best_members')
def update_best_members():
    from django.db.models import Subquery, OuterRef, Sum, IntegerField, Value, F
    from django.db.models.functions import Coalesce
    from django.contrib.auth.models import User
    from .models import Question, Answer

    one_week_ago = timezone.now() - timedelta(days=7)

    q_rating = Subquery(
        Question.objects.filter(author=OuterRef('pk'), created_at__gte=one_week_ago)
        .values('author').annotate(s=Sum('rating')).values('s'),
        output_field=IntegerField()
    )
    a_rating = Subquery(
        Answer.objects.filter(author=OuterRef('pk'), created_at__gte=one_week_ago)
        .values('author').annotate(s=Sum('rating')).values('s'),
        output_field=IntegerField()
    )

    users = list(
        User.objects.annotate(
            q_rating=Coalesce(q_rating, Value(0)),
            a_rating=Coalesce(a_rating, Value(0)),
        ).annotate(
            week_rating=F('q_rating') + F('a_rating')
        ).filter(week_rating__gt=0)
        .order_by('-week_rating')
        .values('username', 'week_rating')[:10]
    )
    cache.set(BEST_MEMBERS_CACHE_KEY, users, CACHE_TIMEOUT)
    logger.info('Best members cache updated: %d users', len(users))
    return len(users)


# ── Email: уведомление автора вопроса ────────────────────────────────────

@shared_task(name='questions.tasks.notify_answer_by_email')
def notify_answer_by_email(question_id, answer_author_username):
    from .models import Question

    try:
        question = Question.objects.select_related('author').get(id=question_id)
    except Question.DoesNotExist:
        return

    author_email = question.author.email
    if not author_email:
        return

    send_mail(
        subject=f'Новый ответ на ваш вопрос: {question.title[:50]}',
        message=(
            f'Пользователь {answer_author_username} ответил на ваш вопрос '
            f'«{question.title}».\n\n'
            f'Посмотреть ответ: http://localhost:8000/question/{question.id}/'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[author_email],
        fail_silently=True,
    )
    logger.info('Email sent to %s for question %d', author_email, question_id)


# ── Centrifugo: публикация нового ответа ─────────────────────────────────

@shared_task(name='questions.tasks.publish_new_answer')
def publish_new_answer(question_id, answer_data):
    channel = f'questions:{question_id}'
    try:
        response = requests.post(
            f'{settings.CENTRIFUGO_API_URL}/publish',
            json={'channel': channel, 'data': answer_data},
            headers={
                'Authorization': f'apikey {settings.CENTRIFUGO_API_KEY}',
                'Content-Type': 'application/json',
            },
            timeout=5,
        )
        response.raise_for_status()
        logger.info('Published to centrifugo channel %s', channel)
    except Exception as exc:
        logger.warning('Centrifugo publish failed: %s', exc)
