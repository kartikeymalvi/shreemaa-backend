from rest_framework import serializers
from django.db import transaction
from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant,ProductModel,InvoiceShipment,Seller,ApprovalRequest, ApprovalItem,GRPORecord,Ticket,RefundRecord

class OrderReportSerializer(serializers.ModelSerializer):
    # Virtual fields takaki agar DB mein column blank ho toh crash na ho
    seller_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    seller_gstn = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    delivered_qty = serializers.SerializerMethodField()
    delivered_amount = serializers.SerializerMethodField()

    class Meta:
        model = OrderReport
        fields = '__all__'
        extra_kwargs = {
            'card_no': {'required': False, 'allow_null': True},
            'placed_by': {'required': False, 'allow_null': True},
            # seller fields upar explicitly define kar diye hain isliye yahan se hata diye
        }

    # 🔥 MAGIC FIX: API response bhejne se pehle data intercept aur auto-fill karega 🔥
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Check agar seller_name blank hai ya '-' hai
        if not data.get('seller_name') or data.get('seller_name') == '-':
            # Local import taaki koi circular import error na aaye
            from .models import InvoiceShipment
            # Usi order_id ki pehli InvoiceShipment dhundho jisme Seller details actually bhari hui hon
            ship = InvoiceShipment.objects.filter(
                order_id=instance.order_id
            ).exclude(seller_name__exact='').exclude(seller_name__isnull=True).first()
            
            if ship:
                data['seller_name'] = ship.seller_name
                data['seller_gstn'] = ship.seller_gstn
            else:
                data['seller_name'] = '-'
                data['seller_gstn'] = '-'
                
        return data

    # 🔥 STRICT VALIDATION: Order ID + ASIN Combo Check (Manual Entry ke liye) 🔥
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

    # 🔥 CRASH-PROOF METHOD (Local import for Sum and InvoiceShipment) 🔥
    def get_delivered_qty(self, obj):
        try:
            from django.db.models import Sum
            from .models import InvoiceShipment
            shipments = InvoiceShipment.objects.filter(
                order_id=obj.order_id, 
                asin_fsn=obj.asin_fsn, 
                delivery_status='Delivered'
            )
            return shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
        except Exception:
            return 0

    # 🔥 CRASH-PROOF METHOD 🔥
    def get_delivered_amount(self, obj):
        try:
            from django.db.models import Sum
            from .models import InvoiceShipment
            shipments = InvoiceShipment.objects.filter(
                order_id=obj.order_id, 
                asin_fsn=obj.asin_fsn, 
                delivery_status='Delivered'
            )
            return float(shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
        except Exception:
            return 0.0

   
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
        extra_kwargs = {
            'invoice_status': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cancel_reason': {'required': False, 'allow_null': True, 'allow_blank': True},
            'delivery_date': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

    # 🔥 STRICT VALIDATION: Duplicate Invoice Number Check
    def validate(self, data):
        invoice_no = data.get('invoice_no')
        
        if invoice_no and str(invoice_no).strip():
            # Check karo ki kya database me ye invoice number pehle se hai
            existing_invoice = InvoiceShipment.objects.filter(invoice_no__iexact=str(invoice_no).strip())
            
            # Agar Edit kar rahe hain (PUT/PATCH), toh khud ki ID ignore karo
            if self.instance:
                existing_invoice = existing_invoice.exclude(id=self.instance.id)
                
            if existing_invoice.exists():
                raise serializers.ValidationError({
                    "error": f"Validation Failed: Invoice Number '{invoice_no}' already exists! Duplicates are not allowed."
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
        read_only_fields = ['approval_no', 'status', 'authorized_by']
        
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
        try:
            # Pop the items array safely
            items_data = validated_data.pop('items', [])
            
            # Master request save karein
            approval = ApprovalRequest.objects.create(**validated_data)
            
            # Items loop karke child table me save karein
            for item_data in items_data:
                ApprovalItem.objects.create(approval=approval, **item_data)
                
            return approval
            
        except Exception as e:
            # 🔥 MAGIC LINE: Agar database fat-ta hai, toh HTML error ki jagah 
            # Frontend par ek popup aayega jo exact Python error batayega!
            raise serializers.ValidationError({
                "error": f"Database Save Error: {str(e)}"
            })
    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            # 1. Naye items nikal lo
            items_data = validated_data.pop('items', [])
            
            # 2. Master Table fields update karo
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # 3. Purane saare items delete karke, Naye (Edited) items insert karo
            instance.items.all().delete()
            for item_data in items_data:
                ApprovalItem.objects.create(approval=instance, **item_data)
                
            return instance
            
        except Exception as e:
            raise serializers.ValidationError({"error": f"Update Error: {str(e)}"})    
    
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



# grpo 

from .models import GRPORecord

# ------------------------- GRPO SERIALIZER -------------------------
class GRPORecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRPORecord
        fields = '__all__'  

# ticket               

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'        


class RefundRecordSerializer(serializers.ModelSerializer):
    # Virtual field in case database me column missing ho
    invoice_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = RefundRecord
        fields = '__all__'

    # 🔥 PROFESSIONAL INTERCEPTOR: Auto-fetch missing Invoice Number 🔥
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Agar invoice_no blank ya '-' hai, toh usey InvoiceShipment se dhoondho
        if not data.get('invoice_no') or data.get('invoice_no') == '-':
            from .models import InvoiceShipment
            ship = InvoiceShipment.objects.filter(
                order_id=instance.order_id
            ).exclude(invoice_no__exact='').exclude(invoice_no__isnull=True).first()
            
            if ship:
                data['invoice_no'] = ship.invoice_no
            else:
                data['invoice_no'] = '-'
                
        return data