# -*- coding: utf-8 -*-

from logging import getLogger

from odoo import models, fields, api


logger = getLogger(__name__)


class MailRouterFieldParser(models.Model):
    _name = 'mail_router.field_parser'

    name = fields.Char(string='Name')
    display_name = fields.Char(string='Display name')

    route_id = fields.Many2one('mail_router.route', string='Mail route')
    field = fields.Selection(selection=[
        ('from', 'From'),
        ('to', 'To'),
        ('body', 'Body'),
    ])
    expression = fields.Char(string='Expression')
    extraction = fields.Char(string='Extraction')
    variable = fields.Char(string='Variable')
