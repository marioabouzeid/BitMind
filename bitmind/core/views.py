"""
Core views for app.
"""
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    # Define a serializer class that doesn't do anything special
    serializer_class = type("HealthCheckSerializer", (serializers.Serializer,), {})

    def get(self, request, *args, **kwargs):
        data = {"healthy": True}
        return Response(data, status=status.HTTP_200_OK)
