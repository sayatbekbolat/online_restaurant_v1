from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.urls import reverse
from django.utils import timezone

from django.db.models import Count
from django.db import models

def get_product_url(obj, viewname, model_name):
    ct_model = obj.__class__.meta.model_name

    return reverse(viewname, kwargs={'ct_model':ct_model, 'slug':obj.slug})

User = get_user_model()


class Menu(models.Model):
 
    name = models.CharField(max_length=255, verbose_name='Версия меню')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class CategoryManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()

    def get_category_count(self):
        
        qs = self.get_queryset().annotate(Count('product'))
        data = [
            dict(
                name=q.name,
                url=q.get_absolute_url(),
                count=q.product__count) for q in qs
            
        ]
        return data


class Category(models.Model):
   
    name = models.CharField(max_length=255, verbose_name='Версия категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})
    

class LatestProducts(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset()

    def get_latest_products(self):
        qs = self.get_queryset()
        data = [
            dict(
                title = q.title,
                url = q.get_absolute_url(),
                price = q.price,
                slug = q.slug,
                category = q.category,
                description = q.description,
                image = q.image
            )for q in qs
        ]
        return data
    

class Product(models.Model):

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField( verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    parts = models.TextField(verbose_name='Ингредиенты')
    objects = LatestProducts()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        ct_model = self.category.slug
        return reverse('product_detail', kwargs={'ct_model':ct_model, 'slug':self.slug})

    def get_model_name(self):
        return self.category.slug
    
    def get_slug(self):
        return self.slug


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_carts')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, verbose_name='Общая цена', decimal_places=2)

    def __str__(self):
        return "Блюдо: {} (для корзины)".format(self.content_object.title)


    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.final_price
        print(self.final_price)
        super().save(*args, **kwargs)


class Cart(models.Model):
  
    owner = models.ForeignKey('Customer', verbose_name='Владелец', null=True, on_delete=models.CASCADE)
    product = models.ManyToManyField('CartProduct', blank=True, related_name='related_products')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, verbose_name='Общая цена', decimal_places=2)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

