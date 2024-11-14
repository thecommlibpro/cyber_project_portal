from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from django.utils import timezone
from .forms import LogForm
from .models import EntryLog, Member
from django.db import IntegrityError


@staff_member_required
def daily_log(request):
    message = ""
    error = ""

    if request.method == "POST":
        form = LogForm(request.POST)
        if form.is_valid():
            member_id = form.cleaned_data['member_id']
            library = form.cleaned_data['library']

            # Get or create the member instance
            member = Member.objects.filter(member_id=member_id).first()

            if not member:
                return render(
                    request,
                    template_name='log.html',
                    context={'form': form, 'error': 'Member not found.'},
                    status=404,
                )

            # Check if entry already exists for today
            today = timezone.now().date()
            previous_entry = EntryLog.objects.filter(member=member, library=library, entered_date=today).first()

            if previous_entry:
                error = f"Member {member_id} already logged in today at {previous_entry.entered_time}"
            else:
                # If it doesn't exist, create a new entry
                try:
                    EntryLog.objects.create(member=member, library=library, entered_date=today)
                    message = "Member logged in."
                except IntegrityError:
                    error = "Failed to create entry due to a conflict."

    else:
        form = LogForm()

    return render(request, 'log.html', {'form': form, 'message': message, 'error': error})
