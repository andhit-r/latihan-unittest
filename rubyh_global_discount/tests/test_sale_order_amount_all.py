from odoo.tests.common import TransactionCase


class TestSaleOrderAmountAll(TransactionCase):

    def setUp(self):
        super(TestSaleOrderAmountAll, self).setUp()
        self.partner_01 = self.env.ref('base.res_partner_10').id
        self.product_01 = self.env.ref('product.product_product_13').id

    def test_amount_all(self):
        data = self._prepare_order_data()
        so = self.env['sale.order'].create(data)
        self.assertEqual(so.amount_total, 9000)

    def _prepare_order_data(self):
        data =  {
            'partner_id': self.partner_01,
            'partner_invoice_id': self.partner_01,
            'partner_shipping_id': self.partner_01,
            'order_line': [(0, 0, {
                'name': 'Test Product',
                'product_id': self.product_01,
                'product_uom_qty': 1,
                'product_uom': 1,
                'price_unit': 10000,
                'tax_id': False,
                }),
            ],
            'disc_amount': 1000,
        }

        return data
    