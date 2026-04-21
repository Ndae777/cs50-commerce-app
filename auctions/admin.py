from django.contrib import admin
from  .models import Auction_listing, Bid, Comment, WatchList, User
# Register your models here.

admin.site.register(Auction_listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(WatchList)
admin.site.register(User)