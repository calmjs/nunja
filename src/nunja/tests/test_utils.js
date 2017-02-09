'use strict';

var utils = require('nunja/utils');
var $ = utils.$;
var addEventListeners = utils.addEventListeners;

window.mocha.setup('bdd');

describe('nunja/utils test cases', function() {
    beforeEach(function() {
        document.body.innerHTML = [
            '<ul id="main">',
            '<li data-dummy="foo">test1</li>',
            '<li data-dummy="bar">test2</li>',
            '<li data-other="alt">test3</li>',
            '<li data-dummy="baz">test4</li>',
            '</ul>',
            '<ul id="other">',
            '<li data-other="tab">test5</li>',
            '</ul>',
        ].join('');
    });

    afterEach(function() {
        document.body.innerHTML = "";
    });

    it('Selector', function() {
        expect($('[data-dummy]').length).to.equal(3);
        expect($('[data-dummy]').length).to.equal(3);
        expect($('[data-dummy="foo"]').length).to.equal(1);

        expect($('[data-other]').length).to.equal(2);
        expect($('[data-other]', $('#main')[0]).length).to.equal(1);
    });

    it('addEventListeners', function() {
        var target = $('[data-dummy="foo"]')[0];
        target.click();
        expect(target.dummy).to.be.undefined;

        addEventListeners($('[data-dummy]'), 'click', function(ev) {
            ev.target.dummy = 'set';
        });

        target.click();
        expect(target.dummy).to.equal('set');
    });

});
