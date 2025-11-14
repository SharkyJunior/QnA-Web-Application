from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.models import User
from .models import Question, Tag, Profile, Answer


def paginate(request, obj_list, per_page=10):
    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1
        
    paginator = Paginator(obj_list, per_page)
    
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def index(request):
    questions = Question.objects.recent()
    
    page = paginate(request, questions)
    
    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page': page
    })
    
def hot(request):
    questions = Question.objects.most_upvoted()
    
    page = paginate(request, questions)
    
    return render(request, 'hot.html', context={
        'questions': page.object_list,
        'page': page
    })

def settings(request):
    return render(request, 'settings.html')

def login(request):
    return render(request, 'login.html')

def tag(request, tag):
    return render(request, 'tag_results.html', context={
        'tag': tag
    })
    
def register(request):
    return render(request, 'register.html')

def question(request, question_id):
    return render(request, 'question.html', context={
        'question': QUESTIONS[question_id - 1],
        'answers': [a for a in ANSWERS if a['question'] == question_id]
    })
    
def ask(request):
    return render(request, 'ask.html')

def tag(request, tag):
    filtered_q = [q for q in QUESTIONS if tag in q['tags']]
    
    page_num = int(request.GET.get('page', 1))
    
    paginator = Paginator(filtered_q, 10)
    
    page = paginator.get_page(page_num)
    
    return render(request, 'tag_results.html', context={
        'page': page,
        'questions': page.object_list
    })
    
def register(request):
    return render(request, 'register.html')