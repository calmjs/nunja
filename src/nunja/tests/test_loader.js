'use strict';

var registry = require('nunja/registry');
var loader = require('nunja/loader');

window.mocha.setup('bdd');


describe('nunja/loader test case', function() {
    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        this.server.respondWith(
            'GET', '/base/mock.molds/loaderasync/template.nja',
            function (xhr, id) {
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

        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
    });

    afterEach(function() {
        requirejs.undef('text!mock.molds/loaderasync/template.nja');
        requirejs.undef('text!mock.molds/loadersync/template.nja');
        this.server.restore();
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it('test getSource async', function() {
        var result;
        var callback = function(err, value) {
            result = value;
        };

        this.loader.getSource('mock.molds/loaderasync/template.nja', callback);
        this.clock.tick(500);

        expect(result['src']).to.equal(
            '<span>Integrated mocked template async: {{ msg }}</span>');
        expect(result['path']).to.equal('mock.molds/loaderasync/template.nja');
    });

    it('test getSource sync', function() {
        var result;
        var callback = function(err, value) {
            result = value;
        };

        define('text!mock.molds/loadersync/template.nja', [], function() {
            return '<span>Manual defined sync: {{ msg }}</span>';
        });
        this.clock.tick(500);

        this.loader.getSource('mock.molds/loadersync/template.nja', callback);
        this.clock.tick(500);

        expect(result['src']).to.equal(
            '<span>Manual defined sync: {{ msg }}</span>');
        expect(result['path']).to.equal('mock.molds/loadersync/template.nja');
    });

});
