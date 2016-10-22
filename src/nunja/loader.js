'use strict';

var RequireJSLoader = function(registry, async) {
    this.registry = registry;
    // TODO figure out consequences of both these flags and best
    // settings for them.

    // async is typically false because we assume requirejs has them
    // already loaded in standard config
    this.async = (async === true);

    // this should trigger typical loading all the time under dev?
    this.noCache = true;
};

RequireJSLoader.prototype.getSource = function(name, callback) {
    var self = this;
    var template_path = self.registry.lookup_path(name);

    if (this.async) {
        require([template_path], function(template_str) {
            callback(null, {
                'src': template_str,
                'path': name,
                'noCache': self.noCache,
            });
        });
    }
    else {
        return {
            'src': require(template_path),
            'path': name,
            'noCache': self.noCache,
        }
    }
};

exports.RequireJSLoader = RequireJSLoader;
// the "default" loader under the "default" name.
exports.NunjaLoader = RequireJSLoader;
