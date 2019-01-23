# -*- coding: utf-8 -*-

from logging import getLogger

from odoo import models, fields, api


logger = getLogger(__name__)


class MailRouterFieldMapper(models.Model):
    _name = 'mail_router.field_mapper'

    name = fields.Char(string='Name')

    route_id = fields.Many2one('mail_router.route', string='Mail route')
    field = fields.Many2one('ir.model.fields', string='Model field')
    variable = fields.Char(string='Variable')
    template = fields.Text(string='Template')
    mode = fields.Selection(selection=[
        ('template', 'Template'),
        ('variable', 'Variable'),
    ])

