from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth.models import User
from .models import Review


class RegisterrForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Passwords do not match.')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Email is already registered.')
        return email



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']

    rating = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Rating (1-5)"
    )
    review_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Review",
        required=False
    )

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        }),
        required=True,
    )