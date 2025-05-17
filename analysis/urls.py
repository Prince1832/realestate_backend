from django.urls import path
from .views import RealEstateAnalysisView

urlpatterns = [
    path('analyze/', RealEstateAnalysisView.as_view(), name='analyze'),
]