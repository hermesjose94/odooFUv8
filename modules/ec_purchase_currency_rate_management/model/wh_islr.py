# coding: utf-8
##############################################################################
#

#
# Colaborador: Roger Sosa <rsosa>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields, osv
from datetime import time

class IslrWhDocInvoices(osv.osv):
    _inherit = 'islr.wh.doc.invoices'

    def _amount_all(self, cr, uid, ids, fieldname, args, context=None):
        """ Return all amount relating to the invoices lines
            _13DIC2016_rsosa: changes..
        """
        res = {}
        ut_obj = self.pool.get('l10n.ut')
        for ret_line in self.browse(cr, uid, ids, context):
            flag = ret_line.invoice_id.flag_currency or False
            f_xc = ut_obj.sxc(
                cr, uid,
                ret_line.invoice_id.company_id.currency_id.id,
                ret_line.invoice_id.currency_id.id,
                ret_line.islr_wh_doc_id.date_uid)
            res[ret_line.id] = {
                'amount_islr_ret': 0.0,
                'base_ret': 0.0,
                'currency_amount_islr_ret': 0.0,
                'currency_base_ret': 0.0,
            }
            for line in ret_line.iwdl_ids:
                res[ret_line.id]['amount_islr_ret'] += line.amount
                res[ret_line.id]['base_ret'] += line.base_amount
                #_14DIC2016_rsosa:
                res[ret_line.id]['currency_amount_islr_ret'] += flag and round((line.amount / line.invoice_id.res_currency_rate),4) \
                                                                or f_xc(line.amount)
                if flag:
                    res[ret_line.id]['currency_base_ret'] = line.invoice_id.amount_untaxed
                else:
                    res[ret_line.id]['currency_base_ret'] += f_xc(line.base_amount) 
                

        return res

    #_14DIC2016_rsosa: Se agrega la definicion de estos campos funcionales no para cambiarlos, sino para poder sobreescribir el metodo
    #                          que los alimenta (_amount_all).
    _columns = {
        'amount_islr_ret': fields.function(
            _amount_all, method=True, digits=(16, 2), string='Withheld Amount',
            multi='all', help="Amount withheld from the base amount"),
        'base_ret': fields.function(
            _amount_all, method=True, digits=(16, 2), string='Base Amount',
            multi='all',
            help="Amount where a withholding is going to be compute from"),
        'currency_amount_islr_ret': fields.function(
            _amount_all, method=True, digits=(16, 2),
            string='Foreign Currency Withheld Amount', multi='all',
            help="Amount withheld from the base amount"),
        'currency_base_ret': fields.function(
            _amount_all, method=True, digits=(16, 2),
            string='Foreign Currency Base Amount', multi='all',
            help="Amount where a withholding is going to be compute from"),
    }

    def _get_wh(self, cr, uid, ids, concept_id, context=None):
        """ Return a dictionary containing all the values of the retention of an
        invoice line.
        @param concept_id: Withholding reason
        """
        # TODO: Change the signature of this method
        # This record already has the concept_id built-in
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        iwdl_brw = iwdl_obj.browse(cr, uid, ids[0], context=context)

        ut_date = iwdl_brw.islr_wh_doc_id.date_uid
        ut_obj = self.pool.get('l10n.ut')
        money2ut = ut_obj.compute
        ut2money = ut_obj.compute_ut_to_money

        vendor, buyer, wh_agent = self._get_partners(
            cr, uid, iwdl_brw.invoice_id)
        wh_agent = wh_agent
        apply_income = not vendor.islr_exempt
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)

        concept_id = iwdl_brw.concept_id.id
        # rate_base,rate_minimum,rate_wh_perc,rate_subtract,rate_code,rate_id,
        # rate_name
        # Add a Key in context to store date of ret fot U.T. value
        # determination
        # TODO: Future me, this context update need to be checked with the
        # other date in the withholding in order to take into account the
        # customer income withholding.
        context.update({
            'wh_islr_date_ret':
            iwdl_brw.islr_wh_doc_id.date_uid or
            iwdl_brw.islr_wh_doc_id.date_ret or False
        })
        base = 0
        wh_concept = 0.0

        # Using a clousure to make this call shorter
        f_xc = ut_obj.sxc(
            cr, uid, iwdl_brw.invoice_id.currency_id.id,
            iwdl_brw.invoice_id.company_id.currency_id.id,
            iwdl_brw.invoice_id.date_invoice)

        if iwdl_brw.invoice_id.type in ('in_invoice', 'in_refund'):
            for line in iwdl_brw.xml_ids:
                if line.account_invoice_id.type == 'in_invoice' and line.account_invoice_id.flag_currency:
                    rate_c = line.account_invoice_id.res_currency_rate
                    #base += f_xc(line.account_invoice_line_id.price_subtotal)
                    base += round((line.account_invoice_line_id.price_subtotal * rate_c), 4)
                else:
                    base += f_xc(line.account_invoice_line_id.price_subtotal)

            # rate_base, rate_minimum, rate_wh_perc, rate_subtract, rate_code,
            # rate_id, rate_name, rate2 = self._get_rate(
            #    cr, uid, ail_brw.concept_id.id, residence, nature, base=base,
            #    inv_brw=ail_brw.invoice_id, context=context)
            rate_tuple = self._get_rate(
                cr, uid, concept_id, residence, nature, base=base,
                inv_brw=iwdl_brw.invoice_id, context=context)

            if rate_tuple[7]:
                apply_income = True
                residual_ut = (
                    (rate_tuple[0] / 100.0) * (rate_tuple[2] / 100.0) *
                    rate_tuple[7]['cumulative_base_ut'])
                residual_ut -= rate_tuple[7]['cumulative_tax_ut']
                residual_ut -= rate_tuple[7]['subtrahend']
            else:
                apply_income = (apply_income and
                                base >= rate_tuple[0] * rate_tuple[1] / 100.0)
            wh = 0.0
            subtract = apply_income and rate_tuple[3] or 0.0
            subtract_write = 0.0
            sb_concept = subtract
            for line in iwdl_brw.xml_ids:
                if line.account_invoice_id.type == 'in_invoice' and line.account_invoice_id.flag_currency:
                    #_13DIC2016_rsosa:
                    rate_c = line.account_invoice_id.res_currency_rate
                    #base_line = f_xc(line.account_invoice_line_id.price_subtotal)
                    base_line = round((line.account_invoice_line_id.price_subtotal * rate_c), 4)
                else:
                    base_line = f_xc(line.account_invoice_line_id.price_subtotal)
                base_line_ut = money2ut(cr, uid, base_line, ut_date)
                values = {}
                if apply_income and not rate_tuple[7]:
                    wh_calc = ((rate_tuple[0] / 100.0) *
                               (rate_tuple[2] / 100.0) * base_line)
                    if subtract >= wh_calc:
                        wh = 0.0
                        subtract -= wh_calc
                    else:
                        wh = wh_calc - subtract
                        subtract_write = subtract
                        subtract = 0.0
                    values = {
                        'wh': wh,
                        'raw_tax_ut': money2ut(cr, uid, wh, ut_date),
                        'sustract': subtract or subtract_write,
                    }
                elif apply_income and rate_tuple[7]:
                    tax_line_ut = (base_line_ut * (rate_tuple[0] / 100.0) *
                                   (rate_tuple[2] / 100.0))
                    if residual_ut >= tax_line_ut:
                        wh_ut = 0.0
                        residual_ut -= tax_line_ut
                    else:
                        wh_ut = tax_line_ut + residual_ut
                        subtract_write_ut = residual_ut
                        residual_ut = 0.0
                    wh = ut2money(cr, uid, wh_ut, ut_date)
                    values = {
                        'wh': wh,
                        'raw_tax_ut': wh_ut,
                        'sustract': ut2money(
                            cr, uid, residual_ut or subtract_write_ut,
                            ut_date),
                    }
                values.update({
                    'base': base_line * (rate_tuple[0] / 100.0),
                    'raw_base_ut': base_line_ut,
                    'rate_id': rate_tuple[5],
                    'porcent_rete': rate_tuple[2],
                    'concept_code': rate_tuple[4],
                })
                ixwl_obj.write(cr, uid, line.id, values, context=context)
                wh_concept += wh
        else:
            for line in iwdl_brw.invoice_id.invoice_line:
                if line.concept_id.id == concept_id:
                    base += f_xc(line.price_subtotal)

            rate_tuple = self._get_rate(
                cr, uid, concept_id, residence, nature, base=0.0,
                inv_brw=iwdl_brw.invoice_id, context=context)

            if rate_tuple[7]:
                apply_income = True
            else:
                apply_income = (apply_income and
                                base >= rate_tuple[0] * rate_tuple[1] / 100.0)
            sb_concept = apply_income and rate_tuple[3] or 0.0
            if apply_income:
                wh_concept = ((rate_tuple[0] / 100.0) *
                              rate_tuple[2] * base / 100.0)
                wh_concept -= sb_concept
        values = {
            'amount': wh_concept,
            'raw_tax_ut': money2ut(cr, uid, wh_concept, ut_date),
            'subtract': sb_concept,
            'base_amount': base * (rate_tuple[0] / 100.0),
            'raw_base_ut': money2ut(cr, uid, base, ut_date),
            'retencion_islr': rate_tuple[2],
            'islr_rates_id': rate_tuple[5],
        }
        iwdl_obj.write(cr, uid, ids[0], values, context=context)
        return True


