from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant, ProductModel, InvoiceShipment,OrderReport,InwardRecord, RefundRecord
from .serializers import OrderReportSerializer, ColumnVisibilityPolicySerializer, FirmSerializer, LocationSerializer, MerchantSerializer, ProductModelSerializer, InvoiceShipmentSerializer
import pandas as pd
from django.db.models import Q
from django.http import HttpResponse
import math
import datetime
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum

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




# class BulkUploadExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
#         if not file: 
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             if file.name.endswith('.csv'): df = pd.read_csv(file)
#             else: df = pd.read_excel(file)
            
#             df = df.fillna('')
#             df.columns = df.columns.str.strip().str.lower()

#             # Master Data Arrays (Strict Match)
#             valid_firms = set(Firm.objects.values_list('name', flat=True))
#             valid_locations = set(Location.objects.values_list('name', flat=True))
#             valid_merchants = set(Merchant.objects.values_list('name', flat=True))
#             valid_asins = set(ProductModel.objects.values_list('asin_fsn', flat=True))
#             valid_model_names = set(ProductModel.objects.values_list('model_name', flat=True))
#             valid_model_nos = set(ProductModel.objects.values_list('model', flat=True))
            
#             # 🔥 FIX 1: Ab sirf Order ID nahi, balki (Order ID, ASIN) dono ka JODA (tuple) layenge
#             existing_orders = set(OrderReport.objects.values_list('order_id', 'asin_fsn'))

#             # INITIALIZE ERROR COUNTERS
#             dup_count = 0
#             firm_count = 0
#             loc_count = 0
#             merch_count = 0
#             asin_count = 0
#             mname_count = 0
#             mno_count = 0
            
#             # 🔥 FIX 2: File ke andar duplicates rokne ke liye naya set
#             file_order_asins = set() 

#             # --- VALIDATION LOOP (Saare records check karega) ---
#             for index, row in df.iterrows():
#                 order_id = str(row.get('order id', row.get('order_id', ''))).strip()
#                 if not order_id: continue
                
#                 firm = str(row.get('firm', '')).strip()
#                 location = str(row.get('location', '')).strip()
#                 merchant = str(row.get('merchant', '')).strip()
#                 asin_fsn = str(row.get('asin/fsn', row.get('fsn', ''))).strip()
#                 model_name = str(row.get('model name', '')).strip()
#                 model_no = str(row.get('model', row.get('model no', row.get('model number', '')))).strip()

#                 # 🔥 FIX 3: Combo Check - Agar same order id aur same ASIN mila, tabhi error aayega
#                 order_asin_combo = (order_id, asin_fsn)
#                 if order_asin_combo in existing_orders or order_asin_combo in file_order_asins:
#                     dup_count += 1
#                 file_order_asins.add(order_asin_combo)

#                 # Strict Master Match Checks
#                 if firm and firm not in valid_firms: firm_count += 1
#                 if location and location not in valid_locations: loc_count += 1
#                 if merchant and merchant not in valid_merchants: merch_count += 1
#                 if asin_fsn and asin_fsn not in valid_asins: asin_count += 1
#                 if model_name and model_name not in valid_model_names: mname_count += 1
#                 if model_no and model_no not in valid_model_nos: mno_count += 1

#             # 🔥 COMPACT SUMMARY GENERATOR
#             error_segments = []
#             if dup_count > 0: error_segments.append(f"{dup_count} Duplicate Order+ASIN entry(s)")
#             if firm_count > 0: error_segments.append(f"{firm_count} Firm mismatch(es)")
#             if loc_count > 0: error_segments.append(f"{loc_count} Location mismatch(es)")
#             if merch_count > 0: error_segments.append(f"{merch_count} Merchant mismatch(es)")
#             if asin_count > 0: error_segments.append(f"{asin_count} ASIN/FSN mismatch(es)")
#             if mname_count > 0: error_segments.append(f"{mname_count} Model Name mismatch(es)")
#             if mno_count > 0: error_segments.append(f"{mno_count} Model Number mismatch(es)")

#             if error_segments:
#                 total_errors = dup_count + firm_count + loc_count + merch_count + asin_count + mname_count + mno_count
#                 summary_msg = "Validation Failed! Found: " + ", ".join(error_segments) + f". Total {total_errors} errors. No records saved!"
#                 return Response({"error": summary_msg}, status=status.HTTP_400_BAD_REQUEST)

