# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.decorators import api_view,permission_classes
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.exceptions import PermissionDenied
# from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant, ProductModel, InvoiceShipment,OrderReport,InwardRecord, RefundRecord,ProductModel,Seller,ApprovalRequest,GRPORecord,Ticket
# from .serializers import OrderReportSerializer, ColumnVisibilityPolicySerializer, FirmSerializer, LocationSerializer, MerchantSerializer, ProductModelSerializer, InvoiceShipmentSerializer,SellerSerializer,ApprovalRequestSerializer,ApprovalRequestSerializer, FirmDropdownSerializer, LocationDropdownSerializer, MerchantDropdownSerializer, ModelDropdownSerializer,GRPORecordSerializer,TicketSerializer,RefundRecordSerializer
# import pandas as pd
# from django.utils import timezone
# from django.db.models import Sum, Count
# from rest_framework.decorators import action
# from django.db.models import Q
# from django.http import HttpResponse
# import csv
# import math
# import datetime
# from rest_framework.pagination import PageNumberPagination
# from django.db.models import Sum
# import io
# from datetime import datetime
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from .models import ApprovalRequest

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 50
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

# # API 1: Fetch all records & Create Single Record manually
# class OrderReportListCreateView(generics.ListCreateAPIView):
#     serializer_class = OrderReportSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = StandardResultsSetPagination

#     def get_queryset(self):
#         queryset = OrderReport.objects.all().order_by('-id')
        
#         # URL se Filters get karna
#         start_date = self.request.query_params.get('start_date')
#         end_date = self.request.query_params.get('end_date')
#         firm = self.request.query_params.get('firm')
#         location = self.request.query_params.get('location')
#         model_no = self.request.query_params.get('model_no')
#         txn_detail = self.request.query_params.get('txn_detail')
#         order_status = self.request.query_params.get('order_status')
        
#         # 🔥 GLOBAL SEARCH PARAMETER
#         search_query = self.request.query_params.get('search')

#         if start_date: queryset = queryset.filter(txn_date__gte=start_date)
#         if end_date: queryset = queryset.filter(txn_date__lte=end_date)
#         if firm: queryset = queryset.filter(firm__icontains=firm)
#         if location: queryset = queryset.filter(location__icontains=location)
#         if model_no: queryset = queryset.filter(model_no__icontains=model_no)
#         if txn_detail: queryset = queryset.filter(txn_detail__icontains=txn_detail)
#         if order_status: queryset = queryset.filter(order_status=order_status)

#         # 🔥 GLOBAL SEARCH LOGIC (Kisi bhi column me search karega)
#         if search_query:
#             queryset = queryset.filter(
#                 Q(order_id__icontains=search_query) |
#                 Q(firm__icontains=search_query) |
#                 Q(merchant__icontains=search_query) |
#                 Q(location__icontains=search_query) |
#                 Q(asin_fsn__icontains=search_query) |
#                 Q(model_name__icontains=search_query) |
#                 Q(model_no__icontains=search_query) |
#                 Q(txn_detail__icontains=search_query)
#             )

#         return queryset



# class BulkUploadExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
#         if not file: 
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # 1. 🚀 Encoding Fail-Safe File Reader
#             if file.name.endswith('.csv'): 
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252') 
#             else: 
#                 df = pd.read_excel(file)
            
#             # --- 🔥 SMART EXCEL HEADER MAPPING FOR ORDERS 🔥 ---
#             column_map = {
#                 'order_id': ['order id', 'order_id', 'orderno', 'amazon order id'],
#                 'txn_date': ['txn date', 'txn_date', 'transaction date', 'order date'],
#                 'month': ['month'],
#                 'day': ['day'],
#                 'txn_detail': ['txn detail', 'txn_detail', 'detail'],
#                 'merchant': ['merchant', 'merchant name', 'vendor'],
#                 'merchant_id': ['merchant id', 'merchant_id'],
#                 'firm': ['firm', 'company'],
#                 'location': ['location', 'branch', 'warehouse', 'shipping address'],
#                 'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'product id'],
#                 'model_name': ['model name', 'model_name', 'product name'],
#                 'model': ['model', 'model no', 'model number'],
#                 'qty': ['qty', 'quantity', 'order qty', 'item quantity'],
#                 'order_amt': ['order amt', 'order_amt', 'order amount', 'item net total', 'total amount'],
#                 'unit_price': ['unit price', 'unit_price', 'price', 'rate'],
#                 'payment': ['payment', 'payment mode', 'type'],
#                 'card_offer': ['card offer', 'card_offer', 'offer'],
#                 'card_no': ['card no', 'card_no', 'card number'],
#                 'placed_by': ['placed by', 'placed_by', 'operator'],
#                 'seller_name': ['seller name', 'seller_name'],
#                 'seller_gstn': ['seller gstn', 'seller_gstn', 'gstin']
#             }

#             # 2. Normalize uploaded file headers (lowercase + strip spaces)
#             df.columns = df.columns.str.strip().str.lower()
#             uploaded_headers = set(df.columns)
            
#             # 3. Validation: Only enforce absolutely critical fields for matching
#             REQUIRED_FIELDS = ['order_id', 'asin_fsn'] 
#             missing_critical = []
            
#             actual_column_names = {} 
#             for db_key, aliases in column_map.items():
#                 clean_aliases = [alias.lower().strip() for alias in aliases]
#                 found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
#                 if found_col:
#                     actual_column_names[db_key] = found_col
#                 elif db_key in REQUIRED_FIELDS:
#                     missing_critical.append(db_key.upper())

#             if missing_critical:
#                 error_msg = f"Excel Validation Error! Missing critical columns: {', '.join(missing_critical)}."
#                 return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

#             df = df.fillna('')
            
#             # --- Bulletproof Extractor Function ---
#             def get_val(row_data, db_field_key, return_type='str'):
#                 col_name = actual_column_names.get(db_field_key)
#                 if not col_name or col_name not in row_data:
#                     return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                
#                 val = row_data[col_name]
#                 if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
#                     return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                
#                 if return_type == 'num':
#                     try: 
#                         return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
#                     except: 
#                         return 0.0
#                 return str(val).strip()

#             # 4. Smart Processing & Bulk Creation
#             records = []
#             for index, row in df.iterrows():
#                 order_id = get_val(row, 'order_id')
#                 asin_fsn = get_val(row, 'asin_fsn')
                
#                 if not order_id or not asin_fsn: 
#                     continue    
                
#                 raw_txn_date = get_val(row, 'txn_date')
#                 try:
#                     # Parse standard datetime format safely
#                     txn_date = pd.to_datetime(raw_txn_date, dayfirst=True).strftime('%Y-%m-%d') if raw_txn_date else None
#                 except:
#                     txn_date = None

#                 records.append(OrderReport(
#                     order_id=order_id,
#                     txn_date=txn_date,
#                     month=get_val(row, 'month'),
#                     day=get_val(row, 'day'),
#                     txn_detail=get_val(row, 'txn_detail'),
#                     merchant=get_val(row, 'merchant'),
#                     merchant_id=get_val(row, 'merchant_id'),
#                     firm=get_val(row, 'firm'),
#                     location=get_val(row, 'location'),
#                     asin_fsn=asin_fsn,
#                     model_name=get_val(row, 'model_name'),
                    
#                     # 🔥 EXACT MATCH FROM YOUR MODELS.PY 🔥
#                     model_no=get_val(row, 'model'), 
#                     order_qty=int(get_val(row, 'qty', 'num') or 1),
#                     order_amount=get_val(row, 'order_amt', 'num'),
                    
#                     unit_price=get_val(row, 'unit_price', 'num'),
#                     card_offer=get_val(row, 'card_offer', 'num'),
#                     card_no=get_val(row, 'card_no'),
#                     placed_by=get_val(row, 'placed_by'),
#                     seller_name=get_val(row, 'seller_name'),
#                     seller_gstn=get_val(row, 'seller_gstn'),
#                     payment_amount=get_val(row, 'payment')
#                 ))
            
#             # ignore_conflicts=True handles duplicate rows safely without throwing 500
#             OrderReport.objects.bulk_create(records, ignore_conflicts=True)
#             return Response({"message": f"Successfully parsed and saved {len(records)} Orders smartly!"}, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# # Nayi API View: Edit aur Delete ke liye
# class OrderReportDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = OrderReport.objects.all()
#     serializer_class = OrderReportSerializer # (FIX: Double serializer hta diya gaya hai)
#     permission_classes = [IsAuthenticated]

#     # Security Layer: Only Admin can EDIT records
#     def perform_update(self, serializer):
#         if self.request.user.role != 'ADMIN':
#             raise PermissionDenied("Access Denied: Only Admins can modify order entries.")
#         serializer.save()

#     # Security Layer: Only Admin can DELETE records
#     def perform_destroy(self, instance):
#         if self.request.user.role != 'ADMIN':
#             raise PermissionDenied("Access Denied: Only Admins can delete order entries.")
#         instance.delete()  

# class ColumnVisibilityView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         p_name = request.query_params.get('policy_name', 'user_view_policy')
#         policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
#         serializer = ColumnVisibilityPolicySerializer(policy)
#         return Response(serializer.data)

#     def put(self, request):
#         if request.user.role != 'ADMIN':
#             return Response({"error": "Access Denied: Only Admins can modify view settings."}, status=403)
        
#         p_name = request.query_params.get('policy_name', 'user_view_policy')
#         policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
        
#         serializer = ColumnVisibilityPolicySerializer(policy, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)   

# # class FirmViewSet(viewsets.ModelViewSet):
# #     queryset = Firm.objects.all().order_by('-id')
# #     serializer_class = FirmSerializer
# #     permission_classes = [IsAuthenticated]

# # class LocationViewSet(viewsets.ModelViewSet):
# #     queryset = Location.objects.all().order_by('-id')
# #     serializer_class = LocationSerializer
# #     permission_classes = [IsAuthenticated]

# # class MerchantViewSet(viewsets.ModelViewSet):
# #     queryset = Merchant.objects.all().order_by('-id')
# #     serializer_class = MerchantSerializer
# #     permission_classes = [IsAuthenticated]    

# # class SellerViewSet(viewsets.ModelViewSet):
# #     serializer_class = SellerSerializer  # Dhyan rahe aapka serializer imported ho
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         queryset = Seller.objects.all().order_by('-id')
# #         search_query = self.request.query_params.get('search')
# #         if search_query:
# #             queryset = queryset.filter(
# #                 Q(name__icontains=search_query) |
# #                 Q(gstn_no__icontains=search_query) |
# #                 Q(sap_polyshri__icontains=search_query) |
# #                 Q(sap_rio__icontains=search_query) |
# #                 Q(sap_ne__icontains=search_query) |
# #                 Q(sap_sms__icontains=search_query) |
# #                 Q(sap_smmpl__icontains=search_query)
# #             )
# #         return queryset

# #     # 🔥 UPLOAD ACTION
# #     @action(detail=False, methods=['post'])
# #     def upload(self, request):
# #         file = request.FILES.get('file')
# #         if not file:
# #             return Response({"error": "Please upload a valid Excel or CSV file."}, status=status.HTTP_400_BAD_REQUEST)
# #         try:
# #             if file.name.endswith('.csv'): df = pd.read_csv(file)
# #             else: df = pd.read_excel(file)
            
# #             df = df.where(pd.notnull(df), None)
# #             created_count, updated_count = 0, 0
# #             for _, row in df.iterrows():
# #                 gstn = str(row.get('gstn_no', '')).strip()
# #                 if not gstn or gstn == 'None' or gstn == 'nan': continue  
                
# #                 name = str(row.get('name', '')).strip()
# #                 obj, created = Seller.objects.update_or_create(
# #                     gstn_no=gstn,
# #                     defaults={
# #                         'name': name,
# #                         'sap_polyshri': row.get('sap_polyshri'),
# #                         'sap_rio': row.get('sap_rio'),
# #                         'sap_ne': row.get('sap_ne'),
# #                         'sap_sms': row.get('sap_sms'),
# #                         'sap_smmpl': row.get('sap_smmpl'),
# #                     }
# #                 )
# #                 if created: created_count += 1
# #                 else: updated_count += 1
# #             return Response({"message": f"Success! Added {created_count} new, Updated {updated_count} existing."}, status=status.HTTP_200_OK)
# #         except Exception as e:
# #             return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

# #     # 🔥 EXPORT ALL ACTION
# #     @action(detail=False, methods=['get'])
# #     def export_data(self, request):
# #         response = HttpResponse(content_type='text/csv')
# #         response['Content-Disposition'] = 'attachment; filename="All_Vendors_List.csv"'
# #         writer = csv.writer(response)
# #         writer.writerow(['GSTN Number', 'Seller Name', 'SAP Polyshri', 'SAP Rio', 'SAP NE', 'SAP SMS', 'SAP SMMPL'])
# #         for obj in Seller.objects.all().order_by('-id'):
# #             writer.writerow([obj.gstn_no, obj.name, obj.sap_polyshri, obj.sap_rio, obj.sap_ne, obj.sap_sms, obj.sap_smmpl])
# #         return response


# # # --- 🚀 2. PRODUCT MODEL VIEWSET ---
# # class ProductModelViewSet(viewsets.ModelViewSet):
# #     serializer_class = ProductModelSerializer # Dhyan rahe aapka serializer imported ho
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         queryset = ProductModel.objects.all().order_by('-id')
# #         search_query = self.request.query_params.get('search')
# #         if search_query:
# #             queryset = queryset.filter(
# #                 Q(asin_fsn__icontains=search_query) |
# #                 Q(model_name__icontains=search_query) |
# #                 Q(model__icontains=search_query) |
# #                 Q(sap_polyshri__icontains=search_query) |
# #                 Q(sap_rio__icontains=search_query) |
# #                 Q(sap_ne__icontains=search_query) |
# #                 Q(sap_sms__icontains=search_query) |
# #                 Q(sap_smmpl__icontains=search_query)
# #             )
# #         return queryset

# #     # 🔥 UPLOAD ACTION
# #     @action(detail=False, methods=['post'])
# #     def upload(self, request):
# #         file = request.FILES.get('file')
# #         if not file:
# #             return Response({"error": "Upload valid file."}, status=status.HTTP_400_BAD_REQUEST)
# #         try:
# #             if file.name.endswith('.csv'): df = pd.read_csv(file)
# #             else: df = pd.read_excel(file)
            
# #             df = df.where(pd.notnull(df), None)
# #             created_count, updated_count = 0, 0
# #             for _, row in df.iterrows():
# #                 asin = str(row.get('asin_fsn', '')).strip()
# #                 if not asin or asin == 'None' or asin == 'nan': continue

# #                 obj, created = ProductModel.objects.update_or_create(
# #                     asin_fsn=asin,
# #                     defaults={
# #                         'model_name': row.get('model_name'),
# #                         'model': row.get('model'),
# #                         'sap_polyshri': row.get('sap_polyshri'),
# #                         'sap_rio': row.get('sap_rio'),
# #                         'sap_ne': row.get('sap_ne'),
# #                         'sap_sms': row.get('sap_sms'),
# #                         'sap_smmpl': row.get('sap_smmpl'),
# #                     }
# #                 )
# #                 if created: created_count += 1
# #                 else: updated_count += 1
# #             return Response({"message": f"Added {created_count}, Updated {updated_count} models."}, status=status.HTTP_200_OK)
# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# #     # 🔥 EXPORT ALL ACTION
# #     @action(detail=False, methods=['get'])
# #     def export_data(self, request):
# #         response = HttpResponse(content_type='text/csv')
# #         response['Content-Disposition'] = 'attachment; filename="All_Models_List.csv"'
# #         writer = csv.writer(response)
# #         writer.writerow(['ASN/FSN', 'Model Name', 'Model', 'SAP Polyshri', 'SAP Rio', 'SAP NE', 'SAP SMS', 'SAP SMMPL'])
# #         for obj in ProductModel.objects.all().order_by('-id'):
# #             writer.writerow([obj.asin_fsn, obj.model_name, obj.model, obj.sap_polyshri, obj.sap_rio, obj.sap_ne, obj.sap_sms, obj.sap_smmpl])
# #         return response

# # 🔥 SMART CRASH-PROOF MIXIN 🔥
# class MasterBulkOperationsMixin:
    
#     # Ye naya function Model dhoondhne me kabhi crash nahi hone dega
#     def get_model_class(self):
#         if hasattr(self, 'queryset') and self.queryset is not None:
#             return self.queryset.model
#         return self.get_queryset().model

#     @action(detail=False, methods=['post'])
#     def upload(self, request):
#         model_class = self.get_model_class() # Safe Call
#         file = request.FILES.get('file')
#         if not file:
#             return Response({"error": "Please upload a valid Excel or CSV file."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             if file.name.endswith('.csv'):
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252')
#             else:
#                 df = pd.read_excel(file)
            
#             df.columns = [str(col).strip().lower().replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
#             df = df.where(pd.notnull(df), None)
            
#             # 3. Smart Header Mapping (Aap Excel me koi bhi header rakho, ye khud match karega)
#             col_map = {
#                 'name': ['name', 'firm name', 'location name', 'merchant name', 'seller name', 'firm', 'location', 'merchant', 'vendor'],
                
#                 # 🔥 FIX: 'gstn no' yahan add kar diya gaya hai 🔥
#                 'gstn_no': ['gstn number', 'gstn_no', 'gstn', 'gstin', 'gstn no'], 
                
#                 'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'asn_fsn'],
#                 'model_name': ['model name', 'model_name'],
#                 'model': ['model code', 'model', 'model no'],
#                 'sap_polyshri': ['sap polyshri', 'sap_polyshri'],
#                 'sap_rio': ['sap rio', 'sap_rio'],
#                 'sap_ne': ['sap ne', 'sap_ne'],
#                 'sap_sms': ['sap sms', 'sap_sms'],
#                 'sap_smmpl': ['sap smmpl', 'sap_smmpl']
#             }

#             actual_cols = {}
#             for db_field, aliases in col_map.items():
#                 for alias in aliases:
#                     if alias in df.columns:
#                         actual_cols[db_field] = alias
#                         break

#             created_count, updated_count = 0, 0
#             for _, row in df.iterrows():
#                 unique_col_name = actual_cols.get(self.unique_field)
#                 if not unique_col_name:
#                     return Response({"error": f"Upload failed! Could not find valid column for '{self.unique_field}'."}, status=status.HTTP_400_BAD_REQUEST)
                
#                 unique_val = str(row.get(unique_col_name, '')).strip()
#                 if not unique_val or unique_val == 'None' or unique_val == 'nan': 
#                     continue  
                
#                 defaults = {}
#                 for field in self.update_fields:
#                     col_name = actual_cols.get(field)
#                     if col_name and row.get(col_name) is not None:
#                         defaults[field] = str(row.get(col_name)).strip()
                
#                 obj, created = model_class.objects.update_or_create(
#                     **{self.unique_field: unique_val}, defaults=defaults
#                 )
#                 if created: created_count += 1
#                 else: updated_count += 1
                
#             return Response({"message": f"Success! Added {created_count} new, Updated {updated_count} existing records."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, methods=['get'])
#     def export_data(self, request):
#         model_class = self.get_model_class() # Safe Call
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename="All_{model_class.__name__}s_List.csv"'
#         writer = csv.writer(response)
        
#         headers = [self.unique_field] + self.update_fields
#         writer.writerow([h.replace('_', ' ').title() for h in headers])
        
#         for obj in model_class.objects.all().order_by('-id'):
#             # Handling None values safely during export
#             row_data = [str(getattr(obj, field)) if getattr(obj, field) is not None else '-' for field in headers]
#             writer.writerow(row_data)
#         return response

#     @action(detail=False, methods=['post'])
#     def bulk_delete(self, request):
#         model_class = self.get_model_class() # Safe Call
#         ids = request.data.get('ids', [])
#         if not ids:
#             return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             deleted_count, _ = model_class.objects.filter(id__in=ids).delete()
#             return Response({"message": f"Successfully deleted {deleted_count} record(s)."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # --- 🚀 5 MASTER VIEWSETS USING THE MIXIN ---

# class FirmViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Firm.objects.all().order_by('-id')
#     serializer_class = FirmSerializer
#     unique_field = 'name'
#     update_fields = [] # Sirf name hai

# class LocationViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Location.objects.all().order_by('-id')
#     serializer_class = LocationSerializer
#     unique_field = 'name'
#     update_fields = []

# class MerchantViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Merchant.objects.all().order_by('-id')
#     serializer_class = MerchantSerializer
#     unique_field = 'name'
#     update_fields = []

# class SellerViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     serializer_class = SellerSerializer  
#     unique_field = 'gstn_no'
#     update_fields = ['name', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

#     def get_queryset(self):
#         queryset = Seller.objects.all().order_by('-id')
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(Q(name__icontains=search) | Q(gstn_no__icontains=search))
#         return queryset

# class ProductModelViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     serializer_class = ProductModelSerializer 
#     unique_field = 'asin_fsn'
#     update_fields = ['model_name', 'model', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

#     def get_queryset(self):
#         queryset = ProductModel.objects.all().order_by('-id')
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(Q(asin_fsn__icontains=search) | Q(model_name__icontains=search) | Q(model__icontains=search))
#         return queryset
# #-------------------------INVOICE SHIPMENT---------------
# class InvoiceShipmentViewSet(viewsets.ModelViewSet):
#     serializer_class = InvoiceShipmentSerializer
#     pagination_class = StandardResultsSetPagination 
#     def get_queryset(self):
    
#         try:
#             queryset = InvoiceShipment.objects.all().order_by('-id')
            
#             # 1. Capture Query Parameters
#             start_date = self.request.query_params.get('start_date')
#             end_date = self.request.query_params.get('end_date')
#             order_id = self.request.query_params.get('order_id')
#             delivery_status = self.request.query_params.get('delivery_status')
#             invoice_no = self.request.query_params.get('invoice_no')
#             firm = self.request.query_params.get('firm')
#             location = self.request.query_params.get('location')

#             # 2. Apply Direct Filters
#             if start_date:
#                 queryset = queryset.filter(txn_date__gte=start_date)
#             if end_date:
#                 queryset = queryset.filter(txn_date__lte=end_date)
#             if order_id:
#                 queryset = queryset.filter(order_id__icontains=order_id)
#             if delivery_status:
#                 queryset = queryset.filter(delivery_status__iexact=delivery_status)
#             if invoice_no:
#                 queryset = queryset.filter(invoice_no__icontains=invoice_no)
#             if firm:
#                 queryset = queryset.filter(firm__iexact=firm)
#             if location:
#                 queryset = queryset.filter(location__iexact=location)

#             # 3. Advanced Global Search Logic
#             search_query = self.request.query_params.get('search', '').strip()
#             if search_query:
#                 queryset = queryset.filter(
#                     Q(order_id__icontains=search_query) |
#                     Q(invoice_no__icontains=search_query) |
#                     Q(seller_name__icontains=search_query) |
#                     Q(asin_fsn__icontains=search_query) |
#                     Q(model_no__icontains=search_query) |
#                     Q(seller_gstn__icontains=search_query) |
#                     Q(tracking_id__icontains=search_query) |
#                     Q(cancel_reason__icontains=search_query) 
#                 )
                
                    

#             return queryset

#         except Exception as e:
#             # 🛑 500 ERROR FAIL-SAFE: Agar database schema aur query me mismatch hua, toh server crash hone ki bajaye safely handle ho jayega
#             print(f"🔥 Error fetching InvoiceShipments: {str(e)}")
#             return InvoiceShipment.objects.none()
#     @action(detail=False, methods=['post'])
#     def bulk_update_status(self, request):
#         ids = request.data.get('ids', [])
#         new_status = request.data.get('delivery_status')
#         new_date = request.data.get('delivery_date')
        
#         if not ids: return Response({"error": "No IDs selected!"}, status=400)
        
#         updated = 0
#         # Loop se save karenge taaki auto-refund wale Signals trigger ho sakein
#         for shipment in InvoiceShipment.objects.filter(id__in=ids):
#             if new_status: shipment.delivery_status = new_status
#             if new_date: shipment.delivery_date = new_date
#             shipment.save()
#             updated += 1
            
#         return Response({"message": f"Successfully updated {updated} shipments."})

# class InvoiceShipmentUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
#         if not file: 
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # 1. Read File with Encoding Fail-Safe
#             if file.name.endswith('.csv'): 
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252') 
#             else: 
#                 df = pd.read_excel(file)
            
#             # --- 🔥 SMART EXCEL HEADER MAPPING 🔥 ---
#             # Aapki batayi hui sheet ke exact names
#             column_map = {
#                 'order_id': ['order id'],
#                 'txn_date': ['order date'], 
#                 'firm': ['account group'], # Account Group map kar diya Firm se
#                 'location': ['shipping address'], # Location map ho rahi hai Shipping Address se
#                 'seller_name': ['seller name'],
#                 'seller_gstn': ['seller gstn', 'seller gstin'],
#                 'invoice_no': ['invoice number', 'invoice no'],
#                 'invoice_date': ['invoice date'],
#                 'invoice_qty': ['shipment quantity', 'item quantity'], # Map updated
#                 'invoice_amount': ['invoice total amount', 'item net total'], # Map updated
#                 'tracking_id': ['carrier tracking #', 'tracking id']
#             }

#             # Normalize headers
#             df.columns = df.columns.str.strip().str.lower()
#             uploaded_headers = set(df.columns)
            
#             # Validation
#             REQUIRED_FIELDS = ['order_id', 'invoice_no'] 
#             missing_critical = []
#             actual_column_names = {} 
#             for db_key, aliases in column_map.items():
#                 clean_aliases = [alias.lower().strip() for alias in aliases]
#                 found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
#                 if found_col:
#                     actual_column_names[db_key] = found_col
#                 elif db_key in REQUIRED_FIELDS:
#                     missing_critical.append(db_key.upper())

#             if missing_critical:
#                 error_msg = f"Excel format error! Missing critical columns: {', '.join(missing_critical)}. Upload aborted!"
#                 return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

#             df = df.fillna('')
            
#             # 4. Master Data Fetches
#             # Fetch valid locations for exact match filtering inside the address string
#             valid_locations_list = list(Location.objects.values_list('name', flat=True))
#             valid_locations_lower = [loc.lower() for loc in valid_locations_list]
            
#             # Fetch all orders at once to avoid querying inside the loop (Speed Optimization)
#             all_orders = {order.order_id: order for order in OrderReport.objects.all()}

#             existing_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            
#             file_invoices = set()
#             missing_order_count = 0
#             dup_invoice_count = 0

#             # --- Extractor Utility ---
#             def get_val(row_data, db_field_key, return_type='str'):
#                 col_name = actual_column_names.get(db_field_key)
#                 if not col_name or col_name not in row_data:
#                     return 0.0 if return_type == 'num' else ''
                
#                 val = row_data[col_name]
#                 if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
#                     return 0.0 if return_type == 'num' else ''
                
#                 if return_type == 'num':
#                     try: return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
#                     except: return 0.0
#                 return str(val).strip()

#             # --- SMART SAVE LOOP ---
#             records = []
#             for index, row in df.iterrows():
#                 order_id = get_val(row, 'order_id')
#                 if not order_id: continue

#                 invoice_no = get_val(row, 'invoice_no')
                
#                 # Check duplicates and missing core orders
#                 if order_id not in all_orders: 
#                     missing_order_count += 1
#                     continue
                
#                 if not invoice_no: 
#                     continue
#                 else:
#                     if invoice_no in existing_invoices or invoice_no in file_invoices: 
#                         dup_invoice_count += 1
#                         continue # Skip saving duplicates
#                     file_invoices.add(invoice_no)

#                 # Linking with Core OrderReport Data (Auto Fetching Fields)
#                 order_data = all_orders[order_id]
                
#                 # 🔥 SMART LOCATION EXTRACTION 🔥
#                 raw_shipping_address = get_val(row, 'location').lower()
#                 final_location = ""
                
#                 if raw_shipping_address:
#                     for i, loc_lower in enumerate(valid_locations_lower):
#                         if loc_lower in raw_shipping_address:
#                             # Location matched with Master Location
#                             final_location = valid_locations_list[i]
#                             break
                
#                 # Handling Date Formatting (Invoice Date)
#                 raw_inv_date = get_val(row, 'invoice_date')
#                 try:
#                     invoice_date = pd.to_datetime(raw_inv_date, dayfirst=True).strftime('%Y-%m-%d') if raw_inv_date else None
#                 except:
#                     invoice_date = None

#                 records.append(InvoiceShipment(
#                     # Autofilled from OrderReports Master Table
#                     order_id=order_data.order_id,
#                     txn_date=order_data.txn_date,
#                     asin_fsn=order_data.asin_fsn,
#                     model_name=order_data.model_name,
#                     model_no=order_data.model_no,
#                     unit_price=order_data.unit_price, 
#                     order_qty=order_data.order_qty,
#                     order_amount=order_data.order_amount,

#                     # Extracted directly from Excel Row
#                     firm=get_val(row, 'firm'), # Account group
#                     location=final_location, # Filtered master location
#                     seller_name=get_val(row, 'seller_name'),
#                     seller_gstn=get_val(row, 'seller_gstn'),
                    
#                     invoice_no=invoice_no,
#                     invoice_date=invoice_date,
#                     invoice_qty=int(get_val(row, 'invoice_qty', 'num') or 1),
#                     invoice_amount=get_val(row, 'invoice_amount', 'num'),
                    
#                     tracking_id=get_val(row, 'tracking_id'),
#                     delivery_status="Pending" # Default status
#                 ))
            
#             # Feedback errors if any files were missed
#             error_segments = []
#             if missing_order_count > 0: error_segments.append(f"Skipped {missing_order_count} row(s): Order ID not found in Master")
#             if dup_invoice_count > 0: error_segments.append(f"Skipped {dup_invoice_count} row(s): Duplicate Invoice No")

#             if records:
#                 InvoiceShipment.objects.bulk_create(records, ignore_conflicts=True)
#                 msg = f"{len(records)} Shipments extracted and uploaded successfully!"
#                 if error_segments:
#                     msg += f" (Note: {', '.join(error_segments)})"
#                 return Response({"message": msg}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"error": f"No valid new records found to save. {', '.join(error_segments)}"}, status=status.HTTP_400_BAD_REQUEST)
            
#         except Exception as e:
#             return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET'])
# def fetch_order_for_shipment(request, order_id):
#     orders = OrderReport.objects.filter(order_id=order_id)
    
#     if not orders.exists():
#         return Response({"error": "Order ID not found in database!"}, status=404)

#     order_data = []
#     for order in orders:
#         # Puraana invoice data check karne wala logic poori tarah hata diya hai.
#         # Ab humesha fresh entry layout hi frontend ko milega.
#         item_data = {
#             "order_id": order.order_id,
#             "txn_date": order.txn_date,
#             "firm": order.firm,
#             "location": order.location,
#             "asin_fsn": order.asin_fsn,
#             "model_name": order.model_name,
#             "model_no": order.model_no,
#             "unit_price": order.unit_price,
#             "order_qty": order.order_qty,
#             "order_amount": order.order_amount,
            
#             # HUMESHA KHALI (FRESH) FIELDS
#             "seller_name": "",
#             "seller_gstn": "",
#             "invoice_no": "",
#             "invoice_date": "",
#             "invoice_qty": order.order_qty,     # Base qty default de rahe hain par fields khali rahengi
#             "invoice_amount": order.order_amount,
#             "delivery_status": "Pending",
#             "delivery_date": "",
#             "tracking_id": "",
            
#             # Indicator fields hamesha false/null taaki naya record hi bane
#             "is_existing": False,
#             "shipment_id": None
#         }
#         order_data.append(item_data)
        
#     return Response(order_data, status=200)



# #-------------------VIEW Button funtionaity api --------------------
# class OrderSummaryView(APIView):
#     def get(self, request, pk):
#         try:
#             # 1. Jis row par click kiya hai, uska Order ID aur FSN nikalo
#             order = OrderReport.objects.get(id=pk)
#             target_order_id = order.order_id
#             target_asin = order.asin_fsn
            
#             # 2. SIRF usi Order ID aur usi FSN ka data fetch karo (No Merging)
#             shipments = InvoiceShipment.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            
#             # 🔥 SAFE FIX: Sirf wahi shipment lo jisme actually seller name ho 🔥
#             first_ship = shipments.exclude(seller_name__exact='').exclude(seller_name__isnull=True).first()
            
#             seller_name_fetched = first_ship.seller_name if first_ship else getattr(order, 'seller_name', '-')
#             seller_gstn_fetched = first_ship.seller_gstn if first_ship else getattr(order, 'seller_gstn', '-')

#             # Fallback for empty strings
#             if not seller_name_fetched or str(seller_name_fetched).strip() == '': seller_name_fetched = '-'
#             if not seller_gstn_fetched or str(seller_gstn_fetched).strip() == '': seller_gstn_fetched = '-'

#             inwards = InwardRecord.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
#             refunds = RefundRecord.objects.filter(order_id=target_order_id) # Refund direct Order ID se nikal rahe hain
            
#             # 3. Delivered Calculations
#             delivered_shipments = shipments.filter(delivery_status='Delivered')
#             delivered_qty = delivered_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
#             delivered_amount = float(delivered_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
#             # 4. Cancelled Calculations
#             cancelled_shipments = shipments.filter(delivery_status='Cancelled')
#             cancel_qty = cancelled_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
#             cancel_amount = float(cancelled_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
#             # 5. Inward & Short Calculations
#             inward_qty = inwards.aggregate(Sum('inward_qty'))['inward_qty__sum'] or 0
#             inward_amount = float(inwards.aggregate(Sum('inward_amount'))['inward_amount__sum'] or 0.0)
            
#             short_qty = inwards.aggregate(Sum('short_qty'))['short_qty__sum'] or 0
#             short_amount = float(inwards.aggregate(Sum('short_amount'))['short_amount__sum'] or 0.0)

#             # 6. Refund Calculations (Ab naye RefundRecord se aayenge)
#             refund_qty = refunds.count() # Kitni items refund hui
#             refund_amount = float(refunds.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)

#             # 7. Pending Calculations (Single Item Formula)
#             pending_qty = order.order_qty - delivered_qty - cancel_qty
#             pending_amount = float(order.order_amount) - delivered_amount - cancel_amount
#             pending_refund_amount = cancel_amount + short_amount - refund_amount
            
#             # 8. Status Sync (Safety ke liye)
#             calculated_status = "Complete" if pending_qty <= 0 else "Open"
#             if order.order_status != calculated_status:
#                 order.order_status = calculated_status
#                 order.save()

#             # 9. Final Response Data (Isme aapki saari naye fields hain)
#             summary_data = {
#                 "order_id": target_order_id,
#                 "txn_date": order.txn_date,
#                 "asin_fsn": target_asin,
#                 "model_no": order.model_no,
#                 "order_qty": order.order_qty,
#                 "order_amount": float(order.order_amount),
#                 "order_status": calculated_status,
                
#                 # 🔥 NEW FIELDS REQUESTED BY YOU 🔥
#                 "card_no": order.card_no or "-",
#                 "placed_by": order.placed_by or "-",
#                 "sap_po_no": getattr(order, 'sap_po_no', '-'), # getattr safe hota hai agar db migrate na hua ho
#                 "seller_name": seller_name_fetched, # Shipment se fetched
#                 "seller_gstn": seller_gstn_fetched, # Shipment se fetched
#                 "cn_amount": float(getattr(order, 'cn_amount', 0.0)),
                
#                 # Metrics
#                 "delivered_qty": delivered_qty,
#                 "delivered_amount": delivered_amount,
#                 "cancel_qty": cancel_qty,
#                 "cancel_amount": cancel_amount,
#                 "short_qty": short_qty, 
#                 "short_amount": short_amount,
#                 "refund_qty": refund_qty, 
#                 "refund_amount": refund_amount,
#                 "pending_qty": pending_qty,
#                 "pending_amount": round(pending_amount, 2),
#                 "pending_refund_amount": round(pending_refund_amount, 2),
#                 "inward_qty": inward_qty, 
#                 "inward_amount": inward_amount,
#                 "grpo_qty": order.grpo_qty,
#                 "grpo_amount": float(order.grpo_amount)
#             }
            
#             return Response(summary_data, status=200)
            
#         except OrderReport.DoesNotExist:
#             return Response({"error": "Order not found"}, status=404)
#         except Exception as e:
#             return Response({"error": f"Error: {str(e)}"}, status=400)
        

# class ExportOrderReportsExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         queryset = OrderReport.objects.all()

#         # 🔥 SMART FILTERS
#         merchant = request.query_params.get('merchant')
#         status_val = request.query_params.get('order_status') 
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         search = request.query_params.get('search') 

#         if merchant:
#             queryset = queryset.filter(merchant__icontains=merchant)
#         if status_val:
#             queryset = queryset.filter(status__iexact=status_val)
#         if start_date and end_date:
#             queryset = queryset.filter(txn_date__range=[start_date, end_date])
#         if search:
#             queryset = queryset.filter(order_id__icontains=search) 

#         data = queryset.values(
#             'order_id', 'txn_date', 'month', 'day', 'txn_detail', 
#             'merchant', 'merchant_id', 'firm', 'location', 
#             'asin_fsn', 'model_name', 'model_no', 
#             'order_qty', 'order_amount', 'unit_price', 
#             'payment_amount', 'card_offer'
#         )
        
#         df = pd.DataFrame(list(data))
#         if df.empty:
#             df = pd.DataFrame(columns=['S.No', 'Order ID', 'Date', 'No Data Found For This Filter'])
#         else:
#             # 🔥 MAGIC: Sabse pehle column (index 0) par S.No add karna (1, 2, 3...)
#             df.insert(0, 'S.No', range(1, len(df) + 1))
            
#             # Columns ko clean format me convert karna
#             df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            
#             # Names ko waisa banana jaisa upload template mein hai
#             df.rename(columns={
#                 'Asin Fsn': 'ASIN/FSN',
#                 'Payment Amount': 'Payment',
#                 'Order Qty': 'Qty',
#                 'Order Amount': 'Order Amt'
#             }, inplace=True)

#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="Filtered_Order_Reports.xlsx"'
        
#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Orders')

#         return response   


# class ExportInvoiceShipmentExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         queryset = InvoiceShipment.objects.all()

#         # 🔥 SMART FILTERS FOR INVOICE
#         merchant = request.query_params.get('merchant')
#         invoice_no = request.query_params.get('invoice_no')
        
#         if merchant:
#             queryset = queryset.filter(firm__icontains=merchant)
            
#         if invoice_no:
#             queryset = queryset.filter(invoice_no__icontains=invoice_no)

#         data = queryset.values(
#             'order_id', 'txn_date', 'firm', 'location', 'seller_name', 'seller_gstn',
#             'invoice_no', 'invoice_date', 'asin_fsn', 'model_name', 'model_no',
#             'invoice_qty', 'invoice_amount', 'unit_price', 'tracking_id', 
#             'delivery_date'
#         )
        
#         df = pd.DataFrame(list(data))
#         if df.empty:
#             df = pd.DataFrame(columns=['S.No', 'Invoice No', 'Date', 'No Data Found For This Filter'])
#         else:
#             # 🔥 MAGIC: Sabse pehle column (index 0) par S.No add karna (1, 2, 3...)
#             df.insert(0, 'S.No', range(1, len(df) + 1))
            
#             # Underscores hata kar proper title case banana (e.g., invoice_no -> Invoice No)
#             df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            
#             df.rename(columns={
#                 'Asin Fsn': 'ASIN/FSN',
#                 'Txn Date': 'Txn Date',
#             }, inplace=True)

#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="Invoice_Shipments.xlsx"'
        
#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Invoices')

#         return response   

# # Bulk delete API for admin --------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_delete_orders(request):
#     ids_to_delete = request.data.get('ids', [])
#     if not ids_to_delete:
#         return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         deleted_count, _ = OrderReport.objects.filter(id__in=ids_to_delete).delete()
#         return Response({"message": f"Successfully deleted {deleted_count} Order Report(s)."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # --- BULK DELETE FOR INVOICE SHIPMENTS ---
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_delete_invoices(request):
#     ids_to_delete = request.data.get('ids', [])
#     if not ids_to_delete:
#         return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         deleted_count, _ = InvoiceShipment.objects.filter(id__in=ids_to_delete).delete()
#         return Response({"message": f"Successfully deleted {deleted_count} Invoice Shipment(s)."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
          
# # MODEL EXCEL UPLOAD API------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated]) # Sirf login wale log/admins kar sakein
# def upload_models_excel(request):
#     if 'file' not in request.FILES:
#         return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

#     file = request.FILES['file']
    
#     try:
#         # Check if file is CSV or Excel
#         if file.name.endswith('.csv'):
#             df = pd.read_csv(file)
#         else:
#             df = pd.read_excel(file)

#         # Excel ke headers ko standardize karna (saare chote akshar, spaces ki jagah underscore)
#         # Taaki agar Excel mein 'Model Name' likha ho toh wo 'model_name' ban jaye
#         df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

#         success_count = 0
#         error_count = 0

#         # Excel ki har row (line) ko check karke save karna
#         for index, row in df.iterrows():
#             try:
#                 # ASIN/FSN sabse zaroori hai, wahi unique ID hai
#                 asin_fsn = str(row.get('asin_fsn') or row.get('asn_fsn') or '').strip()
                
#                 # Agar row khali hai toh skip kar do
#                 if not asin_fsn or asin_fsn == 'nan':
#                     continue 

#                 # update_or_create: Agar ASIN already hai toh baaki data update karega, nahi toh naya banayega
#                 ProductModel.objects.update_or_create(
#                     asin_fsn=asin_fsn,
#                     defaults={
#                         'model_name': str(row.get('model_name', '')).strip() if pd.notna(row.get('model_name')) else "",
#                         'model': str(row.get('model', '')).strip() if pd.notna(row.get('model')) else "",
#                         'sap_polyshri': str(row.get('sap_polyshri', '')).strip() if pd.notna(row.get('sap_polyshri')) else "",
#                         'sap_rio': str(row.get('sap_rio', '')).strip() if pd.notna(row.get('sap_rio')) else "",
#                         'sap_ne': str(row.get('sap_ne', '')).strip() if pd.notna(row.get('sap_ne')) else "",
#                         'sap_sms': str(row.get('sap_sms', '')).strip() if pd.notna(row.get('sap_sms')) else "",
#                         'sap_smmpl': str(row.get('sap_smmpl', '')).strip() if pd.notna(row.get('sap_smmpl')) else "",
#                     }
#                 )
#                 success_count += 1
#             except Exception as row_err:
#                 print(f"Error saving row {index}: {row_err}")
#                 error_count += 1

#         return Response({
#             "message": f"Upload successful! Saved/Updated {success_count} models. Failed: {error_count}."
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f"Excel Upload Error: {e}")
#         return Response({"error": "Failed to read the Excel file. Make sure format is correct."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
      
# class ApprovalViewSet(viewsets.ModelViewSet):
#     serializer_class = ApprovalRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user_role = getattr(self.request.user, 'role', None)
#         username = getattr(self.request.user, 'username', str(self.request.user))
        
#         if user_role == 'ADMIN' or self.request.user.is_superuser or self.request.user.is_staff:
#             return ApprovalRequest.objects.all().order_by('-id')
            
#         return ApprovalRequest.objects.filter(
#             Q(requested_by__iexact=username) | Q(placed_by__iexact=username)
#         ).order_by('-id')

#     @action(detail=False, methods=['get'])
#     def dropdown_data(self, request):
#         return Response({
#             'firms': FirmDropdownSerializer(Firm.objects.all(), many=True).data,
#             'locations': LocationDropdownSerializer(Location.objects.all(), many=True).data,
#             'merchants': MerchantDropdownSerializer(Merchant.objects.all(), many=True).data,
#             'models': ModelDropdownSerializer(ProductModel.objects.all(), many=True).data,
#         })

#     # 🔥 1. PRD AUTO-ID GENERATOR (AMZ, FK, RL) 🔥
#     def perform_create(self, serializer):
#         merchant = serializer.validated_data.get('merchant')
#         merchant_name = merchant.name.upper() if merchant else ""
        
#         if 'AMAZON' in merchant_name:
#             prefix = "AMZ"
#         elif 'FLIPKART' in merchant_name:
#             prefix = "FK"
#         else:
#             prefix = "RL"
            
#         last_approval = ApprovalRequest.objects.filter(approval_no__startswith=prefix).order_by('-id').first()
        
#         if last_approval and last_approval.approval_no:
#             try:
#                 last_no = last_approval.approval_no.replace(prefix, "")
#                 new_no = int(last_no) + 1
#             except ValueError:
#                 new_no = 1
#         else:
#             new_no = 1
            
#         new_approval_no = f"{prefix}{str(new_no).zfill(5)}"
#         serializer.save(approval_no=new_approval_no)

#     # 🔥 2. EXACT TIMESTAMP ON APPROVAL 🔥
#     @action(detail=True, methods=['post'])
#     def approve(self, request, pk=None):
#         user_role = getattr(request.user, 'role', None)
#         if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
#             return Response({"error": "Security Alert: Only authorized Admins can approve."}, status=status.HTTP_403_FORBIDDEN)
            
#         approval = self.get_object()
#         approval.status = 'Approved'
        
#         # 🔥 FIX: Ab ye Local Indian Time uthayega 🔥
#         current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
#         approval.authorized_by = f"{request.user.username} ({current_time})"
#         approval.save()
#         return Response({"message": "Approval Request Approved Successfully!"}, status=status.HTTP_200_OK)

#     # 🔥 EXACT IST TIMESTAMP ON REJECT 🔥
#     @action(detail=True, methods=['post'])
#     def reject(self, request, pk=None):
#         user_role = getattr(request.user, 'role', None)
#         if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
#             return Response({"error": "Security Alert: Only authorized Admins can reject."}, status=status.HTTP_403_FORBIDDEN)
            
#         approval = self.get_object()
#         approval.status = 'Rejected'
        
#         # 🔥 FIX: Ab ye Local Indian Time uthayega 🔥
#         current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
#         approval.authorized_by = f"{request.user.username} ({current_time})"
#         approval.save()
#         return Response({"message": "Approval Request Rejected Successfully!"}, status=status.HTTP_200_OK)



# # ------------------------- GRPO VIEWSET -------------------------
# class GRPORecordViewSet(viewsets.ModelViewSet):
#     queryset = GRPORecord.objects.all().order_by('-id')
#     serializer_class = GRPORecordSerializer
#     permission_classes = [IsAuthenticated] # Agar bina login chalana ho toh ise hata dena

#     # 🔥 BULK EXCEL UPLOAD LOGIC 🔥
#     @action(detail=False, methods=['post'])
#     def upload_excel(self, request):
#         file = request.FILES.get('file')
#         if not file:
#             return Response({"error": "Bhai, koi file upload nahi hui!"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Excel ya CSV dono support karega
#             if file.name.endswith('.csv'):
#                 df = pd.read_csv(file)
#             else:
#                 df = pd.read_excel(file)
                
#             # Khali cells ko khali string bana do taaki 'nan' na aaye
#             df = df.fillna('')
            
#             records = []
#             for index, row in df.iterrows():
#                 # Strings safe conversion
#                 grpo_qty = str(row.get('grpo_quantity', '0')).replace(',', '').strip()
#                 grpo_amt = str(row.get('grpo_amt', '0')).replace(',', '').strip()

#                 records.append(GRPORecord(
#                     firm_name=str(row.get('firm_name', '')),
#                     internal_number=str(row.get('internal_number', '')),
#                     grpo_status=str(row.get('grpo_status', 'Open')),
#                     grpo_user_name=str(row.get('grpo_user_name', '')),
#                     grpo_no=str(row.get('grpo_no', '')),
#                     grpo_invoice_number=str(row.get('grpo_invoice_number', '')),
#                     grpo_create_date=str(row.get('grpo_create_date', '')),
#                     grpo_posting_date=str(row.get('grpo_posting_date', '')),
#                     purchase_vendor_code=str(row.get('purchase_vendor_code', '')),
#                     purchase_vendor_name=str(row.get('purchase_vendor_name', '')),
#                     inward_whs_code=str(row.get('inward_whs_code', '')),
#                     item_code=str(row.get('item_code', '')),
#                     description=str(row.get('description', '')),
                    
#                     # Decimal conversion safe math
#                     grpo_quantity=float(grpo_qty) if grpo_qty.replace('.','',1).isdigit() else 0.0,
#                     grpo_amt=float(grpo_amt) if grpo_amt.replace('.','',1).isdigit() else 0.0,
#                 ))
            
#             # Bulk create for blazing fast database insert
#             GRPORecord.objects.bulk_create(records)
#             return Response({"message": f"{len(records)} GRPO records successfully imported!"}, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({"error": f"File process karne me error aaya: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class DownloadApprovalPDF(APIView):
#     # permission_classes = [IsAuthenticated] 

#     def get(self, request, pk):
#         try:
#             approval = ApprovalRequest.objects.get(pk=pk)
#             buffer = io.BytesIO()
#             # Left/Right margins ko thoda kam kiya hai taaki lamba table aaram se fit ho jaye
#             doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
#             elements = []
#             styles = getSampleStyleSheet()

#             # --- 1. HEADER ROW (Title + Timestamp) ---
#             title_style = ParagraphStyle(
#                 name="TitleStyle", fontSize=14, fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a")
#             )
#             timestamp_style = ParagraphStyle(
#                 name="TimestampStyle", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=2
#             )
            
#             generated_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
#             header_table = Table([
#                 [Paragraph(f"<b>{approval.approval_no} — Online Order Placement Tracker</b>", title_style), 
#                  Paragraph(f"Generated: {generated_time}", timestamp_style)]
#             ], colWidths=[550, 240])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
#                 ('BOTTOMPADDING', (0,0), (-1,-1), 10)
#             ]))
#             elements.append(header_table)
#             elements.append(Spacer(1, 15))

#             # --- 2. TOP DETAILS GRID ---
#             firm_name = approval.firm.name if hasattr(approval, 'firm') and approval.firm else "-"
#             ship_loc = approval.ship_location.name if hasattr(approval, 'ship_location') and approval.ship_location else "-"
#             bill_loc = approval.bill_location.name if hasattr(approval, 'bill_location') and approval.bill_location else "-"
#             merchant_name = approval.merchant.name if hasattr(approval, 'merchant') and approval.merchant else "-"

#             data_top = [
#                 ["Approval Date:", approval.request_date.strftime('%d/%m/%Y') if approval.request_date else "-", "Order Requested By:", str(approval.requested_by or "-")],
#                 ["Firm Name:", firm_name, "Merchant:", merchant_name],
#                 ["Ship Location:", ship_loc, "Merchant_ID:", str(approval.merchant_account_id or "-")],
#                 ["Bill Location:", bill_loc, "Authorized By:", str(approval.authorized_by or "-")]
#             ]
            
#             t_top = Table(data_top, colWidths=[90, 260, 110, 310])
#             t_top.setStyle(TableStyle([
#                 ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), 
#                 ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'), 
#                 ('FONTSIZE', (0,0), (-1,-1), 9),
#                 ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
#                 ('BOTTOMPADDING', (0,0), (-1,-1), 5),
#             ]))
#             elements.append(t_top)
#             elements.append(Spacer(1, 20))

#             # --- 3. ITEMS TABLE WITH TEXT WRAPPING ---
#             # Paragraph Styles text ko cut hone se bachane ke liye (Text-Wrapping)
#             cell_style = ParagraphStyle(name='CellStyle', fontSize=7, leading=9, textColor=colors.HexColor("#475569"))
#             header_cell_style = ParagraphStyle(name='HeaderCellStyle', fontSize=8, leading=10, textColor=colors.white, fontName='Helvetica-Bold')

#             headers = [
#                 Paragraph("<b>ASIN/FSN</b>", header_cell_style), Paragraph("<b>Model</b>", header_cell_style), 
#                 Paragraph("<b>Req<br/>Qty</b>", header_cell_style), Paragraph("<b>Purchase<br/>Price</b>", header_cell_style), 
#                 Paragraph("<b>CN</b>", header_cell_style), Paragraph("<b>Agreed<br/>NLC</b>", header_cell_style), 
#                 Paragraph("<b>Link<br/>Used</b>", header_cell_style), Paragraph("<b>Placed<br/>Qty</b>", header_cell_style), 
#                 Paragraph("<b>Order<br/>NLC</b>", header_cell_style), Paragraph("<b>Payment<br/>Method</b>", header_cell_style), 
#                 Paragraph("<b>Delivery<br/>Date</b>", header_cell_style), Paragraph("<b>Total<br/>Cost</b>", header_cell_style)
#             ]
            
#             item_data = [headers]
#             total_req_qty = 0
#             total_placed_qty = 0
#             total_cost_sum = 0.0

#             for item in approval.items.all():
#                 req_qty = item.req_qty or 0
#                 placed_qty = item.placed_qty or 0
#                 tot_cost = float(item.total_placed_amt or 0)
                
#                 total_req_qty += req_qty
#                 total_placed_qty += placed_qty
#                 total_cost_sum += tot_cost

#                 del_date = item.expected_delivery_date.strftime('%d/%m/%Y') if item.expected_delivery_date else "-"

#                 item_data.append([
#                     Paragraph(str(item.asin_fsn or "-"), cell_style), 
#                     Paragraph(str(item.model_name or "-"), cell_style), 
#                     str(req_qty), 
#                     f"Rs. {item.purchase_price or 0}",
#                     f"Rs. {item.cn_amt or 0}", 
#                     f"Rs. {item.agreed_nlc or 0}", 
#                     str(item.link_used or "-"), 
#                     str(placed_qty),
#                     f"Rs. {item.order_nlc or 0}", 
#                     Paragraph(str(item.payment_method or "-"), cell_style), 
#                     Paragraph(del_date, cell_style),
#                     f"Rs. {tot_cost}"
#                 ])

#             # Totals Row
#             item_data.append([
#                 "Total", "", str(total_req_qty), "", "", "", "", str(total_placed_qty), "", "", "", f"Rs. {total_cost_sum}"
#             ])

#             # Exact widths calculation to fit A4 Landscape (Total ~790 points)
#             t_items = Table(item_data, colWidths=[75, 140, 30, 55, 45, 55, 30, 35, 55, 70, 55, 60])
            
#             table_style = TableStyle([
#                 ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")), 
#                 ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#                 ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
#                 ('BOTTOMPADDING', (0,0), (-1,0), 6),
#                 ('TOPPADDING', (0,0), (-1,0), 6),
#                 ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
#                 ('FONTSIZE', (0,1), (-1,-2), 8),
#                 ('TEXTCOLOR', (0,1), (-1,-2), colors.HexColor("#475569")),
#                 ('BOTTOMPADDING', (0,1), (-1,-1), 5),
#                 ('TOPPADDING', (0,1), (-1,-1), 5),
#                 ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#e2e8f0")), 
#             ])
            
#             for i in range(1, len(item_data)-1):
#                 if i % 2 == 0:
#                     table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8fafc"))
                    
#             table_style.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#fef3c7"))
#             table_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
#             table_style.add('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#000000"))
#             table_style.add('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#eab308"))
            
#             t_items.setStyle(table_style)
#             elements.append(t_items)
#             elements.append(Spacer(1, 40))

#             # --- 4. SIGNATURE SECTIONS (Dynamically picking up Admin's name) ---
#             req_by_text = approval.requested_by if approval.requested_by else "_________________________"
#             placed_by_text = approval.placed_by if approval.placed_by else "_________________________"
            
#             # 🔥 APPROVED BY MEIN ADMIN KA NAAM YAHAN AAYEGA 🔥
#             approved_by_text = approval.authorized_by if approval.authorized_by else "_________________________"

#             sig_data = [
#                 ["Order Requested By", "Order Placed By", "Order Approved By"],
#                 [f"\n\n\n{req_by_text}", f"\n\n\n{placed_by_text}", f"\n\n\n{approved_by_text}"]
#             ]
#             t_sigs = Table(sig_data, colWidths=[260, 260, 260])
#             t_sigs.setStyle(TableStyle([
#                 ('ALIGN', (0,0), (-1,-1), 'CENTER'),
#                 ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0,0), (-1,0), 9),
#                 ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#334155")),
#                 ('FONTNAME', (0,1), (-1,1), 'Helvetica'), # Name lines in normal font
#                 ('FONTSIZE', (0,1), (-1,1), 9),
#             ]))
#             elements.append(t_sigs)
#             elements.append(Spacer(1, 30))
            
#             disclaimer = ParagraphStyle(name="Disclaimer", fontSize=7, textColor=colors.HexColor("#94a3b8"))
#             elements.append(Paragraph(f"This document was generated automatically on {generated_time} upon approval.", disclaimer))

#             doc.build(elements)
#             pdf = buffer.getvalue()
#             buffer.close()
            
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="Approval_{approval.approval_no}.pdf"'
#             return response
            
#         except Exception as e:
#             return HttpResponse(f"Error generating PDF: {str(e)}", status=400)    


# class TicketViewSet(viewsets.ModelViewSet):
#     queryset = Ticket.objects.all().order_by('-id')
#     serializer_class = TicketSerializer

# class RefundRecordViewSet(viewsets.ModelViewSet):
#     queryset = RefundRecord.objects.all().order_by('-id')
#     serializer_class = RefundRecordSerializer
#     permission_classes = [IsAuthenticated]


# # --- ORDER CANCEL API (Manual Cancel in Order Report) ---
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def cancel_order_to_refund(request, pk):
#     try:
#         order = OrderReport.objects.get(pk=pk)
#         order.order_status = 'Complete' # Aapki requirement: "status completed ho jayega iska"
#         order.save()
        
#         # Add to Refund Tab
#         RefundRecord.objects.create(
#             source_date=order.txn_date,
#             firm=order.firm,
#             merchant=order.merchant,
#             order_id=order.order_id,
#             invoice_no="-", # Direct order cancel me invoice nahi hota
#             model_name=order.model_name,
#             invoice_amount=order.order_amount,
#             received_comment="cancel confirmed"
#         )
#         return Response({"message": "Order Cancelled and Moved to Refunds!"})
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)
    


# # live dashboard API

# class DashboardStatsView(APIView):
#     def get(self, request):
#         try:
#             # 1. KPI Calculations
#             total_orders = OrderReport.objects.count()
#             open_orders = OrderReport.objects.filter(order_status='Open').count()
#             completed_orders = OrderReport.objects.filter(order_status='Complete').count()
            
#             # Total Revenue Calculation
#             revenue_data = OrderReport.objects.aggregate(total_revenue=Sum('order_amount'))
#             total_revenue = float(revenue_data['total_revenue'] or 0.0)

#             # 2. Pie Chart (Sales by Merchant)
#             merchants_data = OrderReport.objects.values('merchant').annotate(
#                 total_sales=Sum('order_amount')
#             ).order_by('-total_sales')

#             pie_data = []
#             for item in merchants_data:
#                 merchant_name = item['merchant'] or 'Others'
#                 pie_data.append({
#                     "name": merchant_name,
#                     "value": float(item['total_sales'] or 0.0)
#                 })

#             return Response({
#                 "kpis": {
#                     "totalOrders": total_orders,
#                     "openOrders": open_orders,
#                     "completed": completed_orders,
#                     "revenue": total_revenue
#                 },
#                 "pieData": pie_data
#             }, status=200)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.decorators import api_view,permission_classes
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.exceptions import PermissionDenied
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors
# from .models import OrderReport, ColumnVisibilityPolicy, Firm, Location, Merchant, ProductModel,PurchaseInward, InvoiceShipment,OrderReport,InwardRecord, RefundRecord,ProductModel,Seller,ApprovalRequest,GRPORecord,Ticket,WarehouseAudit,IMEIRecord,Settlement, FinanceReconciliation,UserProfile, RolePermission
# from .serializers import OrderReportSerializer, ColumnVisibilityPolicySerializer, FirmSerializer, LocationSerializer, MerchantSerializer, ProductModelSerializer, InvoiceShipmentSerializer,SellerSerializer,ApprovalRequestSerializer,ApprovalRequestSerializer, FirmDropdownSerializer, LocationDropdownSerializer, MerchantDropdownSerializer, ModelDropdownSerializer,GRPORecordSerializer,TicketSerializer,RefundRecordSerializer,PurchaseInwardSerializer,WarehouseAuditSerializer,IMEIRecordSerializer,UserProfileSerializer, RolePermissionSerializer,SettlementSerializer, FinanceReconciliationSerializer
# import pandas as pd
# from django.utils import timezone
# from django.db.models import Sum, Count
# from rest_framework.decorators import action
# from django.db.models import Q
# from django.http import HttpResponse
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# import csv
# import math
# import datetime
# from rest_framework.pagination import PageNumberPagination
# from django.db.models import Sum
# import io
# from datetime import datetime
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from .models import ApprovalRequest

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 50
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

# # API 1: Fetch all records & Create Single Record manually
# class OrderReportListCreateView(generics.ListCreateAPIView):
#     serializer_class = OrderReportSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = StandardResultsSetPagination

#     def get_queryset(self):
#         queryset = OrderReport.objects.all().order_by('-id')
        
#         # URL se Filters get karna
#         start_date = self.request.query_params.get('start_date')
#         end_date = self.request.query_params.get('end_date')
#         firm = self.request.query_params.get('firm')
#         location = self.request.query_params.get('location')
#         model_no = self.request.query_params.get('model_no')
#         txn_detail = self.request.query_params.get('txn_detail')
#         order_status = self.request.query_params.get('order_status')
        
#         # 🔥 GLOBAL SEARCH PARAMETER
#         search_query = self.request.query_params.get('search')

#         if start_date: queryset = queryset.filter(txn_date__gte=start_date)
#         if end_date: queryset = queryset.filter(txn_date__lte=end_date)
#         if firm: queryset = queryset.filter(firm__icontains=firm)
#         if location: queryset = queryset.filter(location__icontains=location)
#         if model_no: queryset = queryset.filter(model_no__icontains=model_no)
#         if txn_detail: queryset = queryset.filter(txn_detail__icontains=txn_detail)
#         if order_status: queryset = queryset.filter(order_status=order_status)

#         # 🔥 GLOBAL SEARCH LOGIC (Kisi bhi column me search karega)
#         if search_query:
#             queryset = queryset.filter(
#                 Q(order_id__icontains=search_query) |
#                 Q(firm__icontains=search_query) |
#                 Q(merchant__icontains=search_query) |
#                 Q(location__icontains=search_query) |
#                 Q(asin_fsn__icontains=search_query) |
#                 Q(model_name__icontains=search_query) |
#                 Q(model_no__icontains=search_query) |
#                 Q(txn_detail__icontains=search_query)
#             )

#         return queryset


# class BulkUploadExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
#         if not file: 
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # 1. 🚀 Encoding Fail-Safe File Reader
#             if file.name.endswith('.csv'): 
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252') 
#             else: 
#                 df = pd.read_excel(file)
            
#             # --- 🔥 SMART EXCEL HEADER MAPPING FOR ORDERS 🔥 ---
#             column_map = {
#                 'order_id': ['order id', 'order_id', 'orderno', 'amazon order id'],
#                 'txn_date': ['txn date', 'txn_date', 'transaction date', 'order date'],
#                 'month': ['month'],
#                 'day': ['day'],
#                 'txn_detail': ['txn detail', 'txn_detail', 'detail'],
#                 'merchant': ['merchant', 'merchant name', 'vendor'],
#                 'merchant_id': ['merchant id', 'merchant_id'],
#                 'firm': ['firm', 'company'],
#                 'location': ['location', 'branch', 'warehouse', 'shipping address'],
#                 'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'product id'],
#                 'model_name': ['model name', 'model_name', 'product name'],
#                 'model': ['model', 'model no', 'model number'],
#                 'qty': ['qty', 'quantity', 'order qty', 'item quantity'],
#                 'order_amt': ['order amt', 'order_amt', 'order amount', 'item net total', 'total amount'],
#                 'unit_price': ['unit price', 'unit_price', 'price', 'rate'],
#                 'payment': ['payment', 'payment mode', 'type'],
#                 'card_offer': ['card offer', 'card_offer', 'offer'],
#                 'card_no': ['card no', 'card_no', 'card number'],
#                 'placed_by': ['placed by', 'placed_by', 'operator'],
#                 'seller_name': ['seller name', 'seller_name'],
#                 'seller_gstn': ['seller gstn', 'seller_gstn', 'gstin']
#             }

#             # 2. Normalize uploaded file headers (lowercase + strip spaces)
#             df.columns = df.columns.str.strip().str.lower()
#             uploaded_headers = set(df.columns)
            
#             # 3. Validation: Only enforce absolutely critical fields for matching
#             REQUIRED_FIELDS = ['order_id', 'asin_fsn'] 
#             missing_critical = []
            
#             actual_column_names = {} 
#             for db_key, aliases in column_map.items():
#                 clean_aliases = [alias.lower().strip() for alias in aliases]
#                 found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
#                 if found_col:
#                     actual_column_names[db_key] = found_col
#                 elif db_key in REQUIRED_FIELDS:
#                     missing_critical.append(db_key.upper())

#             if missing_critical:
#                 error_msg = f"Excel Validation Error! Missing critical columns: {', '.join(missing_critical)}."
#                 return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

#             df = df.fillna('')
            
#             # --- Bulletproof Extractor Function ---
#             def get_val(row_data, db_field_key, return_type='str'):
#                 col_name = actual_column_names.get(db_field_key)
#                 if not col_name or col_name not in row_data:
#                     return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                
#                 val = row_data[col_name]
#                 if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
#                     return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                
#                 if return_type == 'num':
#                     try: 
#                         return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
#                     except: 
#                         return 0.0
#                 return str(val).strip()

#             # 4. Smart Processing & Bulk Creation
#             records = []
#             for index, row in df.iterrows():
#                 order_id = get_val(row, 'order_id')
#                 asin_fsn = get_val(row, 'asin_fsn')
                
#                 if not order_id or not asin_fsn: 
#                     continue    
                
#                 raw_txn_date = get_val(row, 'txn_date')
#                 try:
#                     # Parse standard datetime format safely
#                     txn_date = pd.to_datetime(raw_txn_date, dayfirst=True).strftime('%Y-%m-%d') if raw_txn_date else None
#                 except:
#                     txn_date = None

#                 records.append(OrderReport(
#                     order_id=order_id,
#                     txn_date=txn_date,
#                     month=get_val(row, 'month'),
#                     day=get_val(row, 'day'),
#                     txn_detail=get_val(row, 'txn_detail'),
#                     merchant=get_val(row, 'merchant'),
#                     merchant_id=get_val(row, 'merchant_id'),
#                     firm=get_val(row, 'firm'),
#                     location=get_val(row, 'location'),
#                     asin_fsn=asin_fsn,
#                     model_name=get_val(row, 'model_name'),
                    
#                     # 🔥 EXACT MATCH FROM YOUR MODELS.PY 🔥
#                     model_no=get_val(row, 'model'), 
#                     order_qty=int(get_val(row, 'qty', 'num') or 1),
#                     order_amount=get_val(row, 'order_amt', 'num'),
                    
#                     unit_price=get_val(row, 'unit_price', 'num'),
#                     card_offer=get_val(row, 'card_offer', 'num'),
#                     card_no=get_val(row, 'card_no'),
#                     placed_by=get_val(row, 'placed_by'),
#                     seller_name=get_val(row, 'seller_name'),
#                     seller_gstn=get_val(row, 'seller_gstn'),
#                     payment_amount=get_val(row, 'payment')
#                 ))
            
#             # ignore_conflicts=True handles duplicate rows safely without throwing 500
#             OrderReport.objects.bulk_create(records, ignore_conflicts=True)
#             return Response({"message": f"Successfully parsed and saved {len(records)} Orders smartly!"}, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# # Nayi API View: Edit aur Delete ke liye
# class OrderReportDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = OrderReport.objects.all()
#     serializer_class = OrderReportSerializer # (FIX: Double serializer hta diya gaya hai)
#     permission_classes = [IsAuthenticated]

