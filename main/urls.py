from django.urls import path
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('room_list/', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path("room/<int:room_id>/book/", views.book_room, name="room_book"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("invoice/<int:booking_id>/",views.invoice_pdf, name="invoice-pdf"),
]
