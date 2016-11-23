(function(app){
"use strict";

    var ngHighlightDirective = function(){
        return {
            scope: {
                keywords: '&ngHighlight'
            },
            link: function(scope, element, attrs) {

                scope.$watchGroup(['keywords', function(){
                    return element.text();
                }], function(){
                    var regex = new RegExp('(' + scope.keywords().join('|') + ')', 'gi'),
                        text = element.text(),
                        highlighted = text.replace(regex, "<span class=\"highlight\">$1</span>");
                    element.html(highlighted);
                });

            }
        }
    };

    app.directive('ngHighlight', ngHighlightDirective);

})(app);