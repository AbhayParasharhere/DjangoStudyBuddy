from django.forms import ModelForm, Textarea
from .models import Room
from django.contrib.auth.models import User


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']
        widgets = {
            'description': Textarea(attrs={'placeholder': 'Write about your study group...'})
        }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
