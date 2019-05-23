'use strict';

var utils = require('nunja/utils');
var registry = require('nunja/registry');
var loader = require('nunja/loader');
var engine = require('nunja/engine');
var nunjucks = require('nunjucks');

var $ = utils.$;

window.mocha.setup('bdd');


/* istanbul ignore next */
var describe_ = (
    (nunjucks.compiler.compile !== undefined) ? describe : describe.skip);


/* istanbul ignore next */
if (describe_ === describe.skip) {
    console.log(
        'engine async tests requires compilation but nunjucks compiler not ' +
        'available; skipping'
    );
}


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
        // Yes, I know I can reuse them but being explicit makes the
        // test less likely to give false positives.  Still, do the
        // cleanups as it is best practice.
        delete window.nunjucksPrecompiled['check/template.nja'];
        delete window.nunjucksPrecompiled['dummy/mold/template.nja'];
        requirejs.undef('text!check/template.nja');
        requirejs.undef('text!dummy/mold/template.nja');
        requirejs.undef(this.dummy_mold_index);
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it('test query template requirejs', function() {
        // Naturally, first verify that the template is not loaded
        expect(this.engine.query_template('check/template.nja')).to.be.false;
        define('text!check/template.nja', [], function () {
            return 'dummy';
        });
        require(['text!check/template.nja'], function() {});
        this.clock.tick(500);
        expect(this.engine.query_template('check/template.nja')).to.be.true;
    });

    it('test query template precompiled', function() {
        // Naturally, first verify that the template is not loaded
        expect(this.engine.query_template('check/template.nja')).to.be.false;
        window.nunjucksPrecompiled['check/template.nja'] = function() {};
        expect(this.engine.query_template('check/template.nja')).to.be.true;
    });

    it('test simple execute, render', function() {
        expect(this.engine.execute('dummy/mold')).to.equal(
            '<div data-nunja="dummy/mold">\ndummy\n</div>\n');

        expect(this.engine.render('dummy/mold')).to.equal('dummy');
    });

    it('test simple populate, undefined index', function(done) {
        document.body.innerHTML = '<div data-nunja="dummy/mold"></div>';
        var element = $('div')[0];

        // forcing an error import handling here to prevent requirejs
        // from raising an exception after this execution was done by
        // running the test within the error handler to ensure the
        // error handler actually gets executed.
        var self = this;
        require([this.dummy_mold_index], function() {}, function() {
            self.engine.populate(element, {});
            self.clock.tick(500);
            expect(document.body.innerHTML).to.equal(
                '<div data-nunja="dummy/mold">dummy</div>');
            done();
        });
        this.clock.tick(500);

    });

    it('test simple populate, defined index', function() {
        document.body.innerHTML = '<div data-nunja="dummy/mold"></div>';
        var element = $('div')[0];
        var called = false;
        define(this.dummy_mold_index, [], function () {
            return {'init': function() {
                called = true;
            }};
        });
        require([this.dummy_mold_index], function() {});
        this.clock.tick(500);
        this.engine.populate(element, {});
        this.clock.tick(500);
        expect(document.body.innerHTML).to.equal(
            '<div data-nunja="dummy/mold">dummy</div>');
        expect(called).to.be.true;
    });

});


describe_('nunja/engine async test case', function() {

    beforeEach(function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;

        this.server.respondWith(
            'GET', '/base/mock.molds/populate/template.nja',
            function (xhr) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<span>nunja/engine populated: {{ msg }}</span>'
                );
            }
        );

        this.server.respondWith(
            'GET', '/base/mock.molds/includes/template.nja',
            function (xhr) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<p>{% include "mock.molds/includes/embedded.nja" %}</p>'
                );
            }
        );

        this.server.respondWith(
            'GET', '/base/mock.molds/includes/embedded.nja',
            function (xhr) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<span>This is second level embedded</span>'
                );
            }
        );

        requirejs.config({
            'baseUrl': '/base',
            'paths': {
                'mock.molds/engine': 'mock.molds/engine',
                'mock.molds/populates': 'mock.molds/populates',
                'mock.molds/includes': 'mock.molds/includes'
            }
        });

        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
        this.env = new nunjucks.Environment(this.loader, {
            'autoescape': true,
        });
        this.engine = new engine.Engine({
            'env': this.env,
            'registry': this.registry,
        });
    });

    afterEach(function() {
        // Yes, I know I can reuse them but being explicit makes the
        // test less likely to give false positives.  Still, do the
        // cleanups as it is best practice.
        requirejs.undef('text!mock.molds/populates/template.nja');
        requirejs.undef('text!mock.molds/includes/template.nja');
        requirejs.undef('text!mock.molds/includes/embedded.nja');
        requirejs.undef('mock.molds/populate/index');
        this.server.restore();
        document.body.innerHTML = "";
    });

    it('test async populate', function(done) {
        // Given that the rendering for client side interactions almost
        // always require async to be responsive, the populate method
        // can and should function without the explicit load_mold like
        // above.

        // First set the innerHTML to a dummy rendering
        document.body.innerHTML = (
            '<div data-nunja="mock.molds/populate"></div>'
        );
        var element = $('div')[0];
        this.engine.populate(element, {'msg': 'Hello World!'}, function() {
            var text = $('div')[0].innerHTML;
            expect(text).to.equal(
                '<span>nunja/engine populated: Hello World!</span>');
            done();
        });
    });

    it('test async include populate, no trigger', function(done) {
        // Same as above, but it includes another template that required
        // to be loaded.
        // Note the lack of the index module.

        // First set the innerHTML to a dummy rendering
        document.body.innerHTML = (
            '<div data-nunja="mock.molds/includes"></div>'
        );
        var element = $('div')[0];
        this.engine.populate(element, {}, function() {
            var text = $('div')[0].innerHTML;
            expect(text).to.equal(
                '<p><span>This is second level embedded</span></p>');
            done();
        });
    });

    it('test async populate trigger', function(done) {
        // Given that the rendering for client side interactions almost
        // always require async to be responsive, the populate method
        // can and should function without the explicit load_mold like
        // above.

        var init_element;
        var self = this;

        // First set the innerHTML to a dummy rendering
        document.body.innerHTML = (
            '<div data-nunja="mock.molds/populate"></div>'
        );
        // Also define the module
        define('mock.molds/populate/index', [], function() {
            return {'init': function(el) {
                init_element = el;
            }};
        });

        // ensure the index module is first loaded to avoid async errors
        require(['mock.molds/populate/index'], function() {
            var element = $('div')[0];
            self.engine.populate(element, {'msg': 'Hello World!'}, function() {
                var text = element.innerHTML;
                expect(text).to.equal(
                    '<span>nunja/engine populated: Hello World!</span>');
                // DOM objects behave weird on assignment, so we cannot
                // compare their identities directly.
                expect(init_element.innerHTML).to.equal(
                    '<span>nunja/engine populated: Hello World!</span>');
                done();
            });
        });
    });

    it('test async execute', function(done) {
        this.engine.execute('mock.molds/includes', {}, function(err, text) {
            expect(err).to.be.null;
            expect(text).to.equal(
                '<div data-nunja="mock.molds/includes">\n' +
                '<p><span>This is second level embedded</span></p>\n' +
                '</div>\n'
            );
            done();
        });
    });

});
