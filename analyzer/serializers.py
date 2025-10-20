from rest_framework import serializers
from .models import StringRecord


class PropertiesSerializer(serializers.Serializer):
    length = serializers.IntegerField()
    is_palindrome = serializers.BooleanField()
    unique_characters = serializers.IntegerField()
    word_count = serializers.IntegerField()
    sha256_hash = serializers.CharField()
    character_frequency_map = serializers.DictField(child=serializers.IntegerField())


class StringRecordSerializer(serializers.ModelSerializer):
    properties = PropertiesSerializer()


    class Meta:
        model = StringRecord
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['id', 'properties', 'created_at']


class AnalyzeRequestSerializer(serializers.Serializer):
    value = serializers.CharField()