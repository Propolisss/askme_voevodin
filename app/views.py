import copy
from audioop import reverse

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse as reverse
from app.forms import LoginForm, UserForm, AnswerForm, SettingsForm, QuestionForm
from app.models import Question, Tag, Answer, Profile


# Create your views here.

def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        if int(page_num) > paginator.num_pages:
            page = paginator.page(paginator.num_pages)
        elif int(page_num) < 1:
            page = paginator.page(1)
    return page


def common_context(request):
    tags = Tag.objects.get_top()
    members = Profile.objects.get_top()
    return {
        'tags': tags,
        'members': members
    }


TAGS = Tag.objects.get_top()
MEMBERS = Profile.objects.get_top()


def index(request):
    page = paginate(Question.objects.get_new(), request, per_page=5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': TAGS,
        'members': MEMBERS
    })


def hot(request):
    page = paginate(Question.objects.get_hot(), request, per_page=5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': TAGS,
        'members': MEMBERS
    })


def get_page_number(questions, answer_id):
    for i, ques in enumerate(questions):
        if ques.id == answer_id:
            return i // 5 + 1
    raise ValueError


def redirect_to_answer(question_id, answer_id, answers):
    return redirect(reverse('question', kwargs={
        'question_id': question_id
    }) + f'?page={get_page_number(answers, answer_id)}' + f'#{answer_id}')


def question(request, question_id):
    try:
        answers = Question.objects.get_answers_by_id(question_id)
        page = paginate(answers, request, per_page=5)
        form = AnswerForm(request.user, question_id,
                          data=(request.POST or None))
        if request.method == 'POST':
            if form.is_valid():
                answer = form.save()
                return redirect_to_answer(question_id, answer.id, answers)
        return render(request, 'question.html', {
            'question': Question.objects.get(id=question_id),
            'answers': page.object_list,
            'page_obj': page,
            'tags': TAGS,
            'members': MEMBERS,
            'form': form
        })
    except Question.DoesNotExist:
        return render(request, 'error.html', {
            'error_code': 404,
            'error_description': 'Page Not Found',
            'error_message': 'Sorry, the question you are looking for does not exist.'
        })
    except ValueError:
        return render(request, 'error.html', {
            'error_code': 404,
            'error_description': 'Answer error',
            'error_message': 'Sorry, your answer was lost'
        })


def tag(request, given_tag):
    try:
        page = paginate(Tag.objects.get_questions_by_tag(given_tag), request, per_page=5)
        return render(request, 'tag.html', {
            'questions': page.object_list,
            'page_obj': page,
            'tag': given_tag,
            'tags': TAGS,
            'members': MEMBERS
        })
    except Tag.DoesNotExist:
        return render(request, 'error.html', {
            'error_code': 404,
            'error_description': 'Page Not Found',
            'error_message': 'Sorry, the tag you are looking for does not exist.'
        })


@login_required
def ask(request):
    form = QuestionForm(request.user, data=(request.POST or None))
    if request.method == 'POST':
        if form.is_valid():
            question = form.save()
            return redirect('question', question_id=question.id)
    return render(request, 'ask.html', {
        'tags': TAGS,
        'members': MEMBERS,
        'form': form
    })


@login_required
def settings(request):
    form = SettingsForm(request.user, data=(request.POST or None), files=(request.FILES or None),
                        instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            form = SettingsForm(request.user, instance=request.user)
    return render(request, 'settings.html', {
        'tags': TAGS,
        'members': MEMBERS,
        'form': form
    })


def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                continue_page = request.GET.get('continue', None)
                if continue_page:
                    return redirect(continue_page)
                else:
                    return redirect(reverse('index'))
            form.add_error('password', 'Invalid username or password')

    return render(request, 'login.html', {
        'tags': TAGS,
        'members': MEMBERS,
        'form': form
    })


def signup(request):
    form = UserForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect(reverse('index'))
    return render(request, 'signup.html', {
        'tags': TAGS,
        'members': MEMBERS,
        'form': form
    })


@login_required
def logout(request):
    continue_page = request.GET.get('continue', None)
    auth.logout(request)
    if continue_page:
        return redirect(continue_page)
    else:
        return redirect(reverse('login'))
