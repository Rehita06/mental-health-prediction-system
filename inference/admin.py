# inference/admin.py
from django.contrib import admin
from .models import Assessment, Responses, Prediction, Profile

# Inline for Responses in Assessment
class ResponsesInline(admin.TabularInline):
    model = Responses
    extra = 0  # do not show extra empty rows

# Inline for Prediction in Assessment
class PredictionInline(admin.StackedInline):
    model = Prediction
    readonly_fields = ("predicted_on",)
    can_delete = False
    max_num = 1

# Admin for Assessment
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date_taken", "total_score")
    list_filter = ("date_taken", "user")
    search_fields = ("user__username",)
    inlines = [ResponsesInline, PredictionInline]
    readonly_fields = ("date_taken",)

# Admin for Responses (optional, can be accessed via AssessmentInline)
@admin.register(Responses)
class ResponsesAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "question", "answer")
    search_fields = ("question", "answer", "assessment__user__username")

# Admin for Prediction
@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "result", "confidence_score", "model_used", "predicted_on")
    list_filter = ("result", "model_used")
    search_fields = ("assessment__user__username", "result", "model_used")
    readonly_fields = ("predicted_on",)

# Admin for Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "gender", "designation", "company", "created_at")
    search_fields = ("user__username", "designation", "company")
    readonly_fields = ("created_at",)
