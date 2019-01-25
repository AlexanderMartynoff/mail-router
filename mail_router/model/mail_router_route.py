# -*- coding: utf-8 -*-

from odoo import models, fields, api
from logging import getLogger
from lxml.html import document_fromstring


_logger = getLogger(__name__)


class MailRouterRoute(models.Model):
    _name = 'mail_router.route'

    name = fields.Char(string='Name', related='model_id.display_name')
    active = fields.Boolean(string='Active', default=True)
    cleanup_html = fields.Boolean(string='Cleanup HTML', default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    model = fields.Char(string='Model', related='model_id.model')
    field_condition_ids = fields.One2many('mail_router.field_condition', 'route_id', string='Field conditions')
    field_parser_ids = fields.One2many('mail_router.field_parser', 'route_id', string='Field parsers')
    field_mapper_ids = fields.One2many('mail_router.field_mapper', 'route_id', string='Field mappers')
    mode = fields.Selection(selection=[
        ('all', 'All'),
        ('any', 'Any'),
    ], default='all')

    fetchmail_server_ids = fields.Many2many(
        'fetchmail.server',
        'mail_router_route_fetchmail_server_rel',
        'mail_router_route_id',
        'fetchmail_server_id',
        string='Mail servers',
    )

    mail_router_snippet_id = fields.Many2one('mail_router.snippet',string='Code snipet',)

    @api.one
    def write(self, values):
        write = super(MailRouterRoute, self).write(values)

        for server in self.env['fetchmail.server'].sudo().search([]):
            if server in self.search([]).mapped('fetchmail_server_ids'):
                server.enable_route_model()
            else:
                server.disable_route_model()

        return write

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        fetchmail_server_id = self.env['fetchmail.server'] \
            .sudo() \
            .browse(self._context.get('fetchmail_server_id', 0))

        if fetchmail_server_id.exists():
            for route in fetchmail_server_id.mail_router_route_ids:

                if route.active:
                    try:
                        record = route._routing(msg_dict)
                    except Exception as error:
                        _logger.exception(error)
                    else:
                        _logger.info('Success created record ``%s`` from route ``%s``', record, route)

    @api.multi
    def _routing(self, msg_dict):
        """
        Contains all steps for processing incoming mail message
        """
        
        self.ensure_one()

        if self.cleanup_html and 'body' in msg_dict:
            msg_dict.update(body=document_fromstring(msg_dict['body']).text_content())
        
        # 1. Check conditions
        if self._check_conditions(msg_dict):
            # 2. Extract variables from message
            variables = self._extract_variables(msg_dict)

            # 3. Extract mapping form variables
            values = self._extract_values(variables)

            # 4. Resolve values for create method
            record_dict = self._resolve_record_dict(values)

            # 5. Create a record
            record = self.env[self.model_id.model].create(record_dict)

            # 6. Record post processing with snippet
            if self.mail_router_snippet_id.exists():

                try:
                    self.mail_router_snippet_id.eval({
                        'record': self
                    })
                except RuntimeError as error:
                    _logger.exception(error)

            return record

    @api.multi
    def _check_conditions(self, msg_dict):
        """
        :type msg_dict: dict
        :rtype: bool
        """

        self.ensure_one()

        match = self.field_condition_ids.match(msg_dict)

        if self.mode == 'all':
            return all(match)
        elif self.mode == 'any':
            return any(match)

    @api.multi
    def _extract_variables(self, msg_dict):
        """
        :type msg_dict: dict 
        :rtype: dict
        """

        self.ensure_one()

        return {
            k: v for k, v in self.field_parser_ids.parse(msg_dict)
        }

    @api.multi
    def _extract_values(self, variables):
        """
        :type variables: dict 
        :rtype: dict
        """

        self.ensure_one()

        return {
             k: v for k, v in self.field_mapper_ids.evaluation(variables)
        }

    @api.multi
    def _resolve_record_dict(self, values):
        """
        :type values: dict
        :description: 
            https://doc.odoo.com/v6.0/developer/2_5_Objects_Fields_Methods/methods.html#osv.osv.osv.write
        """

        self.ensure_one()

        error_text = 'Fields with type ``%s`` cannot be filled'

        record_dict = {}
        model_fields = self.env[self.model]._fields

        def to_int(_):
            try:
                return int(_)
            except (ValueError, TypeError):
                pass

        for key, value in values.items():
            if key in model_fields:
                field = model_fields[key]

                # 1. Special case for ``Many2one``
                if isinstance(field, fields.Many2one):
                    record_value = to_int(value)
                # 2. Special case for ``Datetime/Date``
                elif isinstance(field, fields.Date) or isinstance(field, fields.Datetime):
                    raise NotImplementedError(error_text % 'Date/Datetime')
                # 3. Raise an exception for unsupported types
                elif isinstance(field, (fields.One2many, fields.Many2many)):
                    raise NotImplementedError(error_text % 'One2many/Many2many')
                # 4. Fallback for others cases, left it as is
                else:
                    record_value = value

                record_dict[key] = record_value

        return record_dict

