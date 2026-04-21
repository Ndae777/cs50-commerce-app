from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction_listing, Bid, Comment , WatchList
from django.contrib.auth.decorators import login_required

class CreateListing(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.IntegerField()
    image_url = forms.URLField(required=False) #making it optional 
    category = forms.CharField(max_length=64)
    active = forms.BooleanField(required=False) #helps for form to start as false

class Comment_on_page(forms.Form):
    comment = forms.CharField(required=False) #will use this for comment logic 

def index(request):
    auction_listing = Auction_listing.objects.all() #auction listing table 
    return render(request, "auctions/index.html", {
        "Auction_listings" : auction_listing, 
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):

    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
           auction_listing = Auction_listing(
                item_name = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                start_bid = form.cleaned_data["starting_bid"],
                owner = request.user , 
                image_url = form.cleaned_data["image_url"],
                category = form.cleaned_data["category"],
                active = form.cleaned_data["active"]
            )
           
           auction_listing.save()
           return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/create_listing.html", {
        "form" : CreateListing(),
    })
    
@login_required
def listing_page(request, listing_id):

    auction_listing = Auction_listing.objects.get(id=listing_id)
    all_comments = Comment.objects.filter(item = auction_listing)
    
    watchlist_present = WatchList.objects.filter(
        watchlist_owner = request.user, 
        item = auction_listing
        ).exists() # returns true if the item and owner already in watchlist else false
    
    response_message  = "" #  message to display for user feedback. 
    close_ownership = False  # bool to see if there's ownership to closing bid
    winner_present = False # bool to check if this is the winner    
    
    #close logic
    if request.user == auction_listing.owner:
        close_ownership = True

    if request.user == auction_listing.winner:
        winner_present = True 
    
    if request.method == "POST":
        if "watchlist_act" in request.POST:
            if request.POST["watchlist_act"] == "Add to WatchList":
                watchlist_to_save = WatchList(
                    watchlist_owner = request.user,
                    item = auction_listing,
                )

                watchlist_to_save.save()
                return HttpResponseRedirect(reverse('index'))

            elif request.POST["watchlist_act"] == "Remove from WatchList":
                watchlist_to_delete = WatchList.objects.get(
                    watchlist_owner= request.user,
                    item= auction_listing,
                )

                watchlist_to_delete.delete()
                return HttpResponseRedirect(reverse('index'))           
            
        if "Bid_submit" in request.POST:

        #dealing with bid logic 
            bid_amount = int(request.POST["bid"]) #fixed to convert it into a integer
            highest_bid = auction_listing.start_bid 
            bids_on_the_item = Bid.objects.filter(item=auction_listing)

            for all_bids in bids_on_the_item:
                if all_bids.bid_amount > highest_bid :
                    highest_bid = all_bids.bid_amount #highest bid saved here
                    

            if bid_amount > highest_bid:
                bid_saving = Bid(
                    bidder = request.user,
                    item = auction_listing,
                    bid_amount = bid_amount,
                )

                bid_saving.save()
                response_message = "Bid Successful."
            else:
                response_message  = f"Bid Unsuccessful, Bid a higher amount than the current ${highest_bid}.(Your Current Bid is low)"
        
        # dealing with close bid logic
        if "Close_bid" in request.POST:

            bid_on_item = Bid.objects.filter(item = auction_listing) #all bids on that item
            highest_bid = None #will store winner object
            highest_bid_amount = auction_listing.start_bid #initial highest amount of bid

            for bids in bid_on_item:
                if bids.bid_amount > highest_bid_amount:
                    highest_bid_amount = bids.bid_amount
                    highest_bid = bids

            if highest_bid is not None:
                auction_listing.winner = highest_bid.bidder

            auction_listing.active = False
            auction_listing.save()
        
        #Adding the ability to Reopen Bid
        if "Open_bid" in request.POST:
            auction_listing.active = True
            auction_listing.save()

        #dealing with comments on listing page
        if "Comment_submit" in request.POST:
            comment = Comment_on_page(request.POST)
            if comment.is_valid():
                comment_save = Comment(
                    item = auction_listing,
                    commentor = request.user,
                    comment = comment.cleaned_data["comment"]
                )

                comment_save.save()

        #finding highest bid logic , forgot about this until now
    current_price = auction_listing.start_bid #inital price but will be changed as highest bids update
    item_bids = Bid.objects.filter(item = auction_listing)
    for bids in item_bids:
        if bids.bid_amount > current_price:
            current_price = bids.bid_amount #current price will always be the highest bid
    
    return render(request, "auctions/listing_page.html", {
        "auction_listing" : auction_listing,
        "listing_id" : listing_id,
        "watchlist_present" : watchlist_present,
        "success_message" : response_message,
        "close_ownership": close_ownership,
        "winner_present" : winner_present,
        "form" : Comment_on_page(),
        "all_comments" : all_comments,
        "current_price" : current_price
    })

@login_required
def watchlist(request):
    user_watchlist = WatchList.objects.filter(watchlist_owner = request.user)
    return render (request, "auctions/watchlist.html", {
        "user_watchlist" : user_watchlist
    })

#dealing with category listings
def categories(request):
    auctions = Auction_listing.objects.all()
    unique_auctions = []
    for auction in auctions :
        if auction.category not in unique_auctions:
            unique_auctions.append(auction.category)

    return render (request, "auctions/categories.html",{
        "auctions" : auctions,
        "auctions_list" : unique_auctions,
    })

def category_listings(request , category_name ):
    listings = Auction_listing.objects.filter(category = category_name)
    return render (request, "auctions/category_listing.html",{
        "listings":listings
    })

