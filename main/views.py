from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm , BookingForm
from .models import Room
import razorpay
from django.conf import settings
from .models import Booking
from io import BytesIO
from datetime import timedelta
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required  # optional
from weasyprint import HTML
# Create your views here.
def home(request):
    return render(request,'main/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')  # Replace with your desired page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # For now, just show a success message. You can extend this to send email or save data.
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact')

    return render(request, 'main/contact.html')


def about_view(request):
    return render(request, 'main/about.html')

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'main/room_list.html', {'rooms': rooms})
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    facilities_list = [f.strip() for f in room.facilities.split(',')] if room.facilities else []
    return render(request, 'main/room_detail.html', {
        'room': room,
        'facilities_list': facilities_list
    })


@login_required   
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            nights = (booking.check_out - booking.check_in).days or 1
            booking.amount = int(nights * room.price_per_night * 100)  

            # Create Razorpay order
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            order = client.order.create(
                {
                    "amount": booking.amount,
                    "currency": "INR",
                    "payment_capture": 1,
                }
            )
            booking.razorpay_order_id = order["id"]
            booking.save()

            context = {
                "booking": booking,
                "room": room,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            }
            return render(request, "main/checkout.html", context)
    else:
        form = BookingForm()

    return render(
        request,
        "main/booking_form.html",
        {"form": form, "room": room},
    )


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST
        try:
            booking = Booking.objects.get(razorpay_order_id=data.get("razorpay_order_id"))
            booking.razorpay_payment_id = data.get("razorpay_payment_id")
            booking.razorpay_signature = data.get("razorpay_signature")

            # Verify signature
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            params_dict = {
                "razorpay_order_id": booking.razorpay_order_id,
                "razorpay_payment_id": booking.razorpay_payment_id,
                "razorpay_signature": booking.razorpay_signature,
            }
            client.utility.verify_payment_signature(params_dict)

            booking.status = "paid"
            booking.save()
            return render(request, "main/payment_success.html", {"booking": booking})
        except Exception:
            if "booking" in locals():
                booking.status = "failed"
                booking.save()
            return render(request, "main/payment_failed.html")
    return redirect("room_list")






@login_required            
def invoice_pdf(request, booking_id):
    try:
        booking = Booking.objects.select_related("room").get(pk=booking_id, status="paid")
    except Booking.DoesNotExist:
        raise Http404("No such paid booking")

    nights = (booking.check_out - booking.check_in).days or 1
    total_rupees = booking.amount // 100   # we stored paise

    html_string = render_to_string(
        "main/invoice.html",
        {
            "booking": booking,
            "nights": nights,
            "total_rupees": total_rupees,
        },
    )

    pdf_file = BytesIO()
    HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf(pdf_file)
    pdf_file.seek(0)

    filename = f"Invoice_{booking.id}.pdf"
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
