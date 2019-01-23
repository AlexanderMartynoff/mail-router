# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger


logger = getLogger(__name__)


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
            for route in server.sudo()._search_routes():
                route.fetchmail_server_ids = route.fetchmail_server_ids - server

        return write

    @api.multi
    def _search_routes(self):
        self.ensure_one()

        return self.env['mail_router.route'].search([
            ('fetchmail_server_ids', '=', self.id)
        ])
