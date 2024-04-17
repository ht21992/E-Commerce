from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from core.views import frontpage, shop, signup, myaccount, edit_myaccount, get_products
from product.views import product

urlpatterns = [
    path("", frontpage, name="frontpage"),
    path("signup/", signup, name="signup"),
    path("logout/", LogoutView.as_view(template_name="frontpage.html"), name="logout"),
    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("myaccount/", myaccount, name="myaccount"),
    path("myaccount/edit/", edit_myaccount, name="edit_myaccount"),
    path("shop/", shop, name="shop"),
    path("shop/<slug:slug>/", product, name="product"),
    path("get_products/", get_products, name="get_products"),
]
