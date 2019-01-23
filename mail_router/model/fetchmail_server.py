# -*- coding: utf-8 -*-

from logging import getLogger

from odoo import models, fields, api


logger = getLogger(__name__)


class FetchMailServer(models.Model):
    _inherit = 'fetchmail.server'


    @api.multi
    def write(self, values):
        success = super(FetchMailServer, self).write(values)

        route_model =  self.env['ir.model'].sudo().search([('model', '=', 'mail_router.route')], limit=1)

        for server in self:
            if server.object_id.id != route_model.id:
                for route in self.env['mail_router.route'].sudo().search([('fetchmail_server_ids', '=', server.id)]):
                    route.fetchmail_server_ids = route.fetchmail_server_ids - server

        return success

