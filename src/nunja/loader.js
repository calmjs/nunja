'use strict';

var NUNJA_PRECOMP_NS = '__nunja__';

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
        //require([template_path], process)
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


exports.RequireJSLoader = RequireJSLoader;
// the "default" loader under the "default" name.
exports.NunjaLoader = RequireJSLoader;
