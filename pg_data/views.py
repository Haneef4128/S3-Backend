from rest_framework.generics import ListAPIView
from .models import  Room, Tenant, Expense, TenantForm, Rent
from rest_framework import status
from .serializers import RoomSerializer, TenantSerializer, ExpenseSerializer, RentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import TenantFormResponseSerializer
from django.utils.timezone import now
import datetime
from django.db.models import Sum
import re
from django.db import transaction
from decimal import Decimal
from datetime import date
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST', 'GET'])
@permission_classes([AllowAny]) 
def submit_tenant_form(request):
    if request.method == 'POST':
        print("Received data:", request.data)
        serializer = TenantFormResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Form submitted successfully!"}, status=201)
        return Response(serializer.errors, status=400)
    elif request.method == 'GET':
        issues = TenantForm.objects.all()
        serializer = TenantFormResponseSerializer(issues, many=True)
        return Response(serializer.data, status=200)


class RoomListView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


@api_view(['GET', 'POST'])
def tenant_list(request):
    if request.method == 'GET':
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            room_no = request.data.get("room_no")

            try:
                room = Room.objects.get(room_no=room_no)

                tenant = serializer.save()  # 🔹 Saves automatically, don't save again

                if tenant.status == "Occupied":
                    room.occupied_count += 1
                elif tenant.status == "Booked":
                    room.booked += 1

                room.vacant = room.total_beds - (room.occupied_count + room.booked)
                room.save()

            except Room.DoesNotExist:
                return Response({"error": "Room not found"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET', 'PUT', 'DELETE'])
# def tenant_detail(request, tenant_id):
#     """Handles retrieving, updating, and deleting a specific tenant."""
#     try:
#         tenant = Tenant.objects.get(id=tenant_id)
#     except Tenant.DoesNotExist:
#         return Response({"error": "Tenant not found"}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':  # ✅ Fetch tenant details
#         serializer = TenantSerializer(tenant)
#         return Response(serializer.data)

#     elif request.method == 'PUT':  # ✅ Update tenant details
#         old_status = tenant.status  # Store the previous status
#         serializer = TenantSerializer(tenant, data=request.data)

#         if serializer.is_valid():
#             updated_tenant = serializer.save()  # Save updated tenant

#             # If status has changed, update room counts
#             new_status = updated_tenant.status
#             if old_status != new_status:
#                 if old_status == "Occupied":
#                     room.occupied_count = max(0, room.occupied_count - 1)
#                 elif old_status == "Booked":
#                     room.booked = max(0, room.booked - 1)

#                 if new_status == "Occupied":
#                     room.occupied_count += 1
#                 elif new_status == "Booked":
#                     room.booked += 1

#                 # Recalculate vacant beds
#                 room.vacant = room.total_beds - (room.occupied_count + room.booked)
#                 room.save()

#             return Response(serializer.data)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     elif request.method == 'DELETE':  # ✅ Delete tenant and decrement count
#         room = tenant.room_no  # Get associated room

#         # Decrement the respective count
#         if tenant.status == "Occupied":
#             room.occupied_count = max(0, room.occupied_count - 1)
#         elif tenant.status == "Booked":
#             room.booked = max(0, room.booked - 1)

#         # Recalculate vacant beds
#         room.vacant = room.total_beds - (room.occupied_count + room.booked)
#         room.save()

#         tenant.delete()
#         return Response({"message": "Tenant deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT', 'DELETE'])
def tenant_detail(request, tenant_id):
    """Handles retrieving, updating, and deleting a specific tenant."""
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({"error": "Tenant not found"}, status=status.HTTP_404_NOT_FOUND)

    room = tenant.room_no  # ✅ Fetch the associated Room object

    if request.method == 'GET':  # ✅ Fetch tenant details
        serializer = TenantSerializer(tenant)
        return Response(serializer.data)

    elif request.method == 'PUT':  # ✅ Update tenant details
        old_status = tenant.status  # Store the previous status
        serializer = TenantSerializer(tenant, data=request.data)

        if serializer.is_valid():
            updated_tenant = serializer.save()  # Save updated tenant
            new_status = updated_tenant.status

            if old_status != new_status:
                # ✅ Decrease count from old status
                if old_status == "Occupied":
                    room.occupied_count = max(0, room.occupied_count - 1)
                elif old_status == "Booked":
                    room.booked = max(0, room.booked - 1)

                # ✅ Increase count for new status
                if new_status == "Occupied":
                    room.occupied_count += 1
                elif new_status == "Booked":
                    room.booked += 1

                # ✅ Recalculate vacant beds
                room.vacant = room.total_beds - (room.occupied_count + room.booked)
                room.save()  # ✅ Save the updated room data

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':  # ✅ Delete tenant and decrement count
        # Decrement the respective count
        if tenant.status == "Occupied":
            room.occupied_count = max(0, room.occupied_count - 1)
        elif tenant.status == "Booked":
            room.booked = max(0, room.booked - 1)

        # Recalculate vacant beds
        room.vacant = room.total_beds - (room.occupied_count + room.booked)
        room.save()

        tenant.delete()
        return Response({"message": "Tenant deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# class ExpenseListView(ListAPIView):
#     queryset = Expense.objects.all()
#     serializer_class = ExpenseSerializer

@api_view(['GET', 'POST'])
def expense_list(request):
    """Handles retrieving (GET) and creating (POST) expenses"""
    if request.method == 'GET':  # ✅ Fetch all expenses
        expenses = Expense.objects.all().order_by('-expense_date')  # Sort by latest
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        print("📩 Received Data:", request.data)  # ✅ Debugging

        serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("❌ Validation Errors:", serializer.errors)  # ✅ Debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def update_expense(request, expense_id):
    """Update or delete an existing expense"""
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':  # ✅ Update expense
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)  # ✅ Allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':  # ✅ Delete expense
        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class RentListView(ListAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer

@api_view(['GET'])
def expense_stats(request):
    today = now().date()

    # Get the first day of this month, last month, and two months back
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - datetime.timedelta(days=1)).replace(day=1)
    first_day_two_months_back = (first_day_last_month - datetime.timedelta(days=1)).replace(day=1)

    # Fetch total expenses for each month using Django ORM
    expenses = Expense.objects.filter(expense_date__gte=first_day_two_months_back) \
        .values('expense_date__year', 'expense_date__month') \
        .annotate(total=Sum('amount'))

    # Default expense values
    expense_data = {
        "twoMonthsBack": 0,
        "lastMonth": 0,
        "thisMonth": 0
    }

    # Assign expenses to corresponding months
    for entry in expenses:
        year, month, total = entry['expense_date__year'], entry['expense_date__month'], entry['total']
        if month == first_day_two_months_back.month and year == first_day_two_months_back.year:
            expense_data["twoMonthsBack"] = total
        elif month == first_day_last_month.month and year == first_day_last_month.year:
            expense_data["lastMonth"] = total
        elif month == first_day_this_month.month and year == first_day_this_month.year:
            expense_data["thisMonth"] = total

    return Response(expense_data)

@api_view(['GET'])
def room_occupancy(request):
    today = now().date()
    data = []

    # Get last 5 months data
    for i in range(5):
        month = today - datetime.timedelta(days=i*30)
        available_rooms = Room.objects.count()
        booked_rooms = Tenant.objects.filter(date_of_joining__month=month.month).count()

        data.append({
            "month": month.strftime("%b"),  # Convert to "Jan", "Feb", etc.
            "available": available_rooms,
            "booked": booked_rooms
        })

    return Response(data)

@api_view(['GET'])
def revenue_over_time(request):
    today = now().date()
    data = []

    # Get last 5 months revenue
    for i in range(5):
        month = today - datetime.timedelta(days=i*30)
        revenue = Expense.objects.filter(expense_date__month=month.month).aggregate(Sum('amount'))['amount__sum'] or 0

        data.append({
            "month": month.strftime("%b"),
            "revenue": revenue
        })

    return Response(data)

@api_view(['GET'])
def maintenance_status(request):
    not_resolved_count = TenantForm.objects.filter(status="Not Resolved").count()
    resolved_count = TenantForm.objects.filter(status="Resolved").count()

    data = [
        {"name": "Not Resolved", "value": not_resolved_count},
        {"name": "Resolved", "value": resolved_count},
    ]

    return Response(data)

@api_view(['DELETE'])
def delete_request(request, issue_id):
    print(f"🔍 DELETE Request received for issue_id: {issue_id}")  # ✅ Log incoming request

    try:
        issue = TenantForm.objects.get(id=issue_id)
        issue.delete()
        print(f"✅ Issue {issue_id} deleted successfully!")  # ✅ Log success
        return Response({"message": "Issue deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except TenantForm.DoesNotExist:
        print(f"⚠️ Issue {issue_id} not found in DB!")  # ✅ Log failure
        return Response({"error": "Issue not found"}, status=status.HTTP_404_NOT_FOUND)

TARIFFS = {
    "Non-AC": {1: 6000, 2: 5500, 4: 5000, 6: 4500, 8: 4000},
    "AC": {4: 6500}
}

@api_view(['GET'])
def rent_list(request):
    """Fetch all tenants with their rent payment status (including past dues)"""
    current_month = date.today().replace(day=1)

    # Fetch all unpaid rent records (including past months)
    unpaid_rents = Rent.objects.filter(is_paid=False).order_by('month')

    rent_data = []

    for rent in unpaid_rents:
        rent_data.append({
            "tenant_id": rent.tenant.id,
            "tenant_name": rent.tenant.name,
            "room_no": rent.tenant.room_no.room_no,
            "month": rent.month.strftime("%B %Y"),  # ✅ Show month like "March 2025"
            "due_amount": rent.due_amount,
            "paid_amount": rent.paid_amount,
            "total_rent": rent.total_rent,  # ✅ Include total_rent in response
            "is_paid": bool(rent.is_paid)
        })

    return Response(rent_data, status=status.HTTP_200_OK)

  


@api_view(['POST'])
def make_payment(request, tenant_id):
    """Update rent payment and mark as paid if fully covered"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    current_month = date.today().replace(day=1)
    rent = Rent.objects.get(tenant=tenant, month=current_month)

    paid_amount = Decimal(request.data.get("paid_amount", 0))  # ✅ Ensure decimal type
    rent.paid_amount += paid_amount  # ✅ Add new payment

    # If fully paid, mark as paid
    if rent.paid_amount >= rent.due_amount:
        rent.is_paid = True

    rent.save()

    return Response(RentSerializer(rent).data, status=status.HTTP_200_OK)
