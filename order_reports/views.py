from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import OrderReport,ColumnVisibilityPolicy,Firm, Location, Merchant
from .serializers import OrderReportSerializer,ColumnVisibilityPolicySerializer,FirmSerializer, LocationSerializer, MerchantSerializer
import pandas as pd
import math
import datetime



# API 1: Fetch all records & Create Single Record manually
# order_reports/views.py me is class ko replace karo
class OrderReportListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = OrderReport.objects.all().order_by('-id')
        
        # 1. Date Range Logic
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        firm = self.request.query_params.get('firm')
        location = self.request.query_params.get('location')
        model_no = self.request.query_params.get('model_no')
        txn_detail = self.request.query_params.get('txn_detail')
        order_status = self.request.query_params.get('order_status')

        # Agar 'start_date' hai toh us din ya uske baad ka data
        if start_date: 
            queryset = queryset.filter(txn_date__gte=start_date)
        
        # Agar 'end_date' hai toh us din ya uske pehle ka data
        if end_date: 
            queryset = queryset.filter(txn_date__lte=end_date)
            
        if firm: queryset = queryset.filter(firm__icontains=firm)
        if location: queryset = queryset.filter(location__icontains=location)
        if model_no: queryset = queryset.filter(model_no__icontains=model_no)
        if txn_detail: queryset = queryset.filter(txn_detail__icontains=txn_detail)
        if order_status: queryset = queryset.filter(order_status=order_status)

        return queryset
class BulkUploadExcelView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Please upload a valid Excel or CSV file."}, status=400)

        try:
            # Check file extension and read accordingly
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # Khali boxes (NaN) ko handle karna
            df = df.fillna('')

            # Smart Number Cleaner (agar numbers me comma ',' laga ho toh use bhi handle karega)
            def safe_float(val):
                try: 
                    return float(str(val).replace(',', '').strip()) if val != '' else 0.0
                except: return 0.0

            def safe_int(val):
                try: 
                    return int(float(str(val).replace(',', '').strip())) if val != '' else 1
                except: return 1

            # Smart Date Parser (Kisi bhi date format ko YYYY-MM-DD me convert karega)
            def parse_date(date_str):
                if not date_str:
                    return None
                date_str = str(date_str).strip()
                try:
                    if '.' in date_str: # Handles 15.06.2026
                        return datetime.datetime.strptime(date_str, '%d.%m.%Y').date()
                    elif '/' in date_str: # Handles 15/06/2026
                        return datetime.datetime.strptime(date_str, '%d/%m/%Y').date()
                    elif '-' in date_str: # Handles 2026-06-15
                        try:
                            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        except:
                            return datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
                    return pd.to_datetime(date_str).date()
                except:
                    return None

            for index, row in df.iterrows():
                order_id = str(row.get('Order_ID', '')).strip()
                if not order_id:
                    continue  # Bina Order ID wali line skip kar do

                # 1. ASIN aur FSN ko auto-merge karna (Agar koi ek missing ho toh bhi chalega)
                asin = str(row.get('ASIN', '')).strip()
                fsn = str(row.get('FSN', '')).strip()
                asin_fsn_val = f"{asin} / {fsn}".strip(' /')

                # 2. Number values safely nikalna
                order_amt = safe_float(row.get('Order Amount', 0))
                payment_amt = safe_float(row.get('Payment Amount', 0))
                
                # 3. Card Offer Auto-calculate karna
                card_offer_val = abs(order_amt - payment_amt)

                # 4. Date Parse karna
                txn_date_val = parse_date(row.get('Txn Date'))

                # Create naya order, ya update
                OrderReport.objects.update_or_create(
                    order_id=order_id,
                    defaults={
                        'txn_date': txn_date_val,
                        'month': str(row.get('Month', '')).strip(),
                        'day': str(row.get('Day', '')).strip(),
                        'txn_detail': str(row.get('Txn Detail', '')).strip(),
                        'merchant': str(row.get('Merchant', '')).strip(),
                        'merchant_id': str(row.get('Merchant_ID', '')).strip(),
                        'firm': str(row.get('Firm', '')).strip(),
                        'location': str(row.get('Location', '')).strip(),
                        'asin_fsn': asin_fsn_val, 
                        'model_name': str(row.get('Model Name', '')).strip(),
                        'model_no': str(row.get('Model', '')).strip(),
                        'order_status': str(row.get('Order Status', 'Delivered')).strip() or 'Delivered',
                        'order_qty': safe_int(row.get('Order_Qty', 1)),
                        'order_amount': order_amt,
                        'unit_price': safe_float(row.get('Unit Price', 0)),
                        'payment_amount': payment_amt,
                        'card_offer': card_offer_val, 
                    }
                )
            return Response({"message": "Data uploaded and synced successfully!"}, status=201)
        
        except Exception as e:
            return Response({"error": f"Error parsing file: {str(e)}"}, status=400)
# Nayi API View: Edit aur Delete ke liye
class OrderReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderReport.objects.all()
    serializer_class = OrderReportSerializer
    permission_classes = [IsAuthenticated]

    # Security Layer: Only Admin can EDIT records
    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Access Denied: Only Admins can modify order entries.")
        serializer.save()

    # Security Layer: Only Admin can DELETE records
    def perform_destroy(self, instance):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Access Denied: Only Admins can delete order entries.")
        instance.delete()  
class ColumnVisibilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Setting nahi hai toh automatically nayi bana dega
        policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name="user_view_policy")
        serializer = ColumnVisibilityPolicySerializer(policy)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "Access Denied: Only Admins can modify view settings."}, status=403)
        
        policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name="user_view_policy")
        serializer = ColumnVisibilityPolicySerializer(policy, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)   

# File ke sabse end me ye 3 ViewSets add kar do:
class FirmViewSet(viewsets.ModelViewSet):
    queryset = Firm.objects.all().order_by('-id')
    serializer_class = FirmSerializer
    permission_classes = [IsAuthenticated]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('-id')
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all().order_by('-id')
    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated]               