#type: ignore
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Dashboard Columns
    # Adds 'is_customer' or other custom fields to the main list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

    # 2. Filters (PRD Section 14 Requirement)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # 3. Search (PRD Section 14 Requirement)
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # 4. Organizing Detail View
    # This ensures your custom fields (if any) appear in the edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('is_customer', 'is_admin')}), # Add your custom fields here
    )