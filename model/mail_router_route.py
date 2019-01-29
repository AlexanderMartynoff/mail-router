# -*- coding: utf-8 -*-

from logging import getLogger
from lxml.html import document_fromstring
import psycopg2
from re import sub
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = getLogger(__name__)


def _cleanup_text(value):
    for pattern, replace in ('\n\s*', '\n'), (' +', ' '):
        value = sub(pattern, replace, value)

    return value

class MailRouterRoute(models.Model):
    _name = 'mail_router.route'
    _order = 'sequence, id asc'
    _description = 'Extended mail message routing'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    model = fields.Char(string='Model', related='model_id.model')
    field_condition_ids = fields.One2many('mail_router.field_condition', 'route_id', string='Field conditions')
    field_parser_ids = fields.One2many('mail_router.field_parser', 'route_id', string='Field parsers')
    field_mapper_ids = fields.One2many('mail_router.field_mapper', 'route_id', string='Field mappers')
    mode = fields.Selection(selection=[
        ('all', 'All'),
        ('any', 'Any'),
        ('fallback', 'Fallback'),
    ], default='all')
    sequence = fields.Integer(string="Sequence")
    priority = fields.Integer(string="Priority", related='sequence')
    fetchmail_server_ids = fields.Many2many(
        'fetchmail.server',
        'mail_router_route_fetchmail_server_rel',
        'mail_router_route_id',
        'fetchmail_server_id',
        string='Mail servers',
    )
    before_mail_router_snippet_item_ids = fields.One2many(
        'mail_router.snippet_item', 'before_route_id', string='Before code snipets')
    after_mail_router_snippet_item_ids = fields.One2many(
        'mail_router.snippet_item', 'after_route_id', string='After code snipets')

    @api.multi
    def write(self, values):
        write = super(MailRouterRoute, self).write(values)

        for route in self:
            for server in route.fetchmail_server_ids:
                server.enable_route_model()

        return write

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        fetchmail_server_id = self.env['fetchmail.server'] \
            .sudo() \
            .browse(self._context.get('fetchmail_server_id', 0))

        if fetchmail_server_id.exists():
            for route in fetchmail_server_id.mail_router_route_ids.sorted():

                if route.active:
                    try:
                        record = route._routing({key: value for key, value in msg_dict.items()})
                    except Exception as error:
                        if isinstance(error, psycopg2.IntegrityError):
                            self.env.cr.rollback()

                        _logger.exception(error)
                    else:
                        if record:
                            _logger.info('Successfully created record ``%s`` from route ``%s``',
                                record, route)
                            break

    @api.multi
    def _routing(self, msg_dict):
        """
        Contains all steps for processing incoming mail message
        """
        
        self.ensure_one()

        if 'body' in msg_dict.keys():
            msg_dict.update(bodyplain=_cleanup_text(
                document_fromstring(msg_dict['body']).text_content()))
        
        # 1. Check conditions
        if self._check_conditions(msg_dict):

            # 2. Extract variables from message
            variables = self._extract_variables(msg_dict)
            # 3. Extract mapping form variables
            values = self._extract_values(variables)
            # 4. Resolve values for create method
            record_dict = self._evaluate_record_dict(values)
            # 5. Optional record pre-processing with snippet
            self.before_mail_router_snippet_item_ids.eval({
                'model_id': self.model_id,
                'variables': variables,
                'record_dict': record_dict,
            })
            # 6. Create a record
            record = self.env[self.model_id.model].create(record_dict)
            # 7. Optional record post-processing with snippet
            self.after_mail_router_snippet_item_ids.eval({
                'model_id': self.model_id,
                'variables': variables,
                'record': record,
                'record_dict': record_dict,
            })

            return record

    @api.multi
    def _check_conditions(self, msg_dict):
        """
        :type msg_dict: dict
        :rtype: bool
        """

        self.ensure_one()

        if self.mode == 'fallback':
            return True

        # False if empty
        if not self.field_condition_ids.exists():
            return False

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

        return self.field_parser_ids.parse(msg_dict)

    @api.multi
    def _extract_values(self, variables):
        """
        :type variables: dict 
        :rtype: dict
        """

        self.ensure_one()

        return self.field_mapper_ids.map(variables)

    @api.multi
    def _evaluate_record_dict(self, values):
        """
        Apply type cast and evaluating for raw variables

        :type values: dict
        :description: 
            https://doc.odoo.com/v6.0/developer/2_5_Objects_Fields_Methods/methods.html#osv.osv.osv.write
        """

        self.ensure_one()

        error_text = u'Fields ``%s`` with type ``%s`` cannot be filled'

        record_dict = {}
        model_fields = self.env[self.model]._fields

        # safe_eval
        def _safe_eval(code):
            try:
                return safe_eval(code)
            except Exception as error:
                _logger.exception(error)

            return None

        for key, value in values.items():
            if key in model_fields:
                field = model_fields[key]
                
                # Special case for ``Many2one`` and  ``Many2many``
                if isinstance(field, (fields.Many2one, fields.Many2many)):
                    if isinstance(value, basestring):
                        record_value = _safe_eval(value)
                    else:
                        record_value = value
                # Special case for ``Datetime/Date``
                elif isinstance(field, (fields.Date, fields.Datetime)):
                    record_value = None
                    _logger.error(error_text, key, u'Date/Datetime')
                # Raise an exception for unsupported types
                elif isinstance(field, fields.One2many):
                    record_value = None
                    _logger.error(error_text, key, u'One2many')
                # Fallback for others cases, left it as is
                else:
                    record_value = value

                record_dict[key] = record_value

        return record_dict

