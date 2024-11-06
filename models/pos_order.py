# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from lxml import etree
from odoo.exceptions import UserError, ValidationError
from lxml.builder import ElementMaker
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPBasicAuth
import logging
import xmltodict, json
from datetime import datetime
from urllib.request import urlopen
from odoo import http
from odoo.http import request
import time
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_totalPOS_id = fields.Char("orderId totalPOS")

    def delete_values(self, id):
        print('Ha limpiar la respuesta ')
        print(id[0])
        payment_methods = self.env['pos.payment.method'].search([('id', '=', id[0])])

        for payment_method in payment_methods:
            print(payment_method)
            payment_method.totalPOS_latest_response = ""
        return True

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders, draft)
        print('EL RES')
        print(res)
        print(orders)

        print('SEARRCH create_from_ui ORDER POS NEW')
        if res and res[0]['id'] > 0:
            transaction = self.env['totalpos.transaction'].search([])
            print('TRNSACTION UI')
            print(transaction)
            order_id = self.env['pos.order'].search([('id','=', res[0]['id'])])
            print('encontro orden')
            print(order_id)
            if order_id:
                print(order_id.order_totalPOS_id)
                if orders[0] and 'data' in orders[0] and 'totalPOS_orderId' in orders[0]['data'] and 'orderId' in orders[0]['data']['totalPOS_orderId']:
                    order_id.order_totalPOS_id = orders[0]['data']['totalPOS_orderId']['orderId']
        order_totalPOS = False
        intentos = 0
        return res


    def sale_totalPOS_ui(self, order):
        output = {'error': False, 'transaction': False}
        sesiones = self.env['pos.session'].search([('id', '=', order[0]['data']['pos_session_id'])])
        print('EL totalPOS')
        url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones"
        response = requests.get(url)


        if sesiones:
            refresh_token_config = False
            serial_number = False
            store_id = sesiones.config_id.store_id_totalPOS
            for sesion in sesiones:
                if sesion.config_id.refresh_token != False:
                    refresh_token_config = sesion.config_id.access_token
                    serial_number = sesion.config_id.serial_number

            print('refresh_token')
            print(refresh_token_config)

            if refresh_token_config:

                print('test pos')

                payload = ""

                url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones/sale"
                headers = {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer '+str(refresh_token_config)
                }
                traceability_dic = {

                }

                json_data = False
                print(order)
                if len(order) > 0:
                    if 'data' in order[0]:
                        if 'lines' in order[0]['data']:
                            json_data = {
                                'serialNumber': serial_number,
                                'amount': 0.00,
                                'storeId': store_id,
                                'folioNumber': False,
                                'msi': "",
                                "traceability": {
                                        "idProducto": '',
                                        "idTienda": store_id,
                                        "order_id":'',
                                        "serial_number":serial_number,
                                }
                            }

                            json_data['amount'] = order[0]['data']['amount_total']
                            json_data['folioNumber'] = order[0]['id']
                            json_data['traceability']['idProducto'] = order[0]['id']

                print('JSON totalPOSU')
                print(json_data)
                if json_data:
                    response = requests.post(url, data = json.dumps(json_data), headers = headers)

                    print(response)
                    print(response.content)
                    if response.status_code == 200:
                        if response.content:
                            response_content = response.content.decode('utf8')
                            response_json = json.loads(response_content)
                            print('status code')
                            print(response.status_code)
                    else:
                        if response.content:
                            response_content = response.content.decode('utf8')
                            print('error')
                            print(response_content)
                            if 'message' in response_content:
                                output['error'] = response_content
                else:
                    output['error'] = 'Error odoo totalPOS'

        return output

    def totalPOS_connection(self, extra_info):
        print('test')

        payload = ""

        url = "https://totalpostest.egl-cloud.com/totalpos/ws/autenticacion/oauth/token"
        if 'new_token' in extra_info:
            payload = 'grant_type=password&username=smartPos&password=totalPOS'
        if 'refresh_token' in extra_info:
            payload = 'grant_type=refresh_token&refresh_token='+str(extra_info['refresh_token'])
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic dHJ1c3RlZC1hcHA6c2VjcmV0'
        }
        # auth=HTTPBasicAuth('trusted-app', 'secret')
        response = requests.post(url, data = payload, headers = headers)
        print(response)
        print(response.content)
        if response.status_code == 200:
            if response.content:
                response_content = response.content.decode('utf8')
                response_json = json.loads(response_content)
                if 'access_token' in response_json:
                    self.access_token = response_json['access_token']
                if 'refresh_token' in response_json:
                    self.refresh_token = response_json['refresh_token']
                print('status code')
                print(response.status_code)
        else:
            if response.content:
                response_content = response.content.decode('utf8')
                print(response_content)
                if 'error_description' in response_content:
                    raise UserError(response_content)
        return True

    def get_first_token(self):
        self.totalPOS_connection({'new_token'})

        return True

    def get_refresh_token(self):
        self.totalPOS_connection({'refresh_token': self.refresh_token})

        return True

    def action_pos_order_cancel(self):
        print('Presionando al boton cancelar')
        print(self.cancel_hour)
        print(self.order_cancel_totalPOS)
        now = datetime.now()
        last_minute = 00
        last_hour = 00
        minute_difference = 00
        current_time = now.strftime("%H")
        print(now)
        if self.order_cancel_totalPOS == False:
            if self.cancel_hour != False:
                last_hour = self.cancel_hour.strftime('%H')
                last_minute = self.cancel_hour.strftime('%M')
                current_minute = now.strftime('%M')
                minute_difference = int(current_minute) - int(last_minute)

            if self.cancel_hour == False:
                print('La hora es false')
                self.cancel_hour = now.strftime("%Y-%m-%d %H:%M:%S")
                self.cancel_order_totalPOS()
                self.cancel_hour = now.strftime("%Y-%m-%d %H:%M:%S")

            elif self.cancel_hour != False and int(current_time) > int(last_hour):
                print('La hora es mayor')
                self.cancel_order_totalPOS()
                self.cancel_hour = now.strftime("%Y-%m-%d %H:%M:%S")
            elif self.cancel_hour != False and minute_difference > 2:
                print('2 minutos ya pasaron')
                self.cancel_order_totalPOS()
                self.cancel_hour = now.strftime("%Y-%m-%d %H:%M:%S")
            else:
                raise UserError('Por favor espere un momento')
        return True

    def cancel_order_totalPOS(self):
        print('Funcion cancel order')
        print('')
        now = datetime.now()

        url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones/cancel"

        refresh_token_config = False
        store_id = self.session_id.config_id.store_id_totalPOS
        order_uid = self.pos_reference[5:]
        order_uid = order_uid.replace(' ','')
        print('QUE es reference CANCEL')
