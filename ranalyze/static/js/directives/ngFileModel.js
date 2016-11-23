(function(app){
"use strict";

    var ngFileModelDirective = function(){
        return {
            link: function(scope, element, attrs) {
                scope[attrs.ngFileModel] = {};
                Object.defineProperties(scope[attrs.ngFileModel], {
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
                    scope.$apply(angular.noop);
                });
            },
            restrict: 'A'
        }
    };

    app.directive('ngFileModel', ngFileModelDirective);

})(app);