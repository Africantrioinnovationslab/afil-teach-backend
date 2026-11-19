from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.curriculum.models import Topic, Question
from apps.sessions.models import Session, Attempt
from apps.sessions.serializers import SessionStartSerializer
from apps.curriculum.serializers import QuestionSerializer
from apps.engine.services import evaluate_attempt

class StartSessionView(APIView):
    def post(self, request):
        serializer = SessionStartSerializer(data=request.data)
        if serializer.is_valid():
            topic = get_object_or_404(Topic, id=serializer.validated_data['topic_id'])
            
            # 1. Create the session 
            # (Note: request.user will work once second dev finishes the Auth layer. 
            # For now, you might need to hardcode a dummy student to test this).
            session = Session.objects.create(
                student=request.user, 
                topic=topic,
                current_skill=topic.skills.first() # Start with the first skill of the topic
            )
            
            # 2. Fetch a diagnostic question for the first skill
            diagnostic_q = Question.objects.filter(
                skill=session.current_skill, 
                question_type='DIAGNOSTIC'
            ).first()
            
            if not diagnostic_q:
                return Response({"error": "No diagnostic question found for this skill."}, status=404)

            return Response({
                "session_id": session.id,
                "skill_name": session.current_skill.name,
                "question": QuestionSerializer(diagnostic_q).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitAnswerView(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        question_id = request.data.get('question_id')
        submitted_answer = request.data.get('submitted_answer')
        hints_used = request.data.get('hints_used', 0)

        session = get_object_or_404(Session, id=session_id)
        question = get_object_or_404(Question, id=question_id)

        # 1. Evaluate the answer using your Engine Service
        result = evaluate_attempt(question, submitted_answer)

        # 2. Log the attempt (Audit Trail - FR-022)
        attempt = Attempt.objects.create(
            session=session,
            question=question,
            submitted_answer=submitted_answer,
            is_correct=result['is_correct'],
            hints_used=hints_used,
            diagnosis_result=result
        )

        # 3. Return the evaluation result to the frontend
        return Response({
            "is_correct": result['is_correct'],
            "diagnosis": result['diagnosis'],
            "next_action": result['next_action'],
            "attempt_id": attempt.id
        }, status=status.HTTP_200_OK)