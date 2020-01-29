# coding: utf-8
from openerp import fields, models, api

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = "hr.contract"

    total_anticipo = fields.Float('Total monto solicitado anticipo',digits=(10,4))
    ultimo_anticipo =  fields.Float('Ultimo anticipo', digits=(10,4))
    struct_id_anticipo = fields.Many2one('hr.payroll.structure', 'Tipo de Nomina Especial')
    start_date = fields.Date('Inicio Periodo Anticipo')
    end_date = fields.Date('fin Periodo Anticipoi')

    @api.v7
    def set_anticipo_data(self, cr, uid, contract_id, monto, date_from, date_to, special_id, context=None):
        anticipo_acumulado = monto + self.read(cr, uid, contract_id, ['total_anticipo'])['total_anticipo']
        values = {
            'total_anticipo':anticipo_acumulado,
            'ultimo_anticipo': monto,
            'struct_id_anticipo':special_id,
            'start_date':date_from,
            'end_date':date_to,
        }
        self.write(cr, uid, [contract_id], values, context=context)

    @api.v7
    def get_anticipo_acum(self, cr, uid, contract_id, context=None):
        anticipo_acumulado = self.read(cr, uid, contract_id, ['total_anticipo'])
        return anticipo_acumulado['total_anticipo']


