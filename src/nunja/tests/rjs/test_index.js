'use strict';

window.mocha.setup('bdd');

describe('nunja/engine simple test case', function() {

    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
    });

    afterEach(function() {
        this.clock.restore();
        document.body.innerHTML = '';
    });

    it('test onload event registered', function() {
        document.body.innerHTML = '<div data-nunja="dummy/fake"></div>';
        var called = false;

        // define and preload the template and module.
        define('text!dummy/fake/template.nja', [], function () {
            return 'fake';
        });
        require(['text!dummy/fake/template.nja'], function() {});
        define('dummy/fake/index', [], function () {
            return {'init': function() {
                called = true;
            }};
        });
        require(['dummy/fake/index'], function() {});
        // ensure the modules are available.
        this.clock.tick(500);

        // emulate the import call trigger
        require('nunja/index').main();
        this.clock.tick(500);
        expect(called).to.be.true;
    });

});
