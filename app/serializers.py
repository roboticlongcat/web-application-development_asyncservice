from rest_framework import serializers


class InsulinCalculationSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(min_value=1)
    current_glucose = serializers.FloatField(min_value=0)
    target_glucose = serializers.FloatField(min_value=0)
    sensitivity_coeff = serializers.FloatField(min_value=0.1)
    bread_units = serializers.FloatField(min_value=0)

    def validate(self, data):
        if data['current_glucose'] < data['target_glucose']:
            raise serializers.ValidationError("Текущий уровень глюкозы не может быть ниже целевого")
        return data


class CalculationResponseSerializer(serializers.Serializer):
    calculated_dose = serializers.FloatField()
    calculation_time = serializers.CharField()
    status = serializers.CharField()
    request_id = serializers.CharField(required=False)