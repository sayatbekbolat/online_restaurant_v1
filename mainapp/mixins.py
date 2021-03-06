from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View

from .models import Category, Customer, CartProduct, Cart, Product


class CategoryDetailMixin(SingleObjectMixin):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if isinstance(self.get_object(), Category):
            category_slug = self.get_object().slug
            category = Category.objects.filter(slug=category_slug)
            context['category_products'] = Product.objects.filter(category=category[0])
        
        context['categories'] = Category.objects.get_category_count()
        return context
    


class CartMixin(View):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            
            if not customer:
                customer = Customer.objects.create(
                    user = request.user
                )

            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(
                    owner = customer
                )
        else:
            cart = Cart.objects.filter(for_anonymous_user=True)
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        
        self.cart = cart

        return super().dispatch(request, *args, **kwargs)