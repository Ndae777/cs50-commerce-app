from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Auction_listing(models.Model):
    item_name = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="selling")
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="bid_winner")

    def __str__(self):
        return f"{self.owner} is selling {self.item_name} starting at ${self.start_bid}."

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="biddings")
    item = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.IntegerField()

    def __str__(self):
        return f"Bid ({self.id}) from {self.bidder.username} is: ${self.bid_amount}"

class Comment(models.Model):
    item = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="comments")
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_made")
    comment = models.TextField()

    def __str__(self):
        return f"Comment ({self.id}) from {self.commentor.username} is : \n{self.comment}"
    
class WatchList(models.Model):
    watchlist_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_items")
    item = models.ForeignKey(Auction_listing,on_delete=models.CASCADE,related_name="watchlist_by" )

    def __str__(self):
        return f"Watchlist [{self.id}] : belongs to owner_{self.watchlist_owner} for Auction({self.item})"