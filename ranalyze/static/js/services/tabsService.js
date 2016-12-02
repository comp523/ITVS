(function(app){
"use strict";

    var tabsService = function() {

        var self = this,
            observer;

        self.setTab = function(tabIndex) {
            if (observer) {
                observer(tabIndex);
            }
        };

        self.setObserver = function(func) {
            observer = func;
        };

    };

    app.service('tabs', tabsService);

})(app);