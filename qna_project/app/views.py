from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Question, Tag, Profile
from .forms import *
import os
import uuid


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
  
def get_profile(request):
    if request.user.is_authenticated:
        return Profile.objects.get(user=request.user) 
    return None


def index(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        questions = Question.objects.recent()
    
        page = paginate(request, questions)
        
        return render(request, 'index.html', context={
            'questions': page.object_list,
            'profile': profile,
            'page': page,
            'left_bar_tags': left_bar_tags,
            'left_bar_profiles': left_bar_profiles,
            'search': False
        })
        
    results = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    )
    page = paginate(request, results)

    return render(request, 'index.html', context={
        'page': page,
        'profile': profile,
        'questions': page.object_list,
        'query': query,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'search': True
    }) 
    
def hot(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    questions = Question.objects.most_upvoted()
    
    page = paginate(request, questions)
    
    return render(request, 'hot.html', context={
        'questions': page.object_list,
        'profile': profile,
        'page': page,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })

def question(request, question_id):
    left_bar_tags, left_bar_profiles = left_bar_data()
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseNotFound('<h1>Question not found</h1>')
    
    profile = get_profile(request)
    
    if request.method == 'POST':
        form = NewAnswerForm(request.POST)
        
        if form.is_valid():
            answer = form.save(commit=False, question=question, profile=profile)
            return redirect('question', question.id)
    else:
        form = NewAnswerForm()
    
    return render(request, 'question.html', context={
        'question': question,
        'profile': profile,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'form': form
    })

@login_required(login_url='login')
def ask(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    profile = get_profile(request)
    
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(commit=False, profile=profile)
            return redirect('question', question.id)
    else:
        form = NewQuestionForm()
    
    return render(request, 'ask.html', context={
        'profile': profile,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'form': form
    })

def tag(request, tag):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    try:
        tag = Tag.objects.get(name=tag)
    except Tag.DoesNotExist:
        return HttpResponseNotFound('<h1>Tag not found</h1>')
    
    questions = Question.objects.by_tag(tag)
    
    page = paginate(request, questions)
    
    return render(request, 'tag_results.html', context={
        'page': page,
        'profile': profile,
        'questions': page.object_list,
        'tag_name': tag,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })

def profile(request):
  pass

@login_required(login_url='login')
def edit_profile(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    profile = get_profile(request)
    
    if profile.user != request.user:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('index')
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            saved_profile = form.save()
            
            avatar_file = form.cleaned_data.get('avatar')
            
            if avatar_file:
                try:
                    os.remove(saved_profile.avatar_image.path)
                except FileNotFoundError:
                    pass
                
                original_filename = avatar_file.name
                ext = os.path.splitext(original_filename)[1]
                unique_name = f"avatar_{profile.user.id}_{uuid.uuid4().hex[:8]}{ext}"
                
                saved_profile.avatar_image.save(unique_name, avatar_file)
            
            messages.success(request, 'Your profile has been updated.')
            return redirect('index')
        else:
            print(f"15. Form errors: {form.errors}")
            print(f"16. Form non-field errors: {form.non_field_errors}")
            messages.error(request, 'Please correct the errors.')
    else:
        form = EditProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', context={
        'profile': profile,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'form': form
    })

def login(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data.get('user')
            
            if user:
                auth.login(request, user)
                return redirect('index')
            else:
                return render(request, 'login.html', context={
                    'left_bar_tags': left_bar_tags,
                    'left_bar_profiles': left_bar_profiles,
                    'invalid_credentials': True,
                    'form': form
                })
    else:
        form = LoginForm()
    
    return render(request, 'login.html', context={
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'invalid_credentials': False,
        'form': form
    })

def logout(request):   
    next_page = request.GET.get('next')
    auth.logout(request)
  
    return redirect(next_page)

def register(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            new_profile = Profile.objects.create(
                user=user,
                nickname=form.cleaned_data.get('nickname'),
            )
            
            avatar_file = form.cleaned_data.get('avatar')
            
            if avatar_file:
                original_filename = avatar_file.name
                # Extract extension
                ext = os.path.splitext(original_filename)[1]
                unique_name = f"avatar_{profile.user.id}_{uuid.uuid4().hex[:8]}{ext}"
                
                new_profile.avatar_image.save(unique_name, avatar_file)
            
            new_profile.save()
            
            auth.login(request, user)
            
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', context={
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'form': form
    })