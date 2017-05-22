'use strict';



var core = require('nunja/core');

var main = function() {
    if ((typeof window !== 'undefined') && (window.document)) {
        var f = function() {
            core.engine.do_onload(window.document.body);
            console.log('nunja applied for document.body');
        };

        /* istanbul ignore next */
        if (window.document.readyState != 'loading') {
            f();
        }
        else {
            console.log('registering DOMContentLoaded event for nunja');
            window.document.addEventListener('DOMContentLoaded', f);
        }
    }
};

// immediately call that since that is the entry point.
main();

// for good measure, export the main function also.
exports.main = main;
