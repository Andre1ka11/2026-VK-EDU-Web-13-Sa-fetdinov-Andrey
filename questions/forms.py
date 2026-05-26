from django import forms
from .models import Answer, Question, Tag, QuestionLike, AnswerLike


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш ответ...', 'class': 'form-control'}),
        }

    def save(self, user, question, commit=True):
        answer = super().save(commit=False)
        answer.author = user
        answer.question = question
        if commit:
            answer.save()
            question.update_answers_count()
        return answer


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги (через запятую)',
        required=False,
        max_length=500,
        help_text='Например: python, django, учеба. Каждый тег — не более 50 символов.',
    )

    class Meta:
        model = Question
        fields = ('title', 'text')

    def clean_tags(self):
        tags_input = self.cleaned_data.get('tags', '')
        tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
        for name in tag_names:
            if len(name) > 50:
                raise forms.ValidationError(
                    f'Тег «{name[:20]}…» слишком длинный (максимум 50 символов).'
                )
        return tag_names

    def save(self, user, commit=True):
        question = super().save(commit=False)
        question.author = user
        if commit:
            question.save()
            for tag_name in self.cleaned_data.get('tags', []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
        return question


class VoteForm(forms.Form):
    id = forms.IntegerField(min_value=1)
    value = forms.IntegerField()

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value not in (1, -1):
            raise forms.ValidationError('Значение должно быть 1 (лайк) или -1 (дизлайк).')
        return value

    def save_question_vote(self, user):
        question_id = self.cleaned_data['id']
        value = self.cleaned_data['value']
        question = Question.objects.get(id=question_id)

        try:
            existing = QuestionLike.objects.get(user=user, question=question)
            if existing.value == value:
                existing.delete()
                status = 'removed'
            else:
                existing.value = value
                existing.save(update_fields=['value'])
                status = 'updated'
        except QuestionLike.DoesNotExist:
            QuestionLike.objects.create(user=user, question=question, value=value)
            status = 'created'

        question.update_rating()
        return question, status

    def save_answer_vote(self, user):
        answer_id = self.cleaned_data['id']
        value = self.cleaned_data['value']
        answer = Answer.objects.get(id=answer_id)

        try:
            existing = AnswerLike.objects.get(user=user, answer=answer)
            if existing.value == value:
                existing.delete()
                status = 'removed'
            else:
                existing.value = value
                existing.save(update_fields=['value'])
                status = 'updated'
        except AnswerLike.DoesNotExist:
            AnswerLike.objects.create(user=user, answer=answer, value=value)
            status = 'created'

        answer.update_rating()
        return answer, status


class CorrectAnswerForm(forms.Form):
    question_id = forms.ModelChoiceField(queryset=Question.objects.all())
    answer_id = forms.ModelChoiceField(queryset=Answer.objects.all())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['question_id'].queryset = Question.objects.filter(author=user)

    def save(self):
        question = self.cleaned_data['question_id']
        answer = self.cleaned_data['answer_id']

        if answer.question_id != question.id:
            raise forms.ValidationError('Ответ не принадлежит этому вопросу.')

        new_is_correct = not answer.is_correct
        if new_is_correct:
            question.answers.update(is_correct=False)
        answer.is_correct = new_is_correct
        answer.save(update_fields=['is_correct'])
        return answer
