from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class BootstrapFormMixin:
    """manage/form.html renders `{{ field }}` directly (no crispy-forms), so
    widgets need their Bootstrap classes set explicitly -- this does it for
    every field automatically instead of repeating it per-field per-form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = (existing + ' form-check-input').strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = (existing + ' form-select').strip()
            else:
                widget.attrs['class'] = (existing + ' form-control').strip()


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'emp_id', 'campus', 'dept_code')


class UserProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'campus', 'dept_code', 'designation_code')
