'use strict';

var core = require('nunja/core');
window.mocha.setup('bdd');

describe('Basic nunja.molds/table rendering', function() {
    beforeEach(function() {
        this.engine = core.engine;

        // A barebone mock scaffold that should be enough to trigger
        // the loading and compilation of the template into memory,
        // if it's not there already.
        document.body.innerHTML = (
            '<div data-nunja="nunja.molds/table"></div>');
    });

    afterEach(function() {
        document.body.innerHTML = "";
    });

    it('Null rendering', function() {
        var results = this.engine.render('nunja.molds/table', {
            'active_columns': [],
            'column_map': {},
            'data': [],
            'css': {},
        });

        expect(results).to.equal(
            '<table class="">\n' +
            '  <thead>\n' +
            '    <tr class="">\n' +
            '    \n' +
            '    </tr>\n' +
            '  </thead>\n' +
            '  <tbody>\n' +
            '    \n' +
            '  </tbody>\n' +
            '</table>\n'
        );
    });

    it('Basic data rendering', function() {
        var results = this.engine.render('nunja.molds/table', {
            'active_columns': ['id', 'name'],
            'column_map': {
                'id': 'Id',
                'name': 'Given Name',
            },
            'data': [
                {'id': '1', 'name': 'John Smith'},
                {'id': '2', 'name': 'Eve Adams'},
            ],
            'css': {},

        });
        expect(results).to.equal(
            '<table class="">\n' +
            '  <thead>\n' +
            '    <tr class="">\n' +
            '    <td>Id</td><td>Given Name</td>\n' +
            '    </tr>\n' +
            '  </thead>\n' +
            '  <tbody>\n' +
            '    <tr class="">\n' +
            '      <td>1</td><td>John Smith</td>\n' +
            '    </tr><tr class="">\n' +
            '      <td>2</td><td>Eve Adams</td>\n' +
            '    </tr>\n' +
            '  </tbody>\n' +
            '</table>\n'
        );
    });

});
