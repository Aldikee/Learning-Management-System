from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    raise forms.ValidationError("Invalid login credentials for admin account.")

                elif not user.is_staff:
                    raise forms.ValidationError("Invalid login credentials for student account.")

        return super().clean()


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label='First Name', max_length=30,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', max_length=30,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=True)
    email = forms.EmailField(label='Email', widget=forms.EmailInput(
        attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(
        attrs={'autofocus': 'True', 'autocomplete': 'current-password', 'class': 'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'current-password', 'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'current-password', 'class': 'form-control'}))

class UnitFileForm(forms.Form):
    file = forms.FileField()