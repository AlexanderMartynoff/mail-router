# -*- coding: utf-8 -*-

from logging import getLogger
from textwrap import dedent
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


_logger = getLogger(__name__)


class MailRouterSnippet(models.Model):
    _name = 'mail_router.snippet'

    name = fields.Char(string='Name', required=True)
    code = fields.Text(string='Code', required=True, default=
        '# Available variables:\r\n'
        '# - `record`: singleton `recordset` that was created, only for post-processing snippets\r\n'
        '# - `record_dict`: python `dict` that used for `record` creating\r\n'
        '# - `variables`: python `dict` that filled with varialbles extracted\r\n'
        '# - `model_id`: singleton `recordset` of type `ir.model` that used as factory for record'
    )

    @api.multi
    def eval(self, global_context):
        safe_eval(self.code.strip(), global_context, mode="exec", nocopy=True)


class MailRouterSnippet(models.Model):
    _name = 'mail_router.snippet_item'

    name = fields.Char(related='snippet_id.name')
    sequence = fields.Integer(name='Sequence')
    snippet_id = fields.Many2one('mail_router.snippet', string='Snippet', required=True)
    before_route_id = fields.Many2one('mail_router.route', string='Mail route before')
    after_route_id = fields.Many2one('mail_router.route', string='Mail route after')

    @api.multi
    def eval(self, global_context):
        for snippet_item in self:
            if snippet_item.snippet_id.exists():
                try:
                    snippet_item.snippet_id.eval(global_context)
                except Exception as error:
                    _logger.exception(error)
            
