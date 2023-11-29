from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.core.exceptions import ValidationError
# from django.utils import timezone

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'location',
            'category',
            'pub_date',
            'image',
        )
        widgets = {'pub_date': forms.DateTimeInput({'type': 'datetime-local'})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )
