'use strict';

var loader = require('nunja/loader');
var core = require('nunja/core');
var registry = require('nunja/registry');

/* istanbul ignore next */
var nunja_testing_mold_skip = (function() {
    try {
        require('__nunja__/nunja.testing.mold/basic');
    } catch (e) {
        try {
            require('text!nunja.testing.mold/basic/template.nja');
        } catch(e) {
            console.log(
                "nunja/core/tests/test_core " +
                "requires resources from the 'nunja.mold.testing' registry " +
                "must be made available as part of the source registries"
            );
            return function(self) { self.skip(); };
        }
    }
    return function(){};
})();

window.mocha.setup('bdd');


describe('nunja/loader sync path test case', function() {
    // follows the synchronous path

    beforeEach(function() {
        nunja_testing_mold_skip(this);
        this.registry = new registry.Registry();
        this.loader = new loader.NunjaLoader(this.registry);
    });

    it('test getSource sync with callback', function() {
        // assuming the sources are available (either compiled in or
        // available via RequireJS.
        var result;
        var callback = function(err, value) {
            result = value;
        };

        this.loader.getSource(
            'nunja.testing.mold/basic/template.nja', callback);

        expect(result['src']).to.equal(
            '<span>{{ value }}</span>\n');
        expect(result['path']).to.equal(
            'nunja.testing.mold/basic/template.nja');
    });

});


describe('Engine template core rendering', function() {
    beforeEach(function() {
        nunja_testing_mold_skip(this);
        this.engine = core.engine;
    });

    afterEach(function() {
    });

    it('Core engine renders the correct template', function() {
        var results = this.engine.render(
            'nunja.testing.mold/basic', { value: 'Hello User' });
        expect(results).to.equal('<span>Hello User</span>\n');
    });

    it('Core engine executes the correct template', function() {
        var results = this.engine.execute(
            'nunja.testing.mold/basic', { value: 'Hello User' });
        expect(results).to.equal(
            '<div data-nunja="nunja.testing.mold/basic">\n' +
            '<span>Hello User</span>\n\n</div>\n'
        );
    });

});


describe('Engine main script loading error cases', function() {
    beforeEach(function() {
        nunja_testing_mold_skip(this);
        this.clock = sinon.useFakeTimers();
        this.engine = core.engine;
    });

    afterEach(function() {
        this.clock.restore();
        document.body.innerHTML = "";
    });

    it('An index.js not in AMD format', function() {
        document.body.innerHTML = (
            '<div data-nunja="nunja.testing.mold/problem"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);
    });

    it('An index.js AMD module without init', function() {
        document.body.innerHTML = (
            '<div data-nunja="nunja.testing.mold/noinit"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);
    });

});

describe('Engine main script loading and ui hooks', function() {
    beforeEach(function() {
        nunja_testing_mold_skip(this);
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

    it('Mold index entry point triggered', function() {
        this.rootEl.innerHTML = (
            '<div data-nunja="nunja.testing.mold/itemlist"></div>'
        );
        this.engine.do_onload(document.body);
        this.clock.tick(500);

        // Show that the hook fired as model was set.
        var element = this.rootEl.querySelector('div');
        expect(element).to.equal(element.model.element);
    });

    it('Basic in-place rendering', function() {
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
        this.clock.tick(500);
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

    it('Pure JS in-place rendering', function() {
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
        this.clock.tick(500);
        expect(this.rootEl.innerHTML).to.equal(
            '<div data-nunja="nunja.testing.mold/itemlist">' +
            '<ul>\n' +
            '\n' +
            '</ul>\n' +
            '</div>'
        );
    });

    it('Event hooking onto parent/siblings of nunja node', function() {
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
        this.clock.tick(500);
        expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
            '\n\n' +
            '  <li>Manual 1</li>\n' +
            '  <li>Manual 2</li>\n'
        );
    });

    it('Event hooking and rehooking within nunja node', function() {
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
        this.clock.tick(500);
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
        this.clock.tick(500);
        // restored to 6 elements and reset count be 1.
        expect(model.resetCount).to.equal(1);
        expect(this.rootEl.querySelectorAll('#sample li').length).to.equal(
            6);

        // event still hooked back into this re-rendered list.
        this.rootEl.querySelectorAll('#sample li')[4].click();
        this.clock.tick(500);
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

    it('Mold isolation', function() {
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
        this.clock.tick(500);
        expect(this.rootEl.querySelector('#sample2').innerHTML).to.equal(
            '\n' +
            '  <li>Sample 2</li>\n'
        );

        this.rootEl.querySelector('#n2 .reset').click();
        this.clock.tick(500);
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
        nunja_testing_mold_skip(this);
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

    it('Mold index entry point triggered', function() {
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
        this.clock.tick(500);

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
        this.clock.tick(500);
        expect(this.rootEl.querySelectorAll('li').length).to.equal(2);

        // XXX
        // So, how do we do this while providing actions?  Should
        // there be another rendering method that will also write
        // out the wrapper with the data-nunja stub so that the
        // parent can trigger the onload manually so that all the
        // init hooks will be automatically called on the re-
        // rendered results?
    });

    it('Rendering via manual include in for loop', function() {
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
        this.clock.tick(500);

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

    it('Rendering via named include in for loop', function() {
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
        this.clock.tick(500);

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
