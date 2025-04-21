from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import Expense, Salary, FixedExpense, Routine, FuturePlan

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

# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

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