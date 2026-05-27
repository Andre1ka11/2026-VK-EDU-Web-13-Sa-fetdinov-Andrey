from django.db import models
from django.conf import settings
from django.db.models import Sum


class Tag(models.Model):
    name = models.SlugField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')

    def best(self):
        return self.order_by('-rating')

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name)


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор'
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(max_length=10000, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers_count = models.IntegerField(default=0, verbose_name='Количество ответов')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title

    def update_rating(self):
        result = self.questionlike_set.aggregate(total=Sum('value'))
        self.rating = result['total'] or 0
        self.save(update_fields=['rating'])

    def update_answers_count(self):
        self.answers_count = self.answers.count()
        self.save(update_fields=['answers_count'])


class Answer(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос'
    )
    text = models.TextField(max_length=10000, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'Ответ на {self.question.title[:20]}'

    def update_rating(self):
        result = self.answerlike_set.aggregate(total=Sum('value'))
        self.rating = result['total'] or 0
        self.save(update_fields=['rating'])


class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, 'Лайк'), (DISLIKE, 'Дизлайк')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES, default=LIKE, verbose_name='Значение'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'


class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, 'Лайк'), (DISLIKE, 'Дизлайк')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES, default=LIKE, verbose_name='Значение'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
