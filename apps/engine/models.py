import uuid
from django.db import models
from apps.curriculum.models import Question, Skill

class DiagnosticRule(models.Model):
    """
    The hybrid rules engine storage. 
    These rules evaluate a student's wrong answer to determine the exact gap.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='diagnostic_rules')
    
    # The specific wrong answer the student chose (distractor)
    trigger_answer = models.CharField(max_length=255, help_text="The exact wrong answer that triggers this rule.")
    
    # What does this wrong answer mean?
    DIAGNOSIS_TYPES = (
        ('PREREQUISITE_GAP', 'Prerequisite Gap'),
        ('APPLICATION_ERROR', 'Application Error'),
        ('UNCERTAIN', 'Uncertain / Need Follow-up'),
    )
    diagnosis = models.CharField(max_length=50, choices=DIAGNOSIS_TYPES)
    
    # If it's a prerequisite gap, which skill is missing?
    missing_skill = models.ForeignKey(
        Skill, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='triggered_by_rules'
    )
    
    # What should the system do next?
    NEXT_ACTIONS = (
        ('SERVE_PREREQUISITE', 'Serve Prerequisite Lesson'),
        ('SERVE_HINT', 'Serve Hint'),
        ('ASK_FOLLOW_UP', 'Ask Follow-up Question'),
    )
    next_action = models.CharField(max_length=50, choices=NEXT_ACTIONS)

    def __str__(self):
        return f"Rule for Q:{self.question.id} -> {self.diagnosis}"