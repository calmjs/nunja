'use strict';

var registry = require('nunja/registry');


describe('nunja/registry test case', function() {

    beforeEach(function() {
        this.registry = new registry.Registry();
    });

    it('name_to_mold_id standard', function() {
        expect(this.registry.name_to_mold_id('ns.pkg/name/tmpl.nja')
            ).to.equal('ns.pkg/name');
        expect(this.registry.name_to_mold_id('ns.pkg/name/nested/tmpl.nja')
            ).to.equal('ns.pkg/name');
        // users shouldn't expect this to work, but it works like this
        // now so document it as such.
        expect(this.registry.name_to_mold_id('ns.pkg/name/data.json')
            ).to.equal('ns.pkg/name');
    });

    it('name_to_mold_id badvalue', function() {
        expect(this.registry.name_to_mold_id('ns.pkg/name.tmpl')).to.be.null;
        expect(this.registry.name_to_mold_id('ns.pkg.nja')).to.be.null;
    });

});
