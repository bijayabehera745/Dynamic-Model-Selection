from django.urls import path
from .views import ScenarioListView, ScenarioDetailView, CustomDataUploadView

urlpatterns = [
    path('',        ScenarioListView.as_view(),   name='scenario-list'),
    path('upload/', CustomDataUploadView.as_view(), name='custom-data-upload'),
    path('<uuid:pk>/', ScenarioDetailView.as_view(), name='scenario-detail'),
]
