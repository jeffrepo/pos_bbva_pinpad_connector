odoo.define('pos_totalPOS_connector.models', function(require) {
    var models = require('point_of_sale.models');
    var PaymentTerminal = require('pos_totalPOS_connector.payment');

    models.register_payment_method('totalPOS', PaymentTerminal);
    models.load_fields('pos.payment.method', ['terminal_api_key', 'terminal_api_pwd', 'terminal_id']);
    
    var _payterminal = models.Paymentline.prototype;
   
    models.Paymentline = models.Paymentline.extend({

        init_from_JSON: function(json) {
            _payterminal.init_from_JSON.apply(this, arguments);
            //pass your credentials like    
        },

        export_as_JSON: function() {
            return _.extend(_payterminal.export_as_JSON.apply(this, arguments), {
            //pass your credentials like
            //this.last_digits = json.last_digits;
            });
        },
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.set_totalPOS_orderId();
        },
    
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            
            json.totalPOS_orderId = this.get_totalPOS_orderId();
            
            return json;
        },
    
        get_totalPOS_orderId: function(){
            return this.get('totalPOS_orderId');
        },
        
        set_totalPOS_orderId: function(totalPOS_orderId){
            this.set({
                totalPOS_orderId: totalPOS_orderId
            });
        },
    
    });
});