odoo.define('pos_bbva_pinpad_connector.payment', function(require) {
    "use strict";
         var core = require('web.core');
         var PaymentInterface = require('point_of_sale.PaymentInterface');
         const { Gui } = require('point_of_sale.Gui');
         const rpc = require('web.rpc');
    
         var _t = core._t;

         var PaymentTotalPOS = PaymentInterface.extend({

            send_payment_request: function(cid) {
                console.log("Desde nuevo model");
                this._super.apply(this, arguments);
                // Comentado porque no se necesita
                // var line = this.pos.get_order().selected_paymentline;
                var order = this.pos.get_order();
                var data = this._terminal_pay_data();
                var apikey = data.PaymentMethod.terminal_api_key;
                var apipswd = data.PaymentMethod.terminal_api_pwd;
                var terminalId = data.PaymentMethod.terminal_id;
                this._reset_state();
                return this._totalPOS_pay();
             },

             // Métodos privados
            _reset_state: function () {
                this.was_cancelled = false;
                this.last_diagnosis_service_id = false;
                this.remaining_polls = 4;
                clearTimeout(this.polling);
            },

            _call_totalPOS: function (data, operation='sale') {
                return rpc.query({
                    model: 'pos.payment.method',
                    method: 'proxy_totalPOS_request',
                    args: [[this.payment_method.id], data, operation],
                }, {
                    timeout: 10000,
                    shadow: true,
                }).catch(this._handle_odoo_connection_failure.bind(this));
            },

            _totalPOS_pay_data: function () {
                var order = this.pos.get_order();
                var config = this.pos.config;
                // Comentado porque no se necesita
                // var line = order.selected_paymentline;

                var serial_number = config.serial_number || false;
                var store_id = config.store_id_totalPOS || false;
                var config_id = config.id || false;
                var access_token = config.access_token || false;

                var data = {
                    'serialNumber': serial_number,
                    'amount': order.get_total_with_tax(), // Ajustado para obtener el total con impuestos
                    'storeId': store_id,
                    'folioNumber': order.uid,
                    'msi': "",
                    "traceability": {
                        'access_token': access_token,
                        'type': "sale",
                        'config_id': config_id,
                        'serial_number': serial_number,
                    }
                };

                return data;
            },

            _totalPOS_pay: function () {
                var self = this;
                var order = this.pos.get_order();
                if (order.selected_paymentline.amount < 0) {
                    this._show_error(_t('Cannot process transactions with negative amount.'));
                    return Promise.resolve();
                }

                if (order === this.poll_error_order) {
                    delete this.poll_error_order;
                    return self._totalPOS_handle_response({});
                }

                var data = this._totalPOS_pay_data();
                return this._call_totalPOS(data).then(function (data) {
                    return self._totalPOS_handle_response(data);
                });
            },

            _show_error: function (msg, title) {
                if (!title) {
                    title =  _t('TOTAL POS Error');
                }
                Gui.showPopup('ErrorPopup',{
                    'title': title,
                    'body': msg,
                });
            },

            _totalPOS_handle_response: function (response) {
                // Comentado porque no se necesita
                // var line = this.pos.get_order().selected_paymentline;

                if (response.error && response.error.status_code != 200) {
                    this._show_error(_t(response.error.message.toString()));
                    // line.set_payment_status('force_done'); // Comentado
                    return Promise.resolve();
                }

                response = response.SaleToPOIRequest;
                if (response && response.EventNotification && response.EventNotification.EventToNotify == 'Reject') {
                    console.error('Error from Adyen', response);

                    var msg = response.EventNotification ? new URLSearchParams(response.EventNotification.EventDetails).get('message') : '';

                    this._show_error(_.str.sprintf(_t('An unexpected error occurred. Message from Adyen: %s'), msg));
                    return Promise.resolve();
                } else {
                    return new Promise(function (resolve, reject) {
                        clearTimeout(this.polling);
                        this.polling = setInterval(function () {
                            this._poll_for_response(resolve, reject);
                        }, 5500);
                    });
                }
            },

            _terminal_pay_data: function() {
                var order = this.pos.get_order();
                // var line = order.selected_paymentline; // Comentado porque no se necesita
                var data = {
                      'Name': order.name,
                      'OrderID': order.uid,
                      'TimeStamp': moment().format(),
                      'Currency': this.pos.currency.name, // Mantiene la moneda
                      'RequestedAmount': order.get_total_with_tax(), // Usar total con impuestos si aplica
                      'PaymentMethod': this.payment_method
                };
               return data;
            },

            _handle_odoo_connection_failure: function (data) {
                var line = this.pending_totalPOS_line();
                if (line) {
                    line.set_payment_status('retry');
                }
                this._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'));
                return Promise.reject(data);
            }
         });
         
         return PaymentTotalPOS;
});
