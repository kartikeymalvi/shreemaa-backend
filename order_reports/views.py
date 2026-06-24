from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant, ProductModel, InvoiceShipment
from .serializers import OrderReportSerializer, ColumnVisibilityPolicySerializer, FirmSerializer, LocationSerializer, MerchantSerializer, ProductModelSerializer, InvoiceShipmentSerializer
import pandas as pd
from django.db.models import Q
import math
import datetime
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

# API 1: Fetch all records & Create Single Record manually
class OrderReportListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = OrderReport.objects.all().order_by('-id')
        
        # URL se Filters get karna
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        firm = self.request.query_params.get('firm')
        location = self.request.query_params.get('location')
        model_no = self.request.query_params.get('model_no')
        txn_detail = self.request.query_params.get('txn_detail')
        order_status = self.request.query_params.get('order_status')
        
        # 🔥 GLOBAL SEARCH PARAMETER
        search_query = self.request.query_params.get('search')

        if start_date: queryset = queryset.filter(txn_date__gte=start_date)
        if end_date: queryset = queryset.filter(txn_date__lte=end_date)
        if firm: queryset = queryset.filter(firm__icontains=firm)
        if location: queryset = queryset.filter(location__icontains=location)
        if model_no: queryset = queryset.filter(model_no__icontains=model_no)
        if txn_detail: queryset = queryset.filter(txn_detail__icontains=txn_detail)
        if order_status: queryset = queryset.filter(order_status=order_status)

        # 🔥 GLOBAL SEARCH LOGIC (Kisi bhi column me search karega)
        if search_query:
            queryset = queryset.filter(
                Q(order_id__icontains=search_query) |
                Q(firm__icontains=search_query) |
                Q(merchant__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(asin_fsn__icontains=search_query) |
                Q(model_name__icontains=search_query) |
                Q(model_no__icontains=search_query) |
                Q(txn_detail__icontains=search_query)
            )

        return queryset

class BulkUploadExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file: 
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith('.csv'): df = pd.read_csv(file)
            else: df = pd.read_excel(file)
            
            df = df.fillna('')
            df.columns = df.columns.str.strip().str.lower()

            # Master Data Arrays (Strict Match)
            valid_firms = set(Firm.objects.values_list('name', flat=True))
            valid_locations = set(Location.objects.values_list('name', flat=True))
            valid_merchants = set(Merchant.objects.values_list('name', flat=True))
            valid_asins = set(ProductModel.objects.values_list('asin_fsn', flat=True))
            valid_model_names = set(ProductModel.objects.values_list('model_name', flat=True))
            valid_model_nos = set(ProductModel.objects.values_list('model', flat=True))
            existing_orders = set(OrderReport.objects.values_list('order_id', flat=True))

            # 🔥 INITIALIZE ERROR COUNTERS
            dup_count = 0
            firm_count = 0
            loc_count = 0
            merch_count = 0
            asin_count = 0
            mname_count = 0
            mno_count = 0
            
            file_order_ids = set()

            # --- VALIDATION LOOP (Saare records check karega) ---
            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                if not order_id: continue
                
                firm = str(row.get('firm', '')).strip()
                location = str(row.get('location', '')).strip()
                merchant = str(row.get('merchant', '')).strip()
                asin_fsn = str(row.get('asin/fsn', row.get('fsn', ''))).strip()
                model_name = str(row.get('model name', '')).strip()
                model_no = str(row.get('model', row.get('model no', row.get('model number', '')))).strip()

                # 1. Duplicate Order ID Check
                if order_id in existing_orders or order_id in file_order_ids:
                    dup_count += 1
                file_order_ids.add(order_id)

                # 2. Strict Master Match Checks
                if firm and firm not in valid_firms: dup_count += 0; firm_count += 1
                if location and location not in valid_locations: loc_count += 1
                if merchant and merchant not in valid_merchants: merch_count += 1
                if asin_fsn and asin_fsn not in valid_asins: asin_count += 1
                if model_name and model_name not in valid_model_names: mname_count += 1
                if model_no and model_no not in valid_model_nos: mno_count += 1

            # 🔥 COMPACT SUMMARY GENERATOR
            error_segments = []
            if dup_count > 0: error_segments.append(f"{dup_count} Duplicate Order ID(s)")
            if firm_count > 0: error_segments.append(f"{firm_count} Firm mismatch(es)")
            if loc_count > 0: error_segments.append(f"{loc_count} Location mismatch(es)")
            if merch_count > 0: error_segments.append(f"{merch_count} Merchant mismatch(es)")
            if asin_count > 0: error_segments.append(f"{asin_count} ASIN/FSN mismatch(es)")
            if mname_count > 0: error_segments.append(f"{mname_count} Model Name mismatch(es)")
            if mno_count > 0: error_segments.append(f"{mno_count} Model Number mismatch(es)")

            if error_segments:
                total_errors = dup_count + firm_count + loc_count + merch_count + asin_count + mname_count + mno_count
                summary_msg = "Validation Failed! Found: " + ", ".join(error_segments) + f". Total {total_errors} errors. No records saved!"
                return Response({"error": summary_msg}, status=status.HTTP_400_BAD_REQUEST)

            # --- SAVE LOOP (Sirf tab chalega jab 0 errors honge) ---
            records_to_create = []
            saved_count = 0

            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                if not order_id: continue

                raw_date = str(row.get('txn date', row.get('order date', '')))
                txn_date = None
                if raw_date:
                    try: txn_date = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
                    except: pass

                records_to_create.append(OrderReport(
                    order_id=order_id, txn_date=txn_date,
                    month=str(row.get('month', '')).strip(), day=str(row.get('day', '')).strip(),
                    merchant=str(row.get('merchant', '')).strip(), merchant_id=str(row.get('merchant id', '')).strip(),
                    firm=str(row.get('firm', '')).strip(), location=str(row.get('location', '')).strip(),
                    asin_fsn=str(row.get('asin/fsn', '')).strip(), model_name=str(row.get('model name', '')).strip(),
                    model_no=str(row.get('model', row.get('model no', ''))).strip(), txn_detail=str(row.get('txn detail', '')).strip(),
                    order_status="Open",
                    order_qty=int(float(row.get('order qty', row.get('qty', 1)) or 1)),
                    order_amount=float(row.get('order amt', 0.0) or 0.0),
                    unit_price=float(row.get('unit price', 0.0) or 0.0),
                    payment_amount=float(row.get('payment amt', 0.0) or 0.0),
                    card_offer=float(row.get('card offer', 0.0) or 0.0)
                ))
                saved_count += 1
            
            OrderReport.objects.bulk_create(records_to_create)
            return Response({"message": f"Successfully uploaded {saved_count} records!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# Nayi API View: Edit aur Delete ke liye
class OrderReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderReport.objects.all()
    serializer_class = OrderReportSerializer # (FIX: Double serializer hta diya gaya hai)
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
        p_name = request.query_params.get('policy_name', 'user_view_policy')
        policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
        serializer = ColumnVisibilityPolicySerializer(policy)
        return Response(serializer.data)

    def put(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "Access Denied: Only Admins can modify view settings."}, status=403)
        
        p_name = request.query_params.get('policy_name', 'user_view_policy')
        policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
        
        serializer = ColumnVisibilityPolicySerializer(policy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)   

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

class ProductModelViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all().order_by('-id')
    serializer_class = ProductModelSerializer              


#-------------------------INVOICE SHIPMENT---------------

class InvoiceShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceShipmentSerializer
    pagination_class = StandardResultsSetPagination # (FIX: Pagination Uncomment kar diya hai)

    def get_queryset(self):
        queryset = InvoiceShipment.objects.all().order_by('-id')
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        order_id = self.request.query_params.get('order_id')
        delivery_status = self.request.query_params.get('delivery_status')

        if start_date:
            queryset = queryset.filter(txn_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(txn_date__lte=end_date)
        if order_id:
            queryset = queryset.filter(order_id__icontains=order_id)
        if delivery_status:
            queryset = queryset.filter(delivery_status=delivery_status)

        return queryset

class InvoiceShipmentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file.name.endswith('.csv'): df = pd.read_csv(file)
            else: df = pd.read_excel(file)
            
            df = df.fillna('')
            df.columns = df.columns.str.strip().str.lower()
            
            valid_orders = set(OrderReport.objects.values_list('order_id', flat=True))
            valid_firms = set(Firm.objects.values_list('name', flat=True))
            valid_locations = set(Location.objects.values_list('name', flat=True))
            valid_asins = set(ProductModel.objects.values_list('asin_fsn', flat=True))
            existing_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').exclude(invoice_no__isnull=True).values_list('invoice_no', flat=True))
            
            # 🔥 INITIALIZE COUNTERS FOR SHIPMENTS
            missing_order_count = 0
            missing_invoice_count = 0
            dup_invoice_count = 0
            firm_count = 0
            loc_count = 0
            asin_count = 0
            
            file_invoices = set()

            # --- VALIDATION LOOP ---
            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                if not order_id: continue

                firm = str(row.get('firm', '')).strip()
                location = str(row.get('location', '')).strip()
                asin_fsn = str(row.get('asin/fsn', '')).strip()
                invoice_no = str(row.get('invoice no', row.get('invoice_no', ''))).strip()

                if order_id not in valid_orders:
                    missing_order_count += 1
                
                if not invoice_no:
                    missing_invoice_count += 1
                else:
                    if invoice_no in existing_invoices or invoice_no in file_invoices:
                        dup_invoice_count += 1
                    file_invoices.add(invoice_no)

                if firm and firm not in valid_firms: firm_count += 1
                if location and location not in valid_locations: loc_count += 1
                if asin_fsn and asin_fsn not in valid_asins: asin_count += 1

            # 🔥 COMPACT SUMMARY GENERATOR FOR SHIPMENTS
            error_segments = []
            if missing_order_count > 0: error_segments.append(f"{missing_order_count} Invalid Order ID(s)")
            if missing_invoice_count > 0: error_segments.append(f"{missing_invoice_count} Missing Invoice No(s)")
            if dup_invoice_count > 0: error_segments.append(f"{dup_invoice_count} Duplicate Invoice No(s)")
            if firm_count > 0: error_segments.append(f"{firm_count} Firm mismatch(es)")
            if loc_count > 0: error_segments.append(f"{loc_count} Location mismatch(es)")
            if asin_count > 0: error_segments.append(f"{asin_count} ASIN/FSN mismatch(es)")

            if error_segments:
                total_errors = missing_order_count + missing_invoice_count + dup_invoice_count + firm_count + loc_count + asin_count
                summary_msg = "Validation Failed! Found: " + ", ".join(error_segments) + f". Total {total_errors} errors. No records saved!"
                return Response({"error": summary_msg}, status=status.HTTP_400_BAD_REQUEST)

            # --- SAVE LOOP ---
            records = []
            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                if not order_id: continue

                raw_inv_date = row.get('invoice date', row.get('invoice_date', ''))
                invoice_date = None
                if raw_inv_date:
                    try: invoice_date = pd.to_datetime(raw_inv_date, dayfirst=True).strftime('%Y-%m-%d')
                    except: pass
                
                raw_txn_date = row.get('txn date', row.get('txn_date', ''))
                txn_date = None
                if raw_txn_date:
                    try: txn_date = pd.to_datetime(raw_txn_date, dayfirst=True).strftime('%Y-%m-%d')
                    except: pass

                records.append(InvoiceShipment(
                    order_id=order_id, txn_date=txn_date, invoice_date=invoice_date,
                    firm=str(row.get('firm', '')).strip(), location=str(row.get('location', '')).strip(),
                    asin_fsn=str(row.get('asin/fsn', '')).strip(), invoice_no=str(row.get('invoice no', row.get('invoice_no', ''))).strip(),
                    seller_name=str(row.get('seller name', row.get('seller_name', ''))).strip(),
                    seller_gstn=str(row.get('seller gstn', row.get('seller_gstn', ''))).strip(),
                    invoice_qty=int(float(row.get('inv qty', row.get('invoice_qty', 1)) or 1)),
                    invoice_amount=row.get('inv amount', row.get('invoice_amount', 0.0)) or 0.0,
                    delivery_status="Pending"
                ))
            
            InvoiceShipment.objects.bulk_create(records)
            return Response({"message": f"{len(records)} Shipments uploaded successfully!"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 3. THE SMART AUTO-FETCH API
@api_view(['GET'])
def fetch_order_for_shipment(request, order_id):
    orders = OrderReport.objects.filter(order_id=order_id)
    
    if not orders.exists():
        return Response({"error": "Order ID not found in database!"}, status=404)

    order_data = []
    for order in orders:
        order_data.append({
            "order_id": order.order_id,
            "txn_date": order.txn_date,
            "firm": order.firm,
            "location": order.location,
            "asin_fsn": order.asin_fsn,
            "model_name": order.model_name,
            "model_no": order.model_no,
            "unit_price": order.unit_price,
            "order_qty": order.order_qty,
            "order_amount": order.order_amount,
        })
        
    return Response(order_data, status=200)