#     # Security Layer: Only Admin can EDIT records
#     def perform_update(self, serializer):
#         if self.request.user.role != 'ADMIN':
#             raise PermissionDenied("Access Denied: Only Admins can modify order entries.")
#         serializer.save()

#     # Security Layer: Only Admin can DELETE records
#     def perform_destroy(self, instance):
#         if self.request.user.role != 'ADMIN':
#             raise PermissionDenied("Access Denied: Only Admins can delete order entries.")
#         instance.delete()  

# class ColumnVisibilityView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         p_name = request.query_params.get('policy_name', 'user_view_policy')
#         policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
#         serializer = ColumnVisibilityPolicySerializer(policy)
#         return Response(serializer.data)

#     def put(self, request):
#         if request.user.role != 'ADMIN':
#             return Response({"error": "Access Denied: Only Admins can modify view settings."}, status=403)
        
#         p_name = request.query_params.get('policy_name', 'user_view_policy')
#         policy, created = ColumnVisibilityPolicy.objects.get_or_create(policy_name=p_name)
        
#         serializer = ColumnVisibilityPolicySerializer(policy, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)   

# # 🔥 SMART CRASH-PROOF MIXIN 🔥
# class MasterBulkOperationsMixin:
    
#     # Ye naya function Model dhoondhne me kabhi crash nahi hone dega
#     def get_model_class(self):
#         if hasattr(self, 'queryset') and self.queryset is not None:
#             return self.queryset.model
#         return self.get_queryset().model

#     @action(detail=False, methods=['post'])
#     def upload(self, request):
#         model_class = self.get_model_class() # Safe Call
#         file = request.FILES.get('file')
#         if not file:
#             return Response({"error": "Please upload a valid Excel or CSV file."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             if file.name.endswith('.csv'):
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252')
#             else:
#                 df = pd.read_excel(file)
            
#             df.columns = [str(col).strip().lower().replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
#             df = df.where(pd.notnull(df), None)
            
#             # 3. Smart Header Mapping (Aap Excel me koi bhi header rakho, ye khud match karega)
#             col_map = {
#                 'name': ['name', 'firm name', 'location name', 'merchant name', 'seller name', 'firm', 'location', 'merchant', 'vendor'],
                
#                 # 🔥 FIX: 'gstn no' yahan add kar diya gaya hai 🔥
#                 'gstn_no': ['gstn number', 'gstn_no', 'gstn', 'gstin', 'gstn no'], 
                
#                 'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'asn_fsn'],
#                 'model_name': ['model name', 'model_name'],
#                 'model': ['model code', 'model', 'model no'],
#                 'sap_polyshri': ['sap polyshri', 'sap_polyshri'],
#                 'sap_rio': ['sap rio', 'sap_rio'],
#                 'sap_ne': ['sap ne', 'sap_ne'],
#                 'sap_sms': ['sap sms', 'sap_sms'],
#                 'sap_smmpl': ['sap smmpl', 'sap_smmpl']
#             }

#             actual_cols = {}
#             for db_field, aliases in col_map.items():
#                 for alias in aliases:
#                     if alias in df.columns:
#                         actual_cols[db_field] = alias
#                         break

#             created_count, updated_count = 0, 0
#             for _, row in df.iterrows():
#                 unique_col_name = actual_cols.get(self.unique_field)
#                 if not unique_col_name:
#                     return Response({"error": f"Upload failed! Could not find valid column for '{self.unique_field}'."}, status=status.HTTP_400_BAD_REQUEST)
                
#                 unique_val = str(row.get(unique_col_name, '')).strip()
#                 if not unique_val or unique_val == 'None' or unique_val == 'nan': 
#                     continue  
                
#                 defaults = {}
#                 for field in self.update_fields:
#                     col_name = actual_cols.get(field)
#                     if col_name and row.get(col_name) is not None:
#                         defaults[field] = str(row.get(col_name)).strip()
                
#                 obj, created = model_class.objects.update_or_create(
#                     **{self.unique_field: unique_val}, defaults=defaults
#                 )
#                 if created: created_count += 1
#                 else: updated_count += 1
                
#             return Response({"message": f"Success! Added {created_count} new, Updated {updated_count} existing records."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": f"Error processing file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, methods=['get'])
#     def export_data(self, request):
#         model_class = self.get_model_class() # Safe Call
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename="All_{model_class.__name__}s_List.csv"'
#         writer = csv.writer(response)
        
#         headers = [self.unique_field] + self.update_fields
#         writer.writerow([h.replace('_', ' ').title() for h in headers])
        
#         for obj in model_class.objects.all().order_by('-id'):
#             # Handling None values safely during export
#             row_data = [str(getattr(obj, field)) if getattr(obj, field) is not None else '-' for field in headers]
#             writer.writerow(row_data)
#         return response

#     @action(detail=False, methods=['post'])
#     def bulk_delete(self, request):
#         model_class = self.get_model_class() # Safe Call
#         ids = request.data.get('ids', [])
#         if not ids:
#             return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             deleted_count, _ = model_class.objects.filter(id__in=ids).delete()
#             return Response({"message": f"Successfully deleted {deleted_count} record(s)."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # --- 🚀 5 MASTER VIEWSETS USING THE MIXIN ---

# class FirmViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Firm.objects.all().order_by('-id')
#     serializer_class = FirmSerializer
#     unique_field = 'name'
#     update_fields = [] # Sirf name hai

# class LocationViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Location.objects.all().order_by('-id')
#     serializer_class = LocationSerializer
#     unique_field = 'name'
#     update_fields = []

# class MerchantViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     queryset = Merchant.objects.all().order_by('-id')
#     serializer_class = MerchantSerializer
#     unique_field = 'name'
#     update_fields = []

# class SellerViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     serializer_class = SellerSerializer  
#     unique_field = 'gstn_no'
#     update_fields = ['name', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

#     def get_queryset(self):
#         queryset = Seller.objects.all().order_by('-id')
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(Q(name__icontains=search) | Q(gstn_no__icontains=search))
#         return queryset

# class ProductModelViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
#     serializer_class = ProductModelSerializer 
#     unique_field = 'asin_fsn'
#     update_fields = ['model_name', 'model', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

#     def get_queryset(self):
#         queryset = ProductModel.objects.all().order_by('-id')
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(Q(asin_fsn__icontains=search) | Q(model_name__icontains=search) | Q(model__icontains=search))
#         return queryset

# #-------------------------INVOICE SHIPMENT---------------
# class InvoiceShipmentViewSet(viewsets.ModelViewSet):
#     serializer_class = InvoiceShipmentSerializer
#     pagination_class = StandardResultsSetPagination 
    
#     def get_queryset(self):
#         try:
#             queryset = InvoiceShipment.objects.all().order_by('-id')
            
#             # 🔥 1. PRD ALIGNED DATE LOGIC (3 Types) 🔥
#             date_type = self.request.query_params.get('date_type', 'txn_date') # Default txn_date
#             start_date = self.request.query_params.get('start_date')
#             end_date = self.request.query_params.get('end_date')

#             if start_date and end_date:
#                 if date_type == 'invoice_date':
#                     queryset = queryset.filter(invoice_date__range=[start_date, end_date])
#                 elif date_type == 'delivery_date':
#                     queryset = queryset.filter(delivery_date__range=[start_date, end_date])
#                 else:
#                     queryset = queryset.filter(txn_date__range=[start_date, end_date])
#             elif start_date:
#                 if date_type == 'invoice_date':
#                     queryset = queryset.filter(invoice_date__gte=start_date)
#                 elif date_type == 'delivery_date':
#                     queryset = queryset.filter(delivery_date__gte=start_date)
#                 else:
#                     queryset = queryset.filter(txn_date__gte=start_date)
#             elif end_date:
#                 if date_type == 'invoice_date':
#                     queryset = queryset.filter(invoice_date__lte=end_date)
#                 elif date_type == 'delivery_date':
#                     queryset = queryset.filter(delivery_date__lte=end_date)
#                 else:
#                     queryset = queryset.filter(txn_date__lte=end_date)

#             # 2. Other Parameters
#             order_id = self.request.query_params.get('order_id')
#             delivery_status = self.request.query_params.get('delivery_status')
#             invoice_no = self.request.query_params.get('invoice_no')
#             firm = self.request.query_params.get('firm')
#             location = self.request.query_params.get('location')

#             if order_id: queryset = queryset.filter(order_id__icontains=order_id)
#             if delivery_status: queryset = queryset.filter(delivery_status__iexact=delivery_status)
#             if invoice_no: queryset = queryset.filter(invoice_no__icontains=invoice_no)
#             if firm: queryset = queryset.filter(firm__iexact=firm)
#             if location: queryset = queryset.filter(location__iexact=location)

#             # 3. Global Search Logic
#             search_query = self.request.query_params.get('search', '').strip()
#             if search_query:
#                 queryset = queryset.filter(
#                     Q(order_id__icontains=search_query) |
#                     Q(invoice_no__icontains=search_query) |
#                     Q(seller_name__icontains=search_query) |
#                     Q(asin_fsn__icontains=search_query) |
#                     Q(model_no__icontains=search_query) |
#                     Q(seller_gstn__icontains=search_query) |
#                     Q(tracking_id__icontains=search_query) |
#                     Q(cancel_reason__icontains=search_query) 
#                 )

#             return queryset

#         except Exception as e:
#             print(f"🔥 Error fetching InvoiceShipments: {str(e)}")
#             return InvoiceShipment.objects.none()

#     # 🔥 FIX 1: Bulk Update Cancel Reason Fixed Here 🔥
#     @action(detail=False, methods=['post'])
#     def bulk_update_status(self, request):
#         ids = request.data.get('ids', [])
#         new_status = request.data.get('delivery_status')
#         new_date = request.data.get('delivery_date')
#         new_reason = request.data.get('cancel_reason') # 🔥 ADDED CANCEL REASON CAPTURE 🔥
        
#         if not ids: return Response({"error": "No IDs selected!"}, status=status.HTTP_400_BAD_REQUEST)
        
#         updated = 0
#         for shipment in InvoiceShipment.objects.filter(id__in=ids):
#             if new_status: shipment.delivery_status = new_status
#             if new_date: shipment.delivery_date = new_date
            
#             # Agar Cancel ho raha hai, tabhi reason aur invoice_status update hoga
#             if new_status and new_status.lower() == 'cancelled':
#                 shipment.invoice_status = 'Cancel'
#                 if new_reason: shipment.cancel_reason = new_reason

#             shipment.save()
#             updated += 1
            
#         return Response({"message": f"Successfully updated {updated} shipments."}, status=status.HTTP_200_OK)

# class InvoiceShipmentUploadView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
#         if not file: 
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # 1. Read File with Encoding Fail-Safe
#             if file.name.endswith('.csv'): 
#                 try:
#                     df = pd.read_csv(file)
#                 except UnicodeDecodeError:
#                     file.seek(0)
#                     df = pd.read_csv(file, encoding='cp1252') 
#             else: 
#                 df = pd.read_excel(file)
            
#             # --- 🔥 SMART EXCEL HEADER MAPPING 🔥 ---
#             # Aapki batayi hui sheet ke exact names
#             column_map = {
#                 'order_id': ['order id'],
#                 'txn_date': ['order date'], 
#                 'firm': ['account group'], # Account Group map kar diya Firm se
#                 'location': ['shipping address'], # Location map ho rahi hai Shipping Address se
#                 'seller_name': ['seller name'],
#                 'seller_gstn': ['seller gstn', 'seller gstin'],
#                 'invoice_no': ['invoice number', 'invoice no'],
#                 'invoice_date': ['invoice date'],
#                 'invoice_qty': ['shipment quantity', 'item quantity'], # Map updated
#                 'invoice_amount': ['invoice total amount', 'item net total'], # Map updated
#                 'tracking_id': ['carrier tracking #', 'tracking id']
#             }

#             # Normalize headers
#             df.columns = df.columns.str.strip().str.lower()
#             uploaded_headers = set(df.columns)
            
#             # Validation
#             REQUIRED_FIELDS = ['order_id', 'invoice_no'] 
#             missing_critical = []
#             actual_column_names = {} 
#             for db_key, aliases in column_map.items():
#                 clean_aliases = [alias.lower().strip() for alias in aliases]
#                 found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
#                 if found_col:
#                     actual_column_names[db_key] = found_col
#                 elif db_key in REQUIRED_FIELDS:
#                     missing_critical.append(db_key.upper())

#             if missing_critical:
#                 error_msg = f"Excel format error! Missing critical columns: {', '.join(missing_critical)}. Upload aborted!"
#                 return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

#             df = df.fillna('')
            
#             # 4. Master Data Fetches
#             # Fetch valid locations for exact match filtering inside the address string
#             valid_locations_list = list(Location.objects.values_list('name', flat=True))
#             valid_locations_lower = [loc.lower() for loc in valid_locations_list]
            
#             # Fetch all orders at once to avoid querying inside the loop (Speed Optimization)
#             all_orders = {order.order_id: order for order in OrderReport.objects.all()}

#             existing_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            
#             file_invoices = set()
#             missing_order_count = 0
#             dup_invoice_count = 0

#             # --- Extractor Utility ---
#             def get_val(row_data, db_field_key, return_type='str'):
#                 col_name = actual_column_names.get(db_field_key)
#                 if not col_name or col_name not in row_data:
#                     return 0.0 if return_type == 'num' else ''
                
#                 val = row_data[col_name]
#                 if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
#                     return 0.0 if return_type == 'num' else ''
                
#                 if return_type == 'num':
#                     try: return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
#                     except: return 0.0
#                 return str(val).strip()

#             # --- SMART SAVE LOOP ---
#             records = []
#             for index, row in df.iterrows():
#                 order_id = get_val(row, 'order_id')
#                 if not order_id: continue

#                 invoice_no = get_val(row, 'invoice_no')
                
#                 # Check duplicates and missing core orders
#                 if order_id not in all_orders: 
#                     missing_order_count += 1
#                     continue
                
#                 if not invoice_no: 
#                     continue
#                 else:
#                     if invoice_no in existing_invoices or invoice_no in file_invoices: 
#                         dup_invoice_count += 1
#                         continue # Skip saving duplicates
#                     file_invoices.add(invoice_no)

#                 # Linking with Core OrderReport Data (Auto Fetching Fields)
#                 order_data = all_orders[order_id]
                
#                 # 🔥 SMART LOCATION EXTRACTION 🔥
#                 raw_shipping_address = get_val(row, 'location').lower()
#                 final_location = ""
                
#                 if raw_shipping_address:
#                     for i, loc_lower in enumerate(valid_locations_lower):
#                         if loc_lower in raw_shipping_address:
#                             # Location matched with Master Location
#                             final_location = valid_locations_list[i]
#                             break
                
#                 # Handling Date Formatting (Invoice Date)
#                 raw_inv_date = get_val(row, 'invoice_date')
#                 try:
#                     invoice_date = pd.to_datetime(raw_inv_date, dayfirst=True).strftime('%Y-%m-%d') if raw_inv_date else None
#                 except:
#                     invoice_date = None

#                 records.append(InvoiceShipment(
#                     # Autofilled from OrderReports Master Table
#                     order_id=order_data.order_id,
#                     txn_date=order_data.txn_date,
#                     asin_fsn=order_data.asin_fsn,
#                     model_name=order_data.model_name,
#                     model_no=order_data.model_no,
#                     unit_price=order_data.unit_price, 
#                     order_qty=order_data.order_qty,
#                     order_amount=order_data.order_amount,

#                     # Extracted directly from Excel Row
#                     firm=get_val(row, 'firm'), # Account group
#                     location=final_location, # Filtered master location
#                     seller_name=get_val(row, 'seller_name'),
#                     seller_gstn=get_val(row, 'seller_gstn'),
                    
#                     invoice_no=invoice_no,
#                     invoice_date=invoice_date,
#                     invoice_qty=int(get_val(row, 'invoice_qty', 'num') or 1),
#                     invoice_amount=get_val(row, 'invoice_amount', 'num'),
                    
#                     tracking_id=get_val(row, 'tracking_id'),
#                     delivery_status="Pending" # Default status
#                 ))
            
#             # Feedback errors if any files were missed
#             error_segments = []
#             if missing_order_count > 0: error_segments.append(f"Skipped {missing_order_count} row(s): Order ID not found in Master")
#             if dup_invoice_count > 0: error_segments.append(f"Skipped {dup_invoice_count} row(s): Duplicate Invoice No")

#             if records:
#                 InvoiceShipment.objects.bulk_create(records, ignore_conflicts=True)
#                 msg = f"{len(records)} Shipments extracted and uploaded successfully!"
#                 if error_segments:
#                     msg += f" (Note: {', '.join(error_segments)})"
#                 return Response({"message": msg}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"error": f"No valid new records found to save. {', '.join(error_segments)}"}, status=status.HTTP_400_BAD_REQUEST)
            
#         except Exception as e:
#             return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET'])
# def fetch_order_for_shipment(request, order_id):
#     orders = OrderReport.objects.filter(order_id=order_id)
    
#     if not orders.exists():
#         return Response({"error": "Order ID not found in database!"}, status=404)

#     order_data = []
#     for order in orders:
#         # Puraana invoice data check karne wala logic poori tarah hata diya hai.
#         # Ab humesha fresh entry layout hi frontend ko milega.
#         item_data = {
#             "order_id": order.order_id,
#             "txn_date": order.txn_date,
#             "firm": order.firm,
#             "location": order.location,
#             "asin_fsn": order.asin_fsn,
#             "model_name": order.model_name,
#             "model_no": order.model_no,
#             "unit_price": order.unit_price,
#             "order_qty": order.order_qty,
#             "order_amount": order.order_amount,
            
#             # HUMESHA KHALI (FRESH) FIELDS
#             "seller_name": "",
#             "seller_gstn": "",
#             "invoice_no": "",
#             "invoice_date": "",
#             "invoice_qty": order.order_qty,     # Base qty default de rahe hain par fields khali rahengi
#             "invoice_amount": order.order_amount,
#             "delivery_status": "Pending",
#             "delivery_date": "",
#             "tracking_id": "",
            
#             # Indicator fields hamesha false/null taaki naya record hi bane
#             "is_existing": False,
#             "shipment_id": None
#         }
#         order_data.append(item_data)
        
#     return Response(order_data, status=200)



# #-------------------VIEW Button funtionaity api --------------------
# class OrderSummaryView(APIView):
#     def get(self, request, pk):
#         try:
#             # 1. Jis row par click kiya hai, uska Order ID aur FSN nikalo
#             order = OrderReport.objects.get(id=pk)
#             target_order_id = order.order_id
#             target_asin = order.asin_fsn
            
#             # 2. SIRF usi Order ID aur usi FSN ka data fetch karo (No Merging)
#             shipments = InvoiceShipment.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            
#             # 🔥 SAFE FIX: Sirf wahi shipment lo jisme actually seller name ho 🔥
#             first_ship = shipments.exclude(seller_name__exact='').exclude(seller_name__isnull=True).first()
            
#             seller_name_fetched = first_ship.seller_name if first_ship else getattr(order, 'seller_name', '-')
#             seller_gstn_fetched = first_ship.seller_gstn if first_ship else getattr(order, 'seller_gstn', '-')

#             # Fallback for empty strings
#             if not seller_name_fetched or str(seller_name_fetched).strip() == '': seller_name_fetched = '-'
#             if not seller_gstn_fetched or str(seller_gstn_fetched).strip() == '': seller_gstn_fetched = '-'

#             inwards = InwardRecord.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
#             refunds = RefundRecord.objects.filter(order_id=target_order_id) # Refund direct Order ID se nikal rahe hain
            
#             # 3. Delivered Calculations
#             delivered_shipments = shipments.filter(delivery_status='Delivered')
#             delivered_qty = delivered_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
#             delivered_amount = float(delivered_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
#             # 4. Cancelled Calculations
#             cancelled_shipments = shipments.filter(delivery_status='Cancelled')
#             cancel_qty = cancelled_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
#             cancel_amount = float(cancelled_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
#             # 5. Inward & Short Calculations
#             inward_qty = inwards.aggregate(Sum('inward_qty'))['inward_qty__sum'] or 0
#             inward_amount = float(inwards.aggregate(Sum('inward_amount'))['inward_amount__sum'] or 0.0)
            
#             short_qty = inwards.aggregate(Sum('short_qty'))['short_qty__sum'] or 0
#             short_amount = float(inwards.aggregate(Sum('short_amount'))['short_amount__sum'] or 0.0)

#             # 6. Refund Calculations (Ab naye RefundRecord se aayenge)
#             refund_qty = refunds.count() # Kitni items refund hui
#             refund_amount = float(refunds.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)

#             # 7. Pending Calculations (Single Item Formula)
#             pending_qty = order.order_qty - delivered_qty - cancel_qty
#             pending_amount = float(order.order_amount) - delivered_amount - cancel_amount
#             pending_refund_amount = cancel_amount + short_amount - refund_amount
            
#             # 8. Status Sync (Safety ke liye)
#             calculated_status = "Complete" if pending_qty <= 0 else "Open"
#             if order.order_status != calculated_status:
#                 order.order_status = calculated_status
#                 order.save()

#             # 9. Final Response Data (Isme aapki saari naye fields hain)
#             summary_data = {
#                 "order_id": target_order_id,
#                 "txn_date": order.txn_date,
#                 "asin_fsn": target_asin,
#                 "model_no": order.model_no,
#                 "order_qty": order.order_qty,
#                 "order_amount": float(order.order_amount),
#                 "order_status": calculated_status,
                
#                 # 🔥 NEW FIELDS REQUESTED BY YOU 🔥
#                 "card_no": order.card_no or "-",
#                 "placed_by": order.placed_by or "-",
#                 "sap_po_no": getattr(order, 'sap_po_no', '-'), # getattr safe hota hai agar db migrate na hua ho
#                 "seller_name": seller_name_fetched, # Shipment se fetched
#                 "seller_gstn": seller_gstn_fetched, # Shipment se fetched
#                 "cn_amount": float(getattr(order, 'cn_amount', 0.0)),
                
#                 # Metrics
#                 "delivered_qty": delivered_qty,
#                 "delivered_amount": delivered_amount,
#                 "cancel_qty": cancel_qty,
#                 "cancel_amount": cancel_amount,
#                 "short_qty": short_qty, 
#                 "short_amount": short_amount,
#                 "refund_qty": refund_qty, 
#                 "refund_amount": refund_amount,
#                 "pending_qty": pending_qty,
#                 "pending_amount": round(pending_amount, 2),
#                 "pending_refund_amount": round(pending_refund_amount, 2),
#                 "inward_qty": inward_qty, 
#                 "inward_amount": inward_amount,
#                 "grpo_qty": order.grpo_qty,
#                 "grpo_amount": float(order.grpo_amount)
#             }
            
