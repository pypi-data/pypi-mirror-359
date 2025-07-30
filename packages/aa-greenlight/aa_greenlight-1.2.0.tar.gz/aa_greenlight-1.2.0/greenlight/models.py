"""Models."""
from django.db import models
from eveuniverse.models import EveSolarSystem
from django.urls import reverse
from allianceauth.eveonline.models import EveCharacter
from fittings.models import Doctrine
from django.contrib.auth.models import Group



class WebHook(models.Model):
    """Discord Webhook for pings"""
    name = models.CharField(max_length=150)
    webhook_url = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class GreenlightConfig(models.Model):
    """Fleet configuration (singleton-style)"""
    FLEET_STATUS_CHOICES = [
        ("green", "🟢 Green - All clear"),
        ("yellow", "🟡 Yellow - Be ready"),
        ("red", "🔴 Red - Action needed"),
    ]

    name = models.CharField(max_length=100, default="default", unique=True)

    # Alert Messages
    green_message = models.TextField(default="🟢 **GREEN ALERT!** All clear.")
    yellow_message = models.TextField(default="🟡 **YELLOW ALERT!** Be ready.")
    red_message = models.TextField(default="🔴 **RED ALERT!** Action needed!")

    # Fleet Control Fields
    fleet_status = models.CharField(
        max_length=10, choices=FLEET_STATUS_CHOICES, default="green"
    )
    staging_systems = models.ManyToManyField(
        EveSolarSystem,
        blank=True,
        help_text="Staging systems of umbrella.",
    )

    # NEW FIELDS BELOW
    current_fc = models.ForeignKey(
        EveCharacter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Currently assigned FC",
    )

    current_doctrine = models.ForeignKey(
        Doctrine,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Doctrine for current fleet",
    )

    fleet_status = models.CharField(
        max_length=10,
        choices=[("green", "Green"), ("yellow", "Yellow"), ("red", "Red")],
        default="green",
    )

    def __str__(self):
        return f"Greenlight Config: {self.name}"


class General(models.Model):
    """A meta model for app permissions."""
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"), ("can_manage_fleets", "Can manage fleets"))


class DiscordMessageConfig(models.Model):
    """Singleton-style config for Discord messages on events."""
    green_gif_url = models.URLField(blank=True, help_text="Optional GIF for green status")
    yellow_gif_url = models.URLField(blank=True)
    red_gif_url = models.URLField(blank=True)
    doctrine_gif_url = models.URLField(blank=True)

    PING_CHOICES = [
        ("", "None"),
        ("@everyone", "@everyone"),
        ("@here", "@here"),
    ]

    name = models.CharField(max_length=100, default="default", unique=True)

    # Fleet status messages
    green_message = models.TextField(default="🟢 **GREEN ALERT!** All clear.")
    green_ping_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="Select @everyone, @here, or a group name from AllianceAuth."
    )

    yellow_message = models.TextField(default="🟡 **YELLOW ALERT!** Be ready.")
    yellow_ping_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="Select @everyone, @here, or a group name from AllianceAuth."
    )

    red_message = models.TextField(default="🔴 **RED ALERT!** Action needed!")
    red_ping_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="Select @everyone, @here, or a group name from AllianceAuth."
    )

    # Doctrine/FC change message
    doctrine_change_message = models.TextField(default="🛠️ **Fleet composition updated.**")
    doctrine_ping_target = models.CharField(
        max_length=100,
        blank=True,
        help_text="Select @everyone, @here, or a group name from AllianceAuth."
    )

    def __str__(self):
        return f"Discord Message Config: {self.name}"


