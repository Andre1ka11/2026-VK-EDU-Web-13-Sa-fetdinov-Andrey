from django import forms
from .models import Answer, Question, Tag

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ваш ответ...', 'class': 'form-control'}),
        }

class AskForm(forms.ModelForm):
    tags = forms.CharField(label='Теги (через запятую)', required=False, help_text='Например: python, django, учеба')

    class Meta:
        model = Question
        fields = ('title', 'text')

    def save(self, user, commit=True):
        question = super().save(commit=False)
        question.author = user
        if commit:
            question.save()
        tags_input = self.cleaned_data.get('tags', '')
        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
        return question