#             return Response(summary_data, status=200)
            
#         except OrderReport.DoesNotExist:
#             return Response({"error": "Order not found"}, status=404)
#         except Exception as e:
#             return Response({"error": f"Error: {str(e)}"}, status=400)
        

# class ExportOrderReportsExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         queryset = OrderReport.objects.all()

#         # 🔥 SMART FILTERS
#         merchant = request.query_params.get('merchant')
#         status_val = request.query_params.get('order_status') 
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         search = request.query_params.get('search') 

#         if merchant:
#             queryset = queryset.filter(merchant__icontains=merchant)
#         if status_val:
#             queryset = queryset.filter(status__iexact=status_val)
#         if start_date and end_date:
#             queryset = queryset.filter(txn_date__range=[start_date, end_date])
#         if search:
#             queryset = queryset.filter(order_id__icontains=search) 

#         data = queryset.values(
#             'order_id', 'txn_date', 'month', 'day', 'txn_detail', 
#             'merchant', 'merchant_id', 'firm', 'location', 
#             'asin_fsn', 'model_name', 'model_no', 
#             'order_qty', 'order_amount', 'unit_price', 
#             'payment_amount', 'card_offer'
#         )
        
#         df = pd.DataFrame(list(data))
#         if df.empty:
#             df = pd.DataFrame(columns=['S.No', 'Order ID', 'Date', 'No Data Found For This Filter'])
#         else:
#             # 🔥 MAGIC: Sabse pehle column (index 0) par S.No add karna (1, 2, 3...)
#             df.insert(0, 'S.No', range(1, len(df) + 1))
            
#             # Columns ko clean format me convert karna
#             df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            
#             # Names ko waisa banana jaisa upload template mein hai
#             df.rename(columns={
#                 'Asin Fsn': 'ASIN/FSN',
#                 'Payment Amount': 'Payment',
#                 'Order Qty': 'Qty',
#                 'Order Amount': 'Order Amt'
#             }, inplace=True)

#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="Filtered_Order_Reports.xlsx"'
        
#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Orders')

#         return response   


# class ExportInvoiceShipmentExcelView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         queryset = InvoiceShipment.objects.all()

#         # 🔥 SMART FILTERS FOR INVOICE
#         merchant = request.query_params.get('merchant')
#         invoice_no = request.query_params.get('invoice_no')
        
#         if merchant:
#             queryset = queryset.filter(firm__icontains=merchant)
            
#         if invoice_no:
#             queryset = queryset.filter(invoice_no__icontains=invoice_no)

#         data = queryset.values(
#             'order_id', 'txn_date', 'firm', 'location', 'seller_name', 'seller_gstn',
#             'invoice_no', 'invoice_date', 'asin_fsn', 'model_name', 'model_no',
#             'invoice_qty', 'invoice_amount', 'unit_price', 'tracking_id', 
#             'delivery_date'
#         )
        
#         df = pd.DataFrame(list(data))
#         if df.empty:
#             df = pd.DataFrame(columns=['S.No', 'Invoice No', 'Date', 'No Data Found For This Filter'])
#         else:
#             # 🔥 MAGIC: Sabse pehle column (index 0) par S.No add karna (1, 2, 3...)
#             df.insert(0, 'S.No', range(1, len(df) + 1))
            
#             # Underscores hata kar proper title case banana (e.g., invoice_no -> Invoice No)
#             df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            
#             df.rename(columns={
#                 'Asin Fsn': 'ASIN/FSN',
#                 'Txn Date': 'Txn Date',
#             }, inplace=True)

#         response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = 'attachment; filename="Invoice_Shipments.xlsx"'
        
#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Invoices')

#         return response   

# # Bulk delete API for admin --------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_delete_orders(request):
#     ids_to_delete = request.data.get('ids', [])
#     if not ids_to_delete:
#         return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         deleted_count, _ = OrderReport.objects.filter(id__in=ids_to_delete).delete()
#         return Response({"message": f"Successfully deleted {deleted_count} Order Report(s)."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # --- BULK DELETE FOR INVOICE SHIPMENTS ---
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bulk_delete_invoices(request):
#     ids_to_delete = request.data.get('ids', [])
#     if not ids_to_delete:
#         return Response({"error": "No records selected!"}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         deleted_count, _ = InvoiceShipment.objects.filter(id__in=ids_to_delete).delete()
#         return Response({"message": f"Successfully deleted {deleted_count} Invoice Shipment(s)."}, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
          
# # MODEL EXCEL UPLOAD API------------

# @api_view(['POST'])
# @permission_classes([IsAuthenticated]) # Sirf login wale log/admins kar sakein
# def upload_models_excel(request):
#     if 'file' not in request.FILES:
#         return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

#     file = request.FILES['file']
    
#     try:
#         # Check if file is CSV or Excel
#         if file.name.endswith('.csv'):
#             df = pd.read_csv(file)
#         else:
#             df = pd.read_excel(file)

#         # Excel ke headers ko standardize karna (saare chote akshar, spaces ki jagah underscore)
#         # Taaki agar Excel mein 'Model Name' likha ho toh wo 'model_name' ban jaye
#         df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

#         success_count = 0
#         error_count = 0

#         # Excel ki har row (line) ko check karke save karna
#         for index, row in df.iterrows():
#             try:
#                 # ASIN/FSN sabse zaroori hai, wahi unique ID hai
#                 asin_fsn = str(row.get('asin_fsn') or row.get('asn_fsn') or '').strip()
                
#                 # Agar row khali hai toh skip kar do
#                 if not asin_fsn or asin_fsn == 'nan':
#                     continue 

#                 # update_or_create: Agar ASIN already hai toh baaki data update karega, nahi toh naya banayega
#                 ProductModel.objects.update_or_create(
#                     asin_fsn=asin_fsn,
#                     defaults={
#                         'model_name': str(row.get('model_name', '')).strip() if pd.notna(row.get('model_name')) else "",
#                         'model': str(row.get('model', '')).strip() if pd.notna(row.get('model')) else "",
#                         'sap_polyshri': str(row.get('sap_polyshri', '')).strip() if pd.notna(row.get('sap_polyshri')) else "",
#                         'sap_rio': str(row.get('sap_rio', '')).strip() if pd.notna(row.get('sap_rio')) else "",
#                         'sap_ne': str(row.get('sap_ne', '')).strip() if pd.notna(row.get('sap_ne')) else "",
#                         'sap_sms': str(row.get('sap_sms', '')).strip() if pd.notna(row.get('sap_sms')) else "",
#                         'sap_smmpl': str(row.get('sap_smmpl', '')).strip() if pd.notna(row.get('sap_smmpl')) else "",
#                     }
#                 )
#                 success_count += 1
#             except Exception as row_err:
#                 print(f"Error saving row {index}: {row_err}")
#                 error_count += 1

#         return Response({
#             "message": f"Upload successful! Saved/Updated {success_count} models. Failed: {error_count}."
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f"Excel Upload Error: {e}")
#         return Response({"error": "Failed to read the Excel file. Make sure format is correct."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
      
# class ApprovalViewSet(viewsets.ModelViewSet):
#     serializer_class = ApprovalRequestSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user_role = getattr(self.request.user, 'role', None)
#         username = getattr(self.request.user, 'username', str(self.request.user))
        
#         if user_role == 'ADMIN' or self.request.user.is_superuser or self.request.user.is_staff:
#             return ApprovalRequest.objects.all().order_by('-id')
            
#         return ApprovalRequest.objects.filter(
#             Q(requested_by__iexact=username) | Q(placed_by__iexact=username)
#         ).order_by('-id')

#     @action(detail=False, methods=['get'])
#     def dropdown_data(self, request):
#         return Response({
#             'firms': FirmDropdownSerializer(Firm.objects.all(), many=True).data,
#             'locations': LocationDropdownSerializer(Location.objects.all(), many=True).data,
#             'merchants': MerchantDropdownSerializer(Merchant.objects.all(), many=True).data,
#             'models': ModelDropdownSerializer(ProductModel.objects.all(), many=True).data,
#         })

#     # 🔥 1. PRD AUTO-ID GENERATOR (AMZ, FK, RL) 🔥
#     def perform_create(self, serializer):
#         merchant = serializer.validated_data.get('merchant')
#         merchant_name = merchant.name.upper() if merchant else ""
        
#         if 'AMAZON' in merchant_name:
#             prefix = "AMZ"
#         elif 'FLIPKART' in merchant_name:
#             prefix = "FK"
#         else:
#             prefix = "RL"
            
#         last_approval = ApprovalRequest.objects.filter(approval_no__startswith=prefix).order_by('-id').first()
        
#         if last_approval and last_approval.approval_no:
#             try:
#                 last_no = last_approval.approval_no.replace(prefix, "")
#                 new_no = int(last_no) + 1
#             except ValueError:
#                 new_no = 1
#         else:
#             new_no = 1
            
#         new_approval_no = f"{prefix}{str(new_no).zfill(5)}"
#         serializer.save(approval_no=new_approval_no)

#     # 🔥 2. EXACT TIMESTAMP ON APPROVAL 🔥
#     @action(detail=True, methods=['post'])
#     def approve(self, request, pk=None):
#         user_role = getattr(request.user, 'role', None)
#         if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
#             return Response({"error": "Security Alert: Only authorized Admins can approve."}, status=status.HTTP_403_FORBIDDEN)
            
#         approval = self.get_object()
#         approval.status = 'Approved'
        
#         # 🔥 FIX: Ab ye Local Indian Time uthayega 🔥
#         current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
#         approval.authorized_by = f"{request.user.username} ({current_time})"
#         approval.save()
#         return Response({"message": "Approval Request Approved Successfully!"}, status=status.HTTP_200_OK)

#     # 🔥 EXACT IST TIMESTAMP ON REJECT 🔥
#     @action(detail=True, methods=['post'])
#     def reject(self, request, pk=None):
#         user_role = getattr(request.user, 'role', None)
#         if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
#             return Response({"error": "Security Alert: Only authorized Admins can reject."}, status=status.HTTP_403_FORBIDDEN)
            
#         approval = self.get_object()
#         approval.status = 'Rejected'
        
#         # 🔥 FIX: Ab ye Local Indian Time uthayega 🔥
#         current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
#         approval.authorized_by = f"{request.user.username} ({current_time})"
#         approval.save()
#         return Response({"message": "Approval Request Rejected Successfully!"}, status=status.HTTP_200_OK)



# # ------------------------- GRPO VIEWSET -------------------------
# class GRPORecordViewSet(viewsets.ModelViewSet):
#     queryset = GRPORecord.objects.all().order_by('-id')
#     serializer_class = GRPORecordSerializer
#     permission_classes = [IsAuthenticated] # Agar bina login chalana ho toh ise hata dena

#     # 🔥 STRICT BULK EXCEL UPLOAD LOGIC 🔥
#     @action(detail=False, methods=['post'])
#     def upload_excel(self, request):
#         file = request.FILES.get('file')
#         if not file:
#             return Response({"error": "Bhai, koi file upload nahi hui!"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             if file.name.endswith('.csv'):
#                 df = pd.read_csv(file)
#             else:
#                 df = pd.read_excel(file)
                
#             df = df.fillna('')
            
#             # 🔥 STRICT VALIDATION: Pehle saare valid invoices DB se nikal lo 🔥
#             valid_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            
#             records = []
#             skipped_count = 0
            
#             for index, row in df.iterrows():
#                 inv_no = str(row.get('grpo_invoice_number', '')).strip()
                
#                 # Agar Invoice Number humare record me nahi hai, toh ye row REJECT!
#                 if inv_no not in valid_invoices:
#                     skipped_count += 1
#                     continue
                
#                 grpo_qty = str(row.get('grpo_quantity', '0')).replace(',', '').strip()
#                 grpo_amt = str(row.get('grpo_amt', '0')).replace(',', '').strip()

#                 records.append(GRPORecord(
#                     firm_name=str(row.get('firm_name', '')),
#                     internal_number=str(row.get('internal_number', '')),
#                     grpo_status=str(row.get('grpo_status', 'Open')),
#                     grpo_user_name=str(row.get('grpo_user_name', '')),
#                     grpo_no=str(row.get('grpo_no', '')),
#                     grpo_invoice_number=inv_no,
#                     grpo_create_date=str(row.get('grpo_create_date', '')),
#                     grpo_posting_date=str(row.get('grpo_posting_date', '')),
#                     purchase_vendor_code=str(row.get('purchase_vendor_code', '')),
#                     purchase_vendor_name=str(row.get('purchase_vendor_name', '')),
#                     inward_whs_code=str(row.get('inward_whs_code', '')),
#                     item_code=str(row.get('item_code', '')),
#                     description=str(row.get('description', '')),
#                     grpo_quantity=float(grpo_qty) if grpo_qty.replace('.','',1).isdigit() else 0.0,
#                     grpo_amt=float(grpo_amt) if grpo_amt.replace('.','',1).isdigit() else 0.0,
#                 ))
            
#             GRPORecord.objects.bulk_create(records)
            
#             msg = f"{len(records)} GRPO records successfully imported!"
#             if skipped_count > 0:
#                 msg += f" (Strict Warning: {skipped_count} rows skipped due to invalid/missing Invoice Number)"
                
#             return Response({"message": msg}, status=status.HTTP_201_CREATED)
            
#         except Exception as e:
#             return Response({"error": f"File process karne me error aaya: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class DownloadApprovalPDF(APIView):
#     # permission_classes = [IsAuthenticated] 

#     def get(self, request, pk):
#         try:
#             approval = ApprovalRequest.objects.get(pk=pk)
#             buffer = io.BytesIO()
#             # Left/Right margins ko thoda kam kiya hai taaki lamba table aaram se fit ho jaye
#             doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
#             elements = []
#             styles = getSampleStyleSheet()

#             # --- 1. HEADER ROW (Title + Timestamp) ---
#             title_style = ParagraphStyle(
#                 name="TitleStyle", fontSize=14, fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a")
#             )
#             timestamp_style = ParagraphStyle(
#                 name="TimestampStyle", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=2
#             )
            
#             generated_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
#             header_table = Table([
#                 [Paragraph(f"<b>{approval.approval_no} — Online Order Placement Tracker</b>", title_style), 
#                  Paragraph(f"Generated: {generated_time}", timestamp_style)]
#             ], colWidths=[550, 240])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
#                 ('BOTTOMPADDING', (0,0), (-1,-1), 10)
#             ]))
#             elements.append(header_table)
#             elements.append(Spacer(1, 15))

#             # --- 2. TOP DETAILS GRID ---
#             firm_name = approval.firm.name if hasattr(approval, 'firm') and approval.firm else "-"
#             ship_loc = approval.ship_location.name if hasattr(approval, 'ship_location') and approval.ship_location else "-"
#             bill_loc = approval.bill_location.name if hasattr(approval, 'bill_location') and approval.bill_location else "-"
#             merchant_name = approval.merchant.name if hasattr(approval, 'merchant') and approval.merchant else "-"

#             data_top = [
#                 ["Approval Date:", approval.request_date.strftime('%d/%m/%Y') if approval.request_date else "-", "Order Requested By:", str(approval.requested_by or "-")],
#                 ["Firm Name:", firm_name, "Merchant:", merchant_name],
#                 ["Ship Location:", ship_loc, "Merchant_ID:", str(approval.merchant_account_id or "-")],
#                 ["Bill Location:", bill_loc, "Authorized By:", str(approval.authorized_by or "-")]
#             ]
            
#             t_top = Table(data_top, colWidths=[90, 260, 110, 310])
#             t_top.setStyle(TableStyle([
#                 ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), 
#                 ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'), 
#                 ('FONTSIZE', (0,0), (-1,-1), 9),
#                 ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")),
#                 ('BOTTOMPADDING', (0,0), (-1,-1), 5),
#             ]))
#             elements.append(t_top)
#             elements.append(Spacer(1, 20))

#             # --- 3. ITEMS TABLE WITH TEXT WRAPPING ---
#             # Paragraph Styles text ko cut hone se bachane ke liye (Text-Wrapping)
#             cell_style = ParagraphStyle(name='CellStyle', fontSize=7, leading=9, textColor=colors.HexColor("#475569"))
#             header_cell_style = ParagraphStyle(name='HeaderCellStyle', fontSize=8, leading=10, textColor=colors.white, fontName='Helvetica-Bold')

#             headers = [
#                 Paragraph("<b>ASIN/FSN</b>", header_cell_style), Paragraph("<b>Model</b>", header_cell_style), 
#                 Paragraph("<b>Req<br/>Qty</b>", header_cell_style), Paragraph("<b>Purchase<br/>Price</b>", header_cell_style), 
#                 Paragraph("<b>CN</b>", header_cell_style), Paragraph("<b>Agreed<br/>NLC</b>", header_cell_style), 
#                 Paragraph("<b>Link<br/>Used</b>", header_cell_style), Paragraph("<b>Placed<br/>Qty</b>", header_cell_style), 
#                 Paragraph("<b>Order<br/>NLC</b>", header_cell_style), Paragraph("<b>Payment<br/>Method</b>", header_cell_style), 
#                 Paragraph("<b>Delivery<br/>Date</b>", header_cell_style), Paragraph("<b>Total<br/>Cost</b>", header_cell_style)
#             ]
            
#             item_data = [headers]
#             total_req_qty = 0
#             total_placed_qty = 0
#             total_cost_sum = 0.0

#             for item in approval.items.all():
#                 req_qty = item.req_qty or 0
#                 placed_qty = item.placed_qty or 0
#                 tot_cost = float(item.total_placed_amt or 0)
                
#                 total_req_qty += req_qty
#                 total_placed_qty += placed_qty
#                 total_cost_sum += tot_cost

#                 del_date = item.expected_delivery_date.strftime('%d/%m/%Y') if item.expected_delivery_date else "-"

#                 item_data.append([
#                     Paragraph(str(item.asin_fsn or "-"), cell_style), 
#                     Paragraph(str(item.model_name or "-"), cell_style), 
#                     str(req_qty), 
#                     f"Rs. {item.purchase_price or 0}",
#                     f"Rs. {item.cn_amt or 0}", 
#                     f"Rs. {item.agreed_nlc or 0}", 
#                     str(item.link_used or "-"), 
#                     str(placed_qty),
#                     f"Rs. {item.order_nlc or 0}", 
#                     Paragraph(str(item.payment_method or "-"), cell_style), 
#                     Paragraph(del_date, cell_style),
#                     f"Rs. {tot_cost}"
#                 ])

#             # Totals Row
#             item_data.append([
#                 "Total", "", str(total_req_qty), "", "", "", "", str(total_placed_qty), "", "", "", f"Rs. {total_cost_sum}"
#             ])

#             # Exact widths calculation to fit A4 Landscape (Total ~790 points)
#             t_items = Table(item_data, colWidths=[75, 140, 30, 55, 45, 55, 30, 35, 55, 70, 55, 60])
            
#             table_style = TableStyle([
#                 ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")), 
#                 ('ALIGN', (0,0), (-1,-1), 'LEFT'),
#                 ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
#                 ('BOTTOMPADDING', (0,0), (-1,0), 6),
#                 ('TOPPADDING', (0,0), (-1,0), 6),
#                 ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
#                 ('FONTSIZE', (0,1), (-1,-2), 8),
#                 ('TEXTCOLOR', (0,1), (-1,-2), colors.HexColor("#475569")),
#                 ('BOTTOMPADDING', (0,1), (-1,-1), 5),
#                 ('TOPPADDING', (0,1), (-1,-1), 5),
#                 ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#e2e8f0")), 
#             ])
            
#             for i in range(1, len(item_data)-1):
#                 if i % 2 == 0:
#                     table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8fafc"))
                    
#             table_style.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#fef3c7"))
#             table_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
#             table_style.add('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#000000"))
#             table_style.add('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#eab308"))
            
#             t_items.setStyle(table_style)
#             elements.append(t_items)
#             elements.append(Spacer(1, 40))

#             # --- 4. SIGNATURE SECTIONS (Dynamically picking up Admin's name) ---
#             req_by_text = approval.requested_by if approval.requested_by else "_________________________"
#             placed_by_text = approval.placed_by if approval.placed_by else "_________________________"
            
#             # 🔥 APPROVED BY MEIN ADMIN KA NAAM YAHAN AAYEGA 🔥
#             approved_by_text = approval.authorized_by if approval.authorized_by else "_________________________"

#             sig_data = [
#                 ["Order Requested By", "Order Placed By", "Order Approved By"],
#                 [f"\n\n\n{req_by_text}", f"\n\n\n{placed_by_text}", f"\n\n\n{approved_by_text}"]
#             ]
#             t_sigs = Table(sig_data, colWidths=[260, 260, 260])
#             t_sigs.setStyle(TableStyle([
#                 ('ALIGN', (0,0), (-1,-1), 'CENTER'),
#                 ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0,0), (-1,0), 9),
#                 ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#334155")),
#                 ('FONTNAME', (0,1), (-1,1), 'Helvetica'), # Name lines in normal font
#                 ('FONTSIZE', (0,1), (-1,1), 9),
#             ]))
#             elements.append(t_sigs)
#             elements.append(Spacer(1, 30))
            
#             disclaimer = ParagraphStyle(name="Disclaimer", fontSize=7, textColor=colors.HexColor("#94a3b8"))
#             elements.append(Paragraph(f"This document was generated automatically on {generated_time} upon approval.", disclaimer))

#             doc.build(elements)
#             pdf = buffer.getvalue()
#             buffer.close()
            
#             response = HttpResponse(pdf, content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="Approval_{approval.approval_no}.pdf"'
#             return response
            
#         except Exception as e:
#             return HttpResponse(f"Error generating PDF: {str(e)}", status=400)    
        


# class TicketViewSet(viewsets.ModelViewSet):
#     queryset = Ticket.objects.all().order_by('-id')
#     serializer_class = TicketSerializer

# class RefundRecordViewSet(viewsets.ModelViewSet):
#     queryset = RefundRecord.objects.all().order_by('-id')
#     serializer_class = RefundRecordSerializer
#     permission_classes = [IsAuthenticated]


# # --- ORDER CANCEL API (Manual Cancel in Order Report) ---
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def cancel_order_to_refund(request, pk):
#     try:
#         order = OrderReport.objects.get(pk=pk)
#         order.order_status = 'Complete' # Aapki requirement: "status completed ho jayega iska"
#         order.save()
        
#         # 🔥 FIX: Us order ki saari Invoices ko bhi instantly Cancel mark karo 🔥
#         shipments = InvoiceShipment.objects.filter(order_id=order.order_id, asin_fsn=order.asin_fsn)
#         for ship in shipments:
#             ship.delivery_status = 'Cancelled'
#             ship.invoice_status = 'Cancel'
#             ship.cancel_reason = 'Auto-Cancelled from Order Dashboard'
#             ship.save()
        
#         # Add to Refund Tab
#         RefundRecord.objects.create(
#             source_date=order.txn_date,
#             firm=order.firm,
#             merchant=order.merchant,
#             order_id=order.order_id,
#             invoice_no="-", # Direct order cancel me invoice nahi hota
#             model_name=order.model_name,
#             refund_qty=order.order_qty, # 🔥 FIX: Added Qty here
#             invoice_amount=order.order_amount,
#             received_comment="cancel confirmed"
#         )
#         return Response({"message": "Order Cancelled, Invoices Updated and Moved to Refunds!"})
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)
    

# # live dashboard API

# class DashboardStatsView(APIView):
#     def get(self, request):
#         try:
#             # 1. KPI Calculations
#             total_orders = OrderReport.objects.count()
#             open_orders = OrderReport.objects.filter(order_status='Open').count()
#             completed_orders = OrderReport.objects.filter(order_status='Complete').count()
            
#             # Total Revenue Calculation
#             revenue_data = OrderReport.objects.aggregate(total_revenue=Sum('order_amount'))
#             total_revenue = float(revenue_data['total_revenue'] or 0.0)

#             # 2. Pie Chart (Sales by Merchant)
#             merchants_data = OrderReport.objects.values('merchant').annotate(
#                 total_sales=Sum('order_amount')
#             ).order_by('-total_sales')

#             pie_data = []
#             for item in merchants_data:
#                 merchant_name = item['merchant'] or 'Others'
#                 pie_data.append({
#                     "name": merchant_name,
#                     "value": float(item['total_sales'] or 0.0)
#                 })

#             return Response({
#                 "kpis": {
#                     "totalOrders": total_orders,
#                     "openOrders": open_orders,
#                     "completed": completed_orders,
#                     "revenue": total_revenue
#                 },
#                 "pieData": pie_data
#             }, status=200)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
        

# # --- GRPO SMART AUTO-FETCH API ---
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def fetch_invoice_for_grpo(request, invoice_no):
#     # Invoice module se data dhundhna
#     shipments = InvoiceShipment.objects.filter(invoice_no=invoice_no)
    
#     if not shipments.exists():
#         return Response({"error": "Invoice Number not found in database!"}, status=status.HTTP_404_NOT_FOUND)

#     # Agar ek invoice mein multiple items hain, toh hum sab bhejenge, frontend handle kar lega
#     data = []
#     for ship in shipments:
#         data.append({
#             "firm_name": ship.firm,
#             "purchase_vendor_name": ship.seller_name,
#             "item_code": ship.asin_fsn,
#             "description": ship.model_name,
#             "grpo_quantity": ship.invoice_qty,
#             "grpo_amt": ship.invoice_amount,
#         })
        
#     return Response(data, status=status.HTTP_200_OK)    
# # --- PURCHASE INWARD VIEWSET ---
# class PurchaseInwardViewSet(viewsets.ModelViewSet):
#     queryset = PurchaseInward.objects.all().order_by('-id')
#     serializer_class = PurchaseInwardSerializer
#     permission_classes = [IsAuthenticated]

# # --- SMART AUTO-FETCH GRPO DETAILS ---
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def fetch_grpo_for_inward(request, grpo_no):
#     try:
#         # DB se GRPO details nikalna
#         grpo_record = GRPORecord.objects.filter(grpo_no=grpo_no).first()
        
#         if not grpo_record:
#             return Response({"error": "Bhai, ye GRPO Number database me nahi mila!"}, status=status.HTTP_404_NOT_FOUND)
            
#         data = {
#             "grpo_no": grpo_record.grpo_no,
#             "firm_name": grpo_record.firm_name,
#             "vendor_name": grpo_record.purchase_vendor_name,
#             "item_code": grpo_record.item_code,
#             "expected_qty": grpo_record.grpo_quantity, # GRPO ki qty humari expected qty hai
#             "warehouse_location": grpo_record.inward_whs_code,
#         }
        
#         return Response(data, status=status.HTTP_200_OK)
        
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

# @receiver(post_save, sender=OrderReport)
# def create_refund_on_order_cancel(sender, instance, created, **kwargs):
#     # Agar order ka status Cancelled ho jata hai
#     if instance.status == 'Cancelled' or instance.status == 'Cancel Confirmation':
#         # Check karte hain ki is order ka refund pehle se to nahi bana
#         refund_exists = RefundRecord.objects.filter(order_id=instance.order_id).exists()
        
#         if not refund_exists:
#             RefundRecord.objects.create(
#                 order_id=instance.order_id,
#                 refund_amount=instance.total_amount, # Aapke model mein jo amount field ho
#                 status='Pending',
#                 remarks=f"Auto-generated: Order {instance.order_id} was Cancelled."
#             )

# # =======================================================
# # 🚀 2. AUTO-REFUND TRIGGER (Invoice Cancel Hone Par)
# # =======================================================
# @receiver(post_save, sender=InvoiceShipment)
# def create_refund_on_invoice_cancel(sender, instance, created, **kwargs):
#     # Agar Invoice ka status Cancelled ho jata hai
#     if instance.status == 'Cancelled':
#         refund_exists = RefundRecord.objects.filter(invoice_no=instance.invoice_no).exists()
        
#         if not refund_exists:
#             RefundRecord.objects.create(
#                 order_id=instance.order_id, 
#                 invoice_no=instance.invoice_no,
#                 refund_amount=instance.invoice_amount, # Aapke model mein jo amount field ho
#                 status='Pending',
#                 remarks=f"Auto-generated: Invoice {instance.invoice_no} was Cancelled."
#             )

# # =======================================================
# # 🚀 3. GRPO & INVOICE AUTO-MATCH TRIGGER
# # =======================================================
# @receiver(post_save, sender=GRPORecord)
# def update_invoice_on_grpo_upload(sender, instance, created, **kwargs):
#     # Ye sirf tab chalega jab naya GRPO upload hoga (Bulk upload se)
#     if created: 
#         # PRD ke hisaab se hum Invoice No ke basis par match kar rahe hain
#         matching_invoices = InvoiceShipment.objects.filter(invoice_no=instance.grpo_invoice_number)
        
#         for inv in matching_invoices:
#             # Invoice ka inward status 'Done' mark kar dete hain
#             inv.inward_status = 'Done' 
#             inv.save()       


# class WarehouseAuditViewSet(viewsets.ModelViewSet):
#     queryset = WarehouseAudit.objects.all().order_by('-id')
#     serializer_class = WarehouseAuditSerializer
#     permission_classes = [IsAuthenticated]

# # --- SMART FETCH INVOICE FOR AUDIT ---
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def fetch_invoice_for_audit(request, invoice_no):
#     try:
#         # DB se Invoice details nikalna
#         invoice = InvoiceShipment.objects.filter(invoice_no=invoice_no).first()
        
#         if not invoice:
#             return Response({"error": "Bhai, ye Invoice Number system me nahi mila!"}, status=status.HTTP_404_NOT_FOUND)
            
#         data = {
#             "invoice_no": invoice.invoice_no,
#             "order_id": invoice.order_id,
#             "expected_qty": invoice.invoice_qty, # Aapke model me jo invoice qty ka column ho, wo name yahan daalein
#         }
        
#         return Response(data, status=status.HTTP_200_OK)
        
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class IMEIRecordViewSet(viewsets.ModelViewSet):
#     queryset = IMEIRecord.objects.all().order_by('-id')
#     serializer_class = IMEIRecordSerializer
#     permission_classes = [IsAuthenticated]    


# class AccountsLedgerAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         card_no = request.query_params.get('card_number')
#         firm = request.query_params.get('firm_name')

#         if not card_no or not firm:
#             return Response({"error": "Please provide both card_number and firm_name"}, status=400)

#         ledger_entries = []

#         # -------------------------------------------------------------
#         # 1. SETTLEMENTS -> Treat as CREDIT (Money In)
#         # Fields: card_number, firm_name, date, amount
#         # -------------------------------------------------------------
#         settlements = Settlement.objects.filter(card_number=card_no, firm_name=firm)
#         for s in settlements:
#             if s.date:
#                 ledger_entries.append({
#                     "date": str(s.date),
#                     "ref_no": s.txn_id,
#                     "type": s.txn_type,
#                     "debit": 0.00,
#                     "credit": float(s.amount or 0),
#                     "remarks": s.remarks or "Manual Entry / Refill"
#                 })

#         # -------------------------------------------------------------
#         # 2. ORDERS (PURCHASES) -> Treat as DEBIT (Money Out)
#         # Fields: card_no, firm, txn_date, order_amount
#         # -------------------------------------------------------------
#         orders = OrderReport.objects.filter(card_no=card_no, firm=firm)
#         for o in orders:
#             if o.txn_date:
#                 ledger_entries.append({
#                     "date": str(o.txn_date),
#                     "ref_no": o.order_id,
#                     "type": "Order Purchase",
#                     "debit": float(o.order_amount or 0),
#                     "credit": 0.00,
#                     "remarks": f"ASIN: {o.asin_fsn} | Model: {o.model_name or ''}"
#                 })

#         # -------------------------------------------------------------
#         # 3. REFUNDS -> Treat as CREDIT (Money Back In)
#         # Fields: received_card_no, firm, received_date, invoice_amount
#         # -------------------------------------------------------------
#         # Note: In your model, refund amount is tracked in `invoice_amount` 
#         # and card is `received_card_no` when updated manually.
#         refunds = RefundRecord.objects.filter(received_card_no=card_no, firm=firm)
#         for r in refunds:
#             # We prioritize received_date, fallback to created_at
#             r_date = r.received_date if r.received_date else (r.created_at.date() if r.created_at else None)
#             if r_date:
#                 ledger_entries.append({
#                     "date": str(r_date),
#                     "ref_no": r.order_id,
#                     "type": f"Refund - {r.refund_type or 'General'}",
#                     "debit": 0.00,
#                     "credit": float(r.invoice_amount or 0),
#                     "remarks": r.received_comment or "Refund Processed"
#                 })

#         # -------------------------------------------------------------
#         # 4. SORTING & CALCULATING RUNNING BALANCE
#         # -------------------------------------------------------------
#         # Date ke hisaab se ascending order mein sort karenge
#         ledger_entries.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

#         running_balance = 0.0
#         for entry in ledger_entries:
#             # Credit (Paisa aaya) - Debit (Paisa gaya)
#             running_balance += entry['credit'] - entry['debit']
#             # Balance column mein update kar diya
#             entry['balance'] = round(running_balance, 2)

#         return Response(ledger_entries)

# class FinanceReconciliationViewSet(viewsets.ModelViewSet):
#     queryset = FinanceReconciliation.objects.all().order_by('-date', '-id')
#     serializer_class = FinanceReconciliationSerializer
#     permission_classes = [IsAuthenticated]    


# class UserProfileViewSet(viewsets.ModelViewSet):
#     queryset = UserProfile.objects.all().order_by('-id')
#     serializer_class = UserProfileSerializer

# class RolePermissionViewSet(viewsets.ModelViewSet):
#     queryset = RolePermission.objects.all()
#     serializer_class = RolePermissionSerializer

#     # Ek custom API jo ek sath saari permissions save karegi (Matrix save)
#     @action(detail=False, methods=['post'])
#     def bulk_update(self, request):
#         data_list = request.data
#         for item in data_list:
#             RolePermission.objects.update_or_create(
#                 section=item['section'],
#                 role=item['role'],
#                 defaults={
#                     'can_read': item.get('can_read', False),
#                     'can_create': item.get('can_create', False),
#                     'can_change': item.get('can_change', False),
#                     'can_delete': item.get('can_delete', False),
#                     'can_approve': item.get('can_approve', False),
#                     'can_administer': item.get('can_administer', False),
#                 }
#             )
#         return Response({"status": "Permissions Updated Successfully"})


# class SettlementViewSet(viewsets.ModelViewSet):
#     queryset = Settlement.objects.all().order_by('-date', '-id')
#     serializer_class = SettlementSerializer
#     permission_classes = [IsAuthenticated]


from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
import traceback

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape

from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver

import pandas as pd
import csv
import io
from datetime import datetime

