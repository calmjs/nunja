'use strict';

var core = require('nunja/core');
window.mocha.setup('bdd');

describe('Basic nunja.molds/navtable rendering', function() {
    beforeEach(function() {
        this.engine = core.engine;

        // A barebone mock scaffold that should be enough to trigger
        // the loading and compilation of the template into memory,
        // if it's not there already.
        document.body.innerHTML = (
            '<div data-nunja="nunja.molds/navtable"></div>');
    });

    afterEach(function() {
        document.body.innerHTML = "";
    });

    it('Null rendering', function() {
        var results = this.engine.render('nunja.molds/navtable', {
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
        var results = this.engine.render('nunja.molds/navtable', {
            'active_columns': ['name', 'desc', 'size'],
            'column_map': {
                'name': 'Name',
                'desc': 'Description',
                'size': 'Size',
            },
            'data': [
                {'size': '9', '@id': 'http://example.com/documents',
                    'name': 'documents', 'desc': 'My Documents'},
                {'size': '43', '@id': 'http://example.com/pictures',
                    'name': 'pictures', 'desc': 'My Pictures'},
                {'size': '0', '@id': 'http://example.com/videos',
                    'name': 'videos', 'desc': 'My Videos'},
                {'size': '100', '@id': '',
                    'name': 'file', 'desc': 'A File'},
            ],
            'css': {},
        });

        expect(results).to.equal(
            '<table class="">\n' +
            '  <thead>\n' +
            '    <tr class="">\n' +
            '    <td>Name</td><td>Description</td><td>Size</td>\n' +
            '    </tr>\n' +
            '  </thead>\n' +
            '  <tbody>\n' +
            '    <tr class="">\n' +
            '      <td><a href="http://example.com/documents">documents' +
            '</a></td><td>My Documents</td><td>9</td>\n' +
            '    </tr><tr class="">\n' +
            '      <td><a href="http://example.com/pictures">pictures' +
            '</a></td><td>My Pictures</td><td>43</td>\n' +
            '    </tr><tr class="">\n' +
            '      <td><a href="http://example.com/videos">videos' +
            '</a></td><td>My Videos</td><td>0</td>\n' +
            '    </tr><tr class="">\n' +
            '      <td>file</td><td>A File</td><td>100</td>\n' +
            '    </tr>\n' +
            '  </tbody>\n' +
            '</table>\n'
        );

    });

});
