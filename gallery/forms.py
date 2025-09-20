from django import forms
from .models import Category, Gallery, Contact


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['category', 'image', 'title', 'description']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']

class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }

    def clean_website(self):
        data = self.cleaned_data.get('website')
        if data:
            raise forms.ValidationError("Bot detected.")
        return data
