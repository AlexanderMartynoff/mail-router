# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger


logger = getLogger(__name__)


class MailRouterRoute(models.Model):
    _name = 'mail_router.route'

    name = fields.Char(string='Name', related='model_id.display_name')
    active = fields.Boolean(string='Active', default=True)
    cleanup_html = fields.Boolean(string='Cleanup HTML', default=True)
    model_id = fields.Many2one('ir.model', string='Model')
    field_condition_ids = fields.One2many('mail_router.field_condition', 'route_id', string='Field conditions')
    field_parser_ids = fields.One2many('mail_router.field_parser', 'route_id', string='Field parsers')
    field_mapper_ids = fields.One2many('mail_router.field_mapper', 'route_id', string='Field mappers')

    fetchmail_server_ids = fields.Many2many(
        'fetchmail.server',
        'mail_router_route_fetchmail_server_rel',
        'mail_router_route_id',
        'fetchmail_server_id',
        string='Mail servers'
    )
