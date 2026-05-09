from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

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
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers_count = models.IntegerField(default=0, verbose_name='Количество ответов')
    
    objects = QuestionManager()
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
    
    def __str__(self):
        return self.title

class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'Ответ на {self.question.title[:20]}'

class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, 'Лайк'), (DISLIKE, 'Дизлайк')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    value = models.SmallIntegerField(choices=VALUE_CHOICES, default=LIKE, verbose_name='Значение')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'

class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, 'Лайк'), (DISLIKE, 'Дизлайк')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')
    value = models.SmallIntegerField(choices=VALUE_CHOICES, default=LIKE, verbose_name='Значение')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'