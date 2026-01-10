YUI.add("targetedMediaPlayer-widget", function(a) {
  var e = a.ClassNameManager.getClassName;
  a.TargetedMediaPlayer = a.Base.create("targetedMediaPlayer", a.Widget, [a.MediaCenterBase], {
    initializer: function() {},
    destructor: function() {},
    renderUI: function() {},
    bindUI: function() {
      var t = this,
        e = this.get("domItems");
      this._handles.push(a.all(e).on("click", function(e) {
        return t._domItemSelected(e.target), e.preventDefault(), !1
      }, "a"))
    },
    syncUI: function() {},
    _getCoreMediaLocation: function() {
      var e = this.get("targetSelector");
      return e ? a.one(e) : null
    },
    _getMainContentArea: function() {
      return this._getCoreMediaLocation()
    }
  }, {
    ATTRS: {
      domItems: {
        value: null
      },
      targetSelector: {
        value: null
      }
    },
    CLASSNAMES: {
      overlay: e("lightbox", "overlay"),
      overlay_bg: e("lightbox", "overlay-bg"),
      body: e("lightbox", "body"),
      body_bg: e("lightbox", "body-bg"),
      image: e("lightbox", "image"),
      loading: e("lightbox", "loading"),
      prev: e("lightbox", "prev"),
      next: e("lightbox", "next"),
      close: e("lightbox", "close")
    }
  })
}, "@VERSION@", {
  requires: ["mediaCenter-base", "base-build", "widget-base", "dom-screen", "node-base", "node-event-delegate", "selector-css3", "transition"]
});