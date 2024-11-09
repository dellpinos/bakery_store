from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import re
from users.models import User, Notification

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auth/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auth/login.html", {
            "no_cat": True
        })


def logout_view(request):
    logout(request)
    
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        
        username = request.POST["username"].lower()
        # Verify that it is a valid username
        if not re.match("^[a-z0-9]*$", username):
            return render(request, "auth/register.html", {
                "message": "Username must contain only letters and numbers."
            })
        
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auth/register.html", {
            "no_cat": True
        })

## API ##

# Get user's notifications
@login_required
def get_notifications(request):

    notifications = request.user.notifications.order_by("-created_at")
    counter = request.user.notifications.filter(is_read = False).count()

    if not notifications:
        return JsonResponse({
            "msg" : "There is no notifications",
            "notifications": [],
            "response" : 0
            }, status = 200
        )

    serialized_notifications = []

    for notification in notifications:
        serialized_notifications.append(notification.serialize())

    return JsonResponse({
        "response": counter,
        "notifications": serialized_notifications
    })

# Deletes notification
@login_required
def delete_notification(request, id):

    notif = Notification.objects.filter(pk = id, user = request.user).first()

    if not notif:
        return JsonResponse({
            "msg" : "Something was wrong"
            }, status = 404
        )

    notif.delete()

    return JsonResponse({
        "msg" : "Notification deleted"
        }, status = 200
    )

# Marks a notification as read
@login_required
def mark_read_notification(request, id):

    notif = Notification.objects.filter(pk = id, user = request.user).first()

    if not notif:
        return JsonResponse({
            "msg" : "Something was wrong"
            }, status = 404
        )
    
    notif.is_read = True
    notif.save()

    return JsonResponse({
        "msg" : "Notification marked as read"
        }, status = 200
    )