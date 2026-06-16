from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use_view, name='terms_of_use'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
]
