(function(app){
"use strict";

    var ngFileModelDirective = function(){
        return {
            scope: {
                ngFileModel: "="
            },
            link: function(scope, element) {
                scope.ngFileModel = scope.ngFileModel || {};
                Object.defineProperties(scope.ngFileModel, {
                    files: {
                        get: function(){
                            return element[0].files;
                        },
                        set: function(){
                            throw new Error("<HTMLInputElement>.files is not writeable.");
                        }
                    },
                    value: {
                        get: function(){
                            return element.val();
                        },
                        set: function(value) {
                            element.val(value);
                        }
                    }
                });
                element.on("change", function(){
                    scope.$apply();
                });
            },
            restrict: 'A'
        }
    };

    app.directive('ngFileModel', ngFileModelDirective);

})(app);