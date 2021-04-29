from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import *
# Register your models here.

from PIL import Image

class ProductAdminForm(ModelForm):
    MIN_RES = (300,300)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Мин. размер картинки: {}x{}!'.format(*self.MIN_RES)

    def clean_image(self):
        
        image = self.cleaned_data['image']

        img = Image.open(image)
        print(img.width, img.height)
        if img.width<self.MIN_RES[0] or img.height<self.MIN_RES[1]:
            raise  ValidationError('Размер изображения меньше минимального!')

        return image

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Menu)
admin.site.register(Order)