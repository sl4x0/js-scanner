YUI.add("mediaCenterLightboxFadeAnimationPlugin", function(o) {
  o.MediaCenterLightboxFadeAnimation = o.Base.create("mediaCenterLightboxFadeAnimationPlugin", o.Plugin.Base, [], {
    initializer: function() {
      this._host = this.get("host"), this._host.lbAnimations && (this._host.lbAnimations.fade = this)
    },
    destructor: function() {},
    show: function(i, t) {
      var e = i.get("region"),
        n = o.DOM.winHeight(),
        a = o.DOM.winWidth();
      i.setStyles({
        position: "fixed",
        zIndex: 99999,
        opacity: 0,
        display: "block",
        top: Math.round((n - e.height) / 2) + "px",
        left: Math.round((a - e.width) / 2) + "px"
      }), i.transition({
        opacity: 1,
        duration: this.get("resizeDuration")
      }), t()
    },
    hide: function(i, t) {
      i.transition({
        opacity: 0,
        duration: this.get("resizeDuration")
      }, t)
    }
  }, {
    NS: "lbFadeAnimi",
    ATTRS: {
      resizeDuration: {
        value: .2
      }
    }
  })
}, "@VERSION@", {
  requires: ["mediaCenter-base", "base-build", "plugin"]
});