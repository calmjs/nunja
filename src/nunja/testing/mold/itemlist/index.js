define([
    'nunja/core',
], function(core) {
    'use strict';

    var Model = function(element) {
        this.resetCount = 0;
        this.removeCount = 0;
        this.element = element;
        // Is this early kind of implicit hooking a good idea as the
        // general case?
        this.hook();
    };

    Model.prototype.render = function () {
        var self = this;
        // This one does not poke to a server, but just reorders the
        // list locally here derived from pre-rendered data.
        core.engine.populate(this.element, {
            'list_id': this.id,
            'items': this.items,
        });
        self.hook();
    };

    Model.prototype.mkRemove = function (e) {
        var self = this;
        return function () {
            self.removeCount++;
            e && e.parentNode && e.parentNode.removeChild(e);
        };
    };

    Model.prototype.hook = function () {
        // bound for later usage in forloop.
        var self = this;
        var ul = this.element.querySelector('[id]');
        this.id = ul ? ul.getAttribute('id') : '';
        var items = [];
        var nodes = [];
        // generate pre-rendered data, as this mold does not make its
        // own xhr to source end-point (as no endpoints are defined).
        Array.prototype.slice.call(this.element.querySelectorAll('li')
            ).forEach(function (e) {
                nodes.push(e);
                e.addEventListener('click', self.mkRemove(e));
                items.push(e.textContent);
            });
        this.items = items;
        this.nodes = nodes;
    };

    Model.prototype.reset = function () {
        this.resetCount++;
        this.render();
    };

    var init = function(element) {
        // it is the init's responsiblity to hook things
        var model = new Model(element);
        var rootEl = element.parentElement;
        var resetEl = rootEl.querySelector('.reset');
        if (resetEl) {
            resetEl.addEventListener('click', function() {
                model.reset();
            });
        }

        element.model = model;
    };

    // Thought: core.render should in theory be able to render _any_
    // templates that it knows - could simply define multiple molds and
    // only call the limited internal ones.

    // Now how does this fit together with other JS frameworks (like
    // backbone)?  I have no idea yet.

    return {
        'init': init
    };
});
