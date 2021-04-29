from django.db import models




def recalc_cart(cart):
    cart_data = cart.product.aggregate(models.Sum('final_price'))
    qty = cart.product.aggregate((models.Sum('qty')))
    print('asdasdasd', cart_data.get('final_price__sum'))

    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0 
    
    cart.total_products = int(qty['qty__sum'])
    cart.save()
