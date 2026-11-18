import uuid
from django.db import models

class Subject(models.Model):
    """
    Represents the main subjects (e.g., English Language, Mathematics).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    """
    Represents a specific topic within a subject and class level.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    class_level = models.CharField(max_length=20, help_text="e.g., 'SS2', 'JSS1'")
    
    def __str__(self):
        return f"{self.class_level} {self.subject.name}: {self.name}"


class Skill(models.Model):
    """
    The specific learning objective or skill being tested. 
    This is the core of our diagnostic engine.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)
    learning_objective = models.TextField()
    
    # This allows a skill to point to other skills that must be learned first.
    prerequisites = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True, 
        related_name='dependent_skills',
        help_text="Skills that must be mastered before attempting this one."
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    """
    Represents a specific question (Diagnostic, Practice, or Mastery).
    """
    QUESTION_TYPES = (
        ('DIAGNOSTIC', 'Diagnostic'),
        ('PRACTICE', 'Practice'),
        ('MASTERY', 'Mastery'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    
    # The actual text of the question
    prompt = models.TextField(help_text="e.g., 'Choose the verb: The box of oranges ___ on the table.'")
    
    # For multiple choice (stored as a JSON list, e.g., ["is", "are"])
    options = models.JSONField(default=list, blank=True, help_text="Leave empty for open-ended questions")
    
    # The correct answer
    correct_answer = models.CharField(max_length=255)
    
    # To track why the system selected this question
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_type} | {self.skill.name} | {self.prompt[:40]}..."


class Hint(models.Model):
    """
    Progressive hints for a specific question.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='hints')
    
    # The order of the hint (1, 2, 3...)
    sequence_number = models.PositiveIntegerField()
    text = models.TextField(help_text="e.g., 'Cover the phrase of oranges. What is the true subject?'")

    class Meta:
        ordering = ['sequence_number']
        # Ensure a question doesn't have two 'Hint 1s'
        unique_together = ('question', 'sequence_number')

    def __str__(self):
        return f"Hint {self.sequence_number} for {self.question.id}"    