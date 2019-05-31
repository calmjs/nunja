'use strict';

var registry = require('nunja/registry');
var loader = require('nunja/loader');
var nunjucks = require('nunjucks');

window.mocha.setup('bdd');


describe('nunja/loader async path test case', function() {
    // follows the full asynchronous path

    beforeEach(function() {
        // NOT using fake timers to fully rely on standard flow of time
        // and using the async test handlers.
        // this.clock = sinon.useFakeTimers();

        this.nunjucksPrecompiled = window.nunjucksPrecompiled;
        window.nunjucksPrecompiled = {};

        // Emulate a server responded template
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        this.server.respondWith(
            'GET', '/base/mock.molds/loaderasync/template.nja',
            function (xhr) {
                xhr.respond(
                    200, {'Content-Type': 'text/plain'},
                    '<span>Integrated mocked template async: {{ msg }}</span>'
                );
            }
        );

        requirejs.config({
            'baseUrl': '/base',
            'paths': {
                'mock.molds/loaderasync': 'mock.molds/loaderasync'
            }
        });

        // Generally, precompiled templates through calmjs rjs will be
        // available as a generated module that gets preloaded like so;
        // so while testing the actual module loading through the fake
        // server can be done, that path is not something we intend to
        // support.  In the light of that, inject the module directly
        // into the requirejs framework.

        // This is an imitation of a nunjucks template module that gets
        // produced that has error handling stripped.

        define('__nunja__/mock.molds/preload', [], function() {
            var nunjucksPrecompiled = window.nunjucksPrecompiled;
            nunjucksPrecompiled["mock.molds/preload/template.nja"] = (
                function() { function root(env, context, frame, runtime, cb) {
                    var output = "preload";
                    cb(null, output);
                } return {root: root};}
            )();
            window.nunjucksPrecompiled = nunjucksPrecompiled;
            return nunjucksPrecompiled;
        });

        define('__nunja__/mock.molds/precompiled', [], function() {
            var nunjucksPrecompiled = window.nunjucksPrecompiled;
            nunjucksPrecompiled["mock.molds/precompiled/template.nja"] = (
                function() { function root(env, context, frame, runtime, cb) {
                    var output = "precompiled";
                    cb(null, output);
                } return {root: root};}
            )();
            window.nunjucksPrecompiled = nunjucksPrecompiled;
            return nunjucksPrecompiled;
        });

        // Finally, the objects from our library to test with.
        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
    });

    afterEach(function() {
        requirejs.undef('text!mock.molds/loaderasync/template.nja');
        requirejs.undef('text!mock.molds/precompiled/raw.nja');
        requirejs.undef('__nunja__/mock.molds/preload');
        requirejs.undef('__nunja__/mock.molds/precompiled');
        this.server.restore();
        document.body.innerHTML = "";
        window.nunjucksPrecompiled = this.nunjucksPrecompiled;
    });

    it('test getSource async compile', function(done) {
        this.loader.getSource('mock.molds/loaderasync/template.nja', function(
            err, value
        ) {
            expect(err).to.be.null;
            expect(value['src']).to.equal(
                '<span>Integrated mocked template async: {{ msg }}</span>');
            expect(value['path']).to.equal(
                'mock.molds/loaderasync/template.nja');
            done();
        });
    });

    it('test getSource async 404', function(done) {
        this.loader.getSource('mock.molds/nosuch/template.nja', function(
            err, value
        ) {
            expect(err).not.to.be.null;
            expect(value).to.be.undefined;
            done();
        });
    });

    it('test getSource async precompiled', function(done) {
        var self = this;
        this.loader.getSource('mock.molds/preload/template.nja', function(
            err, value
        ) {
            expect(err).to.be.null;
            expect(value['src']['type']).to.equal('code');
            expect(value['path']).to.equal(
                'mock.molds/preload/template.nja');
            expect(window.nunjucksPrecompiled[
                'mock.molds/preload/template.nja']).to.equal(
                    value['src']['obj']);
            // do a test render, which should render through the now
            // loaded nunjucksPrecompiled
            var env = new nunjucks.Environment(self.loader);
            var tmpl = env.getTemplate('mock.molds/preload/template.nja');
            expect(tmpl.render()).to.equal('preload');
            done();
        });
    });

    it('test getSource async precompiled but missing', function(done) {
        this.loader.getSource('mock.molds/precompiled/missing.nja', function(
            err, value
        ) {
            expect(err).not.to.be.null;
            expect(value).to.be.undefined;
            done();
        });
    });

    it('test getSource async precompiled but recovered', function(done) {
        // try the rendering again
        define('text!mock.molds/precompiled/raw.nja', [], function() {
            return 'recovered';
        });

        this.loader.getSource('mock.molds/precompiled/raw.nja', function(
            err, value
        ) {
            expect(err).to.be.null;
            expect(value['src']).to.equal('recovered');
            expect(value['path']).to.equal('mock.molds/precompiled/raw.nja');
            done();
        });
    });

    it('test getSource async fresh rendering', function(done) {
        // try the rendering again
        var env = new nunjucks.Environment(this.loader);
        env.getTemplate('mock.molds/precompiled/template.nja', function(
            err, tmpl
        ) {
            expect(err).to.be.null;
            expect(tmpl.render()).to.equal('precompiled');
            // should be able to do so synchronously now
            expect(
                env.getTemplate('mock.molds/precompiled/template.nja').render()
            ).to.equal('precompiled');
            done();
        });
    });

});


describe('nunja/loader sync path test case', function() {
    // follows the synchronous path (via callbacks)

    beforeEach(function() {
        // using fake timers to help with poking stuff along
        this.clock = sinon.useFakeTimers();

        define('text!mock.molds/loadersync/template.nja', [], function() {
            return '<span>Manual defined sync: {{ msg }}</span>';
        });
        this.clock.tick(500);
        require(['text!mock.molds/loadersync/template.nja'], function() {});
        this.clock.tick(500);

        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
    });

    afterEach(function() {
        requirejs.undef('text!mock.molds/loadersync/template.nja');
        this.clock.restore();
        document.body.innerHTML = "";
    });


    it('test getSource sync', function() {
        var result;
        var callback = function(err, value) {
            result = value;
        };

        this.loader.getSource('mock.molds/loadersync/template.nja', callback);
        this.clock.tick(500);

        expect(result['src']).to.equal(
            '<span>Manual defined sync: {{ msg }}</span>');
        expect(result['path']).to.equal('mock.molds/loadersync/template.nja');
    });

    it('test Simple getSource sync', function() {
        var result;
        var callback = function(err, value) {
            result = value;
        };

        var simple_loader = new loader.SimpleLoader(this.registry);
        simple_loader.getSource(
            'nunja.testing.mold/basic/template.nja', callback);

        expect(result['src']).to.equal(
            '<span>{{ value }}</span>\n');
        expect(result['path']).to.equal(
            'nunja.testing.mold/basic/template.nja');
    });

});
