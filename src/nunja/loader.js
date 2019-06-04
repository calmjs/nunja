'use strict';

/*
This module is meant for integration with nunjucks getSource API that
they use internally in their template compilation process.  They will
essentially pass the callback function which must be invoked with the
appropriate invocation which is done inside the process function.
*/

var NUNJA_PRECOMP_NS = '__nunja__';

var SimpleLoader = function(registry) {
    this.registry = registry;

    // the simple loader will not make full use of the asynchronous
    // feature, as there will be no separate async downloading of the
    // raw template string.
    this.async = false;

    // don't cache by default.
    this.noCache = true;
};

SimpleLoader.prototype.getSource = function(name, callback) {
    var self = this;
    var template_path = self.registry.lookup_path(name);

    var process = function(template_str) {
        callback(null, {
            'src': template_str,
            'path': name,
            'noCache': self.noCache,
        });
    };

    process(require(template_path));
};


var RequireJSLoader = function(registry) {
    this.registry = registry;

    // async is always used to maximize usability, portability and
    // compatibility with AMD (and that nunjucks correctly supports it).
    this.async = true;

    // this should trigger typical loading all the time under dev?
    // TODO figure this one out.
    this.noCache = true;
};

RequireJSLoader.prototype.getSource = function(name, callback) {
    var self = this;
    var template_path = self.registry.lookup_path(name);
    var mold_id = self.registry.name_to_mold_id(name);
    var module_name = NUNJA_PRECOMP_NS + '/' + mold_id;

    var process = function(template_str) {
        callback(null, {
            'src': template_str,
            'path': name,
            'noCache': self.noCache,
        });
    };

    var compile_template = function () {
        require([template_path], process, function(err) {
            // TODO figure out what actually should be passed...
            callback(err);
        });
    };

    var get_precompiled = function(precompiled) {
        if (precompiled && precompiled[name]) {
            callback(null, {
                'src': {
                    'type': 'code',
                    'obj': precompiled[name]
                },
                'path': name
            });
            return true;
        }
        compile_template();
    };

    if (!require.defined(template_path)) {
        // require([template_path], process)
        require([module_name], get_precompiled, function() {
            // retry with just the template_path
            compile_template();
        });
    }
    else {
        // it's already loaded, call the callback directly.
        process(require(template_path));
    }

};


exports.SimpleLoader = SimpleLoader;
exports.RequireJSLoader = RequireJSLoader;
// the "default" loader under the "default" name.

/* istanbul ignore next */
exports.NunjaLoader = (
    typeof requirejs === "undefined" ? SimpleLoader: RequireJSLoader);
