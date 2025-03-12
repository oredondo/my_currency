from django.contrib import admin

from .models import Credentials


# Register your models here.
class CredentialsAdmin(admin.ModelAdmin):
    model = Credentials
    list_display = (
        'name',
        'url',
        'token',
        'priority',
        'enabled')


admin.site.register(Credentials, CredentialsAdmin)
