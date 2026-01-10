! function e(t, n, o) {
  function i(a, c) {
    if (!n[a]) {
      if (!t[a]) {
        var s = "function" == typeof require && require;
        if (!c && s) return s(a, !0);
        if (r) return r(a, !0);
        var u = new Error("Cannot find module '" + a + "'");
        throw u.code = "MODULE_NOT_FOUND", u
      }
      var l = n[a] = {
        exports: {}
      };
      t[a][0].call(l.exports, (function(e) {
        return i(t[a][1][e] || e)
      }), l, l.exports, e, t, n, o)
    }
    return n[a].exports
  }
  for (var r = "function" == typeof require && require, a = 0; a < o.length; a++) i(o[a]);
  return i
}({
  1: [function(e, t, n) {
    ! function() {
      "use strict";
      /**
       * @preserve FastClick: polyfill to remove click delays on browsers with touch UIs.
       *
       * @codingstandard ftlabs-jsv2
       * @copyright The Financial Times Limited [All Rights Reserved]
       * @license MIT License (see LICENSE.txt)
       */
      function e(t, n) {
        var i;
        if (n = n || {}, this.trackingClick = !1, this.trackingClickStart = 0, this.targetElement = null, this.touchStartX = 0, this.touchStartY = 0, this.lastTouchIdentifier = 0, this.touchBoundary = n.touchBoundary || 10, this.layer = t, this.tapDelay = n.tapDelay || 200, this.tapTimeout = n.tapTimeout || 700, !e.notNeeded(t)) {
          for (var r = ["onMouse", "onClick", "onTouchStart", "onTouchMove", "onTouchEnd", "onTouchCancel"], a = this, c = 0, s = r.length; c < s; c++) a[r[c]] = u(a[r[c]], a);
          o && (t.addEventListener("mouseover", this.onMouse, !0), t.addEventListener("mousedown", this.onMouse, !0), t.addEventListener("mouseup", this.onMouse, !0)), t.addEventListener("click", this.onClick, !0), t.addEventListener("touchstart", this.onTouchStart, !1), t.addEventListener("touchmove", this.onTouchMove, !1), t.addEventListener("touchend", this.onTouchEnd, !1), t.addEventListener("touchcancel", this.onTouchCancel, !1), Event.prototype.stopImmediatePropagation || (t.removeEventListener = function(e, n, o) {
            var i = Node.prototype.removeEventListener;
            "click" === e ? i.call(t, e, n.hijacked || n, o) : i.call(t, e, n, o)
          }, t.addEventListener = function(e, n, o) {
            var i = Node.prototype.addEventListener;
            "click" === e ? i.call(t, e, n.hijacked || (n.hijacked = function(e) {
              e.propagationStopped || n(e)
            }), o) : i.call(t, e, n, o)
          }), "function" == typeof t.onclick && (i = t.onclick, t.addEventListener("click", (function(e) {
            i(e)
          }), !1), t.onclick = null)
        }

        function u(e, t) {
          return function() {
            return e.apply(t, arguments)
          }
        }
      }
      var n = navigator.userAgent.indexOf("Windows Phone") >= 0,
        o = navigator.userAgent.indexOf("Android") > 0 && !n,
        i = /iP(ad|hone|od)/.test(navigator.userAgent) && !n,
        r = i && /OS 4_\d(_\d)?/.test(navigator.userAgent),
        a = i && /OS [6-7]_\d/.test(navigator.userAgent),
        c = navigator.userAgent.indexOf("BB10") > 0;
      e.prototype.needsClick = function(e) {
        switch (e.nodeName.toLowerCase()) {
          case "button":
          case "select":
          case "textarea":
            if (e.disabled) return !0;
            break;
          case "input":
            if (i && "file" === e.type || e.disabled) return !0;
            break;
          case "label":
          case "iframe":
          case "video":
            return !0
        }
        return /\bneedsclick\b/.test(e.className)
      }, e.prototype.needsFocus = function(e) {
        switch (e.nodeName.toLowerCase()) {
          case "textarea":
            return !0;
          case "select":
            return !o;
          case "input":
            switch (e.type) {
              case "button":
              case "checkbox":
              case "file":
              case "image":
              case "radio":
              case "submit":
                return !1
            }
            return !e.disabled && !e.readOnly;
          default:
            return /\bneedsfocus\b/.test(e.className)
        }
      }, e.prototype.sendClick = function(e, t) {
        var n, o;
        document.activeElement && document.activeElement !== e && document.activeElement.blur(), o = t.changedTouches[0], (n = document.createEvent("MouseEvents")).initMouseEvent(this.determineEventType(e), !0, !0, window, 1, o.screenX, o.screenY, o.clientX, o.clientY, !1, !1, !1, !1, 0, null), n.forwardedTouchEvent = !0, e.dispatchEvent(n)
      }, e.prototype.determineEventType = function(e) {
        return o && "select" === e.tagName.toLowerCase() ? "mousedown" : "click"
      }, e.prototype.focus = function(e) {
        var t;
        i && e.setSelectionRange && 0 !== e.type.indexOf("date") && "time" !== e.type && "month" !== e.type ? (t = e.value.length, e.setSelectionRange(t, t)) : e.focus()
      }, e.prototype.updateScrollParent = function(e) {
        var t, n;
        if (!(t = e.fastClickScrollParent) || !t.contains(e)) {
          n = e;
          do {
            if (n.scrollHeight > n.offsetHeight) {
              t = n, e.fastClickScrollParent = n;
              break
            }
            n = n.parentElement
          } while (n)
        }
        t && (t.fastClickLastScrollTop = t.scrollTop)
      }, e.prototype.getTargetElementFromEventTarget = function(e) {
        return e.nodeType === Node.TEXT_NODE ? e.parentNode : e
      }, e.prototype.onTouchStart = function(e) {
        var t, n, o;
        if (e.targetTouches.length > 1) return !0;
        if (t = this.getTargetElementFromEventTarget(e.target), n = e.targetTouches[0], i) {
          if ((o = window.getSelection()).rangeCount && !o.isCollapsed) return !0;
          if (!r) {
            if (n.identifier && n.identifier === this.lastTouchIdentifier) return e.preventDefault(), !1;
            this.lastTouchIdentifier = n.identifier, this.updateScrollParent(t)
          }
        }
        return this.trackingClick = !0, this.trackingClickStart = e.timeStamp, this.targetElement = t, this.touchStartX = n.pageX, this.touchStartY = n.pageY, e.timeStamp - this.lastClickTime < this.tapDelay && e.preventDefault(), !0
      }, e.prototype.touchHasMoved = function(e) {
        var t = e.changedTouches[0],
          n = this.touchBoundary;
        return Math.abs(t.pageX - this.touchStartX) > n || Math.abs(t.pageY - this.touchStartY) > n
      }, e.prototype.onTouchMove = function(e) {
        return !this.trackingClick || ((this.targetElement !== this.getTargetElementFromEventTarget(e.target) || this.touchHasMoved(e)) && (this.trackingClick = !1, this.targetElement = null), !0)
      }, e.prototype.findControl = function(e) {
        return void 0 !== e.control ? e.control : e.htmlFor ? document.getElementById(e.htmlFor) : e.querySelector("button, input:not([type=hidden]), keygen, meter, output, progress, select, textarea")
      }, e.prototype.onTouchEnd = function(e) {
        var t, n, c, s, u, l = this.targetElement;
        if (!this.trackingClick) return !0;
        if (e.timeStamp - this.lastClickTime < this.tapDelay) return this.cancelNextClick = !0, !0;
        if (e.timeStamp - this.trackingClickStart > this.tapTimeout) return !0;
        if (this.cancelNextClick = !1, this.lastClickTime = e.timeStamp, n = this.trackingClickStart, this.trackingClick = !1, this.trackingClickStart = 0, a && (u = e.changedTouches[0], (l = document.elementFromPoint(u.pageX - window.pageXOffset, u.pageY - window.pageYOffset) || l).fastClickScrollParent = this.targetElement.fastClickScrollParent), "label" === (c = l.tagName.toLowerCase())) {
          if (t = this.findControl(l)) {
            if (this.focus(l), o) return !1;
            l = t
          }
        } else if (this.needsFocus(l)) return e.timeStamp - n > 100 || i && window.top !== window && "input" === c ? (this.targetElement = null, !1) : (this.focus(l), this.sendClick(l, e), i && "select" === c || (this.targetElement = null, e.preventDefault()), !1);
        return !(!i || r || !(s = l.fastClickScrollParent) || s.fastClickLastScrollTop === s.scrollTop) || (this.needsClick(l) || (e.preventDefault(), this.sendClick(l, e)), !1)
      }, e.prototype.onTouchCancel = function() {
        this.trackingClick = !1, this.targetElement = null
      }, e.prototype.onMouse = function(e) {
        return !this.targetElement || (!!e.forwardedTouchEvent || (!e.cancelable || (!(!this.needsClick(this.targetElement) || this.cancelNextClick) || (e.stopImmediatePropagation ? e.stopImmediatePropagation() : e.propagationStopped = !0, e.stopPropagation(), e.preventDefault(), !1))))
      }, e.prototype.onClick = function(e) {
        var t;
        return this.trackingClick ? (this.targetElement = null, this.trackingClick = !1, !0) : "submit" === e.target.type && 0 === e.detail || ((t = this.onMouse(e)) || (this.targetElement = null), t)
      }, e.prototype.destroy = function() {
        var e = this.layer;
        o && (e.removeEventListener("mouseover", this.onMouse, !0), e.removeEventListener("mousedown", this.onMouse, !0), e.removeEventListener("mouseup", this.onMouse, !0)), e.removeEventListener("click", this.onClick, !0), e.removeEventListener("touchstart", this.onTouchStart, !1), e.removeEventListener("touchmove", this.onTouchMove, !1), e.removeEventListener("touchend", this.onTouchEnd, !1), e.removeEventListener("touchcancel", this.onTouchCancel, !1)
      }, e.notNeeded = function(e) {
        var t, n, i;
        if (void 0 === window.ontouchstart) return !0;
        if (n = +(/Chrome\/([0-9]+)/.exec(navigator.userAgent) || [, 0])[1]) {
          if (!o) return !0;
          if (t = document.querySelector("meta[name=viewport]")) {
            if (-1 !== t.content.indexOf("user-scalable=no")) return !0;
            if (n > 31 && document.documentElement.scrollWidth <= window.outerWidth) return !0
          }
        }
        if (c && (i = navigator.userAgent.match(/Version\/([0-9]*)\.([0-9]*)/))[1] >= 10 && i[2] >= 3 && (t = document.querySelector("meta[name=viewport]"))) {
          if (-1 !== t.content.indexOf("user-scalable=no")) return !0;
          if (document.documentElement.scrollWidth <= window.outerWidth) return !0
        }
        return "none" === e.style.msTouchAction || "manipulation" === e.style.touchAction || (!!(+(/Firefox\/([0-9]+)/.exec(navigator.userAgent) || [, 0])[1] >= 27 && (t = document.querySelector("meta[name=viewport]")) && (-1 !== t.content.indexOf("user-scalable=no") || document.documentElement.scrollWidth <= window.outerWidth)) || ("none" === e.style.touchAction || "manipulation" === e.style.touchAction))
      }, e.attach = function(t, n) {
        return new e(t, n)
      }, "function" == typeof define && "object" == typeof define.amd && define.amd ? define((function() {
        return e
      })) : void 0 !== t && t.exports ? (t.exports = e.attach, t.exports.FastClick = e) : window.FastClick = e
    }()
  }, {}],
  2: [function(e, t, n) {
    "use strict";
    let o = e("./modules/device"),
      i = e("./modules/load"),
      r = e("./modules/locale");
    Modernizr.backgroundsize && Modernizr.classlist && Modernizr.csscalc && Modernizr.csstransforms3d && (Modernizr.flexbox || Modernizr.flexboxlegacy) && Modernizr.fontface && Modernizr.svg || (window.location.href = `${r.getLocalePath()}browser-upgrade`), e("fastclick/lib/fastclick")(document.body), o.isMobile() ? i.js("/assets/js/mobile.js") : i.js("/assets/js/full.js")
  }, {
    "./modules/device": 3,
    "./modules/load": 4,
    "./modules/locale": 5,
    "fastclick/lib/fastclick": 1
  }],
  3: [function(e, t, n) {
    "use strict";

    function o(e) {
      return Boolean(window.matchMedia(e).matches)
    }

    function i() {
      return o("(orientation: portrait)")
    }
    t.exports = {
      matches: o,
      isMobile: function() {
        return o("(max-width: 767px)")
      },
      isTablet: function() {
        return o("(min-width: 768px) and (max-width: 1024px)")
      },
      isPortrait: i,
      isLandscape: function() {
        return !i()
      }
    }
  }, {}],
  4: [function(e, t, n) {
    "use strict";
    /*!
    loadCSS: load a CSS file asynchronously.
    [c]2014 @scottjehl, Filament Group, Inc.
    Licensed MIT
    */
    n.css = function(e, t, n, o) {
        var i = window.document.createElement("link"),
          r = t || window.document.getElementsByTagName("script")[0],
          a = window.document.styleSheets;
        return i.rel = "stylesheet", i.href = e, i.media = "only x", o && (i.onload = o), r.parentNode.insertBefore(i, r), i.onloadcssdefined = function(e) {
          for (var t, n = 0; n < a.length; n++) a[n].href && a[n].href === i.href && (t = !0);
          t ? e() : setTimeout((function() {
            i.onloadcssdefined(e)
          }))
        }, i.onloadcssdefined((function() {
          i.media = n || "all"
        })), i
      }
      /*! loadJS: load a JS file asynchronously. [c]2014 @scottjehl, Filament Group, Inc. (Based on http://goo.gl/REQGQ by Paul Irish). Licensed MIT */
      , n.js = function(e, t) {
        var n = window.document.getElementsByTagName("script")[0],
          o = window.document.createElement("script");
        return o.src = e, o.async = !0, n.parentNode.insertBefore(o, n), t && "function" == typeof t && (o.onload = t), o
      }
  }, {}],
  5: [function(e, t, n) {
    "use strict";
    let o = document.documentElement.lang || document.documentElement.getAttribute("lang");
    t.exports = {
      getLocale: o,
      getLocalePath: function() {
        return ("en" === o ? "" : `/${o}`) + "/"
      }
    }
  }, {}]
}, {}, [2]);
//# sourceMappingURL=app.js.map