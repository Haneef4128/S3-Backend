from django.db import models
from datetime import date

class Room(models.Model):
    # FLOOR_CHOICES = [(2, '2nd Floor'), (3, '3rd Floor')]
    # ROOM_TYPE_CHOICES = [('AC', 'AC'), ('Non-AC', 'Non-AC')]

    id = models.AutoField(primary_key=True)
    floor = models.IntegerField()
    room_type = models.CharField(max_length=10)
    capacity = models.IntegerField()
    room_no = models.CharField(max_length=10, unique=True)
    total_beds = models.IntegerField()
    occupied_count = models.IntegerField(default=0)  # Auto-updated by PostgreSQL trigger
    booked = models.IntegerField(default=0)
    vacant = models.IntegerField(default=0) 

    class Meta:
        db_table = "rooms"

    def save(self, *args, **kwargs):
        print(f"🛑 save() called - Room {self.room_no}: Occupied: {self.occupied_count}, Booked: {self.booked}")
        self.vacant = self.total_beds - (self.occupied_count + self.booked)
        super().save(*args, **kwargs)




    def __str__(self):
        return f"Room {self.room_no} ({self.room_type}, Floor {self.floor})"


class Tenant(models.Model):
    # STATUS_CHOICES = [('Occupied', 'Occupied'), ('Vacated', 'Vacated')]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    room_no = models.ForeignKey(Room, to_field="room_no", db_column="room_no", on_delete=models.CASCADE, related_name="tenants")  # ✅ Explicit related_name
    date_of_joining = models.DateField()
    status = models.CharField(max_length=10, default='Occupied')
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "tenants"

    def __str__(self):
        return f"{self.name} ({self.room_no.room_no})"

class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    expense = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(auto_now_add=True)
    expense_type = models.CharField(max_length=20)

    class Meta:
        db_table = "expenses"
    
class TenantForm(models.Model):
    tenant_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    room_no = models.CharField(max_length=20)
    issue = models.TextField()
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Not Resolved")
    attachment = models.URLField(null=True, blank=True)  # Store image URL

    class Meta:
        db_table = "issues"

    def __str__(self):
        return f"{self.tenant_name} - {self.issue}"
    
# class Rent(models.Model):
#     tenant_name = models.CharField(max_length=255)
#     room_no = models.CharField(max_length=20)
#     due_amt = models.IntegerField()
#     paid_amt = models.IntegerField()
#     status = models.CharField(max_length=20, default="Pending")

#     class Meta:
#         db_table = "rent"

class Rent(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payments")
    month = models.DateField(default=date.today)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False) 
    total_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    class Meta:
        db_table = "rent"

    def __str__(self):
        status = "Paid" if self.is_paid else "Due"
        return f"{self.tenant.name} - {self.month.strftime('%B %Y')} - {status}"