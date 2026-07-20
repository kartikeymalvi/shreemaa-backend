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
    sap_po_no = models.CharField(max_length=255, null=True, blank=True)
    
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

    card_no = models.CharField(max_length=100, null=True, blank=True)
    placed_by = models.CharField(max_length=255, null=True, blank=True)
    seller_gstn = models.CharField(max_length=15, null=True, blank=True)
    seller_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Auto-computed / Cross-module fields (Default 0 de rahe hain)
    delivered_qty = models.IntegerField(default=0)
    delivered_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    cancel_qty = models.IntegerField(default=0)
    
    discrepancy_qty = models.IntegerField(default=0)
    discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    refund_qty = models.IntegerField(default=0)
    
    pending_qty = models.IntegerField(default=0)
    pending_refund = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    grpo_qty = models.IntegerField(default=0)
    grpo_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

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
class Seller(models.Model):
    gstn_no = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    sap_polyshri = models.CharField(max_length=100, blank=True, null=True)
    sap_rio = models.CharField(max_length=100, blank=True, null=True)
    sap_ne = models.CharField(max_length=100, blank=True, null=True)
    sap_sms = models.CharField(max_length=100, blank=True, null=True)
    sap_smmpl = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.gstn_no}"        

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
    invoice_status = models.CharField(max_length=50, default='Open', null=True, blank=True)
    cancel_reason = models.TextField(null=True, blank=True)
    del_date = models.CharField(max_length=50, null=True, blank=True) # CharField taaki empty string par error na aaye

    # 🔥 CROSS-MODULE METRICS (GRPO, Issues, Refund) 🔥
    grpo_qty = models.IntegerField(default=0)
    grpo_pending_qty = models.IntegerField(default=0)
    grpo_pending_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    refund_discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    cancel_reason = models.TextField(null=True, blank=True)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    delivery_status = models.CharField(max_length=50, default='Pending')
    delivery_date = models.CharField(max_length=50, null=True, blank=True)
    grpo_qty = models.IntegerField(default=0)
    grpo_pending_qty = models.IntegerField(default=0)
    grpo_pending_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    refund_discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

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


# APPROVALS model---------------------


class ApprovalRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    # 1. Approval No -> Auto Generate
    approval_no = models.CharField(max_length=50, unique=True, blank=True)
    # 2. Request Date -> Manual
    request_date = models.DateField()
    # 3. Requested By , placed by  -> Manual
    requested_by = models.CharField(max_length=255)
    placed_by = models.CharField(max_length=255, null=True, blank=True)
    # 4. Merchant_ID -> Manual
    merchant_account_id = models.CharField(max_length=255, blank=True, null=True)
    # 5. Firm Name -> Dropdown
    firm = models.ForeignKey(Firm, on_delete=models.SET_NULL, null=True)
    # 6. Bill Location -> Dropdown
    bill_location = models.ForeignKey(Location, related_name='bill_approvals', on_delete=models.SET_NULL, null=True)
    # 7. Ship Location -> Dropdown
    ship_location = models.ForeignKey(Location, related_name='ship_approvals', on_delete=models.SET_NULL, null=True)
    # 8. Merchant -> Dropdown
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True)

    # 26. Status -> Auto Pending initially
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    # 27. Authorized By -> Admin User details when approved
    authorized_by = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.approval_no

