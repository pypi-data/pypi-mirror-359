import json
import requests
from .models import WebHook, DiscordMessageConfig, GreenlightConfig
from django.contrib.auth.models import Group

def resolve_ping_target(ping_value):
    if ping_value in ["@everyone", "@here", ""]:
        return ping_value
    elif ping_value.startswith("@"):
        group_name = ping_value[1:]
        try:
            group = Group.objects.get(name=group_name)
            if hasattr(group, "discordrole") and group.discordrole:
                return f"<@&{group.discordrole.discord_id}>"
            else:
                return f"@{group_name}"  # fallback as plain mention
        except Group.DoesNotExist:
            return f"@{group_name}"  # fallback
    return ""


def send_discord_message(event_type: str, config):
    """
    Send a Discord message based on the event type and current GreenlightConfig.
    event_type can be one of: 'green', 'yellow', 'red', 'doctrine'
    """

    try:
        fleet_config = GreenlightConfig.objects.first()
        msg_config = DiscordMessageConfig.objects.first()
        if not msg_config:
            return  # no config to send from

        # Map event_type to config fields
        ping_target = ""
        message = ""
        gif_url = ""
        if not fleet_config:
            return
        fc = ""
        doctrine = ""

        if event_type == "green":
            ping_target = resolve_ping_target(msg_config.green_ping_target)
            message = msg_config.green_message
            fc = fleet_config.current_fc
            doctrine = fleet_config.current_doctrine
            gif_url = msg_config.green_gif_url
        elif event_type == "yellow":
            ping_target = resolve_ping_target(msg_config.yellow_ping_target)
            message = msg_config.yellow_message
            fc = fleet_config.current_fc
            doctrine = fleet_config.current_doctrine
            gif_url = msg_config.yellow_gif_url
        elif event_type == "red":
            ping_target = resolve_ping_target(msg_config.red_ping_target)
            message = msg_config.red_message
            gif_url = msg_config.red_gif_url
        elif event_type == "doctrine":
            ping_target = resolve_ping_target(msg_config.doctrine_ping_target)
            message = msg_config.doctrine_message
            gif_url = msg_config.doctrine_gif_url
        # Construct the message
        parts = [message]

        if fc:
            parts.append(str(fc)) 

        if doctrine:
            parts.append(str(doctrine))

        full_msg = "\n".join(parts)

        embed = {
            "description": full_msg,
        }

        if gif_url:
            embed["image"] = {"url": gif_url}


        # Send to all webhooks
        for webhook in WebHook.objects.all():
            payload = {
                "content": ping_target,
                "embeds": [embed]
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(webhook.webhook_url, headers=headers, data=json.dumps(payload))
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"[Discord Ping] Failed to send to {webhook.name}: {e}")

    except Exception as e:
        print(f"[Discord Ping] Unexpected error: {e}")
