# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
      _inherit = 'res.config.settings'

      module_pos_totalPOS = fields.Boolean(string="Payment TotalPOS ", config_parameter='pos_totalPOS_connector.module_pos_totalPOS', help="The transactions are processed by POS.")


      def set_values(self):
             super(ResConfigSettings, self).set_values()
             payment_methods = self.env['pos.payment.method']
             if not self.env['ir.config_parameter'].sudo().get_param('pos_terminal_name.module_pos_totalPOS'):
                    payment_methods |= payment_methods.search([('use_payment_terminal', '=', 'totalPOS')])
                    payment_methods.write({'use_payment_terminal': False})