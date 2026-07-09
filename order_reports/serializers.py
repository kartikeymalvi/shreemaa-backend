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
    items = ApprovalItemSerializer(many=True) 

    # 🔥 FIX 1: 'source' ki jagah SerializerMethodField use kiya taaki Null data par Server Crash (500) na ho!
    firm_detail = serializers.SerializerMethodField()
    bill_location_detail = serializers.SerializerMethodField()
    ship_location_detail = serializers.SerializerMethodField()
    merchant_detail = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = '__all__'
        read_only_fields = ['approval_no', 'requested_by', 'status', 'authorized_by']
        
        extra_kwargs = {
            'firm': {'required': False, 'allow_null': True},
            'merchant': {'required': False, 'allow_null': True},
            'bill_location': {'required': False, 'allow_null': True},
            'ship_location': {'required': False, 'allow_null': True},
        }

    # 🔥 SAFE GETTERS: Agar data nahi hai toh crash karne ki jagah None bhejega
    def get_firm_detail(self, obj):
        return {"name": obj.firm.name} if obj.firm else None
        
    def get_bill_location_detail(self, obj):
        return {"name": obj.bill_location.name} if obj.bill_location else None
        
    def get_ship_location_detail(self, obj):
        return {"name": obj.ship_location.name} if obj.ship_location else None
        
    def get_merchant_detail(self, obj):
        return {"name": obj.merchant.name} if obj.merchant else None

    # Custom Create Logic 
    @transaction.atomic
    def create(self, validated_data):
        # 🔥 FIX 2: [] lagaya taaki agar items khali aaye toh KeyError se crash na ho
        items_data = validated_data.pop('items', []) 
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