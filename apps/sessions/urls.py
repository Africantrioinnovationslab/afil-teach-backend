from django.urls import path
from apps.sessions.views import StartSessionView, SubmitAnswerView, GetHintView, SubmitMasteryView

urlpatterns = [
    path('start/', StartSessionView.as_view(), name='start_session'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('get-hint/', GetHintView.as_view(), name='get_hint'),
    path('submit-mastery/', SubmitMasteryView.as_view(), name='submit_mastery'),
]