#         reference = reference.replace('-','')
        order_id = self.order_totalPOS_id

        if self.session_id.config_id.access_token:
            refresh_token_config = self.session_id.config_id.access_token
        print(order_id)

        serial_number = self.session_id.config_id.serial_number
        payload = {
            "traceability": {
                "cancel": True,
                "refresh_token": refresh_token_config
            },
            "serialNumber": str(serial_number),
            "orderId": str(order_id),
            "storeId": str(store_id),
        }

        print('payload')
        print(payload)
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer '+str(refresh_token_config)
        }

        response = requests.post(url, data = json.dumps(payload), headers = headers)

        print('Response --------')
        print(response)
        print(response.content)
        print('')

#         payment_ids = self.session_id.config_id.serial_number

        payment_method_id = self.env['pos.payment.method'].search([('totalPOS_terminal_identifier', '=', serial_number)])

        if payment_method_id:

            print('Entrando a los metodos de pago')
            print(payment_method_id)
#             model_payment = payment.payment_method_id

            proxy_totalPOS_request = payment_method_id.proxy_totalPOS_request(payload, operation='cancel')
            print('Respuesta de proxy ::::')
            print(proxy_totalPOS_request)
            if proxy_totalPOS_request == True:
                latest_status = False

            print('Que es proxy_totalPOS_request cancel')
            print(proxy_totalPOS_request)
            if proxy_totalPOS_request != True and 'code' in proxy_totalPOS_request and 'message' in proxy_totalPOS_request:
                print('Error de prueba cancel')
                print(proxy_totalPOS_request)
                raise UserError(proxy_totalPOS_request['message'])

            elif proxy_totalPOS_request != True and 'error' in proxy_totalPOS_request and 'message' in proxy_totalPOS_request['error']:
                raise UserError(proxy_totalPOS_request['error']['message'])

            print('Creo que ya pasaste la parte woajaja')

        return True

    def action_pos_order_reprint(self):
        print('Boton para Reimprimir')
        now = datetime.now()
        last_minute = 0
        last_hour = 0
        minute_difference =0
        last_hour = 0
        current_time = now.strftime("%H")
        print(self.id)

        if self.reprint_time != False:
            last_hour = self.reprint_time.strftime("%H")
            last_minute = self.reprint_time.strftime("%M")
            current_minute = now.strftime("%M")
            minute_difference = int(current_minute) - int(last_minute)

        if self.reprint_time == False:
            print('Hora igual a False')
            self.reprint_time = now.strftime("%Y-%m-%d %H:%M:%S")
            self.reprint_order_totalPOS()
            self.reprint_time = now.strftime("%Y-%m-%d %H:%M:%S")
        elif self.reprint_time != False and int(current_time) > int(last_hour):
            self.reprint_order_totalPOS()
            self.reprint_time = now.strftime("%Y-%m-%d %H:%M:%S")
        elif self.reprint_time != False and minute_difference > 2:
            print('Minutos mayor reprint')
            self.reprint_order_totalPOS()
            self.reprint_time = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise UserError('Por favor espere un momento')

        return True
    def reprint_order_totalPOS(self):
        now = datetime.now()
        print(' reprint_order_totalPOS reprint')
        if self.reprint_totalPOS == False:
            url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones/reprint"
            refresh_token_config = False
            if self.session_id.config_id.access_token:
                refresh_token_config = self.session_id.config_id.access_token

            payload = {
                "traceability":{
                    "reprint": True,
                    "refresh_token": refresh_token_config,
                    "type":'reprint'
                },
                "orderId":'',
                "serialNumber":'',
                "storeId":'',
            }

            refresh_token_config = False
            if self.session_id.config_id.access_token:
                refresh_token_config = self.session_id.config_id.access_token

            headers = {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer '+str(refresh_token_config)
            }

            store_id = False
            order_id = False
            serial_number = False
            if self.session_id.config_id.serial_number:
                serial_number = self.session_id.config_id.serial_number
            if self.session_id.config_id.storeid:
                store_id = self.session_id.config_id.storeid

            if self.order_totalPOS_id:
                order_id = self.order_totalPOS_id
            payload["orderId"] = order_id
            payload["serialNumber"] = serial_number
            payload["storeId"] = store_id
            response = requests.post(url, data = json.dumps(payload), headers = headers)
            print('Response reprint-----')
            print(response)
            print(response.content)
            payment_method_id = self.env['pos.payment.method'].search([('totalPOS_terminal_identifier', '=', serial_number)])

            if payment_method_id:

                print('Entrando a los metodos de pago')
                print(payment_method_id)
    #             model_payment = payment.payment_method_id
                proxy_totalPOS_request = payment_method_id.proxy_totalPOS_request(payload, operation='reprint')
                print('Respuesta de proxy ::::')
                print(proxy_totalPOS_request)
                if proxy_totalPOS_request == True:
                    latest_status = False

                print('Que es proxy_totalPOS_request reprint')
                print(proxy_totalPOS_request)
                if proxy_totalPOS_request != True and 'code' in proxy_totalPOS_request and 'message' in proxy_totalPOS_request:
                    print('Error de prueba')
                    print(proxy_totalPOS_request)
                    raise UserError(proxy_totalPOS_request['message'])
                elif proxy_totalPOS_request != True and 'error' in proxy_totalPOS_request and 'message' in proxy_totalPOS_request['error']:
                    raise UserError(proxy_totalPOS_request['error']['message'])

                print('Creo que ya pasaste la parte reprint woajaja')
        return True