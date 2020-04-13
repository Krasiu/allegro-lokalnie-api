from rest_framework_dataclasses.serializers import DataclassSerializer

from clients.allegro.lokalnie import Order


class OrderSerializer(DataclassSerializer):
    class Meta:
        dataclass = Order
