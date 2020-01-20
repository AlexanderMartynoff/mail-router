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
        Advanced routing of mail messages
    """,
}
