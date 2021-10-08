# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger
import re

_logger = getLogger(__name__)
_var_pattern = re.compile(r'{([\w_]+)}')


class MailRouterFieldMapper(models.Model):
    _name = 'mail_router.field_mapper'

    name = fields.Char(string='Name', related='field.model')

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

                if not field_mapper.variables:
                    field_mapper.variables = field_mapper.template[:10]

                    if len(field_mapper.template) > 10:
                        field_mapper.variables += '...'

    @api.multi
    def map(self, varialbes):
        fields_dict = {}
        # remove None values
        varialbes = {key: value for key, value in varialbes.items() if value is not None}

        for mapper in self:
            try:
                value = mapper.template.format(**varialbes)
            except (IndexError, KeyError) as error:
                value = mapper.default

                _logger.error(u'Error during extract values from field ``%s`` for index/name ``%s``',
                    mapper.field.name, str(error))

            fields_dict[mapper.field.name] = value

        return fields_dict
