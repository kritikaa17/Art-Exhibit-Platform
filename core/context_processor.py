from core.models import Product, Category, Artist, CartOrder, CartOrderItems, ProductImages,ProductReview,Address,wishlist_model
from django.db.models import Min,Max
from django.contrib import messages



def default(request):
    categories = Category.objects.all()
    artists = Artist.objects.all()
    min_max_price = Product.objects.aggregate(Min("price"),Max("price"))

    try:
        wishlist = wishlist_model.objects.filter(user=request.user)
    except:
        messages.warning(request, "")
        wishlist = 0

    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None
        
    return {
        'categories':categories,
        'address':address,
        'wishlist':wishlist,
        'artists':artists,
        'min_max_price':min_max_price,
    }