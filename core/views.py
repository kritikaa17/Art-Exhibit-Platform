from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Count,Avg
from taggit.models import Tag
from core.models import Product, Category, Artist, CartOrder, CartOrderItems, ProductImages,ProductReview,Address,wishlist_model,Coupon
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.core import serializers
from userauths.models import Profile

import calendar
from django.db.models.functions import ExtractMonth

def index(request):
    products = Product.objects.filter(featured=True, products_status="published")
    context = {
        "products":products
    }

    return render(request,'core/index.html',context)

def product_list_view(request):
    products = Product.objects.filter(products_status="published")
    

    context = {
        "products":products,
       
    }
    return render(request,'core/product-list.html',context)

def category_list_view(request):

    categories = Category.objects.all()
    context = {
        "categories":categories
    }
    return render(request,'core/category-list.html',context)

def category_product_list_view(request,cid):
    category = Category.objects.get(cid = cid)
    products = Product.objects.filter(products_status="published", category=category)

    context = {
        "category":category,
        "products":products,
    }
    return render(request, "core/category-product-list.html",context)

def artist_list_view(request):
    artists = Artist.objects.all()
    context = {
        "artist": artists,
    }
    return render(request, "core/artist-list.html",context)

def artist_detail_view(request,aid):
    artist = Artist.objects.get(aid = aid)
    products = Product.objects.filter(artist=artist, products_status="published")
    context = {
        "artist": artist,
        "products": products,
    }
    return render(request, "core/artist-detail.html",context)  



@login_required

def product_detail_view(request,pid):
    product = Product.objects.get(pid=pid) 

    products= Product.objects.filter(category=product.category).exclude(pid=pid)

   

    address = Address.objects.filter(user=request.user)

    #getting all review
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    #getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    #product Review Form
    review_form = ProductReviewForm()

    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False

    p_image = product.p_images.all() 
    context = {
        "p": product,
        "p_image": p_image,
        "average_rating": average_rating,
        "reviews": reviews,
        "make_review": make_review,
        "review_form":review_form,
        "products": products,
        "address":address,
      
    }    
    return render(request,"core/product-detail.html",context)

def tag_list(request,tag_slug=None):
    products = Product.objects.filter(products_status="published").order_by("-id")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context={
        "products": products,
        "tag":tag,
    }    
    return render(request, "core/tag.html",context)

def ajax_add_review(request,pid):
    product = Product.objects.get(pid=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST['review'],
        rating=request.POST['rating'],
    )

    context = {
        'user':user.username,
        'review':request.POST['review'],
        'rating':request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
        'bool': True,
        'context': context,
        'average_reviews': average_reviews

        }
        
    )

def search_view(request):
    query = request.GET.get("q")


    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products":products,
        "query":query,

    }    
    return render(request, "core/search.html",context)


def filter_product(request):
    categories = request.GET.getlist('category[]')
    artists = request.GET.getlist('artist[]')
    tags = request.GET.getlist('tag[]')


    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(products_status="published").order_by("-id").distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(artists) > 0:
        products = products.filter(artist__id__in=artists).distinct()  

    if tags:
        products = products.filter(tags__id__in=tags).distinct()

   

    data = render_to_string("core/async/product-list.html",{"products":products})
    return JsonResponse({"data":data})



def add_to_cart(request):
    cart_product = {}
    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': int(request.GET['qty']),  
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],

    }

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']
        if str(request.GET['id']) in cart_data:
            
            cart_data[str(request.GET['id'])]['qty'] = int(request.GET['qty'])
        else:
            
            cart_data.update(cart_product)
    else:
        
        cart_data = cart_product

    
    request.session['cart_data_obj'] = cart_data

   
    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

@login_required         
def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html",{"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index") 



def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data 

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])    
    
    
    context = render_to_string("core/async/cart-list.html",{"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})

    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data 

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])    
    
    
    context = render_to_string("core/async/cart-list.html",{"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})

    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})



