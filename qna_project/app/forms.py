from django import forms
from django.contrib.auth import authenticate
from .models import Profile, Question, Answer, Tag
from django.contrib.auth.models import User
import os

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Login',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'Enter your username',
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Enter your password'
        }),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        # Check authentication
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
            cleaned_data['user'] = user
        
        return cleaned_data
     
class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'Enter your username',
        })
    )
    
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Enter your email',
        })
    )
    
    nickname = forms.CharField(
        label='Nickname',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'nickname',
            'placeholder': 'Enter your nickname',
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Enter your password'
        }),
        required=True
    )
    
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password2',
            'placeholder': 'Repeat your password'
        }),
        required=True
    )
    
    avatar = forms.ImageField(
        label='Avatar (optional)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control w-75',
            'id': 'avatar',
            'accept': 'image/*'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")
        
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError("Username already exists")
        
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("Account with this email already exists")
        
        avatar = cleaned_data.get('avatar')
        if avatar and avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Avatar size must be less than 5MB")
        
        ext = os.path.splitext(avatar.name)[1]
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if ext.lower() not in valid_extensions:
            raise forms.ValidationError("Unsupported file extension.")
        
        return cleaned_data
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'avatar']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate User fields with current values
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
    
    username = forms.CharField(
        label='Username',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'Enter your username',
        })
    )
    
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Enter your email',
        })
    )
    
    nickname = forms.CharField(
        label='Nickname',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'nickname',
            'placeholder': 'Enter your nickname',
        })
    )
    
    avatar = forms.ImageField(
        label='Avatar (optional)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control w-75',
            'id': 'avatar',
            'accept': 'image/*'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if cleaned_data.get('username') and User.objects.filter(username=cleaned_data.get('username')).exclude(username=self.instance.user.username).exists():
            raise forms.ValidationError("Username already exists")
        
        if cleaned_data.get('email') and User.objects.filter(email=cleaned_data.get('email')).exclude(email=self.instance.user.email).exists():
            raise forms.ValidationError("Account with this email already exists")
        
        if cleaned_data.get('avatar'):
            avatar = cleaned_data.get('avatar')
            if avatar and avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Avatar size must be less than 5MB")
            
            ext = os.path.splitext(avatar.name)[1]
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            if ext.lower() not in valid_extensions:
                raise forms.ValidationError("Unsupported file extension.")
        
        return cleaned_data
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        profile.user.username = self.cleaned_data['username']
        profile.user.email = self.cleaned_data['email']
        profile.user.save()
        
        return profile
    
class NewQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        
    title = forms.CharField(
        label='Title',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the title of your question',
        })
    )
    
    text = forms.CharField(
        label='Text',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the text of your question',
        }),
        required=True
    )
    
    tags = forms.CharField(
        label='Tags',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'tag1, tag2, tag3...',
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not cleaned_data.get('tags'):
            cleaned_data['tags'] = ''
        else:
            for tag in cleaned_data['tags'].split(','):
                if tag.strip() == '' or ' ' in tag.strip():
                    raise forms.ValidationError("Invalid tags format")
                
            cleaned_data['tags'] = [tag.strip() for tag in cleaned_data['tags'].split(',')]
        
        return cleaned_data
    
    def save(self, commit=True, profile=None):
        if not profile:
            raise ValueError("Profile is required")
        
        question = super().save(commit=False)
        question.profile = profile
        question.save()
        
        for tag_name in self.cleaned_data['tags']:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)
        
        return question
        
class NewAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        
    text = forms.CharField(
        label='Text',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer...',
            'rows': '5'
        }),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not cleaned_data.get('text'):
            raise forms.ValidationError("Answer text is required")
        
        return cleaned_data
    
    def save(self, commit=True, question=None, profile=None):
        if not question:
            raise ValueError("Question is required")
        
        answer = super().save(commit=False)
        answer.question = question
        answer.profile = profile
        answer.save()
        
        return answer
        