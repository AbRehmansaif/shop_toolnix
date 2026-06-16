from django.urls import path
from . import views

urlpatterns = [
    path('cart/',                     views.cart_view,       name='cart'),
    path('cart/add/<slug:slug>/',     views.add_to_cart,     name='add_to_cart'),
    path('cart/remove/<slug:slug>/',  views.remove_from_cart,name='remove_from_cart'),
    path('cart/update/<slug:slug>/',  views.update_cart,     name='update_cart'),
    path('checkout/',                 views.checkout,        name='checkout'),
    path('order/<str:order_number>/success/', views.order_success, name='order_success'),
    path('track-order/',              views.order_tracking,  name='order_tracking'),
]
