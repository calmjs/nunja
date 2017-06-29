'use strict';


var _main = function() {
    var core = require('nunja/core');
    core.engine.do_onload(window.document.body);
    console.log('nunja applied for document.body');
};

var main = function() {
    if ((typeof window !== 'undefined') && (window.document)) {
        /* istanbul ignore next */
        if (window.document.readyState != 'loading') {
            _main();
        }
        else {
            console.log('registering DOMContentLoaded event for nunja');
            window.document.addEventListener('DOMContentLoaded', _main);
        }
    }
};

// immediately call that since that is the entry point.
main();

// for good measure, export the main function also.
exports.main = main;
