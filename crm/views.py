import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import LeadForm, OpenHouseForm, PropertyVisitForm
from .models import Lead, PropertyVisit


def lead_list(request):
    leads = Lead.objects.all().order_by("-created_at")
    lead_categories = ["FSBO", "Expired", "Seller", "Buyer", "Open House"]
    lead_statuses = ["new", "reached_out", "contacted"]
    client_categories = ["Seller", "Buyer"]
    client_statuses = ["active", "closing", "lost"]

    return render(
        request,
        "crm/lead_list.html",
        {
            "leads": leads,
            "lead_categories": lead_categories,
            "lead_statuses": lead_statuses,
            "client_categories": client_categories,
            "client_statuses": client_statuses,
        },
    )


import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def update_lead_status(request, pk):
    try:
        data = json.loads(request.body)
        new_status = data.get("status")
        new_type = data.get("lead_type")

        if not new_status or not new_type:
            return JsonResponse({"error": "Missing status or type"}, status=400)

        lead = Lead.objects.get(pk=pk)
        lead.status = new_status
        lead.lead_type = new_type
        lead.save()
        return JsonResponse({"success": True})
    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


import logging

logger = logging.getLogger(__name__)


from django.core.files.storage import default_storage


def lead_create(request):
    if request.method == "POST":
        form = LeadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            if "image" in request.FILES:
                uploaded_file = request.FILES["image"]
                path = default_storage.save(
                    f"lead_images/{uploaded_file.name}", uploaded_file
                )
                instance.image = path
            instance.save()
            return redirect("lead_list")
    else:
        form = LeadForm()
    return render(request, "crm/lead_form.html", {"form": form})


def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadForm(request.POST or None, request.FILES or None, instance=lead)
    if form.is_valid():
        form.save()
        return redirect("lead_list")
    return render(request, "crm/lead_form.html", {"form": form})


def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)

    if request.method == "POST":
        form = PropertyVisitForm(request.POST, request.FILES)
        if lead.lead_type == "Buyer" and form.is_valid():
            visit = form.save(commit=False)  # Get the visit instance
            visit.lead = lead  # Assign the related lead
            visit.save()  # Save the visit (image will save here because form handled it)
            return redirect("lead_detail", pk=lead.pk)
    else:
        form = PropertyVisitForm()

    visit_statuses = ["scheduled", "visited", "liked", "disliked"]

    return render(
        request,
        "crm/lead_detail.html",
        {"lead": lead, "form": form, "visit_statuses": visit_statuses},
    )


import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import PropertyVisit


