from odoo.tests.common import TransactionCase


class TestDiscCalculation(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestDiscCalculation, self).setUp(*args, **kwargs)

        # PREPARE DATA
        self.currency_id = self.env.ref('base.IDR')
        self.company_id = self.env.ref('base.main_company')
        self.partner_id = self.env.ref('base.res_partner_1')
        
        # PREPARE OBJECT
        self.po_obj = self.env["purchase.order"]
        
        return result
    
    def _prepare_po_data_true(self):
        data = {
            "disc_method": "percent",
            "amount_untaxed": 5000,
            "disc_amount": 50,
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.currency_id.id
        }

        return data
    
    def _prepare_po_data_false(self):
        data = {
            "disc_method": "fixed",
            "amount_untaxed": 10000,
            "disc_amount": 10,
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "currency_id": self.currency_id.id
        }

        return data

    def test_disc_installation_1(self):
        data = self._prepare_po_data_true()
        po_order = self._create_po_no_error(data)
        po_order._disc_calculation()

        return po_order
    
    def test_disc_installation_2(self):
        data = self._prepare_po_data_false()
        po_order = self._create_po_no_error(data)
        po_order._disc_calculation()

        return po_order

    def _create_po_no_error(self, data):
        order = self.po_obj.create(data)
        self.assertIsNotNone(order)

        return order