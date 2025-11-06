from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator

QUESTIONS = [
    { 
        'id': i,
        'title': f'Title #{i}',
        'text': 'Text',
        'tags': [f'tag{i//2}', 
                 (f'tag{i//2 + 1}' if i % 5 != 0 else 'python'),
                 (f'tag{i//2 + 2}' if i % 3 != 0 else 'django')],
    } for i in range(1, 30)
]

ANSWERS = [
    {
        'id': i,
        'text': f'Answer {i}',
        'correct': i % 3 == 2,
        'votes': i,
        'question': i // 2 + 1,
        'user': 'User'
    } for i in range(1, 50)
]

def index(request):
    page_num = int(request.GET.get('page', 1))
    
    paginator = Paginator(QUESTIONS, 10)
    
    page = paginator.get_page(page_num)
    
    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page': page
    })
    
def hot(request):
    return render(request, 'hot.html', context={
        'questions': QUESTIONS[::-1]
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