from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum


class OrderReport(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Delivered', 'Delivered'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=100)
    txn_date = models.DateField(null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)
    day = models.CharField(max_length=20, null=True, blank=True)
    txn_detail = models.CharField(max_length=255, null=True, blank=True)
    
    # Dropdown based fields (Stored as text in DB)
    merchant = models.CharField(max_length=100, null=True, blank=True)
    merchant_id = models.CharField(max_length=100, null=True, blank=True)
    firm = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    
    # Merged Field
    asin_fsn = models.CharField(max_length=100, null=True, blank=True)
    
    model_name = models.CharField(max_length=255, null=True, blank=True)
    model_no = models.CharField(max_length=255, null=True, blank=True)
    
    # New Field
    order_status = models.CharField(max_length=50, default="Open", null=True, blank=True)
    
    # Number Fields
    order_qty = models.IntegerField(default=0)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # New Auto-calculated field
    card_offer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('order_id', 'asin_fsn')

    def __str__(self):
        return f"{self.order_id} - {self.asin_fsn}"
    

    

# Updated Column Visibility Policy
class ColumnVisibilityPolicy(models.Model):
    policy_name = models.CharField(max_length=50, unique=True, default="user_view_policy")
    
    # --- COMMON FIELDS (Dono Pages me hain) ---
    show_order_id = models.BooleanField(default=True)
    show_txn_date = models.BooleanField(default=True)
    show_firm = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_asin_fsn = models.BooleanField(default=True)
    show_model_name = models.BooleanField(default=True)
    show_model_no = models.BooleanField(default=True)
    show_unit_price = models.BooleanField(default=True)

    # --- EXCLUSIVE FIELDS (Sirf Order Report ke liye) ---
    show_month = models.BooleanField(default=True)
    show_day = models.BooleanField(default=True)
    show_txn_detail = models.BooleanField(default=True)
    show_merchant = models.BooleanField(default=True)
    show_merchant_id = models.BooleanField(default=True)
    show_order_status = models.BooleanField(default=True)
    show_order_qty = models.BooleanField(default=True)
    show_order_amount = models.BooleanField(default=True)
    show_payment_amount = models.BooleanField(default=True)
    show_card_offer = models.BooleanField(default=True)

    # --- EXCLUSIVE FIELDS (Sirf Invoice Shipment ke liye) ---
    show_seller_name = models.BooleanField(default=True)
    show_seller_gstn = models.BooleanField(default=True)
    show_invoice_no = models.BooleanField(default=True)
    show_invoice_date = models.BooleanField(default=True)
    show_invoice_qty = models.BooleanField(default=True)
    show_invoice_amount = models.BooleanField(default=True)
    show_delivery_status = models.BooleanField(default=True)
    show_delivery_date = models.BooleanField(default=True)

    def __str__(self):
        return self.policy_name
class Firm(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Merchant(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name    
    
class ProductModel(models.Model):
    # Required Fields
    asin_fsn = models.CharField(max_length=100, unique=True)
    model_name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    
    # SAP CODES (blank=True rakha hai taaki user khali bhi chhod sake)
    sap_polyshri = models.CharField(max_length=100, blank=True, null=True)
    sap_rio = models.CharField(max_length=100, blank=True, null=True)
    sap_ne = models.CharField(max_length=100, blank=True, null=True)
    sap_sms = models.CharField(max_length=100, blank=True, null=True)
    sap_smmpl = models.CharField(max_length=100, blank=True, null=True)

    # Jab database me entry dekhenge toh is naam se dikhegi
    def __str__(self):
        return f"{self.asin_fsn} - {self.model_name}"    

#----------------------------INVOICE SHIPMENT MODEL--------------------------------------------------

class InvoiceShipment(models.Model):
    # 1. AUTO-FETCHED FIELDS (Order report se aayenge)
    order_id = models.CharField(max_length=150, null=True, blank=True)
    txn_date = models.CharField(max_length=100, null=True, blank=True) # CharField safe hai string dates ke liye
    firm = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    asin_fsn = models.CharField(max_length=150, null=True, blank=True)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    model_no = models.CharField(max_length=150, null=True, blank=True)
    
    # Prices ko hamesha Decimal me rakhna best hai calculation ke liye
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    order_qty = models.IntegerField(default=1, null=True, blank=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)

    # 2. MANUAL ENTRY FIELDS (User/Admin type karenge)
    seller_name = models.CharField(max_length=255, null=True, blank=True)
    seller_gstn = models.CharField(max_length=100, null=True, blank=True)
    invoice_no = models.CharField(max_length=150, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    invoice_qty = models.IntegerField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tracking_id = models.CharField(max_length=255, blank=True, null=True)

    # 3. DASHBOARD CONTROL FIELDS (Delivery Tracking)
    delivery_status = models.CharField(max_length=50, default='Pending', null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)

    # 4. AUDIT FIELDS (Track karne ke liye ki entry kab bani aur kab update hui)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.order_id} - {self.invoice_no}"


# --- INWARD & SHORTAGE TRACKING MODEL  VIEW Button ---
class InwardRecord(models.Model):
    # Linking fields (Order ko pehchanne ke liye)
    order_id = models.CharField(max_length=100)
    asin_fsn = models.CharField(max_length=100)
    
    # Direct fields for Screenshot Boxes
    short_qty = models.IntegerField(default=0)                                      # Box 11
    short_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Box 12
    inward_qty = models.IntegerField(default=0)                                     # Box 18
    inward_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Box 19

    def __str__(self):
        return f"Order: {self.order_id} | Inward: {self.inward_qty} | Short: {self.short_qty}"


# --- REFUND TRACKING MODEL ---
class RefundRecord(models.Model):
    # Linking fields (Order ko pehchanne ke liye)
    order_id = models.CharField(max_length=100)
    asin_fsn = models.CharField(max_length=100)
    
    # Direct fields for Screenshot Boxes
    refund_qty = models.IntegerField(default=0)                                      # Box 13
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Box 14

    def __str__(self):
        return f"Order: {self.order_id} | Refund Amount: ₹{self.refund_amount}"


# 🔥 AUTO STATUS UPDATE SIGNAL
@receiver([post_save, post_delete], sender=InvoiceShipment)
def update_order_status_on_shipment(sender, instance, **kwargs):
    try:
        # Jis FSN ka shipment bana hai, uski Order row dhoondo
        orders = OrderReport.objects.filter(order_id=instance.order_id, asin_fsn=instance.asin_fsn)
        for order in orders:
            shipments = InvoiceShipment.objects.filter(order_id=order.order_id, asin_fsn=order.asin_fsn)
            
            del_qty = shipments.filter(delivery_status='Delivered').aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            can_qty = shipments.filter(delivery_status='Cancelled').aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            
            pending_qty = order.order_qty - del_qty - can_qty
            new_status = "Complete" if pending_qty <= 0 else "Open"
            
            # Agar status badal gaya hai toh DataBase me turant save kar do
            if order.order_status != new_status:
                order.order_status = new_status
                order.save()
    except Exception as e:
        pass