# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger


_logger = getLogger(__name__)


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'

    mail_router_route_ids = fields.Many2many(
        'mail_router.route',
        'mail_router_route_fetchmail_server_rel',
        'fetchmail_server_id',
        'mail_router_route_id',
        string='Mail routes'
    )

    mail_router_route_number = fields.Integer(
        'Number mail ruoters',
        compute='_compute_mail_router_route_number')

    @api.multi
    def _compute_mail_router_route_number(self):
        for route in self:
            route.mail_router_route_number = len(route.mail_router_route_ids)

    @api.multi
    def write(self, values):
        write = super(FetchMailServer, self).write(values)

        for server in self:
            if server.object_id.model != 'mail_router.route':
                for route in server.mail_router_route_ids:
                    route.fetchmail_server_ids = route.fetchmail_server_ids - server

        return write

    @api.multi
    def enable_route_model(self):
        self.object_id = self.env['ir.model'].sudo().search([('model', '=', 'mail_router.route')])

    def disable_route_model(self):
        self.object_id = None
