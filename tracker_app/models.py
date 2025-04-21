from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.TextField()
    payment_method = models.CharField(max_length=100)
    date = models.DateField()
    borrowed = models.BooleanField(default=False)

class Salary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(default=timezone.now)

class FixedExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    description = models.TextField()
    due_date = models.DateField()

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField()
    date = models.DateField()

class FuturePlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField()
    priority = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    email_reminder = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title