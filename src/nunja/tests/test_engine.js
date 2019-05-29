'use strict';

var utils = require('nunja/utils');
var registry = require('nunja/registry');
var loader = require('nunja/loader');
var engine = require('nunja/engine');
var nunjucks = require('nunjucks');

var $ = utils.$;

window.mocha.setup('bdd');

describe('nunja/engine simple test case', function() {

    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
        this.env = new nunjucks.Environment(this.loader, {
            'autoescape': true,
        });
        this.engine = new engine.Engine({
            'env': this.env,
            'registry': this.registry,
        });
        this.dummy_mold_index = 'dummy/mold/index';
        window.nunjucksPrecompiled["dummy/mold/template.nja"] = (
            function() { function root(env, context, frame, runtime, cb) {
                var output = "dummy";
                cb(null, output);
            } return {root: root};}
        )();
    });

    afterEach(function() {
        delete window.nunjucksPrecompiled['check/template.nja'];
        delete window.nunjucksPrecompiled['dummy/mold/template.nja'];
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it('test query template precompiled', function() {
        // Naturally, first verify that the template is not loaded
        expect(this.engine.query_template('check/template.nja')).to.be.false;
        window.nunjucksPrecompiled['check/template.nja'] = function() {};
        expect(this.engine.query_template('check/template.nja')).to.be.true;
    });

    it('test simple synchronous execute and render', function() {
        expect(this.engine.execute('dummy/mold')).to.equal(
            '<div data-nunja="dummy/mold">\ndummy\n</div>\n');
        expect(this.engine.render('dummy/mold')).to.equal('dummy');
    });

    /* istanbul ignore next */
    it('test simple populate with callback', function(done) {
        // This is tested under requirejs specific test suite, as any
        // import failure within a test will indiscrimately fail, even
        // though it was handled elsewhere by a proper error handler.
        if (typeof requirejs !== "undefined") this.skip(done());
        document.body.innerHTML = '<div data-nunja="dummy/mold"></div>';
        var element = $('div')[0];
        var cb = function cb() {
            expect(document.body.innerHTML).to.equal(
                '<div data-nunja="dummy/mold">dummy</div>');
            done();
        };
        this.engine.populate(element, {}, cb);
        this.clock.tick(500);
    });

});
