
from django.urls import path, include
from .views import (
    ProductDetailView, 
    CategoryDetailView, 
    BaseView, 
    CartView, 
    AddToCartView,
    DeleteCartView,
    ChangeQTYView,
    CheckoutView,
    MakeOrderView,
)
urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('delete-from-cart/<str:ct_model>/<str:slug>/', DeleteCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    
    
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root.MEDIA_ROOT)