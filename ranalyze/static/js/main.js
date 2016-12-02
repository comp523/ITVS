var app = (function(){
"use strict";

    var dependencies = [
        'ngMaterial',
        'ngMessages',
        'ngResource',
        'md.data.table',
        'angular-jqcloud'
    ];

    return angular.module("RanalyzeApp", dependencies)
        .run(function($rootScope, $mdDialog){
            var defaults = {
                clickOutsideToClose: true,
                title: "Something Went Wrong",
                textContent: "An unknown error has occurred.",
                ariaLabel: "Error Popup",
                ok: "Okay"
            };
            $rootScope.$on('ranalyze.error', function(event, args){
                var params = angular.copy(defaults);
                angular.extend(params, args);
                $mdDialog.show(
                    $mdDialog.alert(params)
                )
            });
        });

})();