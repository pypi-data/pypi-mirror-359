"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import GreenlightConfig
from django.contrib.auth.models import Group
from fittings.models import Doctrine
from allianceauth.eveonline.models import EveCharacter
from django.views.decorators.http import require_POST
from .utils import send_discord_message


@login_required
def status_view(request):
    config = GreenlightConfig.objects.first()
    return render(request, "greenlight/status_panel.html", {
        "config": config
    })


@login_required
@permission_required("greenlight.can_manage_fleets", raise_exception=True)
def fc_panel(request):
    config = GreenlightConfig.objects.first()
    if request.method == "POST":
        prev_status = config.fleet_status
        prev_fc = config.current_fc
        prev_doctrine = config.current_doctrine

        # --- handle POSTed fields ---
        config.fleet_status = request.POST.get("fleet_status", config.fleet_status)
        doctrine_id = request.POST.get("doctrine")
        fc_id = request.POST.get("fc")

        if doctrine_id:
            config.current_doctrine_id = doctrine_id
        if fc_id:
            config.current_fc_id = fc_id

        config.save()

        # --- send status update ping ---
        if config.fleet_status != prev_status:
            send_discord_message(config.fleet_status, config)

        # --- send doctrine/FC update ping if not red ---
        elif (
            config.fleet_status != "red" and
            (config.current_doctrine_id != getattr(prev_doctrine, 'id', None) or
             config.current_fc_id != getattr(prev_fc, 'id', None))
        ):
            send_discord_message("doctrine", config)

        messages.success(request, "Fleet status updated.")
        return redirect("greenlight:fc_panel")

    doctrines = Doctrine.objects.all()
    characters = EveCharacter.objects.filter(character_ownership__user=request.user)


    return render(request, "greenlight/fc_panel.html", {
        "config": config,
        "doctrines": doctrines,
        "characters": characters,
    })


def get_current_config():
    return GreenlightConfig.objects.first()

@login_required
@permission_required("greenlight.basic_access")
def greenlight_status(request):
    config = get_current_config()
    context = {
        "config": config,
        "fleet_status": config.fleet_status,  # Assuming this is a field
        "fc_name": config.fc_character_name,     # Assuming this is a field
        "doctrine_link": config.doctrine_url(),  # You'll create this method
    }
    return render(request, "greenlight/status.html", context)

