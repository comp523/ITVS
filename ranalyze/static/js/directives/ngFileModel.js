(function(app){

    var ngFileModelDirective = function(){
        return {
            link: function(scope, element, attrs) {
                Object.defineProperty(scope, attrs.ngFileModel, {
                    get: function(){
                        return {
                            element: element,
                            value: element.val()
                        };
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