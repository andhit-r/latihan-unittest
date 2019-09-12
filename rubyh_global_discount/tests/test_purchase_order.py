from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class TestPurchaseOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestPurchaseOrder, self).setUp(*args, **kwargs)

        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        (self.product_id_1 | self.product_id_2).write(
            {"purchase_method": "purchase"}
        )

        self.order_obj = self.env["purchase.order"]

        return result

    def _prepare_base_vals(self):
        return {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today().strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        ),
                    },
                ),
            ],
        }

    def _prepare_order_with_percent_disc(self):
        data = self._prepare_base_vals()
        data.update({"disc_method": "percent", "disc_amount": 50})

        return data

    def _prepare_order_with_fixed_disc(self):
        data = self._prepare_base_vals()
        data.update({"disc_method": "fixed", "disc_amount": 750})

        return data

    def test_discount_percent(self):
        data = self._prepare_order_with_percent_disc()
        order = self.order_obj.create(data)

        self.assertEqual(order.amount_total, 1875)

    def test_discount_fixed(self):
        data = self._prepare_order_with_fixed_disc()
        order = self.order_obj.create(data)

        self.assertEqual(order.amount_total, 3000)

    def test_tax_round_globally(self):
        company = self.env.user.company_id
        company.write({"tax_calculation_rounding_method": "round_globally"})

        data = self._prepare_base_vals()
        order = self.order_obj.create(data)

        self.assertEqual(order.amount_total, 3750)
