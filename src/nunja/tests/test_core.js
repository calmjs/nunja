'use strict';

var core = require('nunja/core');
var nunjucks = require('nunjucks');

window.mocha.setup('bdd');

/* istanbul ignore next */
var it_req_compiler = (
    (nunjucks.compiler.compile !== undefined) ||
    (window.nunjucksPrecompiled && window.nunjucksPrecompiled[
        'nunja.testing.mold/basic/template.nja'])) ? it : it.skip;

/* istanbul ignore next */
if (it_req_compiler === it.skip) {
    console.log(
        'resources from the nunja.mold.tests registry unavailable for use: ' +
        'the nunjucks compiler is unavailable or they are not available as ' +
        'precompiled templates; tests will be skipped'
    );
}

describe('Engine template core rendering', function() {
    beforeEach(function() {
        this.engine = core.engine;
    });

    afterEach(function() {
    });

    it_req_compiler('Core engine renders the correct template', function() {
        var results = this.engine.render(
            'nunja.testing.mold/basic', { value: 'Hello User' });
        expect(results).to.equal('<span>Hello User</span>\n');
    });

    it_req_compiler('Core engine executes the correct template', function() {
        var results = this.engine.execute(
            'nunja.testing.mold/basic', { value: 'Hello User' });
        expect(results).to.equal(
            '<div data-nunja="nunja.testing.mold/basic">\n' +
            '<span>Hello User</span>\n\n</div>\n'
        )
    });

});


describe('Engine main script loading error cases', function() {
    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.engine = core.engine;
    });

    afterEach(function() {
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it_req_compiler('An index.js not in AMD format', function() {
        document.body.innerHTML = (
            '<div data-nunja="nunja.testing.mold/problem"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);
    });

    it_req_compiler('An index.js AMD module without init', function() {
        document.body.innerHTML = (
            '<div data-nunja="nunja.testing.mold/noinit"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);
    });

});

describe('Engine main script loading and ui hooks', function() {
    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.engine = core.engine;
        // create new root element to aid cleanup.
        document.body.innerHTML = '<div id="root"></div>';
        this.rootEl = document.body.querySelector('#root');
    });

    afterEach(function() {
        document.body.innerHTML = "";
        this.clock.restore();
    });

    it_req_compiler('Mold index entry point triggered', function() {
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/itemlist"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        // Show that the hook fired as model was set.
        var element = this.rootEl.querySelector('div');
        expect(element).to.equal(element.model.element);
    });

    it_req_compiler('Basic in-place rendering', function() {
        // Note that this is manual, so formatting is different to
        // final result.
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample-list">\n' +
            '<li>Test Item</li>\n' +
            '</ul>\n' +
            '</div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        // now invoke the assigned model to the element and trigger
        // the render
        this.rootEl.querySelector('div').model.render();
        // should be different to what we assigned originally.
        expect(this.rootEl.innerHTML).to.equal(
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample-list">\n' +
            '\n' +
            '  <li>Test Item</li>\n' +
            '</ul>\n' +
            '</div>'
        );

    });

    it_req_compiler('Pure JS in-place rendering', function() {
        // Server would have only provided just the skeleton tag
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/itemlist"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        // The model would have been assigned; in alternative
        // implementations it could very well do the render in its
        // init, but here we trigger this manually to populate the
        // node with the empty list.
        this.rootEl.querySelector('div').model.render();
        expect(this.rootEl.innerHTML).to.equal(
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul>\n' +
            '\n' +
            '</ul>\n' +
            '</div>'
        );
    });

    it_req_compiler(
            'Event hooking onto parent/siblings of nunja node', function() {
        this.rootEl.innerHTML = (
            '<button class="reset">Reset</button>\n' +
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample">\n' +
            '</ul>\n' +
            '</div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);
        this.rootEl.querySelector('div').model.items = [
            'Manual 1', 'Manual 2'];
        this.rootEl.querySelector('.reset').click();
        expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
            '\n\n' +
            '  <li>Manual 1</li>\n' +
            '  <li>Manual 2</li>\n'
        );
    });

    it_req_compiler(
            'Event hooking and rehooking within nunja node', function() {
        this.rootEl.innerHTML = (
            '<button class="reset">Reset</button>\n' +
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample">\n' +
            '<li>Item 1</li>\n' +
            '<li>Item 2</li>\n' +
            '<li>Item 3</li>\n' +
            '<li>Item 4</li>\n' +
            '<li>Item 5</li>\n' +
            '<li>Item 6</li>\n' +
            '</ul>\n' +
            '</div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        var model = this.rootEl.querySelector('div').model;
        // remove first item
        this.rootEl.querySelectorAll('#sample li')[2].click();
        expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
            '\n' +
            '<li>Item 1</li>\n' +
            '<li>Item 2</li>\n' +
            '\n' +
            '<li>Item 4</li>\n' +
            '<li>Item 5</li>\n' +
            '<li>Item 6</li>\n'
        );
        expect(model.removeCount).to.equal(1);

        this.rootEl.querySelector('.reset').click();
        // restored to 6 elements and reset count be 1.
        expect(model.resetCount).to.equal(1);
        expect(this.rootEl.querySelectorAll('#sample li').length).to.equal(
            6);

        // event still hooked back into this re-rendered list.
        this.rootEl.querySelectorAll('#sample li')[4].click();
        // rendering now derived from template not hardcoded values.
        expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
            '\n\n' +
            '  <li>Item 1</li>\n' +
            '  <li>Item 2</li>\n' +
            '  <li>Item 3</li>\n' +
            '  <li>Item 4</li>\n' +
            '  \n' +
            '  <li>Item 6</li>\n'
        );

        // This should only increase by one, no double events.
        expect(model.removeCount).to.equal(2);

    });

    it_req_compiler('Mold isolation', function() {
        // need to be sure the events as is do not cross-pollinate.
        this.rootEl.innerHTML = (
            '<div id="n1">\n' +
            '<button class="reset">Reset</button>\n' +
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample1">\n' +
            '  <li>Sample 1</li>\n' +
            '</ul>\n' +
            '</div>' +
            '</div>' +

            '<div id="n2">\n' +
            '<button class="reset">Reset</button>\n' +
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul id="sample2">\n' +
            '  <li>Sample 2</li>\n' +
            '</ul>\n' +
            '</div>' +
            '</div>'
        );

        this.engine.do_onload(document.body);
        this.clock.tick(500);
        this.rootEl.querySelector('#n2 div').model.items = [
            'Resample 1', 'Resample 2'];

        this.rootEl.querySelector('#n1 .reset').click();
        expect(this.rootEl.querySelector('#sample2').innerHTML).to.equal(
            '\n' +
            '  <li>Sample 2</li>\n'
        );

        this.rootEl.querySelector('#n2 .reset').click();
        expect(this.rootEl.querySelector('#sample2').innerHTML).to.equal(
            '\n\n' +
            '  <li>Resample 1</li>\n' +
            '  <li>Resample 2</li>\n'
        );
        expect(this.rootEl.querySelector('#sample1').innerHTML).to.equal(
            '\n\n' +
            '  <li>Sample 1</li>\n'
        );

    });

});

