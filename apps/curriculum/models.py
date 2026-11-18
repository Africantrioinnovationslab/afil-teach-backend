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