'use strict';

var RequireJSLoader = function(registry, async) {
    this.registry = registry;
    // TODO figure out consequences of both these flags and best
    // settings for them.

    // async is always used to maximize usability and portability.
    this.async = true;

    // this should trigger typical loading all the time under dev?
    this.noCache = true;
};

RequireJSLoader.prototype.getSource = function(name, callback) {
    var self = this;
    var template_path = self.registry.lookup_path(name);

    var process = function(template_str) {
        callback(null, {
            'src': template_str,
            'path': name,
            'noCache': self.noCache,
        });
    };

    if (!require.defined(template_path)) {
        require([template_path], process)
    }
    else {
        // it's already loaded, call the callback directly.
        process(require(template_path));
    }
};

exports.RequireJSLoader = RequireJSLoader;
// the "default" loader under the "default" name.
exports.NunjaLoader = RequireJSLoader;
