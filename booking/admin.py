from django.contrib import admin
from .models import Country, BookingSource, HousekeepingStatus, AccountType, Charges, BookingInfor, TranInfor, RentalInfor, PaymentMethod, PaymentTranInfor, StayInfor, Promo

admin.site.register(Country)
admin.site.register(HousekeepingStatus)
admin.site.register(BookingSource)
admin.site.register(AccountType)
admin.site.register(Charges)
admin.site.register(Promo)
admin.site.register(PaymentMethod)
admin.site.register(PaymentTranInfor)
admin.site.register(StayInfor)

@admin.register(BookingInfor)
class BookingInforAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'arrival_date', 'payment_for_total', 'is_cityledger']
    search_fields = ['first_name', 'last_name']
    list_filter = ['arrival_date']

@admin.register(TranInfor)
class TranInforAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_id', 'room_id']

@admin.register(RentalInfor)
class RentalInforAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_id', 'old_hk_status', 'new_hk_status']
    list_filter = ['new_hk_status', 'rental_date']

