from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Question, Answer, Tag
from .forms import AnswerForm  # добавим форму ответа
from .forms import AskForm
from django.contrib.auth.decorators import login_required

@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return redirect('questions:question', id=question.id)
    else:
        form = AskForm()
    return render(request, 'ask.html', {'form': form})
def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'page': page})

def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=5)
    return render(request, 'hot.html', {'page': page})

def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=5)
    return render(request, 'tag.html', {'page': page, 'tag_name': tag_name})

def question_detail(request, id):
    question = get_object_or_404(Question.objects.select_related('author'), id=id)
    answers = question.answers.select_related('author').order_by('-created_at')
    page = paginate(answers, request, per_page=4)

    # Обработка формы ответа
    answer_form = None
    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            # Перенаправляем на ту же страницу с якорем к новому ответу
            return redirect(f'{request.path}?page={page.number}#answer-{answer.id}')
    elif request.user.is_authenticated:
        answer_form = AnswerForm()

    return render(request, 'question.html', {
        'question': question,
        'page': page,
        'form': answer_form,
    })

def ask(request):
    return render(request, 'ask.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def profile_view(request):
    return render(request, 'profile.html')