class IslrWhDoc(osv.osv):
    
    _inherit = 'islr.wh.doc'
    
    def action_move_create(self, cr, uid, ids, context=None):
        """ Build account moves related to withholding invoice
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        ret = self.browse(cr, uid, ids[0], context=context)
        context.update({'income_wh': True,
                        'company_id': ret.company_id.id})
        acc_id = ret.account_id.id
        if not ret.date_uid:
            self.write(cr, uid, [ret.id], {
                       'date_uid': time.strftime('%Y-%m-%d')})

        ret.refresh()
        if ret.type in ('in_invoice', 'in_refund'):
            self.write(cr, uid, [ret.id], {
                'date_ret': ret.date_uid}, context=context)
        else:
            if not ret.date_ret:
                self.write(cr, uid, [ret.id], {
                    'date_ret': time.strftime('%Y-%m-%d')})

        # Reload the browse because there have been changes into it
        ret = self.browse(cr, uid, ids[0], context=context)

        period_id = ret.period_id and ret.period_id.id or False
        journal_id = ret.journal_id.id

        if not period_id:
            period_ids = self.pool.get('account.period').search(
                cr, uid,
                [('date_start', '<=',
                  ret.date_ret or time.strftime('%Y-%m-%d')),
                 ('date_stop', '>=',
                  ret.date_ret or time.strftime('%Y-%m-%d'))])
            if len(period_ids):
                period_id = period_ids[0]
            else:
                raise osv.except_osv(
                    _('Warning !'),
                    _("Not found a fiscal period to date: '%s' please check!")
                    % (ret.date_ret or time.strftime('%Y-%m-%d')))

        ut_obj = self.pool.get('l10n.ut')
        for line in ret.invoice_ids:
            if ret.type in ('in_invoice', 'in_refund'):
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (line.invoice_id.supplier_invoice_number or '')
            else:
                name = 'COMP. RET. ISLR ' + ret.number + \
                    ' Doc. ' + (line.invoice_id.number or '')
            #_14DIC2016_rsosa:
            flag = line.invoice_id.flag_currency or False
            rate_c = flag and line.invoice_id.res_currency_rate or 1.0 
            writeoff_account_id = False
            writeoff_journal_id = False
            amount = line.amount_islr_ret
            ret_move = line.invoice_id.ret_and_reconcile(
                amount, acc_id, period_id, journal_id, writeoff_account_id,
                period_id, writeoff_journal_id, ret.date_ret, name,
                line.iwdl_ids, context=context)

            if (line.invoice_id.currency_id.id !=
                    line.invoice_id.company_id.currency_id.id):
                f_xc = ut_obj.sxc(
                    cr, uid,
                    line.invoice_id.company_id.currency_id.id,
                    line.invoice_id.currency_id.id,
                    line.islr_wh_doc_id.date_uid)
                move_obj = self.pool.get('account.move')
                move_line_obj = self.pool.get('account.move.line')
                move_brw = move_obj.browse(cr, uid, ret_move['move_id'])
                for ml in move_brw.line_id:
                    move_line_obj.write(cr, uid, ml.id, {
                        'currency_id': line.invoice_id.currency_id.id})

                    if ml.credit:
                        move_line_obj.write(cr, uid, ml.id, {
                            'amount_currency': flag and round((ml.credit / rate_c), 2) * -1 \
                                               or f_xc(ml.credit) * -1,
                            'rate_currency': rate_c })

                    elif ml.debit:
                        move_line_obj.write(cr, uid, ml.id, {
                            'amount_currency': flag and round((ml.debit / rate_c), 2) * 1 \
                                               or f_xc(ml.debit),
                            'rate_currency': rate_c })

            # make the withholding line point to that move
            rl = {
                'move_id': ret_move['move_id'],
            }
            # lines = [(op,id,values)] escribir en un one2many
            lines = [(1, line.id, rl)]
            self.write(cr, uid, [ret.id], {
                       'invoice_ids': lines, 'period_id': period_id})

        xml_ids = []
        for line in ret.concept_ids:
            xml_ids += [xml.id for xml in line.xml_ids]
        ixwl_obj.write(cr, uid, xml_ids, {
                       'period_id': period_id}, context=context)
        self.write(cr, uid, ids, {'period_id': period_id}, context=context)
        return True