YUI.add("charrousel-timer", function(t) {
  var a = t.Lang;
  t.CharrouselTimer = t.Base.create("charrousel-timer", t.Plugin.Base, [], {
    initializer: function() {
      var t = this;
      t._host = t.get("host"), t._circular = t._host.get("circular"), t._handles = [t._host.after("render", t._setup, t), t._host.after("pageChange", t._pageChange, t), t._host.after("circularChange", function(e) {
        t._circular = e.newVal
      }, t), t.after("delayChange", t._setup)]
    },
    destructor: function() {
      var e = this;
      new t.EventTarget(e._handles).detach(), e._cancel(), delete e._timer, delete e._circular
    },
    _cancel: function() {
      var e = this;
      e._timer && a.isFunction(e._timer.cancel) && e._timer.cancel()
    },
    _setup: function() {
      var e = this;
      e._cancel(), e._timer = t.later(e.get("delay"), e, e._pulse)
    },
    _pulse: function() {
      var e = this,
        t = e._host.get("page");
      e._circular || t + 1 < e._host._pages ? e._host.next() : e._host.set("page", 0), e._setup()
    },
    _pageChange: function(e) {
      this[e.source && -1 < e.source.indexOf("click") ? "_cancel" : "_setup"]()
    }
  }, {
    NS: "timer",
    ATTRS: {
      delay: {
        value: 5e3
      }
    }
  })
}, "@VERSION@", {
  requires: ["charrousel-widget", "base-build", "plugin"]
});