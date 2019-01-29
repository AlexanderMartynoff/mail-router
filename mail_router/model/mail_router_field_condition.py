# -*- coding: utf-8 -*-

import re
from logging import getLogger
from odoo import models, fields, api


_logger = getLogger(__name__)


class MailRouterFieldCondition(models.Model):
    _name = 'mail_router.field_condition'

    name = fields.Char(string='Name', related='route_id.name')
    expression = fields.Char(string='Expression', required=True)
    field = fields.Selection(selection=[
        ('from', 'From'),
        ('to', 'To'),
        ('body', 'Body'),
        ('bodyplain', 'Plain body'),
        ('date', 'Date'),
        ('subject', 'Subject'),
    ], string='Field', required=True)
    negation = fields.Boolean(string='Negation', default=False)
    strict = fields.Boolean(string='Strict', default=False)
    route_id = fields.Many2one('mail_router.route', string='Mail route')

    @api.one
    def match(self, msg_dict):
        def search(*args, **kwargs):
            return re.match(*args, **kwargs) if self.strict else re.search(*args, **kwargs)

        if self.field in msg_dict:
            match = search(self.expression, msg_dict[self.field], re.M | re.S | re.U)

            if self.negation == True:
                return match is None
            else:
                return match is not None

        return False
