import time
import jwt
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings as django_settings
from django.db.models import Q
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from .forms import AnswerForm, AskForm, VoteForm, CorrectAnswerForm


def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)

    current = page.number
    total = page.paginator.num_pages
    pages = sorted({1, total} | set(range(max(1, current - 2), min(total + 1, current + 3))))
    display_range = []
    prev = None
    for p in pages:
        if prev is not None and p - prev > 1:
            display_range.append(None)
        display_range.append(p)
        prev = p
    page.display_range = display_range

    return page


def _get_user_question_votes(user, question_ids):
    if not user.is_authenticated:
        return set(), set()
    votes = QuestionLike.objects.filter(
        user=user, question_id__in=question_ids
    ).values_list('question_id', 'value')
    liked = {qid for qid, v in votes if v == 1}
    disliked = {qid for qid, v in votes if v == -1}
    return liked, disliked


def _get_user_answer_votes(user, answer_ids):
    if not user.is_authenticated:
        return set(), set()
    votes = AnswerLike.objects.filter(
        user=user, answer_id__in=answer_ids
    ).values_list('answer_id', 'value')
    liked = {aid for aid, v in votes if v == 1}
    disliked = {aid for aid, v in votes if v == -1}
    return liked, disliked


def _centrifugo_token(user):
    """JWT-токен для подключения к Centrifugo."""
    if not user.is_authenticated:
        return ''
    return jwt.encode(
        {'sub': str(user.id), 'exp': int(time.time()) + 3600},
        django_settings.CENTRIFUGO_TOKEN_SECRET,
        algorithm='HS256',
    )


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=5)
    question_ids = [q.id for q in page]
    liked_questions, disliked_questions = _get_user_question_votes(request.user, question_ids)
    return render(request, 'index.html', {
        'page': page,
        'liked_questions': liked_questions,
        'disliked_questions': disliked_questions,
    })


def hot(request):
    questions = Question.objects.best()
    page = paginate(questions, request, per_page=5)
    question_ids = [q.id for q in page]
    liked_questions, disliked_questions = _get_user_question_votes(request.user, question_ids)
    return render(request, 'hot.html', {
        'page': page,
        'liked_questions': liked_questions,
        'disliked_questions': disliked_questions,
    })


def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request, per_page=5)
    question_ids = [q.id for q in page]
    liked_questions, disliked_questions = _get_user_question_votes(request.user, question_ids)
    return render(request, 'tag.html', {
        'page': page,
        'tag_name': tag_name,
        'liked_questions': liked_questions,
        'disliked_questions': disliked_questions,
    })


def question_detail(request, id):
    question = get_object_or_404(Question.objects.select_related('author'), id=id)
    answers = question.answers.select_related('author').order_by('-created_at')
    page = paginate(answers, request, per_page=4)

    answer_ids = [a.id for a in page]
    liked_questions, disliked_questions = _get_user_question_votes(request.user, [question.id])
    liked_answers, disliked_answers = _get_user_answer_votes(request.user, answer_ids)

    answer_form = None
    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(user=request.user, question=question)

            # Запускаем фоновые задачи (email + centrifugo)
            from .tasks import notify_answer_by_email, publish_new_answer
            notify_answer_by_email.delay(question.id, request.user.username)
            answer_data = {
                'id': answer.id,
                'text': answer.text,
                'author': answer.author.username,
                'created_at': answer.created_at.strftime('%d.%m.%Y %H:%M'),
                'rating': answer.rating,
            }
            publish_new_answer.delay(question.id, answer_data)

            return redirect(f'{request.path}?page=1#answer-{answer.id}')
    elif request.user.is_authenticated:
        answer_form = AnswerForm()

    return render(request, 'question.html', {
        'question': question,
        'page': page,
        'form': answer_form,
        'liked_questions': liked_questions,
        'disliked_questions': disliked_questions,
        'liked_answers': liked_answers,
        'disliked_answers': disliked_answers,
        'centrifugo_token': _centrifugo_token(request.user),
        'centrifugo_ws_url': django_settings.CENTRIFUGO_WS_URL,
    })


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


# ── AJAX: поиск ──────────────────────────────────────────────────────────

@require_GET
def search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    try:
        # Полнотекстовый поиск PostgreSQL
        from django.contrib.postgres.search import SearchVector, SearchQuery
        questions = (
            Question.objects
            .annotate(search=SearchVector('title', 'text'))
            .filter(search=SearchQuery(query))
            .values('id', 'title')[:7]
        )
    except Exception:
        # Fallback для SQLite (локальная разработка)
        questions = (
            Question.objects
            .filter(Q(title__icontains=query) | Q(text__icontains=query))
            .values('id', 'title')[:7]
        )

    return JsonResponse({'results': list(questions)})


# ── AJAX: лайки/дизлайки ─────────────────────────────────────────────────

@require_POST
def question_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required', 'login_url': '/login/'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    try:
        question, status = form.save_question_vote(request.user)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    return JsonResponse({'rating': question.rating, 'status': status})


@require_POST
def answer_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required', 'login_url': '/login/'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    try:
        answer, status = form.save_answer_vote(request.user)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    return JsonResponse({'rating': answer.rating, 'status': status})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'login_required', 'login_url': '/login/'}, status=401)

    form = CorrectAnswerForm(request.POST, user=request.user)
    if not form.is_valid():
        errors = form.errors
        if 'question_id' in errors:
            return JsonResponse({'error': 'not_author'}, status=403)
        return JsonResponse({'error': errors}, status=400)

    try:
        answer = form.save()
    except Exception:
        return JsonResponse({'error': 'invalid'}, status=400)

    return JsonResponse({'is_correct': answer.is_correct, 'answer_id': answer.id})
