"""Admin site."""
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.contrib.auth.models import Group
from .models import GreenlightConfig, WebHook, DiscordMessageConfig

@admin.register(GreenlightConfig)
class GreenlightConfigAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Messages', {
            'fields': ('green_message', 'yellow_message', 'red_message'),
        }),
        ('Coverage', {
            'fields': ('staging_systems',),
            'description': 'Select EVE systems your defensive umbrella is staged in.',
        }),
    )

    def changelist_view(self, request, extra_context=None):
        obj = GreenlightConfig.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:greenlight_greenlightconfig_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    

class DiscordMessageConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build combined choices
        base_choices = [
            ("", "None"),
            ("@everyone", "@everyone"),
            ("@here", "@here"),
        ]
        group_choices = [('@' + str(g.name), '@' + str(g.name)) for g in Group.objects.all()]
        full_choices = base_choices + group_choices

        for field in [
            "green_ping_target",
            "yellow_ping_target",
            "red_ping_target",
            "doctrine_ping_target"
        ]:
            self.fields[field] = forms.ChoiceField(choices=full_choices, required=False)

    class Meta:
        model = DiscordMessageConfig
        fields = "__all__"

@admin.register(DiscordMessageConfig)
class DiscordMessageConfigAdmin(admin.ModelAdmin):
    form = DiscordMessageConfigForm
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ("Green Alert", {
            'fields': ('green_message', 'green_ping_target'),
        }),
        ("Yellow Alert", {
            'fields': ('yellow_message', 'yellow_ping_target'),
        }),
        ("Red Alert", {
            'fields': ('red_message', 'red_ping_target'),
        }),
        ("Doctrine / FC Change", {
            'fields': ('doctrine_change_message', 'doctrine_ping_target'),
        }),
    )

    def changelist_view(self, request, extra_context=None):
        obj = DiscordMessageConfig.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:greenlight_discordmessageconfig_change', args=[obj.pk]))
        messages.warning(request, "No DiscordMessageConfig found. Please create one.")
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        # Only allow adding one config
        return not DiscordMessageConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class WebHookAdmin(admin.ModelAdmin):
    list_display=('name',)

admin.site.register(WebHook, WebHookAdmin)