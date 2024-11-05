odoo.define('pos_totalPOS_connector.models', function(require) {
    'use strict';

    const models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const rpc = require('web.rpc');
    var { Gui } = require('point_of_sale.Gui');

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