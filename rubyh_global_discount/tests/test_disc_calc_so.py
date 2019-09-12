from odoo.tests.common import TransactionCase
from odoo.exceptions import except_orm

class TestDiscCalculation(TransactionCase):
  
  def setUp(self):
    result = super(TestDiscCalculation, self).setUp()
    # data SO
    self.partner = self.env.ref("base.res_partner_2")
    self.partner_invoice = self.env.ref("base.res_partner_2")
    self.partner_shipping = self.env.ref("base.res_partner_2")
    self.user = self.env.ref("base.user_demo")
    self.pricelist = self.env.ref("product.list0")
    self.team = self.env.ref("sales_team.team_sales_department")
    self.date_order = "2019-09-12"
    # data SO Line
    self.name = "Laptop E5023"
    self.product =  self.env.ref("product.product_product_25")
    self.product_uom =  self.env.ref("product.product_uom_unit")

    return result

  def test_disc_percent(self):
    self.order = self.env["sale.order"].create({
      "partner_id": self.partner.id,
      "partner_invoice_id": self.partner.id,
      "partner_shipping_id": self.partner.id,
      "user_id": self.user.id,
      "pricelist_id": self.pricelist.id,
      "team_id": self.team.id,
      "date_order": self.date_order,
      "discount_method": "percent",
      "discount_amount": 10
    })

    self.orderLine = self.env["sale.order.line"].create({
      "order_id": self.order,
      "name": self.name,
      "product_id": self.product,
      "product_uom_qty": 1,
      "product_uom": self.product_uom,
      "price_unit": 1000,
    })

    self.assertEqual(self.order.disc_calc, 100)
    