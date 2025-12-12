from django.contrib import admin
from django.utils.html import format_html
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number',
        'room_type',
        'price_per_night',
        'is_available',
        'preview_image',
        'short_description',
    )
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number', 'room_type', 'facilities')
    readonly_fields = ('preview_image',)

    fieldsets = (
        ("Basic Info", {
            'fields': ('room_number', 'room_type', 'price_per_night', 'is_available')
        }),
        ("Descriptions", {
            'fields': ('short_description', 'detailed_description')
        }),
        ("Facilities", {
            'fields': ('facilities',)
        }),
        ("Images", {
            'fields': ('main_image', 'preview_image', 'image_2', 'image_3', 'image_4')
        }),
    )

    def preview_image(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit:cover;" />', obj.main_image.url)
        return "No Image"
    preview_image.short_description = "Main Image"


from .models import Room, Booking

admin.site.register(Booking)