
from django.contrib import admin
from .models import Announcement, Files, Comments, OneTimeCode

admin.site.register(Announcement)
admin.site.register(Comments)
admin.site.register(Files)
admin.site.register(OneTimeCode)
