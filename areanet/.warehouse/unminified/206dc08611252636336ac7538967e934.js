YUI.add("lightbox-widget", function(l) {
  var g = l.Lang,
    e = l.ClassNameManager.getClassName;

  function t() {
    return {
      overlay: !1,
      overlayBg: !1,
      body: !1,
      bodyBg: !1,
      image: !1,
      loading: !1,
      prev: !1,
      next: !1,
      close: !1
    }
  }
  l.Lightbox = l.Base.create("lightbox", l.Widget, [l.LightboxBase], {
    _selector: !1,
    _nodes: t(),
    _preloadImage: new Image,
    _nextImage: new Image,
    _timer: null,
    TEMPLATES: {
      overlay: "<div class='{css}'></div>",
      overlayBg: "<div class='{css}'></div>",
      body: "<div class='{css}'></div>",
      bodyBg: "<div class='{css}'><img></div>",
      image: "<div class='{css}'><img><img></div>",
      loading: "<div class='{css}'></div>",
      prev: "<div class='{css}'></div>",
      next: "<div class='{css}'></div>",
      close: "<div class='{css}'></div>"
    },
    SCROLLBARSIZE: {
      x: 38,
      y: 38
    },
    initializer: function() {
      this._nodes = this._buildNodes()
    },
    destructor: function() {
      this._nodes && (this._nodes.overlay.destroy(), this._nodes = null)
    },
    renderUI: function() {
      var e = this._nodes.overlay,
        t = this._nodes.bodyBg,
        i = this._nodes.loading;
      this.get("contentBox").append(e), this.close(!0), (e = t.getComputedStyle("backgroundImage")) && g.isString(e) ? ("url(" === e.substr(0, 4) && (e = (e = e.substr(4, e.length - 5)).replace(/"/g, "")), t.setStyle("background", "transparent"), t.one("img").setAttribute("src", e)) : t.one("img").hide(), this._isAnimationSupported(i) && i.addClass("use-animation")
    },
    bindUI: function() {
      var t, i, o = this,
        e = o.get("items"),
        n = o._nodes.overlay,
        a = o._nodes.overlayBg,
        s = o._nodes.prev,
        r = o._nodes.next,
        d = o._nodes.close;
      n.delegate("click", function(e) {
        e.preventDefault(), e.currentTarget === s ? o.prev() : e.currentTarget === r ? o.next() : e.currentTarget !== d && e.currentTarget !== a || o.close()
      }, "div"), t = function(e) {
        e.preventDefault(), o.move(this.getData("lightbox-index"))
      }, g.isString(o._selector) && 0 < o._selector.indexOf(" ") ? (i = o._selector.split(" ", 2), l.all(i[0]).each(function(e) {
        l.delegate("click", t, e, i[1])
      })) : e.each(function(e) {
        e.on("click", t)
      }), o.on("imageChange", function(e) {
        e.newVal && o._loadImage(e.newVal)
      }), o.on("indexChange", function() {
        o._preloadImage.src = o.nextImage()
      })
    },
    syncUI: function() {
      var e = this,
        t = e._nodes.prev,
        i = e._nodes.next;
      e.get("images").length <= 1 ? (t.hide(), i.hide()) : (t.show(), i.show())
    },
    _isAnimationSupported: function(t) {
      var e = "Webkit Moz O ms Khtml".split(" ");
      return !!(t = t._node ? t._node : t).style.animationName || l.Array.some(e, function(e) {
        return void 0 !== t.style[e + "AnimationName"]
      })
    },
    _buildNodes: function() {
      var i, o = l.Lightbox.CLASSNAMES,
        n = this.get("classes"),
        a = t();
      return l.Object.each(this.TEMPLATES, function(e, t) {
        i = g.sub(e, {
          css: [o[t] || "", n[t] || ""].join(" ")
        }), a[t] = l.Node.create(i)
      }), a.overlay.append(a.overlayBg), a.overlay.append(a.body), a.body.append(a.bodyBg), a.body.append(a.image), a.body.append(a.loading), a.body.append(a.prev), a.body.append(a.next), a.body.append(a.close), a.overlay.hide(), a
    },
    close: function(e) {
      var t = this,
        i = t._nodes.overlay,
        o = t._nodes.overlayBg,
        n = t._nodes.body,
        a = t._nodes.image,
        s = t._nodes.prev,
        r = t._nodes.next,
        d = t._calculateBodySize(200, 200);
      n.setStyles({
        display: "none",
        left: d.left + "px",
        top: d.top + "px",
        width: d.width + "px",
        height: d.height + "px"
      }), e ? i.hide() : o.setStyle("opacity", t.get("overlayOpacity")).transition({
        opacity: 0,
        duration: t.get("resizeDuration") / 2
      }, function() {
        i.hide()
      }), a.all("img").setAttribute("src", "data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw%3D%3D"), s.hide(), r.hide()
    },
    _loadImage: function(e) {
      var o = this,
        n = o._nextImage,
        t = o._nodes.overlay,
        i = o._nodes.overlayBg,
        a = o._nodes.body,
        s = o._nodes.loading;
      t.show(), i.transition({
        opacity: o.get("overlayOpacity"),
        duration: o.get("resizeDuration") / 2
      }), a.show(), o._timer && o._timer.cancel(), o._timer = l.later(250, o, function() {
        s.show(!0), o._timer = null
      }), n.onload = function() {
        var e = n.src,
          t = n.width,
          i = n.height;
        o._timer && o._timer.cancel(), s.hide(!0), o._setImage(e, t, i)
      }, n.src === e ? n.onload() : n.src = e
    },
    _setImage: function(e, t, i) {
      var o = this,
        n = o._nodes.body,
        t = o._calculateBodySize(t, i),
        i = o._nodes.image;
      o.syncUI(), o._swapImages(), n.transition({
        easing: "linear",
        left: t.left + "px",
        top: t.top + "px",
        width: t.width + "px",
        height: t.height + "px",
        duration: o.get("resizeDuration")
      }), i.one("img:first-child").transition({
        opacity: 0,
        duration: o.get("resizeDuration")
      }), i.one("img:last-child").setAttribute("src", e).transition({
        opacity: 1,
        duration: o.get("resizeDuration")
      })
    },
    _swapImages: function() {
      var e = this._nodes.image,
        t = e.one("img");
      t.detach(), e.append(t)
    },
    _getNodeSpacing: function(o, e) {
      var n = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0,
        x: 0,
        y: 0
      };
      return l.Array.each(["Left", "Top", "Right", "Bottom"], function(t) {
        var i = 0;
        l.Array.each(e, function(e) {
          i += parseInt(o.getComputedStyle(e + t), 10) || 0
        }), n[t.toLowerCase()] = i
      }), n.x = n.left + n.right, n.y = n.top + n.bottom, n
    },
    _getConstrainedSize: function(e, t, i, o) {
      var n = e / t,
        a = l.DOM.winWidth() - i.x - o.x - this.SCROLLBARSIZE.x,
        i = l.DOM.winHeight() - i.y - o.y - this.SCROLLBARSIZE.y;
      return {
        width: e = i < (t = a < e ? (e = a) / n : t) ? (t = i) * n : e,
        height: t
      }
    },
    _calculateBodySize: function(e, t) {
      var i = this._nodes.body,
        o = this._getNodeSpacing(i, ["margin", "border"]),
        i = this._getNodeSpacing(i, ["padding"]),
        e = this._getConstrainedSize(e, t, o, i),
        t = l.DOM.winWidth() - o.x - this.SCROLLBARSIZE.x,
        o = l.DOM.winHeight() - o.y - this.SCROLLBARSIZE.y,
        n = e.width + i.x,
        e = e.height + i.y;
      return {
        left: t / 2 - n / 2,
        top: o / 2 - e / 2,
        width: n,
        height: e
      }
    }
  }, {
    ATTRS: {
      items: {
        setter: function(e) {
          var i = [];
          return g.isString(e) && (this._selector = e, e = l.all(e)), e.each(function(e) {
            var t = e.one("a"),
              t = t && t.get("href");
            t && (e.setData("lightbox-index", i.length), e.setData("lightbox-url", t), i.push(t))
          }), this.set("images", i), e
        }
      },
      resizeDuration: {
        value: 0,
        validator: g.isNumber
      },
      overlayOpacity: {
        value: .8,
        validator: g.isNumber
      },
      classes: {
        value: t()
      }
    },
    CLASSNAMES: {
      overlay: e("lightbox", "overlay"),
      overlayBg: e("lightbox", "overlay-bg"),
      body: e("lightbox", "body"),
      bodyBg: e("lightbox", "body-bg"),
      image: e("lightbox", "image"),
      loading: e("lightbox", "loading"),
      prev: e("lightbox", "prev"),
      next: e("lightbox", "next"),
      close: e("lightbox", "close")
    }
  })
}, "@VERSION@", {
  requires: ["lightbox-base", "base-build", "widget-base", "dom-screen", "node-base", "node-event-delegate", "selector-css3", "transition"]
});