from django.contrib import admin

# Register your models here.
from .models import Training, Location, Address, TargetGroup

admin.site.register(Training)
admin.site.register(TargetGroup)
admin.site.register(Location)
admin.site.register(Address)
