# -*- coding: utf-8 -*-

from logging import getLogger
from textwrap import dedent
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval, test_python_expr


logger = getLogger(__name__)


class MailRouterSnippet(models.Model):
    _name = 'mail_router.snippet'

    name = fields.Char(string='Name', required=True)
    code = fields.Text(string='Code', required=True, default='# write your here')
    sequence = fields.Integer(string='Sequence')

    @api.multi
    def eval(self, context):
        safe_eval(self.code.strip(), context, mode="exec", nocopy=True)
