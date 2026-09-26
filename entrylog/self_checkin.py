import logging

from django.db import transaction
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from members.models import Member
from slots.models import LibraryNames

from .external import update_koha
from .models import EntryLog

logger = logging.getLogger(__name__)


def _library_choices():
    return list(LibraryNames.choices)


def _valid_library(value):
    return value in {choice[0] for choice in LibraryNames.choices}


def _normalise_member_id(value):
    return (value or "").strip().upper()


def _result_context(libraries, selected_library="", member_id="", success="", error=""):
    return {
        "libraries": libraries,
        "selected_library": selected_library,
        "member_id": member_id,
        "success": success,
        "error": error,
    }


@ensure_csrf_cookie
def self_checkin(request):
    """Render and process the member self-check-in page.

    This view deliberately reuses the existing Member.get() and EntryLog
    models, so self check-in remains in the same attendance system as staff
    entry. Put this route behind kiosk/network access controls before making
    it available outside the library network.
    """
    libraries = _library_choices()

    if request.method == "GET":
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(libraries),
        )

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    member_id = _normalise_member_id(request.POST.get("member_id"))
    library = (request.POST.get("library") or "").strip()

    if not member_id:
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(libraries, library, error="Please enter or scan your member ID."),
            status=400,
        )

    if not _valid_library(library):
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(libraries, error="Please select a valid library."),
            status=400,
        )

    try:
        member = Member.get(member_id)
    except Exception:
        logger.exception("Member lookup failed for self check-in: %s", member_id)
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(
                libraries,
                library,
                error="The member system is temporarily unavailable. Please ask staff for help.",
            ),
            status=503,
        )

    if not member:
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(libraries, library, error="Member ID not found. Please ask staff for help."),
            status=404,
        )

    if member.is_suspended:
        return render(
            request,
            "entrylog/self_checkin.html",
            _result_context(
                libraries,
                library,
                error="This membership is suspended or retired. Please ask staff for help.",
            ),
            status=403,
        )

    today = timezone.localdate()

    # Keep the check and create operation together. The existing model has no
    # database uniqueness constraint, so a unique constraint should be added
    # after checking and cleaning any historical duplicate rows.
    with transaction.atomic():
        previous_entry = (
            EntryLog.objects.select_for_update()
            .filter(member=member, library=library, entered_date=today)
            .first()
        )

        if previous_entry:
            return render(
                request,
                "entrylog/self_checkin.html",
                _result_context(
                    libraries,
                    library,
                    error=(
                        f"You are already checked in today at "
                        f"{previous_entry.entered_time.strftime('%H:%M')}."
                    ),
                ),
                status=409,
            )

        entry = EntryLog.objects.create(member=member, library=library)

        if member.first_login_at is None:
            member.first_login_at = entry.timestamp
            member.save(update_fields=["first_login_at"])

    # Koha is an external dependency. Do not undo the local attendance record
    # if Koha is temporarily unavailable; log the failure for staff follow-up.
    try:
        update_koha(member_id)
    except Exception:
        logger.exception("Failed to update Koha after self check-in for %s", member_id)

    display_name = (member.member_name or member_id).strip()
    return render(
        request,
        "entrylog/self_checkin.html",
        _result_context(
            libraries,
            library,
            success=f"Check-in successful. Welcome, {display_name}.",
        ),
    )
