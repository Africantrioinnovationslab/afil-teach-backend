from django.urls import path
from apps.sessions.views import StartSessionView, SubmitAnswerView

urlpatterns = [
    path('start/', StartSessionView.as_view(), name='start_session'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit_answer'),
]