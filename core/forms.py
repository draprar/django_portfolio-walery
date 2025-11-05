from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    # honeypot
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name / Imię'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message / Wiadomość', 'rows': 5}),
        }

    def clean_website(self):
        data = self.cleaned_data.get('website')
        if data:
            raise forms.ValidationError("Bot detected.")
        return data

