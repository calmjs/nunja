'use strict';

// Try to load the precompiled core templates and other templates, if
// available.

// TODO following is very coupled to requirejs.  Look into ways to fully
// decouple this (i.e. make it possible for this to work with other
// systems like webpack).

// trick to fool bundler to not explicitly require this
var _require = require;
var PRECOMPILED_NUNJUCKS = 'nunja/__precompiled_nunjucks__';

/* istanbul ignore next */
try {
    var __core__ = _require('nunja/__core__');
}
catch(e) {
    console.log(
        'precompiled core templates missing; performance hit may result');
}

// TODO determine whether this should be a standard for nunja framework
// and/or how should the default templates be included if the single
// artifact method is to be fully supported.

/* istanbul ignore next */
try {
    _require(
        [PRECOMPILED_NUNJUCKS], function(){},
        function(err) {
            console.log(
                'no precompiled templates at module nunja at ' +
                PRECOMPILED_NUNJUCKS
            );
        }
    );
}
catch(e) {
    // console.log('no precompiled templates');
}

var engine = require('nunja/engine');
exports.engine = new engine.Engine({});
