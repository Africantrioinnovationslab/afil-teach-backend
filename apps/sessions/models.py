import uuid
from django.db import models
from django.conf import settings
from apps.curriculum.models import Topic, Skill

class Session(models.Model):
    """
    Tracks a student's complete journey through a single topic.
    """
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Links to Student model
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    
    # Tracks where the student currently is in the engine
    current_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} | Student: {self.student.local_identifier} | Status: {self.status}"


class Attempt(models.Model):
    """
    Logs every single answer a student submits, whether correct or incorrect.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attempts')
    question = models.ForeignKey('curriculum.Question', on_delete=models.CASCADE)
    
    submitted_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    # Tracks hint usage (crucial for Mastery validation)
    hints_used = models.IntegerField(default=0)
    
    # The result of the Rules Engine evaluation
    diagnosis_result = models.JSONField(null=True, blank=True, help_text="Stores the rule triggered and next action")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt on Q:{self.question.id} | Correct: {self.is_correct}"