from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"), #listing id comes from the ahref we made for when user clicks it
    path("watchlist", views.watchlist , name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category_listings/<str:category_name>", views.category_listings , name="category_listings")
    ]
