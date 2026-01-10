YUI.add("pluginhost-config", function(e, t) {
  var n = e.Plugin.Host,
    r = e.Lang;
  n.prototype._initConfigPlugins = function(t) {
    var n = this._getClasses ? this._getClasses() : [this.constructor],
      r = [],
      i = {},
      s, o, u, a, f;
    for (o = n.length - 1; o >= 0; o--) s = n[o], a = s._UNPLUG, a && e.mix(i, a, !0), u = s._PLUG, u && e.mix(r, u, !0);
    for (f in r) r.hasOwnProperty(f) && (i[f] || this.plug(r[f]));
    t && t.plugins && this.plug(t.plugins)
  }, n.plug = function(t, n, i) {
    var s, o, u, a;
    if (t !== e.Base) {
      t._PLUG = t._PLUG || {}, r.isArray(n) || (i && (n = {
        fn: n,
        cfg: i
      }), n = [n]);
      for (o = 0, u = n.length; o < u; o++) s = n[o], a = s.NAME || s.fn.NAME, t._PLUG[a] = s
    }
  }, n.unplug = function(t, n) {
    var i, s, o, u;
    if (t !== e.Base) {
      t._UNPLUG = t._UNPLUG || {}, r.isArray(n) || (n = [n]);
      for (s = 0, o = n.length; s < o; s++) i = n[s], u = i.NAME, t._PLUG[u] ? delete t._PLUG[u] : t._UNPLUG[u] = i
    }
  }
}, "@VERSION@", {
  requires: ["pluginhost-base"]
});

YUI.add("node-pluginhost", function(e, t) {
  e.Node.plug = function() {
    var t = e.Array(arguments);
    return t.unshift(e.Node), e.Plugin.Host.plug.apply(e.Base, t), e.Node
  }, e.Node.unplug = function() {
    var t = e.Array(arguments);
    return t.unshift(e.Node), e.Plugin.Host.unplug.apply(e.Base, t), e.Node
  }, e.mix(e.Node, e.Plugin.Host, !1, null, 1), e.Object.each(e.Node._instances, function(t) {
    e.Plugin.Host.apply(t)
  }), e.NodeList.prototype.plug = function() {
    var t = arguments;
    return e.NodeList.each(this, function(n) {
      e.Node.prototype.plug.apply(e.one(n), t)
    }), this
  }, e.NodeList.prototype.unplug = function() {
    var t = arguments;
    return e.NodeList.each(this, function(n) {
      e.Node.prototype.unplug.apply(e.one(n), t)
    }), this
  }
}, "@VERSION@", {
  requires: ["node-base", "pluginhost"]
});

YUI.add("dom-screen", function(e, t) {
  (function(e) {
    var t = "documentElement",
      n = "compatMode",
      r = "position",
      i = "fixed",
      s = "relative",
      o = "left",
      u = "top",
      a = "BackCompat",
      f = "medium",
      l = "borderLeftWidth",
      c = "borderTopWidth",
      h = "getBoundingClientRect",
      p = "getComputedStyle",
      d = e.DOM,
      v = /^t(?:able|d|h)$/i,
      m;
    e.UA.ie && (e.config.doc[n] !== "BackCompat" ? m = t : m = "body"), e.mix(d, {
      winHeight: function(e) {
        var t = d._getWinSize(e).height;
        return t
      },
      winWidth: function(e) {
        var t = d._getWinSize(e).width;
        return t
      },
      docHeight: function(e) {
        var t = d._getDocSize(e).height;
        return Math.max(t, d._getWinSize(e).height)
      },
      docWidth: function(e) {
        var t = d._getDocSize(e).width;
        return Math.max(t, d._getWinSize(e).width)
      },
      docScrollX: function(n, r) {
        r = r || n ? d._getDoc(n) : e.config.doc;
        var i = r.defaultView,
          s = i ? i.pageXOffset : 0;
        return Math.max(r[t].scrollLeft, r.body.scrollLeft, s)
      },
      docScrollY: function(n, r) {
        r = r || n ? d._getDoc(n) : e.config.doc;
        var i = r.defaultView,
          s = i ? i.pageYOffset : 0;
        return Math.max(r[t].scrollTop, r.body.scrollTop, s)
      },
      getXY: function() {
        return e.config.doc[t][h] ? function(r) {
          var i = null,
            s, o, u, f, l, c, p, v, g, y;
          if (r && r.tagName) {
            p = r.ownerDocument, u = p[n], u !== a ? y = p[t] : y = p.body, y.contains ? g = y.contains(r) : g = e.DOM.contains(y, r);
            if (g) {
              v = p.defaultView, v && "pageXOffset" in v ? (s = v.pageXOffset, o = v.pageYOffset) : (s = m ? p[m].scrollLeft : d.docScrollX(r, p), o = m ? p[m].scrollTop : d.docScrollY(r, p)), e.UA.ie && (!p.documentMode || p.documentMode < 8 || u === a) && (l = y.clientLeft, c = y.clientTop), f = r[h](), i = [f.left, f.top];
              if (l || c) i[0] -= l, i[1] -= c;
              if (o || s)
                if (!e.UA.ios || e.UA.ios >= 4.2) i[0] += s, i[1] += o
            } else i = d._getOffset(r)
          }
          return i
        } : function(t) {
          var n = null,
            s, o, u, a, f;
          if (t)
            if (d.inDoc(t)) {
              n = [t.offsetLeft, t.offsetTop], s = t.ownerDocument, o = t, u = e.UA.gecko || e.UA.webkit > 519 ? !0 : !1;
              while (o = o.offsetParent) n[0] += o.offsetLeft, n[1] += o.offsetTop, u && (n = d._calcBorders(o, n));
              if (d.getStyle(t, r) != i) {
                o = t;
                while (o = o.parentNode) {
                  a = o.scrollTop, f = o.scrollLeft, e.UA.gecko && d.getStyle(o, "overflow") !== "visible" && (n = d._calcBorders(o, n));
                  if (a || f) n[0] -= f, n[1] -= a
                }
                n[0] += d.docScrollX(t, s), n[1] += d.docScrollY(t, s)
              } else n[0] += d.docScrollX(t, s), n[1] += d.docScrollY(t, s)
            } else n = d._getOffset(t);
          return n
        }
      }(),
      getScrollbarWidth: e.cached(function() {
        var t = e.config.doc,
          n = t.createElement("div"),
          r = t.getElementsByTagName("body")[0],
          i = .1;
        return r && (n.style.cssText = "position:absolute;visibility:hidden;overflow:scroll;width:20px;", n.appendChild(t.createElement("p")).style.height = "1px", r.insertBefore(n, r.firstChild), i = n.offsetWidth - n.clientWidth, r.removeChild(n)), i
      }, null, .1),
      getX: function(e) {
        return d.getXY(e)[0]
      },
      getY: function(e) {
        return d.getXY(e)[1]
      },
      setXY: function(e, t, n) {
        var i = d.setStyle,
          a, f, l, c;
        e && t && (a = d.getStyle(e, r), f = d._getOffset(e), a == "static" && (a = s, i(e, r, a)), c = d.getXY(e), t[0] !== null && i(e, o, t[0] - c[0] + f[0] + "px"), t[1] !== null && i(e, u, t[1] - c[1] + f[1] + "px"), n || (l = d.getXY(e), (l[0] !== t[0] || l[1] !== t[1]) && d.setXY(e, t, !0)))
      },
      setX: function(e, t) {
        return d.setXY(e, [t, null])
      },
      setY: function(e, t) {
        return d.setXY(e, [null, t])
      },
      swapXY: function(e, t) {
        var n = d.getXY(e);
        d.setXY(e, d.getXY(t)), d.setXY(t, n)
      },
      _calcBorders: function(t, n) {
        var r = parseInt(d[p](t, c), 10) || 0,
          i = parseInt(d[p](t, l), 10) || 0;
        return e.UA.gecko && v.test(t.tagName) && (r = 0, i = 0), n[0] += i, n[1] += r, n
      },
      _getWinSize: function(r, i) {
        i = i || r ? d._getDoc(r) : e.config.doc;
        var s = i.defaultView || i.parentWindow,
          o = i[n],
          u = s.innerHeight,
          a = s.innerWidth,
          f = i[t];
        return o && !e.UA.opera && (o != "CSS1Compat" && (f = i.body), u = f.clientHeight, a = f.clientWidth), {
          height: u,
          width: a
        }
      },
      _getDocSize: function(r) {
        var i = r ? d._getDoc(r) : e.config.doc,
          s = i[t];
        return i[n] != "CSS1Compat" && (s = i.body), {
          height: s.scrollHeight,
          width: s.scrollWidth
        }
      }
    })
  })(e),
  function(e) {
    var t = "top",
      n = "right",
      r = "bottom",
      i = "left",
      s = function(e, s) {
        var o = Math.max(e[t], s[t]),
          u = Math.min(e[n], s[n]),
          a = Math.min(e[r], s[r]),
          f = Math.max(e[i], s[i]),
          l = {};
        return l[t] = o, l[n] = u, l[r] = a, l[i] = f, l
      },
      o = e.DOM;
    e.mix(o, {
      region: function(e) {
        var t = o.getXY(e),
          n = !1;
        return e && t && (n = o._getRegion(t[1], t[0] + e.offsetWidth, t[1] + e.offsetHeight, t[0])), n
      },
      intersect: function(u, a, f) {
        var l = f || o.region(u),
          c = {},
          h = a,
          p;
        if (h.tagName) c = o.region(h);
        else {
          if (!e.Lang.isObject(a)) return !1;
          c = a
        }
        return p = s(c, l), {
          top: p[t],
          right: p[n],
          bottom: p[r],
          left: p[i],
          area: (p[r] - p[t]) * (p[n] - p[i]),
          yoff: p[r] - p[t],
          xoff: p[n] - p[i],
          inRegion: o.inRegion(u, a, !1, f)
        }
      },
      inRegion: function(u, a, f, l) {
        var c = {},
          h = l || o.region(u),
          p = a,
          d;
        if (p.tagName) c = o.region(p);
        else {
          if (!e.Lang.isObject(a)) return !1;
          c = a
        }
        return f ? h[i] >= c[i] && h[n] <= c[n] && h[t] >= c[t] && h[r] <= c[r] : (d = s(c, h), d[r] >= d[t] && d[n] >= d[i] ? !0 : !1)
      },
      inViewportRegion: function(e, t, n) {
        return o.inRegion(e, o.viewportRegion(e), t, n)
      },
      _getRegion: function(e, s, o, u) {
        var a = {};
        return a[t] = a[1] = e, a[i] = a[0] = u, a[r] = o, a[n] = s, a.width = a[n] - a[i], a.height = a[r] - a[t], a
      },
      viewportRegion: function(t) {
        t = t || e.config.doc.documentElement;
        var n = !1,
          r, i;
        return t && (r = o.docScrollX(t), i = o.docScrollY(t), n = o._getRegion(i, o.winWidth(t) + r, i + o.winHeight(t), r)), n
      }
    })
  }(e)
}, "@VERSION@", {
  requires: ["dom-base", "dom-style"]
});

