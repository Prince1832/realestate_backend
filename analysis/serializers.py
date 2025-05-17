from rest_framework import serializers

class AnalysisRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    file = serializers.FileField(required=False)