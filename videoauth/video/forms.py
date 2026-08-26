from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import os
from .models import Video

ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v']

def validate_video_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

class VideoForm(forms.ModelForm):
    file = forms.FileField(
        validators=[validate_video_extension],
        widget=forms.FileInput(attrs={
            'class': 'form-control file-input',
            'id': 'id_file',
            'accept': 'video/*'
        })
    )


    class Meta:
        model = Video
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter video title (e.g. Security Footage 08-09-2026)',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter optional description or notes about the video...',
                'rows': 3
            }),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'you@example.com'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }