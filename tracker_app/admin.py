from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import Expense, Salary, FixedExpense, Routine, FuturePlan
from django.contrib.admin import AdminSite

# Custom form for User admin to handle password changes
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'] = forms.CharField(widget=forms.PasswordInput(), required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

# Custom User admin to manage users
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

# Admin for Expense model
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'date', 'borrowed')
    list_filter = ('user', 'payment_method', 'borrowed', 'date')
    search_fields = ('description', 'payment_method')
    date_hierarchy = 'date'

# Admin for Salary model
@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'date')
    list_filter = ('user', 'date')
    search_fields = ('user__username',)
    date_hierarchy = 'date'

# Admin for FixedExpense model
@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'due_date')
    list_filter = ('user', 'due_date')
    search_fields = ('description',)
    date_hierarchy = 'due_date'

# Admin for Routine model
@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'start_time', 'end_time', 'date')
    list_filter = ('user', 'date')
    search_fields = ('activity', 'notes')
    date_hierarchy = 'date'

# Admin for FuturePlan model
@admin.register(FuturePlan)
class FuturePlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'target_date', 'priority', 'status', 'email_reminder')
    list_filter = ('user', 'priority', 'status', 'email_reminder', 'target_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'target_date'

# Create a custom admin site
class CustomAdminSite(AdminSite):
    site_header = 'Administration'  # Customize the header
    site_title = 'Admin Panel'  # Customize the title
    index_title = 'Welcome to the Admin Panel'  # Customize the index page title
    
    # Override the Media class to add custom CSS
    class Media:
        css = {
            'all': ('css/custom_admin.css', 'css/expense.css', 'css/future_plan.css', 'css/routine.css')
        }
        js = ('js/admin_custom.js',)

# Instantiate the custom admin site
admin_site = CustomAdminSite(name='custom_admin')

# Unregister the User model from the default admin site
admin.site.unregister(User)

# Register the User model with the custom admin site
admin_site.register(User, UserAdmin)

# Register other models with the custom admin site
admin_site.register(Expense, ExpenseAdmin)
admin_site.register(Salary, SalaryAdmin)
admin_site.register(FixedExpense, FixedExpenseAdmin)
admin_site.register(Routine, RoutineAdmin)
admin_site.register(FuturePlan, FuturePlanAdmin)