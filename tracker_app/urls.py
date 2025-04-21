from django.urls import path
from .views import (
    signup,
    user_login,
    user_logout,
    home,  # ✅ Home view
    expense,
    edit_expense,
    delete_expense,
    routine,
    future_plans,
    get_expense_data,
    update_expense_ajax,
    get_routine,         # ✅ New view for fetching single routine data (for editing)
    delete_routine,      # ✅ New view for deleting routine entry
    get_future_plan, 
    update_future_plan,  # ✅ New view for fetching single future plan data (for editing)
    delete_future_plan,  # ✅ New view for deleting future plan entry
    analytics,         # ✅ New view for analytics
    add_salary, 
    get_salary_data, 
    update_salary_ajax,
    delete_salary,      # ✅ New view for deleting salary entry
)
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # User Authentication URLs
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    # Home Page after login
    path('home/', login_required(home), name='home'),

    # Protected URLs
    path('expense/', login_required(expense), name='expense'),
    path('expense/edit/<int:id>/', login_required(edit_expense), name='edit_expense'),
    path('expense/delete/<int:id>/', login_required(delete_expense), name='delete_expense'),
    path('routine/', login_required(routine), name='routine'),
    path('routine/get/<int:id>/', login_required(get_routine), name='get_routine'),          # ✅ Routine GET for editing
    path('routine/delete/<int:id>/', login_required(delete_routine), name='delete_routine'),  # ✅ Routine DELETE
    path('future_plans/', login_required(future_plans), name='future_plans'),
    path('expense/get/<int:id>/', get_expense_data, name='get_expense_data'),
    path('expense/update/', update_expense_ajax, name='update_expense_ajax'),
    path('future_plans/get/<int:id>/', get_future_plan, name='get_future_plan'),
    path('future_plans/update/', update_future_plan, name='update_future_plan'),
    path('future_plans/delete/<int:id>/', delete_future_plan, name='delete_future_plan'),
    path('analytics/',analytics, name='analytics'),  # ✅ New URL for analytics view
    path('salary/add/', add_salary, name='add_salary'),
    path('salary/get/<int:id>/', get_salary_data, name='get_salary_data'),
    path('salary/update/', update_salary_ajax, name='update_salary_ajax'),
    path('delete_salary/<int:id>/', delete_salary, name='delete_salary'),

]
