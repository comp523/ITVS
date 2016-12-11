(function(app){
"use strict";

    /**
     * Acts as a bridge to allow controllers to change the active tab
     * the controller associated with the <md-tabs> should call
     * tabs.setObserver with a callback that updates the <md-tabs>
     * selectedIndex. Other controllers may then use tabs.setTab to switch
     * the active tab.
     */
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