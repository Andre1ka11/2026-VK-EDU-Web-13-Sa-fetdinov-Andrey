from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('author', 'text', 'created_at', 'rating', 'is_correct')
    readonly_fields = ('created_at',)
    raw_id_fields = ('author',)  # оптимизация для большого количества пользователей

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at', 'rating', 'answers_count')
    search_fields = ('title', 'author__username', 'text')
    list_filter = ('created_at', 'tags')
    raw_id_fields = ('author',)  # вместо выпадающего списка с тысячами пользователей
    filter_horizontal = ('tags',)
    inlines = [AnswerInline]
    date_hierarchy = 'created_at'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'created_at', 'rating', 'is_correct')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('created_at', 'is_correct')
    raw_id_fields = ('author', 'question')

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'created_at')
    raw_id_fields = ('user', 'question')
    list_filter = ('created_at',)

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer', 'created_at')
    raw_id_fields = ('user', 'answer')
    list_filter = ('created_at',)