#             # --- SAVE LOOP (Sirf tab chalega jab 0 errors honge) ---
#             records_to_create = []
#             saved_count = 0

#             for index, row in df.iterrows():
#                 order_id = str(row.get('order id', row.get('order_id', ''))).strip()
#                 if not order_id: continue

#                 raw_date = str(row.get('txn date', row.get('order date', '')))
#                 txn_date = None
#                 if raw_date:
#                     try: txn_date = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
#                     except: pass

#                 records_to_create.append(OrderReport(
#                     order_id=order_id, txn_date=txn_date,
#                     month=str(row.get('month', '')).strip(), day=str(row.get('day', '')).strip(),
#                     merchant=str(row.get('merchant', '')).strip(), merchant_id=str(row.get('merchant id', '')).strip(),
#                     firm=str(row.get('firm', '')).strip(), location=str(row.get('location', '')).strip(),
#                     asin_fsn=str(row.get('asin/fsn', '')).strip(), model_name=str(row.get('model name', '')).strip(),
#                     model_no=str(row.get('model', row.get('model no', ''))).strip(), txn_detail=str(row.get('txn detail', '')).strip(),
#                     order_status="Open",
#                     order_qty=int(float(row.get('order qty', row.get('qty', 1)) or 1)),
#                     order_amount=float(row.get('order amt', 0.0) or 0.0),
#                     unit_price=float(row.get('unit price', 0.0) or 0.0),
#                     payment_amount=float(row.get('payment amt', 0.0) or 0.0),
#                     card_offer=float(row.get('card offer', 0.0) or 0.0)
#                 ))
#                 saved_count += 1
            
#             OrderReport.objects.bulk_create(records_to_create)
#             return Response({"message": f"Successfully uploaded {saved_count} records!"}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class BulkUploadExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file: 
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith('.csv'): 
                df = pd.read_csv(file)
            else: 
                df = pd.read_excel(file)
            
            # --- 🔥 NEW: EXCEL HEADER VALIDATION SHURU 🔥 ---
            # Sheet ke raw headers ko clean karke lower case me convert kar rahe hain check karne ke liye
            uploaded_headers = set(df.columns.str.strip().str.lower())
            
            # Jo headers mandatory hain unki expected list (Lowercase me safe comparison ke liye)
            EXPECTED_HEADERS = [
                's.no', 'order_id', 'txn date', 'month', 'day', 'txn detail', 
                'merchant', 'merchant_id', 'firm', 'location', 'asin/fsn', 
                'model name', 'model', 'qty', 'order amt', 'unit price', 
                'payment', 'card offer', 'status', 'actions'
            ]
            
            missing_headers = []
            for header in EXPECTED_HEADERS:
                # Flexibilities handle karna jo aapke loop me nested hain (e.g. order_id vs order id)
                if header == 'order_id' and ('order id' in uploaded_headers or 'order_id' in uploaded_headers):
                    continue
                if header == 'model' and ('model' in uploaded_headers or 'model no' in uploaded_headers or 'model number' in uploaded_headers):
                    continue
                if header == 'qty' and ('qty' in uploaded_headers or 'order qty' in uploaded_headers):
                    continue
                if header == 'payment' and ('payment' in uploaded_headers or 'payment amt' in uploaded_headers):
                    continue
                if header == 'asin/fsn' and ('asin/fsn' in uploaded_headers or 'fsn' in uploaded_headers):
                    continue
                if header == 'txn date' and ('txn date' in uploaded_headers or 'order date' in uploaded_headers):
                    continue
                
                # Agar inme se koi bhi column na mile to error list me add karein
                if header not in uploaded_headers:
                    missing_headers.append(header.replace('_', ' ').title())

            # Agar koi bhi header missing ya mismatched mila to turant abort kar do
            if missing_headers:
                error_msg = f"Excel format mismatch! Missing or incorrect columns: {', '.join(missing_headers)}. Upload aborted!"
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            # --- 🔥 EXCEL HEADER VALIDATION SAMAPT 🔥 ---

            df = df.fillna('')
            df.columns = df.columns.str.strip().str.lower()

            # Master Data Arrays (Strict Match)
            valid_firms = set(Firm.objects.values_list('name', flat=True))
            valid_locations = set(Location.objects.values_list('name', flat=True))
            valid_merchants = set(Merchant.objects.values_list('name', flat=True))
            valid_asins = set(ProductModel.objects.values_list('asin_fsn', flat=True))
            valid_model_names = set(ProductModel.objects.values_list('model_name', flat=True))
            valid_model_nos = set(ProductModel.objects.values_list('model', flat=True))
            
            # 🔥 FIX 1: Ab sirf Order ID nahi, balki (Order ID, ASIN) dono ka JODA (tuple) layenge
            existing_orders = set(OrderReport.objects.values_list('order_id', 'asin_fsn'))

            # INITIALIZE ERROR COUNTERS
            dup_count = 0
            firm_count = 0
            loc_count = 0
            merch_count = 0
            asin_count = 0
            mname_count = 0
            mno_count = 0
            
            # 🔥 FIX 2: File ke andar duplicates rokne ke liye naya set
            file_order_asins = set() 

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

                # 🔥 FIX 3: Combo Check - Agar same order id aur same ASIN mila, tabhi error aayega
                order_asin_combo = (order_id, asin_fsn)
                if order_asin_combo in existing_orders or order_asin_combo in file_order_asins:
                    dup_count += 1
                file_order_asins.add(order_asin_combo)

                # Strict Master Match Checks
                if firm and firm not in valid_firms: firm_count += 1
                if location and location not in valid_locations: loc_count += 1
                if merchant and merchant not in valid_merchants: merch_count += 1
                if asin_fsn and asin_fsn not in valid_asins: asin_count += 1
                if model_name and model_name not in valid_model_names: mname_count += 1
                if model_no and model_no not in valid_model_nos: mno_count += 1

            # 🔥 COMPACT SUMMARY GENERATOR
            error_segments = []
            if dup_count > 0: error_segments.append(f"{dup_count} Duplicate Order+ASIN entry(s)")
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

        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(order_id__icontains=search_query) |
                Q(invoice_no__icontains=search_query) |
                Q(seller_name__icontains=search_query) |
                Q(asin_fsn__icontains=search_query) |
                Q(model_no__icontains=search_query) |
                Q(seller_gstn__icontains=search_query)
            )    

        return queryset

