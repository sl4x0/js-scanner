YUI.add("widget-autohide", function(e, t) {
  function m(t) {
    e.after(this._bindUIAutohide, this, f), e.after(this._syncUIAutohide, this, l), this.get(c) && (this._bindUIAutohide(), this._syncUIAutohide())
  }
  var n = "widgetAutohide",
    r = "autohide",
    i = "clickoutside",
    s = "focusoutside",
    o = "document",
    u = "key",
    a = "esc",
    f = "bindUI",
    l = "syncUI",
    c = "rendered",
    h = "boundingBox",
    p = "visible",
    d = "Change",
    v = e.ClassNameManager.getClassName;
  m.ATTRS = {
    hideOn: {
      validator: e.Lang.isArray,
      valueFn: function() {
        return [{
          node: e.one(o),
          eventName: u,
          keyCode: a
        }]
      }
    }
  }, m.prototype = {
    _uiHandlesAutohide: null,
    destructor: function() {
      this._detachUIHandlesAutohide()
    },
    _bindUIAutohide: function() {
      this.after(p + d, this._afterHostVisibleChangeAutohide), this.after("hideOnChange", this._afterHideOnChange)
    },
    _syncUIAutohide: function() {
      this._uiSetHostVisibleAutohide(this.get(p))
    },
    _uiSetHostVisibleAutohide: function(t) {
      t ? e.later(1, this, "_attachUIHandlesAutohide") : this._detachUIHandlesAutohide()
    },
    _attachUIHandlesAutohide: function() {
      if (this._uiHandlesAutohide) return;
      var t = this.get(h),
        n = e.bind(this.hide, this),
        r = [],
        i = this,
        s = this.get("hideOn"),
        o = 0,
        u = {
          node: undefined,
          ev: undefined,
          keyCode: undefined
        };
      for (; o < s.length; o++) u.node = s[o].node, u.ev = s[o].eventName, u.keyCode = s[o].keyCode, !u.node && !u.keyCode && u.ev ? r.push(t.on(u.ev, n)) : u.node && !u.keyCode && u.ev ? r.push(u.node.on(u.ev, n)) : u.node && u.keyCode && u.ev && r.push(u.node.on(u.ev, n, u.keyCode));
      this._uiHandlesAutohide = r
    },
    _detachUIHandlesAutohide: function() {
      e.each(this._uiHandlesAutohide, function(e) {
        e.detach()
      }), this._uiHandlesAutohide = null
    },
    _afterHostVisibleChangeAutohide: function(e) {
      this._uiSetHostVisibleAutohide(e.newVal)
    },
    _afterHideOnChange: function(e) {
      this._detachUIHandlesAutohide(), this.get(p) && this._attachUIHandlesAutohide()
    }
  }, e.WidgetAutohide = m
}, "@VERSION@", {
  requires: ["base-build", "event-key", "event-outside", "widget"]
});