# --- 🚀 2. APPROVAL ITEMS (DETAILS TABLE) ---
class ApprovalItem(models.Model):
    # Master se link karne ke liye
    approval = models.ForeignKey('ApprovalRequest', related_name='items', on_delete=models.CASCADE)
    
    # 9. ASIN/FSN -> Dropdown (Frontend se value aayegi)
    asin_fsn = models.CharField(max_length=255, null=True, blank=True)
    
    # 10. Model Name -> Auto Fill
    model_name = models.CharField(max_length=255, null=True, blank=True)
    
    # 11. Model -> Auto Fill
    model_no = models.CharField(max_length=255, null=True, blank=True)
    
    # 12. Req Qty -> Manual
    req_qty = models.IntegerField(default=0)
    
    # 13. Purchase Price -> Manual
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # 14. Cn Amt -> Manual
    cn_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # 15. Agreed NLC -> Auto formula (Purchase Price - CN Amt)
    agreed_nlc = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # 16. Link Used -> Dropdown (Yes/No)
    link_used = models.CharField(max_length=10, default='No')
    
    # 17. Expected Delivery Date -> Calendar
    expected_delivery_date = models.DateField(null=True, blank=True)

    # --- 🛑 HIDDEN FIELDS (For Later Use) ---
    # 18. Placed Qty
    placed_qty = models.IntegerField(null=True, blank=True, default=0)
    
    # 19. Order NLC
    order_nlc = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    # 20. Total Placed Amt
    total_placed_amt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    # 21. Total CN Amt
    total_cn_amt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.00)
    
    # 22. Variance Qty
    variance_qty = models.IntegerField(null=True, blank=True, default=0)
    
    # 23. Placed By
    placed_by = models.CharField(max_length=255, null=True, blank=True)
    
    # 24. Payment Method
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    
    # 25. SAP PO No
    sap_po_no = models.CharField(max_length=255, null=True, blank=True)

    

    def __str__(self):
        # Adding a fallback just in case approval is not linked temporarily
        approval_no = self.approval.approval_no if self.approval else "Pending"
        return f"{self.asin_fsn} - {approval_no}"



#GRPO MODEL-----------------------


class GRPORecord(models.Model):
    firm_name = models.CharField(max_length=255, null=True, blank=True)
    internal_number = models.CharField(max_length=255, null=True, blank=True)
    grpo_status = models.CharField(max_length=100, default='Open')
    grpo_user_name = models.CharField(max_length=255, null=True, blank=True)
    
    grpo_no = models.CharField(max_length=255, null=True, blank=True)
    grpo_invoice_number = models.CharField(max_length=255, null=True, blank=True)
    
    # Dates (Stored as strings mapping DD-MM-YYYY or DateField)
    grpo_create_date = models.CharField(max_length=50, null=True, blank=True)
    grpo_posting_date = models.CharField(max_length=50, null=True, blank=True)
    
    purchase_vendor_code = models.CharField(max_length=255, null=True, blank=True)
    purchase_vendor_name = models.CharField(max_length=255, null=True, blank=True)
    inward_whs_code = models.CharField(max_length=255, null=True, blank=True)
    
    item_code = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    grpo_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    grpo_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grpo_no} - {self.item_code}"

