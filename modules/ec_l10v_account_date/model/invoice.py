# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api ,models
from datetime import date
import time
_DATETIME_FORMAT = "%Y-%m-%d"
class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    _defaults = {
        'date_document':False,
        'date_invoice':False
    }

    @api.multi
    def invoice_validate(self):
        res = {}
        res = {
            'state': 'open',
            'date_document':date.today()
        }
        return self.write(res)




