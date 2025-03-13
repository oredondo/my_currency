from django.contrib import admin

from .models import Credentials


# Register your models here.
class CredentialsAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Credentials model.
    Defines the display and behavior settings in the admin panel.
    """
    model = Credentials
    list_display = (
        'name',
        'url',
        'token',
        'priority',
        'enabled')


admin.site.register(Credentials, CredentialsAdmin)
