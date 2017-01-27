'use strict';

var nunjucks = require('nunjucks');
var registry = require('nunja/registry');
var loader = require('nunja/loader');

/* istanbul ignore next */
try {
    // The precompiled core is definitely required
    var __core__ = require('nunja/__core__');
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

// Don't quite need all of jQuery but the selector.
function $(selector, context) {
    return (context || document).querySelectorAll(selector);
}

var Engine = function(kwargs) {
    for (var key in default_kwargs) {
        this[key] = kwargs[key] || default_kwargs[key];
    }

    // Load the default template.
    this['_core_template_'] = this.load_mold(this._wrapper_name);
};

// global scan function - looks up data-nunja ids and look up
// the default script, execute it on the afflicted element.
Engine.prototype.scan = function (content) {
    /*
    Collates and returns all elements with data-nunja attributes.
    */
    var elements = $('[data-nunja]');
    return Array.prototype.slice.call(elements);
};

Engine.prototype.load_template = function (name) {
    /*
    Load the template identified by this name.
    */
    return this.env.getTemplate(name);
};

Engine.prototype.load_mold = function (mold_id) {
    /*
    Loads the default template for the mold identified by mold_id
    */
    return this.load_template(
        mold_id + '/' + this._required_template_name);
};

Engine.prototype.load_element = function(element) {
    /*
    Process this element.  This also ensures the template is
    available at some point.

    Returns the mold_id associated with this.
    */
    var mold_id = element.attributes.getNamedItem('data-nunja').value;
    this.load_mold(mold_id);
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
    }, function(err) {});
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
    elements.forEach(function (element, index, array) {
        self.init_element(element);
    });
},

Engine.prototype.execute = function (mold_id, data) {
    /*
    Execute the complete template, which renders a parent block
    enclosing with the template that provides the nunja-data
    attribute.
    */
    var template = this.load_mold(mold_id);

    var data = data || {};
    data['_nunja_data_'] = 'data-nunja="' + mold_id + '"';
    data['_template_'] = template;
    data['_wrapper_tag_'] = this._wrapper_tag_;

    var results = this._core_template_.render(data);

    return results;
};

Engine.prototype.populate = function (element, data) {
    /*
    Populate the element that contains a data-nunja identifier
    with the data involved.
    */
    var mold_id = element.getAttribute('data-nunja');
    element.innerHTML = this.render(mold_id, data)
};

Engine.prototype.render = function (mold_id, data) {
    /*
    Very simple, basic rendering method.
    */
    var template = this.load_mold(mold_id);
    var results = template.render(data);
    return results;
};

exports.Engine = Engine;
