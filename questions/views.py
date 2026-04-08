from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Вопрос {i}: Как сдать экзамен?',
            'text': f'Текст вопроса {i}. Нужна помощь с учебой...',
            'answers_count': i * 3 % 10,
            'tags': ['учеба', 'экзамен', f'тег{i}'],
            'author': f'user{i}',
            'created_at': '2 часа назад',
            'likes': i * 2,
        })
    page = paginate(questions, request, per_page=5)
    return render(request, 'index.html', {'page': page})

def hot(request):
    questions = []
    for i in range(1, 30):
        questions.append({
            'id': i,
            'title': f'Горячий вопрос {i}',
            'text': f'Текст горячего вопроса {i}',
            'answers_count': i * 2,
            'tags': ['популярное', 'hot'],
            'author': f'hot_user{i}',
            'created_at': 'вчера',
            'likes': i * 10,
        })
    page = paginate(questions, request, per_page=5)
    return render(request, 'hot.html', {'page': page})

def tag(request, tag_name):
    questions = []
    for i in range(1, 20):
        questions.append({
            'id': i,
            'title': f'Вопрос по тегу {tag_name} #{i}',
            'text': f'Текст вопроса с тегом {tag_name}',
            'answers_count': i,
            'tags': [tag_name, 'другой'],
            'author': f'tag_user{i}',
            'created_at': '3 дня назад',
            'likes': i * 3,
        })
    page = paginate(questions, request, per_page=5)
    return render(request, 'tag.html', {'page': page, 'tag_name': tag_name})

def question_detail(request, id):
    question = {
        'id': id,
        'title': f'Вопрос #{id}: Как сдать экзамен?',
        'text': 'Подробное описание вопроса. Нужна помощь с учебой...',
        'answers_count': 5,
        'tags': ['учеба', 'экзамен'],
        'author': 'student123',
        'created_at': '2 дня назад',
        'likes': 42,
    }
    answers = []
    for i in range(1, 15):
        answers.append({
            'id': i,
            'text': f'Ответ {i}: Попробуй почитать учебник...',
            'author': f'answer_user{i}',
            'created_at': f'{i} часов назад',
            'likes': i * 2,
            'is_correct': i == 1,
        })
    page = paginate(answers, request, per_page=4)
    return render(request, 'question.html', {'question': question, 'page': page})

def ask(request):
    return render(request, 'ask.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def profile_view(request):
    return render(request, 'profile.html')