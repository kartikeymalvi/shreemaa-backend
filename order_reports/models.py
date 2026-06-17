# from django.db import models
# from accounts.models import CustomUser


# class OrderReport(models.Model):
#   # Core Data
#     order_id = models.CharField(max_length=100, unique=True)
#     txn_date = models.DateField(null=True, blank=True)
#     month = models.CharField(max_length=20, null=True, blank=True)
#     day = models.CharField(max_length=20, null=True, blank=True)
#     txn_detail = models.CharField(max_length=255, null=True, blank=True)
    
#     # Merchant & Firm Details
#     merchant = models.CharField(max_length=100, null=True, blank=True)
#     merchant_id = models.CharField(max_length=100, null=True, blank=True)
#     firm = models.CharField(max_length=100, null=True, blank=True)
#     location = models.CharField(max_length=100, null=True, blank=True)
    
#     # Product Details
#     asin = models.CharField(max_length=100, null=True, blank=True)
#     fsn = models.CharField(max_length=100, null=True, blank=True)
#     model_name = models.CharField(max_length=200, null=True, blank=True)
#     model_no = models.CharField(max_length=100, null=True, blank=True) # Renamed 'Model' to 'model_no' to avoid keyword conflict
    
#     # Financials (Using DecimalField for money)
#     order_qty = models.IntegerField(default=0)
#     order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
#     payment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
#     # Tracking
#     uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.order_id} - {self.model_name}"
# class ColumnVisibilityPolicy(models.Model):
#     policy_name = models.CharField(max_length=50, default="user_view_policy", unique=True)
    
#     # All 17 Fields Visibility Control
#     show_order_id = models.BooleanField(default=True)
#     show_txn_date = models.BooleanField(default=True)
#     show_month = models.BooleanField(default=True)
#     show_day = models.BooleanField(default=True)
#     show_txn_detail = models.BooleanField(default=True)
#     show_merchant = models.BooleanField(default=True)
#     show_merchant_id = models.BooleanField(default=True)
#     show_firm = models.BooleanField(default=True)
#     show_location = models.BooleanField(default=True)
#     show_asin = models.BooleanField(default=True)
#     show_fsn = models.BooleanField(default=True)
#     show_model_name = models.BooleanField(default=True)
#     show_model_no = models.BooleanField(default=True)
#     show_order_qty = models.BooleanField(default=True)
#     show_order_amount = models.BooleanField(default=True)
#     show_unit_price = models.BooleanField(default=True)
#     show_payment_amount = models.BooleanField(default=True)

#     def __str__(self):
#         return self.policy_name

from django.db import models

class OrderReport(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Delivered', 'Delivered'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=100, unique=True)
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
    
    model_name = models.CharField(max_length=100, null=True, blank=True)
    model_no = models.CharField(max_length=100, null=True, blank=True)
    
    # New Field
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='Delivered')
    
    # Number Fields
    order_qty = models.IntegerField(default=0)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # New Auto-calculated field
    card_offer = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.order_id

# Updated Column Visibility Policy
class ColumnVisibilityPolicy(models.Model):
    policy_name = models.CharField(max_length=50, default="user_view_policy", unique=True)
    
    show_order_id = models.BooleanField(default=True)
    show_txn_date = models.BooleanField(default=True)
    show_month = models.BooleanField(default=True)
    show_day = models.BooleanField(default=True)
    show_txn_detail = models.BooleanField(default=True)
    show_merchant = models.BooleanField(default=True)
    show_merchant_id = models.BooleanField(default=True)
    show_firm = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_asin_fsn = models.BooleanField(default=True) # Merged
    show_model_name = models.BooleanField(default=True)
    show_model_no = models.BooleanField(default=True)
    show_order_status = models.BooleanField(default=True) # New
    show_order_qty = models.BooleanField(default=True)
    show_order_amount = models.BooleanField(default=True)
    show_unit_price = models.BooleanField(default=True)
    show_payment_amount = models.BooleanField(default=True)
    show_card_offer = models.BooleanField(default=True) # New

    def __str__(self):
        return self.policy_name
# order_reports/models.py me sabse neeche add karein:

class Firm(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Merchant(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name    