import copy
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f"Guys, i have trouble with a moon park. Can't find th black-jack….",
        'tags': ['black-jack', 'bender']
    } for i in range(30)
]

BIG_QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent pulvinar ullamcorper orci, non ornare mi suscipit hendrerit. Cras mattis sed nisl a sodales. Maecenas varius magna vel felis accumsan vulputate. Maecenas mauris erat, viverra in risus volutpat, interdum pellentesque ex. Phasellus fringilla est vehicula venenatis pulvinar. Proin dignissim tincidunt consectetur. Pellentesque a bibendum velit. Curabitur non magna sed eros congue rhoncus eget ut nisl. Donec volutpat interdum facilisis. Donec id maximus diam. Morbi vel sapien pharetra, laoreet magna in, aliquam nunc. Nullam tincidunt velit at ultricies pellentesque. Nulla facilisi. Aenean non ante justo. Donec sed maximus est. Fusce sodales magna. ",
        'tags': ['black-jack', 'bender']
    } for i in range(30)
]

ANSWERS = [
    {
        'text': 'First of all I would like to thank you for the invitation to participate in such a ... Russia is the huge territory which in many respects needs to be render habitable.'
    } for _ in range(15)
]


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


def index(request):
    page = paginate(QUESTIONS, request, per_page=5)
    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def hot(request):
    hot_questions = copy.deepcopy(QUESTIONS)
    hot_questions.reverse()
    page = paginate(hot_questions, request, per_page=5)
    return render(request, 'hot.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def question(request, question_id):
    page = paginate(ANSWERS, request, per_page=5)
    question_item = BIG_QUESTIONS[question_id]
    return render(request, 'question.html', {
        'question': question_item,
        'answers': page.object_list,
        'page_obj': page
    })


def tag(request, given_tag):
    page = paginate(QUESTIONS, request, per_page=5)
    return render(request, 'tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag': given_tag
    })


def ask(request):
    return render(request, 'ask.html')


def settings(request):
    return render(request, 'settings.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')
