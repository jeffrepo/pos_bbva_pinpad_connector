# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests, json
import logging
_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pinpad_ip = fields.Char(string="IP del Pin Pad", help="Dirección IP del Pin Pad")
    pinpad_port = fields.Integer(string="Puerto del Pin Pad", help="Puerto de conexión del Pin Pad")
    pinpad_timeout = fields.Integer(string="Tiempo de Espera", help="Tiempo de espera en segundos")
    pinpad_message = fields.Char(string="Mensaje del Pin Pad", help="Mensaje mostrado en el Pin Pad")
    pinpad_contactless = fields.Boolean(string="Contactless Habilitado", help="Habilitar/deshabilitar pagos sin contacto")
    host_url = fields.Char(string="URL del Host", help="URL base del SDK de TOTAL POS")
    # bines_url = fields.Char(string="URL de Bines", help="URL para actualización de bines")
    token_url = fields.Char(string="URL del Token", help="URL para obtener el token de autenticación")
    # tele_load_url = fields.Char(string="URL de Telecarga", help="URL para telecargar actualizaciones")
    warranty_feature = fields.Boolean(string="Funcionalidad de Garantía", help="Activar funcionalidad de garantía")
    moto_feature = fields.Boolean(string="Funcionalidad Moto", help="Activar funcionalidad Moto")
    merchant_affiliation = fields.Char(string="Afiliación del Comercio", help="ID de Afiliación del Comercio")
    merchant_terminal = fields.Char(string="Terminal del Comercio", help="ID de la Terminal")
    merchant_mac = fields.Char(string="MAC del Comercio", help="MAC de la terminal de pago")
    application_id = fields.Char(string="ID de la Aplicación", help="ID de la aplicación registrada")
    secret_key = fields.Char(string="Clave Secreta", help="Clave secreta para la autenticación")


    def configure_pinpad(self):
        # Configuración inicial del Pin Pad
        try:
            configuration = {
                "logs": True,
                "pinpad_connection": self.pinpad_ip,
                "pinpad_timeout": self.pinpad_timeout,
                "pinpad_port": self.pinpad_port,
                "pinpad_message": self.pinpad_message,
                "pinpad_contactless": self.pinpad_contactless,
                "bines_key": "",
                "host_url": self.host_url + "/totalpos/ws/autorizaciones/transacciones",
                "bines_url": self.host_url + "/totalpos/ws/recursos/bines/concentrado/actualizaciones",
                "token_url": self.host_url + "/oauth/token",
                "tele_load_url": self.host_url + "/descargas",
                "warranty_feature": self.warranty_feature,
                "moto_feature": self.moto_feature,
                "merchant_affiliation": self.merchant_affiliation,
                "merchant_terminal": self.merchant_terminal,
                "merchant_mac": self.merchant_mac,
                "application_id": self.application_id,
                "secret_key": self.secret_key
            }

            self.setConfiguracion(configuration)
            self.inicializar()


            #Omitir todo esto es solo para probar si funcionaban las URL de prueba
            response = requests.post(self.host_url + "/set_configuration", json=configuration)
            
            if response.status_code == 200:
                return True
            else:
                print("Error al configurar el Pin Pad: ", response.text)
                return False
        except Exception as e:
            print("Excepción al configurar el Pin Pad: ", str(e))
            return False

    
    def setConfiguracion(self, configuracion):
        return configuracion
    def inicializar(self):
        return True
    
    # @api.model
    def get_token(self):
        """
        Método para autenticarse y obtener el token de acceso.
        """
        if not self.token_url or not self.application_id or not self.secret_key:
            raise ValueError("URL del Token, ID de Aplicación o Clave Secreta no configurados.")
        
        url = self.token_url
        payload = {
            'client_id': self.application_id,
            'client_secret': self.secret_key,
            'grant_type': 'client_credentials'  # Dependiendo de los requerimientos de autenticación
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Realizar solicitud POST para obtener el token
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()  # Lanza un error si la respuesta tiene un código de error
            
            # Procesar respuesta
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token
        
        except requests.exceptions.RequestException as e:
            # Manejo de errores de conexión o autenticación
            raise UserError(f"Error al obtener el token: {e}")


    def _get_payment_terminal_selection(self):
          return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('totalPOS', 'totalPOS')]

    def proxy_totalPOS_request(self, data, operation):
        print('proxy_totalPOS_request')

        return self._proxy_totalPOS_request_direct(data, operation)

    def _get_totalPOS_endpoints(self, operation):
        url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones"
        if operation == 'sale':
            url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones"
        if operation == 'cancel':
            url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones/cancel"
        if operation == 'reprint':
            url = "https://totalpostest.egl-cloud.com/totalpos/ws/autorizaciones/transacciones/reprint"

        return url

    def get_latest_totalPOS_status(self, pos_config_name, order_uid):
        print('Función get_latest_adyen_status')
        _logger.info('get_latest_adyen_status\n%s', pos_config_name)
        self.ensure_one()

        latest_response = self.sudo().totalPOS_latest_response

        print('latest_response, cruzar dedos')
        print(latest_response)
        latest_response = json.loads(latest_response) if latest_response else False

