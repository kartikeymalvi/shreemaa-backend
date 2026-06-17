from django.contrib import admin
from .models import OrderReport, Firm, Location, Merchant, ColumnVisibilityPolicy

# In sabko admin panel me dikhane ke liye register karna padta hai
admin.site.register(OrderReport)
admin.site.register(Firm)
admin.site.register(Location)
admin.site.register(Merchant)
admin.site.register(ColumnVisibilityPolicy)