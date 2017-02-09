'use strict';

/*
This module is here just to facilitate lookup and also to provide
common default values for the system.
*/

var REQ_TMPL_NAME = 'template.nja';
var DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_';
var DEFAULT_WRAPPER_TAG = 'div';

var Registry = function() {
};

Registry.prototype.lookup_path = function(mold_id_path) {
    return 'text!' + mold_id_path;
};


Registry.prototype.name_to_mold_id = function(name) {
    var match = name.match(/^[^\/]*\/[^\/]*\//);
    return match ?  match[0].slice(0, -1) : null;
};


exports.Registry = Registry;
exports.DEFAULT_WRAPPER_NAME = DEFAULT_WRAPPER_NAME;
exports.DEFAULT_WRAPPER_TAG = DEFAULT_WRAPPER_TAG;
exports.REQ_TMPL_NAME = REQ_TMPL_NAME;