YUI.add("node-screen", function(e, t) {
  e.each(["winWidth", "winHeight", "docWidth", "docHeight", "docScrollX", "docScrollY"], function(t) {
    e.Node.ATTRS[t] = {
      getter: function() {
        var n = Array.prototype.slice.call(arguments);
        return n.unshift(e.Node.getDOMNode(this)), e.DOM[t].apply(this, n)
      }
    }
  }), e.Node.ATTRS.scrollLeft = {
    getter: function() {
      var t = e.Node.getDOMNode(this);
      return "scrollLeft" in t ? t.scrollLeft : e.DOM.docScrollX(t)
    },
    setter: function(t) {
      var n = e.Node.getDOMNode(this);
      n && ("scrollLeft" in n ? n.scrollLeft = t : (n.document || n.nodeType === 9) && e.DOM._getWin(n).scrollTo(t, e.DOM.docScrollY(n)))
    }
  }, e.Node.ATTRS.scrollTop = {
    getter: function() {
      var t = e.Node.getDOMNode(this);
      return "scrollTop" in t ? t.scrollTop : e.DOM.docScrollY(t)
    },
    setter: function(t) {
      var n = e.Node.getDOMNode(this);
      n && ("scrollTop" in n ? n.scrollTop = t : (n.document || n.nodeType === 9) && e.DOM._getWin(n).scrollTo(e.DOM.docScrollX(n), t))
    }
  }, e.Node.importMethod(e.DOM, ["getXY", "setXY", "getX", "setX", "getY", "setY", "swapXY"]), e.Node.ATTRS.region = {
    getter: function() {
      var t = this.getDOMNode(),
        n;
      return t && !t.tagName && t.nodeType === 9 && (t = t.documentElement), e.DOM.isWindow(t) ? n = e.DOM.viewportRegion(t) : n = e.DOM.region(t), n
    }
  }, e.Node.ATTRS.viewportRegion = {
    getter: function() {
      return e.DOM.viewportRegion(e.Node.getDOMNode(this))
    }
  }, e.Node.importMethod(e.DOM, "inViewportRegion"), e.Node.prototype.intersect = function(t, n) {
    var r = e.Node.getDOMNode(this);
    return e.instanceOf(t, e.Node) && (t = e.Node.getDOMNode(t)), e.DOM.intersect(r, t, n)
  }, e.Node.prototype.inRegion = function(t, n, r) {
    var i = e.Node.getDOMNode(this);
    return e.instanceOf(t, e.Node) && (t = e.Node.getDOMNode(t)), e.DOM.inRegion(i, t, n, r)
  }
}, "@VERSION@", {
  requires: ["dom-screen", "node-base"]
});

YUI.add("node-style", function(e, t) {
  (function(e) {
    e.mix(e.Node.prototype, {
      setStyle: function(t, n) {
        return e.DOM.setStyle(this._node, t, n), this
      },
      setStyles: function(t) {
        return e.DOM.setStyles(this._node, t), this
      },
      getStyle: function(t) {
        return e.DOM.getStyle(this._node, t)
      },
      getComputedStyle: function(t) {
        return e.DOM.getComputedStyle(this._node, t)
      }
    }), e.NodeList.importMethod(e.Node.prototype, ["getStyle", "getComputedStyle", "setStyle", "setStyles"])
  })(e);
  var n = e.Node;
  e.mix(n.prototype, {
    show: function(e) {
      return e = arguments[arguments.length - 1], this.toggleView(!0, e), this
    },
    _show: function() {
      this.removeAttribute("hidden"), this.setStyle("display", "")
    },
    _isHidden: function() {
      return this.hasAttribute("hidden") || e.DOM.getComputedStyle(this._node, "display") === "none"
    },
    toggleView: function(e, t) {
      return this._toggleView.apply(this, arguments), this
    },
    _toggleView: function(e, t) {
      return t = arguments[arguments.length - 1], typeof e != "boolean" && (e = this._isHidden() ? 1 : 0), e ? this._show() : this._hide(), typeof t == "function" && t.call(this), this
    },
    hide: function(e) {
      return e = arguments[arguments.length - 1], this.toggleView(!1, e), this
    },
    _hide: function() {
      this.setAttribute("hidden", "hidden"), this.setStyle("display", "none")
    }
  }), e.NodeList.importMethod(e.Node.prototype, ["show", "hide", "toggleView"])
}, "@VERSION@", {
  requires: ["dom-style", "node-base"]
});

