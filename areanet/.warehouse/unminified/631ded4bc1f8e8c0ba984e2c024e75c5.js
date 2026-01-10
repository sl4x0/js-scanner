YUI.add("attribute-complex", function(e, t) {
  var n = e.Attribute;
  n.Complex = function() {}, n.Complex.prototype = {
    _normAttrVals: n.prototype._normAttrVals,
    _getAttrInitVal: n.prototype._getAttrInitVal
  }, e.AttributeComplex = n.Complex
}, "@VERSION@", {
  requires: ["attribute-base"]
});

YUI.add("base-pluginhost", function(e, t) {
  var n = e.Base,
    r = e.Plugin.Host;
  e.mix(n, r, !1, null, 1), n.plug = r.plug, n.unplug = r.unplug
}, "@VERSION@", {
  requires: ["base-base", "pluginhost"]
});

YUI.add("classnamemanager", function(e, t) {
  var n = "classNamePrefix",
    r = "classNameDelimiter",
    i = e.config;
  i[n] = i[n] || "yui3", i[r] = i[r] || "-", e.ClassNameManager = function() {
    var t = i[n],
      s = i[r];
    return {
      getClassName: e.cached(function() {
        var n = e.Array(arguments);
        return n[n.length - 1] !== !0 ? n.unshift(t) : n.pop(), n.join(s)
      })
    }
  }()
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("widget-base", function(e, t) {
  function R(e) {
    var t = this,
      n, r, i = t.constructor;
    t._strs = {}, t._cssPrefix = i.CSS_PREFIX || s(i.NAME.toLowerCase()), e = e || {}, R.superclass.constructor.call(t, e), r = t.get(T), r && (r !== P && (n = r), t.render(n))
  }
  var n = e.Lang,
    r = e.Node,
    i = e.ClassNameManager,
    s = i.getClassName,
    o, u = e.cached(function(e) {
      return e.substring(0, 1).toUpperCase() + e.substring(1)
    }),
    a = "content",
    f = "visible",
    l = "hidden",
    c = "disabled",
    h = "focused",
    p = "width",
    d = "height",
    v = "boundingBox",
    m = "contentBox",
    g = "parentNode",
    y = "ownerDocument",
    b = "auto",
    w = "srcNode",
    E = "body",
    S = "tabIndex",
    x = "id",
    T = "render",
    N = "rendered",
    C = "destroyed",
    k = "strings",
    L = "<div></div>",
    A = "Change",
    O = "loading",
    M = "_uiSet",
    _ = "",
    D = function() {},
    P = !0,
    H = !1,
    B, j = {},
    F = [f, c, d, p, h, S],
    I = e.UA.webkit,
    q = {};
  R.NAME = "widget", B = R.UI_SRC = "ui", R.ATTRS = j, j[x] = {
    valueFn: "_guid",
    writeOnce: P
  }, j[N] = {
    value: H,
    readOnly: P
  }, j[v] = {
    valueFn: "_defaultBB",
    setter: "_setBB",
    writeOnce: P
  }, j[m] = {
    valueFn: "_defaultCB",
    setter: "_setCB",
    writeOnce: P
  }, j[S] = {
    value: null,
    validator: "_validTabIndex"
  }, j[h] = {
    value: H,
    readOnly: P
  }, j[c] = {
    value: H
  }, j[f] = {
    value: P
  }, j[d] = {
    value: _
  }, j[p] = {
    value: _
  }, j[k] = {
    value: {},
    setter: "_strSetter",
    getter: "_strGetter"
  }, j[T] = {
    value: H,
    writeOnce: P
  }, R.CSS_PREFIX = s(R.NAME.toLowerCase()), R.getClassName = function() {
    return s.apply(i, [R.CSS_PREFIX].concat(e.Array(arguments), !0))
  }, o = R.getClassName, R.getByNode = function(t) {
    var n, i = o();
    return t = r.one(t), t && (t = t.ancestor("." + i, !0), t && (n = q[e.stamp(t, !0)])), n || null
  }, e.extend(R, e.Base, {
    getClassName: function() {
      return s.apply(i, [this._cssPrefix].concat(e.Array(arguments), !0))
    },
    initializer: function(t) {
      var n = this.get(v);
      n instanceof r && this._mapInstance(e.stamp(n))
    },
    _mapInstance: function(e) {
      q[e] = this
    },
    destructor: function() {
      var t = this.get(v),
        n;
      t instanceof r && (n = e.stamp(t, !0), n in q && delete q[n], this._destroyBox())
    },
    destroy: function(e) {
      return this._destroyAllNodes = e, R.superclass.destroy.apply(this)
    },
    _destroyBox: function() {
      var e = this.get(v),
        t = this.get(m),
        n = this._destroyAllNodes,
        r;
      r = e && e.compareTo(t), this.UI_EVENTS && this._destroyUIEvents(), this._unbindUI(e), t && (n && t.empty(), t.remove(P)), r || (n && e.empty(), e.remove(P))
    },
    render: function(e) {
      return !this.get(C) && !this.get(N) && (this.publish(T, {
        queuable: H,
        fireOnce: P,
        defaultTargetOnly: P,
        defaultFn: this._defRenderFn
      }), this.fire(T, {
        parentNode: e ? r.one(e) : null
      })), this
    },
    _defRenderFn: function(e) {
      this._parentNode = e.parentNode, this.renderer(), this._set(N, P), this._removeLoadingClassNames()
    },
    renderer: function() {
      var e = this;
      e._renderUI(), e.renderUI(), e._bindUI(), e.bindUI(), e._syncUI(), e.syncUI()
    },
    bindUI: D,
    renderUI: D,
    syncUI: D,
    hide: function() {
      return this.set(f, H)
    },
    show: function() {
      return this.set(f, P)
    },
    focus: function() {
      return this._set(h, P)
    },
    blur: function() {
      return this._set(h, H)
    },
    enable: function() {
      return this.set(c, H)
    },
    disable: function() {
      return this.set(c, P)
    },
    _uiSizeCB: function(e) {
      this.get(m).toggleClass(o(a, "expanded"), e)
    },
    _renderBox: function(e) {
      var t = this,
        n = t.get(m),
        i = t.get(v),
        s = t.get(w),
        o = t.DEF_PARENT_NODE,
        u = s && s.get(y) || i.get(y) || n.get(y);
      s && !s.compareTo(n) && !n.inDoc(u) && s.replace(n), !i.compareTo(n.get(g)) && !i.compareTo(n) && (n.inDoc(u) && n.replace(i), i.appendChild(n)), e = e || o && r.one(o), e ? e.appendChild(i) : i.inDoc(u) || r.one(E).insert(i, 0)
    },
    _setBB: function(e) {
      return this._setBox(this.get(x), e, this.BOUNDING_TEMPLATE, !0)
    },
    _setCB: function(e) {
      return this.CONTENT_TEMPLATE === null ? this.get(v) : this._setBox(null, e, this.CONTENT_TEMPLATE, !1)
    },
    _defaultBB: function() {
      var e = this.get(w),
        t = this.CONTENT_TEMPLATE === null;
      return e && t ? e : null
    },
    _defaultCB: function(e) {
      return this.get(w) || null
    },
    _setBox: function(t, n, i, s) {
      return n = r.one(n), n || (n = r.create(i), s ? this._bbFromTemplate = !0 : this._cbFromTemplate = !0), n.get(x) || n.set(x, t || e.guid()), n
    },
    _renderUI: function() {
      this._renderBoxClassNames(), this._renderBox(this._parentNode)
    },
    _renderBoxClassNames: function() {
      var e = this._getClasses(),
        t, n = this.get(v),
        r;
      n.addClass(o());
      for (r = e.length - 3; r >= 0; r--) t = e[r], n.addClass(t.CSS_PREFIX || s(t.NAME.toLowerCase()));
      this.get(m).addClass(this.getClassName(a))
    },
    _removeLoadingClassNames: function() {
      var e = this.get(v),
        t = this.get(m),
        n = this.getClassName(O),
        r = o(O);
      e.removeClass(r).removeClass(n), t.removeClass(r).removeClass(n)
    },
    _bindUI: function() {
      this._bindAttrUI(this._UI_ATTRS.BIND), this._bindDOM()
    },
    _unbindUI: function(e) {
      this._unbindDOM(e)
    },
    _bindDOM: function() {
      var t = this.get(v).get(y),
        n = R._hDocFocus;
      n || (n = R._hDocFocus = t.on("focus", this._onDocFocus, this), n.listeners = {
        count: 0
      }), n.listeners[e.stamp(this, !0)] = !0, n.listeners.count++, I && (this._hDocMouseDown = t.on("mousedown", this._onDocMouseDown, this))
    },
    _unbindDOM: function(t) {
      var n = R._hDocFocus,
        r = e.stamp(this, !0),
        i, s = this._hDocMouseDown;
      n && (i = n.listeners, i[r] && (delete i[r], i.count--), i.count === 0 && (n.detach(), R._hDocFocus = null)), I && s && s.detach()
    },
    _syncUI: function() {
      this._syncAttrUI(this._UI_ATTRS.SYNC)
    },
    _uiSetHeight: function(e) {
      this._uiSetDim(d, e), this._uiSizeCB(e !== _ && e !== b)
    },
    _uiSetWidth: function(e) {
      this._uiSetDim(p, e)
    },
    _uiSetDim: function(e, t) {
      this.get(v).setStyle(e, n.isNumber(t) ? t + this.DEF_UNIT : t)
    },
    _uiSetVisible: function(e) {
      this.get(v).toggleClass(this.getClassName(l), !e)
    },
    _uiSetDisabled: function(e) {
      this.get(v).toggleClass(this.getClassName(c), e)
    },
    _uiSetFocused: function(e, t) {
      var n = this.get(v);
      n.toggleClass(this.getClassName(h), e), t !== B && (e ? n.focus() : n.blur())
    },
    _uiSetTabIndex: function(e) {
      var t = this.get(v);
      n.isNumber(e) ? t.set(S, e) : t.removeAttribute(S)
    },
    _onDocMouseDown: function(e) {
      this._domFocus && this._onDocFocus(e)
    },
    _onDocFocus: function(e) {
      var t = R.getByNode(e.target),
        n = R._active;
      n && n !== t && (n._domFocus = !1, n._set(h, !1, {
        src: B
      }), R._active = null), t && (t._domFocus = !0, t._set(h, !0, {
        src: B
      }), R._active = t)
    },
    toString: function() {
      return this.name + "[" + this.get(x) + "]"
    },
    DEF_UNIT: "px",
    DEF_PARENT_NODE: null,
    CONTENT_TEMPLATE: L,
    BOUNDING_TEMPLATE: L,
    _guid: function() {
      return e.guid()
    },
    _validTabIndex: function(e) {
      return n.isNumber(e) || n.isNull(e)
    },
    _bindAttrUI: function(e) {
      var t, n = e.length;
      for (t = 0; t < n; t++) this.after(e[t] + A, this._setAttrUI)
    },
    _syncAttrUI: function(e) {
      var t, n = e.length,
        r;
      for (t = 0; t < n; t++) r = e[t], this[M + u(r)](this.get(r))
    },
    _setAttrUI: function(e) {
      e.target === this && this[M + u(e.attrName)](e.newVal, e.src)
    },
    _strSetter: function(t) {
      return e.merge(this.get(k), t)
    },
    getString: function(e) {
      return this.get(k)[e]
    },
    getStrings: function() {
      return this.get(k)
    },
    _UI_ATTRS: {
      BIND: F,
      SYNC: F
    }
  }), e.Widget = R
}, "@VERSION@", {
  requires: ["attribute", "base-base", "base-pluginhost", "classnamemanager", "event-focus", "node-base", "node-style"],
  skinnable: !0
});

YUI.add("selector-css2", function(e, t) {
  var n = "parentNode",
    r = "tagName",
    i = "attributes",
    s = "combinator",
    o = "pseudos",
    u = e.Selector,
    a = {
      _reRegExpTokens: /([\^\$\?\[\]\*\+\-\.\(\)\|\\])/,
      SORT_RESULTS: !0,
      _isXML: function() {
        var t = e.config.doc.createElement("div").tagName !== "DIV";
        return t
      }(),
      shorthand: {
        "\\#(-?[_a-z0-9]+[-\\w\\uE000]*)": "[id=$1]",
        "\\.(-?[_a-z]+[-\\w\\uE000]*)": "[className~=$1]"
      },
      operators: {
        "": function(t, n) {
          return e.DOM.getAttribute(t, n) !== ""
        },
        "~=": "(?:^|\\s+){val}(?:\\s+|$)",
        "|=": "^{val}-?"
      },
      pseudos: {
        "first-child": function(t) {
          return e.DOM._children(t[n])[0] === t
        }
      },
      _bruteQuery: function(t, n, r) {
        var i = [],
          s = [],
          o, a = u._tokenize(t),
          f = a[a.length - 1],
          l = e.DOM._getDoc(n),
          c, h, p, d, v;
        if (f) {
          h = f.id, p = f.className, d = f.tagName || "*";
          if (n.getElementsByTagName) h && (n.all || n.nodeType === 9 || e.DOM.inDoc(n)) ? s = e.DOM.allById(h, n) : p ? s = n.getElementsByClassName(p) : s = n.getElementsByTagName(d);
          else {
            o = [], c = n.firstChild, v = d === "*";
            while (c) {
              while (c) c.tagName > "@" && (v || c.tagName === d) && s.push(c), o.push(c), c = c.firstChild;
              while (o.length > 0 && !c) c = o.pop().nextSibling
            }
          }
          s.length && (i = u._filterNodes(s, a, r))
        }
        return i
      },
      _filterNodes: function(t, n, r) {
        var i = 0,
          s, o = n.length,
          a = o - 1,
          f = [],
          l = t[0],
          c = l,
          h = e.Selector.getters,
          p, d, v, m, g, y, b, w;
        for (i = 0; c = l = t[i++];) {
          a = o - 1, m = null;
          e: while (c && c.tagName) {
            v = n[a], b = v.tests, s = b.length;
            if (s && !g)
              while (w = b[--s]) {
                p = w[1], h[w[0]] ? y = h[w[0]](c, w[0]) : (y = c[w[0]], w[0] === "tagName" && !u._isXML && (y = y.toUpperCase()), typeof y != "string" && y !== undefined && y.toString ? y = y.toString() : y === undefined && c.getAttribute && (y = c.getAttribute(w[0], 2)));
                if (p === "=" && y !== w[2] || typeof p != "string" && p.test && !p.test(y) || !p.test && typeof p == "function" && !p(c, w[0], w[2])) {
                  if (c = c[m])
                    while (c && (!c.tagName || v.tagName && v.tagName !== c.tagName)) c = c[m];
                  continue e
                }
              }
            a--;
            if (!!g || !(d = v.combinator)) {
              f.push(l);
              if (r) return f;
              break
            }
            m = d.axis, c = c[m];
            while (c && !c.tagName) c = c[m];
            d.direct && (m = null)
          }
        }
        return l = c = null, f
      },
      combinators: {
        " ": {
          axis: "parentNode"
        },
        ">": {
          axis: "parentNode",
          direct: !0
        },
        "+": {
          axis: "previousSibling",
          direct: !0
        }
      },
      _parsers: [{
        name: i,
        re: /^\uE003(-?[a-z]+[\w\-]*)+([~\|\^\$\*!=]=?)?['"]?([^\uE004'"]*)['"]?\uE004/i,
        fn: function(t, n) {
          var r = t[2] || "",
            i = u.operators,
            s = t[3] ? t[3].replace(/\\/g, "") : "",
            o;
          if (t[1] === "id" && r === "=" || t[1] === "className" && e.config.doc.documentElement.getElementsByClassName && (r === "~=" || r === "=")) n.prefilter = t[1], t[3] = s, n[t[1]] = t[1] === "id" ? t[3] : s;
          r in i && (o = i[r], typeof o == "string" && (t[3] = s.replace(u._reRegExpTokens, "\\$1"), o = new RegExp(o.replace("{val}", t[3]))), t[2] = o);
          if (!n.last || n.prefilter !== t[1]) return t.slice(1)
        }
      }, {
        name: r,
        re: /^((?:-?[_a-z]+[\w-]*)|\*)/i,
        fn: function(e, t) {
          var n = e[1];
          u._isXML || (n = n.toUpperCase()), t.tagName = n;
          if (n !== "*" && (!t.last || t.prefilter)) return [r, "=", n];
          t.prefilter || (t.prefilter = "tagName")
        }
      }, {
        name: s,
        re: /^\s*([>+~]|\s)\s*/,
        fn: function(e, t) {}
      }, {
        name: o,
        re: /^:([\-\w]+)(?:\uE005['"]?([^\uE005]*)['"]?\uE006)*/i,
        fn: function(e, t) {
          var n = u[o][e[1]];
          return n ? (e[2] && (e[2] = e[2].replace(/\\/g, "")), [e[2], n]) : !1
        }
      }],
      _getToken: function(e) {
        return {
          tagName: null,
          id: null,
          className: null,
          attributes: {},
          combinator: null,
          tests: []
        }
      },
      _tokenize: function(t) {
        t = t || "", t = u._parseSelector(e.Lang.trim(t));
        var n = u._getToken(),
          r = t,
          i = [],
          o = !1,
          a, f, l, c;
        e: do {
          o = !1;
          for (l = 0; c = u._parsers[l++];)
            if (a = c.re.exec(t)) {
              c.name !== s && (n.selector = t), t = t.replace(a[0], ""), t.length || (n.last = !0), u._attrFilters[a[1]] && (a[1] = u._attrFilters[a[1]]), f = c.fn(a, n);
              if (f === !1) {
                o = !1;
                break e
              }
              f && n.tests.push(f);
              if (!t.length || c.name === s) i.push(n), n = u._getToken(n), c.name === s && (n.combinator = e.Selector.combinators[a[1]]);
              o = !0
            }
        } while (o && t.length);
        if (!o || t.length) i = [];
        return i
      },
      _replaceMarkers: function(e) {
        return e = e.replace(/\[/g, "\ue003"), e = e.replace(/\]/g, "\ue004"), e = e.replace(/\(/g, "\ue005"), e = e.replace(/\)/g, "\ue006"), e
      },
      _replaceShorthand: function(t) {
        var n = e.Selector.shorthand,
          r;
        for (r in n) n.hasOwnProperty(r) && (t = t.replace(new RegExp(r, "gi"), n[r]));
        return t
      },
      _parseSelector: function(t) {
        var n = e.Selector._replaceSelector(t),
          t = n.selector;
        return t = e.Selector._replaceShorthand(t), t = e.Selector._restore("attr", t, n.attrs), t = e.Selector._restore("pseudo", t, n.pseudos), t = e.Selector._replaceMarkers(t), t = e.Selector._restore("esc", t, n.esc), t
      },
      _attrFilters: {
        "class": "className",
        "for": "htmlFor"
      },
      getters: {
        href: function(t, n) {
          return e.DOM.getAttribute(t, n)
        },
        id: function(t, n) {
          return e.DOM.getId(t)
        }
      }
    };
  e.mix(e.Selector, a, !0), e.Selector.getters.src = e.Selector.getters.rel = e.Selector.getters.href, e.Selector.useNative && e.config.doc.querySelector && (e.Selector.shorthand["\\.(-?[_a-z]+[-\\w]*)"] = "[class~=$1]")
}, "@VERSION@", {
  requires: ["selector-native"]
});

YUI.add("selector-css3", function(e, t) {
  e.Selector._reNth = /^(?:([\-]?\d*)(n){1}|(odd|even)$)*([\-+]?\d*)$/, e.Selector._getNth = function(t, n, r, i) {
    e.Selector._reNth.test(n);
    var s = parseInt(RegExp.$1, 10),
      o = RegExp.$2,
      u = RegExp.$3,
      a = parseInt(RegExp.$4, 10) || 0,
      f = [],
      l = e.DOM._children(t.parentNode, r),
      c;
    u ? (s = 2, c = "+", o = "n", a = u === "odd" ? 1 : 0) : isNaN(s) && (s = o ? 1 : 0);
    if (s === 0) return i && (a = l.length - a + 1), l[a - 1] === t ? !0 : !1;
    s < 0 && (i = !!i, s = Math.abs(s));
    if (!i) {
      for (var h = a - 1, p = l.length; h < p; h += s)
        if (h >= 0 && l[h] === t) return !0
    } else
      for (var h = l.length - a, p = l.length; h >= 0; h -= s)
        if (h < p && l[h] === t) return !0;
    return !1
  }, e.mix(e.Selector.pseudos, {
    root: function(e) {
      return e === e.ownerDocument.documentElement
    },
    "nth-child": function(t, n) {
      return e.Selector._getNth(t, n)
    },
    "nth-last-child": function(t, n) {
      return e.Selector._getNth(t, n, null, !0)
    },
    "nth-of-type": function(t, n) {
      return e.Selector._getNth(t, n, t.tagName)
    },
    "nth-last-of-type": function(t, n) {
      return e.Selector._getNth(t, n, t.tagName, !0)
    },
    "last-child": function(t) {
      var n = e.DOM._children(t.parentNode);
      return n[n.length - 1] === t
    },
    "first-of-type": function(t) {
      return e.DOM._children(t.parentNode, t.tagName)[0] === t
    },
    "last-of-type": function(t) {
      var n = e.DOM._children(t.parentNode, t.tagName);
      return n[n.length - 1] === t
    },
    "only-child": function(t) {
      var n = e.DOM._children(t.parentNode);
      return n.length === 1 && n[0] === t
    },
    "only-of-type": function(t) {
      var n = e.DOM._children(t.parentNode, t.tagName);
      return n.length === 1 && n[0] === t
    },
    empty: function(e) {
      return e.childNodes.length === 0
    },
    not: function(t, n) {
      return !e.Selector.test(t, n)
    },
    contains: function(e, t) {
      var n = e.innerText || e.textContent || "";
      return n.indexOf(t) > -1
    },
    checked: function(e) {
      return e.checked === !0 || e.selected === !0
    },
    enabled: function(e) {
      return e.disabled !== undefined && !e.disabled
    },
    disabled: function(e) {
      return e.disabled
    }
  }), e.mix(e.Selector.operators, {
    "^=": "^{val}",
    "$=": "{val}$",
    "*=": "{val}"
  }), e.Selector.combinators["~"] = {
    axis: "previousSibling"
  }
}, "@VERSION@", {
  requires: ["selector-native", "selector-css2"]
});

YUI.add("widget-htmlparser", function(e, t) {
  var n = e.Widget,
    r = e.Node,
    i = e.Lang,
    s = "srcNode",
    o = "contentBox";
  n.HTML_PARSER = {}, n._buildCfg = {
    aggregates: ["HTML_PARSER"]
  }, n.ATTRS[s] = {
    value: null,
    setter: r.one,
    getter: "_getSrcNode",
    writeOnce: !0
  }, e.mix(n.prototype, {
    _getSrcNode: function(e) {
      return e || this.get(o)
    },
    _preAddAttrs: function(e, t, n) {
      var r = {
        id: e.id,
        boundingBox: e.boundingBox,
        contentBox: e.contentBox,
        srcNode: e.srcNode
      };
      this.addAttrs(r, t, n), delete e.boundingBox, delete e.contentBox, delete e.srcNode, delete e.id, this._applyParser && this._applyParser(t)
    },
    _applyParsedConfig: function(t, n, r) {
      return r ? e.mix(n, r, !1) : n
    },
    _applyParser: function(t) {
      var n = this,
        r = this._getNodeToParse(),
        s = n._getHtmlParser(),
        o, u;
      s && r && e.Object.each(s, function(e, t, s) {
        u = null, i.isFunction(e) ? u = e.call(n, r) : i.isArray(e) ? (u = r.all(e[0]), u.isEmpty() && (u = null)) : u = r.one(e), u !== null && u !== undefined && (o = o || {}, o[t] = u)
      }), t = n._applyParsedConfig(r, t, o)
    },
    _getNodeToParse: function() {
      var e = this.get("srcNode");
      return this._cbFromTemplate ? null : e
    },
    _getHtmlParser: function() {
      var t = this._getClasses(),
        n = {},
        r, i;
      for (r = t.length - 1; r >= 0; r--) i = t[r].HTML_PARSER, i && e.mix(n, i, !0);
      return n
    }
  })
}, "@VERSION@", {
  requires: ["widget-base"]
});

YUI.add("widget-skin", function(e, t) {
  var n = "boundingBox",
    r = "contentBox",
    i = "skin",
    s = e.ClassNameManager.getClassName;
  e.Widget.prototype.getSkinName = function(e) {
    var t = this.get(r) || this.get(n),
      o, u;
    return e = e || s(i, ""), u = new RegExp("\\b" + e + "(\\S+)"), t && t.ancestor(function(e) {
      return o = e.get("className").match(u), o
    }), o ? o[1] : null
  }
}, "@VERSION@", {
  requires: ["widget-base"]
});

YUI.add("widget-uievents", function(e, t) {
  var n = "boundingBox",
    r = e.Widget,
    i = "render",
    s = e.Lang,
    o = ":",
    u = e.Widget._uievts = e.Widget._uievts || {};
  e.mix(r.prototype, {
    _destroyUIEvents: function() {
      var t = e.stamp(this, !0);
      e.each(u, function(n, r) {
        n.instances[t] && (delete n.instances[t], e.Object.isEmpty(n.instances) && (n.handle.detach(), u[r] && delete u[r]))
      })
    },
    UI_EVENTS: e.Node.DOM_EVENTS,
    _getUIEventNode: function() {
      return this.get(n)
    },
    _createUIEvent: function(t) {
      var n = this._getUIEventNode(),
        i = e.stamp(n) + t,
        s = u[i],
        o;
      s || (o = n.delegate(t, function(e) {
        var t = r.getByNode(this);
        t && t._filterUIEvent(e) && t.fire(e.type, {
          domEvent: e
        })
      }, "." + e.Widget.getClassName()), u[i] = s = {
        instances: {},
        handle: o
      }), s.instances[e.stamp(this)] = 1
    },
    _filterUIEvent: function(e) {
      return e.currentTarget.compareTo(e.container) || e.container.compareTo(this._getUIEventNode())
    },
    _getUIEvent: function(e) {
      if (s.isString(e)) {
        var t = this.parseType(e)[1],
          n, r;
        return t && (n = t.indexOf(o), n > -1 && (t = t.substring(n + o.length)), this.UI_EVENTS[t] && (r = t)), r
      }
    },
    _initUIEvent: function(e) {
      var t = this._getUIEvent(e),
        n = this._uiEvtsInitQueue || {};
      t && !n[t] && (this._uiEvtsInitQueue = n[t] = 1, this.after(i, function() {
        this._createUIEvent(t), delete this._uiEvtsInitQueue[t]
      }))
    },
    on: function(e) {
      return this._initUIEvent(e), r.superclass.on.apply(this, arguments)
    },
    publish: function(e, t) {
      var n = this._getUIEvent(e);
      return n && t && t.defaultFn && this._initUIEvent(n), r.superclass.publish.apply(this, arguments)
    }
  }, !0)
}, "@VERSION@", {
  requires: ["node-event-delegate", "widget-base"]
});

YUI.add("json-parse", function(e, t) {
  var n = e.config.global.JSON;
  e.namespace("JSON").parse = function(e, t, r) {
    return n.parse(typeof e == "string" ? e : e + "", t, r)
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

YUI.add("querystring-stringify-simple", function(e, t) {
  var n = e.namespace("QueryString"),
    r = encodeURIComponent;
  n.stringify = function(t, n) {
    var i = [],
      s = n && n.arrayKey ? !0 : !1,
      o, u, a;
    for (o in t)
      if (t.hasOwnProperty(o))
        if (e.Lang.isArray(t[o]))
          for (u = 0, a = t[o].length; u < a; u++) i.push(r(s ? o + "[]" : o) + "=" + r(t[o][u]));
        else i.push(r(o) + "=" + r(t[o]));
    return i.join("&")
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("io-base", function(e, t) {
  function o(t) {
    var n = this;
    n._uid = "io:" + s++, n._init(t), e.io._map[n._uid] = n
  }
  var n = ["start", "complete", "end", "success", "failure", "progress"],
    r = ["status", "statusText", "responseText", "responseXML"],
    i = e.config.win,
    s = 0;
  o.prototype = {
    _id: 0,
    _headers: {
      "X-Requested-With": "XMLHttpRequest"
    },
    _timeout: {},
    _init: function(t) {
      var r = this,
        i, s;
      r.cfg = t || {}, e.augment(r, e.EventTarget);
      for (i = 0, s = n.length; i < s; ++i) r.publish("io:" + n[i], e.merge({
        broadcast: 1
      }, t)), r.publish("io-trn:" + n[i], t)
    },
    _create: function(t, n) {
      var r = this,
        s = {
          id: e.Lang.isNumber(n) ? n : r._id++,
          uid: r._uid
        },
        o = t.xdr ? t.xdr.use : null,
        u = t.form && t.form.upload ? "iframe" : null,
        a;
      return o === "native" && (o = e.UA.ie && !l ? "xdr" : null, r.setHeader("X-Requested-With")), a = o || u, s = a ? e.merge(e.IO.customTransport(a), s) : e.merge(e.IO.defaultTransport(), s), s.notify && (t.notify = function(e, t, n) {
        r.notify(e, t, n)
      }), a || i && i.FormData && t.data instanceof i.FormData && (s.c.upload.onprogress = function(e) {
        r.progress(s, e, t)
      }, s.c.onload = function(e) {
        r.load(s, e, t)
      }, s.c.onerror = function(e) {
        r.error(s, e, t)
      }, s.upload = !0), s
    },
    _destroy: function(t) {
      i && !t.notify && !t.xdr && (u && !t.upload ? t.c.onreadystatechange = null : t.upload ? (t.c.upload.onprogress = null, t.c.onload = null, t.c.onerror = null) : e.UA.ie && !t.e && t.c.abort()), t = t.c = null
    },
    _evt: function(t, r, i) {
      var s = this,
        o, u = i.arguments,
        a = s.cfg.emitFacade,
        f = "io:" + t,
        l = "io-trn:" + t;
      this.detach(l), r.e && (r.c = {
        status: 0,
        statusText: r.e
      }), o = [a ? {
        id: r.id,
        data: r.c,
        cfg: i,
        arguments: u
      } : r.id], a || (t === n[0] || t === n[2] ? u && o.push(u) : (r.evt ? o.push(r.evt) : o.push(r.c), u && o.push(u))), o.unshift(f), s.fire.apply(s, o), i.on && (o[0] = l, s.once(l, i.on[t], i.context || e), s.fire.apply(s, o))
    },
    start: function(e, t) {
      this._evt(n[0], e, t)
    },
    complete: function(e, t) {
      this._evt(n[1], e, t)
    },
    end: function(e, t) {
      this._evt(n[2], e, t), this._destroy(e)
    },
    success: function(e, t) {
      this._evt(n[3], e, t), this.end(e, t)
    },
    failure: function(e, t) {
      this._evt(n[4], e, t), this.end(e, t)
    },
    progress: function(e, t, r) {
      e.evt = t, this._evt(n[5], e, r)
    },
    load: function(e, t, r) {
      e.evt = t.target, this._evt(n[1], e, r)
    },
    error: function(e, t, r) {
      e.evt = t, this._evt(n[4], e, r)
    },
    _retry: function(e, t, n) {
      return this._destroy(e), n.xdr.use = "flash", this.send(t, n, e.id)
    },
    _concat: function(e, t) {
      return e += (e.indexOf("?") === -1 ? "?" : "&") + t, e
    },
    setHeader: function(e, t) {
      t ? this._headers[e] = t : delete this._headers[e]
    },
    _setHeaders: function(t, n) {
      n = e.merge(this._headers, n), e.Object.each(n, function(e, r) {
        e !== "disable" && t.setRequestHeader(r, n[r])
      })
    },
    _startTimeout: function(e, t) {
      var n = this;
      n._timeout[e.id] = setTimeout(function() {
        n._abort(e, "timeout")
      }, t)
    },
    _clearTimeout: function(e) {
      clearTimeout(this._timeout[e]), delete this._timeout[e]
    },
    _result: function(e, t) {
      var n;
      try {
        n = e.c.status
      } catch (r) {
        n = 0
      }
      n >= 200 && n < 300 || n === 304 || n === 1223 ? this.success(e, t) : this.failure(e, t)
    },
    _rS: function(e, t) {
      var n = this;
      e.c.readyState === 4 && (t.timeout && n._clearTimeout(e.id), setTimeout(function() {
        n.complete(e, t), n._result(e, t)
      }, 0))
    },
    _abort: function(e, t) {
      e && e.c && (e.e = t, e.c.abort())
    },
    send: function(t, n, i) {
      var s, o, u, a, f, c, h = this,
        p = t,
        d = {};
      n = n ? e.Object(n) : {}, s = h._create(n, i), o = n.method ? n.method.toUpperCase() : "GET", f = n.sync, c = n.data, e.Lang.isObject(c) && !c.nodeType && !s.upload && e.QueryString && e.QueryString.stringify && (n.data = c = e.QueryString.stringify(c));
      if (n.form) {
        if (n.form.upload) return h.upload(s, t, n);
        c = h._serialize(n.form, c)
      }
      c || (c = "");
      if (c) switch (o) {
        case "GET":
        case "HEAD":
        case "DELETE":
          p = h._concat(p, c), c = "";
          break;
        case "POST":
        case "PUT":
          n.headers = e.merge({
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
          }, n.headers)
      }
      if (s.xdr) return h.xdr(p, s, n);
      if (s.notify) return s.c.send(s, t, n);
      !f && !s.upload && (s.c.onreadystatechange = function() {
        h._rS(s, n)
      });
      try {
        s.c.open(o, p, !f, n.username || null, n.password || null), h._setHeaders(s.c, n.headers || {}), h.start(s, n), n.xdr && n.xdr.credentials && l && (s.c.withCredentials = !0), s.c.send(c);
        if (f) {
          for (u = 0, a = r.length; u < a; ++u) d[r[u]] = s.c[r[u]];
          return d.getAllResponseHeaders = function() {
            return s.c.getAllResponseHeaders()
          }, d.getResponseHeader = function(e) {
            return s.c.getResponseHeader(e)
          }, h.complete(s, n), h._result(s, n), d
        }
      } catch (v) {
        if (s.xdr) return h._retry(s, t, n);
        h.complete(s, n), h._result(s, n)
      }
      return n.timeout && h._startTimeout(s, n.timeout), {
        id: s.id,
        abort: function() {
          return s.c ? h._abort(s, "abort") : !1
        },
        isInProgress: function() {
          return s.c ? s.c.readyState % 4 : !1
        },
        io: h
      }
    }
  }, e.io = function(t, n) {
    var r = e.io._map["io:0"] || new o;
    return r.send.apply(r, [t, n])
  }, e.io.header = function(t, n) {
    var r = e.io._map["io:0"] || new o;
    r.setHeader(t, n)
  }, e.IO = o, e.io._map = {};
  var u = i && i.XMLHttpRequest,
    a = i && i.XDomainRequest,
    f = i && i.ActiveXObject,
    l = u && "withCredentials" in new XMLHttpRequest;
  e.mix(e.IO, {
    _default: "xhr",
    defaultTransport: function(t) {
      if (!t) {
        var n = {
          c: e.IO.transports[e.IO._default](),
          notify: e.IO._default === "xhr" ? !1 : !0
        };
        return n
      }
      e.IO._default = t
    },
    transports: {
      xhr: function() {
        return u ? new XMLHttpRequest : f ? new ActiveXObject("Microsoft.XMLHTTP") : null
      },
      xdr: function() {
        return a ? new XDomainRequest : null
      },
      iframe: function() {
        return {}
      },
      flash: null,
      nodejs: null
    },
    customTransport: function(t) {
      var n = {
        c: e.IO.transports[t]()
      };
      return n[t === "xdr" || t === "flash" ? "xdr" : "notify"] = !0, n
    }
  }), e.mix(e.IO.prototype, {
    notify: function(e, t, n) {
      var r = this;
      switch (e) {
        case "timeout":
        case "abort":
        case "transport error":
          t.c = {
            status: 0,
            statusText: e
          }, e = "failure";
        default:
          r[e].apply(r, [t, n])
      }
    }
  })
}, "@VERSION@", {
  requires: ["event-custom-base", "querystring-stringify-simple"]
});

YUI.add("yui-throttle", function(e, t) {
  /*! Based on work by Simon Willison: http://gist.github.com/292562 */
  ;
  e.throttle = function(t, n) {
    n = n ? n : e.config.throttleTime || 150;
    if (n === -1) return function() {
      t.apply(this, arguments)
    };
    var r = e.Lang.now();
    return function() {
      var i = e.Lang.now();
      i - r > n && (r = i, t.apply(this, arguments))
    }
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("dd-ddm-base", function(e, t) {
  var n = function() {
    n.superclass.constructor.apply(this, arguments)
  };
  n.NAME = "ddm", n.ATTRS = {
    dragCursor: {
      value: "move"
    },
    clickPixelThresh: {
      value: 3
    },
    clickTimeThresh: {
      value: 1e3
    },
    throttleTime: {
      value: -1
    },
    dragMode: {
      value: "point",
      setter: function(e) {
        return this._setDragMode(e), e
      }
    }
  }, e.extend(n, e.Base, {
    _createPG: function() {},
    _active: null,
    _setDragMode: function(t) {
      t === null && (t = e.DD.DDM.get("dragMode"));
      switch (t) {
        case 1:
        case "intersect":
          return 1;
        case 2:
        case "strict":
          return 2;
        case 0:
        case "point":
          return 0
      }
      return 0
    },
    CSS_PREFIX: e.ClassNameManager.getClassName("dd"),
    _activateTargets: function() {},
    _drags: [],
    activeDrag: !1,
    _regDrag: function(e) {
      return this.getDrag(e.get("node")) ? !1 : (this._active || this._setupListeners(), this._drags.push(e), !0)
    },
    _unregDrag: function(t) {
      var n = [];
      e.Array.each(this._drags, function(e) {
        e !== t && (n[n.length] = e)
      }), this._drags = n
    },
    _setupListeners: function() {
      this._createPG(), this._active = !0;
      var t = e.one(e.config.doc);
      t.on("mousemove", e.throttle(e.bind(this._docMove, this), this.get("throttleTime"))), t.on("mouseup", e.bind(this._end, this))
    },
    _start: function() {
      this.fire("ddm:start"), this._startDrag()
    },
    _startDrag: function() {},
    _endDrag: function() {},
    _dropMove: function() {},
    _end: function() {
      this.activeDrag && (this._shimming = !1, this._endDrag(), this.fire("ddm:end"), this.activeDrag.end.call(this.activeDrag), this.activeDrag = null)
    },
    stopDrag: function() {
      return this.activeDrag && this._end(), this
    },
    _shimming: !1,
    _docMove: function(e) {
      this._shimming || this._move(e)
    },
    _move: function(e) {
      this.activeDrag && (this.activeDrag._move.call(this.activeDrag, e), this._dropMove())
    },
    cssSizestoObject: function(e) {
      var t = e.split(" ");
      switch (t.length) {
        case 1:
          t[1] = t[2] = t[3] = t[0];
          break;
        case 2:
          t[2] = t[0], t[3] = t[1];
          break;
        case 3:
          t[3] = t[1]
      }
      return {
        top: parseInt(t[0], 10),
        right: parseInt(t[1], 10),
        bottom: parseInt(t[2], 10),
        left: parseInt(t[3], 10)
      }
    },
    getDrag: function(t) {
      var n = !1,
        r = e.one(t);
      return r instanceof e.Node && e.Array.each(this._drags, function(e) {
        r.compareTo(e.get("node")) && (n = e)
      }), n
    },
    swapPosition: function(t, n) {
      t = e.DD.DDM.getNode(t), n = e.DD.DDM.getNode(n);
      var r = t.getXY(),
        i = n.getXY();
      return t.setXY(i), n.setXY(r), t
    },
    getNode: function(t) {
      return t instanceof e.Node ? t : (t && t.get ? e.Widget && t instanceof e.Widget ? t = t.get("boundingBox") : t = t.get("node") : t = e.one(t), t)
    },
    swapNode: function(t, n) {
      t = e.DD.DDM.getNode(t), n = e.DD.DDM.getNode(n);
      var r = n.get("parentNode"),
        i = n.get("nextSibling");
      return i === t ? r.insertBefore(t, n) : n === t.get("nextSibling") ? r.insertBefore(n, t) : (t.get("parentNode").replaceChild(n, t), r.insertBefore(t, i)), t
    }
  }), e.namespace("DD"), e.DD.DDM = new n
}, "@VERSION@", {
  requires: ["node", "base", "yui-throttle", "classnamemanager"]
});

YUI.add("dd-ddm", function(e, t) {
  e.mix(e.DD.DDM, {
    _pg: null,
    _debugShim: !1,
    _activateTargets: function() {},
    _deactivateTargets: function() {},
    _startDrag: function() {
      this.activeDrag && this.activeDrag.get("useShim") && (this._shimming = !0, this._pg_activate(), this._activateTargets())
    },
    _endDrag: function() {
      this._pg_deactivate(), this._deactivateTargets()
    },
    _pg_deactivate: function() {
      this._pg.setStyle("display", "none")
    },
    _pg_activate: function() {
      this._pg || this._createPG();
      var e = this.activeDrag.get("activeHandle"),
        t = "auto";
      e && (t = e.getStyle("cursor")), t === "auto" && (t = this.get("dragCursor")), this._pg_size(), this._pg.setStyles({
        top: 0,
        left: 0,
        display: "block",
        opacity: this._debugShim ? ".5" : "0",
        cursor: t
      })
    },
    _pg_size: function() {
      if (this.activeDrag) {
        var t = e.one("body"),
          n = t.get("docHeight"),
          r = t.get("docWidth");
        this._pg.setStyles({
          height: n + "px",
          width: r + "px"
        })
      }
    },
    _createPG: function() {
      var t = e.Node.create("<div></div>"),
        n = e.one("body"),
        r;
      t.setStyles({
        top: "0",
        left: "0",
        position: "absolute",
        zIndex: "9999",
        overflow: "hidden",
        backgroundColor: "red",
        display: "none",
        height: "5px",
        width: "5px"
      }), t.set("id", e.stamp(t)), t.addClass(e.DD.DDM.CSS_PREFIX + "-shim"), n.prepend(t), this._pg = t, this._pg.on("mousemove", e.throttle(e.bind(this._move, this), this.get("throttleTime"))), this._pg.on("mouseup", e.bind(this._end, this)), r = e.one("win"), e.on("window:resize", e.bind(this._pg_size, this)), r.on("scroll", e.bind(this._pg_size, this))
    }
  }, !0)
}, "@VERSION@", {
  requires: ["dd-ddm-base", "event-resize"]
});

YUI.add("dd-ddm-drop", function(e, t) {
  e.mix(e.DD.DDM, {
    _noShim: !1,
    _activeShims: [],
    _hasActiveShim: function() {
      return this._noShim ? !0 : this._activeShims.length
    },
    _addActiveShim: function(e) {
      this._activeShims.push(e)
    },
    _removeActiveShim: function(t) {
      var n = [];
      e.Array.each(this._activeShims, function(e) {
        e._yuid !== t._yuid && n.push(e)
      }), this._activeShims = n
    },
    syncActiveShims: function(t) {
      e.later(0, this, function(t) {
        var n = t ? this.targets : this._lookup();
        e.Array.each(n, function(e) {
          e.sizeShim.call(e)
        }, this)
      }, t)
    },
    mode: 0,
    POINT: 0,
    INTERSECT: 1,
    STRICT: 2,
    useHash: !0,
    activeDrop: null,
    validDrops: [],
    otherDrops: {},
    targets: [],
    _addValid: function(e) {
      return this.validDrops.push(e), this
    },
    _removeValid: function(t) {
      var n = [];
      return e.Array.each(this.validDrops, function(e) {
        e !== t && n.push(e)
      }), this.validDrops = n, this
    },
    isOverTarget: function(e) {
      if (this.activeDrag && e) {
        var t = this.activeDrag.mouseXY,
          n, r = this.activeDrag.get("dragMode"),
          i, s = e.shim;
        if (t && this.activeDrag) {
          i = this.activeDrag.region;
          if (r === this.STRICT) return this.activeDrag.get("dragNode").inRegion(e.region, !0, i);
          if (e && e.shim) return r === this.INTERSECT && this._noShim ? (n = i || this.activeDrag.get("node"), e.get("node").intersect(n, e.region).inRegion) : (this._noShim && (s = e.get("node")), s.intersect({
            top: t[1],
            bottom: t[1],
            left: t[0],
            right: t[0]
          }, e.region).inRegion)
        }
      }
      return !1
    },
    clearCache: function() {
      this.validDrops = [], this.otherDrops = {}, this._activeShims = []
    },
    _activateTargets: function() {
      this._noShim = !0, this.clearCache(), e.Array.each(this.targets, function(e) {
        e._activateShim([]), e.get("noShim") === !0 && (this._noShim = !1)
      }, this), this._handleTargetOver()
    },
    getBestMatch: function(t, n) {
      var r = null,
        i = 0,
        s;
      return e.Object.each(t, function(e) {
        var t = this.activeDrag.get("dragNode").intersect(e.get("node"));
        e.region.area = t.area, t.inRegion && t.area > i && (i = t.area, r = e)
      }, this), n ? (s = [], e.Object.each(t, function(e) {
        e !== r && s.push(e)
      }, this), [r, s]) : r
    },
    _deactivateTargets: function() {
      var t = [],
        n, r = this.activeDrag,
        i = this.activeDrop;
      r && i && this.otherDrops[i] ? (r.get("dragMode") ? (n = this.getBestMatch(this.otherDrops, !0), i = n[0], t = n[1]) : (t = this.otherDrops, delete t[i]), r.get("node").removeClass(this.CSS_PREFIX + "-drag-over"), i && (i.fire("drop:hit", {
        drag: r,
        drop: i,
        others: t
      }), r.fire("drag:drophit", {
        drag: r,
        drop: i,
        others: t
      }))) : r && r.get("dragging") && (r.get("node").removeClass(this.CSS_PREFIX + "-drag-over"), r.fire("drag:dropmiss", {
        pageX: r.lastXY[0],
        pageY: r.lastXY[1]
      })), this.activeDrop = null, e.Array.each(this.targets, function(e) {
        e._deactivateShim([])
      }, this)
    },
    _dropMove: function() {
      this._hasActiveShim() ? this._handleTargetOver() : e.Object.each(this.otherDrops, function(e) {
        e._handleOut.apply(e, [])
      })
    },
    _lookup: function() {
      if (!this.useHash || this._noShim) return this.validDrops;
      var t = [];
      return e.Array.each(this.validDrops, function(e) {
        e.shim && e.shim.inViewportRegion(!1, e.region) && t.push(e)
      }), t
    },
    _handleTargetOver: function() {
      var t = this._lookup();
      e.Array.each(t, function(e) {
        e._handleTargetOver.call(e)
      }, this)
    },
    _regTarget: function(e) {
      this.targets.push(e)
    },
    _unregTarget: function(t) {
      var n = [],
        r;
      e.Array.each(this.targets, function(e) {
        e !== t && n.push(e)
      }, this), this.targets = n, r = [], e.Array.each(this.validDrops, function(e) {
        e !== t && r.push(e)
      }), this.validDrops = r
    },
    getDrop: function(t) {
      var n = !1,
        r = e.one(t);
      return r instanceof e.Node && e.Array.each(this.targets, function(e) {
        r.compareTo(e.get("node")) && (n = e)
      }), n
    }
  }, !0)
}, "@VERSION@", {
  requires: ["dd-ddm"]
});

YUI.add("dd-drag", function(e, t) {
  var n = e.DD.DDM,
    r = "node",
    i = "dragging",
    s = "dragNode",
    o = "offsetHeight",
    u = "offsetWidth",
    a = "drag:mouseDown",
    f = "drag:afterMouseDown",
    l = "drag:removeHandle",
    c = "drag:addHandle",
    h = "drag:removeInvalid",
    p = "drag:addInvalid",
    d = "drag:start",
    v = "drag:end",
    m = "drag:drag",
    g = "drag:align",
    y = function(t) {
      this._lazyAddAttrs = !1, y.superclass.constructor.apply(this, arguments);
      var r = n._regDrag(this);
      r || e.error("Failed to register node, already in use: " + t.node)
    };
  y.NAME = "drag", y.START_EVENT = "mousedown", y.ATTRS = {
    node: {
      setter: function(t) {
        if (this._canDrag(t)) return t;
        var n = e.one(t);
        return n || e.error("DD.Drag: Invalid Node Given: " + t), n
      }
    },
    dragNode: {
      setter: function(t) {
        if (this._canDrag(t)) return t;
        var n = e.one(t);
        return n || e.error("DD.Drag: Invalid dragNode Given: " + t), n
      }
    },
    offsetNode: {
      value: !0
    },
    startCentered: {
      value: !1
    },
    clickPixelThresh: {
      value: n.get("clickPixelThresh")
    },
    clickTimeThresh: {
      value: n.get("clickTimeThresh")
    },
    lock: {
      value: !1,
      setter: function(e) {
        return e ? this.get(r).addClass(n.CSS_PREFIX + "-locked") : this.get(r).removeClass(n.CSS_PREFIX + "-locked"), e
      }
    },
    data: {
      value: !1
    },
    move: {
      value: !0
    },
    useShim: {
      value: !0
    },
    activeHandle: {
      value: !1
    },
    primaryButtonOnly: {
      value: !0
    },
    dragging: {
      value: !1
    },
    parent: {
      value: !1
    },
    target: {
      value: !1,
      setter: function(e) {
        return this._handleTarget(e), e
      }
    },
    dragMode: {
      value: null,
      setter: function(e) {
        return n._setDragMode(e)
      }
    },
    groups: {
      value: ["default"],
      getter: function() {
        return this._groups ? e.Object.keys(this._groups) : (this._groups = {}, [])
      },
      setter: function(t) {
        return this._groups = e.Array.hash(t), t
      }
    },
    handles: {
      value: null,
      setter: function(t) {
        return t ? (this._handles = {}, e.Array.each(t, function(t) {
          var n = t;
          if (t instanceof e.Node || t instanceof e.NodeList) n = t._yuid;
          this._handles[n] = t
        }, this)) : this._handles = null, t
      }
    },
    bubbles: {
      setter: function(e) {
        return this.addTarget(e), e
      }
    },
    haltDown: {
      value: !0
    }
  }, e.extend(y, e.Base, {
    _canDrag: function(e) {
      return e && e.setXY && e.getXY && e.test && e.contains ? !0 : !1
    },
    _bubbleTargets: e.DD.DDM,
    addToGroup: function(e) {
      return this._groups[e] = !0, n._activateTargets(), this
    },
    removeFromGroup: function(e) {
      return delete this._groups[e], n._activateTargets(), this
    },
    target: null,
    _handleTarget: function(t) {
      e.DD.Drop && (t === !1 ? this.target && (n._unregTarget(this.target), this.target = null) : (e.Lang.isObject(t) || (t = {}), t.bubbleTargets = t.bubbleTargets || this.getTargets(), t.node = this.get(r), t.groups = t.groups || this.get("groups"), this.target = new e.DD.Drop(t)))
    },
    _groups: null,
    _createEvents: function() {
      this.publish(a, {
        defaultFn: this._defMouseDownFn,
        queuable: !1,
        emitFacade: !0,
        bubbles: !0,
        prefix: "drag"
      }), this.publish(g, {
        defaultFn: this._defAlignFn,
        queuable: !1,
        emitFacade: !0,
        bubbles: !0,
        prefix: "drag"
      }), this.publish(m, {
        defaultFn: this._defDragFn,
        queuable: !1,
        emitFacade: !0,
        bubbles: !0,
        prefix: "drag"
      }), this.publish(v, {
        defaultFn: this._defEndFn,
        preventedFn: this._prevEndFn,
        queuable: !1,
        emitFacade: !0,
        bubbles: !0,
        prefix: "drag"
      });
      var t = [f, l, c, h, p, d, "drag:drophit", "drag:dropmiss", "drag:over", "drag:enter", "drag:exit"];
      e.Array.each(t, function(e) {
        this.publish(e, {
          type: e,
          emitFacade: !0,
          bubbles: !0,
          preventable: !1,
          queuable: !1,
          prefix: "drag"
        })
      }, this)
    },
    _ev_md: null,
    _startTime: null,
    _endTime: null,
    _handles: null,
    _invalids: null,
    _invalidsDefault: {
      textarea: !0,
      input: !0,
      a: !0,
      button: !0,
      select: !0
    },
    _dragThreshMet: null,
    _fromTimeout: null,
    _clickTimeout: null,
    deltaXY: null,
    startXY: null,
    nodeXY: null,
    lastXY: null,
    actXY: null,
    realXY: null,
    mouseXY: null,
    region: null,
    _handleMouseUp: function() {
      this.fire("drag:mouseup"), this._fixIEMouseUp(), n.activeDrag && n._end()
    },
    _fixDragStart: function(e) {
      this.validClick(e) && e.preventDefault()
    },
    _ieSelectFix: function() {
      return !1
    },
    _ieSelectBack: null,
    _fixIEMouseDown: function() {
      e.UA.ie && (this._ieSelectBack = e.config.doc.body.onselectstart, e.config.doc.body.onselectstart = this._ieSelectFix)
    },
    _fixIEMouseUp: function() {
      e.UA.ie && (e.config.doc.body.onselectstart = this._ieSelectBack)
    },
    _handleMouseDownEvent: function(e) {
      this.validClick(e) && e.preventDefault(), this.fire(a, {
        ev: e
      })
    },
    _defMouseDownFn: function(t) {
      var r = t.ev;
      this._dragThreshMet = !1, this._ev_md = r;
      if (this.get("primaryButtonOnly") && r.button > 1) return !1;
      this.validClick(r) && (this._fixIEMouseDown(r), y.START_EVENT.indexOf("gesture") !== 0 && (this.get("haltDown") ? r.halt() : r.preventDefault()), this._setStartPosition([r.pageX, r.pageY]), n.activeDrag = this, this._clickTimeout = e.later(this.get("clickTimeThresh"), this, this._timeoutCheck)), this.fire(f, {
        ev: r
      })
    },
    validClick: function(t) {
      var n = !1,
        i = !1,
        s = t.target,
        o = null,
        u = null,
        a = null,
        f = !1;
      if (this._handles) e.Object.each(this._handles, function(t, r) {
        t instanceof e.Node || t instanceof e.NodeList ? n || (a = t, a instanceof e.Node && (a = new e.NodeList(t._node)), a.each(function(e) {
          e.contains(s) && (n = !0)
        })) : e.Lang.isString(r) && s.test(r + ", " + r + " *") && !o && (o = r, n = !0)
      });
      else {
        i = this.get(r);
        if (i.contains(s) || i.compareTo(s)) n = !0
      }
      return n && this._invalids && e.Object.each(this._invalids, function(t, r) {
        e.Lang.isString(r) && s.test(r + ", " + r + " *") && (n = !1)
      }), n && (o ? (u = t.currentTarget.all(o), f = !1, u.each(function(e) {
        (e.contains(s) || e.compareTo(s)) && !f && (f = !0, this.set("activeHandle", e))
      }, this)) : this.set("activeHandle", this.get(r))), n
    },
    _setStartPosition: function(e) {
      this.startXY = e, this.nodeXY = this.lastXY = this.realXY = this.get(r).getXY(), this.get("offsetNode") ? this.deltaXY = [this.startXY[0] - this.nodeXY[0], this.startXY[1] - this.nodeXY[1]] : this.deltaXY = [0, 0]
    },
    _timeoutCheck: function() {
      !this.get("lock") && !this._dragThreshMet && this._ev_md && (this._fromTimeout = this._dragThreshMet = !0, this.start(), this._alignNode([this._ev_md.pageX, this._ev_md.pageY], !0))
    },
    removeHandle: function(t) {
      var n = t;
      if (t instanceof e.Node || t instanceof e.NodeList) n = t._yuid;
      return this._handles[n] && (delete this._handles[n], this.fire(l, {
        handle: t
      })), this
    },
    addHandle: function(t) {
      this._handles || (this._handles = {});
      var n = t;
      if (t instanceof e.Node || t instanceof e.NodeList) n = t._yuid;
      return this._handles[n] = t, this.fire(c, {
        handle: t
      }), this
    },
    removeInvalid: function(e) {
      return this._invalids[e] && (this._invalids[e] = null, delete this._invalids[e], this.fire(h, {
        handle: e
      })), this
    },
    addInvalid: function(t) {
      return e.Lang.isString(t) && (this._invalids[t] = !0, this.fire(p, {
        handle: t
      })), this
    },
    initializer: function() {
      this.get(r).dd = this;
      if (!this.get(r).get("id")) {
        var t = e.stamp(this.get(r));
        this.get(r).set("id", t)
      }
      this.actXY = [], this._invalids = e.clone(this._invalidsDefault, !0), this._createEvents(), this.get(s) || this.set(s, this.get(r)), this.on("initializedChange", e.bind(this._prep, this)), this.set("groups", this.get("groups"))
    },
    _prep: function() {
      this._dragThreshMet = !1;
      var t = this.get(r);
      t.addClass(n.CSS_PREFIX + "-draggable"), t.on(y.START_EVENT, e.bind(this._handleMouseDownEvent, this)), t.on("mouseup", e.bind(this._handleMouseUp, this)), t.on("dragstart", e.bind(this._fixDragStart, this))
    },
    _unprep: function() {
      var e = this.get(r);
      e.removeClass(n.CSS_PREFIX + "-draggable"), e.detachAll("mouseup"), e.detachAll("dragstart"), e.detachAll(y.START_EVENT), this.mouseXY = [], this.deltaXY = [0, 0], this.startXY = [], this.nodeXY = [], this.lastXY = [], this.actXY = [], this.realXY = []
    },
    start: function() {
      if (!this.get("lock") && !this.get(i)) {
        var e = this.get(r),
          t, a, f;
        this._startTime = (new Date).getTime(), n._start(), e.addClass(n.CSS_PREFIX + "-dragging"), this.fire(d, {
          pageX: this.nodeXY[0],
          pageY: this.nodeXY[1],
          startTime: this._startTime
        }), e = this.get(s), f = this.nodeXY, t = e.get(u), a = e.get(o), this.get("startCentered") && this._setStartPosition([f[0] + t / 2, f[1] + a / 2]), this.region = {
          0: f[0],
          1: f[1],
          area: 0,
          top: f[1],
          right: f[0] + t,
          bottom: f[1] + a,
          left: f[0]
        }, this.set(i, !0)
      }
      return this
    },
    end: function() {
      return this._endTime = (new Date).getTime(), this._clickTimeout && this._clickTimeout.cancel(), this._dragThreshMet = this._fromTimeout = !1, !this.get("lock") && this.get(i) && this.fire(v, {
        pageX: this.lastXY[0],
        pageY: this.lastXY[1],
        startTime: this._startTime,
        endTime: this._endTime
      }), this.get(r).removeClass(n.CSS_PREFIX + "-dragging"), this.set(i, !1), this.deltaXY = [0, 0], this
    },
    _defEndFn: function() {
      this._fixIEMouseUp(), this._ev_md = null
    },
    _prevEndFn: function() {
      this._fixIEMouseUp(), this.get(s).setXY(this.nodeXY), this._ev_md = null, this.region = null
    },
    _align: function(e) {
      this.fire(g, {
        pageX: e[0],
        pageY: e[1]
      })
    },
    _defAlignFn: function(e) {
      this.actXY = [e.pageX - this.deltaXY[0], e.pageY - this.deltaXY[1]]
    },
    _alignNode: function(e, t) {
      this._align(e), t || this._moveNode()
    },
    _moveNode: function(e) {
      var t = [],
        n = [],
        r = this.nodeXY,
        i = this.actXY;
      t[0] = i[0] - this.lastXY[0], t[1] = i[1] - this.lastXY[1], n[0] = i[0] - this.nodeXY[0], n[1] = i[1] - this.nodeXY[1], this.region = {
        0: i[0],
        1: i[1],
        area: 0,
        top: i[1],
        right: i[0] + this.get(s).get(u),
        bottom: i[1] + this.get(s).get(o),
        left: i[0]
      }, this.fire(m, {
        pageX: i[0],
        pageY: i[1],
        scroll: e,
        info: {
          start: r,
          xy: i,
          delta: t,
          offset: n
        }
      }), this.lastXY = i
    },
    _defDragFn: function(t) {
      if (this.get("move")) {
        if (t.scroll && t.scroll.node) {
          var n = t.scroll.node.getDOMNode();
          n === e.config.win ? n.scrollTo(t.scroll.left, t.scroll.top) : (t.scroll.node.set("scrollTop", t.scroll.top), t.scroll.node.set("scrollLeft", t.scroll.left))
        }
        this.get(s).setXY([t.pageX, t.pageY]), this.realXY = [t.pageX, t.pageY]
      }
    },
    _move: function(e) {
      if (this.get("lock")) return !1;
      this.mouseXY = [e.pageX, e.pageY];
      if (!this._dragThreshMet) {
        var t = Math.abs(this.startXY[0] - e.pageX),
          n = Math.abs(this.startXY[1] - e.pageY);
        if (t > this.get("clickPixelThresh") || n > this.get("clickPixelThresh")) this._dragThreshMet = !0, this.start(), e && e.preventDefault && e.preventDefault(), this._alignNode([e.pageX, e.pageY])
      } else this._clickTimeout && this._clickTimeout.cancel(), this._alignNode([e.pageX, e.pageY])
    },
    stopDrag: function() {
      return this.get(i) && n._end(), this
    },
    destructor: function() {
      this._unprep(), this.target && this.target.destroy(), n._unregDrag(this)
    }
  }), e.namespace("DD"), e.DD.Drag = y
}, "@VERSION@", {
  requires: ["dd-ddm-base"]
});

YUI.add("dd-proxy", function(e, t) {
  var n = e.DD.DDM,
    r = "node",
    i = "dragNode",
    s = "host",
    o = !0,
    u, a = function() {
      a.superclass.constructor.apply(this, arguments)
    };
  a.NAME = "DDProxy", a.NS = "proxy", a.ATTRS = {
    host: {},
    moveOnEnd: {
      value: o
    },
    hideOnEnd: {
      value: o
    },
    resizeFrame: {
      value: o
    },
    positionProxy: {
      value: o
    },
    borderStyle: {
      value: "1px solid #808080"
    },
    cloneNode: {
      value: !1
    }
  }, u = {
    _hands: null,
    _init: function() {
      if (!n._proxy) {
        n._createFrame(), e.on("domready", e.bind(this._init, this));
        return
      }
      this._hands || (this._hands = []);
      var t, o, u = this.get(s),
        a = u.get(i);
      a.compareTo(u.get(r)) && n._proxy && u.set(i, n._proxy), e.Array.each(this._hands, function(e) {
        e.detach()
      }), t = n.on("ddm:start", e.bind(function() {
        n.activeDrag === u && n._setFrame(u)
      }, this)), o = n.on("ddm:end", e.bind(function() {
        u.get("dragging") && (this.get("moveOnEnd") && u.get(r).setXY(u.lastXY), this.get("hideOnEnd") && u.get(i).setStyle("display", "none"), this.get("cloneNode") && (u.get(i).remove(), u.set(i, n._proxy)))
      }, this)), this._hands = [t, o]
    },
    initializer: function() {
      this._init()
    },
    destructor: function() {
      var t = this.get(s);
      e.Array.each(this._hands, function(e) {
        e.detach()
      }), t.set(i, t.get(r))
    },
    clone: function() {
      var t = this.get(s),
        n = t.get(r),
        o = n.cloneNode(!0);
      return o.all('input[type="radio"]').removeAttribute("name"), delete o._yuid, o.setAttribute("id", e.guid()), o.setStyle("position", "absolute"), n.get("parentNode").appendChild(o), t.set(i, o), o
    }
  }, e.namespace("Plugin"), e.extend(a, e.Base, u), e.Plugin.DDProxy = a, e.mix(n, {
    _createFrame: function() {
      if (!n._proxy) {
        n._proxy = o;
        var t = e.Node.create("<div></div>"),
          r = e.one("body");
        t.setStyles({
          position: "absolute",
          display: "none",
          zIndex: "999",
          top: "-999px",
          left: "-999px"
        }), r.prepend(t), t.set("id", e.guid()), t.addClass(n.CSS_PREFIX + "-proxy"), n._proxy = t
      }
    },
    _setFrame: function(e) {
      var t = e.get(r),
        s = e.get(i),
        o, u = "auto";
      o = n.activeDrag.get("activeHandle"), o && (u = o.getStyle("cursor")), u === "auto" && (u = n.get("dragCursor")), s.setStyles({
        visibility: "hidden",
        display: "block",
        cursor: u,
        border: e.proxy.get("borderStyle")
      }), e.proxy.get("cloneNode") && (s = e.proxy.clone()), e.proxy.get("resizeFrame") && s.setStyles({
        height: t.get("offsetHeight") + "px",
        width: t.get("offsetWidth") + "px"
      }), e.proxy.get("positionProxy") && s.setXY(e.nodeXY), s.setStyle("visibility", "visible")
    }
  })
}, "@VERSION@", {
  requires: ["dd-drag"]
});

YUI.add("dd-constrain", function(e, t) {
  var n = "dragNode",
    r = "offsetHeight",
    i = "offsetWidth",
    s = "host",
    o = "tickXArray",
    u = "tickYArray",
    a = e.DD.DDM,
    f = "top",
    l = "right",
    c = "bottom",
    h = "left",
    p = "view",
    d = null,
    v = "drag:tickAlignX",
    m = "drag:tickAlignY",
    g = function() {
      this._lazyAddAttrs = !1, g.superclass.constructor.apply(this, arguments)
    };
  g.NAME = "ddConstrained", g.NS = "con", g.ATTRS = {
    host: {},
    stickX: {
      value: !1
    },
    stickY: {
      value: !1
    },
    tickX: {
      value: !1
    },
    tickY: {
      value: !1
    },
    tickXArray: {
      value: !1
    },
    tickYArray: {
      value: !1
    },
    gutter: {
      value: "0",
      setter: function(t) {
        return e.DD.DDM.cssSizestoObject(t)
      }
    },
    constrain: {
      value: p,
      setter: function(t) {
        var n = e.one(t);
        return n && (t = n), t
      }
    },
    constrain2region: {
      setter: function(e) {
        return this.set("constrain", e)
      }
    },
    constrain2node: {
      setter: function(t) {
        return this.set("constrain", e.one(t))
      }
    },
    constrain2view: {
      setter: function() {
        return this.set("constrain", p)
      }
    },
    cacheRegion: {
      value: !0
    }
  }, d = {
    _lastTickXFired: null,
    _lastTickYFired: null,
    initializer: function() {
      this._createEvents(), this._eventHandles = [this.get(s).on("drag:end", e.bind(this._handleEnd, this)), this.get(s).on("drag:start", e.bind(this._handleStart, this)), this.get(s).after("drag:align", e.bind(this.align, this)), this.get(s).after("drag:drag", e.bind(this.drag, this))]
    },
    destructor: function() {
      e.Array.each(this._eventHandles, function(e) {
        e.detach()
      }), this._eventHandles.length = 0
    },
    _createEvents: function() {
      var t = [v, m];
      e.Array.each(t, function(e) {
        this.publish(e, {
          type: e,
          emitFacade: !0,
          bubbles: !0,
          queuable: !1,
          prefix: "drag"
        })
      }, this)
    },
    _handleEnd: function() {
      this._lastTickYFired = null, this._lastTickXFired = null
    },
    _handleStart: function() {
      this.resetCache()
    },
    _regionCache: null,
    _cacheRegion: function() {
      this._regionCache = this.get("constrain").get("region")
    },
    resetCache: function() {
      this._regionCache = null
    },
    _getConstraint: function() {
      var t = this.get("constrain"),
        r = this.get("gutter"),
        i;
      t && (t instanceof e.Node ? (this._regionCache || (this._eventHandles.push(e.on("resize", e.bind(this._cacheRegion, this), e.config.win)), this._cacheRegion()), i = e.clone(this._regionCache), this.get("cacheRegion") || this.resetCache()) : e.Lang.isObject(t) && (i = e.clone(t)));
      if (!t || !i) t = p;
      return t === p && (i = this.get(s).get(n).get("viewportRegion")), e.Object.each(r, function(e, t) {
        t === l || t === c ? i[t] -= e : i[t] += e
      }), i
    },
    getRegion: function(e) {
      var t = {},
        o = null,
        u = null,
        a = this.get(s);
      return t = this._getConstraint(), e && (o = a.get(n).get(r), u = a.get(n).get(i), t[l] = t[l] - u, t[c] = t[c] - o), t
    },
    _checkRegion: function(e) {
      var t = e,
        o = this.getRegion(),
        u = this.get(s),
        a = u.get(n).get(r),
        p = u.get(n).get(i);
      return t[1] > o[c] - a && (e[1] = o[c] - a), o[f] > t[1] && (e[1] = o[f]), t[0] > o[l] - p && (e[0] = o[l] - p), o[h] > t[0] && (e[0] = o[h]), e
    },
    inRegion: function(e) {
      e = e || this.get(s).get(n).getXY();
      var t = this._checkRegion([e[0], e[1]]),
        r = !1;
      return e[0] === t[0] && e[1] === t[1] && (r = !0), r
    },
    align: function() {
      var e = this.get(s),
        t = [e.actXY[0], e.actXY[1]],
        n = this.getRegion(!0);
      this.get("stickX") && (t[1] = e.startXY[1] - e.deltaXY[1]), this.get("stickY") && (t[0] = e.startXY[0] - e.deltaXY[0]), n && (t = this._checkRegion(t)), t = this._checkTicks(t, n), e.actXY = t
    },
    drag: function() {
      var t = this.get(s),
        n = this.get("tickX"),
        r = this.get("tickY"),
        i = [t.actXY[0], t.actXY[1]];
      (e.Lang.isNumber(n) || this.get(o)) && this._lastTickXFired !== i[0] && (this._tickAlignX(), this._lastTickXFired = i[0]), (e.Lang.isNumber(r) || this.get(u)) && this._lastTickYFired !== i[1] && (this._tickAlignY(), this._lastTickYFired = i[1])
    },
    _checkTicks: function(e, t) {
      var n = this.get(s),
        r = n.startXY[0] - n.deltaXY[0],
        i = n.startXY[1] - n.deltaXY[1],
        p = this.get("tickX"),
        d = this.get("tickY");
      return p && !this.get(o) && (e[0] = a._calcTicks(e[0], r, p, t[h], t[l])), d && !this.get(u) && (e[1] = a._calcTicks(e[1], i, d, t[f], t[c])), this.get(o) && (e[0] = a._calcTickArray(e[0], this.get(o), t[h], t[l])), this.get(u) && (e[1] = a._calcTickArray(e[1], this.get(u), t[f], t[c])), e
    },
    _tickAlignX: function() {
      this.fire(v)
    },
    _tickAlignY: function() {
      this.fire(m)
    }
  }, e.namespace("Plugin"), e.extend(g, e.Base, d), e.Plugin.DDConstrained = g, e.mix(a, {
    _calcTicks: function(e, t, n, r, i) {
      var s = (e - t) / n,
        o = Math.floor(s),
        u = Math.ceil(s);
      return (o !== 0 || u !== 0) && s >= o && s <= u && (e = t + n * o, r && i && (e < r && (e = t + n * (o + 1)), e > i && (e = t + n * (o - 1)))), e
    },
    _calcTickArray: function(e, t, n, r) {
      var i = 0,
        s = t.length,
        o = 0,
        u, a, f;
      if (!t || t.length === 0) return e;
      if (t[0] >= e) return t[0];
      for (i = 0; i < s; i++) {
        o = i + 1;
        if (t[o] && t[o] >= e) return u = e - t[i], a = t[o] - e, f = a > u ? t[i] : t[o], n && r && f > r && (t[i] ? f = t[i] : f = t[s - 1]), f
      }
      return t[t.length - 1]
    }
  })
}, "@VERSION@", {
  requires: ["dd-drag"]
});

YUI.add("dd-drop", function(e, t) {
  var n = "node",
    r = e.DD.DDM,
    i = "offsetHeight",
    s = "offsetWidth",
    o = "drop:over",
    u = "drop:enter",
    a = "drop:exit",
    f = function() {
      this._lazyAddAttrs = !1, f.superclass.constructor.apply(this, arguments), e.on("domready", e.bind(function() {
        e.later(100, this, this._createShim)
      }, this)), r._regTarget(this)
    };
  f.NAME = "drop", f.ATTRS = {
    node: {
      setter: function(t) {
        var n = e.one(t);
        return n || e.error("DD.Drop: Invalid Node Given: " + t), n
      }
    },
    groups: {
      value: ["default"],
      getter: function() {
        return this._groups ? e.Object.keys(this._groups) : (this._groups = {}, [])
      },
      setter: function(t) {
        return this._groups = e.Array.hash(t), t
      }
    },
    padding: {
      value: "0",
      setter: function(e) {
        return r.cssSizestoObject(e)
      }
    },
    lock: {
      value: !1,
      setter: function(e) {
        return e ? this.get(n).addClass(r.CSS_PREFIX + "-drop-locked") : this.get(n).removeClass(r.CSS_PREFIX + "-drop-locked"), e
      }
    },
    bubbles: {
      setter: function(e) {
        return this.addTarget(e), e
      }
    },
    useShim: {
      value: !0,
      setter: function(t) {
        return e.DD.DDM._noShim = !t, t
      }
    }
  }, e.extend(f, e.Base, {
    _bubbleTargets: e.DD.DDM,
    addToGroup: function(e) {
      return this._groups[e] = !0, this
    },
    removeFromGroup: function(e) {
      return delete this._groups[e], this
    },
    _createEvents: function() {
      var t = [o, u, a, "drop:hit"];
      e.Array.each(t, function(e) {
        this.publish(e, {
          type: e,
          emitFacade: !0,
          preventable: !1,
          bubbles: !0,
          queuable: !1,
          prefix: "drop"
        })
      }, this)
    },
    _valid: null,
    _groups: null,
    shim: null,
    region: null,
    overTarget: null,
    inGroup: function(t) {
      this._valid = !1;
      var n = !1;
      return e.Array.each(t, function(e) {
        this._groups[e] && (n = !0, this._valid = !0)
      }, this), n
    },
    initializer: function() {
      e.later(100, this, this._createEvents);
      var t = this.get(n),
        i;
      t.get("id") || (i = e.stamp(t), t.set("id", i)), t.addClass(r.CSS_PREFIX + "-drop"), this.set("groups", this.get("groups"))
    },
    destructor: function() {
      r._unregTarget(this), this.shim && this.shim !== this.get(n) && (this.shim.detachAll(), this.shim.remove(), this.shim = null), this.get(n).removeClass(r.CSS_PREFIX + "-drop"), this.detachAll()
    },
    _deactivateShim: function() {
      if (!this.shim) return !1;
      this.get(n).removeClass(r.CSS_PREFIX + "-drop-active-valid"), this.get(n).removeClass(r.CSS_PREFIX + "-drop-active-invalid"), this.get(n).removeClass(r.CSS_PREFIX + "-drop-over"), this.get("useShim") && this.shim.setStyles({
        top: "-999px",
        left: "-999px",
        zIndex: "1"
      }), this.overTarget = !1
    },
    _activateShim: function() {
      if (!r.activeDrag) return !1;
      if (this.get(n) === r.activeDrag.get(n)) return !1;
      if (this.get("lock")) return !1;
      var e = this.get(n);
      this.inGroup(r.activeDrag.get("groups")) ? (e.removeClass(r.CSS_PREFIX + "-drop-active-invalid"), e.addClass(r.CSS_PREFIX + "-drop-active-valid"), r._addValid(this), this.overTarget = !1, this.get("useShim") || (this.shim = this.get(n)), this.sizeShim()) : (r._removeValid(this), e.removeClass(r.CSS_PREFIX + "-drop-active-valid"), e.addClass(r.CSS_PREFIX + "-drop-active-invalid"))
    },
    sizeShim: function() {
      if (!r.activeDrag) return !1;
      if (this.get(n) === r.activeDrag.get(n)) return !1;
      if (this.get("lock")) return !1;
      if (!this.shim) return e.later(100, this, this.sizeShim), !1;
      var t = this.get(n),
        o = t.get(i),
        u = t.get(s),
        a = t.getXY(),
        f = this.get("padding"),
        l, c, h;
      u = u + f.left + f.right, o = o + f.top + f.bottom, a[0] = a[0] - f.left, a[1] = a[1] - f.top, r.activeDrag.get("dragMode") === r.INTERSECT && (l = r.activeDrag, c = l.get(n).get(i), h = l.get(n).get(s), o += c, u += h, a[0] = a[0] - (h - l.deltaXY[0]), a[1] = a[1] - (c - l.deltaXY[1])), this.get("useShim") && this.shim.setStyles({
        height: o + "px",
        width: u + "px",
        top: a[1] + "px",
        left: a[0] + "px"
      }), this.region = {
        0: a[0],
        1: a[1],
        area: 0,
        top: a[1],
        right: a[0] + u,
        bottom: a[1] + o,
        left: a[0]
      }
    },
    _createShim: function() {
      if (!r._pg) {
        e.later(10, this, this._createShim);
        return
      }
      if (this.shim) return;
      var t = this.get("node");
      this.get("useShim") && (t = e.Node.create('<div id="' + this.get(n).get("id") + '_shim"></div>'), t.setStyles({
        height: this.get(n).get(i) + "px",
        width: this.get(n).get(s) + "px",
        backgroundColor: "yellow",
        opacity: ".5",
        zIndex: "1",
        overflow: "hidden",
        top: "-900px",
        left: "-900px",
        position: "absolute"
      }), r._pg.appendChild(t), t.on("mouseover", e.bind(this._handleOverEvent, this)), t.on("mouseout", e.bind(this._handleOutEvent, this))), this.shim = t
    },
    _handleTargetOver: function() {
      r.isOverTarget(this) ? (this.get(n).addClass(r.CSS_PREFIX + "-drop-over"), r.activeDrop = this, r.otherDrops[this] = this, this.overTarget ? (r.activeDrag.fire("drag:over", {
        drop: this,
        drag: r.activeDrag
      }), this.fire(o, {
        drop: this,
        drag: r.activeDrag
      })) : r.activeDrag.get("dragging") && (this.overTarget = !0, this.fire(u, {
        drop: this,
        drag: r.activeDrag
      }), r.activeDrag.fire("drag:enter", {
        drop: this,
        drag: r.activeDrag
      }), r.activeDrag.get(n).addClass(r.CSS_PREFIX + "-drag-over"))) : this._handleOut()
    },
    _handleOverEvent: function() {
      this.shim.setStyle("zIndex", "999"), r._addActiveShim(this)
    },
    _handleOutEvent: function() {
      this.shim.setStyle("zIndex", "1"), r._removeActiveShim(this)
    },
    _handleOut: function(e) {
      (!r.isOverTarget(this) || e) && this.overTarget && (this.overTarget = !1, e || r._removeActiveShim(this), r.activeDrag && (this.get(n).removeClass(r.CSS_PREFIX + "-drop-over"), r.activeDrag.get(n).removeClass(r.CSS_PREFIX + "-drag-over"), this.fire(a, {
        drop: this,
        drag: r.activeDrag
      }), r.activeDrag.fire("drag:exit", {
        drop: this,
        drag: r.activeDrag
      }), delete r.otherDrops[this]))
    }
  }), e.DD.Drop = f
}, "@VERSION@", {
  requires: ["dd-drag", "dd-ddm-drop"]
});

YUI.add("dd-scroll", function(e, t) {
  var n = function() {
      n.superclass.constructor.apply(this, arguments)
    },
    r, i, s = "host",
    o = "buffer",
    u = "parentScroll",
    a = "windowScroll",
    f = "scrollTop",
    l = "scrollLeft",
    c = "offsetWidth",
    h = "offsetHeight";
  n.ATTRS = {
    parentScroll: {
      value: !1,
      setter: function(e) {
        return e ? e : !1
      }
    },
    buffer: {
      value: 30,
      validator: e.Lang.isNumber
    },
    scrollDelay: {
      value: 235,
      validator: e.Lang.isNumber
    },
    host: {
      value: null
    },
    windowScroll: {
      value: !1,
      validator: e.Lang.isBoolean
    },
    vertical: {
      value: !0,
      validator: e.Lang.isBoolean
    },
    horizontal: {
      value: !0,
      validator: e.Lang.isBoolean
    }
  }, e.extend(n, e.Base, {
    _scrolling: null,
    _vpRegionCache: null,
    _dimCache: null,
    _scrollTimer: null,
    _getVPRegion: function() {
      var e = {},
        t = this.get(u),
        n = this.get(o),
        r = this.get(a),
        i = r ? [] : t.getXY(),
        s = r ? "winWidth" : c,
        p = r ? "winHeight" : h,
        d = r ? t.get(f) : i[1],
        v = r ? t.get(l) : i[0];
      return e = {
        top: d + n,
        right: t.get(s) + v - n,
        bottom: t.get(p) + d - n,
        left: v + n
      }, this._vpRegionCache = e, e
    },
    initializer: function() {
      var t = this.get(s);
      t.after("drag:start", e.bind(this.start, this)), t.after("drag:end", e.bind(this.end, this)), t.on("drag:align", e.bind(this.align, this)), e.one("win").on("scroll", e.bind(function() {
        this._vpRegionCache = null
      }, this))
    },
    _checkWinScroll: function(e) {
      var t = this._getVPRegion(),
        n = this.get(s),
        r = this.get(a),
        i = n.lastXY,
        c = !1,
        h = this.get(o),
        p = this.get(u),
        d = p.get(f),
        v = p.get(l),
        m = this._dimCache.w,
        g = this._dimCache.h,
        y = i[1] + g,
        b = i[1],
        w = i[0] + m,
        E = i[0],
        S = b,
        x = E,
        T = d,
        N = v;
      this.get("horizontal") && (E <= t.left && (c = !0, x = i[0] - (r ? h : 0), N = v - h), w >= t.right && (c = !0, x = i[0] + (r ? h : 0), N = v + h)), this.get("vertical") && (y >= t.bottom && (c = !0, S = i[1] + (r ? h : 0), T = d + h), b <= t.top && (c = !0, S = i[1] - (r ? h : 0), T = d - h)), T < 0 && (T = 0, S = i[1]), N < 0 && (N = 0, x = i[0]), S < 0 && (S = i[1]), x < 0 && (x = i[0]), e ? (n.actXY = [x, S], n._alignNode([x, S], !0), i = n.actXY, n.actXY = [x, S], n._moveNode({
        node: p,
        top: T,
        left: N
      }), !T && !N && this._cancelScroll()) : c ? this._initScroll() : this._cancelScroll()
    },
    _initScroll: function() {
      this._cancelScroll(), this._scrollTimer = e.Lang.later(this.get("scrollDelay"), this, this._checkWinScroll, [!0], !0)
    },
    _cancelScroll: function() {
      this._scrolling = !1, this._scrollTimer && (this._scrollTimer.cancel(), delete this._scrollTimer)
    },
    align: function(e) {
      this._scrolling && (this._cancelScroll(), e.preventDefault()), this._scrolling || this._checkWinScroll()
    },
    _setDimCache: function() {
      var e = this.get(s).get("dragNode");
      this._dimCache = {
        h: e.get(h),
        w: e.get(c)
      }
    },
    start: function() {
      this._setDimCache()
    },
    end: function() {
      this._dimCache = null, this._cancelScroll()
    }
  }), e.namespace("Plugin"), r = function() {
    r.superclass.constructor.apply(this, arguments)
  }, r.ATTRS = e.merge(n.ATTRS, {
    windowScroll: {
      value: !0,
      setter: function(t) {
        return t && this.set(u, e.one("win")), t
      }
    }
  }), e.extend(r, n, {
    initializer: function() {
      this.set("windowScroll", this.get("windowScroll"))
    }
  }), r.NAME = r.NS = "winscroll", e.Plugin.DDWinScroll = r, i = function() {
    i.superclass.constructor.apply(this, arguments)
  }, i.ATTRS = e.merge(n.ATTRS, {
    node: {
      value: !1,
      setter: function(t) {
        var n = e.one(t);
        return n ? this.set(u, n) : t !== !1 && e.error("DDNodeScroll: Invalid Node Given: " + t), n
      }
    }
  }), e.extend(i, n, {
    initializer: function() {
      this.set("node", this.get("node"))
    }
  }), i.NAME = i.NS = "nodescroll", e.Plugin.DDNodeScroll = i, e.DD.Scroll = n
}, "@VERSION@", {
  requires: ["dd-drag"]
});