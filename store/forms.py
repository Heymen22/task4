from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'year', 'category', 'description', 'cover_url',
            'price', 'rent_price_2w', 'rent_price_1m', 'rent_price_3m',
            'status', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class BookQuickEditForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['price', 'rent_price_2w', 'rent_price_1m', 'rent_price_3m', 'status', 'is_active']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
