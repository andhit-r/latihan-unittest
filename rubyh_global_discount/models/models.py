# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from odoo.exceptions import UserError


class RubyhPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    disc_method = fields.Selection(
        string="Discount Method",
        selection=[("fixed", "Fixed"), ("percent", "Percentage")],
    )
    disc_amount = fields.Float(string="Discount Amount")
    disc_calc = fields.Monetary(
        string="Discount",
        store=True,
        readonly=True,
        compute="_disc_calculation",
    )

    @api.onchange("disc_amount", "disc_method")
    @api.depends("disc_amount", "disc_method", "order_line.price_total")
    def _disc_calculation(self):
        for order in self:
            if order.disc_method == "percent":
                order.disc_calc = order.amount_untaxed * (
                    order.disc_amount / 100
                )
            else:
                order.disc_calc = order.disc_amount

    @api.depends("order_line.price_total", "disc_calc", "disc_method")
    def _amount_all(self):
        for order in self:
            # CUSTOM CODE
            total = sum(order.order_line.mapped("price_subtotal"))
            # END OF CUSTOM CODE
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                # CUSTOM CODE
                if order.disc_method == "percent":
                    new_price_unit = line.price_unit - (
                        line.price_unit * (order.disc_amount / 100)
                    )
                else:
                    if total:
                        new_price_unit = line.price_unit - (
                            (line.price_unit / total) * order.disc_calc
                        )
                    else:
                        new_price_unit = line.price_unit

                if (
                    order.company_id.tax_calculation_rounding_method
                    == "round_globally"
                ):
                    taxes = line.taxes_id.compute_all(
                        new_price_unit,
                        line.order_id.currency_id,
                        line.product_qty,
                        product=line.product_id,
                        partner=line.order_id.partner_id,
                    )
                    amount_tax += sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    )
                else:
                    taxes = line.taxes_id.compute_all(
                        new_price_unit,
                        line.order_id.currency_id,
                        line.product_qty,
                        product=line.product_id,
                        partner=line.order_id.partner_id,
                    )
                    amount_tax += (
                        taxes["total_included"] - taxes["total_excluded"]
                    )
                # END OF CUSTOM CODE
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed
                    + amount_tax
                    - order.disc_calc,
                }
            )


class RubyhSaleOrder(models.Model):
    _inherit = "sale.order"

    disc_method = fields.Selection(
        string="Discount Method",
        selection=[("fixed", "Fixed"), ("percent", "Percentage")],
    )
    disc_amount = fields.Float(string="Discount Amount")
    disc_calc = fields.Monetary(
        string="Discount",
        store=True,
        readonly=True,
        compute="_disc_calculation",
    )

    @api.onchange("disc_amount", "disc_method")
    @api.depends("disc_amount", "disc_method", "order_line")
    def _disc_calculation(self):
        for order in self:
            if order.disc_method == "percent":
                order.disc_calc = order.amount_untaxed * (
                    order.disc_amount / 100
                )
            else:
                order.disc_calc = order.disc_amount

    @api.depends("order_line.price_total", "disc_calc")
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        # CUSTOM CODE
        for order in self:
            total = sum(order.order_line.mapped("price_subtotal"))
            # END OF CUSTOM CODE
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                # CUSTOM CODE
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if order.disc_method == "percent":
                    new_price_unit = price - (
                        price * (order.disc_amount / 100)
                    )
                else:
                    if total:
                        new_price_unit = price - (
                            (price / total) * order.disc_calc
                        )
                    else:
                        new_price_unit = price

                if (
                    order.company_id.tax_calculation_rounding_method
                    == "round_globally"
                ):
                    taxes = line.tax_id.compute_all(
                        new_price_unit,
                        line.order_id.currency_id,
                        line.product_uom_qty,
                        product=line.product_id,
                        partner=order.partner_shipping_id,
                    )
                    amount_tax += sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    )
                else:
                    taxes = line.tax_id.compute_all(
                        new_price_unit,
                        line.order_id.currency_id,
                        line.product_uom_qty,
                        product=line.product_id,
                        partner=order.partner_shipping_id,
                    )
                    amount_tax += (
                        taxes["total_included"] - taxes["total_excluded"]
                    )
                # END OF CUSTOM CODE
            order.update(
                {
                    "amount_untaxed": order.pricelist_id.currency_id.round(
                        amount_untaxed
                    ),
                    "amount_tax": order.pricelist_id.currency_id.round(
                        amount_tax
                    ),
                    "amount_total": amount_untaxed
                    + amount_tax
                    - order.disc_calc,
                }
            )


