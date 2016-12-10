(function(app){
"use strict";

    var basicDialogController = function($scope, $mdDialog){

        var ctrl = this;

        ctrl.close = $mdDialog.hide;

    };

    app.controller('basicDialogController', basicDialogController);

})(app);