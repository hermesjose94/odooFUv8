# coding: utf-8
# from openerp import fields, models, api
from openerp.osv import osv, fields
from openerp.exceptions import Warning
from datetime import datetime, time, date

class hr_payslip_run(osv.osv):
    _inherit = 'hr.payslip.run'

    _columns = {
        'util_days_to_pay': fields.integer('Dias a pagar utilidades', size=3),
        'is_util': fields.boolean('Es Utilidades'),
        'is_anticipo': fields.boolean('Anticipos'),
    }


    # @api.v7
    def onchange_struct_id(self, cr, uid, ids, value, context=None):
        res = {}
        is_util = False
        struct_obj = self.pool.get('hr.payroll.struct')
        for s in struct_obj.browse(cr, uid, value, context=context):
            if s.struct_category == 'especial' and 'utilidad' in s.struct_id_payroll_category:
                is_util = True
        res = {'value': {'is_util': is_util}}
        return res

    # @api.v7
    def get_days_util_to_pay(self, cr, uid, id):
        local_obj = self.browse(cr, uid, id)
        return local_obj.util_days_to_pay

    # @api.v7
    def validate_util_days_to_pay(self, cr, uid, id, values, come_from, context=None):
        fecha =None
        dias = values.get('util_days_to_pay',False)
        especial = values.get('check_special_struct', False)
        struct_obj = self.pool.get('hr.payroll.structure')
        struct_id = values.get('struct_id', False)
        is_anticipo = values.get('is_anticipo', False)
        if especial or struct_id:
            struct = struct_obj.read(cr, uid, struct_id, ['name'], context=context )
            if 'UTILIDAD' in struct['name'].upper() and is_anticipo and dias == 0:
                raise Warning(('Advertencia!'), (
                    u'El Número de días a pagar no puede ser 0! Por favor verifique e intente nuevamente.'))
        else:
            hr_util_obj = self.pool.get('hr.payroll.utilidades')
            # for psr in self.browse(cr, uid, id, context=context):
            #     fecha = psr.date_start
            fecha = values['date_start'].split('-')[0]
            year = fecha if fecha else datetime.now().strftime('%Y-%m-%d').split('-')[0]
            total = hr_util_obj.get_last_util_max_days(cr, uid, year)
            # d = total - dias
            if dias > total:
                raise Warning(('Advertencia!'), (
                    u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifie e intente nuevamente.'))
            # elif dias == 0:
            #     raise Warning(('Advertencia!'), (
            #         u'El Número de días a pagar no puede ser 0! Por favor verifie e intente nuevamente.'))

        return True

    # @api.v7
    def write(self, cr, uid, ids, values, context=None):
        if context is None: context = {}
        if not hasattr(ids, '__iter__'): ids = [ids]
        if values.get('check_special_struct', False) or values.get('struct_id', False):
            self.validate_util_days_to_pay(cr, uid, ids, values, 'write', context)
        res = super(hr_payslip_run, self).write(cr, uid, ids, values, context)
        return res

    # @api.v7
    def create(self, cr, uid, values, context=None):
        if context is None: context = {}
        res = {}
        if values.get('check_special_struct',False):
            self.validate_util_days_to_pay(cr, uid, None, values, 'create', context=context)
        res = super(hr_payslip_run, self).create(cr, uid, values, context=context)
        return res