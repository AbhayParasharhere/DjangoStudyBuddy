from django.forms import ModelForm, Textarea
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'username',
                  'password1', 'password2']


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
        fields = ['name', 'email', 'username', 'avatar', 'bio']
