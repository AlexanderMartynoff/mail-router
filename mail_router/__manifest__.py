# -*- coding: utf-8 -*-

{
    'name': 'Mail Router',
    'category': 'Mail',
    'version': '10.1.0.0',
    'author': 'Alexander Martynov',
    'support': 'triplustri@mail.ru',
    'price': 10,
    'currency': 'EUR',
    'depends': ['fetchmail'],
    'data': [
        'view/mail_router_views.xml',
        'view/fetchmail_views.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'OPL-1',
    'description': """
        The module allows you to configure advanced routing of mail messages
        to create entries in the Odoo database. Features provided by the standard module "mail" to create entries may not be enough.
        The module allows you to extract the necessary information from the letters through the flexible settings system
        and save it in the database as model records.
    """,
}
