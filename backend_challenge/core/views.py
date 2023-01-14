import csv
import json
from django.http import HttpResponse
from rest_framework import status, viewsets, filters
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import api_view, permission_classes
from .models import Customer, Delivery, Driver, Order, RouteSettings
from .serializers import (
    CustomerSerializer,
    OrderSerializer,
    RouteSettingsSerializer,
    DeliverySerializer,
)
from .tasks import send_sms
from .exporter import ExportViewMixin
from django.template.defaultfilters import slugify
from rest_framework.reverse import reverse
from django.shortcuts import redirect


class CustomerProfileException(NotFound):
    """Exception raised when customer profile  is not present in the data."""

    status_code = 404
    default_detail = "Customer Profile not found.Create Cussomer profile"


class Customer_Create(APIView):
    permission_classes = [IsAuthenticated]

    """
   create a new customer
    """

    def post(self, request):
        data = request.data
        print(data)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListCreateAPIView(ListCreateAPIView):

    model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):

        user = self.request.user
        try:
            customer = Customer.objects.get(user=user)
        # if not customer:
        #     raise Http404("Create Customer Profile")
        except ObjectDoesNotExist as snip_no_exist:
            raise CustomerProfileException() from snip_no_exist
        return self.queryset.filter(customer=customer)

    def perform_create(self, serializer):
        if serializer.is_valid():
            order = serializer.save()
            transaction.on_commit(lambda: send_sms(order.id))


class OrderViewSet(
    viewsets.ModelViewSet,
    ExportViewMixin,
):
    """
    A viewset that provides the standard actions
    """

    model = Order
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["code", "category", "status"]

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context.update({"request": self.request})
    #     return context

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Order.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
            print(queryset)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
            print(queryset)

        return queryset

    @action(detail=True)
    def clone_order(self, request, pk=None):
        """
        Method to clone an order
        """
        order = self.get_object()
        order.pk = None
        order._state.adding = True

        cloned = order.save()

        if cloned:
            data = {"order_id": cloned.id, "order_code": clone.code}
            return Response(data)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ExportOrdersView(APIView, ExportViewMixin):
    """
    Viewset to export order
    """

    model = Order
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["code", "category", "status"]
    renderer_classes = [TemplateHTMLRenderer]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a ` query parameter in the URL.
        """
        queryset = Order.objects.all()
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
            print(queryset)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
            print(queryset)

        return queryset

    def get_serializer(self, queryset, many=True):
        return self.serializer_class(
            queryset,
            many=many,
        )

    def get(self, request, format=None):
        orders = self.get_queryset()
        return Response({"orders": orders}, template_name="orders.html")


class DeliveryViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """

    serializer_class = DeliverySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["code", "status"]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        qs = Delivery.objects.all()

        return qs

    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def assign(self, request, pk=None):
        """
        Method to assign an order to delivery
        """
        delivery = self.get_object()
        available_drivers = Driver.objects.filter(availability_status=True)
        if available_drivers.exists():
            driver = available_drivers.first()
            delivery = self.get_object()
            delivery.assign(driver)

            driver.availability_status = False
            driver.save()

            data = {
                "delivery_id": delivery.id,
                "order_code": delivery.code,
                "url": reverse("core:delivery-detail", args=[pk], request=request),
                "assignedto": driver.name,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            not_found = {"errors": "No drivers available."}
            return Response(data=not_found, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def export_deliveries(self, request, *args, **kwargs):
        """
        Method to export orders
        """
        queryset = self.filter_queryset(self.get_queryset())
        print(queryset)

        return self.export(queryset)

    @action(detail=False)
    def bulk_assign(self, request, *args, **kwargs):
        """
        Method to export orders
        """
        data = request.data
        

        selected_ids=data.get("data", None)
        if selected_ids:
   
        
            with transaction.atomic():
                for i in selected_ids:
                    key=i["id"]
                    delivery = Delivery.objects.get(id=key)
                    available_drivers = Driver.objects.filter(availability_status=True)
                    if available_drivers.exists():
                        driver = available_drivers.first()
                        delivery.assign(driver)
                        driver.update(availability_status=False)
                   
        

            return Response(data)

        else:
            return
        

       

    @action(detail=True)
    def clone_order(self, request, pk=None):
        """
        Method to clone an order
        """
        delivery = self.get_object()
        delivery.pk = None
        delivery._state.adding = True

        delivery.save()

        if delivery:
            data = {
                "order_id": delivery.id,
                "order_code": delivery.code,
                "url": reverse("core:delivery-detail", args=[pk], request=request),
            }
            return Response(data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for creating route settings and generating
    routes
    """

    queryset = RouteSettings.objects.all()
    serializer_class = RouteSettingsSerializer


# def update(self, request, *args, **kwargs):
#    data = request.POST.getlist("data")
#     data = request.DATA
#     qs = Student_academic_program.objects.filter(student=2773951)
#     serializer = StudentAcademicProgramSerializer(qs, data=data, many=True)

#     if serializer.is_valid():
#         serializer.save()

#         return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])  # policy decorator
# data = request.POST.getlist("data")
# @renderer_classes([JSONRenderer])       # policy decorator
# def items_not_done(request):
#     user_count = Item.objects.filter(done=False).count()
#     content = {'not_done': user_count}

#     return Response(content)
