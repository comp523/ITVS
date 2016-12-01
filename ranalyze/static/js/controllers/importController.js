(function(app){
"use strict";

    var importController = function($scope, database) {

        var self = this;

        self.submit = function(){

            database.Entry.import({
                file: $scope.file.files[0]
            }, function success(data){
                $scope.response = data;
                $scope.file.value=null;
            }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't import csv."
            });
        });

        };

    };

    app.controller("importController", importController);

})(app);