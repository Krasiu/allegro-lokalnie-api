import os

from rest_framework import views
from rest_framework.response import Response

from clients.allegro.lokalnie import AllegroLokalnie
from .serializers import OrderSerializer


class OrderView(views.APIView):
    def get(self, request):
        api = AllegroLokalnie(os.environ["ALLEGRO_LOKALNIE_API_KEY"])
        data = api.get_all_orders()
        results = OrderSerializer(data, many=True).data
        return Response(results)
