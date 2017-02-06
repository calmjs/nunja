'use strict';

var utils = require('nunja/utils');
var registry = require('nunja/registry');
var loader = require('nunja/loader');
var engine = require('nunja/engine');
var nunjucks = require('nunjucks');

window.mocha.setup('bdd');


describe('nunja/engine test case', function() {
    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        this.server.respondWith(
            'GET', '/base/mock.molds/engine/template.nja',
            function (xhr, id) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<span>nunja/engine says: {{ msg }}</span>'
                );
            }
        );

        this.server.respondWith(
            'GET', '/base/mock.molds/populate/template.nja',
            function (xhr, id) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<span>nunja/engine populated: {{ msg }}</span>'
                );
            }
        );

        this.server.respondWith(
            'GET', '/base/mock.molds/includes/template.nja',
            function (xhr, id) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<p>{% include "mock.molds/includes/embedded.nja" %}</p>'
                );
            }
        );

        this.server.respondWith(
            'GET', '/base/mock.molds/includes/embedded.nja',
            function (xhr, id) {
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
        requirejs.undef('text!mock.molds/engine/template.nja');
        requirejs.undef('text!mock.molds/populates/template.nja');
        requirejs.undef('text!mock.molds/includes/template.nja');
        requirejs.undef('text!mock.molds/includes/embedded.nja');
        this.server.restore();
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it('test async load and render', function() {
        // Generally, the on_load handler should trigger the loading of
        // all the required templates for the given page, so the null
        // result should never happen unless the user interacts with the
        // page before all the resources are loaded, which again should
        // not be a problem if all resources are pre-compiled artifacts.
        var initial = this.engine.load_mold('mock.molds/engine')
        this.clock.tick(500);
        expect(initial).to.be.undefined;

        // as the clock has ticked, the resources should be loaded
        var loaded = this.engine.load_mold('mock.molds/engine')
        expect(loaded).not.to.be.undefined;

        // Just run it through render.
        var results = this.engine.render('mock.molds/engine', {'msg': 'hi!'});
        expect(results).to.equal('<span>nunja/engine says: hi!</span>');
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
        this.clock.tick(500);
        var element = $('div')[0];
        this.engine.populate(element, {'msg': 'Hello World!'}, function() {
            var text = $('div')[0].innerHTML;
            expect(text).to.equal(
                '<span>nunja/engine populated: Hello World!</span>');
            done();
        });
        this.clock.tick(500);
    });

    it('test async include populate', function(done) {
        // Same as above, but it includes another template that required
        // to be loaded.

        // First set the innerHTML to a dummy rendering
        document.body.innerHTML = (
            '<div data-nunja="mock.molds/includes"></div>'
        );
        this.clock.tick(500);
        var element = $('div')[0];
        this.engine.populate(element, {}, function() {
            var text = $('div')[0].innerHTML;
            expect(text).to.equal(
                '<p><span>This is second level embedded</span></p>');
            done();
        });
        this.clock.tick(500);
    });

});
