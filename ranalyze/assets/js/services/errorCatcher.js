(function(app){
"use strict";

    var addErrorListener = function($rootScope, $mdDialog, $http){
        var defaults = {
            clickOutsideToClose: true,
            title: "Something Went Wrong",
            textContent: "An unknown error has occurred.",
            ariaLabel: "Error Popup",
            ok: "Okay"
        };
        $rootScope.$on('ranalyze.error', function(event, args){
            var params = angular.extend({}, defaults, args);
            $mdDialog.show(
                $mdDialog.alert(params)
            )
        });
    };

    app.run(addErrorListener);

})(app);