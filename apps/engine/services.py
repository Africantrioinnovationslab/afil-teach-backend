from apps.curriculum.models import Question
from apps.engine.models import DiagnosticRule

def evaluate_attempt(question: Question, submitted_answer: str):
    """
    Evaluates a student's answer against the question's correct answer and diagnostic rules.
    Returns a dictionary detailing the outcome and next steps.
    """
    
    # 1. Check if the answer is correct
    if submitted_answer.strip().lower() == question.correct_answer.strip().lower():
        return {
            "is_correct": True,
            "diagnosis": "CORRECT",
            "next_action": "PROCEED_TO_NEXT_STEP" # e.g., move to practice or mastery
        }
        
    # 2. If wrong, check if there is a specific diagnostic rule for this wrong answer
    try:
        rule = DiagnosticRule.objects.get(
            question=question, 
            trigger_answer__iexact=submitted_answer.strip()
        )
        
        # We found a matching rule! Return the configured diagnosis.
        return {
            "is_correct": False,
            "diagnosis": rule.diagnosis,           # e.g., 'PREREQUISITE_GAP'
            "next_action": rule.next_action,       # e.g., 'SERVE_PREREQUISITE'
            "missing_skill_id": rule.missing_skill.id if rule.missing_skill else None,
            "rule_id": rule.id
        }
        
    except DiagnosticRule.DoesNotExist:
        # 3. No specific rule found (No unsupported certainty)
        # The system shouldn't guess the gap. It asks a follow-up question.
        return {
            "is_correct": False,
            "diagnosis": "UNCERTAIN",
            "next_action": "ASK_FOLLOW_UP",
            "rule_id": None
        }