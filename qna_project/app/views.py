from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Question, Tag, Profile, QuestionVote, AnswerVote
from .forms import *
import os, uuid, json


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

def get_user_votes_context(profile, questions_queryset):
    if not profile:
        return {}
    
    question_ids = list(questions_queryset.values_list('id', flat=True))
    
    question_votes = QuestionVote.objects.filter(
        profile=profile,
        question_id__in=question_ids
    ).values('question_id', 'value')
    
    answer_votes = AnswerVote.objects.filter(
        profile=profile,
        answer__question_id__in=question_ids
    ).values('answer_id', 'value')
    
    question_votes_dict = {
        str(vote['question_id']): 'upvote' if vote['value'] == 1 else 'downvote'
        for vote in question_votes
    }
    
    answer_votes_dict = {
        str(vote['answer_id']): 'upvote' if vote['value'] == 1 else 'downvote'
        for vote in answer_votes
    }
    
    return {
        'questions': question_votes_dict,
        'answers': answer_votes_dict
    }

def index(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        questions = Question.objects.recent().select_related('profile')
        
        page = paginate(request, questions)
        
        profile_votes = get_user_votes_context(profile, questions) if profile else {'questions': {}, 'answers': {}}
        
        enriched_questions = []
        for question in page.object_list:
            question.user_vote = profile_votes['questions'].get(str(question.id))
            enriched_questions.append(question)
        
        
        return render(request, 'index.html', context={
            'questions': enriched_questions,
            'profile': profile,
            'page': page,
            'profile_votes': profile_votes,
            'left_bar_tags': left_bar_tags,
            'left_bar_profiles': left_bar_profiles,
            'search': False
        })
        
    query_results = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    )
    page = paginate(request, query_results)
    
    profile_votes = get_user_votes_context(profile, query_results) if profile else {'questions': {}, 'answers': {}}
        
    enriched_questions = []
    for question in page.object_list:
        question.user_vote = profile_votes['questions'].get(str(question.id))
        
        for answer in question.answers.all():
            answer.user_vote = profile_votes['answers'].get(str(answer.id))
        
        enriched_questions.append(question)
    
    context = {
        'page': page,
        'profile': profile,
        'questions': enriched_questions,
        'query': query,
        'profile_votes': profile_votes,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'search': True,
        'question_count': query_results.count()
    }

    return render(request, 'index.html', context=context) 
    
def hot(request):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    questions = Question.objects.most_upvoted().select_related('profile')

    page = paginate(request, questions)
    
    profile_votes = get_user_votes_context(profile, questions) if profile else {'questions': {}, 'answers': {}}
    
    enriched_questions = []
    for question in page.object_list:
        question.user_vote = profile_votes['questions'].get(str(question.id))
        
        enriched_questions.append(question)
    
    return render(request, 'hot.html', context={
        'questions': enriched_questions,
        'profile_votes': profile_votes,
        'profile': profile,
        'page': page,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles 
    })

def question(request, question_id):
    left_bar_tags, left_bar_profiles = left_bar_data()
    
    profile = get_profile(request)
    
    if not profile:
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return HttpResponseNotFound('<h1>Question not found</h1>')
    
        answers = question.answers.all()
    
        profile_votes = {'questions': {}, 'answers': {}}
    
    else:
        try:
            question = Question.objects.filter(id=question_id)
        except Question.DoesNotExist:
            return HttpResponseNotFound('<h1>Question not found</h1>')
        
        profile_votes = get_user_votes_context(profile, question)
        question = question.first()
        answers = question.answers.all()
        question.user_vote = profile_votes['questions'].get(str(question.id))
        
        for answer in answers:
            answer.user_vote = profile_votes['answers'].get(str(answer.id))
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = NewAnswerForm(request.POST)
        
        if form.is_valid():
            answer = form.save(commit=False, question=question, profile=profile)
            return redirect('question', question.id)
    else:
        form = NewAnswerForm()
    
    return render(request, 'question.html', context={
        'question': question,
        'answers': answers,
        'profile': profile,
        'profile_votes': profile_votes,
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
    
    profile_votes = get_user_votes_context(profile, questions) if profile else {'questions': {}, 'answers': {}}
    
    enriched_questions = []
    for question in page.object_list:
        question.user_vote = profile_votes['questions'].get(str(question.id))
        
        enriched_questions.append(question)
    
    return render(request, 'tag_results.html', context={
        'page': page,
        'profile': profile,
        'questions': enriched_questions,
        'profile_votes': profile_votes,
        'tag_name': tag,
        'left_bar_tags': left_bar_tags,
        'left_bar_profiles': left_bar_profiles,
        'question_count': questions.count()
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
  
@require_POST
def vote(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Вы не авторизованы'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        object_type = data.get('object_type')
        object_id = data.get('object_id')
        vote_type = data.get('vote_type') 
        
        if (not object_id or vote_type not in ['upvote', 'downvote'] or 
            object_type not in ['question', 'answer']):
            return JsonResponse({
                'success': False,
                'error': 'Неверные данные'
            }, status=400)
        
        vote_value = 1 if vote_type == 'upvote' else -1
        
        profile = Profile.objects.get(user=request.user)
        if not profile:
            return JsonResponse({
                'success': False,
                'error': 'Профиль не найден'
            }, status=400)
        
        if object_type == 'question':
            question = get_object_or_404(Question, id=object_id)
            
            existing_vote = QuestionVote.objects.filter(
                profile=profile,
                question=question
            ).first()
            
            if existing_vote:
                if existing_vote.value == vote_value:
                    existing_vote.delete()
                    user_vote = None
                else:
                    existing_vote.value = vote_value
                    existing_vote.save()
                    user_vote = vote_type
            else:
                QuestionVote.objects.create(
                    profile=profile,
                    question=question,
                    value=vote_value
                )
                user_vote = vote_type
                question.refresh_from_db()
        
            return JsonResponse({
                'success': True,
                'new_rating': question.vote_sum,
                'user_vote': user_vote
            })
        else:
            answer = get_object_or_404(Answer, id=object_id)
            
            existing_vote = AnswerVote.objects.filter(
                profile=profile,
                answer=answer
            ).first()
            
            if existing_vote:
                if existing_vote.value == vote_value:
                    existing_vote.delete()
                    user_vote = None
                else:
                    existing_vote.value = vote_value
                    existing_vote.save()
                    user_vote = vote_type
            else:
                AnswerVote.objects.create(
                    profile=profile,
                    answer=answer,
                    value=vote_value
                )
                user_vote = vote_type
                answer.refresh_from_db()
        
            return JsonResponse({
                'success': True,
                'new_rating': answer.vote_sum,
                'user_vote': user_vote
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
def answer_accept(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    if answer.question.profile.user != request.user:
        return HttpResponseForbidden()
    
    answer.is_correct = not answer.is_correct
    answer.save()
    return JsonResponse({'success': True,
                         'is_correct': answer.is_correct})