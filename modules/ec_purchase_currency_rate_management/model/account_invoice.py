# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.osv import osv
from openerp.exceptions import except_orm
from datetime import time

class account_invoice(models.Model):
    
    _inherit = 'account.invoice'
    
    date_currency =     fields.Date('Currency Rate Date')
    res_currency_rate = fields.Float('Rate', digits=(6,6), readonly=True, store=True)
    flag_currency =     fields.Boolean('Flag Currency', default=False)
    
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        company_currency = self.company_id.currency_id.id
        if self.currency_id.id != company_currency: self.flag_currency = True
        else: self.flag_currency = False
    
    @api.onchange('date_currency')
    def onchange_date_currency(self):
        warn = {}
        company_currency = self.company_id.currency_id.id
        if self.currency_id and self.currency_id.id != company_currency:
            rate_list_ids = self.env['res.currency.rate'].search([('currency_id','=', self.currency_id.id),('name','ilike', str(self.date_currency) + '%')])
            if len(rate_list_ids) > 1:
                warn = {'title': 'Error de Validacion', 'message': 'Se encontro mas de una tasa para la fecha especificada. Debe haber solo una tasa por dia.  Comuniquese con el departamento de Contabilidad'}
                self.date_currency = False
                self.res_currency_rate = False
            elif len(rate_list_ids) == 1:
                if rate_list_ids.rate > 0.0:
                    self.res_currency_rate = rate_list_ids.rate
                else:
                    warn = {'title': 'Error de Validacion', 'message': 'La tasa registrada en la fecha indicada no es válida, se le recomienda contactar al departamento de contabilidad'}
            elif len(rate_list_ids) == 0:
                self.date_currency = False
                self.res_currency_rate = False
                warn = {'title': 'Error de Validacion', 'message': 'La fecha ingresada no esta registrada en la moneda configurada en la tarifa de compra.  Seleccione una fecha distinta o contacte al departamento de Contabilidad'}
        return {'warning': warn}
    
    @api.multi
    def compute_invoice_totals(self,inv, company_currency, ref, invoice_move_lines):
        total = 0
        total_currency = 0
        date_currency = inv.type == 'in_invoice' and inv.flag_currency and inv.date_currency or False
        #cur_obj = self.env['res.currency']
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency.id: #Modified
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
                i['price'] = date_currency and round(i['price'] * inv.res_currency_rate, 4) or \
                             cur_obj.compute(self.env.cr, self.env.uid, inv.currency_id.id,
                                             company_currency.id, i['price'],
                                             context={'date': date_currency or inv.date_invoice or time.strftime('%Y-%m-%d')})
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund', 'out_debit'):  # Modified
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)
            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund', 'in_debit'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = inv.number
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(inv, company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        #_13DIC2016_rsosa:
                        #amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                        amount_currency = total_currency
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref,
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
 
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)
            #_30NOV2016_rsosa: agregar campo de la Tasa y modificar la columna Importe impuestos/base
            if diff_currency and inv.type == 'in_invoice' and inv.flag_currency:
                for tpl in line:
                    tpl[2]['tax_amount'] = (tpl[2]['tax_amount'] > 0 and tpl[2]['debit']) or (tpl[2]['tax_amount'] > 0 and tpl[2]['credit'])
                    tpl[2]['rate_currency'] = inv.res_currency_rate
            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'type': entry_type,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv # Modified rsosa
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
    
    def ret_and_reconcile(self, cr, uid, ids, pay_amount, pay_account_id,
                          period_id, pay_journal_id, writeoff_acc_id,
                          writeoff_period_id, writeoff_journal_id, date,
                          name, to_wh, context=None):
        """ Make the payment of the invoice
        """
        #if context is None:
        #    context = {}
        ctx = isinstance(context, dict) and context.copy() or {}
        rp_obj = self.pool.get('res.partner')

        # TODO check if we can use different period for payment and the
        # writeoff line
        assert len(ids) == 1, "Can only pay one invoice at a time"
        invoice = self.browse(cr, uid, ids[0])
        src_account_id = invoice.account_id.id
        flag = invoice.flag_currency or False
        rate_c = flag and invoice.res_currency_rate or 0.0

        # Take the seq as name for move
        types = {'out_invoice': -1,
                 'in_invoice': 1,
                 'out_refund': 1, 'in_refund': -1}
        direction = types[invoice.type]
        l1 = {
            'debit': direction * pay_amount > 0 and direction * pay_amount,
            'credit': direction * pay_amount < 0 and - direction * pay_amount,
            'account_id': src_account_id,
            'partner_id': rp_obj._find_accounting_partner(
                invoice.partner_id).id,
            'ref': invoice.number,
            'date': date,
            'currency_id': False,
            'name': name,
            'rate_currency': rate_c 
        }
        lines = [(0, 0, l1)]

        l2 = self._get_move_lines(
            cr, uid, ids, to_wh, period_id, pay_journal_id, writeoff_acc_id,
            writeoff_period_id, writeoff_journal_id, date,
            name, context=ctx)
        
        # TODO: check the method _get_move_lines that is forced to return []
        # and that makes that aws_customer.yml test cause a error
        if not l2:
            raise osv.except_osv(
                _('Warning !'),
                _('No accounting moves were created.\n Please, Check if there'
                  ' are Taxes/Concepts to withhold in the Invoices!'))
        #_16DIC2016_rsosa:
        elif flag and l2:
            for elem in l2:
                elem[2]['rate_currency'] = rate_c 
        #rsosa: ID 57
        deb = l2[0][2]['debit']
        cred = l2[0][2]['credit']
        if deb < 0: l2[0][2].update({'debit': deb * direction})
        if cred < 0: l2[0][2].update({'credit': cred * direction})
        lines += l2

        move = {'ref': invoice.number, 'line_id': lines,
                'journal_id': pay_journal_id, 'period_id': period_id,
                'date': date}
        move_id = self.pool.get('account.move').create(cr, uid, move,
                                                       context=ctx)

        self.pool.get('account.move').post(cr, uid, [move_id])

        line_ids = []
        total = 0.0
        line = self.pool.get('account.move.line')
        cr.execute(
            'select id'
            ' from account_move_line'
            ' where move_id in (' + str(move_id) + ',' +
            str(invoice.move_id.id) + ')')
        lines = line.browse(cr, uid, [item[0] for item in cr.fetchall()])
        for aml_brw in lines + invoice.payment_ids:
            if aml_brw.account_id.id == src_account_id:
                line_ids.append(aml_brw.id)
                total += (aml_brw.debit or 0.0) - (aml_brw.credit or 0.0)
        if (not round(total, self.pool.get('decimal.precision').precision_get(
                cr, uid, 'Withhold'))) or writeoff_acc_id:
            self.pool.get('account.move.line').reconcile(
                cr, uid, line_ids, 'manual', writeoff_acc_id,
                writeoff_period_id, writeoff_journal_id, ctx)
        else:
            self.pool.get('account.move.line').reconcile_partial(
                cr, uid, line_ids, 'manual', ctx)

        # Update the stored value (fields.function), so we write to trigger
        # recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {},
                                               context=ctx)
        return {'move_id': move_id}



