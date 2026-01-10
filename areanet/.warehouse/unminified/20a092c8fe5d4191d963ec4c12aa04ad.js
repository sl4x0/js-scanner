YUI.add("charrousel-widget", function(u) {
  var s = u.Lang,
    e = u.ClassNameManager.getClassName;
  u.Charrousel = u.Base.create("charrousel", u.Widget, [u.CharrouselBase], {
    _handles: [],
    TEMPLATES: {
      PREV: "<button class='{css}' data-dir='prev'>&lt;</button>",
      NEXT: "<button class='{css}' data-dir='next'>&gt;</button>",
      PAGES: "<ul class='{css}' role='presentation'>{pages}</ul>",
      PAGE: "<li class='{css}' role='presentation'><button data-page='{page}'>{label}</button></li>",
      NAV: "<div class='{css}' role='toolbar'>{prev}{pages}{next}</div>"
    },
    initializer: function() {
      var e = this,
        s = u.one(e.get("show.location"));
      e._cb = e.get("contentBox"), e._bb = e.get("boundingBox"), e._css = u.Charrousel.CLASSNAMES, e.onceAfter("render", function() {
        e._handles.push(e.after("pageChange", e.syncUI))
      }), e.set("show.location", s || e._cb)
    },
    destructor: function() {
      var e = this,
        s = e.get("show");
      new u.EventTarget(e._handles).detach(), (s.pages || s.prev || s.next) && this.get("rendered") && (s = s.location.one("." + e._css.nav)) && s.remove(!0), e._cb = e._bb = e._handles = e._css = null
    },
    renderUI: function() {
      var e, s, t, a = this,
        n = a.getAttrs(["show", "items", "list", "visible", "classes"]),
        i = n.show,
        r = n.list,
        l = n.classes,
        o = n.items,
        c = (o && o.size && o.size(), {
          css: a._css.nav + " " + (l.nav || ""),
          next: "",
          prev: "",
          pages: ""
        });
      if (1 < a._pages && (i.pages || i.next || i.prev)) {
        if (i.next && (c.next = u.Lang.sub(a.TEMPLATES.NEXT, {
            css: [a._css.button, a._css.buttons.next, l.next || ""].join(" ")
          })), i.prev && (c.prev = u.Lang.sub(a.TEMPLATES.PREV, {
            css: [a._css.button, a._css.buttons.prev, l.prev || ""].join(" ")
          })), i.pages) {
          for (e = "", s = 0, t = a._pages; s < t; s++) e += u.Lang.sub(a.TEMPLATES.PAGE, {
            css: a._css.page + (l.page ? " " + l.page : ""),
            page: s,
            label: s + 1
          });
          c.pages = u.Lang.sub(a.TEMPLATES.PAGES, {
            css: a._css.pages + " " + (l.pages || ""),
            pages: e
          })
        }
        i.location.append(u.Lang.sub(a.TEMPLATES.NAV, c))
      } else this.setAttrs({
        "show.pages": !1,
        "show.prev": !1,
        "show.next": !1
      });
      o.setAttribute("role", "option"), r.setAttribute("role", "listbox"), 1 < n.visible && (o.modulus(n.visible).addClass(a._css.itempage.first), o.modulus(n.visible, n.visible - 1).addClass(a._css.itempage.last)), l.list && r.addClass(l.list), l.item && o.addClass(l.item), l.content && a._cb.addClass(l.content), l.bounding && a._bb.addClass(l.bounding)
    },
    bindUI: function() {
      var t = this,
        e = t.get("show");
      e.pages && t._handles.push(e.location.delegate("click", function(e) {
        e.preventDefault(), t.set("page", parseInt(this.getAttribute("data-page"), 10), {
          source: "page-click"
        })
      }, `.${t._css.page} > button`)), (e.prev || e.next) && t._handles.push(e.location.delegate("click", function(e) {
        var s = this.getAttribute("data-dir");
        e.preventDefault(), t[s] && t[s](null, {
          source: s + "-click"
        })
      }, "." + t._css.button))
    },
    syncUI: function() {
      var e = this,
        s = e.get("show"),
        t = e.get("page"),
        a = e._css.current.page,
        n = e._css.current.item,
        i = s.pages && s.location.all("." + e._css.page);
      i && i.size() && (i.removeClass(a), i.item(t).addClass(a)), e.get("circular") || (s.prev && s.location.one("." + e._css.buttons.prev)[`${0<t?"remove":"set"}Attribute`]("disabled"), s.next && s.location.one("." + e._css.buttons.next)[`${t<e._pages-1?"remove":"set"}Attribute`]("disabled")), this.pageItems().addClass(n), this.otherItems().removeClass(n)
    }
  }, {
    ATTRS: {
      show: {
        value: {
          location: null,
          pages: !0,
          next: !0,
          prev: !0
        }
      },
      list: {
        setter: function(e) {
          return (e = u.one(e)) && e.addClass(this._css.list), e
        }
      },
      items: {
        setter: function(e) {
          return (e = s.isString(e) ? u.all(e) : e).size && e.size() && e.addClass(this._css.item), e
        }
      },
      classes: {
        value: {
          list: "yui3-g",
          item: "yui3-u",
          content: !1,
          bounding: !1,
          pages: "yui3-u yui3-g",
          page: "yui3-u",
          nav: "yui3-g",
          prev: "yui3-u",
          next: "yui3-u"
        }
      }
    },
    HTML_PARSER: {
      list: "> ol",
      items: ["> ol > li"]
    },
    CLASSNAMES: {
      list: e("charrousel", "list"),
      item: e("charrousel", "item"),
      nav: e("charrousel", "nav"),
      paging: e("charrousel", "paging"),
      pages: e("charrousel", "pages"),
      page: e("charrousel", "page"),
      disabled: e("charrousel", "paging", "disabled"),
      itempage: {
        first: e("charrousel", "item", "page", "first"),
        last: e("charrousel", "item", "page", "last")
      },
      current: {
        page: e("charrousel", "page", "current"),
        item: e("charrousel", "item", "current")
      },
      button: e("charrousel", "nav", "btn"),
      buttons: {
        prev: e("charrousel", "nav", "prev"),
        next: e("charrousel", "nav", "next")
      }
    }
  })
}, "@VERSION@", {
  requires: ["charrousel-base", "node-base", "base-build", "widget"]
});