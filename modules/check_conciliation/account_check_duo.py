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
# Cambios, rsosa:
#
# - Se agrega un campo booleano para controlar la visualizacion del campo Fecha de Debito (debit_date).
# - El campo 'debit_date' se comento en la clase original y se agrega de nuevo por esta via..
# - Se comenta el campo 'state' de la clase original y se incluye de nuevo aqui con un nuevo estado agregado
#
#
##############################################################################


from openerp import fields, models, api, exceptions



class account_issued_check(models.Model):
    _name = 'account.issued.check'
    _inherit = 'account.issued.check'

    debit_date = fields.Date('Date Debit', invisible=False, states={'draft': [('invisible', True)]})
    reconcile = fields.Boolean('Conciliar?', invisible=False, states={'draft': [('invisible', True)]})
    state = fields.Selection([('draft','Draft'),
                                    ('handed','Handed'),
                                    ('hrejected','Rechazado'),
                                    ('payed','Pagado'),
                                    ('cancel','Cancelled')],
                                   string='State',required=True)
    move_id = fields.Many2one('account.move', 'Asiento contable')
    asiento_conciliado = fields.One2many(related='move_id.line_id', relation='account.move.line', string='Asientos contables', readonly=True)

    @api.multi
    def action_conciliar(self):
        '''
        Metodo para efectuar un nuevo asiento contable que rebaje la cuenta de Banco contra la cuenta
        transitoria, y de esta manera conciliar los saldos de las cuentas bancarias...
        '''

        issued_check_obj = self
        monto = issued_check_obj.amount
        cheq_obj = self.env['account.checkbook']
        cheq_brw = cheq_obj.browse(issued_check_obj.checkbook_id.id)
        if cheq_brw:
            cuenta_deudora = cheq_brw.cuenta_transitoria.id
            cuenta_acreedora = self.env['res.partner.bank'].browse(cheq_brw.account_bank_id.id).account_id.id

        voucher_obj = self.env['account.voucher']
        voucher_brw = voucher_obj.browse(issued_check_obj.voucher_id.id)
        journal_id = voucher_brw.journal_id.id
        period_id = voucher_brw.period_id.id
        vals = {
            'date': issued_check_obj.debit_date,
            'period_id': period_id,
            'journal_id': journal_id,
            'line_id': False,  
        }
        move_obj = self.env['account.move']
        move_id = move_obj.create(vals)

        asiento={
            'account_id': cuenta_deudora, 
            'company_id': 1, 
            'currency_id': False, 
            'date_maturity': False,
            'ref': voucher_brw.number, 
            'period_id': period_id,
            'date': issued_check_obj.debit_date, 
            'partner_id': voucher_brw.partner_id.id, 
            'move_id': move_id.id,
            'name': 'CONCILIACION CHEQUE ' + issued_check_obj.number,
            'journal_id': journal_id, 
            'credit': 0.0, 
            'debit': monto, 
            'amount_currency': 0,
        }
        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(asiento)
        if move_line_id1: move_line_id1.write(asiento)
        asiento['account_id'] = cuenta_acreedora
        asiento['credit'] = monto
        asiento['debit'] = 0.0
        move_line_id2 = move_line_obj.create(asiento)
        if move_line_id2: move_line_id2.write(asiento)
        if move_line_id1 and move_line_id2:
            res = {'state': 'payed',
                   'move_id': move_id.id,}
            #issued_check_obj.write(cr, uid, ids, res, context=None)
            self.write(res)
        
        return True
