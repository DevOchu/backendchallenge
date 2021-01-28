from django.urls import path,include
from .import views 
from .views import OrderListCreateAPIView


app_name = 'core'
urlpatterns = [
    path('customer', views.Customer_Create.as_view(), name='customer'),
    path('order', OrderListCreateAPIView.as_view(), name="order"),
   
]

