import json

from odoo import http

from odoo.http import request, Response, JsonRequest
from odoo.tools.translate import _
from odoo.tools import date_utils
import logging

_logger = logging.getLogger(__name__)

class PosRoute(http.Controller):
        
    def alternative_json_response(self, result=None, error=None):
        if error is not None:
            response = error
        if result is not None:
            response = result
        mime = 'application/json'
        body = json.dumps(response, default=date_utils.json_default)
        return Response(
            body, status=error and error.pop('http_status', 200) or 200,
            headers=[('Content-Type', mime), ('Content-Length', len(body))]
        )

    @http.route('/web/pos/transactions', type='json', methods=['POST'],auth='none', csrf=False)
    def get_sessions(self):

        print('EXTERNAL TOTAL POS CONECTION HTTP')
        json_data = json.loads(request.httprequest.data)
        print(json_data)

        data = {"code": 300, "message": "error"}
        list_keys = ["folioNumber", "internalNumber", "tableId", "listOfPays", "tipTotalAmount", "totalAmount"]
        if ("responseCode" in json_data) and ("traceability" in json_data) and ("type" in json_data["traceability"]) and (json_data["traceability"]["type"] == "sale") and ("terminalId" not in json_data) and ("serial_number" in json_data["traceability"]):
            payment_method = request.env['pos.payment.method'].sudo().search([('totalPOS_terminal_identifier', '=', json_data['traceability']['serial_number'])], limit=1)
            print('Cancelada por el usuario')
            data = {"code": "00", "message": "Recibido"}
            payment_method.totalPOS_latest_response = json.dumps(json_data)

        if "orderId" in json_data and "folioNumber" in json_data and 'terminalId' in json_data:
            payment_method = request.env['pos.payment.method'].sudo().search([('totalPOS_terminal_identifier', '=', json_data['terminalId'])], limit=1)
            print('main 2')
            if payment_method:
                payment_method.totalPOS_latest_response = False
                if json_data['orderId']:
                    if "traceability" in json_data and "cancel" in json_data["traceability"] and json_data["traceability"]["cancel"] == True:
                        orders = request.env['pos.order'].sudo().search([('order_totalPOS_id', '=', json_data['orderId'])])
                        print('Se encontro alguna orden?')
                        print(orders)
                        if orders:
                            data = {"code": "00", "message": "Recibido"}
                            orders.order_cancel_totalPOS = True
                        else:
                            data = {"code": 300, "message": "Orden no encontrada"}
                    if "traceability" in json_data and "type" in json_data["traceability"] and json_data["traceability"]["type"] == 'reprint':
                        orders = request.env['pos.order'].sudo().search([('order_totalPOS_id', '=', json_data['orderId'])])
                        print('Se encontro alguna orden?')
                        print(orders)
                        if orders:
                            data = {"code": "00", "message": "Recibido"}
                            orders.order_cancel_totalPOS = True
                        else:
                            data = {"code": 300, "message": "Orden no encontrada "}
                    if "traceability" in json_data and "type" in json_data["traceability"] and json_data["traceability"]["type"] == 'sale':
                        data = {"code": "00", "message": "Recibido"}
                        payment_method.totalPOS_latest_response = json.dumps(json_data)
                        payment_method.totalPOS_latest_diagnosis = json_data['orderId']

                    print('Que da data?')
                    print(data)
                else:
                    data = {"code": "00", "message": "Recibido"}
                    payment_method.totalPOS_latest_response = json.dumps(json_data)
            else:
                _logger.error('received a message for a terminal not registered in Odoo: PARa mientras')

        print(request.httprequest)
        print('--after alll')

        headers = {'Content-Type': 'application/json'}
        request._json_response = self.alternative_json_response.__get__(request, JsonRequest)
        print('Devolviendo el ultimo data')
        print(data)
        return data