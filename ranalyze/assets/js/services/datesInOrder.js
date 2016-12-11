(function(app){
"use strict";

    /**
     * Determines if two dates are in order, i.e. a is before b.
     * @param a
     * @param b
     * @returns {boolean} a < b
     */
    var datesInOrder = function(a, b) {
        return !(a && b && a.getTime() >= b.getTime());
    };

    app.value('datesInOrder', datesInOrder);

})(app);