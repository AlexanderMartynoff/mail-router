# -*- coding: utf-8 -*-

from logging import getLogger

from odoo import models, fields, api


logger = getLogger(__name__)


class MailRouterFieldCondition(models.Model):
    _name = 'mail_router.field_condition'

    name = fields.Char(string='Name')
    expression = fields.Char(string='Expression')
    field = fields.Selection(selection=[
        ('from', 'From'),
        ('to', 'To'),
        ('body', 'Body'),
    ])
    mode = fields.Selection(selection=[
        ('match', 'Match'),
        ('not_match', 'Not match'),
    ])
    route_id = fields.Many2one('mail_router.route', string='Mail route')

