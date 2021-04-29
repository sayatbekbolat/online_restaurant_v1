from django.shortcuts import render
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect

from django.db.models import Count
from django.db import transaction

from django.contrib.contenttypes.models import ContentType   
from django.contrib import messages  

from .models import Product, Category, Customer, Cart, CartProduct
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm
from .utils import recalc_cart


class BaseView(CartMixin, View):
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_category_count()
        products = Product.objects.get_latest_products()[:6]
        context = {
            'categories':categories,
            'products' : products,
            'cart':self.cart
        }
        return render(request, 'base.html', context)



class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    
    def dispatch(self, request, *args, **kwargs):
        self.model = Product
        self.ct_name = kwargs['ct_model']
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)
    
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self,**kwargs):
        context =super().get_context_data(**kwargs)
        context['ct_model'] = self.ct_name
        context['cart'] = self.cart
        return context 
    

class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg  = 'slug'

    def get_context_data(self,**kwargs):
        context =super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context 

class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_category_count()
        # print(cart.content_object.title)
        # print(cart.product.all()[0].content_object.title)
        context = {
            'cart':self.cart,
            'categories':categories
        }
        return render(request, 'cart.html', context)


class AddToCartView(CartMixin, View):
    
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model='product')
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
                user = self.cart.owner,
                cart = self.cart,
                content_type = content_type,
                object_id = product.id,
                final_price = product.price
        )
        if not created:
            cart_product.qty += 1
            cart_product.save()

        if created: 
            self.cart.product.add(cart_product)
        

        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")  
        return HttpResponseRedirect('/cart/')


class DeleteCartView(CartMixin, View):
    
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model='product')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
                user = self.cart.owner,
                cart = self.cart,
                content_type = content_type,
                object_id = product.id,
                final_price = product.price
        )
        self.cart.product.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs): 
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model='product')
        product = Product.objects.get(slug=product_slug)

        cart_product = CartProduct.objects.get(
                user = self.cart.owner,
                cart = self.cart,
                content_type = content_type,
                object_id = product.id,
                final_price = product.price
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect('/cart/')
        


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_category_count()
        form = OrderForm(request.POST or None)

        context = {
            'cart':self.cart,
            'categories':categories,
            'form':form,
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartView, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.address = form.cleaned_data['address']
            new_order.phone = form.cleaned_data['phone']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')
            


            