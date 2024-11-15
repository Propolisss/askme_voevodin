import copy
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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


TAGS = Tag.objects.get_top()
MEMBERS = Profile.objects.get_top()
HOT = Question.objects.get_hot()


def index(request):
    page = paginate(Question.objects.get_new(), request, per_page=5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': TAGS,
        'members': MEMBERS
    })


def hot(request):
    page = paginate(HOT, request, per_page=5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': TAGS,
        'members': MEMBERS
    })


def question(request, question_id):
    try:
        page = paginate(Question.objects.get_answers_by_id(question_id), request, per_page=5)
        return render(request, 'question.html', {
            'question': Question.objects.get(id=question_id),
            'answers': page.object_list,
            'page_obj': page,
            'tags': TAGS,
            'members': MEMBERS
        })
    except Question.DoesNotExist:
        return render(request, 'error.html', {
            'error_code': 404,
            'error_description': 'Page Not Found',
            'error_message': 'Sorry, the question you are looking for does not exist.'
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


def ask(request):
    return render(request, 'ask.html', {
        'tags': TAGS,
        'members': MEMBERS
    })


def settings(request):
    return render(request, 'settings.html', {
        'tags': TAGS,
        'members': MEMBERS
    })


def login(request):
    return render(request, 'login.html', {
        'tags': TAGS,
        'members': MEMBERS
    })


def signup(request):
    return render(request, 'signup.html', {
        'tags': TAGS,
        'members': MEMBERS
    })
