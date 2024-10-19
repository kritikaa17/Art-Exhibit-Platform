from django.urls import path,include
from core.views import index, product_list_view, category_list_view,category_product_list_view,artist_list_view,artist_detail_view,product_detail_view,tag_list,ajax_add_review,search_view,filter_product,add_to_cart,cart_view,delete_item_from_cart,update_cart,checkout,payment_completed_view,payment_failed_view,customer_dashboard,order_detail,make_address_default,wishlist_view,add_to_wishlist,remove_wishlist,save_checkout_info




app_name = "core"

urlpatterns = [
    #Home
    path("", index, name="index"),
    path("products/", product_list_view, name= "product-list"),
    path("product/<pid>/", product_detail_view, name= "product-detail"),

    #Category
    path("category/", category_list_view, name= "category-list"),
    path("category/<cid>/", category_product_list_view, name= "category-product-list"),

    #Artist
    path("artists/", artist_list_view, name= "artist-list"),
    path("artist/<aid>", artist_detail_view, name= "artist-detail"),

    #Tags
    path("products/tag/<tag_slug>/", tag_list, name="tags"),

    #Reviews
    path("ajax-add-review/<pid>/",ajax_add_review,name ="ajax-add-review"),

    #Search
    path("search/",search_view,name="search"),

    #Filter
    path("filter-products/",filter_product,name="filter-product"),

    #addtocart
    path("add-to-cart/",add_to_cart,name="add-to-cart"),

    #Cart page 
    path("cart/",cart_view,name="cart"),


    #Delete Item from cart
    path("delete-from-cart/",delete_item_from_cart,name="delete-from-cart"),

    #Update Item from cart
    path("update-cart/",update_cart,name="update-cart"),

    #Checkout
    path("checkout/<oid>/",checkout,name="checkout"),

    #Paypal 
    path("paypal/",include("paypal.standard.ipn.urls")),

    #Payment Successful
    path("payment-completed/<oid>/",payment_completed_view,name="payment-completed"),

    #Payment Failed
    path("payment-failed/",payment_failed_view,name="payment-failed"),

    #dashboard
    path("dashboard/",customer_dashboard,name="dashboard"),

    #OrderDetail Url
    path("dashboard/order/<int:id>",order_detail,name="order-detail"),

    #make address default
    path("make-default-address/",make_address_default,name="make-default-address"),

    #wishlist page
    path("wishlist/",wishlist_view,name="wishlist"),

    #add to wishlist
    path("add-to-wishlist/",add_to_wishlist,name="add-to-wishlist"),

    #removing from wishlist
    path("remove-from-wishlist/",remove_wishlist,name="remove-from-wishlist"),

    

    path("save_checkout_info/",save_checkout_info, name="save_checkout_info")

]