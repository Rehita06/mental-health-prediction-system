# inference/models.py
from django.db import models
from django.contrib.auth.models import User

class Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    date_taken = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Assessment {self.id} by {self.user.username}"


class Responses(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="responses")
    question = models.TextField()
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Response {self.id} - {self.question[:30]}..."


class Prediction(models.Model):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="prediction")
    result = models.CharField(max_length=50)
    confidence_score = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=50)
    predicted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.id} - {self.result}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username