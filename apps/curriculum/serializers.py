from rest_framework import serializers
from apps.curriculum.models import Question, Hint

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # We only send what the frontend needs (Low-Data Mode principle)
        fields = ['id', 'question_type', 'prompt', 'options']

class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = ['sequence_number', 'text']