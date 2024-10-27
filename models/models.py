# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class pos_bbva_pinpad_connector(models.Model):
#     _name = 'pos_bbva_pinpad_connector.pos_bbva_pinpad_connector'
#     _description = 'pos_bbva_pinpad_connector.pos_bbva_pinpad_connector'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