def save_checkout_info(request):
    cart_total_amount = 0
    total_amount = 0

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        request.session['full_name'] = full_name
        request.session['email'] = email
        request.session['mobile'] = mobile
        request.session['address'] = address
        request.session['city'] = city
        request.session['state'] = state
        request.session['country'] = country

        if 'cart_data_obj' in request.session:
            # Calculate total amount for PayPal payment
            for p_id, item in request.session['cart_data_obj'].items():
                total_amount += int(item['qty']) * float(item['price'])

            # Create Order Object
            order = CartOrder.objects.create(
                user=request.user,
                price=total_amount,
                full_name=full_name,
                email=email,
                phone=mobile,
                address=address,
                city=city,
                state=state,
                country=country
            )

            # Clear session variables
            del request.session['full_name']
            del request.session['email']
            del request.session['mobile']
            del request.session['address']
            del request.session['city']
            del request.session['state']
            del request.session['country']

            # Add cart items to CartOrderItems
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])

                cart_order_products = CartOrderItems.objects.create(
                    order=order,
                    invoice_no="INVOICE_NO" + str(order.id),
                    item=item['title'],
                    image=item['image'],
                    qty=item['qty'],
                    price=item['price'],
                    total=float(item['qty']) * float(item['price'])
                )

            # Redirect to checkout page with order id
            return redirect("core:checkout", order.oid)

    # If not a POST request or if 'cart_data_obj' not in session, redirect to checkout page without order id
    return redirect("core:checkout")
 
    


def checkout(request, oid):
    order = CartOrder.objects.get(oid=oid)
    order_items = CartOrderItems.objects.filter(order=order)

    if request.method == "POST":
        code = request.POST.get("code")
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request,"Coupon already activated")
                return redirect("core:checkout",order.oid)
            else:
                discount = order.price * coupon.discount / 100
                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()

                messages.success(request,"Coupon Activated")
                return redirect("core:checkout",order.oid)
        else:
            messages.warning(request,"Coupon does not exists.")
            return redirect("core:checkout",order.oid)


    context = {
        "order": order,
        "order_items": order_items,
    }

    return render(request, "core/checkout.html", context)


            

@login_required
def payment_completed_view(request,oid):
    order= CartOrder.objects.get(oid=oid)
    if order.paid_status == False:
        order.paid_status = True
        order.save()

    context={
        "order":order,
    }
    

    return render(request, 'core/payment-completed.html',context)
         


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')     

@login_required
def customer_dashboard(request):
    order_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)
    
    # Filter orders for the current user
    orders = CartOrder.objects.filter(user=request.user) \
                               .annotate(month=ExtractMonth("order_date")) \
                               .values("month") \
                               .annotate(count=Count("id")) \
                               .values("month", "count")
    
    month = []
    total_orders = []

    for i in orders:
        month.append(calendar.month_name[i['month']])
        total_orders.append(i["count"])

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        form_address = request.POST.get("address")
        form_mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=form_address,
            mobile=form_mobile,
        )

        messages.success(request, "Address added successfully.")

        return redirect("core:dashboard")

    context = {
        "profile": profile,
        "order_list": order_list,
        "month": month,
        "total_orders": total_orders,
        "address": address,
    }
    return render(request, 'core/dashboard.html', context)

def order_detail(request,id):
    order = CartOrder.objects.get(user=request.user,id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    context={
        "order_items":order_items
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


@login_required
def wishlist_view(request):
    wishlist = wishlist_model.objects.all()    
    context ={
        "w":wishlist,
    }
    return render(request, "core/wishlist.html", context)

@login_required
def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id= product_id)

    context = {

    }
    wishlist_count = wishlist_model.objects.filter(product=product,user=request.user).count()
    print(wishlist_count)

    if wishlist_count > 0:
        context = {
            "bool":True
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            product=product,
            user=request.user,
        )

        context={
            "bool":True

        }    

    return JsonResponse(context)

def remove_wishlist(request):
    pid = request.GET['id']
    wishlist = wishlist_model.objects.filter(user=request.user)
    wishlist_d= wishlist_model.objects.get(id=pid)
    delete_product = wishlist_d.delete()

    

    context = {
        "bool": True,
        "w": wishlist,
    }
    wishlist_json = serializers.serialize('json', wishlist)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data": data, "wishlist": wishlist_json})

