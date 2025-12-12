from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Room(models.Model):
    ROOM_TYPES = [
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
        ("deluxe", "Deluxe"),
    ]

    room_number        = models.CharField(max_length=10, unique=True)
    room_type          = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night    = models.DecimalField(max_digits=7, decimal_places=2)
    is_available       = models.BooleanField(default=True)

    # Images
    main_image         = models.ImageField(upload_to='room_main/', blank=True, null=True)
    image_2            = models.ImageField(upload_to='room_extra/', blank=True, null=True)
    image_3            = models.ImageField(upload_to='room_extra/', blank=True, null=True)
    image_4            = models.ImageField(upload_to='room_extra/', blank=True, null=True)

    # Descriptions and features
    short_description  = models.TextField(max_length=300, blank=True, help_text="Enter a short description of the room")
    detailed_description = models.TextField(blank=True, help_text="Provide more information about the room")
    facilities         = models.TextField(blank=True, help_text="Comma-separated list of room facilities")

    # Timestamp
    created_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"


from django.utils import timezone



from django.db import models
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=100, default="Guest")  # Default value added
    contact = models.CharField(max_length=15, default="0000000000")  # Default value added
    check_in = models.DateField(default=timezone.now)  # Default value added
    check_out = models.DateField(default=timezone.now)  # Default value added

    amount = models.PositiveIntegerField(
        help_text="Amount in paisa (₹ × 100)", default=0
    )  # Default value added

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.id} – Room {self.room.room_number}"