YUI.add("escape", function(e, t) {
  var n = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#x27;",
      "/": "&#x2F;",
      "`": "&#x60;"
    },
    r = {
      html: function(e) {
        return (e + "").replace(/[&<>"'\/`]/g, r._htmlReplacer)
      },
      regex: function(e) {
        return (e + "").replace(/[\-$\^*()+\[\]{}|\\,.?\s]/g, "\\$&")
      },
      _htmlReplacer: function(e) {
        return n[e]
      }
    };
  r.regexp = r.regex, e.Escape = r
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("button-core", function(e, t) {
  function i(e) {
    this.initializer(e)
  }
  var n = e.ClassNameManager.getClassName,
    r = e.AttributeCore;
  i.prototype = {
    TEMPLATE: "<button/>",
    constructor: i,
    initializer: function(e) {
      this._initNode(e), this._initAttributes(e), this._renderUI(e)
    },
    _initNode: function(t) {
      t.host ? this._host = e.one(t.host) : this._host = e.Node.create(this.TEMPLATE)
    },
    _initAttributes: function(e) {
      r.call(this, i.ATTRS, e)
    },
    _renderUI: function() {
      var e = this.getNode(),
        t = e.get("nodeName").toLowerCase();
      e.addClass(i.CLASS_NAMES.BUTTON), t !== "button" && t !== "input" && e.set("role", "button")
    },
    enable: function() {
      this.set("disabled", !1)
    },
    disable: function() {
      this.set("disabled", !0)
    },
    getNode: function() {
      return this._host || (this._host = this.get("boundingBox")), this._host
    },
    _getLabel: function() {
      var e = this.getNode(),
        t = i._getTextLabelFromNode(e);
      return t
    },
    _getLabelHTML: function() {
      var e = this.getNode(),
        t = i._getHTMLFromNode(e);
      return t
    },
    _setLabel: function(t, n, r) {
      var i = e.Escape.html(t);
      return (!r || r.src !== "internal") && this.set("labelHTML", i, {
        src: "internal"
      }), i
    },
    _setLabelHTML: function(e, t, n) {
      var r = this.getNode(),
        s = i._getLabelNodeFromParent(r),
        o = r.get("nodeName").toLowerCase();
      return o === "input" ? s.set("value", e) : s.setHTML(e), (!n || n.src !== "internal") && this.set("label", e, {
        src: "internal"
      }), e
    },
    _setDisabled: function(e) {
      var t = this.getNode();
      return t.getDOMNode().disabled = e, t.toggleClass(i.CLASS_NAMES.DISABLED, e), e
    }
  }, e.mix(i.prototype, r.prototype), i.ATTRS = {
    label: {
      setter: "_setLabel",
      getter: "_getLabel",
      lazyAdd: !1
    },
    labelHTML: {
      setter: "_setLabelHTML",
      getter: "_getLabelHTML",
      lazyAdd: !1
    },
    disabled: {
      value: !1,
      setter: "_setDisabled",
      lazyAdd: !1
    }
  }, i.NAME = "button", i.CLASS_NAMES = {
    BUTTON: n("button"),
    DISABLED: n("button", "disabled"),
    SELECTED: n("button", "selected"),
    LABEL: n("button", "label")
  }, i.ARIA_STATES = {
    PRESSED: "aria-pressed",
    CHECKED: "aria-checked"
  }, i.ARIA_ROLES = {
    BUTTON: "button",
    CHECKBOX: "checkbox",
    TOGGLE: "toggle"
  }, i._getLabelNodeFromParent = function(e) {
    var t = e.one("." + i.CLASS_NAMES.LABEL) || e;
    return t
  }, i._getTextLabelFromNode = function(e) {
    var t = i._getLabelNodeFromParent(e),
      n = t.get("nodeName").toLowerCase(),
      r = t.get(n === "input" ? "value" : "text");
    return r
  }, i._getHTMLFromNode = function(e) {
    var t = i._getLabelNodeFromParent(e),
      n = t.getHTML();
    return n
  }, i._getDisabledFromNode = function(e) {
    return e.get("disabled")
  }, e.ButtonCore = i
}, "@VERSION@", {
  requires: ["attribute-core", "classnamemanager", "node-base", "escape"]
});

YUI.add("button-plugin", function(e, t) {
  function n() {
    n.superclass.constructor.apply(this, arguments)
  }
  e.extend(n, e.ButtonCore, {
    _afterNodeGet: function(t) {
      var n = this.constructor.ATTRS,
        r = n[t] && n[t].getter && this[n[t].getter];
      if (r) return new e.Do.AlterReturn("get " + t, r.call(this))
    },
    _afterNodeSet: function(e, t) {
      var n = this.constructor.ATTRS,
        r = n[e] && n[e].setter && this[n[e].setter];
      r && r.call(this, t)
    },
    _initNode: function(t) {
      var n = t.host;
      this._host = n, e.Do.after(this._afterNodeGet, n, "get", this), e.Do.after(this._afterNodeSet, n, "set", this)
    },
    destroy: function() {}
  }, {
    ATTRS: e.merge(e.ButtonCore.ATTRS),
    NAME: "buttonPlugin",
    NS: "button"
  }), n.createNode = function(t, n) {
    var r;
    return t && !n && !t.nodeType && !t.getDOMNode && typeof t != "string" && (n = t, t = n.srcNode), n = n || {}, r = n.template || e.Plugin.Button.prototype.TEMPLATE, t = t || n.srcNode || e.DOM.create(r), e.one(t).plug(e.Plugin.Button, n)
  }, e.namespace("Plugin").Button = n
}, "@VERSION@", {
  requires: ["button-core", "cssbutton", "node-pluginhost"]
});

YUI.add("widget-stdmod", function(e, t) {
  function H(e) {}
  var n = e.Lang,
    r = e.Node,
    i = e.UA,
    s = e.Widget,
    o = "",
    u = "hd",
    a = "bd",
    f = "ft",
    l = "header",
    c = "body",
    h = "footer",
    p = "fillHeight",
    d = "stdmod",
    v = "Node",
    m = "Content",
    g = "firstChild",
    y = "childNodes",
    b = "ownerDocument",
    w = "contentBox",
    E = "height",
    S = "offsetHeight",
    x = "auto",
    T = "headerContentChange",
    N = "bodyContentChange",
    C = "footerContentChange",
    k = "fillHeightChange",
    L = "heightChange",
    A = "contentUpdate",
    O = "renderUI",
    M = "bindUI",
    _ = "syncUI",
    D = "_applyParsedConfig",
    P = e.Widget.UI_SRC;
  H.HEADER = l, H.BODY = c, H.FOOTER = h, H.AFTER = "after", H.BEFORE = "before", H.REPLACE = "replace";
  var B = H.HEADER,
    j = H.BODY,
    F = H.FOOTER,
    I = B + m,
    q = F + m,
    R = j + m;
  H.ATTRS = {
    headerContent: {
      value: null
    },
    footerContent: {
      value: null
    },
    bodyContent: {
      value: null
    },
    fillHeight: {
      value: H.BODY,
      validator: function(e) {
        return this._validateFillHeight(e)
      }
    }
  }, H.HTML_PARSER = {
    headerContent: function(e) {
      return this._parseStdModHTML(B)
    },
    bodyContent: function(e) {
      return this._parseStdModHTML(j)
    },
    footerContent: function(e) {
      return this._parseStdModHTML(F)
    }
  }, H.SECTION_CLASS_NAMES = {
    header: s.getClassName(u),
    body: s.getClassName(a),
    footer: s.getClassName(f)
  }, H.TEMPLATES = {
    header: '<div class="' + H.SECTION_CLASS_NAMES[B] + '"></div>',
    body: '<div class="' + H.SECTION_CLASS_NAMES[j] + '"></div>',
    footer: '<div class="' + H.SECTION_CLASS_NAMES[F] + '"></div>'
  }, H.prototype = {
    initializer: function() {
      this._stdModNode = this.get(w), e.before(this._renderUIStdMod, this, O), e.before(this._bindUIStdMod, this, M), e.before(this._syncUIStdMod, this, _)
    },
    _syncUIStdMod: function() {
      var e = this._stdModParsed;
      (!e || !e[I]) && this._uiSetStdMod(B, this.get(I)), (!e || !e[R]) && this._uiSetStdMod(j, this.get(R)), (!e || !e[q]) && this._uiSetStdMod(F, this.get(q)), this._uiSetFillHeight(this.get(p))
    },
    _renderUIStdMod: function() {
      this._stdModNode.addClass(s.getClassName(d)), this._renderStdModSections(), this.after(T, this._afterHeaderChange), this.after(N, this._afterBodyChange), this.after(C, this._afterFooterChange)
    },
    _renderStdModSections: function() {
      n.isValue(this.get(I)) && this._renderStdMod(B), n.isValue(this.get(R)) && this._renderStdMod(j), n.isValue(this.get(q)) && this._renderStdMod(F)
    },
    _bindUIStdMod: function() {
      this.after(k, this._afterFillHeightChange), this.after(L, this._fillHeight), this.after(A, this._fillHeight)
    },
    _afterHeaderChange: function(e) {
      e.src !== P && this._uiSetStdMod(B, e.newVal, e.stdModPosition)
    },
    _afterBodyChange: function(e) {
      e.src !== P && this._uiSetStdMod(j, e.newVal, e.stdModPosition)
    },
    _afterFooterChange: function(e) {
      e.src !== P && this._uiSetStdMod(F, e.newVal, e.stdModPosition)
    },
    _afterFillHeightChange: function(e) {
      this._uiSetFillHeight(e.newVal)
    },
    _validateFillHeight: function(e) {
      return !e || e == H.BODY || e == H.HEADER || e == H.FOOTER
    },
    _uiSetFillHeight: function(e) {
      var t = this.getStdModNode(e),
        n = this._currFillNode;
      n && t !== n && n.setStyle(E, o), t && (this._currFillNode = t), this._fillHeight()
    },
    _fillHeight: function() {
      if (this.get(p)) {
        var e = this.get(E);
        e != o && e != x && this.fillHeight(this.getStdModNode(this.get(p)))
      }
    },
    _uiSetStdMod: function(e, t, r) {
      if (n.isValue(t)) {
        var i = this.getStdModNode(e, !0);
        this._addStdModContent(i, t, r), this.set(e + m, this._getStdModContent(e), {
          src: P
        })
      } else this._eraseStdMod(e);
      this.fire(A)
    },
    _renderStdMod: function(e) {
      var t = this.get(w),
        n = this._findStdModSection(e);
      return n || (n = this._getStdModTemplate(e)), this._insertStdModSection(t, e, n), this[e + v] = n, this[e + v]
    },
    _eraseStdMod: function(e) {
      var t = this.getStdModNode(e);
      t && (t.remove(!0), delete this[e + v])
    },
    _insertStdModSection: function(e, t, n) {
      var r = e.get(g);
      if (t === F || !r) e.appendChild(n);
      else if (t === B) e.insertBefore(n, r);
      else {
        var i = this[F + v];
        i ? e.insertBefore(n, i) : e.appendChild(n)
      }
    },
    _getStdModTemplate: function(e) {
      return r.create(H.TEMPLATES[e], this._stdModNode.get(b))
    },
    _addStdModContent: function(e, t, n) {
      switch (n) {
        case H.BEFORE:
          n = 0;
          break;
        case H.AFTER:
          n = undefined;
          break;
        default:
          n = H.REPLACE
      }
      e.insert(t, n)
    },
    _getPreciseHeight: function(e) {
      var t = e ? e.get(S) : 0,
        n = "getBoundingClientRect";
      if (e && e.hasMethod(n)) {
        var r = e.invoke(n);
        r && (t = r.bottom - r.top)
      }
      return t
    },
    _findStdModSection: function(e) {
      return this.get(w).one("> ." + H.SECTION_CLASS_NAMES[e])
    },
    _parseStdModHTML: function(t) {
      var n = this._findStdModSection(t);
      return n ? (this._stdModParsed || (this._stdModParsed = {}, e.before(this._applyStdModParsedConfig, this, D)), this._stdModParsed[t + m] = 1, n.get("innerHTML")) : null
    },
    _applyStdModParsedConfig: function(e, t, n) {
      var r = this._stdModParsed;
      r && (r[I] = !(I in t) && I in r, r[R] = !(R in t) && R in r, r[q] = !(q in t) && q in r)
    },
    _getStdModContent: function(e) {
      return this[e + v] ? this[e + v].get(y) : null
    },
    setStdModContent: function(e, t, n) {
      this.set(e + m, t, {
        stdModPosition: n
      })
    },
    getStdModNode: function(e, t) {
      var n = this[e + v] || null;
      return !n && t && (n = this._renderStdMod(e)), n
    },
    fillHeight: function(e) {
      if (e) {
        var t = this.get(w),
          r = [this.headerNode, this.bodyNode, this.footerNode],
          s, o, u = 0,
          a = 0,
          f = !1;
        for (var l = 0, c = r.length; l < c; l++) s = r[l], s && (s !== e ? u += this._getPreciseHeight(s) : f = !0);
        f && ((i.ie || i.opera) && e.set(S, 0), o = t.get(S) - parseInt(t.getComputedStyle("paddingTop"), 10) - parseInt(t.getComputedStyle("paddingBottom"), 10) - parseInt(t.getComputedStyle("borderBottomWidth"), 10) - parseInt(t.getComputedStyle("borderTopWidth"), 10), n.isNumber(o) && (a = o - u, a >= 0 && e.set(S, a)))
      }
    }
  }, e.WidgetStdMod = H
}, "@VERSION@", {
  requires: ["base-build", "widget"]
});

YUI.add("widget-buttons", function(e, t) {
  function p(e) {
    return !!e.getDOMNode
  }

  function d() {
    this._buttonsHandles = {}
  }
  var n = e.Array,
    r = e.Lang,
    i = e.Object,
    s = e.Plugin.Button,
    o = e.Widget,
    u = e.WidgetStdMod,
    a = e.ClassNameManager.getClassName,
    f = r.isArray,
    l = r.isNumber,
    c = r.isString,
    h = r.isValue;
  d.ATTRS = {
    buttons: {
      getter: "_getButtons",
      setter: "_setButtons",
      value: {}
    },
    defaultButton: {
      readOnly: !0,
      value: null
    }
  }, d.CLASS_NAMES = {
    button: a("button"),
    buttons: o.getClassName("buttons"),
    primary: a("button", "primary")
  }, d.HTML_PARSER = {
    buttons: function(e) {
      return this._parseButtons(e)
    }
  }, d.NON_BUTTON_NODE_CFG = ["action", "classNames", "context", "events", "isDefault", "section"], d.prototype = {
    BUTTONS: {},
    BUTTONS_TEMPLATE: "<span />",
    DEFAULT_BUTTONS_SECTION: u.FOOTER,
    initializer: function() {
      this._stdModNode || e.error("WidgetStdMod must be added to a Widget before WidgetButtons."), this._mapButtons(this.get("buttons")), this._updateDefaultButton(), this.after({
        buttonsChange: e.bind("_afterButtonsChange", this),
        defaultButtonChange: e.bind("_afterDefaultButtonChange", this)
      }), e.after(this._bindUIButtons, this, "bindUI"), e.after(this._syncUIButtons, this, "syncUI")
    },
    destructor: function() {
      i.each(this._buttonsHandles, function(e) {
        e.detach()
      }), delete this._buttonsHandles, delete this._buttonsMap, delete this._defaultButton
    },
    addButton: function(e, t, r) {
      var i = this.get("buttons"),
        s, o;
      return p(e) || (e = this._mergeButtonConfig(e), t || (t = e.section)), t || (t = this.DEFAULT_BUTTONS_SECTION), s = i[t] || (i[t] = []), l(r) || (r = s.length), s.splice(r, 0, e), o = n.indexOf(s, e), this.set("buttons", i, {
        button: e,
        section: t,
        index: o,
        src: "add"
      }), this
    },
    getButton: function(e, t) {
      if (!h(e)) return;
      var n = this._buttonsMap,
        r;
      return t || (t = this.DEFAULT_BUTTONS_SECTION), l(e) ? (r = this.get("buttons"), r[t] && r[t][e]) : arguments.length > 1 ? n[t + ":" + e] : n[e]
    },
    removeButton: function(e, t) {
      if (!h(e)) return this;
      var r = this.get("buttons"),
        s;
      return l(e) ? (t || (t = this.DEFAULT_BUTTONS_SECTION), s = e, e = r[t][s]) : (c(e) && (e = this.getButton.apply(this, arguments)), i.some(r, function(r, i) {
        s = n.indexOf(r, e);
        if (s > -1) return t = i, !0
      })), e && s > -1 && (r[t].splice(s, 1), this.set("buttons", r, {
        button: e,
        section: t,
        index: s,
        src: "remove"
      })), this
    },
    _bindUIButtons: function() {
      var t = e.bind("_afterContentChangeButtons", this);
      this.after({
        visibleChange: e.bind("_afterVisibleChangeButtons", this),
        headerContentChange: t,
        bodyContentChange: t,
        footerContentChange: t
      })
    },
    _createButton: function(t) {
      var r, i, o, u, a, f, l, h;
      if (p(t)) return e.one(t.getDOMNode()).plug(s);
      r = e.merge({
        context: this,
        events: "click",
        label: t.value
      }, t), i = e.merge(r), o = d.NON_BUTTON_NODE_CFG;
      for (u = 0, a = o.length; u < a; u += 1) delete i[o[u]];
      return t = s.createNode(i), l = r.context, f = r.action, c(f) && (f = e.bind(f, l)), h = t.on(r.events, f, l), this._buttonsHandles[e.stamp(t, !0)] = h, t.setData("name", this._getButtonName(r)), t.setData("default", this._getButtonDefault(r)), n.each(n(r.classNames), t.addClass, t), t
    },
    _getButtonContainer: function(t, n) {
      var r = u.SECTION_CLASS_NAMES[t],
        i = d.CLASS_NAMES.buttons,
        s = this.get("contentBox"),
        o, a;
      return o = "." + r + " ." + i, a = s.one(o), !a && n && (a = e.Node.create(this.BUTTONS_TEMPLATE), a.addClass(i)), a
    },
    _getButtonDefault: function(e) {
      var t = p(e) ? e.getData("default") : e.isDefault;
      return c(t) ? t.toLowerCase() === "true" : !!t
    },
    _getButtonName: function(e) {
      var t;
      return p(e) ? t = e.getData("name") || e.get("name") : t = e && (e.name || e.type), t
    },
    _getButtons: function(e) {
      var t = {};
      return i.each(e, function(e, n) {
        t[n] = e.concat()
      }), t
    },
    _mapButton: function(e, t) {
      var n = this._buttonsMap,
        r = this._getButtonName(e),
        i = this._getButtonDefault(e);
      r && (n[r] = e, n[t + ":" + r] = e), i && (this._defaultButton = e)
    },
    _mapButtons: function(e) {
      this._buttonsMap = {}, this._defaultButton = null, i.each(e, function(e, t) {
        var n, r;
        for (n = 0, r = e.length; n < r; n += 1) this._mapButton(e[n], t)
      }, this)
    },
    _mergeButtonConfig: function(t) {
      var n, r, i, s, o, u;
      return t = c(t) ? {
        name: t
      } : e.merge(t), t.srcNode && (s = t.srcNode, o = s.get("tagName").toLowerCase(), u = s.get(o === "input" ? "value" : "text"), n = {
        disabled: !!s.get("disabled"),
        isDefault: this._getButtonDefault(s),
        name: this._getButtonName(s)
      }, u && (n.label = u), e.mix(t, n, !1, null, 0, !0)), i = this._getButtonName(t), r = this.BUTTONS && this.BUTTONS[i], r && e.mix(t, r, !1, null, 0, !0), t
    },
    _parseButtons: function(e) {
      var t = "." + d.CLASS_NAMES.button,
        r = ["header", "body", "footer"],
        i = null;
      return n.each(r, function(e) {
        var n = this._getButtonContainer(e),
          r = n && n.all(t),
          s;
        if (!r || r.isEmpty()) return;
        s = [], r.each(function(e) {
          s.push({
            srcNode: e
          })
        }), i || (i = {}), i[e] = s
      }, this), i
    },
    _setButtons: function(e) {
      function r(e, r) {
        if (!f(e)) return;
        var i, s, o, u;
        for (i = 0, s = e.length; i < s; i += 1) o = e[i], u = r, p(o) || (o = this._mergeButtonConfig(o), u || (u = o.section)), o = this._createButton(o), u || (u = t), (n[u] || (n[u] = [])).push(o)
      }
      var t = this.DEFAULT_BUTTONS_SECTION,
        n = {};
      return f(e) ? r.call(this, e) : i.each(e, r, this), n
    },
    _syncUIButtons: function() {
      this._uiSetButtons(this.get("buttons")), this._uiSetDefaultButton(this.get("defaultButton")), this._uiSetVisibleButtons(this.get("visible"))
    },
    _uiInsertButton: function(e, t, n) {
      var r = d.CLASS_NAMES.button,
        i = this._getButtonContainer(t, !0),
        s = i.all("." + r);
      i.insertBefore(e, s.item(n)), this.setStdModContent(t, i, "after")
    },
    _uiRemoveButton: function(t, n, r) {
      var i = e.stamp(t, this),
        s = this._buttonsHandles,
        o = s[i],
        u, a;
      o && o.detach(), delete s[i], t.remove(), r || (r = {}), r.preserveContent || (u = this._getButtonContainer(n), a = d.CLASS_NAMES.button, u && u.all("." + a).isEmpty() && (u.remove(), this._updateContentButtons(n)))
    },
    _uiSetButtons: function(e) {
      var t = d.CLASS_NAMES.button,
        r = ["header", "body", "footer"];
      n.each(r, function(n) {
        var r = e[n] || [],
          i = r.length,
          s = this._getButtonContainer(n, i),
          o = !1,
          u, a, f, l;
        if (!s) return;
        u = s.all("." + t);
        for (a = 0; a < i; a += 1) f = r[a], l = u.indexOf(f), l > -1 ? (u.splice(l, 1), l !== a && (s.insertBefore(f, a + 1), o = !0)) : (s.appendChild(f), o = !0);
        u.each(function(e) {
          this._uiRemoveButton(e, n, {
            preserveContent: !0
          }), o = !0
        }, this);
        if (i === 0) {
          s.remove(), this._updateContentButtons(n);
          return
        }
        o && this.setStdModContent(n, s, "after")
      }, this)
    },
    _uiSetDefaultButton: function(e, t) {
      var n = d.CLASS_NAMES.primary;
      e && e.addClass(n), t && t.removeClass(n)
    },
    _uiSetVisibleButtons: function(e) {
      if (!e) return;
      var t = this.get("defaultButton");
      t && t.focus()
    },
    _unMapButton: function(e, t) {
      var n = this._buttonsMap,
        r = this._getButtonName(e),
        i;
      r && (n[r] === e && delete n[r], i = t + ":" + r, n[i] === e && delete n[i]), this._defaultButton === e && (this._defaultButton = null)
    },
    _updateDefaultButton: function() {
      var e = this._defaultButton;
      this.get("defaultButton") !== e && this._set("defaultButton", e)
    },
    _updateContentButtons: function(e) {
      var t = this.getStdModNode(e).get("childNodes");
      this.set(e + "Content", t.isEmpty() ? null : t, {
        src: "buttons"
      })
    },
    _afterButtonsChange: function(e) {
      var t = e.newVal,
        n = e.section,
        r = e.index,
        i = e.src,
        s;
      if (i === "add") {
        s = t[n][r], this._mapButton(s, n), this._updateDefaultButton(), this._uiInsertButton(s, n, r);
        return
      }
      if (i === "remove") {
        s = e.button, this._unMapButton(s, n), this._updateDefaultButton(), this._uiRemoveButton(s, n);
        return
      }
      this._mapButtons(t), this._updateDefaultButton(), this._uiSetButtons(t)
    },
    _afterContentChangeButtons: function(e) {
      var t = e.src,
        n = e.stdModPosition,
        r = !n || n === u.REPLACE;
      r && t !== "buttons" && t !== o.UI_SRC && this._uiSetButtons(this.get("buttons"))
    },
    _afterDefaultButtonChange: function(e) {
      this._uiSetDefaultButton(e.newVal, e.prevVal)
    },
    _afterVisibleChangeButtons: function(e) {
      this._uiSetVisibleButtons(e.newVal)
    }
  }, e.WidgetButtons = d
}, "@VERSION@", {
  requires: ["button-plugin", "cssbutton", "widget-stdmod"]
});

YUI.add("widget-modality", function(e, t) {
  function g(e) {}
  var n = "widget",
    r = "renderUI",
    i = "bindUI",
    s = "syncUI",
    o = "boundingBox",
    u = "visible",
    a = "zIndex",
    f = "Change",
    l = e.Lang.isBoolean,
    c = e.ClassNameManager.getClassName,
    h = "maskShow",
    p = "maskHide",
    d = "clickoutside",
    v = "focusoutside",
    m = function() {
      /*! IS_POSITION_FIXED_SUPPORTED - Juriy Zaytsev (kangax) - http://yura.thinkweb2.com/cft/ */
      ;
      var t = e.config.doc,
        n = null,
        r, i;
      return t.createElement && (r = t.createElement("div"), r && r.style && (r.style.position = "fixed", r.style.top = "10px", i = t.body, i && i.appendChild && i.removeChild && (i.appendChild(r), n = r.offsetTop === 10, i.removeChild(r)))), n
    }(),
    y = "modal",
    b = "mask",
    w = {
      modal: c(n, y),
      mask: c(n, b)
    };
  g.ATTRS = {
    maskNode: {
      getter: "_getMaskNode",
      readOnly: !0
    },
    modal: {
      value: !1,
      validator: l
    },
    focusOn: {
      valueFn: function() {
        return [{
          eventName: d
        }, {
          eventName: v
        }]
      },
      validator: e.Lang.isArray
    }
  }, g.CLASSES = w, g._MASK = null, g._GET_MASK = function() {
    var t = g._MASK,
      n = e.one("win");
    return t && t.getDOMNode() !== null && t.inDoc() ? t : (t = e.Node.create("<div></div>").addClass(w.mask), g._MASK = t, m ? t.setStyles({
      position: "fixed",
      width: "100%",
      height: "100%",
      top: "0",
      left: "0",
      display: "block"
    }) : t.setStyles({
      position: "absolute",
      width: n.get("winWidth") + "px",
      height: n.get("winHeight") + "px",
      top: "0",
      left: "0",
      display: "block"
    }), t)
  }, g.STACK = [], g.prototype = {
    initializer: function() {
      e.after(this._renderUIModal, this, r), e.after(this._syncUIModal, this, s), e.after(this._bindUIModal, this, i)
    },
    destructor: function() {
      this._uiSetHostVisibleModal(!1)
    },
    _uiHandlesModal: null,
    _renderUIModal: function() {
      var e = this.get(o);
      this._repositionMask(this), e.addClass(w.modal)
    },
    _bindUIModal: function() {
      this.after(u + f, this._afterHostVisibleChangeModal), this.after(a + f, this._afterHostZIndexChangeModal), this.after("focusOnChange", this._afterFocusOnChange), (!m || e.UA.ios && e.UA.ios < 5 || e.UA.android && e.UA.android < 3) && e.one("win").on("scroll", this._resyncMask, this)
    },
    _syncUIModal: function() {
      this._uiSetHostVisibleModal(this.get(u))
    },
    _focus: function() {
      var e = this.get(o),
        t = e.get("tabIndex");
      e.set("tabIndex", t >= 0 ? t : 0), this.focus()
    },
    _blur: function() {
      this.blur()
    },
    _getMaskNode: function() {
      return g._GET_MASK()
    },
    _uiSetHostVisibleModal: function(t) {
      var n = g.STACK,
        r = this.get("maskNode"),
        i = this.get("modal"),
        s, o;
      t ? (e.Array.each(n, function(e) {
        e._detachUIHandlesModal(), e._blur()
      }), n.unshift(this), this._repositionMask(this), this._uiSetHostZIndexModal(this.get(a)), i && (r.show(), e.later(1, this, "_attachUIHandlesModal"), this._focus())) : (o = e.Array.indexOf(n, this), o >= 0 && n.splice(o, 1), this._detachUIHandlesModal(), this._blur(), n.length ? (s = n[0], this._repositionMask(s), s._uiSetHostZIndexModal(s.get(a)), s.get("modal") && (e.later(1, s, "_attachUIHandlesModal"), s._focus())) : r.getStyle("display") === "block" && r.hide())
    },
    _uiSetHostZIndexModal: function(e) {
      this.get("modal") && this.get("maskNode").setStyle(a, e || 0)
    },
    _attachUIHandlesModal: function() {
      if (this._uiHandlesModal || g.STACK[0] !== this) return;
      var t = this.get(o),
        n = this.get("maskNode"),
        r = this.get("focusOn"),
        i = e.bind(this._focus, this),
        s = [],
        u, a, f;
      for (u = 0, a = r.length; u < a; u++) f = {}, f.node = r[u].node, f.ev = r[u].eventName, f.keyCode = r[u].keyCode, !f.node && !f.keyCode && f.ev ? s.push(t.on(f.ev, i)) : f.node && !f.keyCode && f.ev ? s.push(f.node.on(f.ev, i)) : f.node && f.keyCode && f.ev ? s.push(f.node.on(f.ev, i, f.keyCode)) : e.Log('focusOn ATTR Error: The event with name "' + f.ev + '" could not be attached.');
      m || s.push(e.one("win").on("scroll", e.bind(function() {
        n.setStyle("top", n.get("docScrollY"))
      }, this))), this._uiHandlesModal = s
    },
    _detachUIHandlesModal: function() {
      e.each(this._uiHandlesModal, function(e) {
        e.detach()
      }), this._uiHandlesModal = null
    },
    _afterHostVisibleChangeModal: function(e) {
      this._uiSetHostVisibleModal(e.newVal)
    },
    _afterHostZIndexChangeModal: function(e) {
      this._uiSetHostZIndexModal(e.newVal)
    },
    isNested: function() {
      var e = g.STACK.length,
        t = e > 1 ? !0 : !1;
      return t
    },
    _repositionMask: function(t) {
      var n = this.get("modal"),
        r = t.get("modal"),
        i = this.get("maskNode"),
        s, u;
      if (n && !r) i.remove(), this.fire(p);
      else if (!n && r || n && r) i.remove(), this.fire(p), s = t.get(o), u = s.get("parentNode") || e.one("body"), u.insert(i, u.get("firstChild")), this.fire(h)
    },
    _resyncMask: function(e) {
      var t = e.currentTarget,
        n = t.get("docScrollX"),
        r = t.get("docScrollY"),
        i = t.get("innerWidth") || t.get("winWidth"),
        s = t.get("innerHeight") || t.get("winHeight"),
        o = this.get("maskNode");
      o.setStyles({
        top: r + "px",
        left: n + "px",
        width: i + "px",
        height: s + "px"
      })
    },
    _afterFocusOnChange: function() {
      this._detachUIHandlesModal(), this.get(u) && this._attachUIHandlesModal()
    }
  }, e.WidgetModality = g
}, "@VERSION@", {
  requires: ["base-build", "event-outside", "widget"],
  skinnable: !0
});

YUI.add("widget-position", function(e, t) {
  function d(e) {}
  var n = e.Lang,
    r = e.Widget,
    i = "xy",
    s = "position",
    o = "positioned",
    u = "boundingBox",
    a = "relative",
    f = "renderUI",
    l = "bindUI",
    c = "syncUI",
    h = r.UI_SRC,
    p = "xyChange";
  d.ATTRS = {
    x: {
      setter: function(e) {
        this._setX(e)
      },
      getter: function() {
        return this._getX()
      },
      lazyAdd: !1
    },
    y: {
      setter: function(e) {
        this._setY(e)
      },
      getter: function() {
        return this._getY()
      },
      lazyAdd: !1
    },
    xy: {
      value: [0, 0],
      validator: function(e) {
        return this._validateXY(e)
      }
    }
  }, d.POSITIONED_CLASS_NAME = r.getClassName(o), d.prototype = {
    initializer: function() {
      this._posNode = this.get(u), e.after(this._renderUIPosition, this, f), e.after(this._syncUIPosition, this, c), e.after(this._bindUIPosition, this, l)
    },
    _renderUIPosition: function() {
      this._posNode.addClass(d.POSITIONED_CLASS_NAME)
    },
    _syncUIPosition: function() {
      var e = this._posNode;
      e.getStyle(s) === a && this.syncXY(), this._uiSetXY(this.get(i))
    },
    _bindUIPosition: function() {
      this.after(p, this._afterXYChange)
    },
    move: function() {
      var e = arguments,
        t = n.isArray(e[0]) ? e[0] : [e[0], e[1]];
      this.set(i, t)
    },
    syncXY: function() {
      this.set(i, this._posNode.getXY(), {
        src: h
      })
    },
    _validateXY: function(e) {
      return n.isArray(e) && n.isNumber(e[0]) && n.isNumber(e[1])
    },
    _setX: function(e) {
      this.set(i, [e, this.get(i)[1]])
    },
    _setY: function(e) {
      this.set(i, [this.get(i)[0], e])
    },
    _getX: function() {
      return this.get(i)[0]
    },
    _getY: function() {
      return this.get(i)[1]
    },
    _afterXYChange: function(e) {
      e.src != h && this._uiSetXY(e.newVal)
    },
    _uiSetXY: function(e) {
      this._posNode.setXY(e)
    }
  }, e.WidgetPosition = d
}, "@VERSION@", {
  requires: ["base-build", "node-screen", "widget"]
});

YUI.add("widget-position-align", function(e, t) {
  function c(e) {}
  var n = e.Lang,
    r = "align",
    i = "alignOn",
    s = "visible",
    o = "boundingBox",
    u = "offsetWidth",
    a = "offsetHeight",
    f = "region",
    l = "viewportRegion";
  c.ATTRS = {
    align: {
      value: null
    },
    centered: {
      setter: "_setAlignCenter",
      lazyAdd: !1,
      value: !1
    },
    alignOn: {
      value: [],
      validator: e.Lang.isArray
    }
  }, c.TL = "tl", c.TR = "tr", c.BL = "bl", c.BR = "br", c.TC = "tc", c.RC = "rc", c.BC = "bc", c.LC = "lc", c.CC = "cc", c.prototype = {
    initializer: function() {
      this._posNode || e.error("WidgetPosition needs to be added to the Widget, before WidgetPositionAlign is added"), e.after(this._bindUIPosAlign, this, "bindUI"), e.after(this._syncUIPosAlign, this, "syncUI")
    },
    _posAlignUIHandles: null,
    destructor: function() {
      this._detachPosAlignUIHandles()
    },
    _bindUIPosAlign: function() {
      this.after("alignChange", this._afterAlignChange), this.after("alignOnChange", this._afterAlignOnChange), this.after("visibleChange", this._syncUIPosAlign)
    },
    _syncUIPosAlign: function() {
      var e = this.get(r);
      this._uiSetVisiblePosAlign(this.get(s)), e && this._uiSetAlign(e.node, e.points)
    },
    align: function(e, t) {
      return arguments.length ? this.set(r, {
        node: e,
        points: t
      }) : this._syncUIPosAlign(), this
    },
    centered: function(e) {
      return this.align(e, [c.CC, c.CC])
    },
    _setAlignCenter: function(e) {
      return e && this.set(r, {
        node: e === !0 ? null : e,
        points: [c.CC, c.CC]
      }), e
    },
    _uiSetAlign: function(t, r) {
      if (!n.isArray(r) || r.length !== 2) {
        e.error("align: Invalid Points Arguments");
        return
      }
      var i = this._getRegion(t),
        s, o, u;
      if (!i) return;
      s = r[0], o = r[1];
      switch (o) {
        case c.TL:
          u = [i.left, i.top];
          break;
        case c.TR:
          u = [i.right, i.top];
          break;
        case c.BL:
          u = [i.left, i.bottom];
          break;
        case c.BR:
          u = [i.right, i.bottom];
          break;
        case c.TC:
          u = [i.left + Math.floor(i.width / 2), i.top];
          break;
        case c.BC:
          u = [i.left + Math.floor(i.width / 2), i.bottom];
          break;
        case c.LC:
          u = [i.left, i.top + Math.floor(i.height / 2)];
          break;
        case c.RC:
          u = [i.right, i.top + Math.floor(i.height / 2)];
          break;
        case c.CC:
          u = [i.left + Math.floor(i.width / 2), i.top + Math.floor(i.height / 2)];
          break;
        default:
      }
      u && this._doAlign(s, u[0], u[1])
    },
    _uiSetVisiblePosAlign: function(e) {
      e ? this._attachPosAlignUIHandles() : this._detachPosAlignUIHandles()
    },
    _attachPosAlignUIHandles: function() {
      if (this._posAlignUIHandles) return;
      var t = this.get(o),
        n = e.bind(this._syncUIPosAlign, this),
        r = [];
      e.Array.each(this.get(i), function(i) {
        var s = i.eventName,
          o = e.one(i.node) || t;
        s && r.push(o.on(s, n))
      }), this._posAlignUIHandles = r
    },
    _detachPosAlignUIHandles: function() {
      var t = this._posAlignUIHandles;
      t && ((new e.EventHandle(t)).detach(), this._posAlignUIHandles = null)
    },
    _doAlign: function(e, t, n) {
      var r = this._posNode,
        i;
      switch (e) {
        case c.TL:
          i = [t, n];
          break;
        case c.TR:
          i = [t - r.get(u), n];
          break;
        case c.BL:
          i = [t, n - r.get(a)];
          break;
        case c.BR:
          i = [t - r.get(u), n - r.get(a)];
          break;
        case c.TC:
          i = [t - r.get(u) / 2, n];
          break;
        case c.BC:
          i = [t - r.get(u) / 2, n - r.get(a)];
          break;
        case c.LC:
          i = [t, n - r.get(a) / 2];
          break;
        case c.RC:
          i = [t - r.get(u), n - r.get(a) / 2];
          break;
        case c.CC:
          i = [t - r.get(u) / 2, n - r.get(a) / 2];
          break;
        default:
      }
      i && this.move(i)
    },
    _getRegion: function(t) {
      var n;
      return t ? (t = e.Node.one(t), t && (n = t.get(f))) : n = this._posNode.get(l), n
    },
    _afterAlignChange: function(e) {
      var t = e.newVal;
      t && this._uiSetAlign(t.node, t.points)
    },
    _afterAlignOnChange: function(e) {
      this._detachPosAlignUIHandles(), this.get(s) && this._attachPosAlignUIHandles()
    }
  }, e.WidgetPositionAlign = c
}, "@VERSION@", {
  requires: ["widget-position"]
});

YUI.add("widget-position-constrain", function(e, t) {
  function m(e) {}
  var n = "constrain",
    r = "constrain|xyChange",
    i = "constrainChange",
    s = "preventOverlap",
    o = "align",
    u = "",
    a = "bindUI",
    f = "xy",
    l = "x",
    c = "y",
    h = e.Node,
    p = "viewportRegion",
    d = "region",
    v;
  m.ATTRS = {
    constrain: {
      value: null,
      setter: "_setConstrain"
    },
    preventOverlap: {
      value: !1
    }
  }, v = m._PREVENT_OVERLAP = {
    x: {
      tltr: 1,
      blbr: 1,
      brbl: 1,
      trtl: 1
    },
    y: {
      trbr: 1,
      tlbl: 1,
      bltl: 1,
      brtr: 1
    }
  }, m.prototype = {
    initializer: function() {
      this._posNode || e.error("WidgetPosition needs to be added to the Widget, before WidgetPositionConstrain is added"), e.after(this._bindUIPosConstrained, this, a)
    },
    getConstrainedXY: function(e, t) {
      t = t || this.get(n);
      var r = this._getRegion(t === !0 ? null : t),
        i = this._posNode.get(d);
      return [this._constrain(e[0], l, i, r), this._constrain(e[1], c, i, r)]
    },
    constrain: function(e, t) {
      var r, i, s = t || this.get(n);
      s && (r = e || this.get(f), i = this.getConstrainedXY(r, s), (i[0] !== r[0] || i[1] !== r[1]) && this.set(f, i, {
        constrained: !0
      }))
    },
    _setConstrain: function(e) {
      return e === !0 ? e : h.one(e)
    },
    _constrain: function(e, t, n, r) {
      if (r) {
        this.get(s) && (e = this._preventOverlap(e, t, n, r));
        var i = t == l,
          o = i ? r.width : r.height,
          u = i ? n.width : n.height,
          a = i ? r.left : r.top,
          f = i ? r.right - u : r.bottom - u;
        if (e < a || e > f) u < o ? e < a ? e = a : e > f && (e = f) : e = a
      }
      return e
    },
    _preventOverlap: function(e, t, n, r) {
      var i = this.get(o),
        s = t === l,
        a, f, c, h, p, d;
      return i && i.points && v[t][i.points.join(u)] && (f = this._getRegion(i.node), f && (a = s ? n.width : n.height, c = s ? f.left : f.top, h = s ? f.right : f.bottom, p = s ? f.left - r.left : f.top - r.top, d = s ? r.right - f.right : r.bottom - f.bottom), e > c ? d < a && p > a && (e = c - a) : p < a && d > a && (e = h)), e
    },
    _bindUIPosConstrained: function() {
      this.after(i, this._afterConstrainChange), this._enableConstraints(this.get(n))
    },
    _afterConstrainChange: function(e) {
      this._enableConstraints(e.newVal)
    },
    _enableConstraints: function(e) {
      e ? (this.constrain(), this._cxyHandle = this._cxyHandle || this.on(r, this._constrainOnXYChange)) : this._cxyHandle && (this._cxyHandle.detach(), this._cxyHandle = null)
    },
    _constrainOnXYChange: function(e) {
      e.constrained || (e.newVal = this.getConstrainedXY(e.newVal))
    },
    _getRegion: function(e) {
      var t;
      return e ? (e = h.one(e), e && (t = e.get(d))) : t = this._posNode.get(p), t
    }
  }, e.WidgetPositionConstrain = m
}, "@VERSION@", {
  requires: ["widget-position"]
});

YUI.add("widget-stack", function(e, t) {
  function O(e) {}
  var n = e.Lang,
    r = e.UA,
    i = e.Node,
    s = e.Widget,
    o = "zIndex",
    u = "shim",
    a = "visible",
    f = "boundingBox",
    l = "renderUI",
    c = "bindUI",
    h = "syncUI",
    p = "offsetWidth",
    d = "offsetHeight",
    v = "parentNode",
    m = "firstChild",
    g = "ownerDocument",
    y = "width",
    b = "height",
    w = "px",
    E = "shimdeferred",
    S = "shimresize",
    x = "visibleChange",
    T = "widthChange",
    N = "heightChange",
    C = "shimChange",
    k = "zIndexChange",
    L = "contentUpdate",
    A = "stacked";
  O.ATTRS = {
    shim: {
      value: r.ie == 6
    },
    zIndex: {
      value: 0,
      setter: "_setZIndex"
    }
  }, O.HTML_PARSER = {
    zIndex: function(e) {
      return this._parseZIndex(e)
    }
  }, O.SHIM_CLASS_NAME = s.getClassName(u), O.STACKED_CLASS_NAME = s.getClassName(A), O.SHIM_TEMPLATE = '<iframe class="' + O.SHIM_CLASS_NAME + '" frameborder="0" title="Widget Stacking Shim" src="javascript:false" tabindex="-1" role="presentation"></iframe>', O.prototype = {
    initializer: function() {
      this._stackNode = this.get(f), this._stackHandles = {}, e.after(this._renderUIStack, this, l), e.after(this._syncUIStack, this, h), e.after(this._bindUIStack, this, c)
    },
    _syncUIStack: function() {
      this._uiSetShim(this.get(u)), this._uiSetZIndex(this.get(o))
    },
    _bindUIStack: function() {
      this.after(C, this._afterShimChange), this.after(k, this._afterZIndexChange)
    },
    _renderUIStack: function() {
      this._stackNode.addClass(O.STACKED_CLASS_NAME)
    },
    _parseZIndex: function(e) {
      var t;
      return !e.inDoc() || e.getStyle("position") === "static" ? t = "auto" : t = e.getComputedStyle("zIndex"), t === "auto" ? null : t
    },
    _setZIndex: function(e) {
      return n.isString(e) && (e = parseInt(e, 10)), n.isNumber(e) || (e = 0), e
    },
    _afterShimChange: function(e) {
      this._uiSetShim(e.newVal)
    },
    _afterZIndexChange: function(e) {
      this._uiSetZIndex(e.newVal)
    },
    _uiSetZIndex: function(e) {
      this._stackNode.setStyle(o, e)
    },
    _uiSetShim: function(e) {
      e ? (this.get(a) ? this._renderShim() : this._renderShimDeferred(), r.ie == 6 && this._addShimResizeHandlers()) : this._destroyShim()
    },
    _renderShimDeferred: function() {
      this._stackHandles[E] = this._stackHandles[E] || [];
      var e = this._stackHandles[E],
        t = function(e) {
          e.newVal && this._renderShim()
        };
      e.push(this.on(x, t))
    },
    _addShimResizeHandlers: function() {
      this._stackHandles[S] = this._stackHandles[S] || [];
      var e = this.sizeShim,
        t = this._stackHandles[S];
      t.push(this.after(x, e)), t.push(this.after(T, e)), t.push(this.after(N, e)), t.push(this.after(L, e))
    },
    _detachStackHandles: function(e) {
      var t = this._stackHandles[e],
        n;
      if (t && t.length > 0)
        while (n = t.pop()) n.detach()
    },
    _renderShim: function() {
      var e = this._shimNode,
        t = this._stackNode;
      e || (e = this._shimNode = this._getShimTemplate(), t.insertBefore(e, t.get(m)), this._detachStackHandles(E), this.sizeShim())
    },
    _destroyShim: function() {
      this._shimNode && (this._shimNode.get(v).removeChild(this._shimNode), this._shimNode = null, this._detachStackHandles(E), this._detachStackHandles(S))
    },
    sizeShim: function() {
      var e = this._shimNode,
        t = this._stackNode;
      e && r.ie === 6 && this.get(a) && (e.setStyle(y, t.get(p) + w), e.setStyle(b, t.get(d) + w))
    },
    _getShimTemplate: function() {
      return i.create(O.SHIM_TEMPLATE, this._stackNode.get(g))
    }
  }, e.WidgetStack = O
}, "@VERSION@", {
  requires: ["base-build", "widget"],
  skinnable: !0
});

YUI.add("panel", function(e, t) {
  var n = e.ClassNameManager.getClassName;
  e.Panel = e.Base.create("panel", e.Widget, [e.WidgetPosition, e.WidgetStdMod, e.WidgetAutohide, e.WidgetButtons, e.WidgetModality, e.WidgetPositionAlign, e.WidgetPositionConstrain, e.WidgetStack], {
    BUTTONS: {
      close: {
        label: "Close",
        action: "hide",
        section: "header",
        template: '<button type="button" />',
        classNames: n("button", "close")
      }
    }
  }, {
    ATTRS: {
      buttons: {
        value: ["close"]
      }
    }
  })
}, "@VERSION@", {
  requires: ["widget", "widget-autohide", "widget-buttons", "widget-modality", "widget-position", "widget-position-align", "widget-position-constrain", "widget-stack", "widget-stdmod"],
  skinnable: !0
});