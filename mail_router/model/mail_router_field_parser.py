# -*- coding: utf-8 -*-

import re
from logging import getLogger
from odoo import models, fields, api


_logger = getLogger(__name__)


class MailRouterFieldParser(models.Model):
    _name = 'mail_router.field_parser'

    name = fields.Char(string='Name')

    route_id = fields.Many2one('mail_router.route', string='Mail route', required=True)
    field = fields.Selection(selection=[
        ('from', 'From'),
        ('to', 'To'),
        ('body', 'Body'),
        ('date', 'Date'),
        ('subject', 'Subject'),
    ], required=True)
    strict = fields.Boolean(string='Strict', default=False)
    expression = fields.Char(string='Expression', required=True)
    extraction = fields.Char(string='Extraction', required=True)
    variable = fields.Char(string='Variable', required=True)

    @api.one
    def parse(self, msg_dict):

        def search(*args, **kwargs):
            # Use closure for acces ``self``
            return re.match(*args, **kwargs) if self.strict else re.search(*args, **kwargs)

        if self.field in msg_dict:
            match = search(self.expression, msg_dict[self.field], re.M | re.S | re.U)

            if match:
                try:
                    return self.variable, match.expand(self.extraction)
                except (IndexError, KeyError):
                    _logger.error(
                        u'Error during extract values from mail field ``%s`` for variable ``%s``',
                        self.field,
                        self.variable)

        return self.variable, None

