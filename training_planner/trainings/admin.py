from django.contrib import admin

# Register your models here.
from .models import Address, Location, Restriction, TargetGroup, Training

admin.site.register(Training)
admin.site.register(TargetGroup)
admin.site.register(Location)
admin.site.register(Address)
admin.site.register(Restriction)
