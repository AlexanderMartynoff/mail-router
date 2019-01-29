# -*- coding: utf-8 -*-

import re
from logging import getLogger
from odoo import models, fields, api
from collections import defaultdict
from lxml.html import document_fromstring


_logger = getLogger(__name__)

def _split_and_strip(expression):
    return [_.strip() for _ in expression.split(',')]


class MailRouterFieldParser(models.Model):
    _name = 'mail_router.field_parser'

    name = fields.Char(string='Name', related='route_id.name')

    route_id = fields.Many2one('mail_router.route', string='Mail route', required=True)
    field = fields.Selection(selection=[
        ('from', 'From'),
        ('to', 'To'),
        ('body', 'Body'),
        ('bodyplain', 'Plain body'),
        ('date', 'Date'),
        ('subject', 'Subject'),
    ], string='Field', required=True)
    strict = fields.Boolean(string='Strict', default=False)
    expression = fields.Char(string='Expression', required=True)
    extraction = fields.Char(string='Extraction', required=True)
    variable = fields.Char(string='Variable', required=True)

    @api.multi
    def parse(self, msg_dict):
        variables_dict = {}

        for parser in self:

            def search(*args, **kwargs):
                return re.match(*args, **kwargs) if parser.strict else re.search(*args, **kwargs)
            
            if parser.field in msg_dict:
                match = search(parser.expression, msg_dict[parser.field], re.M | re.S | re.U)
                
                variables = _split_and_strip(parser.variable)
                extractions = _split_and_strip(parser.extraction)

                for position, variable in enumerate(variables):
                    if match is None:
                        value = None
                    else:
                        try:
                            value = match.expand(extractions[position])
                        except (re.error, IndexError):
                            value = None

                            _logger.error(u'Error during extract values from mail field ``%s`` for variable ``%s`` - %s',
                                parser.field, parser.variable, str(re.error))

                    variables_dict[variable] = value

        return variables_dict
