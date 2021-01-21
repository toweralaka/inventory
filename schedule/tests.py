from django.test import TestCase
from django.utils import timezone

from datetime import date, datetime, timedelta

from .models import Product, PurchaseOrder
from management.models import Merchant

# if instance.is_reorder_level():
#         if instance.sent_purchase_order():
#             if instance.is_late_delivery():
#                 instance.purchase_order_reminder()

class ProductModelTests(TestCase):
    def test_reorder_level_with_lower_balance(self):
        """
        is_reorder_level returns true with lower balance.
        """
        balance = 10
        reorder_level = 12
        d_product = Product(reorder_level=reorder_level, balance=balance)
        self.assertIs(d_product.is_reorder_level(), True)

    # def test_late_delivery(self):
    #     merch = Merchant(name='Company')
    #     prod = Product(minimum_order_wait_duration=5, merchant=merch)
    #     d_date = timezone.now() - timedelta(days=5)
    #     the_order = PurchaseOrder(
    #         product=prod, fulfilled=False, date=d_date)
    #     self.assertIs(the_order.product.is_late_delivery(), True)

    # def test_sent_purchase_order_without_sending(self):
    #     """
    #     is_reorder_level returns true with lower balance.
    #     """
    #     merch = Merchant.objects.get(pk=1)
    #     d_product = Product(merchant=merch)
    #     self.assertIs(d_product.sent_purchase_order(), False)


class PurchaseOrderModelTest(TestCase):
    def test_late_delivery(self):
        prod = Product(minimum_order_wait_duration=5)
        d_date = timezone.now() - timedelta(days=5)
        the_order = PurchaseOrder(
            product=prod, fulfilled=False, date=d_date)
        self.assertIs(the_order.is_late_delivery(), True)