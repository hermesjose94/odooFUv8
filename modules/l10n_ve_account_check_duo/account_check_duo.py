# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
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


from openerp import models, fields, api, exceptions, _
import logging
import time
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _
from datetime import datetime

class account_issued_check(models.Model):

    @api.multi
    @api.returns('account.checkbook') #, lambda r: r.id
    def _get_checkbook_id(self):

        checkbook_pool = self.env['account.checkbook']

        res = checkbook_pool.search([('state', '=', 'active')],)

        if res: return res
        else: return False


    _name = 'account.issued.check'
    _description = 'Manage Checks Issued'


    number = fields.Char('Check Number', size=8, required=True,select=True,readonly=True,states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount Check', required=True,readonly=True,states={'draft': [('readonly', False)]})
    date = fields.Date('Date Check', required=True,readonly=True,states={'draft': [('readonly', False)]})
    debit_date = fields.Date('Date Debit', readonly=True) # clearing date + clearing
    receiving_partner_id = fields.Many2one('res.partner','Destiny Partner' ,readonly=True,states={'draft': [('readonly', False)]})
    clearing = fields.Selection((
            ('24', '24 hs'),
            ('48', '48 hs'),
            ('72', '72 hs'),
        ), 'Clearing',readonly=True,states={'draft': [('readonly', False)]})
    account_bank_id = fields.Many2one('res.partner.bank','Account Bank',required=True,readonly=True,states={'draft': [('readonly', False)]})
    voucher_id = fields.Many2one('account.voucher', 'Voucher')
    issued = fields.Boolean('Issued')
    user_id = fields.Many2one('res.users','User')
    change_date = fields.Date('Change Date', required=True)
    clearing_date = fields.Date('Clearing Date', required=True,readonly=True,states={'draft':[('readonly',False)]})
    state =fields.Selection([('draft','Draft'),
                                ('handed','Handed'),
                                 ('hrejected','Hand-Rejected'),
                                 ('cancel','Cancelled')],
                                string='State',required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,readonly=True,states={'draft':[('readonly',False)]}, select=1, help="Company related to this Check")
    reject_debit_note = fields.Many2one('account.invoice','Reject Debit Note')
    checkbook_id = fields.Many2one('account.checkbook','Checkbook',readonly=True,required=True,states={'draft': [('readonly', False)]})


    _sql_constraints = [('number_check_uniq','unique(number,account_bank_id)','The number must be unique!')]
    _order = "number"
    _defaults = {
        'clearing': lambda *a: '48',
        'state': 'draft',
        'change_date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda s, cr, u, c: u,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'checkbook_id': _get_checkbook_id,
    }

    @api.model
    def unlink(self):
        res= {}
        for order in self:
            if order.state not in ('draft'):
                raise exceptions.except_orm(_('Error !'), _('The Check must  be in draft state only for unlink !'))

        return res

    @api.model
    def create(self, vals):
        order_obj= self.env['account.voucher']
        order_id = vals.get('voucher_id', self._context.get('active_ids', []))

        if not order_obj.browse(order_id):
            raise exceptions.except_orm(_('Error !'), _('The Check must be create on one payment !'))
            return res

        checkbook_obj = self.env['account.checkbook']
        num = vals['checkbook_id']
        book = checkbook_obj.browse(num)

        hasta = actual=0
        actual= int(book.actual_number)
        hasta= int(book.range_hasta)
        if actual == hasta:
            book.write({'state': 'used',})
        else:
            if str(book.actual_number) < str(book.range_hasta):
                sum_actual_number = int(book.actual_number) + 1
                book.write({'actual_number': str(sum_actual_number)})

        vals['account_bank_id'] = book.account_bank_id.id
        res = super(account_issued_check, self).create(vals)
        return res

    @api.multi
    def onchange_checkbook_id(self, number, checkbook_id):
        result = {}
        if checkbook_id:
            res = self.env['account.checkbook'].browse([checkbook_id])

            #Busca la chequera activa de acuerdo a la cuenta
            if not res.id:
                result = {'value':{'checkbook_id': None, 'number': None}}
                result.update({'warning': {'title': _('Error !'), 'message': _('You must be create a checkbook or change state')}})
                return result

            if res.state != 'active':
                result = {'value':{'checkbook_id': False}}
                result.update({'warning': {'title': _('Error !'), 'message': _('The Checkbook is not active')}})
            else:
                result = {'value':{'number': str(res.actual_number)}}

        return result

    @api.multi
    def onchange_number(self, number):
        res = {}
        if number:
            number_str = str(number)
            if len(number_str) != 8:
                res = {'value':{'number': False}}
                res.update({'warning': {'title': _('Error !'), 'message': _('Ckeck Number must be 8 numbers !')}})
            else:
    
                res = {'value':{'number': number}}
        return res

    @api.multi
    def onchange_clearing_date(self, date, clearing_date):
        res = {}
        if clearing_date < date:
            res = {'value':{'clearing_date': None}}
            res.update({'warning': {'title': _('Error !'), 'message': _('Clearing date must be greater than check date')}})
        else:
            res = {'value':{'clearing_date': clearing_date}}
        return res

    @api.multi
    def wkfw_draft(self):
        return self.write({'state':'draft'})

    @api.multi
    def wkfw_handed(self):
        for check in self:
            current_date = datetime.now().strftime('%Y-%m-%d')
            check.write({
                'state': 'handed',
                'change_date': current_date,
                'user_id':self.env.user.id,
                 })
        return True

    @api.multi
    def wkfw_hrejected(self):
        # TODO: Ejecutar el armado de nota de debito por cheque rechazado!
        # Ver si el cheque fue emitido por la empresa, si es asi deberia generar
        # una nota de credito al proveedor.
        for check in self:
            current_date = datetime.now().strftime('%Y-%m-%d')
            check.write({
                'state': 'hrejected',
                'change_date': current_date,
                'user_id':self.user.id
                 })
        return True

    @api.multi
    def wkfw_cancel(self):
        for check in self:
            current_date = datetime.now().strftime('%Y-%m-%d')
            check.write({
                'state': 'cancel',
                'change_date': current_date,
                'user_id':self.user.id
                 })
        return True

class account_third_check(models.Model):


    _name = 'account.third.check'
    _description = 'Manage Checks Third'

    number = fields.Char('Check Number', size=8, required=True,readonly=True,states={'draft': [('readonly', False)]})
    sequence_number = fields.Char('Id Number', size=40,readonly=True)
    amount = fields.Float('Check Amount', required=True,readonly=True,states={'draft':[('readonly',False)]})
    date_in = fields.Date('Date In', required=True,readonly=True,states={'draft':[('readonly',False)]})
    date = fields.Date('Check Date', required=True,readonly=True,states={'draft':[('readonly',False)]})
    source_partner_id = fields.Many2one('res.partner', 'Source Partner', readonly=True, states={'draft':[('readonly',False)]})
    destiny_partner_id = fields.Many2one('res.partner', 'Destiny Partner',readonly=False, required=False,states={'handed': [('required', True)]})
    state = fields.Selection((
            ('draft', 'Draft'),
            ('holding', 'Holding'),
            ('deposited', 'Deposited'),
            ('drejected', 'Dep-Rejected'),
            ('handed', 'Handed'),
            ('hrejected', 'Hand-Rejected'),
            ('sold', 'Sold'),
        ), 'State', required=True)
    bank_id = fields.Many2one('res.bank', 'Bank', readonly=True,required=True,states={'draft': [('readonly', False)]})
    vat = fields.Char('RIF', size=11,states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users','User')
    change_date = fields.Date('Change Date', required=True)
    clearing_date = fields.Date('Clearing Date', required=True,readonly=True,states={'draft':[('readonly',False)]})
    clearing = fields.Selection((
            ('24', '24 hs'),
            ('48', '48 hs'),
            ('72', '72 hs'),
        ), 'Clearing', readonly=True,states={'draft': [('readonly', False)]})
    account_bank_id = fields.Many2one('res.partner.bank','Destiny Account')
    voucher_id = fields.Many2one('account.voucher', 'Voucher')
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}, select=1, help="Company related to this Check")
    reject_debit_note = fields.Many2one('account.invoice','Reject Debit Note')
    reject_debit_note_prov = fields.Many2one('account.invoice','Reject Debit Note Prov')
    clearing_date_hasta = fields.Date('Clearing Date Hasta', required=False)
    ticket_deposit_id = fields.Many2one('ticket.deposit', string='Ticket Deposit', required=False, readonly=True, states={'draft':[('readonly',False)]})

    _order = "clearing_date"
    _defaults = {
        'state': 'draft',
        'clearing': lambda *a: '48',
        'date_in': lambda *a: time.strftime('%Y-%m-%d'),
        'change_date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda s, cr, u, c: u,
        'company_id': lambda s, cr, u, c: s.env.user.company_id.id,
    }

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        pos = 0
        desde = False
        hasta = False
        while pos < len(args):
            if args[pos][0] == 'clearing_date':
                desde= args[pos][2]
            if args[pos][0] == 'clearing_date_hasta':
                hasta= args[pos][2]
            pos += 1

            if  desde and hasta:

                return super(account_third_check, self).search([('clearing_date', '>', desde),
                                                                     ('clearing_date', '<', hasta),
                                                                    ])

        return super(account_third_check, self).search(args, offset=offset, limit=limit,
                order=order, count=count)

    @api.multi
    def onchange_number(self, number):
        res = {}
        if number:
            if len(number) != 8:
                res = {'value':{'number': '0'}}
                res.update({'warning': {'title': _('Error !'), 'message': _('Ckeck Number must be 8 numbers !')}})
            else:
    
                res = {'value':{'number': number}}
        return res
    @api.multi
    def onchange_clearing_date(self, date,clearing_date):
        res = {}
        if clearing_date < date:
            res = {'value':{'clearing_date': None}}
            res.update({'warning': {'title': _('Error !'), 'message': _('Clearing date must be greater than check date')}})
        else:
            res = {'value':{'clearing_date': clearing_date}}
        return res

    @api.multi
    def onchange_vat(self, vat):
        res = {}
        if not vat:
            res.update({'warning': {'title': _('Error !'), 'message': _('Vat number must be not null !')}})
        else:
            if len(vat) != 11:
                res = {'value':{'vat': None}}
                res.update({'warning': {'title': _('Error !'), 'message': _('Vat number must be 11 numbers !')}})
            else:
                res = {'value':{'vat': vat}}
        return res

    @api.multi
    def unlink(self):
        res= {}
        for order in self:
            if  order.state not in ('draft'):
                raise exceptions.except_orm(_('Error !'), _('The Check must  be in draft state only for unlink !'))
        return res

    @api.multi
    def create(self, vals):
        order_obj= self.pool.get('account.voucher')

        seq_obj_name =  'check.third'
        name = self.pool.get('ir.sequence').get(seq_obj_name)

        vals['sequence_number']= name

        res = super(account_third_check, self).create(vals)
        return res

    @api.multi
    def wkf_draft(self):
        return self.write({'state':'draft'})

    @api.multi
    def wkf_holding(self):
        #Transicion efectuada al validar un pago de cliente que contenga cheque
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:

            if check.voucher_id:
                source_partner_id = check.voucher_id.partner_id.id

            else:
                source_partner_id = None

            check.write({
                    'source_partner_id': source_partner_id,
                    'state': 'holding',
                    'change_date': current_date,
                    'user_id':self.env.user.id
                    })
        return True

    @api.multi
    def wkf_handed(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:
            check.write({
                'state': 'handed',
                'change_date': current_date,
                'user_id':self.env.user.id
                 })
        return True

    @api.multi
    def wkf_hrejected(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:
            check.write({
                'state': 'hrejected',
                'change_date': current_date,
                'user_id':self.env.user.id
                 })
        return True

    @api.multi
    def wkf_deposited(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:
            check.write({
                'state': 'deposited',
                'change_date': current_date,
                'user_id':self.env.user.id
                 })
        return True

    @api.multi
    def wkf_drejected(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:

            check.write({
                'state': 'drejected',
                'change_date': current_date,
                'user_id':self.env.user.id,
                 })
        return True

    @api.multi
    def wkf_sold(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:

            check.write({
                'state': 'sold',
                'change_date': current_date,
                'user_id':self.env.user.id
                 })
        return True

    @api.multi
    def wkf_cancel(self):
        current_date = datetime.now().strftime('%Y-%m-%d')
        for check in self:

            check.write({
                'state': 'cancel',
                'change_date': current_date,
                'user_id':self.env.user.id
                 })
        return True


