from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Expense, Routine, FuturePlan
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


# SignUp view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'signup.html')
        
        # Create a new user
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, 'Signup successful! You can now log in.')
        return redirect('login')
    
    return render(request, 'signup.html')

from django.db import transaction, DatabaseError

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                with transaction.atomic():
                    login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home')
            except DatabaseError as e:
                messages.error(request, 'Login failed due to a database error. Please try again.')
                print("Database Error:", e)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

# Home page after login
def home(request):
    return render(request, 'home.html')

# Logout view
@require_POST
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out.')
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from collections import defaultdict
from .models import Expense, Salary

def expense(request):
    if request.method == 'POST':
        # Handle expense addition
        amount = float(request.POST['amount'])  # Ensure amount is treated as a float
        description = request.POST['description']
        payment_method = request.POST['payment_method']
        date = request.POST['date']
        borrowed = request.POST.get('borrowed') == 'on'

        # Create a new expense entry
        Expense.objects.create(
            user=request.user,
            amount=amount,
            description=description,
            payment_method=payment_method,
            date=date,
            borrowed=borrowed
        )
        messages.success(request, 'Expense added successfully!')
        return redirect('expense')

    # Fetch expenses for the current user
    expenses = Expense.objects.filter(user=request.user).order_by('date')

    # Calculate total amount spent till date
    total_amount = sum(expense.amount for expense in expenses)

    # Current month and year
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Current month salary (only salaries added for the current month)
    current_month_salary = Salary.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Net worth calculation (current month salary minus total expenses)
    net_worth = current_month_salary - total_amount

    # Group expenses by "Month Year"
    expenses_by_month = defaultdict(list)
    for exp in expenses:
        key = exp.date.strftime('%B %Y')
        expenses_by_month[key].append(exp)

    # Create list of tuples (month, list_of_expenses, total, salary, remaining)
    totals_by_month = []
    for month_str, month_expenses in expenses_by_month.items():
        total = sum(exp.amount for exp in month_expenses)
        salary = Salary.objects.filter(
            user=request.user,
            date__month=now.month,
            date__year=now.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        remaining = salary - total
        totals_by_month.append((month_str, month_expenses, total, salary, remaining))

    # Sort by date (optional, if needed for descending order)
    totals_by_month.sort(key=lambda x: x[1][0].date, reverse=True)

    return render(request, 'expense.html', {
        'expenses': expenses,
        'total_amount': total_amount,
        'net_worth': net_worth,
        'totals_by_month': totals_by_month,
        'salaries': Salary.objects.filter(user=request.user)
    })

# For fetching expense data (AJAX)
def get_expense_data(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    data = {
        'id': expense.id,
        'amount': expense.amount,
        'description': expense.description,
        'payment_method': expense.payment_method,
        'date': expense.date.strftime('%Y-%m-%d'),
        'borrowed': expense.borrowed,
    }
    return JsonResponse(data)

# For updating expense via AJAX
# For updating expense via AJAX
def update_expense_ajax(request):
    if request.method == 'POST':
        expense_id = request.POST['id']
        expense = get_object_or_404(Expense, id=expense_id, user=request.user)
        expense.amount = request.POST['amount']
        expense.description = request.POST['description']
        expense.payment_method = request.POST['payment_method']
        expense.date = request.POST['date']
        expense.borrowed = 'borrowed' in request.POST
        expense.save()

        # Recalculate totals
        total_amount = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        current_month_salary = Salary.objects.filter(
            user=request.user,
            date__month=timezone.now().month,
            date__year=timezone.now().year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        net_worth = current_month_salary - total_amount

        return JsonResponse({'success': True, 'total_amount': total_amount, 'net_worth': net_worth})
    return JsonResponse({'success': False})

# For deleting expense
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expense')  # Redirect to the 

# New view to handle adding salaries
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone

def add_salary(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        date = request.POST['date']
        
        # Create a new salary entry
        Salary.objects.create(
            user=request.user,
            amount=amount,
            date=date
        )
        
        # Recalculate total amount spent and net worth
        total_amount = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        current_month_salary = Salary.objects.filter(
            user=request.user,
            date__month=timezone.now().month,
            date__year=timezone.now().year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        net_worth = current_month_salary - total_amount
        
        return JsonResponse({'success': True, 'net_worth': net_worth})
    
    return JsonResponse({'success': False})

# View to delete salary
def delete_salary(request, id):
    salary = get_object_or_404(Salary, id=id, user=request.user)
    salary.delete()
    messages.success(request, 'Salary deleted successfully!')
    return redirect('expense')

# View to fetch salary data for editing
def get_salary_data(request, id):
    salary = get_object_or_404(Salary, id=id, user=request.user)
    data = {
        'id': salary.id,
        'amount': salary.amount,
        'date': salary.date.strftime('%Y-%m-%d'),
    }
    return JsonResponse(data)

# View to update salary via AJAX
def update_salary_ajax(request):
    if request.method == 'POST':
        salary_id = request.POST['id']
        salary = get_object_or_404(Salary, id=salary_id , user=request.user)
        salary.amount = request.POST['amount']
        salary.date = request.POST['date']
        salary.save()
        messages.success(request, 'Salary updated successfully!')
        return redirect('expense')  # Redirect to the expense page
    return JsonResponse({'success': False})

# Edit expense view
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    
    if request.method == 'POST':
        # Update the expense
        expense.amount = request.POST['amount']
        expense.description = request.POST['description']
        expense.payment_method = request.POST['payment_method']
        expense.date = request.POST['date']
        expense.borrowed = request.POST.get('borrowed', False)
        expense.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('expense')  # Redirect to the expense page

    return render(request, 'edit_expense.html', {'expense': expense})


# Routine view
def routine(request):
    if request.method == 'POST':
        # Handle routine submission
        activity = request.POST['activity']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        notes = request.POST['notes']
        date = request.POST['date']
        
        # Create a new routine
        Routine.objects.create(
            user=request.user,
            activity=activity,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            date=date
        )
        messages.success(request, 'Routine added successfully!')
        return redirect('routine')  # Redirect to the same page or another page

    routines = Routine.objects.filter(user=request.user)
    return render(request, 'routine.html', {'routines': routines})

# Get routine data for editing (AJAX)
def get_routine(request, id):
    routine = get_object_or_404(Routine, id=id, user=request.user)
    data = {
        'id': routine.id,
        'activity': routine.activity,
        'start_time': routine.start_time,
        'end_time': routine.end_time,
        'notes': routine.notes,
        'date': routine.date.strftime('%Y-%m-%d'),
    }
    return JsonResponse(data)

# Delete routine entry
def delete_routine(request, id):
    routine = get_object_or_404(Routine, id=id, user=request.user)
    routine.delete()
    messages.success(request, 'Routine entry deleted successfully!')
    return redirect('routine')

# Future plans view
def send_future_plan_reminder(plan):
    subject = f"Reminder for Future Plan: {plan.title}"
    message = f"Dear {plan.user.username},\n\nThis is a reminder for your future plan: {plan.title}\nDescription: {plan.description}\nTarget Date: {plan.target_date}\nPriority: {plan.priority}\nStatus: {plan.status}\n\nPlease make sure to update your progress!"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [plan.user.email]

    send_mail(subject, message, email_from, recipient_list)

# Future plans view (with email reminder functionality)
from django.utils import timezone
from datetime import timedelta

def future_plans(request):
    if request.method == 'POST':
        # Handle future plans submission
        title = request.POST['title']
        description = request.POST['description']
        target_date = request.POST['target_date']
        priority = request.POST['priority']
        status = request.POST['status']
        
        # Convert email_reminder to boolean
        email_reminder = request.POST.get('email_reminder') == 'on'  # This will be True if checked, False otherwise
        
        # Create a new future plan
        plan = FuturePlan.objects.create(
            user=request.user,
            title=title,
            description=description,
            target_date=target_date,
            priority=priority,
            status=status,
            email_reminder=email_reminder
        )

        # If email reminder is enabled, set up the reminder
        if email_reminder:
            # Convert target_date to a timezone-aware datetime
            target_date_aware = timezone.make_aware(timezone.datetime.strptime(target_date, '%Y-%m-%d'))
            reminder_date = target_date_aware - timedelta(days=1)  # Reminder set for one day before the target date
            
            if reminder_date > timezone.now():
                # Schedule the email reminder to be sent the day before the target date
                send_future_plan_reminder(plan)
        
        messages.success(request, 'Future plan added successfully!')
        return redirect('future_plans')

    plans = FuturePlan.objects.filter(user=request.user)
    return render(request, 'future_plan.html', {'plans': plans})

def get_future_plan(request, id):
    plan = FuturePlan.objects.get(id=id, user=request.user)
    data = {
        'id': plan.id,
        'title': plan.title,
        'description': plan.description,
        'target_date': plan.target_date,
        'priority': plan.priority,
        'status': plan.status,
        'email_reminder': plan.email_reminder,
    }
    return JsonResponse(data)
def update_future_plan(request):
    if request.method == 'POST':
        plan_id = request.POST['id']
        plan = FuturePlan.objects.get(id=plan_id, user=request.user)

        plan.title = request.POST['title']
        plan.description = request.POST['description']
        plan.target_date = request.POST['target_date']
        plan.priority = request.POST['priority']
        plan.status = request.POST['status']
        plan.email_reminder = 'email_reminder' in request.POST
        
        plan.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def delete_future_plan(request, id):
    plan = get_object_or_404(FuturePlan, id=id, user=request.user)
    plan.delete()
    messages.success(request, 'Future plan deleted successfully!')
    return redirect('future_plans')

from django.shortcuts import render
from .models import Expense, Salary, FixedExpense
from django.db.models import Sum

def analytics(request):
    if request.user.is_authenticated:
        # Fetch expenses, salaries, and fixed expenses for the current user
        expenses = Expense.objects.filter(user=request.user)
        salaries = Salary.objects.filter(user=request.user)
        fixed_expenses = FixedExpense.objects.filter(user=request.user)

        # Prepare data for the graph
        expense_data = expenses.values('date').annotate(total_amount=Sum('amount')).order_by('date')
        salary_data = salaries.values('date').annotate(total_amount=Sum('amount')).order_by('date')
        fixed_expense_data = fixed_expenses.values('due_date').annotate(total_amount=Sum('amount')).order_by('due_date')

        # Prepare labels and data for the chart
        expense_labels = [entry['date'].strftime('%Y-%m-%d') for entry in expense_data]
        expense_values = [entry['total_amount'] for entry in expense_data]

        salary_labels = [entry['date'].strftime('%Y-%m-%d') for entry in salary_data]
        salary_values = [entry['total_amount'] for entry in salary_data]

        fixed_expense_labels = [entry['due_date'].strftime('%Y-%m-%d') for entry in fixed_expense_data]
        fixed_expense_values = [entry['total_amount'] for entry in fixed_expense_data]

        context = {
            'expense_labels': expense_labels,
            'expense_values': expense_values,
            'salary_labels': salary_labels,
            'salary_values': salary_values,
            'fixed_expense_labels': fixed_expense_labels,
            'fixed_expense_values': fixed_expense_values,
        }
    else:
        context = {
            'expense_labels': [],
            'expense_values': [],
            'salary_labels': [],
            'salary_values': [],
            'fixed_expense_labels': [],
            'fixed_expense_values': [],
        }

    return render(request, 'analytics.html', context)