# --- INVOICE SHIPMENT UPLOAD (STRICT COMBINED VALIDATION) ---
class InvoiceShipmentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        file = request.FILES.get('file')
        # --- 🔥 INVOICE EXCEL HEADER VALIDATION 🔥 ---
        uploaded_headers = set(df.columns.str.strip().str.lower())
            
            # Invoice Shipment ke mandatory headers (Aapke model ke hisaab se)
        EXPECTED_HEADERS = [
                'order id', 'txn date', 'firm', 'seller name', 
                'invoice no', 'delivery status', 'delivery date'
            ]
            
        missing_headers = []
        for header in EXPECTED_HEADERS:
                # Flexible matches
                if header == 'order id' and ('order id' in uploaded_headers or 'order_id' in uploaded_headers): continue
                if header == 'txn date' and ('txn date' in uploaded_headers or 'txn_date' in uploaded_headers): continue
                if header == 'seller name' and ('seller name' in uploaded_headers or 'seller_name' in uploaded_headers): continue
                if header == 'invoice no' and ('invoice no' in uploaded_headers or 'invoice_no' in uploaded_headers): continue
                if header == 'delivery status' and ('delivery status' in uploaded_headers or 'delivery_status' in uploaded_headers): continue
                if header == 'delivery date' and ('delivery date' in uploaded_headers or 'delivery_date' in uploaded_headers): continue
                
                if header not in uploaded_headers:
                    missing_headers.append(header.title())

        if missing_headers:
            error_msg = f"Excel format mismatch! Missing columns: {', '.join(missing_headers)}. Upload aborted!"
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
           
        if not file: return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file.name.endswith('.csv'): df = pd.read_csv(file)
            else: df = pd.read_excel(file)
            
            df = df.fillna('')
            df.columns = df.columns.str.strip().str.lower()
            
            # Master Data Lookups
            valid_orders = set(OrderReport.objects.values_list('order_id', flat=True))
            valid_firms = set(Firm.objects.values_list('name', flat=True))
            valid_locations = set(Location.objects.values_list('name', flat=True))
            
            # Model checking lookup: { 'asin': ('model_name', 'model_no') }
            valid_models = {m.asin_fsn: (m.model_name, m.model) for m in ProductModel.objects.all()}
            
            existing_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            
            # 🔥 SMART CHECK: Existing Order + ASIN pairs in Database
            existing_order_items = set(InvoiceShipment.objects.values_list('order_id', 'asin_fsn'))
            
            # Counters
            missing_order_count = 0
            missing_invoice_count = 0
            dup_invoice_count = 0
            dup_item_in_order_count = 0
            master_mismatch_count = 0
            
            file_invoices = set()
            file_order_items = set()

            # --- VALIDATION LOOP ---
            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                if not order_id: continue

                invoice_no = str(row.get('invoice no', row.get('invoice_no', ''))).strip()
                asin_fsn = str(row.get('asin/fsn', row.get('asin_fsn', ''))).strip()
                model_name = str(row.get('model name', '')).strip()
                model_no = str(row.get('model', row.get('model no', ''))).strip()
                firm = str(row.get('firm', '')).strip()
                location = str(row.get('location', '')).strip()

                # 1. Order ID Exist Check
                if order_id not in valid_orders:
                    missing_order_count += 1
                
                # 2. Invoice No Unique Check (Cannot be duplicate)
                if not invoice_no:
                    missing_invoice_count += 1
                else:
                    if invoice_no in existing_invoices or invoice_no in file_invoices:
                        dup_invoice_count += 1
                    file_invoices.add(invoice_no)

                # 3. Same Order ID + Same ASIN Check (Must be different)
                order_item_pair = (order_id, asin_fsn)
                if order_item_pair in existing_order_items or order_item_pair in file_order_items:
                    dup_item_in_order_count += 1
                file_order_items.add(order_item_pair)

                # 4. Master Data & Model Name/No Validation
                if firm and firm not in valid_firms: master_mismatch_count += 1
                if location and location not in valid_locations: master_mismatch_count += 1
                
                if asin_fsn in valid_models:
                    db_model_name, db_model_no = valid_models[asin_fsn]
                    if model_name and model_name != db_model_name: master_mismatch_count += 1
                    if model_no and model_no != db_model_no: master_mismatch_count += 1
                else:
                    if asin_fsn: master_mismatch_count += 1

            # --- ERROR SUMMARY GENERATOR ---
            error_segments = []
            if missing_order_count > 0: error_segments.append(f"{missing_order_count} Order ID(s) not found in Order Reports")
            if missing_invoice_count > 0: error_segments.append(f"{missing_invoice_count} Missing Invoice No(s)")
            if dup_invoice_count > 0: error_segments.append(f"{dup_invoice_count} Duplicate Invoice No(s)")
            if dup_item_in_order_count > 0: error_segments.append(f"{dup_item_in_order_count} Duplicate Item(s) in same Order ID")
            if master_mismatch_count > 0: error_segments.append(f"{master_mismatch_count} Master/Model mismatch(es)")

            if error_segments:
                total_errors = missing_order_count + missing_invoice_count + dup_invoice_count + dup_item_in_order_count + master_mismatch_count
                return Response({"error": f"Validation Failed! Found: {', '.join(error_segments)}. Total {total_errors} errors. No records saved!"}, status=status.HTTP_400_BAD_REQUEST)

            # --- SMART SAVE LOOP (Auto-Fetch from Order Reports) ---
            records = []
            for index, row in df.iterrows():
                order_id = str(row.get('order id', row.get('order_id', ''))).strip()
                asin_fsn = str(row.get('asin/fsn', row.get('asin_fsn', ''))).strip()
                
                if not order_id or not asin_fsn: 
                    continue

                # 🔥 1. Database se exact Order Report fetch karo
                order_data = OrderReport.objects.filter(order_id=order_id, asin_fsn=asin_fsn).first()
                
                if order_data:
                    # 🔥 2. Excel se SIRF nayi Invoice Details lo
                    raw_inv_date = row.get('invoice date', row.get('invoice_date', ''))
                    invoice_date = pd.to_datetime(raw_inv_date, dayfirst=True).strftime('%Y-%m-%d') if raw_inv_date else None
                    
                    invoice_no = str(row.get('invoice no', row.get('invoice_no', ''))).strip()
                    seller_name = str(row.get('seller name', row.get('seller_name', ''))).strip()
                    seller_gstn = str(row.get('seller gstn', row.get('seller_gstn', ''))).strip()
                    invoice_qty = int(float(row.get('inv qty', row.get('invoice_qty', 1)) or 1))
                    invoice_amount = float(row.get('inv amount', row.get('invoice_amount', 0.0)) or 0.0)

                    # 🔥 3. Dono ko milakar Shipment Record banao (Unit price aur baaki sab Auto-Fill from DB)
                    records.append(InvoiceShipment(
                        # --- DATA COMING DIRECTLY FROM ORDER REPORTS DB ---
                        order_id=order_data.order_id,
                        txn_date=order_data.txn_date,
                        firm=order_data.firm,
                        location=order_data.location,
                        asin_fsn=order_data.asin_fsn,
                        model_name=order_data.model_name,
                        model_no=order_data.model_no,
                        unit_price=order_data.unit_price,  # <-- Ye DB se exact calculate hokar aayega
                        
                        # --- DATA COMING FROM EXCEL ---
                        invoice_no=invoice_no,
                        invoice_date=invoice_date,
                        seller_name=seller_name,
                        seller_gstn=seller_gstn,
                        invoice_qty=invoice_qty,
                        invoice_amount=invoice_amount,
                        delivery_status="Pending"
                    ))
            
            InvoiceShipment.objects.bulk_create(records)
            return Response({"message": f"{len(records)} Shipments uploaded successfully!"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def fetch_order_for_shipment(request, order_id):
    orders = OrderReport.objects.filter(order_id=order_id)
    
    if not orders.exists():
        return Response({"error": "Order ID not found in database!"}, status=404)

    order_data = []
    for order in orders:
        # Puraana invoice data check karne wala logic poori tarah hata diya hai.
        # Ab humesha fresh entry layout hi frontend ko milega.
        item_data = {
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
            
            # HUMESHA KHALI (FRESH) FIELDS
            "seller_name": "",
            "seller_gstn": "",
            "invoice_no": "",
            "invoice_date": "",
            "invoice_qty": order.order_qty,     # Base qty default de rahe hain par fields khali rahengi
            "invoice_amount": order.order_amount,
            "delivery_status": "Pending",
            "delivery_date": "",
            
            # Indicator fields hamesha false/null taaki naya record hi bane
            "is_existing": False,
            "shipment_id": None
        }
        order_data.append(item_data)
        
    return Response(order_data, status=200)



#-------------------VIEW Button funtionaity api --------------------
class OrderSummaryView(APIView):
    def get(self, request, pk):
        try:
            # 1. Jis row par click kiya hai, uska Order ID aur FSN nikalo
            order = OrderReport.objects.get(id=pk)
            target_order_id = order.order_id
            target_asin = order.asin_fsn
            
            # 2. SIRF usi Order ID aur usi FSN ka data fetch karo (No Merging)
            shipments = InvoiceShipment.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            inwards = InwardRecord.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            refunds = RefundRecord.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            
            # 3. Delivered Calculations
            delivered_shipments = shipments.filter(delivery_status='Delivered')
            delivered_qty = delivered_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            delivered_amount = float(delivered_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
            # 4. Cancelled Calculations
            cancelled_shipments = shipments.filter(delivery_status='Cancelled')
            cancel_qty = cancelled_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            cancel_amount = float(cancelled_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
            # 5. Inward & Short Calculations
            inward_qty = inwards.aggregate(Sum('inward_qty'))['inward_qty__sum'] or 0
            inward_amount = float(inwards.aggregate(Sum('inward_amount'))['inward_amount__sum'] or 0.0)
            
            short_qty = inwards.aggregate(Sum('short_qty'))['short_qty__sum'] or 0
            short_amount = float(inwards.aggregate(Sum('short_amount'))['short_amount__sum'] or 0.0)

            # 6. Refund Calculations
            refund_qty = refunds.aggregate(Sum('refund_qty'))['refund_qty__sum'] or 0
            refund_amount = float(refunds.aggregate(Sum('refund_amount'))['refund_amount__sum'] or 0.0)

            # 7. Pending Calculations (Single Item Formula)
            pending_qty = order.order_qty - delivered_qty - cancel_qty
            pending_amount = float(order.order_amount) - delivered_amount - cancel_amount
            pending_refund_amount = cancel_amount + short_amount - refund_amount
            
            # 8. Status Sync (Safety ke liye)
            calculated_status = "Complete" if pending_qty <= 0 else "Open"
            if order.order_status != calculated_status:
                order.order_status = calculated_status
                order.save()

            # 9. Final Response
            summary_data = {
                "order_id": target_order_id,
                "txn_date": order.txn_date,
                "asin_fsn": target_asin,
                "model_no": order.model_no,
                "order_qty": order.order_qty,
                "order_amount": float(order.order_amount),
                "order_status": calculated_status,
                
                "delivered_qty": delivered_qty,
                "delivered_amount": delivered_amount,
                "cancel_qty": cancel_qty,
                "cancel_amount": cancel_amount,
                "short_qty": short_qty, 
                "short_amount": short_amount,
                "refund_qty": refund_qty, 
                "refund_amount": refund_amount,
                "pending_qty": pending_qty,
                "pending_amount": round(pending_amount, 2),
                "pending_refund_amount": round(pending_refund_amount, 2),
                "inward_qty": inward_qty, 
                "inward_amount": inward_amount
            }
            
            return Response(summary_data, status=200)
            
        except OrderReport.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

class ExportOrderReportsExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Shuruat me saara data le lo
        queryset = OrderReport.objects.all()

        # 🔥 SMART FILTERS: Frontend se aane wale filters ko catch karo
        merchant = request.query_params.get('merchant')
        status = request.query_params.get('order_status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        search = request.query_params.get('search') # Agar koi search bar hai

        # Filter apply karo agar value aayi hai
        if merchant:
            queryset = queryset.filter(merchant__icontains=merchant)
        if status:
            queryset = queryset.filter(order_status__iexact=status)
        if start_date and end_date:
            queryset = queryset.filter(txn_date__range=[start_date, end_date])
        if search:
            queryset = queryset.filter(order_id__icontains=search) # Ya kisi aur field me search

        # Filtered data ko columns ke sath nikalna
        data = queryset.values(
            'order_id', 'txn_date', 'merchant', 'firm', 'location', 
            'asin_fsn', 'model_name', 'model_no', 'order_status', 
            'order_qty', 'order_amount'
        )
        
        df = pd.DataFrame(list(data))
        if df.empty:
            df = pd.DataFrame(columns=['Order ID', 'Date', 'No Data Found For This Filter'])
        else:
            df.columns = [col.replace('_', ' ').title() for col in df.columns]

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Filtered_Order_Reports.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Orders')

        return response   


class ExportInvoiceShipmentExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = InvoiceShipment.objects.all()

        # 🔥 SMART FILTERS FOR INVOICE
        merchant = request.query_params.get('merchant')
        invoice_no = request.query_params.get('invoice_no')
        
        if merchant:
            # Column ka naam 'firm' hai database mein, isliye firm__icontains lagega
            queryset = queryset.filter(firm__icontains=merchant)
            
        if invoice_no:
            queryset = queryset.filter(invoice_no__icontains=invoice_no)

        data = queryset.values(
            'invoice_no', 'invoice_date', 'order_id', 'asin_fsn', 
            'model_name', 'invoice_qty', 'invoice_amount'
        )
        
        df = pd.DataFrame(list(data))
        if df.empty:
            df = pd.DataFrame(columns=['Invoice No', 'Date', 'No Data Found For This Filter'])
        else:
            df.columns = [col.replace('_', ' ').title() for col in df.columns]

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Invoice_Shipments.xlsx"'
        
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Invoices')

        return response   

# Bulk delete API for admin --------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_orders(request):
    ids_to_delete = request.data.get('ids', [])
    if not ids_to_delete:
        return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        deleted_count, _ = OrderReport.objects.filter(id__in=ids_to_delete).delete()
        return Response({"message": f"Successfully deleted {deleted_count} Order Report(s)."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- BULK DELETE FOR INVOICE SHIPMENTS ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_invoices(request):
    ids_to_delete = request.data.get('ids', [])
    if not ids_to_delete:
        return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        deleted_count, _ = InvoiceShipment.objects.filter(id__in=ids_to_delete).delete()
        return Response({"message": f"Successfully deleted {deleted_count} Invoice Shipment(s)."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        