class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
    
    
    @api.model
    def move_line_get(self, invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        #_28NOV2016_rsosa: correccion de la manera en que es instanciado el objeto currency
        #currency = inv.currency_id.with_context(date=inv.date_invoice)
        currency = self.env['res.currency'].browse(inv.currency_id.id)
        #company_currency = inv.company_id.currency_id

        res = []
        for line in inv.invoice_line:
            mres = self.move_line_get_item(line)
            mres['invl_id'] = line.id
            res.append(mres)
            tax_code_found = False
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(dict(mres))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, currency)

        return res

class account_invoice_tax(models.Model):
    _inherit = 'account.invoice.tax'
    
    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_currency or invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        #_28NOV2016_rsosa:
        flag = invoice.type == 'in_invoice' and invoice.flag_currency or False  
        rate = flag and invoice.res_currency_rate or 1.0
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                    'tax_id': tax['id']
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    #val['id'] = tax['id']
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = flag and round((val['base'] * tax['base_sign']) * rate, 2) or \
                                         currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = flag and round((val['amount'] * tax['tax_sign']) * rate, 2) or \
                                        currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = flag and round((val['base'] * tax['ref_base_sign']) * rate, 2) or \
                                         currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = flag and round((val['amount'] * tax['ref_tax_sign']) * rate, 2) or \
                                        currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                #key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                #key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['id'])
                key = val['tax_id']
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped
