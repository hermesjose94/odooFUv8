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

from openerp.osv import fields, orm, osv
from openerp import api
from openerp.tools.translate import _

class FiscalBook(orm.Model):
    _name = 'fiscal.book'
    _inherit = 'fiscal.book'
    
#_22SEP2016_rsosa: En el código original olvidaron agregar el default del campo 'company_id'
#                          lo cual causa un error ya que es un campo requerido y esta oculto.
    
    def _get_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        return user.company_id.id

#_27SEP2016_rsosa: Estos métodos se usan para el calculo de los creditos y debitos de periodos anteriores:
    @api.v7
    def _get_creditos_periodos_anteriores(self, cr, uid, ids, field_names, arg, context=None):
        context = context or {}
        if not ids: return True
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        period_obj = self.pool.get('account.period')
        for fb_brw in self.browse(cr, uid, ids, context=context):
            #document_period_id = fb_brw.period_id.id 
            for fbl_brw in fb_brw.fbl_ids:
                #fecha = fbl_brw.invoice_id.date_invoice
                #if fecha: p_fact_padre = period_obj.find(cr, uid, fecha, context=context)
                #else: p_fact_padre = 0
                if fbl_brw.doc_type == 'N/CR' and fbl_brw.invoice_id.parent_id.period_id \
                    and fbl_brw.invoice_id.parent_id.period_id.id != fb_brw.period_id.id:
                    #and fbl_brw.invoice_id.parent_id.period_id.id != p_fact_padre:
                    res[fb_brw.id]['creditos_p_anteriores_base_sum'] += (fbl_brw.vat_sdcf + \
                                                                         fbl_brw.vat_exempt + fbl_brw.vat_reduced_base + \
                                                                         fbl_brw.vat_general_base + fbl_brw.vat_additional_base)
                    res[fb_brw.id]['creditos_p_anteriores_tax_sum'] += (fbl_brw.vat_reduced_tax + \
                                                                         fbl_brw.vat_general_tax + fbl_brw.vat_additional_tax)
                    
        return res
    
    @api.v7
    def _get_debitos_periodos_anteriores(self, cr, uid, ids, field_names, arg, context=None):
        context = context or {}
        if not ids: return True
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        period_obj = self.pool.get('account.period')
        for fb_brw in self.browse(cr, uid, ids, context=context):
            #period_id = fb_brw.period_id.id 
            for fbl_brw in fb_brw.fbl_ids:
                #fecha = fbl_brw.invoice_id.date_invoice
                #if fecha: p_fact_padre = period_obj.find(cr, uid, fecha, context=context)
                #else: p_fact_padre = 0
                if fbl_brw.doc_type == 'N/DB' and fbl_brw.invoice_id.parent_id.period_id \
                    and fbl_brw.invoice_id.parent_id.period_id.id != fb_brw.period_id.id:
                    #and fbl_brw.invoice_id.parent_id.period_id.id != p_fact_padre:
                    res[fb_brw.id]['debitos_p_anteriores_base_sum'] += (fbl_brw.vat_sdcf + \
                                                                         fbl_brw.vat_exempt + fbl_brw.vat_reduced_base + \
                                                                         fbl_brw.vat_general_base + fbl_brw.vat_additional_base)
                    res[fb_brw.id]['debitos_p_anteriores_tax_sum'] += (fbl_brw.vat_reduced_tax + \
                                                                         fbl_brw.vat_general_tax + fbl_brw.vat_additional_tax)
        return res

#_28SEP2016_rsosa: Se reescribe este método para mejorar el calculo de los totales de retencion
    @api.v7
    def _get_wh(self, cr, uid, ids, field_names, arg, context=None):
        """ It returns sum of all data in the withholding summary table.
        @param field_name: ['get_total_wh_sum', 'get_previous_wh_sum',
                            'get_wh_sum']"""
        # TODO: this works if its ensuring that that emmision date is always
        # set and and all periods for every past dates are created.
        ctx = context.copy() or {}
        res = {}.fromkeys(ids, {}.fromkeys(field_names, 0.0))
        period_obj = self.pool.get('account.period')
        for fb_brw in self.browse(cr, uid, ids, context=ctx):
            for fbl_brw in fb_brw.fbl_ids:
                if fbl_brw.iwdl_id and fbl_brw.doc_type in ['AJST','RET']:
                    emission_period = period_obj.find(cr, uid, fbl_brw.emission_date, context=ctx)
                    if emission_period[0] == fb_brw.period_id.id:
                        res[fb_brw.id]['get_wh_sum'] += (fbl_brw.iwdl_id.amount_tax_ret * -1)
                        res[fb_brw.id]['get_wh_debit_credit_sum'] += fbl_brw.get_wh_debit_credit 
                    else:
                        res[fb_brw.id]['get_previous_wh_sum'] += (fbl_brw.iwdl_id.amount_tax_ret * -1)
            res[fb_brw.id]['get_total_wh_sum'] = res[fb_brw.id]['get_wh_sum'] + res[fb_brw.id]['get_previous_wh_sum']
        return res

#_22SEP2016_rsosa: En el código original olvidaron agregar el default del campo 'company_id'
#                          lo cual causa un error ya que es un campo requerido y esta oculto.    
    _defaults = {
        'company_id': _get_company
    }
    
    
#_27SEP2016_rsosa: Se agregan campos adicionales para calcular los cŕeditos y débitos de períodos anteriores
    _columns = {
        'creditos_p_anteriores_base_sum': fields.function(
            _get_creditos_periodos_anteriores,
            type='float', method=True, store=True,
            multi='creditos_p_anteriores',
            string='Total Base de Periodos Anteriores'),
        
        'creditos_p_anteriores_tax_sum': fields.function(
            _get_creditos_periodos_anteriores,
            type='float', method=True, store=True,
            multi='creditos_p_anteriores',
            string='Total IVA de Periodos Anteriores'),
        
        'debitos_p_anteriores_base_sum': fields.function(
            _get_debitos_periodos_anteriores,
            type='float', method=True, store=True,
            multi='debitos_p_anteriores',
            string='Total Base de Periodos Anteriores'),
        
        'debitos_p_anteriores_tax_sum': fields.function(
            _get_debitos_periodos_anteriores,
            type='float', method=True, store=True,
            multi='debitos_p_anteriores',
            string='Total IVA de Periodos Anteriores'),
        
        #_28SEP2016_rsosa: No se cambió la definición de estos campos, pero si no se incluyen en la herencia,
        #                          el metodo sobreescrito que los alimenta no es llamado
        'get_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Current Period Withholding",
            help="Used at"
            " 1. Totalization row in Fiscal Book Line block at Withholding"
            " VAT Column"
            " 2. Second row at the Withholding Summary block"),
        'get_previous_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Previous Period Withholding",
            help="First row at the Withholding Summary block"),
        'get_total_wh_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="VAT Withholding Sum",
            help="Totalization row at the Withholding Summary block"),
        'get_wh_debit_credit_sum': fields.function(
            _get_wh,
            type="float", method=True, store=True, multi="get_wh",
            string="Based Tax Debit Sum",
            help="Totalization row in Fiscal Book Line block at"
            " Based Tax Debit Column"),
    }
    
#_22SEP2016_rsosa: Los métodos relacionados con el workflow fueron modificados usando la api de Odoo 8 para que funcionaran

    @api.multi
    def clear_book(self):
    #def clear_book(self, cr, uid, fb_id, context=None):
        """ It delete all book data information.
        @param fb_id: fiscal book line id
        """
        self.clear_book_taxes_amount_fields()
        # delete data
        self.clear_book_lines()
        self.clear_book_taxes()
        self.clear_book_taxes_summary()
        # unrelate data
        self.clear_book_invoices()
        self.clear_book_issue_invoices()
        self.clear_book_iwdl_ids()
        self.clear_book_customs_form()
        return True
    
    @api.multi
    def clear_book_lines(self):
    #def clear_book_lines(self, cr, uid, ids, context=None):
        """ It delete all book lines loaded in the book """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        fbl_obj = self.pool.get("fiscal.book.line")
        for fb_id in self.ids:
            fbl_brws = self.browse(fb_id).fbl_ids
            fbl_ids = [fbl.id for fbl in fbl_brws]
            fbl_obj.unlink(cr, uid, fbl_ids, context=context)
            self.clear_book_taxes_amount_fields()
        return True
    
    @api.multi
    def clear_book_taxes(self):
    #def clear_book_taxes(self, cr, uid, ids, context=None):
        """ It delete all book taxes loaded in the book """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        fbt_obj = self.pool.get("fiscal.book.taxes")
        for fb_id in ids:
            fbt_brws = self.browse(fb_id).fbt_ids
            fbt_ids = [fbt.id for fbt in fbt_brws]
            fbt_obj.unlink(cr, uid, fbt_ids, context=context)
            self.clear_book_taxes_amount_fields()
        return True
    
    @api.multi
    def clear_book_taxes_summary(self):
    #def clear_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """ It delete fiscal book taxes summary data for the book """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        fbts_obj = self.pool.get('fiscal.book.taxes.summary')
        #fb_id = isinstance(fb_id, (int, long)) and [fb_id] or fb_id
        fbts_ids = fbts_obj.search(cr, uid, [('fb_id', 'in', [self.id])], context=context)
        fbts_obj.unlink(cr, uid, fbts_ids, context=context)
        return True
    
    @api.multi
    def clear_book_taxes_amount_fields(self):
    #def clear_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """ Clean amount taxes fields in fiscal book """
        vat_fields = [
            'tax_amount',
            'base_amount',
            'imex_vat_base_sum',
            'imex_exempt_vat_sum',
            'imex_sdcf_vat_sum',
            'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum',
            'imex_additional_vat_base_sum',
            'imex_additional_vat_tax_sum',
            'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum',
            'do_vat_base_sum',
            'do_exempt_vat_sum',
            'do_sdcf_vat_sum',
            'do_general_vat_base_sum',
            'do_general_vat_tax_sum',
            'do_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'do_reduced_vat_base_sum',
            'do_reduced_vat_tax_sum',
            'tp_vat_base_sum',
            'tp_exempt_vat_sum',
            'tp_sdcf_vat_sum',
            'tp_general_vat_base_sum',
            'tp_general_vat_tax_sum',
            'tp_additional_vat_base_sum',
            'tp_additional_vat_tax_sum',
            'tp_reduced_vat_base_sum',
            'tp_reduced_vat_tax_sum',
            'ntp_vat_base_sum',
            'ntp_exempt_vat_sum',
            'ntp_sdcf_vat_sum',
            'ntp_general_vat_base_sum',
            'ntp_general_vat_tax_sum',
            'ntp_additional_vat_base_sum',
            'ntp_additional_vat_tax_sum',
            'ntp_reduced_vat_base_sum',
            'ntp_reduced_vat_tax_sum',
        ]

        #return self.write(cr, uid, fb_id, {}.fromkeys(vat_fields, 0.0), context=context)
        return self.write({}.fromkeys(vat_fields, 0.0))
    
    @api.multi
    def clear_book_invoices(self):
    #def clear_book_invoices(self, cr, uid, ids, context=None):
        """ Unrelate all invoices of the book. And delete fiscal book taxes """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            self.clear_book_taxes()
            inv_brws = self.browse(fb_id).invoice_ids
            inv_ids = [inv.id for inv in inv_brws]
            inv_obj.write(cr, uid, inv_ids, {'fb_id': False}, context=context)
        return True

    @api.multi
    def clear_book_issue_invoices(self):
    #def clear_book_issue_invoices(self, cr, uid, ids, context=None):
        """ Unrelate all issue invoices of the book """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        inv_obj = self.pool.get("account.invoice")
        for fb_id in ids:
            inv_brws = self.browse(fb_id).issue_invoice_ids
            inv_ids = [inv.id for inv in inv_brws]
            inv_obj.write(cr, uid, inv_ids, {'issue_fb_id': False}, context=context)
        return True
    
    @api.multi
    def clear_book_customs_form(self):
    #def clear_book_customs_form(self, cr, uid, ids, context=None):
        """ Unrelate all customs form of the book """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        cf_obj = self.pool.get("customs.form")
        for fb_id in ids:
            cf_brws = self.browse(fb_id).cf_ids
            if cf_brws:
                cf_ids = [cf.id for cf in cf_brws]
                cf_obj.write(cr, uid, cf_ids, {'fb_id': False}, context=context)
        return True
    
    @api.multi
    def clear_book_iwdl_ids(self):
    #def clear_book_iwdl_ids(self, cr, uid, ids, context=None):
        """ Unrelate all wh iva lines of the book. """
        context = self.env.context and {k:v for k,v in self.env.context.items()} or {}
        cr = self.env.cr
        ids = self.ids
        uid = self.env.uid
        iwdl_obj = self.pool.get("account.wh.iva.line")
        for fb_id in ids:
            iwdl_brws = self.browse(fb_id).iwdl_ids
            iwdl_ids = [iwdl.id for iwdl in iwdl_brws]
            iwdl_obj.write(cr, uid, iwdl_ids, {'fb_id': False}, context=context)
        return True
    
    
#_27SEP2016_rsosa: Se sobreescribe este metodo para establecer un solo criterio de ordenación para las lineas de los Libros Fiscales
    @api.v7
    def order_book_lines(self, cr, uid, fb_id, context=None):
        """ It orders book lines by a set of criteria:
            - chronologically ascendant date (For purchase book by
              emission date, for sale book by accounting date).
            - ascendant ordering for fiscal printer ascending number.
            - ascendant ordering for z report number.
            - ascendant ordering for invoice number.
        @param fb_id: book id.
        """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        fbl_ids = [line_brw.id for line_brw in fb_brw.fbl_ids]

        #ajst_order_criteria = self.get_order_criteria_adjustment(
        #    cr, uid, fb_brw.type, context=context)
        #ajst_ordered_fbl_ids = \
        #    fbl_obj.search(
        #        cr, uid, [('id', 'in', fbl_ids), ('doc_type', '=', 'AJST')],
        #        order=ajst_order_criteria, context=context)
        #
        #for rank, fbl_id in enumerate(ajst_ordered_fbl_ids, 1):
        #    fbl_obj.write(cr, uid, fbl_id, {'rank': rank}, context=context)
        #
        #order_criteria = self.get_order_criteria(cr, uid, fb_brw.type,
        #                                         context=context)
        
        order_criteria = 'imex_date asc, emission_date asc, invoice_number asc'
        ordered_fbl_ids = \
            fbl_obj.search(
                cr, uid, [('id', 'in', fbl_ids)], #('doc_type', '!=', 'AJST')],
                          order=order_criteria, context=context)

        for rank, fbl_id in enumerate(ordered_fbl_ids, 1):
                                      #len(ajst_ordered_fbl_ids) + 1):
            fbl_obj.write(cr, uid, fbl_id, {'rank': rank}, context=context)

        return True

