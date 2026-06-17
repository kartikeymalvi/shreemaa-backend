from rest_framework import serializers
from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant

class OrderReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReport
        fields = '__all__'

   
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