from rest_framework import serializers

from tax.models import TaxCenterAssigned


class TaxCenterAssignedSerializer(serializers.ModelSerializer):
    taxCenter_name = serializers.CharField(source="taxCenter.name", read_only=True)

    class Meta:
        model = TaxCenterAssigned
        fields = [
            "id",
            "taxCenter",
            "taxCenter_name",
            "status",
            "created_at",
            "updated_at",
        ]