#_27SEP2016_rsosa: Se sobreescribe este método para modificar los criterios de determinacion del tipo de documento para las Notas de Credito y Debito
    def get_doc_type(self, cr, uid, inv_id=None, iwdl_id=None, cf_id=None,
                     fb_id=None, context=None):
        """ Returns a string that indicates de document type. For withholding
        returns 'AJST' and for invoice docuemnts returns different values
        depending of the invoice type: Debit Note 'N/DE', Credit Note 'N/CR',
        Invoice 'FACT'.
        @param inv_id : invoice id
        @param iwdl_id: wh iva line id
        """
        context = context or {}
        res = False
        if fb_id:
            obj_fb = self.pool.get('fiscal.book')
            fb_brw = obj_fb.browse(cr, uid, fb_id, context=context)
        if inv_id:
            inv_obj = self.pool.get('account.invoice')
            inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
            if (inv_brw.type in ["in_invoice","out_invoice"] and inv_brw.parent_id):
                res = "N/DB"
            elif inv_brw.type in ['in_refund','out_refund']:
                res = "N/CR"
            elif inv_brw.type in ["in_invoice", "out_invoice"]:
                res = "FACT"
    
            assert res, str(inv_brw) + ": Error in the definition \
            of the document type. \n There is not type category definied for \
            your invoice."
        elif iwdl_id:
            res = 'AJST' if fb_id and fb_brw.type == 'sale' else 'RET'
        elif cf_id:
            res = 'F/IMP'
    
        return res

    @api.v7
    def get_transaction_type(self, cr, uid, fb_id, inv_id, context=None):
        """ Method that returns the type of the fiscal book line related to the
        given invoice by cheking the customs form associated and the fiscal
        book type.
        @param fb_id: fiscal book id
        @param inv_id: invoice id
        """
        context = context or {}
        inv_obj = self.pool.get('account.invoice')
        inv_brw = inv_obj.browse(cr, uid, inv_id, context=context)
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        if inv_brw.customs_form_id:
            return 'ex' if fb_brw.type == 'sale' else 'do'
        else:
            if fb_brw.type == 'purchase':
                return 'do'
            else:
                return 'tp' if inv_brw.partner_id.vat_subjected else 'ntp'


    @api.v7
    def update_book_taxes_amount_fields(self, cr, uid, fb_id, context=None):
        """ It update the base_amount and the tax_amount field for book, and
        extract data from the book tax summary to store fields inside the
        book model.
        @param fb_id: fiscal book id
        """
        context = context or {}
        data = {}
        # totalization of book tax amount and base amount fields
        tax_amount = base_amount = 0.0
        for fbl_brw in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            sign = 1 if fbl_brw.doc_type != 'N/CR' else -1
            if fbl_brw.invoice_id:
                taxes = fbl_brw.type in ['im', 'ex'] \
                        and fbl_brw.invoice_id.imex_tax_line \
                        or fbl_brw.invoice_id.tax_line
                #taxes = fbl_brw.invoice_id.tax_line
                for ait in taxes:
                    if ait.tax_id:
                        base_amount += not ait.tax_id.ret and ait.invoice_id and \
                                       ait.invoice_id.flag_currency and (ait.base * ait.invoice_id.res_currency_rate) * sign \
                                       or ait.base_amount * sign
                        #if ait.tax_id.ret:
                        tax_amount += ait.invoice_id and ait.invoice_id.flag_currency and (ait.amount * ait.invoice_id.res_currency_rate) * sign \
                                      or ait.tax_amount * sign

        data['tax_amount'] = tax_amount
        data['base_amount'] = base_amount

        # totalization of book taxable and taxed amount for every tax type and
        # operation type
        vat_fields = [
            'imex_exempt_vat_sum',
            'imex_sdcf_vat_sum',
            'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum',
            'imex_additional_vat_base_sum',
            'imex_additional_vat_tax_sum',
            'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum',
            'do_exempt_vat_sum',
            'do_sdcf_vat_sum',
            'do_general_vat_base_sum',
            'do_general_vat_tax_sum',
            'do_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'do_reduced_vat_base_sum',
            'do_reduced_vat_tax_sum',
            'tp_exempt_vat_sum',
            'tp_sdcf_vat_sum',
            'tp_general_vat_base_sum',
            'tp_general_vat_tax_sum',
            'tp_additional_vat_base_sum',
            'tp_additional_vat_tax_sum',
            'tp_reduced_vat_base_sum',
            'tp_reduced_vat_tax_sum',
            'ntp_exempt_vat_sum',
            'ntp_sdcf_vat_sum',
            'ntp_general_vat_base_sum',
            'ntp_general_vat_tax_sum',
            'ntp_additional_vat_base_sum',
            'ntp_additional_vat_tax_sum',
            'ntp_reduced_vat_base_sum',
            'ntp_reduced_vat_tax_sum',
        ]
        for field_name in vat_fields:
            data[field_name] = \
                self.update_vat_fields(cr, uid, fb_id, field_name,
                                       context=context)

        # more complex totalization amounts.
        fb_brw = self.browse(cr, uid, fb_id, context=context)

        data['do_sdcf_and_exempt_sum'] = fb_brw.type == 'sale' \
            and (data['tp_exempt_vat_sum'] + data['tp_sdcf_vat_sum'] +
                 data['ntp_exempt_vat_sum'] + data['ntp_sdcf_vat_sum']) \
            or (data['do_exempt_vat_sum'] + data['do_sdcf_vat_sum'])

        for optype in ['imex', 'do', 'tp', 'ntp']:
            data[optype + '_vat_base_sum'] = \
                sum([data[optype + '_' + ttax + "_vat_base_sum"]
                     for ttax in ["general", "additional", "reduced"]])

        data['imex_vat_base_sum'] += \
            data['imex_exempt_vat_sum'] + data['imex_sdcf_vat_sum']

        # sale book domestic fields transformations (ntp and tp sums)
        if fb_brw.type == 'sale':

            data["do_vat_base_sum"] = \
                data["tp_vat_base_sum"] + data["ntp_vat_base_sum"]

            for ttax in ["general", "additional", "reduced"]:
                for amttype in ["base", "tax"]:
                    data['do_' + ttax + '_vat_' + amttype + '_sum'] = sum(
                        [data[optype + "_" + ttax + "_vat_" + amttype + "_sum"]
                         for optype in ["ntp", "tp"]])
            for ttax in ["exempt", "sdcf"]:
                data['do_' + ttax + '_vat_sum'] =  \
                    sum([data[optype + "_" + ttax + "_vat_sum"]
                         for optype in ["ntp", "tp"]
                         ])

        return self.write(cr, uid, fb_id, data, context=context)


