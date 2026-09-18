# inference/serializers.py
from rest_framework import serializers
from .models import Assessment, Responses, Prediction


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responses
        fields = ["id", "question", "answer"]


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ["id", "user", "date_taken", "total_score"]
        read_only_fields = ["user", "date_taken", "total_score"]

    def to_internal_value(self, data):
        """
        Allow extra keys (like Age, Gender, etc.) instead of rejecting them.
        """
        ret = {}
        ret["_extra"] = {k: v for k, v in data.items()}
        return ret

    def create(self, validated_data):
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Request is required in context")

        user = request.user
        answers = validated_data.pop("_extra", {})

        assessment = Assessment.objects.create(**validated_data, user=user)

        # Save answers as Response objects
        for q, a in answers.items():
            if q in ["user", "date_taken", "total_score"]:
                continue
            Responses.objects.create(
                assessment=assessment,
                question=q,
                answer=a if a is not None else ""
            )

        return assessment




# inference/serializers.py
class PredictionSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    recommendation = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = ["id", "assessment", "result", "confidence_score", "model_used", "predicted_on", "description", "recommendation"]

    def get_description(self, obj):
        from .utils import get_recommendation
        label = self.map_prediction(obj.result)
        return get_recommendation(label)["description"]

    def get_recommendation(self, obj):
        from .utils import get_recommendation
        label = self.map_prediction(obj.result)
        return get_recommendation(label)["recommendation"]

    def map_prediction(self, result):
        """Map numeric or coded model output to low/medium/high"""
        if str(result) in ["0", "low"]:
            return "low"
        elif str(result) in ["1", "medium"]:
            return "medium"
        elif str(result) in ["2", "high"]:
            return "high"
        else:
            return "low"  # default fallback
