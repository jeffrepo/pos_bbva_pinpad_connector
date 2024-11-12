# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests, json

class PosConfig(models.Model):
    _inherit = 'pos.config'

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
                    value = self.get_first_token()
                    print('lowwwwwwwwwwwwwwwwwwwwwwww')
                    print(value)
                    if value == True:
                        self.get_refresh_token()
                    else:
                        raise UserError(response_content)
        return True

    def get_first_token(self):
        self.totalPOS_connection({'new_token'})

        return True

    def get_refresh_token(self):
        self.totalPOS_connection({'refresh_token': self.refresh_token})

        return True

    def activate_token_netapy(self):
        print('Acción automatizada')
        points_of_sale = self.env['pos.config'].search([
            ('access_token', '!=', False),
            ('serial_number', '!=', False),
            ('refresh_token', '!=', False),
            ('store_id_totalPOS', '!=', False)])
        print(points_of_sale)
        for point in points_of_sale:
            print('punto')
            print(point.name)
            point.get_refresh_token()
            print('Se ha llegado más lejos de refrescar el token ;D')

        return True
