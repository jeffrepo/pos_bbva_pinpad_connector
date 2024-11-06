odoo.define('pos_bbva_pinpad_connector.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PaymentScreenInherit = PaymentScreen => class extends PaymentScreen {
        // Sobrescribimos la función validateOrder
        async validateOrder(isForceValidate) {
            // Aquí puedes agregar lógica adicional antes de llamar a la función original
            console.log('Hi Geordie ')
            var order = this.env.pos.get_order();
            console.log("order ", order);
            // console.lg()
            return super.validateOrder(...arguments);
        }
    }

    Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

    return PaymentScreen;
});
