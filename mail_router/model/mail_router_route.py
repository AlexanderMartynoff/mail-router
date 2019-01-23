# -*- coding: utf-8 -*-

from logging import getLogger

from odoo import models, fields, api


logger = getLogger(__name__)


class MailRouterRoute(models.Model):
    _name = 'mail_router.route'

    name = fields.Char(string='Name', related='model_id.display_name')
    active = fields.Boolean(string='Active', default=True)
    cleanup_html = fields.Boolean(string='Cleanup HTML', default=True)
    fetchmail_server_ids = fields.Many2many('fetchmail.server', string='Mail servers')
    model_id = fields.Many2one('ir.model', string='Model')
    field_condition_ids = fields.One2many('mail_router.field_condition', 'route_id', string='Field conditions')
    field_parser_ids = fields.One2many('mail_router.field_parser', 'route_id', string='Field parsers')
    field_mapper_ids = fields.One2many('mail_router.field_mapper', 'route_id', string='Field mappers')

    @api.one
    def write(self, values):
        success = super(MailRouterRoute, self).write(values)

        route_model = self.env['ir.model'].sudo().search([('model', '=', 'mail_router.route')], limit=1)

        for route in self:
            for server in route.fetchmail_server_ids:
                if server.object_id.id != route_model.id:
                    server.object_id = route_model

        used_servers = self.sudo().search([]).mapped('fetchmail_server_ids')

        for server in self.env['fetchmail.server'].sudo().search([]):
            if server not in used_servers:
                server.object_id = None

        return success

