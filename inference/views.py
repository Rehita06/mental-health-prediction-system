# inference/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd, numpy as np, os, json
from .serializers import AssessmentSerializer, PredictionSerializer
from rest_framework import permissions
from .utils import get_model_and_meta
from pathlib import Path
from .models import Prediction, Assessment, Responses
from collections import Counter
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

@login_required(login_url='/login/')
def demo_page(request):
    return render(request, 'form.html')

# Assessment API
class AssessmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = AssessmentSerializer(data=request.data, context={'request': request})
        if ser.is_valid():
            assessment = ser.save()
            return Response(AssessmentSerializer(assessment).data, status=201)
        return Response(ser.errors, status=400)



# Prediction API
class PredictAssessmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id, user=request.user)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=404)

        # Build feature row from responses
        responses = {r.question: r.answer for r in assessment.responses.all()}

        try:
            model, meta = get_model_and_meta()
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        cols = meta["raw_feature_names"]
        row = {c: responses.get(c, None) for c in cols}
        X = pd.DataFrame([row], columns=cols)

        try:
            pos_prob = None
            # --- CHANGED: compute probability if possible and capture classes ---
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)
                classes = list(model.classes_)
                # DEBUG prints to help find why probabilities look the way they do.
                # Replace prints with proper logger.debug in production.
                print("DEBUG: model.classes_ =", classes)
                print("DEBUG: proba =", proba)
                print("DEBUG: feature row =", X.to_dict(orient='records')[0])

                # pick positive label from meta if provided, otherwise use last class
                pos_label = meta.get("positive_label", classes[-1])
                if pos_label not in classes:
                    # fallback to last class
                    pos_idx = -1
                else:
                    pos_idx = classes.index(pos_label)
                pos_prob = float(proba[0, pos_idx])
            else:
                pos_prob = None

            pred = model.predict(X)[0]

            # --- CHANGED: enforce HIGH risk if confidence > 0.75 ---
            # If model gave a probability and it's > 0.75, override the prediction
            # to the code '2' (your serializer maps "2" or "high" -> high).
            # Change "2" to whatever numeric label your model uses for "high" if different.
            if pos_prob is not None and pos_prob > 0.75:
                # For safety, convert prediction to string (you store str in DB)
                pred = "2"  # force 'high' label
                print("DEBUG: Overriding prediction to HIGH because confidence >", 0.75)

            prediction = Prediction.objects.create(
                assessment=assessment,
                result=str(pred),
                confidence_score=pos_prob,
                model_used=meta.get("best_model", "unknown"),
            )

            return Response(PredictionSerializer(prediction).data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

# User Dashboard API (view own results)
# class UserResultsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         assessments = Assessment.objects.filter(user=request.user).prefetch_related("responses", "prediction")
#         data = AssessmentSerializer(assessments, many=True).data
#         return render(request, "user_results.html", {"assessments": assessments})


# Health check
def health(request):
    return JsonResponse({"status": "ok"})


# Admin dashboard 
from django.contrib.admin.views.decorators import staff_member_required
# inference/views.py
from django.db.models import Prefetch
from collections import Counter
from .models import Prediction, Profile

@staff_member_required
def admin_dashboard(request):
    records = (
        Prediction.objects
        .select_related("assessment__user", "assessment__user__profile")  # ✅ fetch profile
        .order_by("-predicted_on")
    )

    risks = [r.result for r in records]
    risk_counts = Counter(risks)
    users = Counter([r.assessment.user.username for r in records])

    context = {
        "records": records,
        "risk_labels": list(risk_counts.keys()),
        "risk_values": list(risk_counts.values()),
        "user_labels": list(users.keys()),
        "user_values": list(users.values()),
    }
    return render(request, "admin_dashboard.html", context)


class UserResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch model instances instead of serialized data
        assessments = Assessment.objects.filter(user=request.user).select_related("prediction").order_by("-date_taken")
        return render(request, "user_results.html", {"assessments": assessments})

# authentication
# inference/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Profile
from django.contrib.auth import logout

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        designation = request.POST.get("designation")
        company = request.POST.get("company")
        phone = request.POST.get("phone")   # ✅ new field

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password, email=email)
            profile = Profile.objects.get(user=user)
            profile.age = age
            profile.gender = gender
            profile.designation = designation
            profile.company = company
            profile.phone = phone   # ✅ save phone
            profile.save()

            login(request, user)
            return redirect("demo")
        else:
            return render(request, "signup.html", {"error": "Username already exists"})
    return render(request, "signup.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("demo")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
