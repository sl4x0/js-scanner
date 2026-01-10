YUI.add("charrousel-fade", function(a) {
  var n = {
      hiding: (0, a.ClassNameManager.getClassName)("charrousel", "item", "hiding")
    },
    h = a.Charrousel.CLASSNAMES;
  a.CharrouselFade = a.Base.create("charrousel-fade", a.Plugin.Base, [], {
    initializer: function() {
      var e = this;
      e._host = e.get("host"), e._handles = [e.on("transitionChange", e._transitionChange)], e._host.once("render", function() {
        e._handles.push(e._host.on("pageChange", e._pageChange, e))
      }), e._transitionChange()
    },
    destructor: function() {
      new a.EventTarget(this._handles).detach(), this._handles = this._hide = this._show = null
    },
    _transitionChange: function(e) {
      e = e && e.newVal || this.get("transition");
      this._hide = a.merge(e.base, e.hide), this._show = a.merge(e.base, e.show)
    },
    _pageChange: function(e) {
      var a = this,
        s = (a._host.get("items"), a._host.get("visible"), a._host.pageItems(e.prevVal)),
        t = a._host.pageItems(e.newVal),
        i = n.hiding;
      t.setStyle("opacity", 0), t.addClass(h.current.item), s.addClass(i), s.transition(a._hide, function() {
        this.removeClass(i), a.fire("moved", {
          prevVal: e.prevVal,
          newVal: e.newVal
        })
      }), t.transition(a._show)
    }
  }, {
    NS: "fade",
    ATTRS: {
      transition: {
        value: {
          base: {
            easing: "ease-in",
            duration: .25
          },
          hide: {
            opacity: 0
          },
          show: {
            opacity: 1,
            delay: .125
          }
        }
      }
    }
  })
}, "@VERSION@", {
  requires: ["charrousel-widget", "base-build", "plugin", "transition"]
});