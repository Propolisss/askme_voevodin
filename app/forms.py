import os

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.context_processors import request

from app.models import Profile, Answer, Question, Tag


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Login',
        'autofocus': True,
        'required': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'required': True,
    }))

    def clean_username(self):
        return self.cleaned_data['username'].strip()


class UserForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'required': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'required': True,
    }))
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repeated password',
        'required': True,
    }))
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_email(self):
        return self.cleaned_data['email'].strip()

    def clean_username(self):
        return self.cleaned_data['username'].strip()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['password'] != cleaned_data['repeat_password']:
            raise ValidationError('Passwords do not match')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()

        if self.cleaned_data['avatar']:
            ext = os.path.splitext(self.cleaned_data['avatar'].name)[1]
            self.cleaned_data['avatar'].name = f"{user.username}_avatar{ext}"
        Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'])

        return user


class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer here...'
        })
    )

    def __init__(self, user, question_id, **kwargs):
        self._user = user
        self._question_id = question_id
        super().__init__(**kwargs)

    class Meta:
        model = Answer
        fields = ('text',)

    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.question_id = self._question_id
        answer.profile = self._user.profile
        answer.save()

        return answer


class SettingsForm(forms.ModelForm):
    def __init__(self, user, **kwargs):
        self._user = user
        super().__init__(**kwargs)
        self.fields['username'].initial = self._user.username
        self.fields['email'].initial = self._user.email
        self.fields['avatar'].initial = self._user.profile.avatar

    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'required': True,
    }))
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={}))

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if 'username' in self.changed_data and User.objects.filter(username=username).exists():
            raise ValidationError('A user with that username already exists.')
        return username

    def clean_email(self):
        return self.cleaned_data['email'].strip()

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        if 'username' in self.changed_data:
            self._user.username = self.cleaned_data['username']
            old_avatar = self._user.profile.avatar
            if old_avatar:
                old_avatar_path = old_avatar.path
                ext = os.path.splitext(old_avatar_path)[1]
                new_avatar_name = f"{self.cleaned_data['username']}_avatar{ext}"
                new_avatar_path = os.path.join(os.path.dirname(old_avatar_path), new_avatar_name)
                os.rename(old_avatar_path, new_avatar_path)
                self._user.profile.avatar.name = os.path.join(os.path.dirname(old_avatar.name), new_avatar_name)

        if 'email' in self.changed_data:
            self._user.email = self.cleaned_data['email']

        print(f'before: {self._user.profile.avatar.url}')
        if 'avatar' in self.changed_data:
            old_avatar = self._user.profile.avatar
            if old_avatar:
                old_avatar_path = old_avatar.path
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
                self._user.profile.avatar = None
            if self.cleaned_data['avatar']:
                self._user.profile.avatar = self.cleaned_data['avatar']
                ext = os.path.splitext(self._user.profile.avatar.path)[1]
                self._user.profile.avatar.name = os.path.join(os.path.dirname(self.cleaned_data['avatar'].name),
                                                              f"{self._user.username}_avatar{ext}")
        self._user.save()
        self._user.profile.save()
        print(f'after: {self._user.profile.avatar.url}')
        print(f'{self._user.profile.avatar.path}')

        return self._user


class QuestionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your title here...',
        'style': "height: 50px; max-height: 100px;",
        'required': True,
    }))
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your question here...',
        'style': "height: 200px; max-height: 400px;",
        'required': True,
    }))
    tags = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your tags here...',
        'style': "height: 50px; max-height: 100px;",
        'required': True,
    }))

    def __init__(self, user, **kwargs):
        self._user = user
        super().__init__(**kwargs)

    class Meta:
        model = Question
        fields = ('title', 'text')

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean_text(self):
        return self.cleaned_data['text'].strip()

    def clean_tags(self):
        tags_list = [tag.strip() for tag in self.cleaned_data['tags'].lower().strip().replace(',', ' ').split(' ') if
                     tag.strip()]
        return tags_list

    def save(self, commit=True):
        question = super().save(commit=False)
        question.profile = self._user.profile
        question.save()
        self.save_m2m()

        for tag_name in self.cleaned_data['tags']:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)

        return question
