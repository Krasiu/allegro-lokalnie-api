import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

from .config import headers


@dataclass
class Order:
    item_name: str = None
    buyer_login: str = None
    quantity: int = None
    payment_status: str = None
    item_id: str = None
    user_id: str = None
    bought_at: datetime = None
    buyer_email: str = None


class AllegroLokalnie:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update({"_ui_key": api_key})

    def get_orders(self, page: int = 1) -> List[Order]:
        params = {"page": page}
        response = self.session.get(
            "https://allegrolokalnie.pl/konto/oferty/sprzedane", params=params
        )
        soup = BeautifulSoup(response.text, "lxml")
        offers: List[Tag] = soup.find_all("div", itemtype="http://schema.org/Offer")
        orders = []
        for o in offers:
            order = self._parse_offer(o)
            orders.append(order)
        return orders

    def get_all_orders(self) -> List[Order]:
        last_page = self._get_number_of_pages_with_orders()
        all_orders = []
        for page in range(1, last_page + 1):
            orders = self.get_orders(page=page)
            all_orders.extend(orders)
        return all_orders

    def _get_number_of_pages_with_orders(self) -> int:
        response = self.session.get("https://allegrolokalnie.pl/konto/oferty/sprzedane")
        soup = BeautifulSoup(response.text, "lxml")
        number_of_pages = int(
            soup.find("div", class_="pagination__pages")
            .find("input")
            .next.strip()
            .split()[-1]
        )
        return number_of_pages

    @staticmethod
    def _parse_offer(offer: Tag) -> Order:
        order = Order()
        order.item_name = offer.find(itemprop="itemOffered").text
        order.buyer_login = (
            offer.find(class_="offer-card__extended-buyer").text.strip().split()[0]
        )
        order.quantity = int(offer.find(text=re.compile("Liczba sztuk")).next.text)
        _, _, order.item_id, order.user_id = offer.find(
            "a", href=re.compile("konwersacje")
        )["href"].split("/")
        order.payment_status = offer.find(text=re.compile("Płatność")).next.text
        order.bought_at = datetime.strptime(
            offer.find("time")["datetime"], "%Y-%m-%d %H:%M:%S.%fZ"
        )
        try:
            order.buyer_email = (
                offer.find(text=re.compile("email.")).strip().split()[-1]
            )
        except AttributeError:
            pass
        return order
