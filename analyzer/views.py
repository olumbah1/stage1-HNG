from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import StringRecord
from .serializers import StringRecordSerializer, AnalyzeRequestSerializer
from .nl_parser import parse_nl_query
import hashlib
import re


def sha256_hash(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def is_palindrome(s: str) -> bool:
    return s.lower() == s.lower()[::-1]


def character_frequency_map(s: str) -> dict:
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def word_count(s: str) -> int:
    return len([w for w in re.split(r"\s+", s) if w != ""])


class CreateAnalyzeString(APIView):
    def post(self, request):
        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        value = serializer.validated_data['value']

        if not isinstance(value, str):
            return Response(
                {'detail': 'Invalid data type for "value" (must be string)'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        record_id = sha256_hash(value)

        if StringRecord.objects.filter(id=record_id).exists():
            return Response(
                {'detail': 'String already exists in the system'},
                status=status.HTTP_409_CONFLICT
            )

        props = {
            'length': len(value),
            'is_palindrome': is_palindrome(value),
            'unique_characters': len(set(value)),
            'word_count': word_count(value),
            'sha256_hash': record_id,
            'character_frequency_map': character_frequency_map(value),
        }

        rec = StringRecord.objects.create(id=record_id, value=value, properties=props)
        out = StringRecordSerializer(rec)
        return Response(out.data, status=status.HTTP_201_CREATED)


class GetSpecificString(APIView):
    def get(self, request, string_value):
        record_id = sha256_hash(string_value)
        rec = get_object_or_404(StringRecord, id=record_id)
        out = StringRecordSerializer(rec)
        return Response(out.data)


class DeleteString(APIView):
    def delete(self, request, string_value):
        record_id = sha256_hash(string_value)
        try:
            rec = StringRecord.objects.get(id=record_id)
        except StringRecord.DoesNotExist:
            return Response(
                {'detail': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )
        rec.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListStrings(APIView):
    def get(self, request):
        is_palindrome_param = request.query_params.get('is_palindrome')
        min_length = request.query_params.get('min_length')
        max_length = request.query_params.get('max_length')
        word_count_q = request.query_params.get('word_count')
        contains_char = request.query_params.get('contains_character')

        parsed_is_pal = None
        if is_palindrome_param is not None:
            low = is_palindrome_param.lower()
            if low not in ('true', 'false'):
                return Response(
                    {'detail': "Invalid value for is_palindrome; must be 'true' or 'false'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            parsed_is_pal = (low == 'true')

        if contains_char is not None and len(contains_char) != 1:
            return Response(
                {'detail': 'contains_character must be a single character'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = StringRecord.objects.all().order_by('-created_at')
        results = []

        for rec in queryset:
            p = rec.properties
            ok = True

            if parsed_is_pal is not None and p.get('is_palindrome') != parsed_is_pal:
                ok = False
            if min_length is not None and p.get('length') < int(min_length):
                ok = False
            if max_length is not None and p.get('length') > int(max_length):
                ok = False
            if word_count_q is not None and p.get('word_count') != int(word_count_q):
                ok = False
            if contains_char is not None and contains_char not in rec.value:
                ok = False

            if ok:
                results.append(StringRecordSerializer(rec).data)

        filters_applied = {
            'is_palindrome': parsed_is_pal,
            'min_length': min_length,
            'max_length': max_length,
            'word_count': word_count_q,
            'contains_character': contains_char
        }

        return Response({
            'data': results,
            'count': len(results),
            'filters_applied': filters_applied
        }, status=status.HTTP_200_OK)
