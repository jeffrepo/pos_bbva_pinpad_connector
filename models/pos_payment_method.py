# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import requests

class PoSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pinpad_ip = fields.Char(string="IP del Pin Pad", help="Dirección IP del Pin Pad")
    pinpad_port = fields.Integer(string="Puerto del Pin Pad", help="Puerto de conexión del Pin Pad")
    pinpad_timeout = fields.Integer(string="Tiempo de Espera", help="Tiempo de espera en segundos")
    pinpad_message = fields.Char(string="Mensaje del Pin Pad", help="Mensaje mostrado en el Pin Pad")
    pinpad_contactless = fields.Boolean(string="Contactless Habilitado", help="Habilitar/deshabilitar pagos sin contacto")
    host_url = fields.Char(string="URL del Host", help="URL base del SDK de TOTAL POS")
    # bines_url = fields.Char(string="URL de Bines", help="URL para actualización de bines")
    # token_url = fields.Char(string="URL del Token", help="URL para obtener el token de autenticación")
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

            # Supongamos que la API requiere un POST para configurar
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
        

        
    def initialize_pinpad(self):
        # Inicialización del Pin Pad
        try:
            response = requests.post(self.host_url + "/initialize_pinpad")
            
            if response.status_code == 200:
                return True
            else:
                print("Error al inicializar el Pin Pad: ", response.text)
                return False
        except Exception as e:
            print("Excepción al inicializar el Pin Pad: ", str(e))
            return False