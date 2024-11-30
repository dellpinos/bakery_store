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
from datetime import datetime

# User's data validation
def validate_user(body):
    errors = []
    if len(body["first_name"]) < 3 or len(body["first_name"]) > 30 :
        errors.append('The First Name must be between 3 and 30 characters long.')

    if len(body["last_name"]) < 3 or len(body["last_name"]) > 30 :
        errors.append('The Last Name must be between 3 and 30 characters long.')

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, body["email"]):
        errors.append('Invalid email format.')

    # Verify that it is a valid username
    if not re.match("^[a-z0-9]*$", body["username"].lower()):
        errors.append('Invalid username format.')
    return errors

# Password format validation
def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain at least one number")

# Login view
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
                    "message": "Please activate your account via the email we sent",
                    "no_cat": True
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auth/login.html", {
                "message": "Invalid username and/or password",
                "no_cat": True
            })
    else:
        return render(request, "auth/login.html", {
            "no_cat": True
        })

# Logout
def logout_view(request):
    logout(request)
    
    return HttpResponseRedirect(reverse("index"))

# Register view
def register(request):
    if request.method == "POST":
        
        # Validates email, username, first_name and last_name
        errors = validate_user(request.POST)

        if len(errors) != 0:
            return render(request, "auth/register.html", {
                "errors": errors,
                "body": request.POST,
                "no_cat": True
            })

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        email = request.POST["email"].lower()
        username = request.POST["username"].lower()
        first_name = request.POST["first_name"].lower()
        last_name = request.POST["last_name"].lower()

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match.",
                "body": request.POST,
                "no_cat": True
            })

        try:
            # Custom password validator
            validate_password(password)
        except ValueError as e:
            return render(request, "auth/register.html", {
                "message": str(e),
                "body": request.POST,
                "no_cat": True
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()

        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "Username already taken.",
                "body": request.POST,
                "no_cat": True
            })
        
        # Send confirmation email
        mail_subject = 'Activate your account'
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        message = render_to_string('emails/activation_email.html', {
            'app_url': config('APP_URL'),
            'app_name': config('APP_NAME'),
            'current_year': datetime.now().year,
            'uid': uid,
            'token': token,
        })

        send_mail(
            mail_subject,
            '',
            config('APP_EMAIL'), 
            [email],
            html_message=message
        )

        return render(request, "auth/message.html", {
            "title": "Email Confirm",
            "content": "We have sent an email to your inbox. Please check it to proceed",
            "no_cat": True
        })

    else:
        return render(request, "auth/register.html", {
            "no_cat": True
        })
    

# Handles user redirection and token validation after email confirmation
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
            "content": "Your email has been successfully verified. Please continue to home page",
            "no_cat": True
        })
    else:
        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "Activation link is invalid!",
            "no_cat": True
        })
    
# Handles the password reset request form and email submission validation
def forgot_password(request):

    if request.method == "POST":
        user = User.objects.filter(email = request.POST['email'], is_active = True).first()

        if not user:
            return render(request, "auth/message.html", {
                "title": "Invalid Email",
                "content": "Email address is invalid",
                "no_cat": True
            })


        # Send confirmation email
        mail_subject = 'Reset your password'
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        message = render_to_string('emails/forgot_password_email.html', {
            'app_url': config('APP_URL'),
            'app_name': config('APP_NAME'),
            'current_year': datetime.now().year,
            'uid': uid,
            'token': token,
            'user': user
        })

        send_mail(
            mail_subject,
            '',
            config('APP_EMAIL'), 
            [user.email],
            html_message=message
        )


        return render(request, "auth/message.html", {
            "title": "Email Confirm",
            "content": "We have sent an email to your inbox. Please check it to proceed",
            "no_cat": True
        })
    
    else:
        return render(request, "auth/forgot_password.html", {
            "no_cat": True
        })

# Handles user redirection and token validation after email confirmation
def password_verify_email(request, uidb64, token):

    logout(request)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        # Sends the token to the view
        return render(request, "auth/reset_password.html", {
        "no_cat": True,
        "uidb64": uidb64,
        "token": token
    })
    
    else:
        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "The reset password link is invalid or has expired",
            "no_cat": True
        })
    
# Handles the form for setting a new password, including validation and saving the new password
def reset_password(request):

    if request.method == "POST":

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        email = request.POST["email"]
        uidb64 = request.POST["uidb64"]
        token = request.POST["token"]

        if password != confirmation:
            return render(request, "auth/reset_password.html", {
                "message": "Passwords must match",
                "no_cat": True,
                "uidb64": uidb64,
                "token": token
            })

        try:
            # Custom password validator
            validate_password(password)
        except ValueError as e:
            return render(request, "auth/reset_password.html", {
                "message": str(e),
                "no_cat": True,
                "uidb64": uidb64,
                "token": token
            })

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user.email != email:
            return render(request, "auth/reset_password.html", {
                "message": "The email address does not match",
                "no_cat": True,
                "uidb64": uidb64,
                "token": token
            })

        if user is not None and default_token_generator.check_token(user, token):
            # Attempt to save new password

            try:
                user = User.objects.filter(email = email).first()
                user.set_password(password)
                user.save()

            except IntegrityError:
                return render(request, "auth/message.html", {
                    "title": "Invalid Token",
                    "content": "The reset password link is invalid or has expired",
                    "no_cat": True
                })

            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        return render(request, "auth/message.html", {
            "title": "Invalid Token",
            "content": "The reset password link is invalid or has expired",
            "no_cat": True
        })
    else:
        return login_view(request)


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