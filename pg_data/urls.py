from django.urls import path
from .views import tenant_list, RoomListView, expense_list, submit_tenant_form, RentListView, rent_list, make_payment, delete_request, update_expense, expense_stats, room_occupancy, revenue_over_time, maintenance_status, tenant_detail

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="room-list"),
    path("tenants/", tenant_list, name="tenant-list"),
    path("expenses/", expense_list, name="expense-list"),
    path("expenses/<int:expense_id>/", update_expense, name="expense-detail"),
    path('tenants/<int:tenant_id>/', tenant_detail, name='tenant-detail'),
    path('submit-form/', submit_tenant_form),
    path("rent/", RentListView.as_view(), name="rent-list"),
    path('expense-stats/', expense_stats, name='expense_stats'),
    path('room-occupancy/', room_occupancy, name='room_occupancy'),
    path('revenue-over-time/', revenue_over_time, name='revenue_over_time'),
    path('maintenance-status/', maintenance_status, name='maintenance_status'),
    path('delete_request/<int:issue_id>/', delete_request, name='delete_request'),
    path('rents/', rent_list, name="rent-list"),
    path('rents/<int:tenant_id>/', make_payment, name="update-rent"),
    # path('rents/delete/<int:rent_id>/', delete_rent, name="delete-rent")
]
