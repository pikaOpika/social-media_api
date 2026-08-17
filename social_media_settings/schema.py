from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

DETAIL_RESPONSE = inline_serializer(
    name="DetailResponse",
    fields={"detail": serializers.CharField()}
)