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

from openerp import osv, fields, api, models, _, netsvc, exceptions


class account_check_dreject(models.TransientModel):
    _name = 'account.check.dreject'


    reject_date = fields.Date('Reject Date', required=True)
    expense_account = fields.Many2one('account.account','Expense Account')
    expense_amount = fields.Float('Expense Amount')
    invoice_expense = fields.Boolean('Invoice Expense?')
    make_expense = fields.Boolean('Make Expenses ?')


    @api.one
    def _get_address_invoice(self, partner):
        partner_obj = self.env['res.partner']
        return partner_obj.address_get([partner],['contact', 'invoice'])


    @api.one
    def action_dreject(self):

        record_ids = self._context.get('active_ids', [])
        third_check = self.env['account.third.check']
        check_objs = third_check.browse(record_ids)

        wf_service = netsvc.LocalService('workflow')
        invoice_obj = self.env['account.invoice']
        move_line = self.env['account.move.line']
        invoice_line_obj = self.env['account.invoice.line']
        wizard = self

        period_id = self.env['account.period'].find(wizard.reject_date)[0]

        for check in check_objs:
            if check.state != 'deposited':
                raise exceptions.except_orm('Check %s selected error' % (check.number),
                    'The selected checks must to be in deposited.')
                    
            if not (check.voucher_id.journal_id.default_credit_account_id.id or check.voucher_id.journal_id.default_debit_account_id.id):
                raise exceptions.except_orm('Journal %s selected error' % (check.voucher_id.journal_id.id),
                    'The journal must to be created defaults account for debit and credit.' )
                            
            partner_address = self._get_address_invoice(check.voucher_id.partner_id.id)
            contact_address = partner_address['contact']
            invoice_address = partner_address['invoice']
            invoice_vals = {
                            'name': check.number,
                            'origin': 'Check Rejected Dep Nr. ' + (check.number or '') + ',' + (check.voucher_id.number),
                            'type': 'out_invoice',
                            'account_id': check.voucher_id.partner_id.property_account_receivable.id,
                            'partner_id': check.voucher_id.partner_id.id,
                            'address_invoice_id': invoice_address,
                            'address_contact_id': contact_address,
                            'date_invoice': wizard.reject_date,
                        }

            invoice_id = invoice_obj.create(invoice_vals)
            
            # 'account_id': check.voucher_id.journal_id.default_debit_account_id.id,
            invoice_line_vals = {
                'name': 'Check Rejected Dep Nr. ' + check.number,
                'origin': 'Check Rejected Dep Nr. ' + check.number,
                'invoice_id': invoice_id.id,
                'account_id': check.account_bank_id.account_id.id,
                'price_unit': check.amount,
                'quantity': 1,
            }
            invoice_line_obj.create(invoice_line_vals)
            check.write({'reject_debit_note': invoice_id.id})

            if wizard.make_expense:
                if wizard.invoice_expense:
                    if  wizard.expense_amount != 0.00 and wizard.expense_account:
                        invoice_line_obj.create({
                            'name': 'Check Rejected Dep Expenses Nr. ' + check.number,
                            'origin': 'Check Rejected Dep Nr. ' + check.number,
                            'invoice_id': invoice_id.id,
                            'account_id': wizard.expense_account.id,
                            'price_unit': wizard.expense_amount,
                            'quantity': 1,
                        })
                    else:
                        raise exceptions.except_orm(_('Error'),
                            _('You must assign expense account and amount !'))

                else:
                    if  wizard.expense_amount != 0.00 \
                    and wizard.expense_account:
                        name = self.pool.get('ir.sequence').next_by_id(check.voucher_id.journal_id.sequence_id.id, context=context)
                        move_id = self.pool.get('account.move').create({
                            'name': name,
                            'journal_id': check.voucher_id.journal_id.id,
                            'state': 'draft',
                            'period_id': period_id,
                            'date': wizard.reject_date,
                            'ref': 'Check Rejected Dep Nr. ' + check.number,
                        })  

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': wizard.expense_account.id,
                            'move_id': move_id,
                            'journal_id': check.voucher_id.journal_id.id,
                            'period_id': period_id,
                            'date': wizard.reject_date,
                            'debit': wizard.expense_amount,
                            'credit': 0.0,
                            'ref': 'Check Dep Reject Nr. ' + check.number,
                            'state': 'valid',
                        })

                        move_line.create({
                            'name': name,
                            'centralisation': 'normal',
                            'account_id': check.voucher_id.journal_id.default_credit_account_id.id,
                            'move_id': move_id,
                            'journal_id': check.voucher_id.journal_id.id,
                            'period_id': period_id,
                            'date': wizard.reject_date,
                            'debit': 0.0,
                            'credit': wizard.expense_amount,
                            'ref': 'Check Dep Reject Nr. ' + check.number,
                            'state': 'valid',
                        })
                        move_id.write({
                            'state': 'posted',
                        })

            wf_service.trg_validate('account.third.check', check.id,
                    'deposited_drejected')

        return {}

