(function(app){
"use strict";

    var ssoTimeoutInterceptorFactory = function($q, $rootScope, constants) {

        var failCount = 0;

        return {
            'responseError': function(rejection) {

                if (rejection.status === -1 && failCount++ == constants.SSO_ERROR_THRESHOLD) {

                    $rootScope.$emit('ranalyze.error', {
                        controller: ssoDialogController,
                        controllerAs: 'ctrl',
                        templateUrl: 'templates/dialogs/sso-error.html'
                    });

                }

                return $q.reject(rejection);

            }
        };
    };

    var ssoDialogController = function($mdDialog, $window) {

        var ctrl = this;

        angular.extend(ctrl, {
            close: $mdDialog.hide,
            reload: function(){
                $window.location.reload();
            }
        });

    };

    app.config(function($httpProvider, $provide){

        $provide.factory('ssoTimeoutInterceptor', ssoTimeoutInterceptorFactory);

        $httpProvider.interceptors.push('ssoTimeoutInterceptor');

    });

})(app);