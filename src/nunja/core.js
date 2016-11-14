'use strict';

// Try to load the precompiled core templates and other templates, if
// available.

// TODO determine whether this should be a standard for nunja framework
// and/or how should the default templates be included if the single
// artifact method is to be fully supported.

/* istanbul ignore next */
try {
    // trick to fool bundler to not explicitly require this
    var _require = require;
    var PRECOMPILED_NUNJUCKS = 'nunja/__precompiled_nunjucks__';
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
