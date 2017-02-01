'use strict';

// Try to load the precompiled core templates and other templates, if
// available.

// TODO determine whether this should be a standard for nunja framework
// and/or how should the default templates be included if the single
// artifact method is to be fully supported.

var preloaded = require('nunja/__precompiled_nunjucks__');

var engine = require('nunja/engine');
exports.engine = new engine.Engine({});