#_27SEP2016_rsosa: Se sobreescribe este metodo para implementar los siguientes cambios:
# - 
    @api.v7
    def update_book_lines(self, cr, uid, fb_id, context=None):
        """ It updates the fiscal book lines values. Cretate, order and rank
        the book lines. Creates the book taxes too acorring to lines created.
        @param fb_id: fiscal book id
        """
        context = context or {}
        data = []
        #_27SEP2016_rsosa: distintos mensajes que sirven para señalar una factura dañada.
        damages = ['DOCUMENTO DAÑADO',
                   'FORMATO DAÑADO',
                   'FACTURA DAÑADA',
                   'DOCUMENTO ANULADO',
                   'FACTURA ANULADA',
                   'PAPELANULADO']
        iwdl_obj = self.pool.get('account.wh.iva.line')
        fb_brw = self.browse(cr, uid, fb_id, context=context)
        rp_obj = self.pool.get('res.partner')

        # add book lines for withholding iva lines
        if fb_brw.iwdl_ids:
            flag_anulada = fb_brw.name and str(fb_brw.name[:12]).upper() in damages or False
            orphan_iwdl_ids = self._get_orphan_iwdl_ids(cr, uid, fb_id,context=context)
            no_match_dt_iwdl_ids = self._get_no_match_date_iwdl_ids(cr, uid, fb_id, context=context)
            #_28SEP2016_rsosa: crea una lista de ID's de los documentos de Retencion de IVA ....
            #ret_ids = []
            #if self.browse(cr, uid, fb_id, context=context).type == 'purchase':
            ret_ids = iwdl_obj.search(cr, uid, [('fb_id','=',fb_id)])
            ret_ids = len(ret_ids) > 0 and ret_ids or []
            #_28SEP2016_rsosa: ... y los agrega a la lista general
            iwdl_ids = orphan_iwdl_ids + no_match_dt_iwdl_ids + ret_ids  
            t_type = fb_brw.type == 'sale' and 'tp' or 'do'
            for iwdl_brw in iwdl_obj.browse(cr, uid, iwdl_ids, context=context):
                rp_brw = rp_obj._find_accounting_partner(iwdl_brw.retention_id.partner_id)
                #_27SEP2016_rsosa: se agrega una variable para almacenar el tipo de documento, ya que se usara en otras validaciones
                doc_ty = self.get_doc_type(cr, uid, iwdl_id=iwdl_brw.id,context=context)
                values = {
                    'iwdl_id': iwdl_brw.id,
                    'type': t_type,
                    'accounting_date': iwdl_brw.date_ret or False,
                    'emission_date':
                        iwdl_brw.date or iwdl_brw.date_ret or False,
                    'doc_type': doc_ty,
                    'wh_number': doc_ty in ['AJST','RET'] and iwdl_brw.retention_id.number or False,
                    'partner_name': rp_brw.name or 'N/A',
                    #_27SEP2016_rsosa: se ajusta la presentacion del campo RIF al requerimiento de la ley venezolana
                    #'partner_vat': rp_brw.vat or 'N/A',
                    'partner_vat': (rp_brw.vat and rp_brw.vat[2] + '-' + rp_brw.vat[3:-1] + '-' + rp_brw.vat[-1]) or 'N/A',
                    'affected_invoice':
                        iwdl_brw.invoice_id.fiscal_printer and
                        iwdl_brw.invoice_id.invoice_printer or
                        (fb_brw.type == 'sale' and
                         iwdl_brw.invoice_id.number or
                         iwdl_brw.invoice_id.supplier_invoice_number),
                    'affected_invoice_date':
                        iwdl_brw.invoice_id.date_document or
                        iwdl_brw.invoice_id.date_invoice,
                    'wh_rate': iwdl_brw.wh_iva_rate,
                    #_27SEP2016_rsosa: se almacena el tipo de documento para que contenga sus denominaciones correctas
                    'void_form': iwdl_brw.name and (iwdl_brw.name and (iwdl_brw.name[:12].upper() in damages and '03-REG')) \
                             or (doc_ty in ['N/CR','N/DB'] and '02-REG') or (doc_ty in ['AJST','RET'] and '04-REG') \
                             or (doc_ty in ['FACT','F/IMP'] and '01-REG'),
                }
                data.append((0, 0, values))
        cf_ids = []
        # add book lines for invoices
        for inv_brw in self.browse(cr, uid, fb_id,context=context).invoice_ids:
            
            #imex_invoice = self.is_invoice_imex(cr, uid, inv_brw.id, context=context)
            iwdl_id = self._get_invoice_iwdl_id(cr, uid, fb_id, inv_brw.id, context=context)
            doc_type = self.get_doc_type(cr, uid, inv_id=inv_brw.id, fb_id=fb_id, context=context)
            rp_brw = rp_obj._find_accounting_partner(inv_brw.partner_id)
            iwdl_brw = iwdl_obj.browse(cr, uid, iwdl_id, context=context) \
                       if iwdl_id and iwdl_id not in no_match_dt_iwdl_ids else False
            
            if inv_brw.customs_form_id : 
                cf_ids.append(inv_brw)
            #_27SEP2016_rsosa: Validación para evitar reflejar en los Libros las facturas de pagos de estos servicios y/o compromisos fiscales
            if inv_brw.type == 'in_invoice' and rp_brw.name in ['INSTITUTO VENEZOLANO DE LOS SEGUROS SOCIALES (IVSS)',
                                                                'INSTITUTO VENEZOLANO DE LOS SEGUROS SOCIALES',
                                                                'BANCO NACIONAL PARA LA VIVIENDA Y HABITAT (BANAVIH)',
                                                                'BANCO NACIONAL PARA LA VIVIENDA Y HABITAT',
                                                                'INSTITUTO NACIONAL DE CAPACITACION Y EDUCACION SOCIALISTA (INCES)',
                                                                'INSTITUTO NACIONAL DE CAPACITACION Y EDUCACION SOCIALISTA',
                                                                'TESORERIA DE LA SEGURIDAD SOCIAL']:
                continue
            
            #_27SEP2016_rsosa: Validacion para reflejar correctamente las facturas afectadas
            aff_invoice = False
            if doc_type in ['N/CR', 'N/DB'] and inv_brw.parent_id:
                if fb_brw.type == 'purchase': aff_invoice = inv_brw.parent_id.supplier_invoice_number
                else: aff_invoice = inv_brw.parent_id.number
            
            flag_anulada = inv_brw.name and str(inv_brw.name[:12]).upper() in damages or False
            
            values = {
                'invoice_id': inv_brw.id,
                #_13OCT2016_rsosa: se define de nuevo la asignacion de las fechas. La condicion de importacion
                #                          no deberia tener nada que ver con la asignacion de la fecha. Averiguar.
                'emission_date': inv_brw.date_document or False,
                    #(not imex_invoice) and
                    #(inv_brw.date_document or inv_brw.date_invoice) or
                    #False,
                'accounting_date': inv_brw.date_invoice or False,
                    #(not imex_invoice) and
                    #inv_brw.date_invoice or
                    #False,
                'imex_date': False,
                    #imex_invoice and
                    #inv_brw.customs_form_id.date_liq or
                    #False,
                'type': self.get_transaction_type(cr, uid, fb_id, inv_brw.id, context=context),
                'debit_affected':
                    inv_brw.parent_id and
                    inv_brw.parent_id.type in
                    ['in_invoice', 'out_invoice'] and
                    inv_brw.parent_id.parent_id and
                    inv_brw.parent_id.number or
                False,
                'credit_affected':
                    inv_brw.parent_id and
                    inv_brw.parent_id.type in
                    ['in_refund', 'out_refund'] and
                    inv_brw.parent_id.number or
                    False,
                'ctrl_number':
                    not inv_brw.fiscal_printer and
                    inv_brw.nro_ctrl or
                    False,
                #_27SEP2016_rsosa: la validacion para este campo se coloco lineas atras
                #'affected_invoice':
                #    (doc_type == "N/DB" or doc_type == "N/CR") and (
                #        inv_brw.parent_id and
                #        inv_brw.parent_id.number or
                #        False) or
                #    False,
                'affected_invoice': aff_invoice,
                'partner_name': not flag_anulada and rp_brw.name or 'FACTURA ANULADA',
                #_27SEP2016_rsosa: se ajusta la presentacion del campo RIF al requerimiento de la ley venezolana
                #'partner_vat': rp_brw.vat and rp_brw.vat[2:] or 'N/A',
                'partner_vat': flag_anulada and ' ' \
                               or (rp_brw.vat and rp_brw.vat[2] + '-' + rp_brw.vat[3:-1] + '-' + rp_brw.vat[-1]) or 'N/A',
                'invoice_number': flag_anulada and ' ' \
                    or inv_brw.fiscal_printer and
                       inv_brw.invoice_printer or (
                           fb_brw.type == 'sale' and
                           inv_brw.number or
                           inv_brw.supplier_invoice_number),
                'doc_type': doc_type,
                #_27SEP2016_rsosa: se ajusta el tipo de documento para que contenga sus denominaciones correctas
                #'void_form':
                #    inv_brw.name and (
                #        inv_brw.name.find('PAPELANULADO') >= 0 and
                #        '03-ANU' or
                #        '01-REG') or
                #    '01-REG',
                'void_form': inv_brw.name and (inv_brw.name[:12].upper() in damages and '03-REG') \
                             or (doc_type in ['N/CR','N/DB'] and '02-REG') or (doc_type in ['AJST','RET'] and '04-REG') \
                             or (doc_type == 'FACT' and '01-REG'),
                'fiscal_printer': inv_brw.fiscal_printer or False,
                'z_report': inv_brw.z_report or False,
                'custom_statement': inv_brw.customs_form_id.name or False,
                'iwdl_id': iwdl_brw and iwdl_brw.id,
                'wh_number': doc_type in ['AJST','RET'] and iwdl_brw and iwdl_brw.retention_id.number or '',
                'wh_rate': iwdl_brw and iwdl_brw.wh_iva_rate or 0.0,
            }
            data.append((0, 0, values))

        # add book lines for customs forms
        #for cf_brw in fb_brw.cf_ids:
        #
        #    cf_partner_brws = \
        #        list(set([
        #            rp_obj._find_accounting_partner(
        #                cfl_brw.tax_code.partner_id)
        #            for cfl_brw in cf_brw.cfl_ids
        #            if not cfl_brw.tax_code.vat_detail]))
        #
        #    common_values = {
        #        'cf_id': cf_brw.id,
        #        'type': 'do',
        #        'emission_date': cf_brw.date_liq or False,
        #        'doc_type': self.get_doc_type(cr, uid, cf_id=cf_brw.id,
        #                                      fb_id=fb_id, context=context),
        #    }
        #
        #    for partner_brw in cf_partner_brws:
        #        values = common_values.copy()
        #        values['partner_name'] = partner_brw.name or 'N/A'
        #        values['partner_vat'] = partner_brw.vat \
        #            and partner_brw.vat[2:] or 'N/A'
        #        values['total_with_iva'] = \
        #            self.get_cfl_sum(cr, uid, cf_brw.id, partner_brw.id,
        #                             context=context)
        #        values['vat_sdcf'] = values['total_with_iva']
        #        
        #
        #        data.append((0, 0, values))
        
        #_14OCT2016_rsosa: Procesamiento de las facturas de Importacion.
        for inv in cf_ids:
            val = {
                #'invoice_id': inv.id,
                'cf_id': inv.customs_form_id.id,
                'emission_date': inv.customs_form_id.date_liq,
                'imex_date': self.is_invoice_imex(cr, uid, inv.id, context=context) and \
                             inv.customs_form_id.date_liq or False,
                'type': 'im',
                'doc_type': self.get_doc_type(cr, uid, cf_id= inv.customs_form_id.id, fb_id = fb_id, context=context),
                'void_form': '01-REG',
                'partner_name': inv.partner_id.name or 'N/A',
                'partner_vat': (inv.partner_id.vat and inv.partner_id.vat[2] + '-' + inv.partner_id.vat[3:-1] + '-' + inv.partner_id.vat[-1]) or 'N/A',
                #_27SEP2016_rsosa: se agregan campos que son obligatorios en los formatos de Libros Fiscales.
                'planilla_importacion': inv.n_formulario or False,
                'exp_importacion': inv.n_expediente or False,
                'invoice_number': inv.supplier_invoice_number or False,
                'ctrl_number': inv.nro_ctrl
            }
            
            data.append((0, 0, val))
            

        if data:
            self.write(cr, uid, fb_id, {'fbl_ids': data}, context=context)
            self.link_book_lines_and_taxes(cr, uid, fb_id, context=context)

        if fb_brw.article_number in ['77', '78']:
            self.update_book_ntp_lines(cr, uid, fb_brw.id, context=context)
        else:
            self.order_book_lines(cr, uid, fb_brw.id, context=context)

        return True
    
    @api.v7
    def link_book_lines_and_taxes(self, cr, uid, fb_id, context=None):
        """ Updates the fiscal book taxes. Link the tax with the corresponding
        book line and update the fields of sum taxes in the book.
        @param fb_id: the id of the current fiscal book """
        context = context or {}
        fbl_obj = self.pool.get('fiscal.book.line')
        #ut_obj = self.pool.get('l10n.ut')
        # write book taxes
        data = []
        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                #f_xc = ut_obj.sxc(
                #    cr, uid,
                #    fbl.invoice_id.currency_id.id,
                #    fbl.invoice_id.company_id.currency_id.id,
                #    fbl.invoice_id.date_invoice)
                sign = 1 if fbl.doc_type != 'N/CR' else -1
                amount_field_data = \
                    {'total_with_iva': (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                        fbl.invoice_id.amount_untaxed * fbl.invoice_id.res_currency_rate or \
                                        fbl.invoice_id.amount_untaxed ) * sign,
                     'vat_sdcf': 0.0, 'vat_exempt': 0.0}
                #taxes = fbl.type in ['im', 'ex'] \
                #    and fbl.invoice_id.imex_tax_line \
                #    or fbl.invoice_id.tax_line
                taxes = fbl.invoice_id.tax_line
                for ait in taxes:
                    if ait.tax_id and ait.base_code_id:

                        amount_field_data['total_with_iva'] += (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                                                ait.amount * fbl.invoice_id.res_currency_rate or \
                                                                ait.tax_amount) * sign
                        if ait.tax_id.appl_type == 'sdcf':
                            amount_field_data['vat_sdcf'] += (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                                              ait.base * fbl.invoice_id.res_currency_rate or \
                                                              ait.base_amount) * sign
                        if ait.tax_id.appl_type == 'exento':
                            amount_field_data['vat_exempt'] += (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                                                ait.base * fbl.invoice_id.res_currency_rate or \
                                                                ait.base_amount) * sign
                        data.append((0, 0, {'fb_id': fb_id,
                                            'fbl_id': fbl.id,
                                            'ait_id': ait.id,
                                            'base_amount': (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                                            ait.base * fbl.invoice_id.res_currency_rate or \
                                                            ait.base_amount) * sign,
                                            'tax_amount': (fbl.invoice_id.flag_currency and fbl.invoice_id.res_currency_rate and \
                                                           ait.amount * fbl.invoice_id.res_currency_rate or \
                                                           ait.tax_amount) * sign}))
                    #else:
                    #    data.append((0, 0, {
                    #        'fb_id': fb_id, 'fbl_id': False,
                    #        'ait_id': ait.id}))
                fbl_obj.write(cr, uid, fbl.id, amount_field_data, context=context)

            elif fbl.cf_id:
                imex_obj = self.pool.get('account.invoice.tax')
                for cf_line in fbl.cf_id.cfl_ids:
                    if cf_line.tax_code.vat_detail:
                        imex_id = imex_obj.search(cr, uid, [('cfl_id','=',cf_line.id)], context=context)
                        imex_tax = imex_obj.browse(cr, uid, imex_id)
                        base_am = imex_tax.base_amount
                        tax_am = imex_tax.tax_amount
                        trad = {'exento': 'exempt', 'reducido': 'reduced', 'general': 'general', 'adicional': 'additional', 'sdcf': 'sdcf'}
                        if imex_tax.tax_id.appl_type:
                            if imex_tax.tax_id.appl_type not in ['exento', 'sdcf']:
                                field_base_name = str('vat_' + trad[imex_tax.tax_id.appl_type] + '_base')
                                field_tax_name = str('vat_' + trad[imex_tax.tax_id.appl_type] + '_tax')
                            else:
                                field_name = 'vat_' + trad[imex_tax.tax_id.appl_type]
                            amount_field_data = {
                                'total_with_iva': base_am + tax_am,
                                field_base_name: base_am,
                                field_tax_name: tax_am }
                            data.append((0, 0, {'fb_id': fb_id,
                                                'fbl_id': fbl.id,
                                                'ait_id': len(imex_id) > 0 and imex_id[0] or False,
                                                'base_amount': base_am,
                                                'tax_amount': tax_am}))
                            fbl_obj.write(cr, uid, fbl.id, amount_field_data, context=context)

        if data:
            self.write(cr, uid, fb_id, {'fbt_ids': data}, context=context)
        self.update_book_taxes_summary(cr, uid, fb_id, context=context)
        self.update_book_lines_taxes_fields(cr, uid, fb_id, context=context)
        self.update_book_taxes_amount_fields(cr, uid, fb_id, context=context)
        return True
    
    #_19OCY2016_rsosa: Se sobreescribe este método para recalcular las lineas del libro provenientes de facturas en dolares a la tasa especificada en la factura
    @api.v7
    def update_book_taxes_summary(self, cr, uid, fb_id, context=None):
        """ It update the summaroty of taxes by type for this book.
        @param fb_id: fiscal book id
        """
        context = context or {}
        self.clear_book_taxes_summary(cr, uid, fb_id, context=context)
        tax_types = ['exento', 'sdcf', 'reducido', 'general', 'adicional']
        op_types = self.browse(cr, uid, fb_id, context=context).type \
            == 'sale' and ['ex', 'tp', 'ntp'] or ['im', 'do']
        base_sum = {}.fromkeys(op_types)
        tax_sum = base_sum.copy()
        for op_type in op_types:
            tax_sum[op_type] = {}.fromkeys(tax_types, 0.0)
            base_sum[op_type] = {}.fromkeys(tax_types, 0.0)

        for fbl in self.browse(cr, uid, fb_id, context=context).fbl_ids:
            if fbl.invoice_id:
                flag = fbl.invoice_id.flag_currency
                rate = flag and fbl.invoice_id.res_currency_rate or 0.0
                sign = 1 if fbl.doc_type != 'N/CR' else -1
                #tax_lines = fbl.type in ['im', 'ex'] \
                #    and fbl.invoice_id.imex_tax_line \
                #    or fbl.invoice_id.tax_line
                tax_lines = fbl.invoice_id.tax_line
                for ait in tax_lines:
                    if ait.tax_id.appl_type:
                        if not ait.base_code_id: continue 
                        base_sum[fbl.type][ait.tax_id.appl_type] += (flag and ait.base * rate) * sign or \
                            ait.base_amount * sign
                        tax_sum[fbl.type][ait.tax_id.appl_type] += (flag and ait.amount * rate) * sign or \
                            ait.tax_amount * sign
                    else:
                        raise osv.except_osv(
                            _('Error!'),
                            _('You must assign the Aliquot Type to: %s') % (
                                ait.tax_id.name))
            elif fbl.cf_id:
                if fbl.type != 'im':
                    raise osv.except_osv(
                        _('Programing Error!'),
                        ("Verifique las planillas de importacion"))
                #base_sum['do']['sdcf'] += fbl.vat_sdcf
                #_05DIC2016_rsosa: Totalizacion correcta de las alicuotas de importacion
                imp_base_dict = {'general': fbl.vat_general_base, 
                                 'reducido': fbl.vat_reduced_base, 
                                 'adicional': fbl.vat_additional_base, 
                                 'exento': fbl.vat_exempt,
                                 'sdcf': fbl.vat_sdcf}
                imp_tax_dict = {'general': fbl.vat_general_tax, 
                                'reducido': fbl.vat_reduced_tax, 
                                'adicional': fbl.vat_additional_tax}
                for elem in imp_base_dict: base_sum['im'][elem] += imp_base_dict[elem]
                for elem in imp_tax_dict: tax_sum['im'][elem] += imp_tax_dict[elem]
                #base_sum['im']['general'] += fbl.vat_general_base
                #tax_sum['im']['general'] += fbl.vat_general_tax

        data = [(0, 0, {'tax_type': ttype, 'op_type': optype,
                        'base_amount_sum': base_sum[optype][ttype],
                        'tax_amount_sum': tax_sum[optype][ttype]
                        })
                for ttype in tax_types
                for optype in op_types
                ]
        return data and self.write(cr, uid, fb_id, {'fbts_ids': data}, context=context)
    
    
    #@api.v7
    #def update_book_lines_taxes_fields(self, cr, uid, fb_id, context=None):
    #    """ Update taxes data for every line in the fiscal book given,
    #    extrating de data from the fiscal book taxes associated.
    #    @param fb_id: fiscal book line id.
    #    """
    #    context = context or {}
    #    fbl_obj = self.pool.get('fiscal.book.line')
    #    field_names = ['vat_reduced_base', 'vat_reduced_tax',
    #                   'vat_general_base', 'vat_general_tax',
    #                   'vat_additional_base', 'vat_additional_tax']
    #    tax_type = {'reduced': 'reducido', 'general': 'general',
    #                'additional': 'adicional'}
    #    for fbl_brw in self.browse(cr, uid, fb_id, context=context).fbl_ids:
    #        sign = 1 if fbl_brw.doc_type != 'N/CR' else -1
    #        data = {}.fromkeys(field_names, 0.0)
    #        for fbt_brw in fbl_brw.fbt_ids:
    #            for field_name in field_names:
    #                field_tax, field_amount = field_name[4:].split('_')
    #                if fbt_brw.ait_id.tax_id.appl_type == tax_type[field_tax]:
    #                    data[field_name] += field_amount == 'base' \
    #                        and fbt_brw.base_amount * sign \
    #                        or fbt_brw.tax_amount * sign
    #        fbl_obj.write(cr, uid, fbl_brw.id, data, context=context)
    #    return True
    
class FiscalBookLines(orm.Model):
    
    _inherit = 'fiscal.book.line'
    
#_27SEP2016_rsosa: se agregan campos que son obligatorios en los formatos de Libros Fiscales.
    _columns = {
        'planilla_importacion': fields.char(string='Numero de Planilla de Importacion', size=120),
        'exp_importacion': fields.char(string='Numero de Expediente de Importacion', size=120),
    }
    
    def alicuota(self, cr, uid, ids, type, list_base=None, list_tax=None, base=None, vat=None, context=None):
        '''
        _24NOV2016_rsosa:
        This function returns the tax rate based on the base_amount and tax supplied, to show in the report
        '''
        if type == 'im' and list_base and list_tax:
            list_base.sort(None,None,True)
            list_tax.sort(None,None,True)
            return str(round(((list_tax[0] * 100) / list_base[0]), 1)) + '%'
        elif base and vat and not (base * vat) == 0:
            return str(round(((vat * 100) / base), 1)) + '%'
        else:
            return '0,0%'
