(function(app){
"use strict";

    var importController = function($scope, database) {

        var self = this;

        self.submit = function(){

            database.entry.import($scope.file.files[0])
                .then(function(data){
                    $scope.response = data;
                    $scope.file.value=null;
                });

        };

    };

    app.controller("importController", importController);

})(app);