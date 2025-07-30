"""App Configuration"""

# Django
from django.apps import AppConfig

# AA greenlight App
from greenlight import __version__


class greenlightConfig(AppConfig):
    """App Config"""

    name = "greenlight"
    label = "greenlight"
    verbose_name = f"greenlight App v{__version__}"
