from django import forms

from slots.models import LibraryNames

class LogForm(forms.Form):
    member_id = forms.CharField(label="Member ID", max_length=100, required=True)
    library = forms.ChoiceField(label="Select Library", choices=LibraryNames.choices, required=True)
