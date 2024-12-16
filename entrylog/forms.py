from django import forms

from entrylog.models import EntryLog
from slots.forms import MemberWidget
from slots.models import LibraryNames

class LogForm(forms.Form):
    member_id = forms.CharField(label="Member ID", max_length=100, required=True)
    library = forms.ChoiceField(label="Select Library", choices=LibraryNames.choices, required=True)


class LogAdminForm(forms.ModelForm):
    class Meta:
        model = EntryLog
        fields = "__all__"
        widgets = {
            "member": MemberWidget,
        }