@csrf_exempt
def update_visit_status(request, pk):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            visit = PropertyVisit.objects.get(pk=pk)
            new_status = data.get("status")
            if new_status in dict(PropertyVisit.STATUS_CHOICES):
                visit.status = new_status
                visit.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Invalid status"}, status=400)
        except PropertyVisit.DoesNotExist:
            return JsonResponse({"error": "Visit not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def delete_visit(request, pk):
    try:
        visit = PropertyVisit.objects.get(pk=pk)
        visit.delete()
        return JsonResponse({"success": True})
    except PropertyVisit.DoesNotExist:
        return JsonResponse({"error": "Visit not found"}, status=404)


@csrf_exempt
@require_POST
def update_visit_notes(request, pk):
    try:
        data = json.loads(request.body)
        visit = PropertyVisit.objects.get(pk=pk)
        visit.notes = data.get("notes", visit.notes)
        visit.save()
        return JsonResponse({"success": True})
    except PropertyVisit.DoesNotExist:
        return JsonResponse({"error": "Visit not found"}, status=404)


from django.shortcuts import get_object_or_404, redirect, render

from .forms import OpenHouseSignInForm
from .models import OpenHouse


def open_house_sign_in(request, pk):
    open_house = get_object_or_404(OpenHouse, pk=pk)
    submitted = False

    if request.method == "POST":
        form = OpenHouseSignInForm(request.POST)
        if form.is_valid():
            sign_in = form.save(commit=False)
            sign_in.open_house = open_house
            sign_in.save()
            form = OpenHouseSignInForm()  # reset form
            submitted = True
    else:
        form = OpenHouseSignInForm()

    return render(
        request,
        "crm/open_house_sign_in.html",
        {"form": form, "open_house": open_house, "submitted": submitted},
    )


def open_house_thank_you(request):
    return render(request, "crm/open_house_thank_you.html")


def create_open_house(request):
    if request.method == "POST":
        print(request.FILES)  # ✅ TEMPORARY - See if files are uploading
        form = OpenHouseForm(
            request.POST, request.FILES
        )  # ✅ make sure request.FILES is included
        if form.is_valid():
            form.save()
            return redirect("open_house_list")
    else:
        form = OpenHouseForm()
    return render(request, "crm/open_house_create.html", {"form": form})


def open_house_list(request):
    events = OpenHouse.objects.order_by("-date")
    return render(request, "crm/open_house.html", {"events": events})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def delete_lead(request, pk):
    if request.method == "POST":
        try:
            Lead.objects.get(pk=pk).delete()
            return JsonResponse({"success": True})
        except Lead.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Lead not found"}, status=404
            )
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def create_open_house_for_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)

    if request.method == "POST":
        form = OpenHouseForm(request.POST)
        if form.is_valid():
            open_house = form.save(commit=False)
            open_house.lead = lead

            # ✅ Only assign agent if user is authenticated
            if request.user.is_authenticated:
                open_house.agent = request.user

            open_house.save()
            return redirect("lead_detail", pk=lead.id)

    else:
        form = OpenHouseForm()

    return render(request, "crm/open_house_create.html", {"form": form, "lead": lead})


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect


def delete_open_house(request, pk):
    open_house = get_object_or_404(OpenHouse, pk=pk)
    lead_id = open_house.lead.id if open_house.lead else None
    open_house.delete()
    messages.success(request, "🗑️ Open House deleted successfully.")

    if lead_id:
        return redirect("lead_detail", pk=lead_id)
    return redirect("open_house_list")


import io
from datetime import datetime

import pandas as pd
from django.http import HttpResponse

from .models import Lead


def export_new_leads(request):
    new_leads = Lead.objects.filter(status="new")

    lead_data = []
    for lead in new_leads:
        lead_info = {
            "Name": lead.name,
            "Phone Number": lead.phone_number,
            "Email": lead.email,
            "Category": lead.lead_type,
        }

        # 📍 Only include Address for FSBO, Expired, Seller
        if lead.lead_type in ["FSBO", "Expired", "Seller"]:
            lead_info["Address"] = lead.address

        lead_data.append(lead_info)

    df = pd.DataFrame(lead_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="New Leads", index=False)

        # 📏 Auto-fit columns based on content
        worksheet = writer.sheets["New Leads"]
        for column_cells in worksheet.columns:
            length = max(
                len(str(cell.value)) if cell.value else 0 for cell in column_cells
            )
            column_letter = column_cells[0].column_letter
            worksheet.column_dimensions[column_letter].width = length + 2

    output.seek(0)

    filename = f"new_leads_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


from django.shortcuts import get_object_or_404, redirect, render

from .forms import OpenHouseSignInForm
from .models import OpenHouse


def public_open_house_sign_in(request, event_id):
    open_house = get_object_or_404(OpenHouse, id=event_id)
    if request.method == "POST":
        form = OpenHouseSignInForm(request.POST)
        if form.is_valid():
            sign_in = form.save(commit=False)
            sign_in.open_house = open_house
            sign_in.save()
            return redirect("open_house_thank_you")  # ✅ Redirect to thank you
    else:
        form = OpenHouseSignInForm()
    return render(
        request,
        "crm/public_open_house_sign_in.html",
        {"form": form, "open_house": open_house},
    )


from django.shortcuts import get_object_or_404, render

from .models import OpenHouse


def open_house_detail(request, pk):
    open_house = get_object_or_404(OpenHouse, pk=pk)
    return render(request, "crm/open_house_detail.html", {"open_house": open_house})
