from rest_framework import serializers
from django.db import transaction
from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant,ProductModel,InvoiceShipment,Seller,ApprovalRequest, ApprovalItem

class OrderReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReport
        fields = '__all__'

    # 🔥 STRICT VALIDATION: Order ID + ASIN Combo Check (Manual Entry ke liye)
    def validate(self, data):
        order_id = data.get('order_id')
        asin_fsn = data.get('asin_fsn')
        
        # Agar Order ID aur ASIN dono aaye hain, tabhi combo check karo
        if order_id and asin_fsn:
            # Check karo ki kya is Order ID aur ASIN ka exact match pehle se hai?
            existing_record = OrderReport.objects.filter(order_id=order_id, asin_fsn=asin_fsn)
            
            # Agar hum "Edit" kar rahe hain (PUT request), toh khud ki ID ko hata do
            if self.instance:
                existing_record = existing_record.exclude(id=self.instance.id)
                
            # Agar combo mil gaya, toh Custom Error feko!
            if existing_record.exists():
                raise serializers.ValidationError({
                    "error": f"Order ID '{order_id}' aur ASIN '{asin_fsn}' ki entry pehle se exist karti hai! Ek hi item do baar add nahi kar sakte."
                })
                
        return data 

   
class ColumnVisibilityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnVisibilityPolicy
        fields = '__all__'         

# File ke end me ye classes add karo:
class FirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'    
class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = '__all__'    
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'                
# -------------------------INVOICE SHIPMENT---------------------------------------

       
class InvoiceShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceShipment
        fields = '__all__'

    # 🔥 STRICT VALIDATION: Duplicate Invoice Number Check (Manual Entry ke liye)
    def validate(self, data):
        invoice_no = data.get('invoice_no')
        
        # Agar user ne invoice number dala hai, toh check karo
        if invoice_no:
            # Check karo ki kya database me ye invoice number pehle se hai?
            existing_invoice = InvoiceShipment.objects.filter(invoice_no=invoice_no)
            
            # Agar hum "Edit" kar rahe hain (PUT request), toh khud ki ID ko check me se hata do
            if self.instance:
                existing_invoice = existing_invoice.exclude(id=self.instance.id)
                
            # Agar record mil gaya, toh turant Error feko!
            if existing_invoice.exists():
                raise serializers.ValidationError({
                    "error": f"Validation Failed: Invoice Number '{invoice_no}' pehle se exist karta hai! Duplicate allowed nahi hai."
                })
                
        return data       


#APPROVAL SERIALISERS---------------     
class ApprovalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalItem
        fields = '__all__'
        read_only_fields = ['approval'] # Ye backend khud set karega

class ApprovalRequestSerializer(serializers.ModelSerializer):
    items = ApprovalItemSerializer(many=True) # Items array accept karne ke liye

    # GET api me Dropdown ke names dikhane ke liye
    firm_name = serializers.CharField(source='firm.name', read_only=True)
    bill_location_name = serializers.CharField(source='bill_location.name', read_only=True)
    ship_location_name = serializers.CharField(source='ship_location.name', read_only=True)
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = '__all__'
        read_only_fields = ['approval_no', 'requested_by', 'status', 'authorized_by']

    # Custom Create Logic (Master + Multiple Items Ek Sath Save)
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        approval = ApprovalRequest.objects.create(**validated_data)
        
        for item_data in items_data:
            ApprovalItem.objects.create(approval=approval, **item_data)
            
        return approval
    
class FirmDropdownSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Firm
        fields = ['id', 'name']

class LocationDropdownSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Location
        fields = ['id', 'name']

class MerchantDropdownSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Merchant
        fields = ['id', 'name']

class ModelDropdownSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ProductModel
        fields = ['id', 'asin_fsn', 'model_name', 'model']    