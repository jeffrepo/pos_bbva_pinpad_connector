# -*- coding: utf-8 -*-
# from odoo import http


# class PosBbvaPinpadConnector(http.Controller):
#     @http.route('/pos_bbva_pinpad_connector/pos_bbva_pinpad_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_bbva_pinpad_connector/pos_bbva_pinpad_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_bbva_pinpad_connector.listing', {
#             'root': '/pos_bbva_pinpad_connector/pos_bbva_pinpad_connector',
#             'objects': http.request.env['pos_bbva_pinpad_connector.pos_bbva_pinpad_connector'].search([]),
#         })

#     @http.route('/pos_bbva_pinpad_connector/pos_bbva_pinpad_connector/objects/<model("pos_bbva_pinpad_connector.pos_bbva_pinpad_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_bbva_pinpad_connector.object', {
#             'object': obj
#         })
