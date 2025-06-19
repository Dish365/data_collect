"""
Views for API v1.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from forms.models import Question
from forms.serializers import QuestionSerializer
from projects.models import Project

# Example ViewSet
# class ExampleViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Example.objects.all()
#     serializer_class = ExampleSerializer 

class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Question.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)

    @action(detail=False, methods=['get'])
    def reorder(self, request, project_pk=None):
        """Reorder questions within a project"""
        questions = self.get_queryset()
        order_data = request.data.get('order', [])
        
        if not order_data:
            return Response(
                {'error': 'Order data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update order_index for each question
        for index, question_id in enumerate(order_data):
            Question.objects.filter(id=question_id).update(order_index=index)

        return Response({'status': 'Questions reordered successfully'}) 