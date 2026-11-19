from rest_framework import serializers
from apps.sessions.models import Session

class SessionStartSerializer(serializers.Serializer):
    topic_id = serializers.UUIDField()