from django import forms

class EmailForm(forms.Form):
    # This replaces sender, subject, and body fields entirely
    email_file = forms.FileField(
        label="Upload Email File",
        widget=forms.FileInput(attrs={'accept': '.eml'}) # Restricts picker to .eml files
    )