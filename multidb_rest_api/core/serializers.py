from rest_framework import serializers


class CoreModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = None  # To be assigned dynamically from ViewSet 