#         print(latest_response[0])
        print('')
        if latest_response != False:
            if "folioNumber" in latest_response:

#             latest_response_dumps=json.dumps(latest_response)
                if order_uid == latest_response['folioNumber']:
                    print('Si son iguales')


                else:
                    print('No es Igual llllllllllll')
                    latest_response = False
        print('Antes del return :::C')
        print(latest_response)
        return {
            'latest_response': latest_response,
        }

    def _is_write_forbidden(self, fields):
        whitelisted_fields = set(('totalPOS_latest_response', 'totalPOS_latest_diagnosis'))
        return super(PosPaymentMethod, self)._is_write_forbidden(fields - whitelisted_fields)

    def _proxy_totalPOS_request_direct(self, data, operation):
        print('Function _proxy_totalPOS_request_direct')
        print(self)
        for x in self:
            x.ensure_one()
        TIMEOUT = 10
        print('_proxy_totalPOS_request_direct')
        print('request to adyen\n%s' + str(data))

        #environment = 'test' if self.adyen_test_mode else 'live'

        refresh_token_config = False
        if operation == 'sale':
            endpoint = self._get_totalPOS_endpoints(operation)
            if 'traceability' in data and data['traceability'] and 'access_token' in data['traceability'] and data['traceability']['access_token']:
                refresh_token_config = data['traceability']['access_token']
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(refresh_token_config)
            }
            traceability_dic = {}
            serial_number = False
            if 'serialNumber' in data:
                serial_number=data['serialNumber']
            store_id = False
            if 'storeId' in data:
                store_id = data['storeId']
            amount=False
            if 'amount' in data:
                amount = data['amount']
            folio_number = False
            if 'folioNumber' in data:
                folio_number = data['folioNumber']

            serial_number = False
            if "traceability" in data:
                if "serial_number" in data["traceability"]:
                    serial_number = data["traceability"]["serial_number"]

            json_data = {
                'serialNumber': serial_number,
                'amount': amount,
                'storeId': store_id,
                'folioNumber': folio_number,
                'msi': "",
                "traceability": {
                    'type':'sale',
                    'serial_number':serial_number
                }
            }
            print('endpoint--')
            print(endpoint)
            print(json_data)
            print('...........')
            print('')
            print('')
            req = requests.post(endpoint, data = json.dumps(json_data), headers = headers)
            print('Request---------1')
            print(req)
            print(req.content)
            
            if req.status_code == 200:
                if req.content:
                    response_content = req.content.decode('utf8')
                    response_json = json.loads(response_content)
                    print('status code')
                    print(req.status_code)
                    return True


            if req.status_code != 200:
                response_content = req.content.decode('utf8')
                print("Estado de respuesta:", req.status_code, "\n\n")
                print("Contenido de respuesta:", req.content, "\n\n")
                print("response_content ", response_content ,"\n\n\n")

                if response_content:
                    json_loads = json.loads(response_content)

                    print("json_loads \n\n\n", json_loads)
                    if "error_description" in json_loads:
                        logging.warning('Entro al IF?')
                        return {
                            'error':{
                                'status_code': req.status_code,
                                'message': json_loads["error_description"],

                            }
                        }
                    
                    if "message" in json_loads:
                        logging.warning('entra message no error_description')
                        return {
                            'error':{
                                'status_code': req.status_code,
                                'message': json_loads["message"],

                            }
                        }
                    
                if req.status_code == 401:
                    print('Entro al IF 401 \n\n')
                    return {
                        'error':{
                            'status_code': req.status_code,
                            'message': req.content,}
                    }
                    
            return req.json()


            

        if operation == 'cancel':
            endpoint = self._get_totalPOS_endpoints(operation)
            print('Bienvenido a una función con opcion cancel')
            if ("traceability" and "serialNumber" and "orderId" and "storeId") in data:
                refresh_token_config = False

            if 'traceability' in data and data['traceability'] and 'refresh_token' in data['traceability'] and data['traceability']['refresh_token']:
                refresh_token_config = data['traceability']['refresh_token']
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(refresh_token_config)
            }
            serial_number = False
            if "serialNumber" in data:
                serial_number = data["serialNumber"]
            order_id = False
            if "orderId" in data:
                order_id = data["orderId"]
            if "storeId" in data:
                store_id = data["storeId"]


            json_data = {
                "traceability": {
                    "cancel": True,
                    'type': 'cancel'
                },
                "serialNumber": str(serial_number),
                "orderId": str(order_id),
                "storeId": str(store_id),
            }

            print('endpoint--')
            print(endpoint)
            print(json_data)
            print('...........')
            print('')
            print('')
            req = requests.post(endpoint, data = json.dumps(json_data), headers = headers)
            print('Request---------2 cancel')
            print(req)
            print(req.content)

            if req.status_code == 200:
                if req.content:
                    response_content = req.content.decode('utf8')
                    response_json = json.loads(response_content)
                    print('status code')
                    print(req.status_code)
                    return True

            if req.status_code != 200:
                response_content = req.content.decode('utf8')
                print('error')
                print(response_content)
                print(response_content[0])
                json_loads = json.loads(response_content)
                if "error_description" in json_loads:
                    print('Entro al IF?')
                    print(json_loads["error_description"])
                    return {
                        'error':{
                            'status_code': req.status_code,
                            'message': json_loads["error_description"],

                        }
                    }

            return req.json()

        if operation == 'reprint':
            endpoint = self._get_totalPOS_endpoints(operation)
            print('Bienvenido a una función con opcion reprint')
            if ("traceability" and "serialNumber" and "orderId" and "storeId") in data:
                refresh_token_config = False

            if 'traceability' in data and data['traceability'] and 'refresh_token' in data['traceability'] and data['traceability']['refresh_token']:
                refresh_token_config = data['traceability']['refresh_token']
            headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+str(refresh_token_config)
            }
            serial_number = False
            if "serialNumber" in data:
                serial_number = data["serialNumber"]
            order_id = False
            if "orderId" in data:
                order_id = data["orderId"]
            if "storeId" in data:
                store_id = data["storeId"]


            json_data = {
                "traceability": {
                    "reprint": True,
                    "type": 'reprint'
                },
                "serialNumber": str(serial_number),
                "orderId": str(order_id),
                "storeId": str(store_id),
            }

            print('endpoint--')
            print(endpoint)
            print(json_data)
            print('...........')
            print('')
            print('')
            req = requests.post(endpoint, data = json.dumps(json_data), headers = headers)
            print('Request---------2 reprint')
            print(req)
            print(req.content)

            if req.status_code == 200:
                if req.content:
                    response_content = req.content.decode('utf8')
                    response_json = json.loads(response_content)
                    print('status code')
                    print(req.status_code)
                    return True

            if req.status_code != 200:
                response_content = req.content.decode('utf8')
                print('error')
                print(response_content)
                print(response_content[0])
                json_loads = json.loads(response_content)
                if "error_description" in json_loads:
                    print('Entro al IF?')
                    print(json_loads["error_description"])
                    return {
                        'error':{
                            'status_code': req.status_code,
                            'message': json_loads["error_description"],

                        }
                    }

            return req.json()
    