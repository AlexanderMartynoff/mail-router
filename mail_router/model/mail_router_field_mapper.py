# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger
import re

_logger = getLogger(__name__)
_var_pattern = re.compile('{([\w_]+)}')


class MailRouterFieldMapper(models.Model):
    _name = 'mail_router.field_mapper'

    name = fields.Char(string='Name')

    route_id = fields.Many2one('mail_router.route', string='Mail route', required=True)
    field = fields.Many2one('ir.model.fields', string='Model field', required=True)
    template = fields.Char(string='Template', required=True)
    default = fields.Char(string='Default')
    variables = fields.Char(string='Variables', compute='_compute_varialbes')

    @api.depends('template')
    def _compute_varialbes(self):
        for field_mapper in self:
            if field_mapper.template:
                field_mapper.variables = ', '.join(_var_pattern.findall(field_mapper.template))

    @api.one
    def evaluation(self, varialbes):
        try:
            return self.field.name, self.template.format(**varialbes)
        except (IndexError, KeyError) as error:
            _logger.error(u'Error during extract values from field ``%s`` for index/name ``%s``',
                self.field.name, str(error))

        return self.field.name, self.default
