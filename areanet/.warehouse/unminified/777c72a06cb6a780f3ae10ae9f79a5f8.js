(() => {
  var e = {
      10: e => {
        e.exports = {
          en: {
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "About Us",
                slug: "about"
              }, {
                name: "Our Games",
                slug: "games"
              }, {
                name: "Careers",
                slug: "careers"
              }],
              shoplink: {
                name: "Merchandise",
                slug: "https://www.guildwars2.com/en/shop/"
              },
              dimebar: {
                forums: "Forums",
                wiki: "Wiki",
                support: "Support",
                login: "Sign in",
                account: "Account",
                logout: "Logout",
                register: "Register"
              }
            }
          },
          de: {
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "\xdcber uns",
                slug: "about"
              }, {
                name: "Unsere Spiele",
                slug: "games"
              }, {
                name: "Jobs",
                slug: "careers"
              }],
              shoplink: {
                name: "Merchandising-Artikel",
                slug: "https://www.guildwars2.com/de/shop/"
              },
              dimebar: {
                forums: "Foren",
                wiki: "Wiki",
                support: "Support",
                login: "Login",
                account: "Account",
                logout: "Ausloggen",
                register: "Registrieren"
              }
            }
          },
          es: {
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "Sobre nosotros",
                slug: "about"
              }, {
                name: "Nuestros juegos",
                slug: "games"
              }, {
                name: "Carrera",
                slug: "careers"
              }],
              shoplink: {
                name: "Productos",
                slug: "https://www.guildwars2.com/es/shop/"
              },
              dimebar: {
                forums: "Foros",
                wiki: "Wiki",
                support: "Ayuda",
                login: "Iniciar sesi\xf3n",
                account: "Cuenta",
                logout: "Cerrar Sesi\xf3n",
                register: "Registro"
              }
            }
          },
          fr: {
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "Qui nous sommes",
                slug: "about"
              }, {
                name: "Nos jeux",
                slug: "games"
              }, {
                name: "Emplois",
                slug: "careers"
              }],
              shoplink: {
                name: "Produits d\xe9riv\xe9s",
                slug: "https://www.guildwars2.com/fr/shop/"
              },
              dimebar: {
                forums: "Forums",
                wiki: "Wiki",
                support: "Assistance",
                login: "Se connecter",
                account: "Compte",
                logout: "D\xe9connexion",
                register: "S'inscrire"
              }
            }
          },
          "en-gb": {
            nav: {
              navlinks: [{
                name: " About Us",
                slug: "about"
              }, {
                name: "Our Games",
                slug: "games"
              }, {
                name: "Careers",
                slug: "careers"
              }],
              shoplink: {
                name: "Merchandise",
                slug: "https://www.guildwars2.com/en-gb/shop/"
              },
              dimebar: {
                forums: "Forums",
                wiki: "Wiki",
                support: "Support",
                login: "Sign in",
                account: "Account",
                logout: "Logout",
                register: "Register"
              }
            }
          }
        }
      },
      58: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = n(361),
          o = n(894);
        e.exports = {
          view(e) {
            const t = a[e.attrs.lang].footer.esrb[e.attrs.footerLinks];
            return r("div", {
              class: o.rating,
              "data-test": "esrb-rating"
            }, r("a", {
              class: o.esrb,
              href: "https://www.esrb.org",
              target: "_blank",
              "aria-label": "esrb"
            }, "esrb"), r("div", r("ul", t.upper.split(",").map((e => r("li", e.trim())))), t.lower && [r("hr"), r("ul", t.lower.split(",").map((e => r("li", e.trim()))))]))
          }
        }
      },
      114: (e, t, n) => {
        ! function() {
          "use strict";

          function t(e, t, n, r, a, o) {
            return {
              tag: e,
              key: t,
              attrs: n,
              children: r,
              text: a,
              dom: o,
              domSize: void 0,
              state: void 0,
              _state: void 0,
              events: void 0,
              instance: void 0,
              skip: !1
            }
          }
          t.normalize = function(e) {
            return Array.isArray(e) ? t("[", void 0, void 0, t.normalizeChildren(e), void 0, void 0) : null != e && "object" != typeof e ? t("#", void 0, void 0, !1 === e ? "" : e, void 0, void 0) : e
          }, t.normalizeChildren = function(e) {
            for (var n = 0; n < e.length; n++) e[n] = t.normalize(e[n]);
            return e
          };
          var r = /(?:(^|#|\.)([^#\.\[\]]+))|(\[(.+?)(?:\s*=\s*("|'|)((?:\\["'\]]|.)*?)\5)?\])/g,
            a = {},
            o = {}.hasOwnProperty;

          function i(e) {
            for (var t in e)
              if (o.call(e, t)) return !1;
            return !0
          }

          function l(e) {
            var n, l = arguments[1],
              s = 2;
            if (null == e || "string" != typeof e && "function" != typeof e && "function" != typeof e.view) throw Error("The selector must be either a string or a component.");
            if ("string" == typeof e) var c = a[e] || function(e) {
              for (var t, n = "div", o = [], i = {}; t = r.exec(e);) {
                var l = t[1],
                  s = t[2];
                if ("" === l && "" !== s) n = s;
                else if ("#" === l) i.id = s;
                else if ("." === l) o.push(s);
                else if ("[" === t[3][0]) {
                  var c = t[6];
                  c && (c = c.replace(/\\(["'])/g, "$1").replace(/\\\\/g, "\\")), "class" === t[4] ? o.push(c) : i[t[4]] = "" === c ? c : c || !0
                }
              }
              return o.length > 0 && (i.className = o.join(" ")), a[e] = {
                tag: n,
                attrs: i
              }
            }(e);
            if (null == l ? l = {} : ("object" != typeof l || null != l.tag || Array.isArray(l)) && (l = {}, s = 1), arguments.length === s + 1) n = arguments[s], Array.isArray(n) || (n = [n]);
            else
              for (n = []; s < arguments.length;) n.push(arguments[s++]);
            var u = t.normalizeChildren(n);
            return "string" == typeof e ? function(e, n, r) {
              var a, l, s = !1,
                c = n.className || n.class;
              if (!i(e.attrs) && !i(n)) {
                var u = {};
                for (var f in n) o.call(n, f) && (u[f] = n[f]);
                n = u
              }
              for (var f in e.attrs) o.call(e.attrs, f) && (n[f] = e.attrs[f]);
              for (var f in void 0 !== c && (void 0 !== n.class && (n.class = void 0, n.className = c), null != e.attrs.className && (n.className = e.attrs.className + " " + c)), n)
                if (o.call(n, f) && "key" !== f) {
                  s = !0;
                  break
                } return Array.isArray(r) && 1 === r.length && null != r[0] && "#" === r[0].tag ? l = r[0].children : a = r, t(e.tag, n.key, s ? n : void 0, a, l)
            }(c, l, u) : t(e, l.key, l, u)
          }
          l.trust = function(e) {
            return null == e && (e = ""), t("<", void 0, void 0, e, void 0, void 0)
          }, l.fragment = function(e, n) {
            return t("[", e.key, e, t.normalizeChildren(n), void 0, void 0)
          };
          var s = l;
          if ((c = function(e) {
              if (!(this instanceof c)) throw new Error("Promise must be called with `new`");
              if ("function" != typeof e) throw new TypeError("executor must be a function");
              var t = this,
                n = [],
                r = [],
                a = s(n, !0),
                o = s(r, !1),
                i = t._instance = {
                  resolvers: n,
                  rejectors: r
                },
                l = "function" == typeof setImmediate ? setImmediate : setTimeout;

              function s(e, a) {
                return function s(c) {
                  var f;
                  try {
                    if (!a || null == c || "object" != typeof c && "function" != typeof c || "function" != typeof(f = c.then)) l((function() {
                      a || 0 !== e.length || console.error("Possible unhandled promise rejection:", c);
                      for (var t = 0; t < e.length; t++) e[t](c);
                      n.length = 0, r.length = 0, i.state = a, i.retry = function() {
                        s(c)
                      }
                    }));
                    else {
                      if (c === t) throw new TypeError("Promise can't be resolved w/ itself");
                      u(f.bind(c))
                    }
                  } catch (e) {
                    o(e)
                  }
                }
              }

              function u(e) {
                var t = 0;

                function n(e) {
                  return function(n) {
                    t++ > 0 || e(n)
                  }
                }
                var r = n(o);
                try {
                  e(n(a), r)
                } catch (e) {
                  r(e)
                }
              }
              u(e)
            }).prototype.then = function(e, t) {
              var n, r, a = this._instance;

              function o(e, t, o, i) {
                t.push((function(t) {
                  if ("function" != typeof e) o(t);
                  else try {
                    n(e(t))
                  } catch (e) {
                    r && r(e)
                  }
                })), "function" == typeof a.retry && i === a.state && a.retry()
              }
              var i = new c((function(e, t) {
                n = e, r = t
              }));
              return o(e, a.resolvers, n, !0), o(t, a.rejectors, r, !1), i
            }, c.prototype.catch = function(e) {
              return this.then(null, e)
            }, c.resolve = function(e) {
              return e instanceof c ? e : new c((function(t) {
                t(e)
              }))
            }, c.reject = function(e) {
              return new c((function(t, n) {
                n(e)
              }))
            }, c.all = function(e) {
              return new c((function(t, n) {
                var r = e.length,
                  a = 0,
                  o = [];
                if (0 === e.length) t([]);
                else
                  for (var i = 0; i < e.length; i++) ! function(i) {
                    function l(e) {
                      a++, o[i] = e, a === r && t(o)
                    }
                    null == e[i] || "object" != typeof e[i] && "function" != typeof e[i] || "function" != typeof e[i].then ? l(e[i]) : e[i].then(l, n)
                  }(i)
              }))
            }, c.race = function(e) {
              return new c((function(t, n) {
                for (var r = 0; r < e.length; r++) e[r].then(t, n)
              }))
            }, "undefined" != typeof window) {
            void 0 === window.Promise && (window.Promise = c);
            var c = window.Promise
          } else void 0 !== n.g && (void 0 === n.g.Promise && (n.g.Promise = c), c = n.g.Promise);
          var u, f = function(e) {
              if ("[object Object]" !== Object.prototype.toString.call(e)) return "";
              var t = [];
              for (var n in e) r(n, e[n]);
              return t.join("&");

              function r(e, n) {
                if (Array.isArray(n))
                  for (var a = 0; a < n.length; a++) r(e + "[" + a + "]", n[a]);
                else if ("[object Object]" === Object.prototype.toString.call(n))
                  for (var a in n) r(e + "[" + a + "]", n[a]);
                else t.push(encodeURIComponent(e) + (null != n && "" !== n ? "=" + encodeURIComponent(n) : ""))
              }
            },
            d = new RegExp("^file://", "i"),
            p = function(e, t) {
              var n, r = 0;

              function a() {
                var e = 0;

                function t() {
                  0 == --e && "function" == typeof n && n()
                }
                return function n(r) {
                  var a = r.then;
                  return r.then = function() {
                    e++;
                    var o = a.apply(r, arguments);
                    return o.then(t, (function(n) {
                      if (t(), 0 === e) throw n
                    })), n(o)
                  }, r
                }
              }

              function o(e, t) {
                if ("string" == typeof e) {
                  var n = e;
                  null == (e = t || {}).url && (e.url = n)
                }
                return e
              }

              function i(e, t) {
                if (null == t) return e;
                for (var n = e.match(/:[^\/]+/gi) || [], r = 0; r < n.length; r++) {
                  var a = n[r].slice(1);
                  null != t[a] && (e = e.replace(n[r], t[a]))
                }
                return e
              }

              function l(e, t) {
                var n = f(t);
                if ("" !== n) {
                  var r = e.indexOf("?") < 0 ? "?" : "&";
                  e += r + n
                }
                return e
              }

              function s(e) {
                try {
                  return "" !== e ? JSON.parse(e) : null
                } catch (t) {
                  throw new Error(e)
                }
              }

              function c(e) {
                return e.responseText
              }

              function u(e, t) {
                if ("function" == typeof e) {
                  if (!Array.isArray(t)) return new e(t);
                  for (var n = 0; n < t.length; n++) t[n] = new e(t[n])
                }
                return t
              }
              return {
                request: function(n, r) {
                  var f = a();
                  n = o(n, r);
                  var p = new t((function(t, r) {
                    null == n.method && (n.method = "GET"), n.method = n.method.toUpperCase();
                    var a = "GET" !== n.method && "TRACE" !== n.method && ("boolean" != typeof n.useBody || n.useBody);
                    "function" != typeof n.serialize && (n.serialize = "undefined" != typeof FormData && n.data instanceof FormData ? function(e) {
                      return e
                    } : JSON.stringify), "function" != typeof n.deserialize && (n.deserialize = s), "function" != typeof n.extract && (n.extract = c), n.url = i(n.url, n.data), a ? n.data = n.serialize(n.data) : n.url = l(n.url, n.data);
                    var o = new e.XMLHttpRequest,
                      f = !1,
                      p = o.abort;
                    for (var g in o.abort = function() {
                        f = !0, p.call(o)
                      }, o.open(n.method, n.url, "boolean" != typeof n.async || n.async, "string" == typeof n.user ? n.user : void 0, "string" == typeof n.password ? n.password : void 0), n.serialize !== JSON.stringify || !a || n.headers && n.headers.hasOwnProperty("Content-Type") || o.setRequestHeader("Content-Type", "application/json; charset=utf-8"), n.deserialize !== s || n.headers && n.headers.hasOwnProperty("Accept") || o.setRequestHeader("Accept", "application/json, text/*"), n.withCredentials && (o.withCredentials = n.withCredentials), n.headers)({}).hasOwnProperty.call(n.headers, g) && o.setRequestHeader(g, n.headers[g]);
                    "function" == typeof n.config && (o = n.config(o, n) || o), o.onreadystatechange = function() {
                      if (!f && 4 === o.readyState) try {
                        var e = n.extract !== c ? n.extract(o, n) : n.deserialize(n.extract(o, n));
                        if (o.status >= 200 && o.status < 300 || 304 === o.status || d.test(n.url)) t(u(n.type, e));
                        else {
                          var a = new Error(o.responseText);
                          for (var i in e) a[i] = e[i];
                          r(a)
                        }
                      } catch (e) {
                        r(e)
                      }
                    }, a && null != n.data ? o.send(n.data) : o.send()
                  }));
                  return !0 === n.background ? p : f(p)
                },
                jsonp: function(n, s) {
                  var c = a();
                  n = o(n, s);
                  var f = new t((function(t, a) {
                    var o = n.callbackName || "_mithril_" + Math.round(1e16 * Math.random()) + "_" + r++,
                      s = e.document.createElement("script");
                    e[o] = function(r) {
                      s.parentNode.removeChild(s), t(u(n.type, r)), delete e[o]
                    }, s.onerror = function() {
                      s.parentNode.removeChild(s), a(new Error("JSONP request failed")), delete e[o]
                    }, null == n.data && (n.data = {}), n.url = i(n.url, n.data), n.data[n.callbackKey || "callback"] = o, s.src = l(n.url, n.data), e.document.documentElement.appendChild(s)
                  }));
                  return !0 === n.background ? f : c(f)
                },
                setCompletionCallback: function(e) {
                  n = e
                }
              }
            }(window, c),
            g = function(e) {
              var n, r = e.document,
                a = r.createDocumentFragment(),
                o = {
                  svg: "http://www.w3.org/2000/svg",
                  math: "http://www.w3.org/1998/Math/MathML"
                };

              function i(e) {
                return e.attrs && e.attrs.xmlns || o[e.tag]
              }

              function l() {
                try {
                  return r.activeElement
                } catch (e) {
                  return null
                }
              }

              function s(e, t, n, r, a, o, i) {
                for (var l = n; l < r; l++) {
                  var s = t[l];
                  null != s && c(e, s, a, i, o)
                }
              }

              function c(e, n, o, l, d) {
                var p = n.tag;
                if ("string" != typeof p) return function(e, t, n, r, o) {
                  if (f(t, n), null != t.instance) {
                    var i = c(e, t.instance, n, r, o);
                    return t.dom = t.instance.dom, t.domSize = null != t.dom ? t.instance.domSize : 0, w(e, i, o), i
                  }
                  return t.domSize = 0, a
                }(e, n, o, l, d);
                switch (n.state = {}, null != n.attrs && S(n.attrs, n, o), p) {
                  case "#":
                    return function(e, t, n) {
                      return t.dom = r.createTextNode(t.children), w(e, t.dom, n), t.dom
                    }(e, n, d);
                  case "<":
                    return u(e, n, d);
                  case "[":
                    return function(e, t, n, a, o) {
                      var i = r.createDocumentFragment();
                      if (null != t.children) {
                        var l = t.children;
                        s(i, l, 0, l.length, n, null, a)
                      }
                      return t.dom = i.firstChild, t.domSize = i.childNodes.length, w(e, i, o), i
                    }(e, n, o, l, d);
                  default:
                    return function(e, n, a, o, l) {
                      var c = n.tag,
                        u = n.attrs,
                        f = u && u.is,
                        d = (o = i(n) || o) ? f ? r.createElementNS(o, c, {
                          is: f
                        }) : r.createElementNS(o, c) : f ? r.createElement(c, {
                          is: f
                        }) : r.createElement(c);
                      if (n.dom = d, null != u && function(e, t, n) {
                          for (var r in t) x(e, r, null, t[r], n)
                        }(n, u, o), w(e, d, l), null != n.attrs && null != n.attrs.contenteditable) v(n);
                      else if (null != n.text && ("" !== n.text ? d.textContent = n.text : n.children = [t("#", void 0, void 0, n.text, void 0, void 0)]), null != n.children) {
                        var p = n.children;
                        s(d, p, 0, p.length, a, null, o),
                          function(e) {
                            var t = e.attrs;
                            "select" === e.tag && null != t && ("value" in t && x(e, "value", null, t.value, void 0), "selectedIndex" in t && x(e, "selectedIndex", null, t.selectedIndex, void 0))
                          }(n)
                      }
                      return d
                    }(e, n, o, l, d)
                }
              }

              function u(e, t, n) {
                var a = {
                    caption: "table",
                    thead: "table",
                    tbody: "table",
                    tfoot: "table",
                    tr: "tbody",
                    th: "tr",
                    td: "tr",
                    colgroup: "table",
                    col: "colgroup"
                  } [(t.children.match(/^\s*?<(\w+)/im) || [])[1]] || "div",
                  o = r.createElement(a);
                o.innerHTML = t.children, t.dom = o.firstChild, t.domSize = o.childNodes.length;
                for (var i, l = r.createDocumentFragment(); i = o.firstChild;) l.appendChild(i);
                return w(e, l, n), l
              }

              function f(e, n) {
                var r;
                if ("function" == typeof e.tag.view) {
                  if (e.state = Object.create(e.tag), null != (r = e.state.view).$$reentrantLock$$) return a;
                  r.$$reentrantLock$$ = !0
                } else {
                  if (e.state = void 0, null != (r = e.tag).$$reentrantLock$$) return a;
                  r.$$reentrantLock$$ = !0, e.state = null != e.tag.prototype && "function" == typeof e.tag.prototype.view ? new e.tag(e) : e.tag(e)
                }
                if (e._state = e.state, null != e.attrs && S(e.attrs, e, n), S(e._state, e, n), e.instance = t.normalize(e._state.view.call(e.state, e)), e.instance === e) throw Error("A view cannot return the vnode it received as argument");
                r.$$reentrantLock$$ = null
              }

              function d(e, t, n, r, a, o, i) {
                if (t !== n && (null != t || null != n))
                  if (null == t) s(e, n, 0, n.length, a, o, i);
                  else if (null == n) b(t, 0, t.length, n);
                else {
                  if (t.length === n.length) {
                    for (var l = !1, u = 0; u < n.length; u++)
                      if (null != n[u] && null != t[u]) {
                        l = null == n[u].key && null == t[u].key;
                        break
                      } if (l) {
                      for (u = 0; u < t.length; u++) t[u] !== n[u] && (null == t[u] && null != n[u] ? c(e, n[u], a, i, h(t, u + 1, o)) : null == n[u] ? b(t, u, u + 1, n) : p(e, t[u], n[u], a, h(t, u + 1, o), r, i));
                      return
                    }
                  }
                  if (r = r || function(e, t) {
                      if (null != e.pool && Math.abs(e.pool.length - t.length) <= Math.abs(e.length - t.length)) {
                        var n = e[0] && e[0].children && e[0].children.length || 0,
                          r = e.pool[0] && e.pool[0].children && e.pool[0].children.length || 0,
                          a = t[0] && t[0].children && t[0].children.length || 0;
                        if (Math.abs(r - a) <= Math.abs(n - a)) return !0
                      }
                      return !1
                    }(t, n), r) {
                    var f = t.pool;
                    t = t.concat(t.pool)
                  }
                  for (var d, v = 0, y = 0, k = t.length - 1, A = n.length - 1; k >= v && A >= y;)
                    if ((C = t[v]) !== (N = n[y]) || r)
                      if (null == C) v++;
                      else if (null == N) y++;
                  else if (C.key === N.key) {
                    var x = null != f && v >= t.length - f.length || null == f && r;
                    y++, p(e, C, N, a, h(t, ++v, o), x, i), r && C.tag === N.tag && w(e, m(C), o)
                  } else if ((C = t[k]) !== N || r)
                    if (null == C) k--;
                    else if (null == N) y++;
                  else {
                    if (C.key !== N.key) break;
                    x = null != f && k >= t.length - f.length || null == f && r, p(e, C, N, a, h(t, k + 1, o), x, i), (r || y < A) && w(e, m(C), h(t, v, o)), k--, y++
                  } else k--, y++;
                  else v++, y++;
                  for (; k >= v && A >= y;) {
                    var C, N;
                    if ((C = t[k]) !== (N = n[A]) || r)
                      if (null == C) k--;
                      else if (null == N) A--;
                    else if (C.key === N.key) x = null != f && k >= t.length - f.length || null == f && r, p(e, C, N, a, h(t, k + 1, o), x, i), r && C.tag === N.tag && w(e, m(C), o), null != C.dom && (o = C.dom), k--, A--;
                    else {
                      if (d || (d = g(t, k)), null != N) {
                        var S = d[N.key];
                        if (null != S) {
                          var _ = t[S];
                          x = null != f && S >= t.length - f.length || null == f && r, p(e, _, N, a, h(t, k + 1, o), r, i), w(e, m(_), o), t[S].skip = !0, null != _.dom && (o = _.dom)
                        } else o = c(e, N, a, i, o)
                      }
                      A--
                    } else k--, A--;
                    if (A < y) break
                  }
                  s(e, n, y, A + 1, a, o, i), b(t, v, k + 1, n)
                }
              }

              function p(e, n, r, a, o, l, s) {
                var g = n.tag;
                if (g === r.tag) {
                  if (r.state = n.state, r._state = n._state, r.events = n.events, !l && function(e, t) {
                      var n, r;
                      return null != e.attrs && "function" == typeof e.attrs.onbeforeupdate && (n = e.attrs.onbeforeupdate.call(e.state, e, t)), "string" != typeof e.tag && "function" == typeof e._state.onbeforeupdate && (r = e._state.onbeforeupdate.call(e.state, e, t)), !(void 0 === n && void 0 === r || n || r || (e.dom = t.dom, e.domSize = t.domSize, e.instance = t.instance, 0))
                    }(r, n)) return;
                  if ("string" == typeof g) switch (null != r.attrs && (l ? (r.state = {}, S(r.attrs, r, a)) : _(r.attrs, r, a)), g) {
                    case "#":
                      ! function(e, t) {
                        e.children.toString() !== t.children.toString() && (e.dom.nodeValue = t.children), t.dom = e.dom
                      }(n, r);
                      break;
                    case "<":
                      ! function(e, t, n, r) {
                        t.children !== n.children ? (m(t), u(e, n, r)) : (n.dom = t.dom, n.domSize = t.domSize)
                      }(e, n, r, o);
                      break;
                    case "[":
                      ! function(e, t, n, r, a, o, i) {
                        d(e, t.children, n.children, r, a, o, i);
                        var l = 0,
                          s = n.children;
                        if (n.dom = null, null != s) {
                          for (var c = 0; c < s.length; c++) {
                            var u = s[c];
                            null != u && null != u.dom && (null == n.dom && (n.dom = u.dom), l += u.domSize || 1)
                          }
                          1 !== l && (n.domSize = l)
                        }
                      }(e, n, r, l, a, o, s);
                      break;
                    default:
                      ! function(e, n, r, a, o) {
                        var l = n.dom = e.dom;
                        o = i(n) || o, "textarea" === n.tag && (null == n.attrs && (n.attrs = {}), null != n.text && (n.attrs.value = n.text, n.text = void 0)),
                          function(e, t, n, r) {
                            if (null != n)
                              for (var a in n) x(e, a, t && t[a], n[a], r);
                            if (null != t)
                              for (var a in t) null != n && a in n || ("className" === a && (a = "class"), "o" !== a[0] || "n" !== a[1] || C(a) ? "key" !== a && e.dom.removeAttribute(a) : N(e, a, void 0))
                          }(n, e.attrs, n.attrs, o), null != n.attrs && null != n.attrs.contenteditable ? v(n) : null != e.text && null != n.text && "" !== n.text ? e.text.toString() !== n.text.toString() && (e.dom.firstChild.nodeValue = n.text) : (null != e.text && (e.children = [t("#", void 0, void 0, e.text, void 0, e.dom.firstChild)]), null != n.text && (n.children = [t("#", void 0, void 0, n.text, void 0, void 0)]), d(l, e.children, n.children, r, a, null, o))
                      }(n, r, l, a, s)
                  } else ! function(e, n, r, a, o, i, l) {
                    if (i) f(r, a);
                    else {
                      if (r.instance = t.normalize(r._state.view.call(r.state, r)), r.instance === r) throw Error("A view cannot return the vnode it received as argument");
                      null != r.attrs && _(r.attrs, r, a), _(r._state, r, a)
                    }
                    null != r.instance ? (null == n.instance ? c(e, r.instance, a, l, o) : p(e, n.instance, r.instance, a, o, i, l), r.dom = r.instance.dom, r.domSize = r.instance.domSize) : null != n.instance ? (y(n.instance, null), r.dom = void 0, r.domSize = 0) : (r.dom = n.dom, r.domSize = n.domSize)
                  }(e, n, r, a, o, l, s)
                } else y(n, null), c(e, r, a, s, o)
              }

              function g(e, t) {
                var n = {},
                  r = 0;
                for (r = 0; r < t; r++) {
                  var a = e[r];
                  if (null != a) {
                    var o = a.key;
                    null != o && (n[o] = r)
                  }
                }
                return n
              }

              function m(e) {
                var t = e.domSize;
                if (null != t || null == e.dom) {
                  var n = r.createDocumentFragment();
                  if (t > 0) {
                    for (var a = e.dom; --t;) n.appendChild(a.nextSibling);
                    n.insertBefore(a, n.firstChild)
                  }
                  return n
                }
                return e.dom
              }

              function h(e, t, n) {
                for (; t < e.length; t++)
                  if (null != e[t] && null != e[t].dom) return e[t].dom;
                return n
              }

              function w(e, t, n) {
                n && n.parentNode ? e.insertBefore(t, n) : e.appendChild(t)
              }

              function v(e) {
                var t = e.children;
                if (null != t && 1 === t.length && "<" === t[0].tag) {
                  var n = t[0].children;
                  e.dom.innerHTML !== n && (e.dom.innerHTML = n)
                } else if (null != e.text || null != t && 0 !== t.length) throw new Error("Child node of a contenteditable must be trusted")
              }

              function b(e, t, n, r) {
                for (var a = t; a < n; a++) {
                  var o = e[a];
                  null != o && (o.skip ? o.skip = !1 : y(o, r))
                }
              }

              function y(e, t) {
                var n, r = 1,
                  a = 0;

                function o() {
                  if (++a === r && (A(e), e.dom)) {
                    var n = e.domSize || 1;
                    if (n > 1)
                      for (var o = e.dom; --n;) k(o.nextSibling);
                    k(e.dom), null == t || null != e.domSize || null != (i = e.attrs) && (i.oncreate || i.onupdate || i.onbeforeremove || i.onremove) || "string" != typeof e.tag || (t.pool ? t.pool.push(e) : t.pool = [e])
                  }
                  var i
                }
                e.attrs && "function" == typeof e.attrs.onbeforeremove && null != (n = e.attrs.onbeforeremove.call(e.state, e)) && "function" == typeof n.then && (r++, n.then(o, o)), "string" != typeof e.tag && "function" == typeof e._state.onbeforeremove && null != (n = e._state.onbeforeremove.call(e.state, e)) && "function" == typeof n.then && (r++, n.then(o, o)), o()
              }

              function k(e) {
                var t = e.parentNode;
                null != t && t.removeChild(e)
              }

              function A(e) {
                if (e.attrs && "function" == typeof e.attrs.onremove && e.attrs.onremove.call(e.state, e), "string" != typeof e.tag) "function" == typeof e._state.onremove && e._state.onremove.call(e.state, e), null != e.instance && A(e.instance);
                else {
                  var t = e.children;
                  if (Array.isArray(t))
                    for (var n = 0; n < t.length; n++) {
                      var r = t[n];
                      null != r && A(r)
                    }
                }
              }

              function x(e, t, n, r, a) {
                var o = e.dom;
                if ("key" !== t && "is" !== t && (n !== r || function(e, t) {
                    return "value" === t || "checked" === t || "selectedIndex" === t || "selected" === t && e.dom === l()
                  }(e, t) || "object" == typeof r) && void 0 !== r && !C(t)) {
                  var i, s = t.indexOf(":");
                  if (s > -1 && "xlink" === t.substr(0, s)) o.setAttributeNS("http://www.w3.org/1999/xlink", t.slice(s + 1), r);
                  else if ("o" === t[0] && "n" === t[1] && "function" == typeof r) N(e, t, r);
                  else if ("style" === t) ! function(e, t, n) {
                    if (t === n && (e.style.cssText = "", t = null), null == n) e.style.cssText = "";
                    else if ("string" == typeof n) e.style.cssText = n;
                    else {
                      for (var r in "string" == typeof t && (e.style.cssText = ""), n) e.style[r] = n[r];
                      if (null != t && "string" != typeof t)
                        for (var r in t) r in n || (e.style[r] = "")
                    }
                  }(o, n, r);
                  else if (t in o && "href" !== (i = t) && "list" !== i && "form" !== i && "width" !== i && "height" !== i && void 0 === a && ! function(e) {
                      return e.attrs.is || e.tag.indexOf("-") > -1
                    }(e)) {
                    if ("value" === t) {
                      var c = "" + r;
                      if (("input" === e.tag || "textarea" === e.tag) && e.dom.value === c && e.dom === l()) return;
                      if ("select" === e.tag)
                        if (null === r) {
                          if (-1 === e.dom.selectedIndex && e.dom === l()) return
                        } else if (null !== n && e.dom.value === c && e.dom === l()) return;
                      if ("option" === e.tag && null != n && e.dom.value === c) return
                    }
                    if ("input" === e.tag && "type" === t) return void o.setAttribute(t, r);
                    o[t] = r
                  } else "boolean" == typeof r ? r ? o.setAttribute(t, "") : o.removeAttribute(t) : o.setAttribute("className" === t ? "class" : t, r)
                }
              }

              function C(e) {
                return "oninit" === e || "oncreate" === e || "onupdate" === e || "onremove" === e || "onbeforeremove" === e || "onbeforeupdate" === e
              }

              function N(e, t, r) {
                var a = e.dom,
                  o = "function" != typeof n ? r : function(e) {
                    var t = r.call(a, e);
                    return n.call(a, e), t
                  };
                if (t in a) a[t] = "function" == typeof r ? o : null;
                else {
                  var i = t.slice(2);
                  if (void 0 === e.events && (e.events = {}), e.events[t] === o) return;
                  null != e.events[t] && a.removeEventListener(i, e.events[t], !1), "function" == typeof r && (e.events[t] = o, a.addEventListener(i, e.events[t], !1))
                }
              }

              function S(e, t, n) {
                "function" == typeof e.oninit && e.oninit.call(t.state, t), "function" == typeof e.oncreate && n.push(e.oncreate.bind(t.state, t))
              }

              function _(e, t, n) {
                "function" == typeof e.onupdate && n.push(e.onupdate.bind(t.state, t))
              }
              return {
                render: function(e, n) {
                  if (!e) throw new Error("Ensure the DOM element being passed to m.route/m.mount/m.render is not undefined.");
                  var r = [],
                    a = l(),
                    o = e.namespaceURI;
                  null == e.vnodes && (e.textContent = ""), Array.isArray(n) || (n = [n]), d(e, e.vnodes, t.normalizeChildren(n), !1, r, null, "http://www.w3.org/1999/xhtml" === o ? void 0 : o), e.vnodes = n, null != a && l() !== a && a.focus();
                  for (var i = 0; i < r.length; i++) r[i]()
                },
                setEventCallback: function(e) {
                  return n = e
                }
              }
            },
            m = function(e) {
              var t = g(e);
              t.setEventCallback((function(e) {
                !1 === e.redraw ? e.redraw = void 0 : a()
              }));
              var n = [];

              function r(e) {
                var t = n.indexOf(e);
                t > -1 && n.splice(t, 2)
              }

              function a() {
                for (var e = 1; e < n.length; e += 2) n[e]()
              }
              return {
                subscribe: function(e, t) {
                  r(e), n.push(e, function(e) {
                    var t = 0,
                      n = null,
                      r = "function" == typeof requestAnimationFrame ? requestAnimationFrame : setTimeout;
                    return function() {
                      var a = Date.now();
                      0 === t || a - t >= 16 ? (t = a, e()) : null === n && (n = r((function() {
                        n = null, e(), t = Date.now()
                      }), 16 - (a - t)))
                    }
                  }(t))
                },
                unsubscribe: r,
                redraw: a,
                render: t.render
              }
            }(window);
          p.setCompletionCallback(m.redraw), s.mount = (u = m, function(e, n) {
            if (null === n) return u.render(e, []), void u.unsubscribe(e);
            if (null == n.view && "function" != typeof n) throw new Error("m.mount(element, component) expects a component, not a vnode");
            u.subscribe(e, (function() {
              u.render(e, t(n))
            })), u.redraw()
          });
          var h = c,
            w = function(e) {
              if ("" === e || null == e) return {};
              "?" === e.charAt(0) && (e = e.slice(1));
              for (var t = e.split("&"), n = {}, r = {}, a = 0; a < t.length; a++) {
                var o = t[a].split("="),
                  i = decodeURIComponent(o[0]),
                  l = 2 === o.length ? decodeURIComponent(o[1]) : "";
                "true" === l ? l = !0 : "false" === l && (l = !1);
                var s = i.split(/\]\[?|\[/),
                  c = r;
                i.indexOf("[") > -1 && s.pop();
                for (var u = 0; u < s.length; u++) {
                  var f = s[u],
                    d = s[u + 1],
                    p = "" == d || !isNaN(parseInt(d, 10));
                  if ("" === f) null == n[i = s.slice(0, u).join()] && (n[i] = Array.isArray(c) ? c.length : 0), f = n[i]++;
                  else if ("__proto__" === f) break;
                  if (u === s.length - 1) c[f] = l;
                  else {
                    var g = Object.getOwnPropertyDescriptor(c, f);
                    null != g && (g = g.value), null == g && (c[f] = g = p ? [] : {}), c = g
                  }
                }
              }
              return r
            };
          s.route = function(e, n) {
            var r, a, o, i, l, s = function(e) {
                var t, n = "function" == typeof e.history.pushState,
                  r = "function" == typeof setImmediate ? setImmediate : setTimeout;

                function a(t) {
                  var n = e.location[t].replace(/(?:%[a-f89][a-f0-9])+/gim, decodeURIComponent);
                  return "pathname" === t && "/" !== n[0] && (n = "/" + n), n
                }

                function o(e, t, n) {
                  var r = e.indexOf("?"),
                    a = e.indexOf("#"),
                    o = r > -1 ? r : a > -1 ? a : e.length;
                  if (r > -1) {
                    var i = a > -1 ? a : e.length,
                      l = w(e.slice(r + 1, i));
                    for (var s in l) t[s] = l[s]
                  }
                  if (a > -1) {
                    var c = w(e.slice(a + 1));
                    for (var s in c) n[s] = c[s]
                  }
                  return e.slice(0, o)
                }
                var i = {
                  prefix: "#!",
                  getPath: function() {
                    switch (i.prefix.charAt(0)) {
                      case "#":
                        return a("hash").slice(i.prefix.length);
                      case "?":
                        return a("search").slice(i.prefix.length) + a("hash");
                      default:
                        return a("pathname").slice(i.prefix.length) + a("search") + a("hash")
                    }
                  },
                  setPath: function(t, r, a) {
                    var l = {},
                      s = {};
                    if (t = o(t, l, s), null != r) {
                      for (var c in r) l[c] = r[c];
                      t = t.replace(/:([^\/]+)/g, (function(e, t) {
                        return delete l[t], r[t]
                      }))
                    }
                    var u = f(l);
                    u && (t += "?" + u);
                    var d = f(s);
                    if (d && (t += "#" + d), n) {
                      var p = a ? a.state : null,
                        g = a ? a.title : null;
                      e.onpopstate(), a && a.replace ? e.history.replaceState(p, g, i.prefix + t) : e.history.pushState(p, g, i.prefix + t)
                    } else e.location.href = i.prefix + t
                  },
                  defineRoutes: function(a, l, s) {
                    function c() {
                      var t = i.getPath(),
                        n = {},
                        r = o(t, n, n),
                        c = e.history.state;
                      if (null != c)
                        for (var u in c) n[u] = c[u];
                      for (var f in a) {
                        var d = new RegExp("^" + f.replace(/:[^\/]+?\.{3}/g, "(.*?)").replace(/:[^\/]+/g, "([^\\/]+)") + "/?$");
                        if (d.test(r)) return void r.replace(d, (function() {
                          for (var e = f.match(/:[^\/]+/g) || [], r = [].slice.call(arguments, 1, -2), o = 0; o < e.length; o++) n[e[o].replace(/:|\./g, "")] = decodeURIComponent(r[o]);
                          l(a[f], n, t, f)
                        }))
                      }
                      s(t, n)
                    }
                    var u;
                    n ? e.onpopstate = (u = c, function() {
                      null == t && (t = r((function() {
                        t = null, u()
                      })))
                    }) : "#" === i.prefix.charAt(0) && (e.onhashchange = c), c()
                  }
                };
                return i
              }(e),
              c = function(e) {
                return e
              },
              u = function(e, u, f) {
                if (null == e) throw new Error("Ensure the DOM element that was passed to `m.route` is not undefined");
                var d = function() {
                    null != r && n.render(e, r(t(a, o.key, o)))
                  },
                  p = function(e) {
                    if (e === u) throw new Error("Could not resolve default route " + u);
                    s.setPath(u, null, {
                      replace: !0
                    })
                  };
                s.defineRoutes(f, (function(e, t, n) {
                  var s = l = function(e, u) {
                    s === l && (a = null == u || "function" != typeof u.view && "function" != typeof u ? "div" : u, o = t, i = n, l = null, r = (e.render || c).bind(e), d())
                  };
                  e.view || "function" == typeof e ? s({}, e) : e.onmatch ? h.resolve(e.onmatch(t, n)).then((function(t) {
                    s(e, t)
                  }), p) : s(e, "div")
                }), p), n.subscribe(e, d)
              };
            return u.set = function(e, t, n) {
              null != l && ((n = n || {}).replace = !0), l = null, s.setPath(e, t, n)
            }, u.get = function() {
              return i
            }, u.prefix = function(e) {
              s.prefix = e
            }, u.link = function(e) {
              e.dom.setAttribute("href", s.prefix + e.attrs.href), e.dom.onclick = function(e) {
                if (!(e.ctrlKey || e.metaKey || e.shiftKey || 2 === e.which)) {
                  e.preventDefault(), e.redraw = !1;
                  var t = this.getAttribute("href");
                  0 === t.indexOf(s.prefix) && (t = t.slice(s.prefix.length)), u.set(t, void 0, void 0)
                }
              }
            }, u.param = function(e) {
              return void 0 !== o && void 0 !== e ? o[e] : o
            }, u
          }(window, m), s.withAttr = function(e, t, n) {
            return function(r) {
              t.call(n || this, e in r.currentTarget ? r.currentTarget[e] : r.currentTarget.getAttribute(e))
            }
          };
          var v = g(window);
          s.render = v.render, s.redraw = m.redraw, s.request = p.request, s.jsonp = p.jsonp, s.parseQueryString = w, s.buildQueryString = f, s.version = "1.1.7", s.vnode = t, e.exports = s
        }()
      },
      204: (e, t, n) => {
        "use strict";
        n.r(t), n.d(t, {
          anetDimebar: () => r,
          anetDimebarAbs: () => a,
          anetLogo: () => u,
          currentLang: () => d,
          default: () => g,
          downloadBtn: () => c,
          hideable: () => p,
          langSelectBar: () => f,
          primaryNav: () => l,
          secondaryNav: () => s,
          siteNav: () => i,
          wrapper: () => o
        });
        const r = "mcc512ad16_anetDimebar",
          a = r + " mcc512ad16_anetDimebarAbs",
          o = "mcc512ad16_wrapper",
          i = "mcc512ad16_siteNav",
          l = "mcc512ad16_primaryNav",
          s = "mcc512ad16_secondaryNav",
          c = "mcc512ad16_downloadBtn",
          u = "mcc512ad16_anetLogo",
          f = "mcc512ad16_langSelectBar",
          d = "mcc512ad16_currentLang",
          p = "mcc512ad16_hideable",
          g = {
            anetDimebar: r,
            anetDimebarAbs: a,
            wrapper: o,
            siteNav: i,
            primaryNav: l,
            secondaryNav: s,
            downloadBtn: c,
            anetLogo: u,
            langSelectBar: f,
            currentLang: d,
            hideable: p
          }
      },
      246: e => {
        "use strict";

        function t(e, t, n, r) {
          (window.dataLayer || []).push({
            event: "event",
            eventCategory: r || "anet2",
            eventAction: e,
            eventLabel: t,
            eventValue: n
          })
        }
        e.exports = {
          event: t,
          clickTracker: function() {
            const e = document.querySelectorAll("[data-ga-event]");
            Array.prototype.forEach.call(e, (e => {
              e.addEventListener("click", (e => {
                t(e.target.dataset.gaAction || "click", e.target.dataset.gaLabel || e.target.text, e.target.dataset.gaValue || 1, e.target.dataset.gaCategory)
              }))
            }))
          },
          pageView: function(e, t) {
            (window.dataLayer || []).push({
              event: "pageview",
              url: e,
              title: t
            })
          },
          scrollHandler: function(e) {
            const n = document.getElementsByTagName("section");
            Array.prototype.forEach.call(n, (n => {
              const r = Date.now(),
                a = n.getBoundingClientRect().top < window.innerHeight,
                o = !n.dataset.gaTriggered || parseInt(n.dataset.gaTriggered, 10) + 3e4 < r;
              a && o && (n.dataset.gaTriggered = r, t("Section view", `${n.id.charAt(0).toUpperCase()+n.id.slice(1)}`, "", `${e} Page`))
            }))
          }
        }
      },
      301: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = n(58),
          o = n(353),
          i = n(649),
          l = n(894),
          s = n(246).event,
          c = n(361),
          u = n(716),
          f = n(453),
          d = {
            esrb: a,
            pegi: o,
            usk: i
          };
        let p;
        const g = {
          view(e) {
            const t = p ? r.route.link : null;
            return r("a", Object.assign({
              oncreate: t,
              onupdate: t
            }, e.attrs), e.children)
          }
        };
        e.exports = {
          oninit(e) {
            const {
              lang: t,
              curDate: n,
              routeLink: r
            } = e.attrs;
            p = r;
            const a = c[t] || c.en,
              o = u[t] || u.en;
            e.state.i18n = a, e.state.navs = a.nav.navlinks, e.state.followLinks = Object.keys(a.footer.socials), e.state.copyrightWithYear = o.copyright.replace("{year}", n)
          },
          oncreate() {
            document.dispatchEvent(new Event("anetfooter-loaded"))
          },
          view(e) {
            const {
              lang: t,
              rating: n,
              routeLink: a,
              noSocial: o,
              showNav: i,
              theme: c = "",
              light: u = !1,
              footerLinks: p = "gw2",
              nc: m = !1
            } = e.attrs, {
              followLinks: h,
              i18n: w,
              navs: v,
              copyrightWithYear: b
            } = e.state;
            return r("div", {
              class: [i || o ? null : l.navCleanup, !i && o ? l.halfFooter : l.footer, u ? l.footerLight : "", m ? l.ncFooter : ""].join(" "),
              "data-test": "footer"
            }, i || !o ? [r("ul", {
              class: l.pageFooterNav
            }, Object.keys(v).map((e => r("li", r(g, {
              href: `${a?"":"https://www.arena.net"}/${t}/${v[e].slug}`,
              "data-ga-event": "",
              "data-ga-category": "Footer"
            }, v[e].name)))), r("li", r("a", {
              href: w.nav.shoplink.slug,
              target: "_blank",
              rel: "noreferrer",
              "data-ga-event": "",
              "data-ga-category": "Footer"
            }, w.nav.shoplink.name))), o ? null : r("div", {
              class: `${l[c]} ${l.socialBar}`
            }, r("p", {
              class: l.followUs
            }, w.footer.followUs), h.map((e => r("a", {
              onclick() {
                s("Social Media", w.footer.socials[e].label, 1, "Footer")
              },
              class: l[e],
              href: f.socials[e][t],
              target: "_blank",
              rel: "noreferrer",
              "aria-label": w.footer.socials[e].label
            }))))] : null, r("div", {
              class: l.logos
            }, m ? r(g, {
              class: l.nc,
              href: a ? "" : "https://www.ncsoft.com",
              "data-ga-event": "",
              "data-ga-category": "Footer",
              "aria-label": "NCSoft Home"
            }, "NCSoft") : null, r(g, {
              class: `${l.anet} ${l[`anet${c}`]}`,
              href: a ? "" : "https://www.arena.net",
              "data-ga-event": "",
              "data-ga-category": "Footer",
              "aria-label": "ArenaNet Home"
            }, "ArenaNet")), r("div", {
              class: l.legalFooter
            }, r("div", r("a", {
              href: "#ShowCookiePreferences",
              onclick: function(e) {
                e.preventDefault();
                const t = window.arenanetCookieNotification;
                t && t.toggle && t.toggle()
              }
            }, w.footer.links.cookiepreferences), Object.entries(f.footer[p]).map((([e, n]) => {
              const a = n.replace("{lang}", t),
                o = w.footer.links[p][e];
              return r(n.includes("https") ? "a" : g, {
                href: a
              }, o)
            }))), r("p", b)), n && d[n] ? r(d[n], {
              lang: t,
              theme: c,
              footerLinks: p
            }) : null)
          }
        }
      },
      353: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = n(894);
        e.exports = {
          view: () => r("div", {
            class: a.rating,
            "data-test": "pegi-rating"
          }, r("a", {
            class: a.pegi,
            href: "https://www.pegi.info",
            target: "_blank",
            "aria-label": "pegi"
          }, "pegi"))
        }
      },
      361: e => {
        e.exports = {
          en: {
            "": "",
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "About Us",
                slug: "about"
              }, {
                name: "Our Games",
                slug: "games",
                dropdown: [{
                  name: "Guild Wars 2",
                  slug: "https://www.guildwars2.com"
                }, {
                  name: "Guild Wars",
                  slug: "https://www.guildwars.com"
                }]
              }, {
                name: "Careers",
                slug: "careers"
              }, {
                name: "Contact",
                slug: "contact"
              }],
              shoplink: {
                name: "Merchandise",
                slug: "https://www.guildwars2.com/en/shop/"
              },
              supportlink: {
                name: "Support",
                slug: "https://help.guildwars2.com"
              }
            },
            misc: {
              buttons: {
                labels: {
                  next: "Next",
                  prev: "Previous",
                  openmenu: "Menu",
                  close: "Close",
                  play: "Play Video",
                  readmore: "Read More"
                }
              }
            },
            footer: {
              followUs: "Follow Us",
              socials: {
                youtube: {
                  label: "YouTube",
                  href: "https://www.youtube.com/arenanet"
                },
                facebook: {
                  label: "Facebook",
                  href: "https://www.facebook.com/ArenaNet/"
                },
                twitter: {
                  label: "Twitter",
                  href: "https://twitter.com/ArenaNet"
                },
                twitch: {
                  label: "Twitch",
                  href: "https://twitch.tv/guildwars2"
                },
                instagram: {
                  label: "Instagram",
                  href: "https://instagram.com/arenanet"
                },
                tumblr: {
                  label: "Tumblr",
                  href: "https://guildwars2.tumblr.com"
                },
                flickr: {
                  label: "Flickr",
                  href: "https://flickr.com/photos/arenanet"
                }
              },
              links: {
                cookiepreferences: "Cookie Preferences",
                gw2: {
                  privacy: "Privacy Policy",
                  legal: "Legal Documentation"
                },
                gw1: {
                  partners: "Partners",
                  legal: "Legal Documentation",
                  privacy: "Privacy Policy"
                }
              },
              esrb: {
                gw2: {
                  upper: "Blood and Gore, Language, Use of Alcohol, Violence",
                  lower: "In-Game Purchases, Users Interact"
                },
                gw1: {
                  upper: "Animated Blood, Mild Suggestive Themes, Violence, Use of Alcohol"
                }
              },
              pegi: {
                provisional: "Provisional"
              },
              ad: {
                label: "Buy Now"
              }
            }
          },
          de: {
            "": "",
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "\xdcber uns",
                slug: "about"
              }, {
                name: "Unsere Spiele",
                slug: "games",
                dropdown: [{
                  name: "Guild Wars 2",
                  slug: "https://www.guildwars2.com/de/"
                }, {
                  name: "Guild Wars",
                  slug: "https://www.guildwars.com/de/"
                }]
              }, {
                name: "Jobs",
                slug: "careers"
              }, {
                name: "Kontakt",
                slug: "contact"
              }],
              shoplink: {
                name: "Merchandising-Artikel",
                slug: "https://www.guildwars2.com/de/shop/"
              },
              supportlink: {
                name: "Support",
                slug: "https://help.guildwars2.com"
              }
            },
            misc: {
              buttons: {
                labels: {
                  next: "Weiter",
                  prev: "Zur\xfcck",
                  openmenu: "Men\xfc",
                  close: "Schliessen",
                  play: "Abspielen",
                  readmore: "Weitere Infos"
                }
              }
            },
            footer: {
              followUs: "Folgt Uns",
              socials: {
                youtube: {
                  label: "YouTube",
                  href: "https://www.youtube.com/arenanet"
                },
                facebook: {
                  label: "Facebook",
                  href: "https://www.facebook.com/ArenaNet/"
                },
                twitter: {
                  label: "Twitter",
                  href: "https://twitter.com/ArenaNet"
                },
                twitch: {
                  label: "Twitch",
                  href: "https://twitch.tv/guildwars2"
                },
                instagram: {
                  label: "Instagram",
                  href: "https://instagram.com/arenanet"
                },
                tumblr: {
                  label: "Tumblr",
                  href: "https://guildwars2.tumblr.com"
                },
                flickr: {
                  label: "Flickr",
                  href: "https://flickr.com/photos/arenanet"
                }
              },
              links: {
                cookiepreferences: "Cookie-Einstellungen",
                gw2: {
                  privacy: "Datenschutzrichtlinie",
                  legal: "Rechtliche Informationen"
                },
                gw1: {
                  partners: "Partner",
                  legal: "Rechtliche Informationen",
                  privacy: "Datenschutzrichtlinie"
                }
              },
              esrb: {
                gw2: {
                  upper: "Blood and Gore, Language, Use of Alcohol, Violence",
                  lower: "In-Game Purchases, Users Interact"
                },
                gw1: {
                  upper: "Animiertes Blut, Leichte Anspielungen, Gewalt, Alkoholkonsum"
                }
              },
              pegi: {
                provisional: "Provisorisch"
              },
              ad: {
                label: "Jetzt kaufen"
              }
            }
          },
          es: {
            "": "",
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "Sobre nosotros",
                slug: "about"
              }, {
                name: "Nuestros juegos",
                slug: "games",
                dropdown: [{
                  name: "Guild Wars 2",
                  slug: "https://www.guildwars2.com/es/"
                }, {
                  name: "Guild Wars",
                  slug: "https://www.guildwars.com/es/"
                }]
              }, {
                name: "Carrera",
                slug: "careers"
              }, {
                name: "Contacto",
                slug: "contact"
              }],
              shoplink: {
                name: "Productos",
                slug: "https://www.guildwars2.com/es/shop/"
              },
              supportlink: {
                name: "Ayuda",
                slug: "https://help.guildwars2.com"
              }
            },
            misc: {
              buttons: {
                labels: {
                  next: "Siguiente",
                  prev: "Anterior",
                  openmenu: "Men\xfa",
                  close: "Cerrar",
                  play: "Reproducir",
                  readmore: "Seguir leyendo"
                }
              }
            },
            footer: {
              followUs: "S\xedguenos",
              socials: {
                youtube: {
                  label: "YouTube",
                  href: "https://www.youtube.com/arenanet"
                },
                facebook: {
                  label: "Facebook",
                  href: "https://www.facebook.com/ArenaNet/"
                },
                twitter: {
                  label: "Twitter",
                  href: "https://twitter.com/ArenaNet"
                },
                twitch: {
                  label: "Twitch",
                  href: "https://twitch.tv/guildwars2"
                },
                instagram: {
                  label: "Instagram",
                  href: "https://instagram.com/arenanet"
                },
                tumblr: {
                  label: "Tumblr",
                  href: "https://guildwars2.tumblr.com"
                },
                flickr: {
                  label: "Flickr",
                  href: "https://flickr.com/photos/arenanet"
                }
              },
              links: {
                cookiepreferences: "Preferencias de cookies",
                gw2: {
                  privacy: "Pol\xedtica de privacidad",
                  legal: "Documentos legales"
                },
                gw1: {
                  partners: "Socios",
                  legal: "Documentos legales",
                  privacy: "Pol\xedtica de privacidad"
                }
              },
              esrb: {
                gw2: {
                  upper: "Blood and Gore, Language, Use of Alcohol, Violence",
                  lower: "In-Game Purchases, Users Interact"
                },
                gw1: {
                  upper: "Animaci\xf3n de sangre, Temas insinuantes moderados, Violencia, Uso de alcohol"
                }
              },
              pegi: {
                provisional: "Provisional"
              },
              ad: {
                label: "Comprar ahora"
              }
            }
          },
          fr: {
            "": "",
            nav: {
              logoTitle: "ArenaNet",
              navlinks: [{
                name: "Qui nous sommes",
                slug: "about"
              }, {
                name: "Nos jeux",
                slug: "games",
                dropdown: [{
                  name: "Guild Wars 2",
                  slug: "https://www.guildwars2.com/fr/"
                }, {
                  name: "Guild Wars",
                  slug: "https://www.guildwars.com/fr/"
                }]
              }, {
                name: "Emplois",
                slug: "careers"
              }, {
                name: "Contact",
                slug: "contact"
              }],
              shoplink: {
                name: "Produits d\xe9riv\xe9s",
                slug: "https://www.guildwars2.com/fr/shop/"
              },
              supportlink: {
                name: "Assistance",
                slug: "https://help.guildwars2.com"
              }
            },
            misc: {
              buttons: {
                labels: {
                  next: "Suivant",
                  prev: "Pr\xe9c\xe9dent",
                  openmenu: "Menu",
                  close: "Fermer",
                  play: "Regarder",
                  readmore: "En savoir plus"
                }
              }
            },
            footer: {
              followUs: "Suivez-Nous",
              socials: {
                youtube: {
                  label: "YouTube",
                  href: "https://www.youtube.com/arenanet"
                },
                facebook: {
                  label: "Facebook",
                  href: "https://www.facebook.com/ArenaNet/"
                },
                twitter: {
                  label: "Twitter",
                  href: "https://twitter.com/ArenaNet"
                },
                twitch: {
                  label: "Twitch",
                  href: "https://twitch.tv/guildwars2"
                },
                instagram: {
                  label: "Instagram",
                  href: "https://instagram.com/arenanet"
                },
                tumblr: {
                  label: "Tumblr",
                  href: "https://guildwars2.tumblr.com"
                },
                flickr: {
                  label: "Flickr",
                  href: "https://flickr.com/photos/arenanet"
                }
              },
              links: {
                cookiepreferences: "Pr\xe9f\xe9rences cookie",
                gw2: {
                  privacy: "Charte de confidentialit\xe9",
                  legal: "Mentions L\xe9gales"
                },
                gw1: {
                  partners: "Partenaires",
                  legal: "Mentions L\xe9gales",
                  privacy: "Charte de confidentialit\xe9"
                }
              },
              esrb: {
                gw2: {
                  upper: "Blood and Gore, Language, Use of Alcohol, Violence",
                  lower: "In-Game Purchases, Users Interact"
                },
                gw1: {
                  upper: "Sang anim\xe9, Th\xe8mes suggestifs mod\xe9r\xe9s, Violence, Consommation d'alcool"
                }
              },
              pegi: {
                provisional: "Provisoire"
              },
              ad: {
                label: "Acheter maintenant"
              }
            }
          },
          "en-gb": {
            "": "",
            nav: {
              navlinks: [{
                name: " About Us",
                slug: "about"
              }, {
                name: "Our Games",
                slug: "games",
                dropdown: [{
                  name: "Guild Wars 2",
                  slug: "https://www.guildwars2.com/en-gb/"
                }, {
                  name: "Guild Wars",
                  slug: "https://www.guildwars.com"
                }]
              }, {
                name: "Careers",
                slug: "careers"
              }, {
                name: "Contact",
                slug: "contact"
              }],
              shoplink: {
                name: "Merchandise",
                slug: "https://www.guildwars2.com/en-gb/shop/"
              },
              supportlink: {
                name: "Support",
                slug: "https://help.guildwars2.com"
              }
            },
            misc: {
              buttons: {
                labels: {
                  next: "Next",
                  prev: "Previous",
                  openmenu: "Menu",
                  close: "Close",
                  play: "Play Video",
                  readmore: "Read More"
                }
              }
            },
            footer: {
              followUs: "Follow Us",
              socials: {
                youtube: {
                  label: "YouTube",
                  href: "https://www.youtube.com/arenanet"
                },
                facebook: {
                  label: "Facebook",
                  href: "https://www.facebook.com/ArenaNet/"
                },
                twitter: {
                  label: "Twitter",
                  href: "https://twitter.com/ArenaNet"
                },
                twitch: {
                  label: "Twitch",
                  href: "https://twitch.tv/guildwars2"
                },
                instagram: {
                  label: "Instagram",
                  href: "https://instagram.com/arenanet"
                },
                tumblr: {
                  label: "Tumblr",
                  href: "https://guildwars2.tumblr.com"
                },
                flickr: {
                  label: "Flickr",
                  href: "https://flickr.com/photos/arenanet"
                }
              },
              links: {
                cookiepreferences: "Cookie Preferences",
                gw2: {
                  privacy: "Privacy Policy",
                  legal: "Legal Documentation"
                },
                gw1: {
                  partners: "Partners",
                  legal: "Legal Documentation",
                  privacy: "Privacy Policy"
                }
              },
              esrb: {
                gw2: {
                  upper: "Blood and Gore, Language, Use of Alcohol, Violence",
                  lower: "In-Game Purchases, Users Interact"
                },
                gw1: {
                  upper: "Animated Blood, Mild Suggestive Themes, Violence, Use of Alcohol"
                }
              },
              pegi: {
                provisional: "Provisional"
              },
              ad: {
                label: "Buy Now"
              }
            }
          }
        }
      },
      453: e => {
        "use strict";
        e.exports = JSON.parse('{"dimebar":{"forums":{"en":"https://en-forum.guildwars2.com","de":"https://de-forum.guildwars2.com","es":"https://es-forum.guildwars2.com","fr":"https://fr-forum.guildwars2.com","en-gb":"https://en-forum.guildwars2.com"},"support":{"en":"https://help.guildwars2.com/hc/en","de":"https://help.guildwars2.com/hc/de","es":"https://help.guildwars2.com/hc/es","fr":"https://help.guildwars2.com/hc/fr","en-gb":"https://help.guildwars2.com/hc/en"},"wiki":{"en":"https://wiki-en.guildwars2.com","de":"https://wiki-de.guildwars2.com","es":"https://wiki-es.guildwars2.com","fr":"https://wiki-fr.guildwars2.com","en-gb":"https://wiki-en.guildwars2.com"},"login":{"en":"https://account.arena.net","de":"https://account.arena.net","es":"https://account.arena.net","fr":"https://account.arena.net","en-gb":"https://account.arena.net"}},"download":"https://account.arena.net/welcome","socials":{"youtube":{"en":"https://www.youtube.com/GuildWars2","de":"https://www.youtube.com/GuildWars2","es":"https://www.youtube.com/GuildWars2","fr":"https://www.youtube.com/GuildWars2","en-gb":"https://www.youtube.com/GuildWars2"},"facebook":{"en":"https://www.facebook.com/GuildWars2","de":"https://www.facebook.com/GuildWars2","es":"https://www.facebook.com/GuildWars2","fr":"https://www.facebook.com/GuildWars2","en-gb":"https://www.facebook.com/GuildWars2"},"twitter":{"en":"https://twitter.com/GuildWars2","de":"https://twitter.com/GuildWars2_DE","es":"https://twitter.com/GuildWars2_ES","fr":"https://twitter.com/GuildWars2_FR","en-gb":"https://twitter.com/GuildWars2"},"twitch":{"en":"https://twitch.tv/guildwars2","de":"https://twitch.tv/guildwars2","es":"https://twitch.tv/guildwars2","fr":"https://twitch.tv/guildwars2","en-gb":"https://twitch.tv/guildwars2"},"instagram":{"en":"https://instagram.com/guildwars2","de":"https://instagram.com/guildwars2","es":"https://instagram.com/guildwars2","fr":"https://instagram.com/guildwars2","en-gb":"https://instagram.com/guildwars2"},"tumblr":{"en":"https://guildwars2.tumblr.com","de":"https://guildwars2.tumblr.com","es":"https://guildwars2.tumblr.com","fr":"https://guildwars2.tumblr.com","en-gb":"https://guildwars2.tumblr.com"},"flickr":{"en":"https://www.flickr.com/photos/arenanet","de":"https://www.flickr.com/photos/arenanet","es":"https://www.flickr.com/photos/arenanet","fr":"https://www.flickr.com/photos/arenanet","en-gb":"https://www.flickr.com/photos/arenanet"}},"footer":{"gw2":{"privacy":"https://arena.net/legal/privacy-policy","legal":"https://arena.net/legal"},"gw1":{"partners":"/{lang}/partners","privacy":"/{lang}/privacy-policy","legal":"https://arena.net/legal"}}}')
      },
      649: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = n(894);
        e.exports = {
          view: e => r("div", {
            class: a.rating,
            "data-test": "usk-rating"
          }, r("a", {
            class: a.usk,
            href: "https://www.usk.de",
            target: "_blank",
            "aria-label": "usk"
          }, "usk"))
        }
      },
      716: e => {
        e.exports = {
          en: {
            copyright: "\xa9{year} ArenaNet, LLC. All rights reserved. All trademarks are the property of their respective owners."
          },
          de: {
            copyright: "\xa9{year} ArenaNet, LLC. Alle Rechte vorbehalten. Alle Warenzeichen sind das Eigentum ihrer jeweiligen Besitzer."
          },
          es: {
            copyright: "\xa9{year} ArenaNet, LLC. Reservados todos los derechos. Todas las marcas comerciales son propiedad de sus respectivos due\xf1os."
          },
          fr: {
            copyright: "\xa9{year} ArenaNet, LLC. Tous droits r\xe9serv\xe9s. Toutes les marques d\xe9pos\xe9es sont la propri\xe9t\xe9 de leurs propri\xe9taires respectifs."
          },
          "en-gb": {
            copyright: "\xa9{year} ArenaNet, LLC. All rights reserved. All trademarks are the property of their respective owners."
          }
        }
      },
      887: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = n(204),
          o = n(246),
          i = n(10),
          l = n(453),
          s = ["forums", "wiki"];
        e.exports = {
          oninit(e) {
            const {
              lang: t,
              langs: n
            } = e.attrs, r = 0 === t.indexOf("en-") ? "en" : t, a = i[r] || i.en;
            e.state.i18nLang = r, e.state.i18n = a, e.state.otherLangs = n.filter((e => e !== t)), e.state.dimebarLeft = a.nav.navlinks, e.state.dimebarLeftKeys = Object.keys(e.state.dimebarLeft), e.state.dimebarRight = a.nav.dimebar, e.state.dimebarRightKeys = Object.keys(e.state.dimebarRight)
          },
          oncreate() {
            o.clickTracker(), document.dispatchEvent(new Event("anetdimebar-loaded"))
          },
          view(e) {
            const {
              pageName: t,
              excludeDimebar: n,
              position: o,
              opacity: i,
              lang: c
            } = e.attrs, {
              dimebarLeft: u,
              dimebarLeftKeys: f,
              dimebarRight: d,
              dimebarRightKeys: p,
              otherLangs: g,
              i18n: m,
              i18nLang: h
            } = e.state;
            let {
              pathname: w
            } = window.location;
            return r("nav", {
              class: "absolute" === o ? a.anetDimebarAbs : a.anetDimebar,
              "data-title": m.logoTitle,
              "aria-label": "ArenaNet Menu",
              "data-test": "dimebar",
              style: `opacity:${i||1}`
            }, r("div", {
              class: a.wrapper
            }, r("div", {
              class: a.primaryNav
            }, r("a", {
              class: a.anetLogo,
              href: `https://www.arena.net/${h}`,
              "data-ga-event": "",
              "data-ga-category": "Header"
            }, r("img", {
              src: "https://services.staticwars.com/services/2bumpers/img/arenanet-color.34ce7b81-svc.svg",
              alt: "ArenaNet"
            })), f.map((e => r("a", {
              href: `https://www.arena.net/${h}/${u[e].slug}`,
              "data-ga-event": "",
              "data-ga-category": "Header",
              "data-selected": t === u[e].slug ? "current" : ""
            }, u[e].name))), r("a", {
              href: `${m.nav.shoplink.slug}`,
              target: "_blank",
              rel: "noreferrer",
              "data-ga-event": "",
              "data-ga-category": "Header"
            }, m.nav.shoplink.name)), r("ul", {
              class: a.secondaryNav
            }, n ? null : p.filter((t => {
              const n = !1 === e.attrs[t],
                r = !l.dimebar[t] && !e.attrs[t];
              return !(n || r)
            })).map((t => {
              const n = Object.assign({
                "data-ga-event": "",
                "data-ga-category": "dimebar",
                "data-test": t
              }, e.attrs[t] || {
                href: l.dimebar[t]?.[h] || e.attrs[t],
                target: "_blank",
                rel: "noopener"
              });
              let o = d[t];
              return "login" !== t || window.location.href.includes("account") || e.attrs.login || (o = d.account), r("li", {
                class: s.includes(t) ? a.hideable : ""
              }, r("a", n, o))
            })), g.length ? r("li", {
              class: a.langSelectBar
            }, r("a", {
              class: a.currentLang,
              onmouseover() {
                w = window.location.pathname
              }
            }, c), g.map((e => r("a", {
              href: w.replace(c, e)
            }, e)))) : null)))
          }
        }
      },
      894: (e, t, n) => {
        "use strict";
        n.r(t), n.d(t, {
          anet: () => C,
          anetpof: () => N,
          default: () => j,
          esrb: () => L,
          facebook: () => d,
          flickr: () => w,
          followUs: () => c,
          footer: () => r,
          footerLight: () => o,
          halfFooter: () => a,
          instagram: () => m,
          legalFooter: () => y,
          logo: () => A,
          logos: () => k,
          navChildBar: () => l,
          navCleanup: () => P,
          nc: () => x,
          ncFooter: () => F,
          pageFooterNav: () => i,
          pageFooterNavContainer: () => E,
          pegi: () => _,
          pof: () => b,
          rating: () => S,
          rss: () => v,
          socialBar: () => s,
          socialIcon: () => u,
          tumblr: () => h,
          twitch: () => g,
          twitter: () => p,
          usk: () => T,
          youtube: () => f
        });
        const r = "mc7ff6cbbf_footer",
          a = r + " mc7ff6cbbf_halfFooter",
          o = "mc7ff6cbbf_footerLight",
          i = "mc7ff6cbbf_pageFooterNav",
          l = "mc7ff6cbbf_navChildBar",
          s = "mc7ff6cbbf_socialBar",
          c = "mc7ff6cbbf_followUs",
          u = "mc7ff6cbbf_socialIcon",
          f = u + " mc7ff6cbbf_youtube",
          d = u + " mc7ff6cbbf_facebook",
          p = u + " mc7ff6cbbf_twitter",
          g = u + " mc7ff6cbbf_twitch",
          m = u + " mc7ff6cbbf_instagram",
          h = u + " mc7ff6cbbf_tumblr",
          w = u + " mc7ff6cbbf_flickr",
          v = u + " mc7ff6cbbf_rss",
          b = "mc7ff6cbbf_pof",
          y = "mc7ff6cbbf_legalFooter",
          k = "mc7ff6cbbf_logos",
          A = "mc7ff6cbbf_logo",
          x = A + " mc7ff6cbbf_nc",
          C = A + " mc7ff6cbbf_anet",
          N = C + " mc7ff6cbbf_anetpof",
          S = "mc7ff6cbbf_rating",
          _ = "mc7ff6cbbf_pegi",
          L = "mc7ff6cbbf_esrb",
          T = "mc7ff6cbbf_usk",
          P = "mc7ff6cbbf_navCleanup",
          F = "mc7ff6cbbf_ncFooter",
          E = "mc7ff6cbbf_pageFooterNavContainer",
          j = {
            footer: r,
            halfFooter: a,
            footerLight: o,
            pageFooterNav: i,
            navChildBar: l,
            socialBar: s,
            followUs: c,
            socialIcon: u,
            youtube: f,
            facebook: d,
            twitter: p,
            twitch: g,
            instagram: m,
            tumblr: h,
            flickr: w,
            rss: v,
            pof: b,
            legalFooter: y,
            logos: k,
            logo: A,
            nc: x,
            anet: C,
            anetpof: N,
            rating: S,
            pegi: _,
            esrb: L,
            usk: T,
            navCleanup: P,
            ncFooter: F,
            pageFooterNavContainer: E
          }
      },
      980: (e, t, n) => {
        "use strict";
        const r = n(114),
          a = "data-mount",
          o = document.documentElement.getAttribute("data-rating") || "esrb",
          i = document.documentElement.lang.toLowerCase(),
          l = document.querySelectorAll("link[hreflang]"),
          s = l.length ? [] : ["en", "de", "es", "fr"],
          c = {
            lang: i.slice(0, 2),
            langs: s,
            rating: o,
            curDate: (new Date).getFullYear()
          };
        for (let e = 0; e < l.length; e++) {
          const t = l[e].getAttribute("hreflang");
          s.includes(t) || "x-default" === t || s.push(t)
        }
        e.exports = function(e) {
          (e = Array.isArray(e) ? e : [e]).forEach((({
            component: e,
            attrs: t = {},
            name: n
          }) => {
            const o = document.querySelector(`[${a}=${n}]`) || function(e) {
              const t = document.createElement("div");
              return t.setAttribute(a, e), "anetdimebar" === e ? document.body.prepend(t) : document.body.append(t), t
            }(n);
            r.mount(o, {
              view: () => r(e, Object.assign({}, c, t))
            })
          }))
        }
      }
    },
    t = {};

  function n(r) {
    var a = t[r];
    if (void 0 !== a) return a.exports;
    var o = t[r] = {
      exports: {}
    };
    return e[r](o, o.exports, n), o.exports
  }
  n.d = (e, t) => {
    for (var r in t) n.o(t, r) && !n.o(e, r) && Object.defineProperty(e, r, {
      enumerable: !0,
      get: t[r]
    })
  }, n.g = function() {
    if ("object" == typeof globalThis) return globalThis;
    try {
      return this || new Function("return this")()
    } catch (e) {
      if ("object" == typeof window) return window
    }
  }(), n.o = (e, t) => Object.prototype.hasOwnProperty.call(e, t), n.r = e => {
    "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {
      value: "Module"
    }), Object.defineProperty(e, "__esModule", {
      value: !0
    })
  }, (() => {
    "use strict";
    const e = n(980),
      t = n(887),
      r = n(301);
    e([{
      name: "anetdimebar",
      component: t,
      attrs: window.anetDimebarAttrs
    }, {
      name: "anetfooter",
      component: r,
      attrs: window.anetFooterAttrs
    }])
  })()
})();
//# sourceMappingURL=index.js.map