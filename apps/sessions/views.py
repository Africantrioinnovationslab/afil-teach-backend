from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.curriculum.models import Topic, Question, Hint
from apps.sessions.models import Session, Attempt
from apps.sessions.serializers import SessionStartSerializer
from apps.curriculum.serializers import QuestionSerializer, HintSerializer
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

        # 1. Evaluate the answer
        result = evaluate_attempt(question, submitted_answer)

        # 2. Log the attempt
        Attempt.objects.create(
            session=session, question=question, submitted_answer=submitted_answer,
            is_correct=result['is_correct'], hints_used=hints_used, diagnosis_result=result
        )

        response_data = {
            "is_correct": result['is_correct'],
            "diagnosis": result['diagnosis'],
            "next_action": result['next_action'],
        }

        # 3. THE REMEDIATION ROUTER
        if result['next_action'] == 'SERVE_PREREQUISITE' and result.get('missing_skill_id'):
            # Swap the session to the prerequisite skill
            from apps.curriculum.models import Skill
            prerequisite_skill = Skill.objects.get(id=result['missing_skill_id'])
            session.current_skill = prerequisite_skill
            session.save()
            
            # Fetch a practice question for the prerequisite
            prereq_q = Question.objects.filter(skill=prerequisite_skill).first()
            response_data['next_question'] = QuestionSerializer(prereq_q).data
            response_data['message'] = "Let's step back and practice a foundational skill first."
            
        elif result['next_action'] == 'ASK_FOLLOW_UP':
             # FR-020: Serve a follow-up diagnostic question if uncertain
             follow_up_q = Question.objects.filter(skill=session.current_skill, question_type='DIAGNOSTIC').exclude(id=question.id).first()
             if follow_up_q:
                 response_data['next_question'] = QuestionSerializer(follow_up_q).data
                 response_data['message'] = "Let's try another one to see exactly where you're stuck."

        return Response(response_data, status=status.HTTP_200_OK)

class GetHintView(APIView):
    def post(self, request):
        question_id = request.data.get('question_id')
        current_hint_level = request.data.get('current_hint_level', 0)
        
        question = get_object_or_404(Question, id=question_id)
        
        # Find the next hint in the sequence
        next_hint = Hint.objects.filter(
            question=question, 
            sequence_number=current_hint_level + 1
        ).first()
        
        if not next_hint:
            return Response({"message": "No more hints available."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "hint": HintSerializer(next_hint).data,
            "new_hint_level": next_hint.sequence_number
        }, status=status.HTTP_200_OK)    

class SubmitMasteryView(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        question_id = request.data.get('question_id')
        submitted_answer = request.data.get('submitted_answer')
        hints_used = request.data.get('hints_used', 0)

        session = get_object_or_404(Session, id=session_id)
        question = get_object_or_404(Question, id=question_id)

        # Mastery check cannot be completed with hints
        if hints_used > 0:
            return Response({
                "error": "Independent mastery invalidated. Hints were used on this question."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate the answer
        result = evaluate_attempt(question, submitted_answer)

        # Log the attempt
        Attempt.objects.create(
            session=session, question=question, submitted_answer=submitted_answer,
            is_correct=result['is_correct'], hints_used=hints_used, diagnosis_result=result
        )

        if result['is_correct']:
            # Mark the session as complete / skill mastered
            session.status = 'COMPLETED'
            session.save()
            return Response({"message": "Mastery Achieved!", "status": "COMPLETED"}, status=status.HTTP_200_OK)
        else:
            # If they fail mastery, route them back
            return Response({
                "message": "Mastery not achieved. Let's review.",
                "is_correct": False,
                "next_action": "RETRY_OR_PREREQUISITE"
            }, status=status.HTTP_200_OK)    