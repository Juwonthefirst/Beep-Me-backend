import profile
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    identification = serializers.CharField(max_length=60)
    password = serializers.CharField(write_only=True)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=60)
    password = serializers.CharField(write_only=True)
