'use strict';
/*
This utils module provide helpers that work with acquiring nodes and
helper functions that bulk apply functions to them.
*/

function $(selector, context) {
    /*
    Operates similar to the jQuery selector, though on a much more
    limited scale.
    */

    return Array.prototype.slice.call(
        (context || document).querySelectorAll(selector));
}

function addEventListeners(elements, event_id, cb) {
    /*
    For each item in the selected list, call `addEventListener` with the
    arguments provided.
    */

    elements.forEach(function (el, index, array) {
        el.addEventListener(event_id, cb);
    });
}

exports = {
    '$': $,
    'addEventListeners': addEventListeners,
}
