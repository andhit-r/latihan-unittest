# -*- coding: utf-8 -*-
{
    'name': "Global Discount",
    'summary': """Global Discount Costumization for Purchase order,
               Sales order, and Vendor bills.""",
    'description': """
        This module manages the followings:
            - Purchase
            - Sale
    """,
    'author': "Ruby.h",
    'website': "http://www.rubyh.co",
    'category': 'Purchase',
    'version': '10.0.0.0.1',
    'depends': [
        'base',
        'sale',
        'purchase',
    ],
    'data': [
        'views/rubyh_purchase_order.xml',
        'views/rubyh_reports.xml',
        'views/rubyh_po_report.xml',
        'views/rubyh_rfq_report.xml',
        'views/rubyh_account_report.xml',
        'views/rubyh_sale_report.xml',
    ],
    'demo': [

    ],
}
