from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from .forms import AnswerForm, AskForm, VoteForm, CorrectAnswerForm


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


def _get_user_question_votes(user, question_ids):
    if not user.is_authenticated:
        return {}, {}
    votes = QuestionLike.objects.filter(
        user=user, question_id__in=question_ids
    ).values_list('question_id', 'value')
    liked = {qid for qid, v in votes if v == 1}
    disliked = {qid for qid, v in votes if v == -1}
    return liked, disliked


def _get_user_answer_votes(user, answer_ids):
    if not user.is_authenticated:
        return {}, {}
    votes = AnswerLike.objects.filter(
        user=user, answer_id__in=answer_ids
    ).values_list('answer_id', 'value')
    liked = {aid for aid, v in votes if v == 1}
    disliked = {aid for aid, v in votes if v == -1}
    return liked, disliked


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
            answer = answer_form.save(commit=False)
            answer.author = request.user
            answer.question = question
            answer.save()
            question.answers_count = question.answers.count()
            question.save(update_fields=['answers_count'])
            return redirect(f'{request.path}?page={page.number}#answer-{answer.id}')
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


@require_POST
def question_like(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'login_required', 'login_url': '/login/'},
            status=401,
        )

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    question_id = form.cleaned_data['id']
    value = form.cleaned_data['value']

    question = get_object_or_404(Question, id=question_id)

    try:
        existing = QuestionLike.objects.get(user=request.user, question=question)
        if existing.value == value:
            question.rating -= existing.value
            question.save(update_fields=['rating'])
            existing.delete()
            status = 'removed'
        else:
            question.rating = question.rating - existing.value + value
            question.save(update_fields=['rating'])
            existing.value = value
            existing.save(update_fields=['value'])
            status = 'updated'
    except QuestionLike.DoesNotExist:
        QuestionLike.objects.create(user=request.user, question=question, value=value)
        question.rating += value
        question.save(update_fields=['rating'])
        status = 'created'

    return JsonResponse({'rating': question.rating, 'status': status})


@require_POST
def answer_like(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'login_required', 'login_url': '/login/'},
            status=401,
        )

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    answer_id = form.cleaned_data['id']
    value = form.cleaned_data['value']

    answer = get_object_or_404(Answer, id=answer_id)

    try:
        existing = AnswerLike.objects.get(user=request.user, answer=answer)
        if existing.value == value:
            answer.rating -= existing.value
            answer.save(update_fields=['rating'])
            existing.delete()
            status = 'removed'
        else:
            answer.rating = answer.rating - existing.value + value
            answer.save(update_fields=['rating'])
            existing.value = value
            existing.save(update_fields=['value'])
            status = 'updated'
    except AnswerLike.DoesNotExist:
        AnswerLike.objects.create(user=request.user, answer=answer, value=value)
        answer.rating += value
        answer.save(update_fields=['rating'])
        status = 'created'

    return JsonResponse({'rating': answer.rating, 'status': status})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'login_required', 'login_url': '/login/'},
            status=401,
        )

    form = CorrectAnswerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    question_id = form.cleaned_data['question_id']
    answer_id = form.cleaned_data['answer_id']

    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, id=answer_id, question=question)

    if question.author != request.user:
        return JsonResponse({'error': 'not_author'}, status=403)

    new_is_correct = not answer.is_correct
    if new_is_correct:
        question.answers.update(is_correct=False)

    answer.is_correct = new_is_correct
    answer.save(update_fields=['is_correct'])

    return JsonResponse({'is_correct': answer.is_correct, 'answer_id': answer.id})