from .models import (
    Firm, Location, Merchant, ProductModel, PurchaseInward, InvoiceShipment, 
    OrderReport, InwardRecord, RefundRecord, Seller, ApprovalRequest, 
    GRPORecord, Ticket, WarehouseAudit, IMEIRecord, Settlement, 
    FinanceReconciliation, UserProfile, RolePermission,ColumnVisibilityPolicy
)
from .serializers import (
    OrderReportSerializer, ColumnVisibilityPolicySerializer, FirmSerializer, 
    LocationSerializer, MerchantSerializer, ProductModelSerializer, 
    InvoiceShipmentSerializer, SellerSerializer, ApprovalRequestSerializer, 
    FirmDropdownSerializer, LocationDropdownSerializer, MerchantDropdownSerializer, 
    ModelDropdownSerializer, GRPORecordSerializer, TicketSerializer, 
    RefundRecordSerializer, PurchaseInwardSerializer, WarehouseAuditSerializer, 
    IMEIRecordSerializer, UserProfileSerializer, RolePermissionSerializer, 
    SettlementSerializer, FinanceReconciliationSerializer,ColumnVisibilityPolicySerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

# =======================================================
# 🚀 1. ORDER REPORT VIEWSET (Unified & Fixed for Cancel Action)
# =======================================================
class OrderReportViewSet(viewsets.ModelViewSet):
    serializer_class = OrderReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = OrderReport.objects.all().order_by('-id')
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        firm = self.request.query_params.get('firm')
        location = self.request.query_params.get('location')
        model_no = self.request.query_params.get('model_no')
        txn_detail = self.request.query_params.get('txn_detail')
        order_status = self.request.query_params.get('order_status')
        search_query = self.request.query_params.get('search')

        if start_date: queryset = queryset.filter(txn_date__gte=start_date)
        if end_date: queryset = queryset.filter(txn_date__lte=end_date)
        if firm: queryset = queryset.filter(firm__icontains=firm)
        if location: queryset = queryset.filter(location__icontains=location)
        if model_no: queryset = queryset.filter(model_no__icontains=model_no)
        if txn_detail: queryset = queryset.filter(txn_detail__icontains=txn_detail)
        if order_status: queryset = queryset.filter(order_status=order_status)

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

    # Security Layer
    def perform_update(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Access Denied: Only Admins can modify order entries.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied("Access Denied: Only Admins can delete order entries.")
        instance.delete()

    # 🔥 THE CANCEL ACTION FIX 🔥
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            order = self.get_object()
            order.order_status = 'Cancelled'
            order.save() # Ye signal ko trigger karega
            
            # Related shipments ko bhi cancel kar do
            shipments = InvoiceShipment.objects.filter(order_id=order.order_id, asin_fsn=order.asin_fsn)
            for ship in shipments:
                ship.delivery_status = 'Cancelled'
                ship.invoice_status = 'Cancel'
                ship.cancel_reason = 'Auto-Cancelled from Order Dashboard'
                ship.save()
                
            return Response({"message": "Order Cancelled successfully & Sent to Refunds!"}, status=200)
        except Exception as e:
            print("🔥 CANCEL ACTION ERROR 🔥")
            traceback.print_exc() # Ye terminal me exact error line batayega
            return Response({"error": f"Database Error: {str(e)}"}, status=400)


class BulkUploadExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file: 
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. Encoding Fail-Safe File Reader
            if file.name.endswith('.csv'): 
                try: df = pd.read_csv(file)
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='cp1252') 
            else: 
                df = pd.read_excel(file)
            
            # 2. Smart Excel Header Mapping
            column_map = {
                'order_id': ['order id', 'order_id', 'orderno', 'amazon order id'],
                'txn_date': ['txn date', 'txn_date', 'transaction date', 'order date'],
                'month': ['month'], 'day': ['day'],
                'txn_detail': ['txn detail', 'txn_detail', 'detail'],
                'merchant': ['merchant', 'merchant name', 'vendor'],
                'merchant_id': ['merchant id', 'merchant_id'],
                'firm': ['firm', 'company'],
                'location': ['location', 'branch', 'warehouse', 'shipping address'],
                'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'product id'],
                'model_name': ['model name', 'model_name', 'product name'],
                'model': ['model', 'model no', 'model number'],
                'qty': ['qty', 'quantity', 'order qty', 'item quantity'],
                'order_amt': ['order amt', 'order_amt', 'order amount', 'item net total', 'total amount'],
                'unit_price': ['unit price', 'unit_price', 'price', 'rate'],
                'payment': ['payment', 'payment mode', 'type'],
                'card_offer': ['card offer', 'card_offer', 'offer'],
                'card_no': ['card no', 'card_no', 'card number'],
                'placed_by': ['placed by', 'placed_by', 'operator'],
                'seller_name': ['seller name', 'seller_name'],
                'seller_gstn': ['seller gstn', 'seller_gstn', 'gstin']
            }

            df.columns = df.columns.str.strip().str.lower()
            uploaded_headers = set(df.columns)
            
            REQUIRED_FIELDS = ['order_id', 'asin_fsn'] 
            missing_critical = []
            actual_column_names = {} 
            for db_key, aliases in column_map.items():
                clean_aliases = [alias.lower().strip() for alias in aliases]
                found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
                if found_col: actual_column_names[db_key] = found_col
                elif db_key in REQUIRED_FIELDS: missing_critical.append(db_key.upper())

            if missing_critical:
                return Response({"error": f"Excel Validation Error! Zaroori columns missing hain: {', '.join(missing_critical)}."}, status=status.HTTP_400_BAD_REQUEST)

            df = df.fillna('')
            
            # 🔥 SMART MASTER DATA DICTIONARIES (Lowercase to Actual Case mapping) 🔥
            # Isse "BHOPAL", " Bhopal " automatically "Bhopal" ban jayega
            valid_firms = {f.strip().lower(): f for f in Firm.objects.values_list('name', flat=True) if f}
            valid_locations = {l.strip().lower(): l for l in Location.objects.values_list('name', flat=True) if l}
            valid_merchants = {m.strip().lower(): m for m in Merchant.objects.values_list('name', flat=True) if m}
            valid_asins = {a.strip().lower(): a for a in ProductModel.objects.values_list('asin_fsn', flat=True) if a}
            existing_orders_db = set(OrderReport.objects.values_list('order_id', 'asin_fsn'))
            existing_orders_lower = {(str(o_id).strip().lower(), str(asin).strip().lower()) for o_id, asin in existing_orders_db}
            file_orders_tracker = set() # Excel ke andar ke duplicates rokne ke liye

            def get_val(row_data, db_field_key, return_type='str'):
                col_name = actual_column_names.get(db_field_key)
                if not col_name or col_name not in row_data:
                    return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                val = row_data[col_name]
                if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
                    return 0.0 if return_type == 'num' else (1 if db_field_key == 'qty' else '')
                if return_type == 'num':
                    try: return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
                    except: return 0.0
                return str(val).strip()

            records = []
            skipped_errors = {}
            
            for index, row in df.iterrows():
                order_id = get_val(row, 'order_id')
                asin_fsn = get_val(row, 'asin_fsn')
                
                if not order_id or not asin_fsn: continue    
                
                raw_firm = get_val(row, 'firm')
                raw_loc = get_val(row, 'location')
                raw_merchant = get_val(row, 'merchant')

                # 🔥 STRICT VALIDATION LOCK 🔥
                row_errors = []
                if raw_firm and raw_firm.strip().lower() not in valid_firms: row_errors.append(f"Firm '{raw_firm}'")
                if raw_loc and raw_loc.strip().lower() not in valid_locations: row_errors.append(f"Location '{raw_loc}'")
                if raw_merchant and raw_merchant.strip().lower() not in valid_merchants: row_errors.append(f"Merchant '{raw_merchant}'")
                if asin_fsn.strip().lower() not in valid_asins: row_errors.append(f"ASIN '{asin_fsn}'")

                if row_errors:
                    err_msg = "In Master  missing: " + ", ".join(row_errors)
                    skipped_errors[err_msg] = skipped_errors.get(err_msg, 0) + 1
                    continue # REJECT THIS ROW!
                clean_order_id = str(order_id).strip().lower()
                clean_asin = str(asin_fsn).strip().lower()
                
                # Check 1: Kya ye Database me already saved hai?
                if (clean_order_id, clean_asin) in existing_orders_lower:
                    skipped_errors["Already Saved in DB (Duplicate)"] = skipped_errors.get("Already Saved in DB (Duplicate)", 0) + 1
                    continue
                
                # Check 2: Kya isi Excel sheet me ye line dobara repeat hui hai?
                if (clean_order_id, clean_asin) in file_orders_tracker:
                    skipped_errors["Duplicate Row in Excel File"] = skipped_errors.get("Duplicate Row in Excel File", 0) + 1
                    continue
                    
                file_orders_tracker.add((clean_order_id, clean_asin))

                raw_txn_date = get_val(row, 'txn_date')
                try: txn_date = pd.to_datetime(raw_txn_date, dayfirst=True).strftime('%Y-%m-%d') if raw_txn_date else None
                except: txn_date = None

                records.append(OrderReport(
                    order_id=order_id, txn_date=txn_date, month=get_val(row, 'month'), day=get_val(row, 'day'), txn_detail=get_val(row, 'txn_detail'),
                    # Smart Values Assigned Here
                    merchant=valid_merchants.get(raw_merchant.strip().lower(), raw_merchant),
                    firm=valid_firms.get(raw_firm.strip().lower(), raw_firm),
                    location=valid_locations.get(raw_loc.strip().lower(), raw_loc),
                    asin_fsn=valid_asins.get(asin_fsn.strip().lower(), asin_fsn),
                    
                    merchant_id=get_val(row, 'merchant_id'), model_name=get_val(row, 'model_name'), model_no=get_val(row, 'model'), 
                    order_qty=int(get_val(row, 'qty', 'num') or 1), order_amount=get_val(row, 'order_amt', 'num'),
                    unit_price=get_val(row, 'unit_price', 'num'), card_offer=get_val(row, 'card_offer', 'num'),
                    card_no=get_val(row, 'card_no'), placed_by=get_val(row, 'placed_by'),
                    seller_name=get_val(row, 'seller_name'), seller_gstn=get_val(row, 'seller_gstn'),
                    payment_amount=get_val(row, 'payment'),
                    order_status="Open" # Hamesha open rahega
                ))
            
            # Response handling based on Strict Validation
            if records: OrderReport.objects.bulk_create(records, ignore_conflicts=True)
            
            if not skipped_errors:
                return Response({"message": f"Successfully parsed and saved {len(records)} Orders smartly!"}, status=status.HTTP_201_CREATED)
            else:
                error_summary = " | ".join([f"{count} rows skipped ({reason})" for reason, count in skipped_errors.items()])
                if len(records) == 0:
                    return Response({"error": f"Upload Rejected! 0 saved.\nErrors: {error_summary}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": f"Partial Success: Saved {len(records)}.\nWARNING: {error_summary}"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

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

# 🔥 SMART CRASH-PROOF MIXIN 🔥
class MasterBulkOperationsMixin:
    def get_model_class(self):
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model
        return self.get_queryset().model

    @action(detail=False, methods=['post'])
    def upload(self, request):
        model_class = self.get_model_class()
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Please upload a valid Excel or CSV file."}, status=400)
        
        try:
            # 1. Encoding Fail-Safe File Reader
            if file.name.endswith('.csv'):
                try: df = pd.read_csv(file)
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='cp1252')
            else:
                df = pd.read_excel(file)
            
            # 2. Smart Column Cleanup (Handle hidden BOM characters and spaces)
            df.columns = [str(col).strip().lower().replace('\ufeff', '').replace('ï»¿', '') for col in df.columns]
            df = df.where(pd.notnull(df), None)
            
            # 3. Robust Column Mapping Dictionary
            col_map = {
                'name': ['name', 'firm name', 'location name', 'merchant name', 'seller name', 'firm', 'location', 'merchant', 'vendor'],
                'gstn_no': ['gstn number', 'gstn_no', 'gstn', 'gstin', 'gstn no'], 
                'asin_fsn': ['asin/fsn', 'asin_fsn', 'asin', 'fsn', 'asn_fsn', 'product id'],
                'model_name': ['model name', 'model_name', 'product name'],
                'model': ['model code', 'model', 'model no', 'model number'],
                'sap_polyshri': ['sap polyshri', 'sap_polyshri'],
                'sap_rio': ['sap rio', 'sap_rio'],
                'sap_ne': ['sap ne', 'sap_ne'],
                'sap_sms': ['sap sms', 'sap_sms'],
                'sap_smmpl': ['sap smmpl', 'sap_smmpl']
            }

            # Map the exact uploaded column names to database keys
            actual_cols = {}
            for db_field, aliases in col_map.items():
                for alias in aliases:
                    if alias in df.columns:
                        actual_cols[db_field] = alias
                        break

            # Check if the unique field exists in the uploaded file
            unique_col_name = actual_cols.get(self.unique_field)
            if not unique_col_name:
                return Response({"error": f"Upload failed! Missing critical column for '{self.unique_field}'."}, status=400)

            # 4. Smart Process Loop
            created_count, updated_count, skipped_count = 0, 0, 0
            
            for _, row in df.iterrows():
                # Extract Unique Value safely
                unique_val = str(row.get(unique_col_name, '')).strip()
                if not unique_val or unique_val.lower() in ['none', 'nan', 'null', '']: 
                    skipped_count += 1
                    continue  
                
                # Extract Update Fields safely
                defaults = {}
                for field in self.update_fields:
                    col_name = actual_cols.get(field)
                    if col_name and row.get(col_name) is not None:
                        val = str(row.get(col_name)).strip()
                        if val.lower() not in ['none', 'nan', 'null']:
                            defaults[field] = val
                
                # Perform the DB Transaction
                obj, created = model_class.objects.update_or_create(
                    **{self.unique_field: unique_val}, defaults=defaults
                )
                
                if created: created_count += 1
                else: updated_count += 1
                
            msg = f"Saved {created_count} models, Updated {updated_count} models. Failed: {skipped_count}."
            return Response({"message": msg}, status=200 if (created_count+updated_count)>0 else 400)
            
        except Exception as e:
            return Response({"error": f"Error processing file: {str(e)}"}, status=400)

    @action(detail=False, methods=['get'])
    def export_data(self, request):
        model_class = self.get_model_class()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="All_{model_class.__name__}s_List.csv"'
        writer = csv.writer(response)
        
        headers = [self.unique_field] + self.update_fields
        writer.writerow([h.replace('_', ' ').title() for h in headers])
        
        for obj in model_class.objects.all().order_by('-id'):
            row_data = [str(getattr(obj, field)) if getattr(obj, field) is not None else '-' for field in headers]
            writer.writerow(row_data)
        return response

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        model_class = self.get_model_class()
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No records selected!"}, status=400)
        try:
            deleted_count, _ = model_class.objects.filter(id__in=ids).delete()
            return Response({"message": f"Successfully deleted {deleted_count} record(s)."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# --- 🚀 MASTER VIEWSETS ---
class FirmViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
    queryset = Firm.objects.all().order_by('-id')
    serializer_class = FirmSerializer
    unique_field = 'name'
    update_fields = [] 

class LocationViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('-id')
    serializer_class = LocationSerializer
    unique_field = 'name'
    update_fields = []

class MerchantViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
    queryset = Merchant.objects.all().order_by('-id')
    serializer_class = MerchantSerializer
    unique_field = 'name'
    update_fields = []

class SellerViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
    serializer_class = SellerSerializer  
    unique_field = 'gstn_no'
    update_fields = ['name', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

    def get_queryset(self):
        queryset = Seller.objects.all().order_by('-id')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(gstn_no__icontains=search))
        return queryset

class ProductModelViewSet(MasterBulkOperationsMixin, viewsets.ModelViewSet):
    serializer_class = ProductModelSerializer 
    unique_field = 'asin_fsn'
    update_fields = ['model_name', 'model', 'sap_polyshri', 'sap_rio', 'sap_ne', 'sap_sms', 'sap_smmpl']

    def get_queryset(self):
        queryset = ProductModel.objects.all().order_by('-id')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(asin_fsn__icontains=search) | Q(model_name__icontains=search) | Q(model__icontains=search))
        return queryset

#-------------------------INVOICE SHIPMENT---------------
class InvoiceShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceShipmentSerializer
    pagination_class = StandardResultsSetPagination 
    
    def get_queryset(self):
        try:
            queryset = InvoiceShipment.objects.all().order_by('-id')
            date_type = self.request.query_params.get('date_type', 'txn_date')
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')

            if start_date and end_date:
                if date_type == 'invoice_date': queryset = queryset.filter(invoice_date__range=[start_date, end_date])
                elif date_type == 'delivery_date': queryset = queryset.filter(delivery_date__range=[start_date, end_date])
                else: queryset = queryset.filter(txn_date__range=[start_date, end_date])
            elif start_date:
                if date_type == 'invoice_date': queryset = queryset.filter(invoice_date__gte=start_date)
                elif date_type == 'delivery_date': queryset = queryset.filter(delivery_date__gte=start_date)
                else: queryset = queryset.filter(txn_date__gte=start_date)
            elif end_date:
                if date_type == 'invoice_date': queryset = queryset.filter(invoice_date__lte=end_date)
                elif date_type == 'delivery_date': queryset = queryset.filter(delivery_date__lte=end_date)
                else: queryset = queryset.filter(txn_date__lte=end_date)

            order_id = self.request.query_params.get('order_id')
            delivery_status = self.request.query_params.get('delivery_status')
            invoice_no = self.request.query_params.get('invoice_no')
            firm = self.request.query_params.get('firm')
            location = self.request.query_params.get('location')

            if order_id: queryset = queryset.filter(order_id__icontains=order_id)
            if delivery_status: queryset = queryset.filter(delivery_status__iexact=delivery_status)
            if invoice_no: queryset = queryset.filter(invoice_no__icontains=invoice_no)
            if firm: queryset = queryset.filter(firm__iexact=firm)
            if location: queryset = queryset.filter(location__iexact=location)

            search_query = self.request.query_params.get('search', '').strip()
            if search_query:
                queryset = queryset.filter(
                    Q(order_id__icontains=search_query) |
                    Q(invoice_no__icontains=search_query) |
                    Q(seller_name__icontains=search_query) |
                    Q(asin_fsn__icontains=search_query) |
                    Q(model_no__icontains=search_query) |
                    Q(seller_gstn__icontains=search_query) |
                    Q(tracking_id__icontains=search_query) |
                    Q(cancel_reason__icontains=search_query) 
                )
            return queryset
        except Exception as e:
            return InvoiceShipment.objects.none()

    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        ids = request.data.get('ids', [])
        new_status = request.data.get('delivery_status')
        new_date = request.data.get('delivery_date')
        new_reason = request.data.get('cancel_reason') 
        
        if not ids: return Response({"error": "No IDs selected!"}, status=400)
        
        updated = 0
        for shipment in InvoiceShipment.objects.filter(id__in=ids):
            if new_status: shipment.delivery_status = new_status
            if new_date: shipment.delivery_date = new_date
            
            if new_status and new_status.lower() == 'cancelled':
                shipment.invoice_status = 'Cancel'
                if new_reason: shipment.cancel_reason = new_reason

            shipment.save() # Triggers signal
            updated += 1
            
        return Response({"message": f"Successfully updated {updated} shipments."}, status=200)


class InvoiceShipmentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file: return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file.name.endswith('.csv'): 
                try: df = pd.read_csv(file)
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='cp1252') 
            else: df = pd.read_excel(file)
            
            column_map = {
                'order_id': ['order id'], 'txn_date': ['order date'], 
                'firm': ['account group'], 'location': ['shipping address'], 
                'seller_name': ['seller name'], 'seller_gstn': ['seller gstn', 'seller gstin'],
                'invoice_no': ['invoice number', 'invoice no'], 'invoice_date': ['invoice date'],
                'invoice_qty': ['shipment quantity', 'item quantity'], 
                'invoice_amount': ['invoice total amount', 'item net total'], 
                'tracking_id': ['carrier tracking #', 'tracking id']
            }

            df.columns = df.columns.str.strip().str.lower()
            uploaded_headers = set(df.columns)
            
            REQUIRED_FIELDS = ['order_id', 'invoice_no'] 
            missing_critical = []
            actual_column_names = {} 
            for db_key, aliases in column_map.items():
                clean_aliases = [alias.lower().strip() for alias in aliases]
                found_col = next((alias for alias in clean_aliases if alias in uploaded_headers), None)
                if found_col: actual_column_names[db_key] = found_col
                elif db_key in REQUIRED_FIELDS: missing_critical.append(db_key.upper())

            if missing_critical:
                return Response({"error": f"Excel error! Zaroori columns missing hain: {', '.join(missing_critical)}."}, status=status.HTTP_400_BAD_REQUEST)

            df = df.fillna('')
            
            # 🔥 SMART MASTER & ORDER FETCHING 🔥
            valid_firms = {f.strip().lower(): f for f in Firm.objects.values_list('name', flat=True) if f}
            valid_locations = {l.strip().lower(): l for l in Location.objects.values_list('name', flat=True) if l}
            
            # Order ID ko bhi smart lowercase me match karenge
            all_orders = {order.order_id.strip().lower(): order for order in OrderReport.objects.all()}
            existing_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            existing_invoices_lower = {inv.strip().lower() for inv in existing_invoices}
            
            file_invoices = set()
            skipped_errors = {}

            def get_val(row_data, db_field_key, return_type='str'):
                col_name = actual_column_names.get(db_field_key)
                if not col_name or col_name not in row_data:
                    return 0.0 if return_type == 'num' else ''
                val = row_data[col_name]
                if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', 'null', '']:
                    return 0.0 if return_type == 'num' else ''
                if return_type == 'num':
                    try: return float(str(val).replace(',', '').replace('₹', '').replace('$', '').replace(' ', '').strip())
                    except: return 0.0
                return str(val).strip()

            records = []
            for index, row in df.iterrows():
                raw_order_id = get_val(row, 'order_id')
                if not raw_order_id: continue

                invoice_no = get_val(row, 'invoice_no')
                if not invoice_no: continue
                
                # Check 1: Order ID must exist in Orders Master
                clean_order_id = raw_order_id.strip().lower()
                if clean_order_id not in all_orders: 
                    skipped_errors["Order ID not found"] = skipped_errors.get("Order ID not found", 0) + 1
                    continue
                
                # Check 2: Invoice Number Uniqueness
                clean_inv_no = invoice_no.strip().lower()
                if clean_inv_no in existing_invoices_lower or clean_inv_no in file_invoices: 
                    skipped_errors["Duplicate Invoice No"] = skipped_errors.get("Duplicate Invoice No", 0) + 1
                    continue 
                file_invoices.add(clean_inv_no)

                # Fetching Master Order details smoothly
                order_data = all_orders[clean_order_id]
                
                # 🔥 SMART LOCATION & FIRM VALIDATION 🔥
                raw_firm = get_val(row, 'firm')
                raw_shipping_address = get_val(row, 'location')
                
                row_errors = []
                final_location = ""

                # Firm Strict check (If firm is in excel)
                if raw_firm and raw_firm.strip().lower() not in valid_firms:
                    row_errors.append(f"Firm '{raw_firm}'")
                
                # Smart Location Extraction from long address
                if raw_shipping_address:
                    addr_lower = raw_shipping_address.strip().lower()
                    for master_loc_lower, master_loc_actual in valid_locations.items():
                        if master_loc_lower in addr_lower:
                            final_location = master_loc_actual
                            break
                    if not final_location:
                        row_errors.append(f"Location not mapped from address")
                
                if row_errors:
                    err_msg = "Master Data Error: " + ", ".join(row_errors)
                    skipped_errors[err_msg] = skipped_errors.get(err_msg, 0) + 1
                    continue # Reject this Invoice!

                raw_inv_date = get_val(row, 'invoice_date')
                try: invoice_date = pd.to_datetime(raw_inv_date, dayfirst=True).strftime('%Y-%m-%d') if raw_inv_date else None
                except: invoice_date = None

                records.append(InvoiceShipment(
                    order_id=order_data.order_id, txn_date=order_data.txn_date, asin_fsn=order_data.asin_fsn,
                    model_name=order_data.model_name, model_no=order_data.model_no, unit_price=order_data.unit_price, 
                    order_qty=order_data.order_qty, order_amount=order_data.order_amount,
                    
                    # Smart Master Assingments
                    firm=valid_firms.get(raw_firm.strip().lower(), raw_firm) if raw_firm else order_data.firm, 
                    location=final_location if final_location else order_data.location, 
                    
                    seller_name=get_val(row, 'seller_name'), seller_gstn=get_val(row, 'seller_gstn'),
                    invoice_no=invoice_no, invoice_date=invoice_date,
                    invoice_qty=int(get_val(row, 'invoice_qty', 'num') or 1),
                    invoice_amount=get_val(row, 'invoice_amount', 'num'),
                    tracking_id=get_val(row, 'tracking_id'),
                    delivery_status="Pending" 
                ))
            
            if records: InvoiceShipment.objects.bulk_create(records, ignore_conflicts=True)
            
            if not skipped_errors:
                return Response({"message": f"{len(records)} Shipments extracted and uploaded successfully!"}, status=status.HTTP_201_CREATED)
            else:
                error_summary = " | ".join([f"{count} skipped ({reason})" for reason, count in skipped_errors.items()])
                if len(records) == 0:
                    return Response({"error": f"Upload Failed! 0 saved.\nErrors: {error_summary}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": f"Partial Success: {len(records)} saved.\nWARNING: {error_summary}"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": f"Upload Processing Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def fetch_order_for_shipment(request, order_id):
    orders = OrderReport.objects.filter(order_id=order_id)
    if not orders.exists():
        return Response({"error": "Order ID not found in database!"}, status=404)

    order_data = []
    for order in orders:
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
            "seller_name": "",
            "seller_gstn": "",
            "invoice_no": "",
            "invoice_date": "",
            "invoice_qty": order.order_qty,     
            "invoice_amount": order.order_amount,
            "delivery_status": "Pending",
            "delivery_date": "",
            "tracking_id": "",
            "is_existing": False,
            "shipment_id": None
        }
        order_data.append(item_data)
    return Response(order_data, status=200)


#-------------------VIEW Button API --------------------
class OrderSummaryView(APIView):
    def get(self, request, pk):
        try:
            order = OrderReport.objects.get(id=pk)
            target_order_id = order.order_id
            target_asin = order.asin_fsn
            
            shipments = InvoiceShipment.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            first_ship = shipments.exclude(seller_name__exact='').exclude(seller_name__isnull=True).first()
            
            seller_name_fetched = first_ship.seller_name if first_ship else getattr(order, 'seller_name', '-')
            seller_gstn_fetched = first_ship.seller_gstn if first_ship else getattr(order, 'seller_gstn', '-')
            if not seller_name_fetched or str(seller_name_fetched).strip() == '': seller_name_fetched = '-'
            if not seller_gstn_fetched or str(seller_gstn_fetched).strip() == '': seller_gstn_fetched = '-'

            inwards = InwardRecord.objects.filter(order_id=target_order_id, asin_fsn=target_asin)
            refunds = RefundRecord.objects.filter(order_id=target_order_id) 
            
            delivered_shipments = shipments.filter(delivery_status='Delivered')
            delivered_qty = delivered_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            delivered_amount = float(delivered_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
            cancelled_shipments = shipments.filter(delivery_status='Cancelled')
            cancel_qty = cancelled_shipments.aggregate(Sum('invoice_qty'))['invoice_qty__sum'] or 0
            cancel_amount = float(cancelled_shipments.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)
            
            inward_qty = inwards.aggregate(Sum('inward_qty'))['inward_qty__sum'] or 0
            inward_amount = float(inwards.aggregate(Sum('inward_amount'))['inward_amount__sum'] or 0.0)
            
            short_qty = inwards.aggregate(Sum('short_qty'))['short_qty__sum'] or 0
            short_amount = float(inwards.aggregate(Sum('short_amount'))['short_amount__sum'] or 0.0)

            refund_qty = refunds.count() 
            refund_amount = float(refunds.aggregate(Sum('invoice_amount'))['invoice_amount__sum'] or 0.0)

            pending_qty = order.order_qty - delivered_qty - cancel_qty
            pending_amount = float(order.order_amount) - delivered_amount - cancel_amount
            pending_refund_amount = cancel_amount + short_amount - refund_amount
            
            # 🔥 FIX: Do not override "Cancelled" status
            current_status = getattr(order, 'order_status', getattr(order, 'status', 'Open'))
            if current_status not in ['Cancelled', 'Cancel Confirmation']:
                calculated_status = "Complete" if pending_qty <= 0 else "Open"
                if current_status != calculated_status:
                    order.order_status = calculated_status
                    order.save()
            else:
                calculated_status = current_status

            summary_data = {
                "order_id": target_order_id,
                "txn_date": order.txn_date,
                "asin_fsn": target_asin,
                "model_no": order.model_no,
                "order_qty": order.order_qty,
                "order_amount": float(order.order_amount),
                "order_status": calculated_status,
                
                "card_no": order.card_no or "-",
                "placed_by": order.placed_by or "-",
                "sap_po_no": getattr(order, 'sap_po_no', '-'), 
                "seller_name": seller_name_fetched, 
                "seller_gstn": seller_gstn_fetched, 
                "cn_amount": float(getattr(order, 'cn_amount', 0.0)),
                
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
                "inward_amount": inward_amount,
                "grpo_qty": getattr(order, 'grpo_qty', 0),
                "grpo_amount": float(getattr(order, 'grpo_amount', 0.0))
            }
            return Response(summary_data, status=200)
            
        except OrderReport.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        except Exception as e:
            return Response({"error": f"Error: {str(e)}"}, status=400)


class ExportOrderReportsExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = OrderReport.objects.all()

        merchant = request.query_params.get('merchant')
        status_val = request.query_params.get('order_status') 
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        search = request.query_params.get('search') 

        if merchant: queryset = queryset.filter(merchant__icontains=merchant)
        if status_val: queryset = queryset.filter(order_status__iexact=status_val)
        if start_date and end_date: queryset = queryset.filter(txn_date__range=[start_date, end_date])
        if search: queryset = queryset.filter(order_id__icontains=search) 

        data = queryset.values(
            'order_id', 'txn_date', 'month', 'day', 'txn_detail', 
            'merchant', 'merchant_id', 'firm', 'location', 
            'asin_fsn', 'model_name', 'model_no', 
            'order_qty', 'order_amount', 'unit_price', 
            'payment_amount', 'card_offer'
        )
        
        df = pd.DataFrame(list(data))
        if df.empty:
            df = pd.DataFrame(columns=['S.No', 'Order ID', 'Date', 'No Data Found For This Filter'])
        else:
            df.insert(0, 'S.No', range(1, len(df) + 1))
            df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            df.rename(columns={
                'Asin Fsn': 'ASIN/FSN', 'Payment Amount': 'Payment',
                'Order Qty': 'Qty', 'Order Amount': 'Order Amt'
            }, inplace=True)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Filtered_Order_Reports.xlsx"'
        
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Orders')
        return response   

class ExportInvoiceShipmentExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = InvoiceShipment.objects.all()
        merchant = request.query_params.get('merchant')
        invoice_no = request.query_params.get('invoice_no')
        
        if merchant: queryset = queryset.filter(firm__icontains=merchant)
        if invoice_no: queryset = queryset.filter(invoice_no__icontains=invoice_no)

        data = queryset.values(
            'order_id', 'txn_date', 'firm', 'location', 'seller_name', 'seller_gstn',
            'invoice_no', 'invoice_date', 'asin_fsn', 'model_name', 'model_no',
            'invoice_qty', 'invoice_amount', 'unit_price', 'tracking_id', 
            'delivery_date'
        )
        
        df = pd.DataFrame(list(data))
        if df.empty:
            df = pd.DataFrame(columns=['S.No', 'Invoice No', 'Date', 'No Data Found For This Filter'])
        else:
            df.insert(0, 'S.No', range(1, len(df) + 1))
            df.columns = [col.replace('_', ' ').title() if col != 'S.No' else col for col in df.columns]
            df.rename(columns={'Asin Fsn': 'ASIN/FSN', 'Txn Date': 'Txn Date'}, inplace=True)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Invoice_Shipments.xlsx"'
        
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Invoices')
        return response   

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_orders(request):
    ids_to_delete = request.data.get('ids', [])
    if not ids_to_delete: return Response({"error": "No records selected!"}, status=400)
    try:
        deleted_count, _ = OrderReport.objects.filter(id__in=ids_to_delete).delete()
        return Response({"message": f"Successfully deleted {deleted_count} Order Report(s)."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_invoices(request):
    ids_to_delete = request.data.get('ids', [])
    if not ids_to_delete: return Response({"error": "No records selected!"}, status=400)
    try:
        deleted_count, _ = InvoiceShipment.objects.filter(id__in=ids_to_delete).delete()
        return Response({"message": f"Successfully deleted {deleted_count} Invoice Shipment(s)."}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)  
          
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def upload_models_excel(request):
    if 'file' not in request.FILES: return Response({"error": "No file uploaded."}, status=400)
    file = request.FILES['file']
    try:
        if file.name.endswith('.csv'): df = pd.read_csv(file)
        else: df = pd.read_excel(file)

        df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
        success_count, error_count = 0, 0

        for index, row in df.iterrows():
            try:
                asin_fsn = str(row.get('asin_fsn') or row.get('asn_fsn') or '').strip()
                if not asin_fsn or asin_fsn == 'nan': continue 

                ProductModel.objects.update_or_create(
                    asin_fsn=asin_fsn,
                    defaults={
                        'model_name': str(row.get('model_name', '')).strip() if pd.notna(row.get('model_name')) else "",
                        'model': str(row.get('model', '')).strip() if pd.notna(row.get('model')) else "",
                        'sap_polyshri': str(row.get('sap_polyshri', '')).strip() if pd.notna(row.get('sap_polyshri')) else "",
                        'sap_rio': str(row.get('sap_rio', '')).strip() if pd.notna(row.get('sap_rio')) else "",
                        'sap_ne': str(row.get('sap_ne', '')).strip() if pd.notna(row.get('sap_ne')) else "",
                        'sap_sms': str(row.get('sap_sms', '')).strip() if pd.notna(row.get('sap_sms')) else "",
                        'sap_smmpl': str(row.get('sap_smmpl', '')).strip() if pd.notna(row.get('sap_smmpl')) else "",
                    }
                )
                success_count += 1
            except Exception as row_err:
                error_count += 1
        return Response({"message": f"Saved/Updated {success_count} models. Failed: {error_count}."}, status=200)
    except Exception as e:
        return Response({"error": "Failed to read Excel file."}, status=500)  
      
class ApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_role = getattr(self.request.user, 'role', None)
        username = getattr(self.request.user, 'username', str(self.request.user))
        
        if user_role == 'ADMIN' or self.request.user.is_superuser or self.request.user.is_staff:
            return ApprovalRequest.objects.all().order_by('-id')
            
        return ApprovalRequest.objects.filter(
            Q(requested_by__iexact=username) | Q(placed_by__iexact=username)
        ).order_by('-id')

    @action(detail=False, methods=['get'])
    def dropdown_data(self, request):
        return Response({
            'firms': FirmDropdownSerializer(Firm.objects.all(), many=True).data,
            'locations': LocationDropdownSerializer(Location.objects.all(), many=True).data,
            'merchants': MerchantDropdownSerializer(Merchant.objects.all(), many=True).data,
            'models': ModelDropdownSerializer(ProductModel.objects.all(), many=True).data,
        })

    def perform_create(self, serializer):
        merchant = serializer.validated_data.get('merchant')
        merchant_name = merchant.name.upper() if merchant else ""
        
        if 'AMAZON' in merchant_name: prefix = "AMZ"
        elif 'FLIPKART' in merchant_name: prefix = "FK"
        else: prefix = "RL"
            
        last_approval = ApprovalRequest.objects.filter(approval_no__startswith=prefix).order_by('-id').first()
        if last_approval and last_approval.approval_no:
            try:
                last_no = last_approval.approval_no.replace(prefix, "")
                new_no = int(last_no) + 1
            except ValueError: new_no = 1
        else: new_no = 1
            
        new_approval_no = f"{prefix}{str(new_no).zfill(5)}"
        serializer.save(approval_no=new_approval_no)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user_role = getattr(request.user, 'role', None)
        if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
            return Response({"error": "Security Alert: Only authorized Admins can approve."}, status=403)
            
        approval = self.get_object()
        approval.status = 'Approved'
        current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
        approval.authorized_by = f"{request.user.username} ({current_time})"
        approval.save()
        return Response({"message": "Approval Request Approved Successfully!"}, status=200)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        user_role = getattr(request.user, 'role', None)
        if not (user_role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
            return Response({"error": "Security Alert: Only authorized Admins can reject."}, status=403)
            
        approval = self.get_object()
        approval.status = 'Rejected'
        current_time = timezone.localtime(timezone.now()).strftime('%d/%m/%Y %I:%M %p')
        approval.authorized_by = f"{request.user.username} ({current_time})"
        approval.save()
        return Response({"message": "Approval Request Rejected Successfully!"}, status=200)


class GRPORecordViewSet(viewsets.ModelViewSet):
    queryset = GRPORecord.objects.all().order_by('-id')
    serializer_class = GRPORecordSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def upload_excel(self, request):
        file = request.FILES.get('file')
        if not file: 
            return Response({"error": "No file uploaded!"}, status=400)
        
        try:
            file.seek(0) # Safety check for file reading
            if file.name.endswith('.csv'): 
                df = pd.read_csv(file)
            else: 
                df = pd.read_excel(file)
            
            # Lowercase headers to avoid Case Sensitive issues
            df.columns = [str(col).strip().lower() for col in df.columns]
            df = df.fillna('')
            
            valid_invoices = set(InvoiceShipment.objects.exclude(invoice_no='').values_list('invoice_no', flat=True))
            
            created_count, updated_count, skipped_count = 0, 0, 0
            successful_invoices = []
            
            for index, row in df.iterrows():
                inv_no = str(row.get('grpo_invoice_number', '')).strip()
                
                # Check 1: Must have invoice number and should be valid
                if not inv_no or inv_no not in valid_invoices:
                    skipped_count += 1
                    continue
                
                grpo_qty = str(row.get('grpo_quantity', '0')).replace(',', '').strip()
                grpo_amt = str(row.get('grpo_amt', '0')).replace(',', '').strip()

                # 🔥 FIX 1: Prevent Duplicates using update_or_create (Checks by Invoice Number)
                obj, created = GRPORecord.objects.update_or_create(
                    grpo_invoice_number=inv_no,
                    defaults={
                        'firm_name': str(row.get('firm_name', '')),
                        'internal_number': str(row.get('internal_number', '')),
                        'grpo_status': str(row.get('grpo_status', 'Open')),
                        'grpo_user_name': str(row.get('grpo_user_name', '')),
                        'grpo_no': str(row.get('grpo_no', '')),
                        'grpo_create_date': str(row.get('grpo_create_date', '')),
                        'grpo_posting_date': str(row.get('grpo_posting_date', '')),
                        'purchase_vendor_code': str(row.get('purchase_vendor_code', '')),
                        'purchase_vendor_name': str(row.get('purchase_vendor_name', '')),
                        'inward_whs_code': str(row.get('inward_whs_code', '')),
                        'item_code': str(row.get('item_code', '')),
                        'description': str(row.get('description', '')),
                        'grpo_quantity': float(grpo_qty) if grpo_qty.replace('.','',1).isdigit() else 0.0,
                        'grpo_amt': float(grpo_amt) if grpo_amt.replace('.','',1).isdigit() else 0.0,
                    }
                )
                
                if created: 
                    created_count += 1
                else: 
                    updated_count += 1
                    
                # Store the invoice number for status update
                successful_invoices.append(inv_no)
            
            # 🔥 FIX 2: Manually update Inward Status in Bulk (Since bulk ignores signals)
            if successful_invoices:
                try:
                    InvoiceShipment.objects.filter(
                        invoice_no__in=successful_invoices
                    ).update(delivery_status='Done') # 👈 Yahan bhi change kiya
                except Exception as e:
                    print("Status update warning:", str(e))
            
            # Prepare final response message
            msg = f"Success! Created {created_count}, Updated {updated_count} GRPO records."
            if skipped_count > 0: 
                msg += f" (Warning: {skipped_count} skipped - invalid Invoice No)"
            
            return Response({"message": msg}, status=201 if (created_count + updated_count) > 0 else 400)
            
        except Exception as e:
            return Response({"error": f"File error: {str(e)}"}, status=500)


class DownloadApprovalPDF(APIView):
    def get(self, request, pk):
        try:
            approval = ApprovalRequest.objects.get(pk=pk)
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
            elements = []
            
            title_style = ParagraphStyle(name="TitleStyle", fontSize=14, fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a"))
            timestamp_style = ParagraphStyle(name="TimestampStyle", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=2)
            generated_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            header_table = Table([[Paragraph(f"<b>{approval.approval_no} — Online Order Placement Tracker</b>", title_style), Paragraph(f"Generated: {generated_time}", timestamp_style)]], colWidths=[550, 240])
            header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
            elements.append(header_table)
            elements.append(Spacer(1, 15))

            firm_name = approval.firm.name if hasattr(approval, 'firm') and approval.firm else "-"
            ship_loc = approval.ship_location.name if hasattr(approval, 'ship_location') and approval.ship_location else "-"
            bill_loc = approval.bill_location.name if hasattr(approval, 'bill_location') and approval.bill_location else "-"
            merchant_name = approval.merchant.name if hasattr(approval, 'merchant') and approval.merchant else "-"

            data_top = [
                ["Approval Date:", approval.request_date.strftime('%d/%m/%Y') if approval.request_date else "-", "Order Requested By:", str(approval.requested_by or "-")],
                ["Firm Name:", firm_name, "Merchant:", merchant_name],
                ["Ship Location:", ship_loc, "Merchant_ID:", str(approval.merchant_account_id or "-")],
                ["Bill Location:", bill_loc, "Authorized By:", str(approval.authorized_by or "-")]
            ]
            t_top = Table(data_top, colWidths=[90, 260, 110, 310])
            t_top.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,-1), 9), ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#334155")), ('BOTTOMPADDING', (0,0), (-1,-1), 5),]))
            elements.append(t_top)
            elements.append(Spacer(1, 20))

            cell_style = ParagraphStyle(name='CellStyle', fontSize=7, leading=9, textColor=colors.HexColor("#475569"))
            header_cell_style = ParagraphStyle(name='HeaderCellStyle', fontSize=8, leading=10, textColor=colors.white, fontName='Helvetica-Bold')

            headers = [
                Paragraph("<b>ASIN/FSN</b>", header_cell_style), Paragraph("<b>Model</b>", header_cell_style), 
                Paragraph("<b>Req<br/>Qty</b>", header_cell_style), Paragraph("<b>Purchase<br/>Price</b>", header_cell_style), 
                Paragraph("<b>CN</b>", header_cell_style), Paragraph("<b>Agreed<br/>NLC</b>", header_cell_style), 
                Paragraph("<b>Link<br/>Used</b>", header_cell_style), Paragraph("<b>Placed<br/>Qty</b>", header_cell_style), 
                Paragraph("<b>Order<br/>NLC</b>", header_cell_style), Paragraph("<b>Payment<br/>Method</b>", header_cell_style), 
                Paragraph("<b>Delivery<br/>Date</b>", header_cell_style), Paragraph("<b>Total<br/>Cost</b>", header_cell_style)
            ]
            
            item_data = [headers]
            total_req_qty, total_placed_qty, total_cost_sum = 0, 0, 0.0

            for item in approval.items.all():
                req_qty = item.req_qty or 0
                placed_qty = item.placed_qty or 0
                tot_cost = float(item.total_placed_amt or 0)
                total_req_qty += req_qty
                total_placed_qty += placed_qty
                total_cost_sum += tot_cost
                del_date = item.expected_delivery_date.strftime('%d/%m/%Y') if item.expected_delivery_date else "-"

                item_data.append([
                    Paragraph(str(item.asin_fsn or "-"), cell_style), Paragraph(str(item.model_name or "-"), cell_style), 
                    str(req_qty), f"Rs. {item.purchase_price or 0}", f"Rs. {item.cn_amt or 0}", f"Rs. {item.agreed_nlc or 0}", 
                    str(item.link_used or "-"), str(placed_qty), f"Rs. {item.order_nlc or 0}", Paragraph(str(item.payment_method or "-"), cell_style), 
                    Paragraph(del_date, cell_style), f"Rs. {tot_cost}"
                ])

            item_data.append(["Total", "", str(total_req_qty), "", "", "", "", str(total_placed_qty), "", "", "", f"Rs. {total_cost_sum}"])
            t_items = Table(item_data, colWidths=[75, 140, 30, 55, 45, 55, 30, 35, 55, 70, 55, 60])
            
            table_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")), ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-2), 8), ('TEXTCOLOR', (0,1), (-1,-2), colors.HexColor("#475569")), ('BOTTOMPADDING', (0,1), (-1,-1), 5),
                ('TOPPADDING', (0,1), (-1,-1), 5), ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#e2e8f0")), 
            ])
            for i in range(1, len(item_data)-1):
                if i % 2 == 0: table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8fafc"))
                    
            table_style.add('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#fef3c7"))
            table_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
            table_style.add('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#000000"))
            table_style.add('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor("#eab308"))
            
            t_items.setStyle(table_style)
            elements.append(t_items)
            elements.append(Spacer(1, 40))

            req_by_text = approval.requested_by if approval.requested_by else "_________________________"
            placed_by_text = approval.placed_by if approval.placed_by else "_________________________"
            approved_by_text = approval.authorized_by if approval.authorized_by else "_________________________"

            sig_data = [["Order Requested By", "Order Placed By", "Order Approved By"], [f"\n\n\n{req_by_text}", f"\n\n\n{placed_by_text}", f"\n\n\n{approved_by_text}"]]
            t_sigs = Table(sig_data, colWidths=[260, 260, 260])
            t_sigs.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 9), ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#334155")), ('FONTNAME', (0,1), (-1,1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,1), 9)]))
            elements.append(t_sigs)
            elements.append(Spacer(1, 30))
            
            disclaimer = ParagraphStyle(name="Disclaimer", fontSize=7, textColor=colors.HexColor("#94a3b8"))
            elements.append(Paragraph(f"This document was generated automatically on {generated_time} upon approval.", disclaimer))

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Approval_{approval.approval_no}.pdf"'
            return response
        except Exception as e:
            return HttpResponse(f"Error generating PDF: {str(e)}", status=400)    


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-id')
    serializer_class = TicketSerializer

class RefundRecordViewSet(viewsets.ModelViewSet):
    queryset = RefundRecord.objects.all().order_by('-id')
    serializer_class = RefundRecordSerializer
    permission_classes = [IsAuthenticated]

class DashboardStatsView(APIView):
    def get(self, request):
        try:
            total_orders = OrderReport.objects.count()
            open_orders = OrderReport.objects.filter(order_status='Open').count()
            completed_orders = OrderReport.objects.filter(order_status='Complete').count()
            
            revenue_data = OrderReport.objects.aggregate(total_revenue=Sum('order_amount'))
            total_revenue = float(revenue_data['total_revenue'] or 0.0)

            merchants_data = OrderReport.objects.values('merchant').annotate(
                total_sales=Sum('order_amount')
            ).order_by('-total_sales')

            pie_data = []
            for item in merchants_data:
                merchant_name = item['merchant'] or 'Others'
                pie_data.append({
                    "name": merchant_name,
                    "value": float(item['total_sales'] or 0.0)
                })

            return Response({
                "kpis": {
                    "totalOrders": total_orders,
                    "openOrders": open_orders,
                    "completed": completed_orders,
                    "revenue": total_revenue
                },
                "pieData": pie_data
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_invoice_for_grpo(request, invoice_no):
    shipments = InvoiceShipment.objects.filter(invoice_no=invoice_no)
    if not shipments.exists(): 
        return Response({"error": "Invoice Number not found in database!"}, status=404)

    data = []
    for ship in shipments:
        data.append({
            "firm_name": ship.firm, 
            "purchase_vendor_name": ship.seller_name,
            "item_code": ship.asin_fsn, 
            "description": ship.model_name,
            "grpo_quantity": ship.invoice_qty, 
            "grpo_amt": ship.invoice_amount,
        })
    return Response(data, status=200)   

class PurchaseInwardViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInward.objects.all().order_by('-id')
    serializer_class = PurchaseInwardSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_grpo_for_inward(request, grpo_no):
    try:
        grpo_record = GRPORecord.objects.filter(grpo_no=grpo_no).first()
        if not grpo_record: 
            return Response({"error": "Bhai, ye GRPO Number database me nahi mila!"}, status=404)
            
        data = {
            "grpo_no": grpo_record.grpo_no, 
            "firm_name": grpo_record.firm_name,
            "vendor_name": grpo_record.purchase_vendor_name, 
            "item_code": grpo_record.item_code,
            "expected_qty": grpo_record.grpo_quantity, 
            "warehouse_location": grpo_record.inward_whs_code,
        }
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)  

@receiver(post_save, sender=OrderReport)
def create_refund_on_order_cancel(sender, instance, created, **kwargs):
    order_status = getattr(instance, 'order_status', getattr(instance, 'status', ''))
    
    if order_status in ['Cancelled', 'Cancel Confirmation']:
        refund_exists = RefundRecord.objects.filter(order_id=instance.order_id).exists()
        if not refund_exists:
            RefundRecord.objects.create(
                source_date=instance.txn_date,
                firm=instance.firm,
                merchant=instance.merchant,
                order_id=instance.order_id,
                invoice_no="-", 
                model_name=instance.model_name,
                refund_qty=getattr(instance, 'order_qty', 1),
                invoice_amount=getattr(instance, 'order_amount', 0), 
                received_comment="Auto-Cancelled from Order Dashboard" # FIX: 'remarks' aur 'status' hata diya gaya hai
            )


# . AUTO-REFUND TRIGGER FOR INVOICES 
# =======================================================
@receiver(post_save, sender=InvoiceShipment)
def create_refund_on_invoice_cancel(sender, instance, created, **kwargs):
    delivery_status = getattr(instance, 'delivery_status', '')
    invoice_status = getattr(instance, 'invoice_status', '')
    
    if delivery_status == 'Cancelled' or invoice_status == 'Cancel':
        # Check 1: Kya is exact invoice no. ka refund pehle se hai?
        invoice_refund_exists = RefundRecord.objects.filter(invoice_no=instance.invoice_no).exists()
        
        if not invoice_refund_exists:
            # Check 2: Kya Order level par koi generic refund bana hai (jiska invoice_no "-" hai)?
            generic_refund = RefundRecord.objects.filter(
                order_id=instance.order_id, 
                invoice_no="-", 
                model_name=instance.model_name
            ).first()
            
            if generic_refund:
                # 🔥 DUPLICATE BANANE KE BAJAYE, PURANE WALE KO HI UPDATE KAR DO! 🔥
                generic_refund.invoice_no = instance.invoice_no
                generic_refund.merchant = getattr(instance, 'seller_name', generic_refund.merchant)
                generic_refund.received_comment = "Auto-Cancelled (Order & Invoice Linked)"
                generic_refund.save()
            else:
                # Agar generic nahi hai (yani user ne direct Invoice dashboard se cancel kiya hai), toh naya banao
                RefundRecord.objects.create(
                    source_date=instance.txn_date,
                    firm=instance.firm,
                    merchant=getattr(instance, 'seller_name', 'Unknown'),
                    order_id=instance.order_id, 
                    invoice_no=instance.invoice_no,
                    model_name=instance.model_name,
                    refund_qty=getattr(instance, 'invoice_qty', 1),
                    invoice_amount=getattr(instance, 'invoice_amount', 0), 
                    received_comment="Auto-generated from Cancelled Shipment"
                )
@receiver(post_save, sender=GRPORecord)
def update_invoice_on_grpo_upload(sender, instance, created, **kwargs):
    # Agar GRPO UI se manual banaya gaya hai, toh ye update karega
    if created and instance.grpo_invoice_number: 
        InvoiceShipment.objects.filter(
            invoice_no=instance.grpo_invoice_number
        ).update(delivery_status='Done')      

class WarehouseAuditViewSet(viewsets.ModelViewSet):
    queryset = WarehouseAudit.objects.all().order_by('-id')
    serializer_class = WarehouseAuditSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_invoice_for_audit(request, invoice_no):
    try:
        invoice = InvoiceShipment.objects.filter(invoice_no=invoice_no).first()
        if not invoice: return Response({"error": "Bhai, ye Invoice Number system me nahi mila!"}, status=404)
            
        data = {
            "invoice_no": invoice.invoice_no, "order_id": invoice.order_id,
            "expected_qty": invoice.invoice_qty, 
        }
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

class IMEIRecordViewSet(viewsets.ModelViewSet):
    queryset = IMEIRecord.objects.all().order_by('-id')
    serializer_class = IMEIRecordSerializer
    permission_classes = [IsAuthenticated]   

class AccountsLedgerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        card_no = request.query_params.get('card_number')
        firm = request.query_params.get('firm_name')

        if not card_no or not firm: return Response({"error": "Please provide both card_number and firm_name"}, status=400)

        ledger_entries = []
        settlements = Settlement.objects.filter(card_number=card_no, firm_name=firm)
        for s in settlements:
            if s.date:
                ledger_entries.append({
                    "date": str(s.date), "ref_no": s.txn_id, "type": s.txn_type,
                    "debit": 0.00, "credit": float(s.amount or 0), "remarks": s.remarks or "Manual Entry / Refill"
                })

        orders = OrderReport.objects.filter(card_no=card_no, firm=firm)
        for o in orders:
            if o.txn_date:
                ledger_entries.append({
                    "date": str(o.txn_date), "ref_no": o.order_id, "type": "Order Purchase",
                    "debit": float(o.order_amount or 0), "credit": 0.00, "remarks": f"ASIN: {o.asin_fsn} | Model: {o.model_name or ''}"
                })

        refunds = RefundRecord.objects.filter(received_card_no=card_no, firm=firm)
        for r in refunds:
            r_date = r.received_date if r.received_date else (r.created_at.date() if r.created_at else None)
            if r_date:
                ledger_entries.append({
                    "date": str(r_date), "ref_no": r.order_id, "type": f"Refund - {r.refund_type or 'General'}",
                    "debit": 0.00, "credit": float(r.invoice_amount or 0), "remarks": r.received_comment or "Refund Processed"
                })

        ledger_entries.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
        running_balance = 0.0
        for entry in ledger_entries:
            running_balance += entry['credit'] - entry['debit']
            entry['balance'] = round(running_balance, 2)

        return Response(ledger_entries)

class FinanceReconciliationViewSet(viewsets.ModelViewSet):
    queryset = FinanceReconciliation.objects.all().order_by('-date', '-id')
    serializer_class = FinanceReconciliationSerializer
    permission_classes = [IsAuthenticated]   

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by('-id')
    serializer_class = UserProfileSerializer

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        data_list = request.data
        for item in data_list:
            RolePermission.objects.update_or_create(
                section=item['section'], role=item['role'],
                defaults={
                    'can_read': item.get('can_read', False), 'can_create': item.get('can_create', False),
                    'can_change': item.get('can_change', False), 'can_delete': item.get('can_delete', False),
                    'can_approve': item.get('can_approve', False), 'can_administer': item.get('can_administer', False),
                }
            )
        return Response({"status": "Permissions Updated Successfully"})

class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all().order_by('-date', '-id')
    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated]