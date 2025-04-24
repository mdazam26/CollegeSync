from django import forms
from .models import College

class CollegeForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
        required=True
    )

    class Meta:
        model = College
        fields = [
            'institute_name', 'institute_address', 'institute_email', 
            'institute_number', 'admin_name', 'admin_number', 
            'admin_email', 'admin_username', 'admin_password'
        ]

    # You can add additional validations here if needed
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
