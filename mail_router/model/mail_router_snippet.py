# -*- coding: utf-8 -*-

from logging import getLogger
from textwrap import dedent

from odoo import models, fields, api


logger = getLogger(__name__)


class MailRouterSnippet(models.Model):
    _name = 'mail_router.snippet'

    name = fields.Char(string='Name', required=True)
    code = fields.Text(string='Code', required=True, default='returned = None')

    @api.multi
    def eval(self, context):
        return
