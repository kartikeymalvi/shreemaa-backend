from django.contrib import admin
from .models import OrderReport, Firm, Location, Merchant,ProductModel, ColumnVisibilityPolicy,InvoiceShipment,InwardRecord,RefundRecord

# In sabko admin panel me dikhane ke liye register karna padta hai

admin.site.register(OrderReport)
admin.site.register(ProductModel)
admin.site.register(Firm)
admin.site.register(Location)
admin.site.register(Merchant)
admin.site.register(ColumnVisibilityPolicy)
# invoice shipment 
admin.site.register(InwardRecord)
admin.site.register(RefundRecord)


#------------invoice-shipment--------------------------


# --- INVOICE SHIPMENT ADMIN VIEW ---
@admin.register(InvoiceShipment)
class InvoiceShipmentAdmin(admin.ModelAdmin):
    # Admin panel ki table me konsi columns baahar hi dikhni chahiye
    list_display = ('order_id', 'txn_date', 'firm', 'seller_name', 'invoice_no', 'delivery_status', 'delivery_date')
    
    # Admin panel me kiske base par search karna hai
    search_fields = ('order_id', 'invoice_no', 'seller_name', 'firm')
    
    # Side me ek Filter ka box aa jayega
    list_filter = ('delivery_status', 'firm', 'location')
