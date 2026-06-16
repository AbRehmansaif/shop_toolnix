from django.urls import path
from . import views

app_name = 'paymentsystem'

urlpatterns = [
    path('process/<str:order_number>/', views.payment_process, name='process'),
    path('success/<str:order_number>/', views.payment_success, name='success'),
    path('cancelled/<str:order_number>/', views.payment_cancelled, name='cancelled'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
