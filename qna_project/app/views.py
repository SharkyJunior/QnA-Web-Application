from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseNotFound
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

def left_bar_data():
    return Tag.objects.most_popular()[:7], Profile.objects.most_active()[:7]

def index(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    questions = Question.objects.recent()
    
    page = paginate(request, questions)
    
    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page': page,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })
    
def hot(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    questions = Question.objects.most_upvoted()
    
    page = paginate(request, questions)
    
    return render(request, 'hot.html', context={
        'questions': page.object_list,
        'page': page,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })

def settings(request):
    return render(request, 'settings.html')

def login(request):
    return render(request, 'login.html')
    
def register(request):
    return render(request, 'register.html')

def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseNotFound('<h1>Question not found</h1>')
    
    return render(request, 'question.html', context={
        'question': question,
    })
    
def ask(request):
    return render(request, 'ask.html')

def tag(request, tag):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    try:
        tag = Tag.objects.get(name=tag)
    except Tag.DoesNotExist:
        return HttpResponseNotFound('<h1>Tag not found</h1>')
    
    questions = Question.objects.by_tag(tag)
    
    page = paginate(request, questions)
    
    return render(request, 'tag_results.html', context={
        'page': page,
        'questions': page.object_list,
        'tag_name': tag,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })
    
def register(request):
    return render(request, 'register.html')

def profile(request):
    pass
