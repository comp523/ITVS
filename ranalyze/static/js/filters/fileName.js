(function(app){

    var fileNameFilter = function(){
        var slashRegExp = /[\/\\]/;
        return function(input) {
            if (input===undefined || !input.match(slashRegExp)) {
                return input;
            }
            var segments = input.split(slashRegExp);
            return segments[segments.length-1];
        };
    };

    app.filter("fileName", fileNameFilter);

})(app);