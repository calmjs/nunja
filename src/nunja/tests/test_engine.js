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
    });

    afterEach(function() {
        // Yes, I know I can reuse them but being explicit makes the
        // test less likely to give false positives.  Still, do the
        // cleanups as it is best practice.
        delete window.nunjucksPrecompiled['check/template.nja'];
        requirejs.undef('text!check/template.nja');
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

    it('test async include populate', function(done) {
        // Same as above, but it includes another template that required
        // to be loaded.

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

});