describe('Support of imported template by data', function() {
    beforeEach(function() {
        this.clock = sinon.useFakeTimers();
        this.engine = core.engine;
        // create new root element to aid cleanup.
        document.body.innerHTML = '<div id="root"></div>';
        this.rootEl = document.body.querySelector('#root');
    });

    afterEach(function() {
        document.body.innerHTML = "";
        this.clock.restore();
    });

    it_req_compiler('Mold index entry point triggered', function() {
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/' +
                             'include_by_value"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        this.rootEl.querySelector('div').model.itemlists = [
            ['list_1', ['Item 1', 'Item 2']],
        ];
        // providing 'sample' as id to allow IE not omit element
        this.rootEl.querySelector('div').model.render('sample');

        expect(this.rootEl.querySelector('div').innerHTML).to.equal(
            '<dl id="sample">\n' +
            '\n' +
            '  <dt>list_1</dt>\n' +
            '  <dd><ul id="list_1">\n' +
            '\n' +
            '  <li>Item 1</li>\n' +
            '  <li>Item 2</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '</dl>\n'
        );

        // As this was basically rendered out of band, no init call
        // was made, so these events should be null
        this.rootEl.querySelector('li').click();
        expect(this.rootEl.querySelectorAll('li').length).to.equal(2);

        // XXX
        // So, how do we do this while providing actions?  Should
        // there be another rendering method that will also write
        // out the wrapper with the data-nunja stub so that the
        // parent can trigger the onload manually so that all the
        // init hooks will be automatically called on the re-
        // rendered results?
    });

    it_req_compiler('Rendering via manual include in for loop', function() {
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/' +
                             'include_by_value"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        this.rootEl.querySelector('div').model.itemlists = [
            ['list_1', ['Item 1', 'Item 2']],
            ['list_2', ['Item 3', 'Item 4']],
            ['list_3', ['Item 5', 'Item 6']],
        ];
        this.rootEl.querySelector('div').model.render('root_list');

        expect(this.rootEl.querySelector('div').innerHTML).to.equal(
            '<dl id="root_list">\n\n' +
            '  <dt>list_1</dt>\n' +
            '  <dd><ul id="list_1">\n\n' +
            '  <li>Item 1</li>\n' +
            '  <li>Item 2</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '  <dt>list_2</dt>\n' +
            '  <dd><ul id="list_2">\n\n' +
            '  <li>Item 3</li>\n' +
            '  <li>Item 4</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '  <dt>list_3</dt>\n' +
            '  <dd><ul id="list_3">\n\n' +
            '  <li>Item 5</li>\n' +
            '  <li>Item 6</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '</dl>\n'
        );
    });

    it_req_compiler('Rendering via named include in for loop', function() {
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/' +
                             'include_by_name"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        this.rootEl.querySelector('div').model.itemlists = [
            ['list_1', ['Item 1', 'Item 2']],
            ['list_2', ['Item 3', 'Item 4']],
            ['list_3', ['Item 5', 'Item 6']],
        ];
        this.rootEl.querySelector('div').model.render('root_list');

        expect(this.rootEl.querySelector('div').innerHTML).to.equal(
            '<dl id="root_list">\n\n' +
            '  <dt>list_1</dt>\n' +
            '  <dd><ul id="list_1">\n\n' +
            '  <li>Item 1</li>\n' +
            '  <li>Item 2</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '  <dt>list_2</dt>\n' +
            '  <dd><ul id="list_2">\n\n' +
            '  <li>Item 3</li>\n' +
            '  <li>Item 4</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '  <dt>list_3</dt>\n' +
            '  <dd><ul id="list_3">\n\n' +
            '  <li>Item 5</li>\n' +
            '  <li>Item 6</li>\n' +
            '</ul>\n' +
            '</dd>\n' +
            '</dl>\n'
        );
    });

});
