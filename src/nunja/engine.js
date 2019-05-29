'use strict';

var nunjucks = require('nunjucks');
var registry = require('nunja/registry');
var loader = require('nunja/loader');
var utils = require('nunja/utils');

var $ = utils.$;

/* istanbul ignore next */
try {
    // The precompiled core is definitely required
    require('nunja/__core__');
}
catch(e) {
    console.log(
        'precompiled core templates missing; performance hit may result');
}

var _registry = new registry.Registry();

// Default environment that includes the nunja specific loader, and
// make use of autoescape as it's better to untrust templates by
// default.  To do unsafe actions one must include the safe filter,
// and this should stick out in auditing while keeping safety first.
var env = new nunjucks.Environment(new loader.NunjaLoader(_registry), {
    'autoescape': true,
});

// If any of these are overridden, we don't really support them but
// it's there if this later gets extended to do whatever other stuff
// that is needed.
var default_kwargs = {
    '_required_template_name': registry.REQ_TMPL_NAME,
    '_wrapper_name': registry.DEFAULT_WRAPPER_NAME,
    '_wrapper_tag_': registry.DEFAULT_WRAPPER_TAG,
    'env': env,
    'registry': _registry,
};

var Engine = function(kwargs) {
    for (var key in default_kwargs) {
        this[key] = kwargs[key] || default_kwargs[key];
    }

    // Load the default template.
    this['_core_template_'] = this.load_mold(this._wrapper_name);
};

// global scan function - looks up data-nunja ids and look up
// the default script, execute it on the afflicted element.
Engine.prototype.scan = function(context) {
    /*
    Collates and returns all elements with data-nunja attributes.
    */
    return $('[data-nunja]', context);
};

Engine.prototype.query_template = function (name) {
    /*
    Query for the template's loaded state.  Returns true if template can
    be loaded synchronously, false if otherwise.
    */

    // Two places that the template can be loaded: either through the
    // window.nunjucksPrecompiled or in the requirejs framework, if
    // available.

    return (
        (name in window.nunjucksPrecompiled) || (
            typeof requirejs !== "undefined" &&
            requirejs.defined('text!' + name)
        )
    );
};

Engine.prototype.load_template = function (name, cb) {
    /*
    Load the template identified by this name.
    */
    return this.env.getTemplate(name, cb);
};

Engine.prototype.load_mold = function (mold_id, cb) {
    /*
    Loads the default template for the mold identified by mold_id
    */
    return this.load_template(
        mold_id + '/' + this._required_template_name, cb);
};

Engine.prototype.load_element = function(element, cb) {
    /*
    Process this element.  This also ensures the template is
    available at some point.

    Returns the mold_id associated with this.
    */
    var mold_id = element.attributes.getNamedItem('data-nunja').value;
    this.load_mold(mold_id, cb);
    return mold_id;
};

Engine.prototype.init_element = function(element) {
    /*
    Triggers the main.init function associated with the mold of the
    element.  This should only be called once ever per element.

    element - The element we want.
    */
    var mold_id = this.load_element(element);
    var entry_point = mold_id + '/index';
    require([entry_point], function(main) {
        if (main && main.init instanceof Function) {
            main.init(element);
        }
    }, function() {
        // TODO whether have this be a definable behavior, i.e. whether
        // to leave undefine instead so import can be attempted again,
        // or that it be hard-defined to be nothing like so:
        // define(entry_point, [], {});
        // requirejs.undef(entry_point);
    });
};

Engine.prototype.do_onload = function (content) {
    /*
    The onLoad trigger.

    This scans for all relevant nodes that are related to nunja
    molds, and executes the relevant script for the relevant
    elements.
    */
    var elements = this.scan(content);
    var self = this;
    // elements.forEach(function (element, index, array) {
    elements.forEach(function (element) {
        self.init_element(element);
    });
};

Engine.prototype.execute = function (mold_id, data, cb) {
    /*
    Execute the complete template, which renders a parent block
    enclosing with the template that provides the nunja-data
    attribute.
    */
    var self = this;

    var _execute = function(error, template) {
        var params = data || {};
        params['_nunja_data_'] = 'data-nunja="' + mold_id + '"';
        params['_template_'] = template;
        params['_wrapper_tag_'] = self._wrapper_tag_;
        return self._core_template_.render(params, cb);
    };

    if (cb instanceof Function) {
        this.load_mold(mold_id, _execute);
    }
    else {
        var template = this.load_mold(mold_id);
        return _execute(null, template);
    }
};

Engine.prototype.populate = function (element, data, cb) {
    /*
    Populate the element that contains a data-nunja identifier with the
    data involved.  If a callback is provided, do so asynchronously.
    */
    var mold_id = element.getAttribute('data-nunja');

    if (!(cb instanceof Function)) {
        element.innerHTML = this.render(mold_id, data);
        this.init_element(element);
    }
    else {
        var self = this;
        this.render(mold_id, data, function(err, result) {
            // TODO handle err if there is an error somewhere...
            element.innerHTML = result;
            self.init_element(element);
            cb();
        });
    }

};

Engine.prototype.render = function (mold_id, data, cb) {
    /*
    Very simple, basic rendering method.

    The standard calling is done without the callback, which follow a
    synchronous flow.  If the callback ``cb`` is provided, the calling
    will be done asynchronously, where the cb must accept an error
    object produced by the template.render, and also the result of the
    rendering.
    */
    if (cb instanceof Function) {
        this.load_mold(mold_id, function(err, tmpl) {
            tmpl.render(data, cb);
        });
    }
    else {
        var template = this.load_mold(mold_id);
        var results = template.render(data);
        return results;
    }
};

exports.Engine = Engine;
