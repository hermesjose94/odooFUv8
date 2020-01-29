# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Venezuela.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import logging
import time
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _
from datetime import datetime
from openerp import models, fields, api,exceptions, _

class account_checkbook(osv.osv):

    _name = 'account.checkbook'
    _description = 'Manage Checkbook'

    name = fields.Char('CheckBook Name', size=30, readonly=True, select=True, required=True, states={'draft': [('readonly', False)]})
    range_desde = fields.Char('Check Number Desde', size=8, readonly=True, required=True, states={'draft': [('readonly', False)]})
    range_hasta = fields.Char('Check Number Hasta', size=8, readonly=True, required=True ,states={'draft': [('readonly', False)]})
    actual_number = fields.Char('Next Check Number', size=8, readonly=True, required=True, states={'draft': [('readonly', False)]})
    account_bank_id = fields.Many2one('res.partner.bank','Account Bank', readonly=True, required=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users','User')
    change_date = fields.Date('Change Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'In Use'),
                              ('used', 'Used')], string='State',readonly=True, default='draft')


    _order = "name"

    @api.model
    def unlink(self):
        res = {}
        for order in self.browse(self):

            if order.state not in ('draft'):
                raise exceptions.except_orm(_('Error !'), _('You can drop the checkbook(s) only in  draft state !'))
                return False
        return res

    @api.onchange('range_desde')
    def onchange_desde(self):
        if self.range_desde:
            if len(self.range_desde) != 8:
                return {
                    'warning': {'title': "Warning", 'message': "Ckeck range desde must be 8 numbers !"},
                }
            else:
                return {'value': {'range_desde': self.range_desde}}
        else:
            return {'value': {'range_desde': '00000000'}}
        

    @api.onchange('range_hasta')
    def onchange_hasta(self):
        if int(self.range_hasta) < int(self.range_desde):
            self.range_hasta = '00000000'
            return {
                'warning': {'title': "Warning", 'message': "Range hasta must be greater than range desde!"},
            }

    @api.model
    def wkf_active(self):
        res= {}
        check_obj= self.env['account.checkbook']
        for order in self:

            if not order.account_bank_id.account_id.id:
                raise exceptions.except_orm(' %s selected error' % (order.account_bank_id.bank.name),
                    'The account must to be created in The Company Bank / Accounting Information.' )

            res = check_obj.search([('account_bank_id', '=', order.account_bank_id.id),
                                              ('state', '=', 'active')],)

            if res:
                raise exceptions.except_orm(_('Error !'), _('You cant change the checkbook´s state, there is one active !'))
                return False

            else:
                self.write({ 'state' : 'active' })
                return True

    @api.model
    def wkf_used(self):
        self.write({ 'state' : 'used' })
        return True

