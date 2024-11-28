import re
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from users.models import User, Notification
from decouple import config # Environment Variables (.env) - Python Decouple
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain at least one number")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)

        # Check if authentication successful
        if user is not None:
            if not user.is_active:
                return render(request, "auth/login.html", {
                    "message": "Please activate your account via the email we sent"
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auth/login.html", {
                "message": "Invalid username and/or password"
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
                "message": "Username must contain only letters and numbers"
            })
        
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match."
            })

        try:
            # Custom password validator
            validate_password(password)
        except ValueError as e:
            return render(request, "auth/register.html", {
                "message": str(e)
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.is_active = False
            user.save()
        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "Username already taken."
            })
        
        # Send confirmation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        message = render_to_string('emails/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        send_mail(mail_subject, message, config('APP_EMAIL'), [email])

        return render(request, "auth/message.html", {
            "title": "Email Confirm",
            "content": "We have sent an email to your inbox. Please check it to proceed"
        })

    else:
        return render(request, "auth/register.html", {
            "no_cat": True
        })
    
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
    
        return render(request, "auth/message.html", {
            "title": "Email Verified",
            "content": "Your email has been successfully verified. Please continue to home page"
        })
    else:
        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "Activation link is invalid!"
        })
    

def forgot_password(request):

    if request.method == "POST":
        user = User.objects.filter(email = request.POST['email']).first()

        if not user:
            return render(request, "auth/message.html", {
                "title": "Invalid Email",
                "content": "Email address is invalid!"
            })

        # Send confirmation email
        current_site = get_current_site(request)
        mail_subject = 'Reset your password'
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        message = render_to_string('emails/forgot_password_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })
        send_mail(mail_subject, message, config('APP_EMAIL'), [user.email])

        return render(request, "auth/message.html", {
            "title": "Email Confirm",
            "content": "We have sent an email to your inbox. Please check it to proceed"
        })
    
    else:
        return render(request, "auth/forgot_password.html")




#####
def password_verify_email(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        login(request, user)

        return reset_password(request, user)
    
    else:
        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "Activation link is invalid!"
        })
    






def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
    
        return render(request, "auth/message.html", {
            "title": "Email Verified",
            "content": "Your email has been successfully verified. Please continue to home page"
        })
    else:
        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "Activation link is invalid!"
        })
    


        



# Request password 
def reset_password(request):

    if request.method == "POST":

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match."
            })

        try:
            # Custom password validator
            validate_password(password)
        except ValueError as e:
            return render(request, "auth/register.html", {
                "message": str(e)
            })

        # Attempt to create new user
        try:
            user = User.objects.filter(email = request.user.email).first()
            user.password = password
            user.save()
        except IntegrityError:
            return render(request, "auth/forgot_password.html", {
                "message": "Invalid password"
            })
    else:
        return render(request, "auth/forgot_password.html")


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