class RubyhAccountInvoice(models.Model):
    _inherit = "account.invoice"

    disc_method = fields.Selection(
        string="Discount Method",
        selection=[("fixed", "Fixed"), ("percent", "Percentage")],
    )
    disc_amount = fields.Float(string="Discount Amount")
    disc_calc = fields.Monetary(
        string="Discount",
        store=True,
        readonly=True,
        compute="_disc_calculation",
    )

    @api.onchange("disc_amount", "disc_method", "invoice_line_ids")
    @api.depends("disc_amount", "disc_method", "invoice_line_ids")
    def _disc_calculation(self):
        for order in self:
            if order.disc_method == "percent":
                order.disc_calc = order.amount_untaxed * (
                    order.disc_amount / 100
                )
            else:
                order.disc_calc = order.disc_amount

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        total = sum(self.invoice_line_ids.mapped("price_subtotal"))
        for line in self.invoice_line_ids:
            # apply global discount from PO
            if self.disc_method == "percent":
                price_unit = line.price_unit - (
                    line.price_unit * (self.disc_amount / 100)
                )
            elif self.disc_method == "fixed":
                price_unit = line.price_unit - (
                    line.price_unit / total * self.disc_calc
                )
            else:
                price_unit = line.price_unit
            # END OF CUSTOM CODE
            taxes = line.invoice_line_tax_ids.compute_all(
                price_unit,
                self.currency_id,
                line.quantity,
                line.product_id,
                self.partner_id,
            )["taxes"]
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = (
                    self.env["account.tax"]
                    .browse(tax["id"])
                    .get_grouping_key(val)
                )

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]["amount"] += val["amount"]
                    tax_grouped[key]["base"] += val["base"]
        return tax_grouped

    # compute amount_total
    @api.one
    @api.depends(
        "invoice_line_ids.price_subtotal",
        "tax_line_ids.amount",
        "currency_id",
        "company_id",
        "date_invoice",
        "type",
        "disc_method",
        "disc_amount",
    )
    def _compute_amount(self):
        round_curr = self.currency_id.round
        # CUSTOM CODE
        self.amount_untaxed = sum(
            line.price_subtotal for line in self.invoice_line_ids
        )
        # END OF CUSTOM CODE
        self.amount_tax = sum(
            round_curr(line.amount) for line in self.tax_line_ids
        )
        self.amount_total = (
            self.amount_untaxed + self.amount_tax - self.disc_calc
        )
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if (
            self.currency_id
            and self.company_id
            and self.currency_id != self.company_id.currency_id
        ):
            currency_id = self.currency_id.with_context(
                date=self.date_invoice
            )
            amount_total_company_signed = currency_id.compute(
                self.amount_total, self.company_id.currency_id
            )
            amount_untaxed_signed = currency_id.compute(
                self.amount_untaxed, self.company_id.currency_id
            )
        sign = self.type in ["in_refund", "out_refund"] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    # Same with the default code, just add onchange key
    @api.onchange("invoice_line_ids", "disc_calc")
    @api.depends("disc_calc")
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered("manual")
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    # Create move line for global discount
    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        if self.disc_method:
            # SUBSTRACT TOTAL AMOUNT WITH DISCOUNT IN TOTAL MOVE LINE
            total_line = list(
                filter(lambda l: l[2]["name"] == "/", move_lines)
            )
            if self.journal_id.type == "purchase":
                if not self.company_id.purchase_disc_acc_id:
                    raise UserError(
                        _("Please choose an account for recording discounts.")
                    )

                # SUBSTRACT TOTAL AMOUNT WITH DISCOUNT IN TOTAL MOVE LINE
                new_credit = total_line[0][2]["credit"] - self.disc_calc
                total_line[0][2]["credit"] = new_credit
                # CREATE NEW DISCOUNT MOVE LINE
                move_lines.append(
                    (
                        0,
                        0,
                        {
                            "analytic_account_id": False,  #
                            "tax_ids": [],  #
                            "name": "Global Discount",
                            "analytic_tag_ids": [],  #
                            "product_uom_id": False,  #
                            "invoice_id": self.id,
                            "analytic_line_ids": [],  #
                            "tax_line_id": False,  #
                            "currency_id": False,  #
                            "credit": self.disc_calc,
                            "product_id": False,  #
                            "date_maturity": False,
                            "debit": False,
                            "amount_currency": 0,  #
                            "quantity": 1,
                            "partner_id": (
                                self.partner_id.commercial_partner_id.id
                            ),
                            "account_id": (
                                # self.company_id.discount_debit_acc.id
                                self.company_id.purchase_disc_acc_id.id,
                            ),
                        },
                    )
                )
            else:
                if not self.company_id.sales_disc_acc_id:
                    raise UserError(
                        _("Please choose an account for recording discounts.")
                    )

                # import wdb; wdb.set_trace()
                # SUBSTRACT TOTAL AMOUNT WITH DISCOUNT IN TOTAL MOVE LINE
                new_debit = total_line[0][2]["debit"] - self.disc_calc
                total_line[0][2]["debit"] = new_debit
                # CREATE NEW DISCOUNT MOVE LINE
                move_lines.append(
                    (
                        0,
                        0,
                        {
                            "analytic_account_id": False,  #
                            "tax_ids": [],  #
                            "name": "Global Discount",
                            "analytic_tag_ids": [],  #
                            "product_uom_id": False,  #
                            "invoice_id": self.id,
                            "analytic_line_ids": [],  #
                            "tax_line_id": False,  #
                            "currency_id": False,  #
                            "credit": False,
                            "product_id": False,  #
                            "date_maturity": False,
                            "debit": self.disc_calc,
                            "amount_currency": 0,  #
                            "quantity": 1,
                            "partner_id": (
                                self.partner_id.commercial_partner_id.id
                            ),
                            "account_id": self.company_id.sales_disc_acc_id.id,
                        },
                    )
                )
        return move_lines

    # VALIDATION FOR DISCOUNT ACCOUNTS IN COMPANY
    @api.multi
    def action_invoice_open(self):
        if (
            self.disc_method
            and not self.company_id.purchase_disc_acc_id
            and not self.company_id.sales_disc_acc_id
        ):
            raise UserError(
                _("Please set Discount Accounts if you use Global Discount!")
            )
            return False
        return super(RubyhAccountInvoice, self).action_invoice_open()

    # LOAD DISCOUNT METHOD AND AMOUNT FROM SO
    @api.model
    def create(self, vals):
        res = super(RubyhAccountInvoice, self).create(vals)
        # link to the SO, and assign the discount fields
        so = self.env["sale.order"].search([("name", "=", res.origin)])
        if so.disc_method:
            res.update(
                {"disc_method": so.disc_method, "disc_amount": so.disc_amount}
            )
        return res


class RubyhResCompany(models.Model):
    _inherit = "res.company"

    sales_disc_acc_id = fields.Many2one(
        "account.account", "Sales Discount Account"
    )
    purchase_disc_acc_id = fields.Many2one(
        "account.account", "Purchase Discount Account"
    )