class Ticket(models.Model):
    ticket_no = models.CharField(max_length=50, unique=True, blank=True)
    invoice_no = models.CharField(max_length=255)
    invoice_date = models.CharField(max_length=50, null=True, blank=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    order_date = models.CharField(max_length=50, null=True, blank=True)
    merchant = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    asin = models.CharField(max_length=255)
    model = models.CharField(max_length=255, null=True, blank=True)
    complaint_type = models.CharField(max_length=255)
    discrepancy_qty = models.IntegerField(default=0)
    discrepancy_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    remark = models.TextField(null=True, blank=True)
    
    raised_by = models.CharField(max_length=255, null=True, blank=True)
    raised_date = models.CharField(max_length=50, null=True, blank=True)
    ticket_status = models.CharField(max_length=50, default='Open')
    
    credit_note_no = models.CharField(max_length=255, null=True, blank=True)
    refund_received_amt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Photo upload ke liye
    photo = models.ImageField(upload_to='tickets/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate Ticket Number (e.g., TCK-0001)
        if not self.ticket_no:
            last_ticket = Ticket.objects.all().order_by('id').last()
            if last_ticket:
                new_id = last_ticket.id + 1
            else:
                new_id = 1
            self.ticket_no = f"TCK-{new_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.ticket_no)   

    # --- REFUND TRACKING MODEL ---  

class RefundRecord(models.Model):
    # Auto-fetched columns
    source_date = models.CharField(max_length=50, null=True, blank=True) # Invoice del_date ya Order date
    firm = models.CharField(max_length=200, null=True, blank=True)
    merchant = models.CharField(max_length=200, null=True, blank=True)
    order_id = models.CharField(max_length=150, null=True, blank=True)
    invoice_no = models.CharField(max_length=150, null=True, blank=True)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Manual Input (Update Button se aayenge)
    refund_type = models.CharField(max_length=100, null=True, blank=True) 
    refund_status = models.CharField(max_length=100, default='Pending', null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    received_txn_type = models.CharField(max_length=100, null=True, blank=True)
    received_card_no = models.CharField(max_length=100, null=True, blank=True)
    received_comment = models.TextField(null=True, blank=True)
    refund_qty = models.IntegerField(default=0, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Refund for {self.order_id}"
    @receiver([post_save], sender=InvoiceShipment)
    def auto_refund_from_shipment(sender, instance, **kwargs):
        orders = OrderReport.objects.filter(order_id=instance.order_id, asin_fsn=instance.asin_fsn)
        if orders.exists() and instance.delivery_status == 'Cancelled':
            order = orders.first()
            if order.order_status == 'Complete':
                RefundRecord.objects.get_or_create(
                    order_id=instance.order_id,
                    invoice_no=instance.invoice_no,
                    defaults={
                        'source_date': instance.delivery_date or instance.invoice_date,
                        'firm': instance.firm,
                        'merchant': order.merchant,
                        'model_name': instance.model_name,
                        'invoice_amount': instance.invoice_amount,
                        'refund_qty': instance.invoice_qty, # 🔥 BAS YE LINE ADD KARNI HAI
                        'received_comment': 'Auto-generated from Cancelled Shipment'
                    }
                )

    @receiver([post_save], sender=Ticket)
    def auto_refund_from_ticket(sender, instance, **kwargs):
        # Rule: Agar Ticket Closed hui -> Send to Refund
        if instance.ticket_status == 'Closed':
            RefundRecord.objects.get_or_create(
                order_id=instance.order_id,
                invoice_no=instance.invoice_no,
                defaults={
                    'source_date': instance.invoice_date or instance.raised_date,
                    'firm': '', 
                    'merchant': instance.merchant,
                    'model_name': instance.model,
                    'invoice_amount': instance.discrepancy_amount,
                    'refund_qty': instance.discrepancy_qty,
                    'received_comment': 'Auto-generated from Closed Ticket'
                }
            )


# --- PURCHASE INWARD MODEL ---
class PurchaseInward(models.Model):
    inward_no = models.CharField(max_length=50, unique=True, blank=True)
    grpo_no = models.CharField(max_length=100) # Linking to GRPO
    inward_date = models.DateField(auto_now_add=True)
    
    # Auto-fetched from GRPO
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    item_code = models.CharField(max_length=100, blank=True, null=True)
    expected_qty = models.FloatField(default=0.0)
    
    # Physical Verification Data
    received_qty = models.FloatField(default=0.0)
    shortage_qty = models.FloatField(default=0.0) # Auto Calculate
    
    received_by = models.CharField(max_length=100, blank=True, null=True)
    warehouse_location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default='Completed') # Partial / Completed
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Auto-generate Inward Number (e.g., INW-0001)
        if not self.inward_no:
            last_inward = PurchaseInward.objects.order_by('id').last()
            if last_inward and last_inward.inward_no.startswith('INW-'):
                try:
                    last_id = int(last_inward.inward_no.split('-')[1])
                    self.inward_no = f"INW-{last_id + 1:04d}"
                except:
                    self.inward_no = "INW-0001"
            else:
                self.inward_no = "INW-0001"
        
        # 2. Auto-calculate Shortage Quantity
        self.shortage_qty = float(self.expected_qty) - float(self.received_qty)
        
        # 3. Smart Status Update
        if self.received_qty < self.expected_qty:
            self.status = 'Partial'
        else:
            self.status = 'Completed'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.inward_no} - {self.grpo_no}"