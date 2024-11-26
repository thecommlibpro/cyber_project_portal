from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import LogForm
from .models import EntryLog, Member
from django.db import IntegrityError


@staff_member_required
def daily_log(request):
    context = {
        "form": LogForm(),
        "message": '',
        "error": '',
        "warning": '',
    }

    if request.method == "POST":
        form = LogForm(request.POST)
        if form.is_valid():
            context['form'] = form
            member_id = form.cleaned_data['member_id']
            library = form.cleaned_data['library']

            # Get or create the member instance
            member = Member.objects.filter(member_id=member_id).first()

            if not member:
                context['error'] = "Member not found"
                return render(
                    request,
                    template_name='log.html',
                    context=context,
                    status=404,
                )

            context['member_id'] = member_id
            # Check if entry already exists for today
            today = timezone.now().date()
            previous_entry = EntryLog.objects.filter(member=member, library=library, entered_date=today).first()

            if previous_entry:
                context['error'] = f"Member {member_id} already logged in today at {previous_entry.entered_time.strftime('%H:%M')}"
            else:
                # If it doesn't exist, create a new entry
                try:
                    EntryLog.objects.create(member=member, library=library, entered_date=today)

                    context['message'] = "Member logged in."
                    if EntryLog.objects.filter(member=member).count() == 1:
                        member.first_login_at = datetime.now()
                        member.save()

                        context['show_sticker_message'] = True
                except IntegrityError:
                    context['error'] = "Failed to create entry due to a conflict."

    return render(request, 'log.html', context)


@staff_member_required
def mark_sticker(request):
    if request.method == "POST":
        member_id = request.POST.get('member_id')
        sticker_given = request.POST.get('sticker_given')
        member = Member.objects.filter(member_id=member_id).first()

        member.is_sticker_received = sticker_given == 'true'
        member.save()

        return redirect(to='daily_log')
