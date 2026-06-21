from django.contrib import admin
from . models import *
from django.contrib.auth.admin import UserAdmin


admin.site.register(User, UserAdmin)
admin.site.register(Feedback)
admin.site.register(BookedRide)
admin.site.register(Payment)
admin.site.register(Offer_ride)
