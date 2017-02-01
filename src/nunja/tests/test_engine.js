'use strict';

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

        requirejs.config({
            'baseUrl': '/base',
            'paths': {
                'mock.molds/engine': 'mock.molds/engine'
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
        requirejs.undef('text!mock.molds/engine/template.nja');
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

});