YUI.add("json-parse", function(e, t) {
  var n = e.config.global.JSON;
  e.namespace("JSON").parse = function(e, t, r) {
    return n.parse(typeof e == "string" ? e : e + "", t, r)
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("model", function(e, t) {
  function l() {
    l.superclass.constructor.apply(this, arguments)
  }
  var n = YUI.namespace("Env.Model"),
    r = e.Lang,
    i = e.Array,
    s = e.Object,
    o = "change",
    u = "error",
    a = "load",
    f = "save";
  e.Model = e.extend(l, e.Base, {
    idAttribute: "id",
    _allowAdHocAttrs: !0,
    _isYUIModel: !0,
    initializer: function(e) {
      this.changed = {}, this.lastChange = {}, this.lists = []
    },
    destroy: function(e, t) {
      var n = this;
      return typeof e == "function" && (t = e, e = null), n.onceAfter("destroy", function() {
        function r(r) {
          r || i.each(n.lists.concat(), function(t) {
            t.remove(n, e)
          }), t && t.apply(null, arguments)
        }
        e && (e.remove || e["delete"]) ? n.sync("delete", e, r) : r()
      }), l.superclass.destroy.call(n)
    },
    generateClientId: function() {
      return n.lastId || (n.lastId = 0), this.constructor.NAME + "_" + (n.lastId += 1)
    },
    getAsHTML: function(t) {
      var n = this.get(t);
      return e.Escape.html(r.isValue(n) ? String(n) : "")
    },
    getAsURL: function(e) {
      var t = this.get(e);
      return encodeURIComponent(r.isValue(t) ? String(t) : "")
    },
    isModified: function() {
      return this.isNew() || !s.isEmpty(this.changed)
    },
    isNew: function() {
      return !r.isValue(this.get("id"))
    },
    load: function(e, t) {
      var n = this;
      return typeof e == "function" && (t = e, e = {}), e || (e = {}), n.sync("read", e, function(r, i) {
        var s = {
            options: e,
            response: i
          },
          o;
        r ? (s.error = r, s.src = "load", n.fire(u, s)) : (n._loadEvent || (n._loadEvent = n.publish(a, {
          preventable: !1
        })), o = s.parsed = n._parse(i), n.setAttrs(o, e), n.changed = {}, n.fire(a, s)), t && t.apply(null, arguments)
      }), n
    },
    parse: function(t) {
      if (typeof t == "string") try {
        return e.JSON.parse(t)
      } catch (n) {
        return this.fire(u, {
          error: n,
          response: t,
          src: "parse"
        }), null
      }
      return t
    },
    save: function(e, t) {
      var n = this;
      return typeof e == "function" && (t = e, e = {}), e || (e = {}), n._validate(n.toJSON(), function(r) {
        if (r) {
          t && t.call(null, r);
          return
        }
        n.sync(n.isNew() ? "create" : "update", e, function(r, i) {
          var s = {
              options: e,
              response: i
            },
            o;
          r ? (s.error = r, s.src = "save", n.fire(u, s)) : (n._saveEvent || (n._saveEvent = n.publish(f, {
            preventable: !1
          })), i && (o = s.parsed = n._parse(i), n.setAttrs(o, e)), n.changed = {}, n.fire(f, s)), t && t.apply(null, arguments)
        })
      }), n
    },
    set: function(e, t, n) {
      var r = {};
      return r[e] = t, this.setAttrs(r, n)
    },
    setAttrs: function(t, n) {
      var r = this.idAttribute,
        i, u, a, f, l;
      n = e.merge(n), l = n._transaction = {}, r !== "id" && (t = e.merge(t), s.owns(t, r) ? t.id = t[r] : s.owns(t, "id") && (t[r] = t.id));
      for (a in t) s.owns(t, a) && this._setAttr(a, t[a], n);
      if (!s.isEmpty(l)) {
        i = this.changed, f = this.lastChange = {};
        for (a in l) s.owns(l, a) && (u = l[a], i[a] = u.newVal, f[a] = {
          newVal: u.newVal,
          prevVal: u.prevVal,
          src: u.src || null
        });
        n.silent || (this._changeEvent || (this._changeEvent = this.publish(o, {
          preventable: !1
        })), n.changed = f, this.fire(o, n))
      }
      return this
    },
    sync: function() {
      var e = i(arguments, 0, !0).pop();
      typeof e == "function" && e()
    },
    toJSON: function() {
      var e = this.getAttrs();
      return delete e.clientId, delete e.destroyed, delete e.initialized, this.idAttribute !== "id" && delete e.id, e
    },
    undo: function(e, t) {
      var n = this.lastChange,
        r = this.idAttribute,
        o = {},
        u;
      return e || (e = s.keys(n)), i.each(e, function(e) {
        s.owns(n, e) && (e = e === r ? "id" : e, u = !0, o[e] = n[e].prevVal)
      }), u ? this.setAttrs(o, t) : this
    },
    validate: function(e, t) {
      t && t()
    },
    addAttr: function(e, t, n) {
      var i = this.idAttribute,
        s, o;
      return i && e === i && (s = this._isLazyAttr("id") || this._getAttrCfg("id"), o = t.value === t.defaultValue ? null : t.value, r.isValue(o) || (o = s.value === s.defaultValue ? null : s.value, r.isValue(o) || (o = r.isValue(t.defaultValue) ? t.defaultValue : s.defaultValue)), t.value = o, s.value !== o && (s.value = o, this._isLazyAttr("id") ? this._state.add("id", "lazy", s) : this._state.add("id", "value", o))), l.superclass.addAttr.apply(this, arguments)
    },
    _parse: function(e) {
      return this.parse(e)
    },
    _validate: function(e, t) {
      function i(i) {
        if (r.isValue(i)) {
          n.fire(u, {
            attributes: e,
            error: i,
            src: "validate"
          }), t(i);
          return
        }
        t()
      }
      var n = this;
      n.validate.length === 1 ? i(n.validate(e, i)) : n.validate(e, i)
    },
    _setAttrVal: function(e, t, n, r, i, s) {
      var o = l.superclass._setAttrVal.apply(this, arguments),
        u = i && i._transaction,
        a = s && s.initializing;
      return o && u && !a && (u[e] = {
        newVal: this.get(e),
        prevVal: n,
        src: i.src || null
      }), o
    }
  }, {
    NAME: "model",
    ATTRS: {
      clientId: {
        valueFn: "generateClientId",
        readOnly: !0
      },
      id: {
        value: null
      }
    }
  })
}, "@VERSION@", {
  requires: ["base-build", "escape", "json-parse"]
});

YUI.add("array-extras", function(e, t) {
  var n = e.Array,
    r = e.Lang,
    i = Array.prototype;
  n.lastIndexOf = r._isNative(i.lastIndexOf) ? function(e, t, n) {
    return n || n === 0 ? e.lastIndexOf(t, n) : e.lastIndexOf(t)
  } : function(e, t, n) {
    var r = e.length,
      i = r - 1;
    if (n || n === 0) i = Math.min(n < 0 ? r + n : n, r);
    if (i > -1 && r > 0)
      for (; i > -1; --i)
        if (i in e && e[i] === t) return i;
    return -1
  }, n.unique = function(e, t) {
    var n = 0,
      r = e.length,
      i = [],
      s, o, u, a;
    e: for (; n < r; n++) {
      a = e[n];
      for (s = 0, u = i.length; s < u; s++) {
        o = i[s];
        if (t) {
          if (t.call(e, a, o, n, e)) continue e
        } else if (a === o) continue e
      }
      i.push(a)
    }
    return i
  }, n.filter = r._isNative(i.filter) ? function(e, t, n) {
    return i.filter.call(e, t, n)
  } : function(e, t, n) {
    var r = 0,
      i = e.length,
      s = [],
      o;
    for (; r < i; ++r) r in e && (o = e[r], t.call(n, o, r, e) && s.push(o));
    return s
  }, n.reject = function(e, t, r) {
    return n.filter(e, function(e, n, i) {
      return !t.call(r, e, n, i)
    })
  }, n.every = r._isNative(i.every) ? function(e, t, n) {
    return i.every.call(e, t, n)
  } : function(e, t, n) {
    for (var r = 0, i = e.length; r < i; ++r)
      if (r in e && !t.call(n, e[r], r, e)) return !1;
    return !0
  }, n.map = r._isNative(i.map) ? function(e, t, n) {
    return i.map.call(e, t, n)
  } : function(e, t, n) {
    var r = 0,
      s = e.length,
      o = i.concat.call(e);
    for (; r < s; ++r) r in e && (o[r] = t.call(n, e[r], r, e));
    return o
  }, n.reduce = r._isNative(i.reduce) ? function(e, t, n, r) {
    return i.reduce.call(e, function(e, t, i, s) {
      return n.call(r, e, t, i, s)
    }, t)
  } : function(e, t, n, r) {
    var i = 0,
      s = e.length,
      o = t;
    for (; i < s; ++i) i in e && (o = n.call(r, o, e[i], i, e));
    return o
  }, n.find = function(e, t, n) {
    for (var r = 0, i = e.length; r < i; r++)
      if (r in e && t.call(n, e[r], r, e)) return e[r];
    return null
  }, n.grep = function(e, t) {
    return n.filter(e, function(e, n) {
      return t.test(e)
    })
  }, n.partition = function(e, t, r) {
    var i = {
      matches: [],
      rejects: []
    };
    return n.each(e, function(n, s) {
      var u = t.call(r, n, s, e) ? i.matches : i.rejects;
      u.push(n)
    }), i
  }, n.zip = function(e, t) {
    var r = [];
    return n.each(e, function(e, n) {
      r.push([e, t[n]])
    }), r
  }, n.flatten = function(e) {
    var t = [],
      i, s, o;
    if (!e) return t;
    for (i = 0, s = e.length; i < s; ++i) o = e[i], r.isArray(o) ? t.push.apply(t, n.flatten(o)) : t.push(o);
    return t
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("plugin", function(e, t) {
  function n(t) {
    !this.hasImpl || !this.hasImpl(e.Plugin.Base) ? n.superclass.constructor.apply(this, arguments) : n.prototype.initializer.apply(this, arguments)
  }
  n.ATTRS = {
    host: {
      writeOnce: !0
    }
  }, n.NAME = "plugin", n.NS = "plugin", e.extend(n, e.Base, {
    _handles: null,
    initializer: function(e) {
      this._handles = []
    },
    destructor: function() {
      if (this._handles)
        for (var e = 0, t = this._handles.length; e < t; e++) this._handles[e].detach()
    },
    doBefore: function(e, t, n) {
      var r = this.get("host"),
        i;
      return e in r ? i = this.beforeHostMethod(e, t, n) : r.on && (i = this.onHostEvent(e, t, n)), i
    },
    doAfter: function(e, t, n) {
      var r = this.get("host"),
        i;
      return e in r ? i = this.afterHostMethod(e, t, n) : r.after && (i = this.afterHostEvent(e, t, n)), i
    },
    onHostEvent: function(e, t, n) {
      var r = this.get("host").on(e, t, n || this);
      return this._handles.push(r), r
    },
    onceHostEvent: function(e, t, n) {
      var r = this.get("host").once(e, t, n || this);
      return this._handles.push(r), r
    },
    afterHostEvent: function(e, t, n) {
      var r = this.get("host").after(e, t, n || this);
      return this._handles.push(r), r
    },
    onceAfterHostEvent: function(e, t, n) {
      var r = this.get("host").onceAfter(e, t, n || this);
      return this._handles.push(r), r
    },
    beforeHostMethod: function(t, n, r) {
      var i = e.Do.before(n, this.get("host"), t, r || this);
      return this._handles.push(i), i
    },
    afterHostMethod: function(t, n, r) {
      var i = e.Do.after(n, this.get("host"), t, r || this);
      return this._handles.push(i), i
    },
    toString: function() {
      return this.constructor.NAME + "[" + this.constructor.NS + "]"
    }
  }), e.namespace("Plugin").Base = n
}, "@VERSION@", {
  requires: ["base-base"]
});

YUI.add("base-pluginhost", function(e, t) {
  var n = e.Base,
    r = e.Plugin.Host;
  e.mix(n, r, !1, null, 1), n.plug = r.plug, n.unplug = r.unplug
}, "@VERSION@", {
  requires: ["base-base", "pluginhost"]
});

YUI.add("transition", function(e, t) {
  var n = "",
    r = "",
    i = e.config.doc,
    s = "documentElement",
    o = i[s].style,
    u = "transition",
    a = "transitionProperty",
    f, l, c, h, p, d, v = {},
    m = ["Webkit", "Moz"],
    g = {
      Webkit: "webkitTransitionEnd"
    },
    y = function() {
      this.init.apply(this, arguments)
    };
  y._TRANSFORM = "transform", y._toCamel = function(e) {
    return e = e.replace(/-([a-z])/gi, function(e, t) {
      return t.toUpperCase()
    }), e
  }, y._toHyphen = function(e) {
    return e = e.replace(/([A-Z]?)([a-z]+)([A-Z]?)/g, function(e, t, n, r) {
      var i = (t ? "-" + t.toLowerCase() : "") + n;
      return r && (i += "-" + r.toLowerCase()), i
    }), e
  }, y.SHOW_TRANSITION = "fadeIn", y.HIDE_TRANSITION = "fadeOut", y.useNative = !1, "transition" in o && "transitionProperty" in o && "transitionDuration" in o && "transitionTimingFunction" in o && "transitionDelay" in o ? (y.useNative = !0, y.supported = !0) : e.Array.each(m, function(e) {
    var t = e + "Transition";
    t in i[s].style && (n = e, r = y._toHyphen(e) + "-", y.useNative = !0, y.supported = !0, y._VENDOR_PREFIX = e)
  }), typeof o.transform == "undefined" && e.Array.each(m, function(e) {
    var t = e + "Transform";
    typeof o[t] != "undefined" && (y._TRANSFORM = t)
  }), n && (u = n + "Transition", a = n + "TransitionProperty"), f = r + "transition-property", l = r + "transition-duration", c = r + "transition-timing-function", h = r + "transition-delay", p = "transitionend", d = "on" + n.toLowerCase() + "transitionend", p = g[n] || p, y.fx = {}, y.toggles = {}, y._hasEnd = {}, y._reKeywords = /^(?:node|duration|iterations|easing|delay|on|onstart|onend)$/i, e.Node.DOM_EVENTS[p] = 1, y.NAME = "transition", y.DEFAULT_EASING = "ease", y.DEFAULT_DURATION = .5, y.DEFAULT_DELAY = 0, y._nodeAttrs = {}, y.prototype = {
    constructor: y,
    init: function(e, t) {
      var n = this;
      return n._node = e, !n._running && t && (n._config = t, e._transition = n, n._duration = "duration" in t ? t.duration : n.constructor.DEFAULT_DURATION, n._delay = "delay" in t ? t.delay : n.constructor.DEFAULT_DELAY, n._easing = t.easing || n.constructor.DEFAULT_EASING, n._count = 0, n._running = !1), n
    },
    addProperty: function(t, n) {
      var r = this,
        i = this._node,
        s = e.stamp(i),
        o = e.one(i),
        u = y._nodeAttrs[s],
        a, f, l, c, h;
      u || (u = y._nodeAttrs[s] = {}), c = u[t], n && n.value !== undefined ? h = n.value : n !== undefined && (h = n, n = v), typeof h == "function" && (h = h.call(o, o)), c && c.transition && c.transition !== r && c.transition._count--, r._count++, l = (typeof n.duration != "undefined" ? n.duration : r._duration) || 1e-4, u[t] = {
        value: h,
        duration: l,
        delay: typeof n.delay != "undefined" ? n.delay : r._delay,
        easing: n.easing || r._easing,
        transition: r
      }, a = e.DOM.getComputedStyle(i, t), f = typeof h == "string" ? a : parseFloat(a), y.useNative && f === h && setTimeout(function() {
        r._onNativeEnd.call(i, {
          propertyName: t,
          elapsedTime: l
        })
      }, l * 1e3)
    },
    removeProperty: function(t) {
      var n = this,
        r = y._nodeAttrs[e.stamp(n._node)];
      r && r[t] && (delete r[t], n._count--)
    },
    initAttrs: function(t) {
      var n, r = this._node;
      t.transform && !t[y._TRANSFORM] && (t[y._TRANSFORM] = t.transform, delete t.transform);
      for (n in t) t.hasOwnProperty(n) && !y._reKeywords.test(n) && (this.addProperty(n, t[n]), r.style[n] === "" && e.DOM.setStyle(r, n, e.DOM.getComputedStyle(r, n)))
    },
    run: function(t) {
      var n = this,
        r = n._node,
        i = n._config,
        s = {
          type: "transition:start",
          config: i
        };
      return n._running || (n._running = !0, i.on && i.on.start && i.on.start.call(e.one(r), s), n.initAttrs(n._config), n._callback = t, n._start()), n
    },
    _start: function() {
      this._runNative()
    },
    _prepDur: function(e) {
      return e = parseFloat(e) * 1e3, e + "ms"
    },
    _runNative: function() {
      var t = this,
        n = t._node,
        r = e.stamp(n),
        i = n.style,
        s = n.ownerDocument.defaultView.getComputedStyle(n),
        o = y._nodeAttrs[r],
        u = "",
        a = s[y._toCamel(f)],
        d = f + ": ",
        v = l + ": ",
        m = c + ": ",
        g = h + ": ",
        b, w, E;
      a !== "all" && (d += a + ",", v += s[y._toCamel(l)] + ",", m += s[y._toCamel(c)] + ",", g += s[y._toCamel(h)] + ",");
      for (E in o) b = y._toHyphen(E), w = o[E], (w = o[E]) && w.transition === t && (E in n.style ? (v += t._prepDur(w.duration) + ",", g += t._prepDur(w.delay) + ",", m += w.easing + ",", d += b + ",", u += b + ": " + w.value + "; ") : this.removeProperty(E));
      d = d.replace(/,$/, ";"), v = v.replace(/,$/, ";"), m = m.replace(/,$/, ";"), g = g.replace(/,$/, ";"), y._hasEnd[r] || (n.addEventListener(p, t._onNativeEnd, ""), y._hasEnd[r] = !0), i.cssText += d + v + m + g + u
    },
    _end: function(t) {
      var n = this,
        r = n._node,
        i = n._callback,
        s = n._config,
        o = {
          type: "transition:end",
          config: s,
          elapsedTime: t
        },
        u = e.one(r);
      n._running = !1, n._callback = null, r && (s.on && s.on.end ? setTimeout(function() {
        s.on.end.call(u, o), i && i.call(u, o)
      }, 1) : i && setTimeout(function() {
        i.call(u, o)
      }, 1))
    },
    _endNative: function(e) {
      var t = this._node,
        n = t.ownerDocument.defaultView.getComputedStyle(t, "")[y._toCamel(f)];
      e = y._toHyphen(e), typeof n == "string" && (n = n.replace(new RegExp("(?:^|,\\s)" + e + ",?"), ","), n = n.replace(/^,|,$/, ""), t.style[u] = n)
    },
    _onNativeEnd: function(t) {
      var n = this,
        r = e.stamp(n),
        i = t,
        s = y._toCamel(i.propertyName),
        o = i.elapsedTime,
        u = y._nodeAttrs[r],
        f = u[s],
        l = f ? f.transition : null,
        c, h;
      l && (l.removeProperty(s), l._endNative(s), h = l._config[s], c = {
        type: "propertyEnd",
        propertyName: s,
        elapsedTime: o,
        config: h
      }, h && h.on && h.on.end && h.on.end.call(e.one(n), c), l._count <= 0 && (l._end(o), n.style[a] = ""))
    },
    destroy: function() {
      var e = this,
        t = e._node;
      t && (t.removeEventListener(p, e._onNativeEnd, !1), e._node = null)
    }
  }, e.Transition = y, e.TransitionNative = y, e.Node.prototype.transition = function(t, n, r) {
    var i = y._nodeAttrs[e.stamp(this._node)],
      s = i ? i.transition || null : null,
      o, u;
    if (typeof t == "string") {
      typeof n == "function" && (r = n, n = null), o = y.fx[t];
      if (n && typeof n == "object") {
        n = e.clone(n);
        for (u in o) o.hasOwnProperty(u) && (u in n || (n[u] = o[u]))
      } else n = o
    } else r = n, n = t;
    return s && !s._running ? s.init(this, n) : s = new y(this._node, n), s.run(r), this
  }, e.Node.prototype.show = function(t, n, r) {
    return this._show(), t && e.Transition && (typeof t != "string" && !t.push && (typeof n == "function" && (r = n, n = t), t = y.SHOW_TRANSITION), this.transition(t, n, r)), this
  }, e.NodeList.prototype.show = function(t, n, r) {
    var i = this._nodes,
      s = 0,
      o;
    while (o = i[s++]) e.one(o).show(t, n, r);
    return this
  };
  var b = function(e, t, n) {
    return function() {
      t && t.call(e), n && typeof n == "function" && n.apply(e._node, arguments)
    }
  };
  e.Node.prototype.hide = function(t, n, r) {
      return t && e.Transition ? (typeof n == "function" && (r = n, n = null), r = b(this, this._hide, r), typeof t != "string" && !t.push && (typeof n == "function" && (r = n, n = t), t = y.HIDE_TRANSITION), this.transition(t, n, r)) : this._hide(), this
    }, e.NodeList.prototype.hide = function(t, n, r) {
      var i = this._nodes,
        s = 0,
        o;
      while (o = i[s++]) e.one(o).hide(t, n, r);
      return this
    }, e.NodeList.prototype
    .transition = function(t, n, r) {
      var i = this._nodes,
        s = this.size(),
        o = 0,
        r = r === !0,
        u;
      while (u = i[o++]) o < s && r ? e.one(u).transition(t) : e.one(u).transition(t, n);
      return this
    }, e.Node.prototype.toggleView = function(t, n, r) {
      this._toggles = this._toggles || [], r = arguments[arguments.length - 1];
      if (typeof t != "string") {
        n = t, this._toggleView(n, r);
        return
      }
      return typeof n == "function" && (n = undefined), typeof n == "undefined" && t in this._toggles && (n = !this._toggles[t]), n = n ? 1 : 0, n ? this._show() : r = b(this, this._hide, r), this._toggles[t] = n, this.transition(e.Transition.toggles[t][n], r), this
    }, e.NodeList.prototype.toggleView = function(t, n, r) {
      var i = this._nodes,
        s = 0,
        o;
      while (o = i[s++]) o = e.one(o), o.toggleView.apply(o, arguments);
      return this
    }, e.mix(y.fx, {
      fadeOut: {
        opacity: 0,
        duration: .5,
        easing: "ease-out"
      },
      fadeIn: {
        opacity: 1,
        duration: .5,
        easing: "ease-in"
      },
      sizeOut: {
        height: 0,
        width: 0,
        duration: .75,
        easing: "ease-out"
      },
      sizeIn: {
        height: function(e) {
          return e.get("scrollHeight") + "px"
        },
        width: function(e) {
          return e.get("scrollWidth") + "px"
        },
        duration: .5,
        easing: "ease-in",
        on: {
          start: function() {
            var e = this.getStyle("overflow");
            e !== "hidden" && (this.setStyle("overflow", "hidden"), this._transitionOverflow = e)
          },
          end: function() {
            this._transitionOverflow && (this.setStyle("overflow", this._transitionOverflow), delete this._transitionOverflow)
          }
        }
      }
    }), e.mix(y.toggles, {
      size: ["sizeOut", "sizeIn"],
      fade: ["fadeOut", "fadeIn"]
    })
}, "@VERSION@", {
  requires: ["node-style"]
});

YUI.add("event-simulate", function(e, t) {
  (function() {
    function v(t, n, a, f, l, c, h, p, d, v, m) {
      t || e.error("simulateKeyEvent(): Invalid target.");
      if (i(n)) {
        n = n.toLowerCase();
        switch (n) {
          case "textevent":
            n = "keypress";
            break;
          case "keyup":
          case "keydown":
          case "keypress":
            break;
          default:
            e.error("simulateKeyEvent(): Event type '" + n + "' not supported.")
        }
      } else e.error("simulateKeyEvent(): Event type must be a string.");
      s(a) || (a = !0), s(f) || (f = !0), o(l) || (l = e.config.win), s(c) || (c = !1), s(h) || (h = !1), s(p) || (p = !1), s(d) || (d = !1), u(v) || (v = 0), u(m) || (m = 0);
      var g = null;
      if (r(e.config.doc.createEvent)) {
        try {
          g = e.config.doc.createEvent("KeyEvents"), g.initKeyEvent(n, a, f, l, c, h, p, d, v, m)
        } catch (y) {
          try {
            g = e.config.doc.createEvent("Events")
          } catch (b) {
            g = e.config.doc.createEvent("UIEvents")
          } finally {
            g.initEvent(n, a, f), g.view = l, g.altKey = h, g.ctrlKey = c, g.shiftKey = p, g.metaKey = d, g.keyCode = v, g.charCode = m
          }
        }
        t.dispatchEvent(g)
      } else o(e.config.doc.createEventObject) ? (g = e.config.doc.createEventObject(), g.bubbles = a, g.cancelable = f, g.view = l, g.ctrlKey = c, g.altKey = h, g.shiftKey = p, g.metaKey = d, g.keyCode = m > 0 ? m : v, t.fireEvent("on" + n, g)) : e.error("simulateKeyEvent(): No event simulation framework present.")
    }

    function m(t, n, l, c, h, p, d, v, m, g, y, b, w, E, S, x) {
      t || e.error("simulateMouseEvent(): Invalid target."), i(n) ? !a[n.toLowerCase()] && !f[n] && e.error("simulateMouseEvent(): Event type '" + n + "' not supported.") : e.error("simulateMouseEvent(): Event type must be a string."), s(l) || (l = !0), s(c) || (c = n !== "mousemove"), o(h) || (h = e.config.win), u(p) || (p = 1), u(d) || (d = 0), u(v) || (v = 0), u(m) || (m = 0), u(g) || (g = 0), s(y) || (y = !1), s(b) || (b = !1), s(w) || (w = !1), s(E) || (E = !1), u(S) || (S = 0), x = x || null;
      var T = null;
      if (r(e.config.doc.createEvent)) T = e.config.doc.createEvent("MouseEvents"), T.initMouseEvent ? T.initMouseEvent(n, l, c, h, p, d, v, m, g, y, b, w, E, S, x) : (T = e.config.doc.createEvent("UIEvents"), T.initEvent(n, l, c), T.view = h, T.detail = p, T.screenX = d, T.screenY = v, T.clientX = m, T.clientY = g, T.ctrlKey = y, T.altKey = b, T.metaKey = E, T.shiftKey = w, T.button = S, T.relatedTarget = x), x && !T.relatedTarget && (n === "mouseout" ? T.toElement = x : n === "mouseover" && (T.fromElement = x)), t.dispatchEvent(T);
      else if (o(e.config.doc.createEventObject)) {
        T = e.config.doc.createEventObject(), T.bubbles = l, T.cancelable = c, T.view = h, T.detail = p, T.screenX = d, T.screenY = v, T.clientX = m, T.clientY = g, T.ctrlKey = y, T.altKey = b, T.metaKey = E, T.shiftKey = w;
        switch (S) {
          case 0:
            T.button = 1;
            break;
          case 1:
            T.button = 4;
            break;
          case 2:
            break;
          default:
            T.button = 0
        }
        T.relatedTarget = x, t.fireEvent("on" + n, T)
      } else e.error("simulateMouseEvent(): No event simulation framework present.")
    }

    function g(t, n, a, f, l, p) {
      t || e.error("simulateUIEvent(): Invalid target."), i(n) ? (n = n.toLowerCase(), c[n] || e.error("simulateUIEvent(): Event type '" + n + "' not supported.")) : e.error("simulateUIEvent(): Event type must be a string.");
      var d = null;
      s(a) || (a = n in h), s(f) || (f = n === "submit"), o(l) || (l = e.config.win), u(p) || (p = 1), r(e.config.doc.createEvent) ? (d = e.config.doc.createEvent("UIEvents"), d.initUIEvent(n, a, f, l, p), t.dispatchEvent(d)) : o(e.config.doc.createEventObject) ? (d = e.config.doc.createEventObject(), d.bubbles = a, d.cancelable = f, d.view = l, d.detail = p, t.fireEvent("on" + n, d)) : e.error("simulateUIEvent(): No event simulation framework present.")
    }

    function y(t, n, r, i, s, o, u, a, f, l, c, h, p, v, m, g) {
      var y;
      (!e.UA.ios || e.UA.ios < 2) && e.error("simulateGestureEvent(): Native gesture DOM eventframe is not available in this platform."), t || e.error("simulateGestureEvent(): Invalid target."), e.Lang.isString(n) ? (n = n.toLowerCase(), d[n] || e.error("simulateTouchEvent(): Event type '" + n + "' not supported.")) : e.error("simulateGestureEvent(): Event type must be a string."), e.Lang.isBoolean(r) || (r = !0), e.Lang.isBoolean(i) || (i = !0), e.Lang.isObject(s) || (s = e.config.win), e.Lang.isNumber(o) || (o = 2), e.Lang.isNumber(u) || (u = 0), e.Lang.isNumber(a) || (a = 0), e.Lang.isNumber(f) || (f = 0), e.Lang.isNumber(l) || (l = 0), e.Lang.isBoolean(c) || (c = !1), e.Lang.isBoolean(h) || (h = !1), e.Lang.isBoolean(p) || (p = !1), e.Lang.isBoolean(v) || (v = !1), e.Lang.isNumber(m) || (m = 1), e.Lang.isNumber(g) || (g = 0), y = e.config.doc.createEvent("GestureEvent"), y.initGestureEvent(n, r, i, s, o, u, a, f, l, c, h, p, v, t, m, g), t.dispatchEvent(y)
    }

    function b(t, n, r, i, s, o, u, a, f, l, c, h, d, v, m, g, y, b, w) {
      var E;
      t || e.error("simulateTouchEvent(): Invalid target."), e.Lang.isString(n) ? (n = n.toLowerCase(), p[n] || e.error("simulateTouchEvent(): Event type '" + n + "' not supported.")) : e.error("simulateTouchEvent(): Event type must be a string."), n === "touchstart" || n === "touchmove" ? m.length === 0 && e.error("simulateTouchEvent(): No touch object in touches") : n === "touchend" && y.length === 0 && e.error("simulateTouchEvent(): No touch object in changedTouches"), e.Lang.isBoolean(r) || (r = !0), e.Lang.isBoolean(i) || (i = n !== "touchcancel"), e.Lang.isObject(s) || (s = e.config.win), e.Lang.isNumber(o) || (o = 1), e.Lang.isNumber(u) || (u = 0), e.Lang.isNumber(a) || (a = 0), e.Lang.isNumber(f) || (f = 0), e.Lang.isNumber(l) || (l = 0), e.Lang.isBoolean(c) || (c = !1), e.Lang.isBoolean(h) || (h = !1), e.Lang.isBoolean(d) || (d = !1), e.Lang.isBoolean(v) || (v = !1), e.Lang.isNumber(b) || (b = 1), e.Lang.isNumber(w) || (w = 0), e.Lang.isFunction(e.config.doc.createEvent) ? (e.UA.android ? e.UA.android < 4 ? (E = e.config.doc.createEvent("MouseEvents"), E.initMouseEvent(n, r, i, s, o, u, a, f, l, c, h, d, v, 0, t), E.touches = m, E.targetTouches = g, E.changedTouches = y) : (E = e.config.doc.createEvent("TouchEvent"), E.initTouchEvent(m, g, y, n, s, u, a, f, l, c, h, d, v)) : e.UA.ios ? e.UA.ios >= 2 ? (E = e.config.doc.createEvent("TouchEvent"), E.initTouchEvent(n, r, i, s, o, u, a, f, l, c, h, d, v, m, g, y, b, w)) : e.error("simulateTouchEvent(): No touch event simulation framework present for iOS, " + e.UA.ios + ".") : e.error("simulateTouchEvent(): Not supported agent yet, " + e.UA.userAgent), t.dispatchEvent(E)) : e.error("simulateTouchEvent(): No event simulation framework present.")
    }
    var t = e.Lang,
      n = e.config.win,
      r = t.isFunction,
      i = t.isString,
      s = t.isBoolean,
      o = t.isObject,
      u = t.isNumber,
      a = {
        click: 1,
        dblclick: 1,
        mouseover: 1,
        mouseout: 1,
        mousedown: 1,
        mouseup: 1,
        mousemove: 1,
        contextmenu: 1
      },
      f = n && n.PointerEvent ? {
        pointerover: 1,
        pointerout: 1,
        pointerdown: 1,
        pointerup: 1,
        pointermove: 1
      } : {
        MSPointerOver: 1,
        MSPointerOut: 1,
        MSPointerDown: 1,
        MSPointerUp: 1,
        MSPointerMove: 1
      },
      l = {
        keydown: 1,
        keyup: 1,
        keypress: 1
      },
      c = {
        submit: 1,
        blur: 1,
        change: 1,
        focus: 1,
        resize: 1,
        scroll: 1,
        select: 1
      },
      h = {
        scroll: 1,
        resize: 1,
        reset: 1,
        submit: 1,
        change: 1,
        select: 1,
        error: 1,
        abort: 1
      },
      p = {
        touchstart: 1,
        touchmove: 1,
        touchend: 1,
        touchcancel: 1
      },
      d = {
        gesturestart: 1,
        gesturechange: 1,
        gestureend: 1
      };
    e.mix(h, a), e.mix(h, l), e.mix(h, p), e.Event.simulate = function(t, n, r) {
      r = r || {}, a[n] || f[n] ? m(t, n, r.bubbles, r.cancelable, r.view, r.detail, r.screenX, r.screenY, r.clientX, r.clientY, r.ctrlKey, r.altKey, r.shiftKey, r.metaKey, r.button, r.relatedTarget) : l[n] ? v(t, n, r.bubbles, r.cancelable, r.view, r.ctrlKey, r.altKey, r.shiftKey, r.metaKey, r.keyCode, r.charCode) : c[n] ? g(t, n, r.bubbles, r.cancelable, r.view, r.detail) : p[n] ? e.config.win && "ontouchstart" in e.config.win && !e.UA.phantomjs && !(e.UA.chrome && e.UA.chrome < 6) ? b(t, n, r.bubbles, r.cancelable, r.view, r.detail, r.screenX, r.screenY, r.clientX, r.clientY, r.ctrlKey, r.altKey, r.shiftKey, r.metaKey, r.touches, r.targetTouches, r.changedTouches, r.scale, r.rotation) : e.error("simulate(): Event '" + n + "' can't be simulated. Use gesture-simulate module instead.") : e.UA.ios && e.UA.ios >= 2 && d[n] ? y(t, n, r.bubbles, r.cancelable, r.view, r.detail, r.screenX, r.screenY, r.clientX, r.clientY, r.ctrlKey, r.altKey, r.shiftKey, r.metaKey, r.scale, r.rotation) : e.error("simulate(): Event '" + n + "' can't be simulated.")
    }
  })()
}, "@VERSION@", {
  requires: ["event-base"]
});

YUI.add("async-queue", function(e, t) {
  e.AsyncQueue = function() {
    this._init(), this.add.apply(this, arguments)
  };
  var n = e.AsyncQueue,
    r = "execute",
    i = "shift",
    s = "promote",
    o = "remove",
    u = e.Lang.isObject,
    a = e.Lang.isFunction;
  n.defaults = e.mix({
    autoContinue: !0,
    iterations: 1,
    timeout: 10,
    until: function() {
      return this.iterations |= 0, this.iterations <= 0
    }
  }, e.config.queueDefaults || {}), e.extend(n, e.EventTarget, {
    _running: !1,
    _init: function() {
      e.EventTarget.call(this, {
        prefix: "queue",
        emitFacade: !0
      }), this._q = [], this.defaults = {}, this._initEvents()
    },
    _initEvents: function() {
      this.publish({
        execute: {
          defaultFn: this._defExecFn,
          emitFacade: !0
        },
        shift: {
          defaultFn: this._defShiftFn,
          emitFacade: !0
        },
        add: {
          defaultFn: this._defAddFn,
          emitFacade: !0
        },
        promote: {
          defaultFn: this._defPromoteFn,
          emitFacade: !0
        },
        remove: {
          defaultFn: this._defRemoveFn,
          emitFacade: !0
        }
      })
    },
    next: function() {
      var e;
      while (this._q.length) {
        e = this._q[0] = this._prepare(this._q[0]);
        if (!e || !e.until()) break;
        this.fire(i, {
          callback: e
        }), e = null
      }
      return e || null
    },
    _defShiftFn: function(e) {
      this.indexOf(e.callback) === 0 && this._q.shift()
    },
    _prepare: function(t) {
      if (a(t) && t._prepared) return t;
      var r = e.merge(n.defaults, {
          context: this,
          args: [],
          _prepared: !0
        }, this.defaults, a(t) ? {
          fn: t
        } : t),
        i = e.bind(function() {
          i._running || i.iterations--, a(i.fn) && i.fn.apply(i.context || e, e.Array(i.args))
        }, this);
      return e.mix(i, r)
    },
    run: function() {
      var e, t = !0;
      if (this._executing) return this._running = !0, this;
      for (e = this.next(); e && !this.isRunning(); e = this.next()) {
        t = e.timeout < 0 ? this._execute(e) : this._schedule(e);
        if (!t) break
      }
      return e || this.fire("complete"), this
    },
    _execute: function(e) {
      this._running = e._running = !0, this._executing = e, e.iterations--, this.fire(r, {
        callback: e
      });
      var t = this._running && e.autoContinue;
      return this._running = e._running = !1, this._executing = !1, t
    },
    _schedule: function(t) {
      return this._running = e.later(t.timeout, this, function() {
        this._execute(t) && this.run()
      }), !1
    },
    isRunning: function() {
      return !!this._running
    },
    _defExecFn: function(e) {
      e.callback()
    },
    add: function() {
      return this.fire("add", {
        callbacks: e.Array(arguments, 0, !0)
      }), this
    },
    _defAddFn: function(t) {
      var n = this._q,
        r = [];
      e.Array.each(t.callbacks, function(e) {
        u(e) && (n.push(e), r.push(e))
      }), t.added = r
    },
    pause: function() {
      return this._running && u(this._running) && this._running.cancel(), this._running = !1, this
    },
    stop: function() {
      return this._q = [], this._running && u(this._running) && (this._running.cancel(), this._running = !1), this._executing || this.run(), this
    },
    indexOf: function(e) {
      var t = 0,
        n = this._q.length,
        r;
      for (; t < n; ++t) {
        r = this._q[t];
        if (r === e || r.id === e) return t
      }
      return -1
    },
    getCallback: function(e) {
      var t = this.indexOf(e);
      return t > -1 ? this._q[t] : null
    },
    promote: function(e) {
      var t = {
          callback: e
        },
        n;
      return this.isRunning() ? n = this.after(i, function() {
        this.fire(s, t), n.detach()
      }, this) : this.fire(s, t), this
    },
    _defPromoteFn: function(e) {
      var t = this.indexOf(e.callback),
        n = t > -1 ? this._q.splice(t, 1)[0] : null;
      e.promoted = n, n && this._q.unshift(n)
    },
    remove: function(e) {
      var t = {
          callback: e
        },
        n;
      return this.isRunning() ? n = this.after(i, function() {
        this.fire(o, t), n.detach()
      }, this) : this.fire(o, t), this
    },
    _defRemoveFn: function(e) {
      var t = this.indexOf(e.callback);
      e.removed = t > -1 ? this._q.splice(t, 1)[0] : null
    },
    size: function() {
      return this.isRunning() || this.next(), this._q.length
    }
  })
}, "@VERSION@", {
  requires: ["event-custom"]
});

YUI.add("gesture-simulate", function(e, t) {
  function T(n) {
    n || e.error(t + ": invalid target node"), this.node = n, this.target = e.Node.getDOMNode(n);
    var r = this.node.getXY(),
      i = this._getDims();
    a = r[0] + i[0] / 2, f = r[1] + i[1] / 2
  }
  var t = "gesture-simulate",
    n = e.config.win && "ontouchstart" in e.config.win && !e.UA.phantomjs && !(e.UA.chrome && e.UA.chrome < 6),
    r = {
      tap: 1,
      doubletap: 1,
      press: 1,
      move: 1,
      flick: 1,
      pinch: 1,
      rotate: 1
    },
    i = {
      touchstart: 1,
      touchmove: 1,
      touchend: 1,
      touchcancel: 1
    },
    s = e.config.doc,
    o, u = 20,
    a, f, l = {
      HOLD_TAP: 10,
      DELAY_TAP: 10,
      HOLD_PRESS: 3e3,
      MIN_HOLD_PRESS: 1e3,
      MAX_HOLD_PRESS: 6e4,
      DISTANCE_MOVE: 200,
      DURATION_MOVE: 1e3,
      MAX_DURATION_MOVE: 5e3,
      MIN_VELOCITY_FLICK: 1.3,
      DISTANCE_FLICK: 200,
      DURATION_FLICK: 1e3,
      MAX_DURATION_FLICK: 5e3,
      DURATION_PINCH: 1e3
    },
    c = "touchstart",
    h = "touchmove",
    p = "touchend",
    d = "gesturestart",
    v = "gesturechange",
    m = "gestureend",
    g = "mouseup",
    y = "mousemove",
    b = "mousedown",
    w = "click",
    E = "dblclick",
    S = "x",
    x = "y";
  T.prototype = {
    _toRadian: function(e) {
      return e * (Math.PI / 180)
    },
    _getDims: function() {
      var e, t, n;
      return this.target.getBoundingClientRect ? (e = this.target.getBoundingClientRect(), "height" in e ? n = e.height : n = Math.abs(e.bottom - e.top), "width" in e ? t = e.width : t = Math.abs(e.right - e.left)) : (e = this.node.get("region"), t = e.width, n = e.height), [t, n]
    },
    _calculateDefaultPoint: function(t) {
      var n;
      return !e.Lang.isArray(t) || t.length === 0 ? t = [a, f] : (t.length == 1 && (n = this._getDims[1], t[1] = n / 2), t[0] = this.node.getX() + t[0], t[1] = this.node.getY() + t[1]), t
    },
    rotate: function(n, r, i, s, o, u, a) {
      var f, l = i,
        c = s;
      if (!e.Lang.isNumber(l) || !e.Lang.isNumber(c) || l < 0 || c < 0) f = this.target.offsetWidth < this.target.offsetHeight ? this.target.offsetWidth / 4 : this.target.offsetHeight / 4, l = f, c = f;
      e.Lang.isNumber(a) || e.error(t + "Invalid rotation detected."), this.pinch(n, r, l, c, o, u, a)
    },
    pinch: function(n, r, i, s, o, a, f) {
      var g, y, b = u,
        w, E = 0,
        S = i,
        x = s,
        T, N, C, k, L, A, O, M, _, D = {
          start: [],
          end: []
        },
        P = {
          start: [],
          end: []
        },
        H, B;
      r = this._calculateDefaultPoint(r), (!e.Lang.isNumber(S) || !e.Lang.isNumber(x) || S < 0 || x < 0) && e.error(t + "Invalid startRadius and endRadius detected.");
      if (!e.Lang.isNumber(o) || o <= 0) o = l.DURATION_PINCH;
      if (!e.Lang.isNumber(a)) a = 0;
      else {
        a %= 360;
        while (a < 0) a += 360
      }
      e.Lang.isNumber(f) || (f = 0), e.AsyncQueue.defaults.timeout = b, g = new e.AsyncQueue, N = r[0], C = r[1], O = a, M = a + f, D.start = [N + S * Math.sin(this._toRadian(O)), C - S * Math.cos(this._toRadian(O))], D.end = [N + x * Math.sin(this._toRadian(M)), C - x * Math.cos(this._toRadian(M))], P.start = [N - S * Math.sin(this._toRadian(O)), C + S * Math.cos(this._toRadian(O))], P.end = [N - x * Math.sin(this._toRadian(M)), C + x * Math.cos(this._toRadian(M))], k = 1, L = s / i, g.add({
        fn: function() {
          var t, n, r, i;
          t = {
            pageX: D.start[0],
            pageY: D.start[1],
            clientX: D.start[0],
            clientY: D.start[1]
          }, n = {
            pageX: P.start[0],
            pageY: P.start[1],
            clientX: P.start[0],
            clientY: P.start[1]
          }, i = this._createTouchList([e.merge({
            identifier: E++
          }, t), e.merge({
            identifier: E++
          }, n)]), r = {
            pageX: (D.start[0] + P.start[0]) / 2,
            pageY: (D.start[0] + P.start[1]) / 2,
            clientX: (D.start[0] + P.start[0]) / 2,
            clientY: (D.start[0] + P.start[1]) / 2
          }, this._simulateEvent(this.target, c, e.merge({
            touches: i,
            targetTouches: i,
            changedTouches: i,
            scale: k,
            rotation: O
          }, r)), e.UA.ios >= 2 && this._simulateEvent(this.target, d, e.merge({
            scale: k,
            rotation: O
          }, r))
        },
        timeout: 0,
        context: this
      }), H = Math.floor(o / b), T = (x - S) / H, A = (L - k) / H, _ = (M - O) / H, B = function(t) {
        var n = S + T * t,
          r = N + n * Math.sin(this._toRadian(O + _ * t)),
          i = C - n * Math.cos(this._toRadian(O + _ * t)),
          s = N - n * Math.sin(this._toRadian(O + _ * t)),
          o = C + n * Math.cos(this._toRadian(O + _ * t)),
          u = (r + s) / 2,
          a = (i + o) / 2,
          f, l, c, p;
        f = {
          pageX: r,
          pageY: i,
          clientX: r,
          clientY: i
        }, l = {
          pageX: s,
          pageY: o,
          clientX: s,
          clientY: o
        }, p = this._createTouchList([e.merge({
          identifier: E++
        }, f), e.merge({
          identifier: E++
        }, l)]), c = {
          pageX: u,
          pageY: a,
          clientX: u,
          clientY: a
        }, this._simulateEvent(this.target, h, e.merge({
          touches: p,
          targetTouches: p,
          changedTouches: p,
          scale: k + A * t,
          rotation: O + _ * t
        }, c)), e.UA.ios >= 2 && this._simulateEvent(this.target, v, e.merge({
          scale: k + A * t,
          rotation: O + _ * t
        }, c))
      };
      for (y = 0; y < H; y++) g.add({
        fn: B,
        args: [y],
        context: this
      });
      g.add({
        fn: function() {
          var t = this._getEmptyTouchList(),
            n, r, i, s;
          n = {
            pageX: D.end[0],
            pageY: D.end[1],
            clientX: D.end[0],
            clientY: D.end[1]
          }, r = {
            pageX: P.end[0],
            pageY: P.end[1],
            clientX: P.end[0],
            clientY: P.end[1]
          }, s = this._createTouchList([e.merge({
            identifier: E++
          }, n), e.merge({
            identifier: E++
          }, r)]), i = {
            pageX: (D.end[0] + P.end[0]) / 2,
            pageY: (D.end[0] + P.end[1]) / 2,
            clientX: (D.end[0] + P.end[0]) / 2,
            clientY: (D.end[0] + P.end[1]) / 2
          }, e.UA.ios >= 2 && this._simulateEvent(this.target, m, e.merge({
            scale: L,
            rotation: M
          }, i)), this._simulateEvent(this.target, p, e.merge({
            touches: t,
            targetTouches: t,
            changedTouches: s,
            scale: L,
            rotation: M
          }, i))
        },
        context: this
      }), n && e.Lang.isFunction(n) && g.add({
        fn: n,
        context: this.node
      }), g.run()
    },
    tap: function(t, r, i, s, o) {
      var u = new e.AsyncQueue,
        a = this._getEmptyTouchList(),
        f, h, d, v, m;
      r = this._calculateDefaultPoint(r);
      if (!e.Lang.isNumber(i) || i < 1) i = 1;
      e.Lang.isNumber(s) || (s = l.HOLD_TAP), e.Lang.isNumber(o) || (o = l.DELAY_TAP), h = {
        pageX: r[0],
        pageY: r[1],
        clientX: r[0],
        clientY: r[1]
      }, f = this._createTouchList([e.merge({
        identifier: 0
      }, h)]), v = function() {
        this._simulateEvent(this.target, c, e.merge({
          touches: f,
          targetTouches: f,
          changedTouches: f
        }, h))
      }, m = function() {
        this._simulateEvent(this.target, p, e.merge({
          touches: a,
          targetTouches: a,
          changedTouches: f
        }, h))
      };
      for (d = 0; d < i; d++) u.add({
        fn: v,
        context: this,
        timeout: d === 0 ? 0 : o
      }), u.add({
        fn: m,
        context: this,
        timeout: s
      });
      i > 1 && !n && u.add({
        fn: function() {
          this._simulateEvent(this.target, E, h)
        },
        context: this
      }), t && e.Lang.isFunction(t) && u.add({
        fn: t,
        context: this.node
      }), u.run()
    },
    flick: function(n, r, i, s, o) {
      var u;
      r = this._calculateDefaultPoint(r), e.Lang.isString(i) ? (i = i.toLowerCase(), i !== S && i !== x && e.error(t + "(flick): Only x or y axis allowed")) : i = S, e.Lang.isNumber(s) || (s = l.DISTANCE_FLICK), e.Lang.isNumber(o) ? o > l.MAX_DURATION_FLICK && (o = l.MAX_DURATION_FLICK) : o = l.DURATION_FLICK, Math.abs(s) / o < l.MIN_VELOCITY_FLICK && (o = Math.abs(s) / l.MIN_VELOCITY_FLICK), u = {
        start: e.clone(r),
        end: [i === S ? r[0] + s : r[0], i === x ? r[1] + s : r[1]]
      }, this._move(n, u, o)
    },
    move: function(t, n, r) {
      var i;
      e.Lang.isObject(n) ? (e.Lang.isArray(n.point) ? n.point = this._calculateDefaultPoint(n.point) : n.point = this._calculateDefaultPoint([]), e.Lang.isNumber(n.xdist) || (n.xdist = l.DISTANCE_MOVE), e.Lang.isNumber(n.ydist) || (n.ydist = 0)) : n = {
        point: this._calculateDefaultPoint([]),
        xdist: l.
        DISTANCE_MOVE,
        ydist: 0
      }, e.Lang.isNumber(r) ? r > l.MAX_DURATION_MOVE && (r = l.MAX_DURATION_MOVE) : r = l.DURATION_MOVE, i = {
        start: e.clone(n.point),
        end: [n.point[0] + n.xdist, n.point[1] + n.ydist]
      }, this._move(t, i, r)
    },
    _move: function(t, n, r) {
      var i, s, o = u,
        d, v, m, g = 0,
        y;
      e.Lang.isNumber(r) ? r > l.MAX_DURATION_MOVE && (r = l.MAX_DURATION_MOVE) : r = l.DURATION_MOVE, e.Lang.isObject(n) ? (e.Lang.isArray(n.start) || (n.start = [a, f]), e.Lang.isArray(n.end) || (n.end = [a + l.DISTANCE_MOVE, f])) : n = {
        start: [a, f],
        end: [a + l.DISTANCE_MOVE, f]
      }, e.AsyncQueue.defaults.timeout = o, i = new e.AsyncQueue, i.add({
        fn: function() {
          var t = {
              pageX: n.start[0],
              pageY: n.start[1],
              clientX: n.start[0],
              clientY: n.start[1]
            },
            r = this._createTouchList([e.merge({
              identifier: g++
            }, t)]);
          this._simulateEvent(this.target, c, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: r
          }, t))
        },
        timeout: 0,
        context: this
      }), d = Math.floor(r / o), v = (n.end[0] - n.start[0]) / d, m = (n.end[1] - n.start[1]) / d, y = function(t) {
        var r = n.start[0] + v * t,
          i = n.start[1] + m * t,
          s = {
            pageX: r,
            pageY: i,
            clientX: r,
            clientY: i
          },
          o = this._createTouchList([e.merge({
            identifier: g++
          }, s)]);
        this._simulateEvent(this.target, h, e.merge({
          touches: o,
          targetTouches: o,
          changedTouches: o
        }, s))
      };
      for (s = 0; s < d; s++) i.add({
        fn: y,
        args: [s],
        context: this
      });
      i.add({
        fn: function() {
          var t = {
              pageX: n.end[0],
              pageY: n.end[1],
              clientX: n.end[0],
              clientY: n.end[1]
            },
            r = this._createTouchList([e.merge({
              identifier: g
            }, t)]);
          this._simulateEvent(this.target, h, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: r
          }, t))
        },
        timeout: 0,
        context: this
      }), i.add({
        fn: function() {
          var t = {
              pageX: n.end[0],
              pageY: n.end[1],
              clientX: n.end[0],
              clientY: n.end[1]
            },
            r = this._getEmptyTouchList(),
            i = this._createTouchList([e.merge({
              identifier: g
            }, t)]);
          this._simulateEvent(this.target, p, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: i
          }, t))
        },
        context: this
      }), t && e.Lang.isFunction(t) && i.add({
        fn: t,
        context: this.node
      }), i.run()
    },
    _getEmptyTouchList: function() {
      return o || (o = this._createTouchList([])), o
    },
    _createTouchList: function(n) {
      var r = [],
        i, o = this;
      return !!n && e.Lang.isArray(n) ? e.UA.android && e.UA.android >= 4 || e.UA.ios && e.UA.ios >= 2 ? (e.each(n, function(t) {
        t.identifier || (t.identifier = 0), t.pageX || (t.pageX = 0), t.pageY || (t.pageY = 0), t.screenX || (t.screenX = 0), t.screenY || (t.screenY = 0), r.push(s.createTouch(e.config.win, o.target, t.identifier, t.pageX, t.pageY, t.screenX, t.screenY))
      }), i = s.createTouchList.apply(s, r)) : e.UA.ios && e.UA.ios < 2 ? e.error(t + ": No touch event simulation framework present.") : (i = [], e.each(n, function(e) {
        e.identifier || (e.identifier = 0), e.clientX || (e.clientX = 0), e.clientY || (e.clientY = 0), e.pageX || (e.pageX = 0), e.pageY || (e.pageY = 0), e.screenX || (e.screenX = 0), e.screenY || (e.screenY = 0), i.push({
          target: o.target,
          identifier: e.identifier,
          clientX: e.clientX,
          clientY: e.clientY,
          pageX: e.pageX,
          pageY: e.pageY,
          screenX: e.screenX,
          screenY: e.screenY
        })
      }), i.item = function(e) {
        return i[e]
      }) : e.error(t + ": Invalid touchPoints passed"), i
    },
    _simulateEvent: function(t, r, s) {
      var o;
      i[r] ? n ? e.Event.simulate(t, r, s) : this._isSingleTouch(s.touches, s.targetTouches, s.changedTouches) ? (r = {
        touchstart: b,
        touchmove: y,
        touchend: g
      } [r], s.button = 0, s.relatedTarget = null, o = r === g ? s.changedTouches : s.touches, s = e.mix(s, {
        screenX: o.item(0).screenX,
        screenY: o.item(0).screenY,
        clientX: o.item(0).clientX,
        clientY: o.item(0).clientY
      }, !0), e.Event.simulate(t, r, s), r == g && e.Event.simulate(t, w, s)) : e.error("_simulateEvent(): Event '" + r + "' has multi touch objects that can't be simulated in your platform.") : e.Event.simulate(t, r, s)
    },
    _isSingleTouch: function(e, t, n) {
      return e && e.length <= 1 && t && t.length <= 1 && n && n.length <= 1
    }
  }, e.GestureSimulation = T, e.GestureSimulation.defaults = l, e.GestureSimulation.GESTURES = r, e.Event.simulateGesture = function(n, i, s, o) {
    n = e.one(n);
    var u = new e.GestureSimulation(n);
    i = i.toLowerCase(), !o && e.Lang.isFunction(s) && (o = s, s = {}), s = s || {};
    if (r[i]) switch (i) {
      case "tap":
        u.tap(o, s.point, s.times, s.hold, s.delay);
        break;
      case "doubletap":
        u.tap(o, s.point, 2);
        break;
      case "press":
        e.Lang.isNumber(s.hold) ? s.hold < l.MIN_HOLD_PRESS ? s.hold = l.MIN_HOLD_PRESS : s.hold > l.MAX_HOLD_PRESS && (s.hold = l.MAX_HOLD_PRESS) : s.hold = l.HOLD_PRESS, u.tap(o, s.point, 1, s.hold);
        break;
      case "move":
        u.move(o, s.path, s.duration);
        break;
      case "flick":
        u.flick(o, s.point, s.axis, s.distance, s.duration);
        break;
      case "pinch":
        u.pinch(o, s.center, s.r1, s.r2, s.duration, s.start, s.rotation);
        break;
      case "rotate":
        u.rotate(o, s.center, s.r1, s.r2, s.duration, s.start, s.rotation)
    } else e.error(t + ": Not a supported gesture simulation: " + i)
  }
}, "@VERSION@", {
  requires: ["async-queue", "event-simulate", "node-screen"]
});

YUI.add("node-event-simulate", function(e, t) {
  e.Node.prototype.simulate = function(t, n) {
    e.Event.simulate(e.Node.getDOMNode(this), t, n)
  }, e.Node.prototype.simulateGesture = function(t, n, r) {
    e.Event.simulateGesture(this, t, n, r)
  }
}, "@VERSION@", {
  requires: ["node-base", "event-simulate", "gesture-simulate"]
});