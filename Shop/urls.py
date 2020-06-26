from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="Shop Home"),
    path("Search/", views.search, name="Search Here"),
    path("products/<int:myid>", views.productview, name="Our Products"),
    path("Checkout/", views.checkout, name="Checkout"),
    path("Track_Order/", views.trackorder, name="Tracking Order"),
    path("About/", views.about, name="About Us"),
    path("Contact/", views.contact, name="Contact Us"),
    # path("Login/", views.login, name="Login"),
    # path("Cart/", views.cart, name="My Cart"),
    # path("Wishlist/", views.wishlist, name="Your wishlist")
]