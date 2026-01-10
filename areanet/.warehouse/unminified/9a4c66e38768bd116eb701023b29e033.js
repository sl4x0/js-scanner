/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("dom-base", function(D) {
  (function(J) {
    var T = "nodeType",
      G = "ownerDocument",
      F = "documentElement",
      E = "defaultView",
      L = "parentWindow",
      O = "tagName",
      Q = "parentNode",
      S = "firstChild",
      N = "previousSibling",
      R = "nextSibling",
      M = "contains",
      I = "compareDocumentPosition",
      H = "",
      P = J.config.doc.documentElement,
      K = /<([a-z]+)/i;
    J.DOM = {
      byId: function(V, U) {
        return J.DOM.allById(V, U)[0] || null;
      },
      children: function(W, U) {
        var V = [];
        if (W) {
          U = U || "*";
          V = J.Selector.query("> " + U, W);
        }
        return V;
      },
      firstByTag: function(U, V) {
        var W;
        V = V || J.config.doc;
        if (U && V.getElementsByTagName) {
          W = V.getElementsByTagName(U)[0];
        }
        return W || null;
      },
      getText: (P.textContent !== undefined) ? function(V) {
        var U = "";
        if (V) {
          U = V.textContent;
        }
        return U || "";
      } : function(V) {
        var U = "";
        if (V) {
          U = V.innerText;
        }
        return U || "";
      },
      setText: (P.textContent !== undefined) ? function(U, V) {
        if (U) {
          U.textContent = V;
        }
      } : function(U, V) {
        if (U) {
          U.innerText = V;
        }
      },
      previous: function(U, W, V) {
        return J.DOM.elementByAxis(U, N, W, V);
      },
      next: function(U, W, V) {
        return J.DOM.elementByAxis(U, R, W, V);
      },
      ancestor: function(V, W, X) {
        var U = null;
        if (X) {
          U = (!W || W(V)) ? V : null;
        }
        return U || J.DOM.elementByAxis(V, Q, W, null);
      },
      elementByAxis: function(U, X, W, V) {
        while (U && (U = U[X])) {
          if ((V || U[O]) && (!W || W(U))) {
            return U;
          }
        }
        return null;
      },
      contains: function(V, W) {
        var U = false;
        if (!W || !V || !W[T] || !V[T]) {
          U = false;
        } else {
          if (V[M]) {
            if (J.UA.opera || W[T] === 1) {
              U = V[M](W);
            } else {
              U = J.DOM._bruteContains(V, W);
            }
          } else {
            if (V[I]) {
              if (V === W || !!(V[I](W) & 16)) {
                U = true;
              }
            }
          }
        }
        return U;
      },
      inDoc: function(W, X) {
        var V = false,
          U;
        if (W && W.nodeType) {
          (X) || (X = W[G]);
          U = X[F];
          if (U && U.contains && W.tagName) {
            V = U.contains(W);
          } else {
            V = J.DOM.contains(U, W);
          }
        }
        return V;
      },
      allById: function(Z, U) {
        U = U || J.config.doc;
        var V = [],
          W = [],
          X, Y;
        if (U.querySelectorAll) {
          W = U.querySelectorAll('[id="' + Z + '"]');
        } else {
          if (U.all) {
            V = U.all(Z);
            if (V && V.nodeType) {
              V = [V];
            }
            if (V && V.length) {
              for (X = 0; Y = V[X++];) {
                if (Y.attributes && Y.attributes.id && Y.attributes.id.value === Z) {
                  W.push(Y);
                }
              }
            }
          } else {
            W = [J.DOM._getDoc(U).getElementById(Z)];
          }
        }
        return W;
      },
      create: function(Z, b) {
        if (typeof Z === "string") {
          Z = J.Lang.trim(Z);
        }
        b = b || J.config.doc;
        var V = K.exec(Z),
          Y = J.DOM._create,
          a = J.DOM.creators,
          X = null,
          U, W;
        if (Z != undefined) {
          if (V && a[V[1]]) {
            if (typeof a[V[1]] === "function") {
              Y = a[V[1]];
            } else {
              U = a[V[1]];
            }
          }
          W = Y(Z, b, U).childNodes;
          if (W.length === 1) {
            X = W[0].parentNode.removeChild(W[0]);
          } else {
            if (W[0] && W[0].className === "yui3-big-dummy") {
              if (W.length === 2) {
                X = W[0].nextSibling;
              } else {
                W[0].parentNode.removeChild(W[0]);
                X = J.DOM._nl2frag(W, b);
              }
            } else {
              X = J.DOM._nl2frag(W, b);
            }
          }
        }
        return X;
      },
      _nl2frag: function(V, Y) {
        var W = null,
          X, U;
        if (V && (V.push || V.item) && V[0]) {
          Y = Y || V[0].ownerDocument;
          W = Y.createDocumentFragment();
          if (V.item) {
            V = J.Array(V, 0, true);
          }
          for (X = 0, U = V.length; X < U; X++) {
            W.appendChild(V[X]);
          }
        }
        return W;
      },
      CUSTOM_ATTRIBUTES: (!P.hasAttribute) ? {
        "for": "htmlFor",
        "class": "className"
      } : {
        "htmlFor": "for",
        "className": "class"
      },
      setAttribute: function(W, U, X, V) {
        if (W && W.setAttribute) {
          U = J.DOM.CUSTOM_ATTRIBUTES[U] || U;
          W.setAttribute(U, X, V);
        }
      },
      getAttribute: function(X, U, W) {
        W = (W !== undefined) ? W : 2;
        var V = "";
        if (X && X.getAttribute) {
          U = J.DOM.CUSTOM_ATTRIBUTES[U] || U;
          V = X.getAttribute(U, W);
          if (V === null) {
            V = "";
          }
        }
        return V;
      },
      isWindow: function(U) {
        return U.alert && U.document;
      },
      _fragClones: {},
      _create: function(V, W, U) {
        U = U || "div";
        var X = J.DOM._fragClones[U];
        if (X) {
          X = X.cloneNode(false);
        } else {
          X = J.DOM._fragClones[U] = W.createElement(U);
        }
        X.innerHTML = V;
        return X;
      },
      _removeChildNodes: function(U) {
        while (U.firstChild) {
          U.removeChild(U.firstChild);
        }
      },
      addHTML: function(Y, X, V) {
        var U = Y.parentNode,
          W;
        if (X !== undefined && X !== null) {
          if (X.nodeType) {
            W = X;
          } else {
            W = J.DOM.create(X);
          }
        }
        if (V) {
          if (V.nodeType) {
            V.parentNode.insertBefore(W, V);
          } else {
            switch (V) {
              case "replace":
                while (Y.firstChild) {
                  Y.removeChild(Y.firstChild);
                }
                if (W) {
                  Y.appendChild(W);
                }
                break;
              case "before":
                U.insertBefore(W, Y);
                break;
              case "after":
                if (Y.nextSibling) {
                  U.insertBefore(W, Y.nextSibling);
                } else {
                  U.appendChild(W);
                }
                break;
              default:
                Y.appendChild(W);
            }
          }
        } else {
          Y.appendChild(W);
        }
        return W;
      },
      VALUE_SETTERS: {},
      VALUE_GETTERS: {},
      getValue: function(W) {
        var V = "",
          U;
        if (W && W[O]) {
          U = J.DOM.VALUE_GETTERS[W[O].toLowerCase()];
          if (U) {
            V = U(W);
          } else {
            V = W.value;
          }
        }
        if (V === H) {
          V = H;
        }
        return (typeof V === "string") ? V : "";
      },
      setValue: function(U, V) {
        var W;
        if (U && U[O]) {
          W = J.DOM.VALUE_SETTERS[U[O].toLowerCase()];
          if (W) {
            W(U, V);
          } else {
            U.value = V;
          }
        }
      },
      siblings: function(X, W) {
        var U = [],
          V = X;
        while ((V = V[N])) {
          if (V[O] && (!W || W(V))) {
            U.unshift(V);
          }
        }
        V = X;
        while ((V = V[R])) {
          if (V[O] && (!W || W(V))) {
            U.push(V);
          }
        }
        return U;
      },
      _bruteContains: function(U, V) {
        while (V) {
          if (U === V) {
            return true;
          }
          V = V.parentNode;
        }
        return false;
      },
      _getRegExp: function(V, U) {
        U = U || "";
        J.DOM._regexCache = J.DOM._regexCache || {};
        if (!J.DOM._regexCache[V + U]) {
          J.DOM._regexCache[V + U] = new RegExp(V, U);
        }
        return J.DOM._regexCache[V + U];
      },
      _getDoc: function(U) {
        var V = J.config.doc;
        if (U) {
          V = (U[T] === 9) ? U : U[G] || U.document || J.config.doc;
        }
        return V;
      },
      _getWin: function(U) {
        var V = J.DOM._getDoc(U);
        return V[E] || V[L] || J.config.win;
      },
      _batch: function(X, b, a, W, V, Z) {
        b = (typeof name === "string") ? J.DOM[b] : b;
        var U, Y = [];
        if (b && X) {
          J.each(X, function(c) {
            if ((U = b.call(J.DOM, c, a, W, V, Z)) !== undefined) {
              Y[Y.length] = U;
            }
          });
        }
        return Y.length ? Y : X;
      },
      creators: {},
      _IESimpleCreate: function(U, V) {
        V = V || J.config.doc;
        return V.createElement(U);
      }
    };
    (function(Z) {
      var a = Z.DOM.creators,
        U = Z.DOM.create,
        X = /(?:\/(?:thead|tfoot|tbody|caption|col|colgroup)>)+\s*<tbody/,
        W = "<table>",
        V = "</table>";
      if (Z.UA.ie) {
        Z.mix(a, {
          tbody: function(b, c) {
            var d = U(W + b + V, c),
              Y = d.children.tags("tbody")[0];
            if (d.children.length > 1 && Y && !X.test(b)) {
              Y[Q].removeChild(Y);
            }
            return d;
          },
          script: function(Y, b) {
            var c = b.createElement("div");
            c.innerHTML = "-" + Y;
            c.removeChild(c[S]);
            return c;
          }
        }, true);
        Z.mix(Z.DOM.VALUE_GETTERS, {
          button: function(Y) {
            return (Y.attributes && Y.attributes.value) ? Y.attributes.value.value : "";
          }
        });
        Z.mix(Z.DOM.VALUE_SETTERS, {
          button: function(b, c) {
            var Y = b.attributes.value;
            if (!Y) {
              Y = b[G].createAttribute("value");
              b.setAttributeNode(Y);
            }
            Y.value = c;
          },
          select: function(d, e) {
            for (var b = 0, Y = d.getElementsByTagName("option"), c; c = Y[b++];) {
              if (Z.DOM.getValue(c) === e) {
                Z.DOM.setAttribute(c, "selected", true);
                break;
              }
            }
          }
        });
        Z.DOM.creators.style = Z.DOM.creators.script;
      }
      if (Z.UA.gecko || Z.UA.ie) {
        Z.mix(a, {
          option: function(Y, b) {
            return U('<select><option class="yui3-big-dummy" selected></option>' + Y + "</select>", b);
          },
          tr: function(Y, b) {
            return U("<tbody>" + Y + "</tbody>", b);
          },
          td: function(Y, b) {
            return U("<tr>" + Y + "</tr>", b);
          },
          tbody: function(Y, b) {
            return U(W + Y + V, b);
          }
        });
        Z.mix(a, {
          legend: "fieldset",
          th: a.td,
          thead: a.tbody,
          tfoot: a.tbody,
          caption: a.tbody,
          colgroup: a.tbody,
          col: a.tbody,
          optgroup: a.option
        });
      }
      Z.mix(Z.DOM.VALUE_GETTERS, {
        option: function(b) {
          var Y = b.attributes;
          return (Y.value && Y.value.specified) ? b.value : b.text;
        },
        select: function(b) {
          var c = b.value,
            Y = b.options;
          if (Y && Y.length && c === "") {
            if (b.multiple) {} else {
              c = Z.DOM.getValue(Y[b.selectedIndex]);
            }
          }
          return c;
        }
      });
    })(J);
  })(D);
  var B, A, C;
  D.mix(D.DOM, {
    hasClass: function(G, F) {
      var E = D.DOM._getRegExp("(?:^|\\s+)" + F + "(?:\\s+|$)");
      return E.test(G.className);
    },
    addClass: function(F, E) {
      if (!D.DOM.hasClass(F, E)) {
        F.className = D.Lang.trim([F.className, E].join(" "));
      }
    },
    removeClass: function(F, E) {
      if (E && A(F, E)) {
        F.className = D.Lang.trim(F.className.replace(D.DOM._getRegExp("(?:^|\\s+)" + E + "(?:\\s+|$)"), " "));
        if (A(F, E)) {
          C(F, E);
        }
      }
    },
    replaceClass: function(F, E, G) {
      C(F, E);
      B(F, G);
    },
    toggleClass: function(F, E, G) {
      var H = (G !== undefined) ? G : !(A(F, E));
      if (H) {
        B(F, E);
      } else {
        C(F, E);
      }
    }
  });
  A = D.DOM.hasClass;
  C = D.DOM.removeClass;
  B = D.DOM.addClass;
  D.mix(D.DOM, {
    setWidth: function(F, E) {
      D.DOM._setSize(F, "width", E);
    },
    setHeight: function(F, E) {
      D.DOM._setSize(F, "height", E);
    },
    _setSize: function(F, H, G) {
      G = (G > 0) ? G : 0;
      var E = 0;
      F.style[H] = G + "px";
      E = (H === "height") ? F.offsetHeight : F.offsetWidth;
      if (E > G) {
        G = G - (E - G);
        if (G < 0) {
          G = 0;
        }
        F.style[H] = G + "px";
      }
    }
  });
}, "3.2.0", {
  requires: ["oop"]
});
YUI.add("dom-style", function(A) {
  (function(E) {
    var O = "documentElement",
      B = "defaultView",
      N = "ownerDocument",
      H = "style",
      I = "float",
      Q = "cssFloat",
      R = "styleFloat",
      K = "transparent",
      D = "getComputedStyle",
      C = "getBoundingClientRect",
      G = E.config.doc,
      S = undefined,
      P = E.DOM,
      F = "transform",
      L = ["WebkitTransform", "MozTransform", "OTransform"],
      M = /color$/i,
      J = /width|height|top|left|right|bottom|margin|padding/i;
    E.Array.each(L, function(T) {
      if (T in G[O].style) {
        F = T;
      }
    });
    E.mix(P, {
      DEFAULT_UNIT: "px",
      CUSTOM_STYLES: {},
      setStyle: function(W, T, Y, V) {
        V = V || W.style;
        var U = P.CUSTOM_STYLES,
          X;
        if (V) {
          if (Y === null || Y === "") {
            Y = "";
          } else {
            if (!isNaN(new Number(Y)) && J.test(T)) {
              Y += P.DEFAULT_UNIT;
            }
          }
          if (T in U) {
            if (U[T].set) {
              U[T].set(W, Y, V);
              return;
            } else {
              if (typeof U[T] === "string") {
                T = U[T];
              }
            }
          }
          V[T] = Y;
        }
      },
      getStyle: function(W, T, V) {
        V = V || W.style;
        var U = P.CUSTOM_STYLES,
          X = "";
        if (V) {
          if (T in U) {
            if (U[T].get) {
              return U[T].get(W, T, V);
            } else {
              if (typeof U[T] === "string") {
                T = U[T];
              }
            }
          }
          X = V[T];
          if (X === "") {
            X = P[D](W, T);
          }
        }
        return X;
      },
      setStyles: function(U, V) {
        var T = U.style;
        E.each(V, function(W, X) {
          P.setStyle(U, X, W, T);
        }, P);
      },
      getComputedStyle: function(U, T) {
        var W = "",
          V = U[N];
        if (U[H]) {
          W = V[B][D](U, null)[T];
        }
        return W;
      }
    });
    if (G[O][H][Q] !== S) {
      P.CUSTOM_STYLES[I] = Q;
    } else {
      if (G[O][H][R] !== S) {
        P.CUSTOM_STYLES[I] = R;
      }
    }
    if (E.UA.opera) {
      P[D] = function(V, U) {
        var T = V[N][B],
          W = T[D](V, "")[U];
        if (M.test(U)) {
          W = E.Color.toRGB(W);
        }
        return W;
      };
    }
    if (E.UA.webkit) {
      P[D] = function(V, U) {
        var T = V[N][B],
          W = T[D](V, "")[U];
        if (W === "rgba(0, 0, 0, 0)") {
          W = K;
        }
        return W;
      };
    }
    E.DOM._getAttrOffset = function(X, U) {
      var Z = E.DOM[D](X, U),
        W = X.offsetParent,
        T, V, Y;
      if (Z === "auto") {
        T = E.DOM.getStyle(X, "position");
        if (T === "static" || T === "relative") {
          Z = 0;
        } else {
          if (W && W[C]) {
            V = W[C]()[U];
            Y = X[C]()[U];
            if (U === "left" || U === "top") {
              Z = Y - V;
            } else {
              Z = V - X[C]()[U];
            }
          }
        }
      }
      return Z;
    };
    E.DOM._getOffset = function(T) {
      var V, U = null;
      if (T) {
        V = P.getStyle(T, "position");
        U = [parseInt(P[D](T, "left"), 10), parseInt(P[D](T, "top"), 10)];
        if (isNaN(U[0])) {
          U[0] = parseInt(P.getStyle(T, "left"), 10);
          if (isNaN(U[0])) {
            U[0] = (V === "relative") ? 0 : T.offsetLeft || 0;
          }
        }
        if (isNaN(U[1])) {
          U[1] = parseInt(P.getStyle(T, "top"), 10);
          if (isNaN(U[1])) {
            U[1] = (V === "relative") ? 0 : T.offsetTop || 0;
          }
        }
      }
      return U;
    };
    P.CUSTOM_STYLES.transform = {
      set: function(U, V, T) {
        T[F] = V;
      },
      get: function(U, T) {
        return P[D](U, F);
      }
    };
  })(A);
  (function(D) {
    var B = parseInt,
      C = RegExp;
    D.Color = {
      KEYWORDS: {
        black: "000",
        silver: "c0c0c0",
        gray: "808080",
        white: "fff",
        maroon: "800000",
        red: "f00",
        purple: "800080",
        fuchsia: "f0f",
        green: "008000",
        lime: "0f0",
        olive: "808000",
        yellow: "ff0",
        navy: "000080",
        blue: "00f",
        teal: "008080",
        aqua: "0ff"
      },
      re_RGB: /^rgb\(([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\)$/i,
      re_hex: /^#?([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})$/i,
      re_hex3: /([0-9A-F])/gi,
      toRGB: function(E) {
        if (!D.Color.re_RGB.test(E)) {
          E = D.Color.toHex(E);
        }
        if (D.Color.re_hex.exec(E)) {
          E = "rgb(" + [B(C.$1, 16), B(C.$2, 16), B(C.$3, 16)].join(", ") + ")";
        }
        return E;
      },
      toHex: function(F) {
        F = D.Color.KEYWORDS[F] || F;
        if (D.Color.re_RGB.exec(F)) {
          F = [Number(C.$1).toString(16), Number(C.$2).toString(16), Number(C.$3).toString(16)];
          for (var E = 0; E < F.length; E++) {
            if (F[E].length < 2) {
              F[E] = "0" + F[E];
            }
          }
          F = F.join("");
        }
        if (F.length < 6) {
          F = F.replace(D.Color.re_hex3, "$1$1");
        }
        if (F !== "transparent" && F.indexOf("#") < 0) {
          F = "#" + F;
        }
        return F.toUpperCase();
      }
    };
  })(A);
}, "3.2.0", {
  requires: ["dom-base"]
});
YUI.add("dom-screen", function(A) {
  (function(F) {
    var D = "documentElement",
      Q = "compatMode",
      O = "position",
      C = "fixed",
      M = "relative",
      G = "left",
      H = "top",
      I = "BackCompat",
      P = "medium",
      E = "borderLeftWidth",
      B = "borderTopWidth",
      R = "getBoundingClientRect",
      K = "getComputedStyle",
      L = F.DOM,
      N = /^t(?:able|d|h)$/i,
      J;
    if (F.UA.ie) {
      if (F.config.doc[Q] !== "quirks") {
        J = D;
      } else {
        J = "body";
      }
    }
    F.mix(L, {
      winHeight: function(T) {
        var S = L._getWinSize(T).height;
        return S;
      },
      winWidth: function(T) {
        var S = L._getWinSize(T).width;
        return S;
      },
      docHeight: function(T) {
        var S = L._getDocSize(T).height;
        return Math.max(S, L._getWinSize(T).height);
      },
      docWidth: function(T) {
        var S = L._getDocSize(T).width;
        return Math.max(S, L._getWinSize(T).width);
      },
      docScrollX: function(U, V) {
        V = V || (U) ? L._getDoc(U) : F.config.doc;
        var T = V.defaultView,
          S = (T) ? T.pageXOffset : 0;
        return Math.max(V[D].scrollLeft, V.body.scrollLeft, S);
      },
      docScrollY: function(U, V) {
        V = V || (U) ? L._getDoc(U) : F.config.doc;
        var T = V.defaultView,
          S = (T) ? T.pageYOffset : 0;
        return Math.max(V[D].scrollTop, V.body.scrollTop, S);
      },
      getXY: function() {
        if (F.config.doc[D][R]) {
          return function(W) {
            var d = null,
              X, T, Y, b, a, S, V, Z, c, U;
            if (W && W.tagName) {
              c = W.ownerDocument;
              U = c[D];
              if (U.contains) {
                inDoc = U.contains(W);
              } else {
                inDoc = F.DOM.contains(U, W);
              }
              if (inDoc) {
                X = (J) ? c[J].scrollLeft : L.docScrollX(W, c);
                T = (J) ? c[J].scrollTop : L.docScrollY(W, c);
                Y = W[R]();
                d = [Y.left, Y.top];
                if (F.UA.ie) {
                  b = 2;
                  a = 2;
                  Z = c[Q];
                  S = L[K](c[D], E);
                  V = L[K](c[D], B);
                  if (F.UA.ie === 6) {
                    if (Z !== I) {
                      b = 0;
                      a = 0;
                    }
                  }
                  if ((Z == I)) {
                    if (S !== P) {
                      b = parseInt(S, 10);
                    }
                    if (V !== P) {
                      a = parseInt(V, 10);
                    }
                  }
                  d[0] -= b;
                  d[1] -= a;
                }
                if ((T || X)) {
                  if (!F.UA.ios) {
                    d[0] += X;
                    d[1] += T;
                  }
                }
              } else {
                d = L._getOffset(W);
              }
            }
            return d;
          };
        } else {
          return function(T) {
            var W = null,
              V, S, Y, U, X;
            if (T) {
              if (L.inDoc(T)) {
                W = [T.offsetLeft, T.offsetTop];
                V = T.ownerDocument;
                S = T;
                Y = ((F.UA.gecko || F.UA.webkit > 519) ? true : false);
                while ((S = S.offsetParent)) {
                  W[0] += S.offsetLeft;
                  W[1] += S.offsetTop;
                  if (Y) {
                    W = L._calcBorders(S, W);
                  }
                }
                if (L.getStyle(T, O) != C) {
                  S = T;
                  while ((S = S.parentNode)) {
                    U = S.scrollTop;
                    X = S.scrollLeft;
                    if (F.UA.gecko && (L.getStyle(S, "overflow") !== "visible")) {
                      W = L._calcBorders(S, W);
                    }
                    if (U || X) {
                      W[0] -= X;
                      W[1] -= U;
                    }
                  }
                  W[0] += L.docScrollX(T, V);
                  W[1] += L.docScrollY(T, V);
                } else {
                  W[0] += L.docScrollX(T, V);
                  W[1] += L.docScrollY(T, V);
                }
              } else {
                W = L._getOffset(T);
              }
            }
            return W;
          };
        }
      }(),
      getX: function(S) {
        return L.getXY(S)[0];
      },
      getY: function(S) {
        return L.getXY(S)[1];
      },
      setXY: function(T, W, Z) {
        var U = L.setStyle,
          Y, X, S, V;
        if (T && W) {
          Y = L.getStyle(T, O);
          X = L._getOffset(T);
          if (Y == "static") {
            Y = M;
            U(T, O, Y);
          }
          V = L.getXY(T);
          if (W[0] !== null) {
            U(T, G, W[0] - V[0] + X[0] + "px");
          }
          if (W[1] !== null) {
            U(T, H, W[1] - V[1] + X[1] + "px");
          }
          if (!Z) {
            S = L.getXY(T);
            if (S[0] !== W[0] || S[1] !== W[1]) {
              L.setXY(T, W, true);
            }
          }
        } else {}
      },
      setX: function(T, S) {
        return L.setXY(T, [S, null]);
      },
      setY: function(S, T) {
        return L.setXY(S, [null, T]);
      },
      swapXY: function(T, S) {
        var U = L.getXY(T);
        L.setXY(T, L.getXY(S));
        L.setXY(S, U);
      },
      _calcBorders: function(U, V) {
        var T = parseInt(L[K](U, B), 10) || 0,
          S = parseInt(L[K](U, E), 10) || 0;
        if (F.UA.gecko) {
          if (N.test(U.tagName)) {
            T = 0;
            S = 0;
          }
        }
        V[0] += S;
        V[1] += T;
        return V;
      },
      _getWinSize: function(V, X) {
        X = X || (V) ? L._getDoc(V) : F.config.doc;
        var W = X.defaultView || X.parentWindow,
          Y = X[Q],
          U = W.innerHeight,
          T = W.innerWidth,
          S = X[D];
        if (Y && !F.UA.opera) {
          if (Y != "CSS1Compat") {
            S = X.body;
          }
          U = S.clientHeight;
          T = S.clientWidth;
        }
        return {
          height: U,
          width: T
        };
      },
      _getDocSize: function(T) {
        var U = (T) ? L._getDoc(T) : F.config.doc,
          S = U[D];
        if (U[Q] != "CSS1Compat") {
          S = U.body;
        }
        return {
          height: S.scrollHeight,
          width: S.scrollWidth
        };
      }
    });
  })(A);
  (function(G) {
    var D = "top",
      C = "right",
      H = "bottom",
      B = "left",
      F = function(L, K) {
        var N = Math.max(L[D], K[D]),
          O = Math.min(L[C], K[C]),
          I = Math.min(L[H], K[H]),
          J = Math.max(L[B], K[B]),
          M = {};
        M[D] = N;
        M[C] = O;
        M[H] = I;
        M[B] = J;
        return M;
      },
      E = G.DOM;
    G.mix(E, {
      region: function(J) {
        var K = E.getXY(J),
          I = false;
        if (J && K) {
          I = E._getRegion(K[1], K[0] + J.offsetWidth, K[1] + J.offsetHeight, K[0]);
        }
        return I;
      },
      intersect: function(K, I, M) {
        var J = M || E.region(K),
          L = {},
          O = I,
          N;
        if (O.tagName) {
          L = E.region(O);
        } else {
          if (G.Lang.isObject(I)) {
            L = I;
          } else {
            return false;
          }
        }
        N = F(L, J);
        return {
          top: N[D],
          right: N[C],
          bottom: N[H],
          left: N[B],
          area: ((N[H] - N[D]) * (N[C] - N[B])),
          yoff: ((N[H] - N[D])),
          xoff: (N[C] - N[B]),
          inRegion: E.inRegion(K, I, false, M)
        };
      },
      inRegion: function(L, I, J, N) {
        var M = {},
          K = N || E.region(L),
          P = I,
          O;
        if (P.tagName) {
          M = E.region(P);
        } else {
          if (G.Lang.isObject(I)) {
            M = I;
          } else {
            return false;
          }
        }
        if (J) {
          return (K[B] >= M[B] && K[C] <= M[C] && K[D] >= M[D] && K[H] <= M[H]);
        } else {
          O = F(M, K);
          if (O[H] >= O[D] && O[C] >= O[B]) {
            return true;
          } else {
            return false;
          }
        }
      },
      inViewportRegion: function(J, I, K) {
        return E.inRegion(J, E.viewportRegion(J), I, K);
      },
      _getRegion: function(K, L, I, J) {
        var M = {};
        M[D] = M[1] = K;
        M[B] = M[0] = J;
        M[H] = I;
        M[C] = L;
        M.width = M[C] - M[B];
        M.height = M[H] - M[D];
        return M;
      },
      viewportRegion: function(J) {
        J = J || G.config.doc.documentElement;
        var I = false,
          L, K;
        if (J) {
          L = E.docScrollX(J);
          K = E.docScrollY(J);
          I = E._getRegion(K, E.winWidth(J) + L, K + E.winHeight(J), L);
        }
        return I;
      }
    });
  })(A);
}, "3.2.0", {
  requires: ["dom-base", "dom-style", "event-base"]
});
YUI.add("selector-native", function(A) {
  (function(E) {
    E.namespace("Selector");
    var C = "compareDocumentPosition",
      D = "ownerDocument";
    var B = {
      _foundCache: [],
      useNative: true,
      _compare: ("sourceIndex" in E.config.doc.documentElement) ? function(I, H) {
        var G = I.sourceIndex,
          F = H.sourceIndex;
        if (G === F) {
          return 0;
        } else {
          if (G > F) {
            return 1;
          }
        }
        return -1;
      } : (E.config.doc.documentElement[C] ? function(G, F) {
        if (G[C](F) & 4) {
          return -1;
        } else {
          return 1;
        }
      } : function(J, I) {
        var H, F, G;
        if (J && I) {
          H = J[D].createRange();
          H.setStart(J, 0);
          F = I[D].createRange();
          F.setStart(I, 0);
          G = H.compareBoundaryPoints(1, F);
        }
        return G;
      }),
      _sort: function(F) {
        if (F) {
          F = E.Array(F, 0, true);
          if (F.sort) {
            F.sort(B._compare);
          }
        }
        return F;
      },
      _deDupe: function(F) {
        var G = [],
          H, I;
        for (H = 0;
          (I = F[H++]);) {
          if (!I._found) {
            G[G.length] = I;
            I._found = true;
          }
        }
        for (H = 0;
          (I = G[H++]);) {
          I._found = null;
          I.removeAttribute("_found");
        }
        return G;
      },
      query: function(G, N, O, F) {
        N = N || E.config.doc;
        var K = [],
          H = (E.Selector.useNative && E.config.doc.querySelector && !F),
          J = [
            [G, N]
          ],
          L, P, I, M = (H) ? E.Selector._nativeQuery : E.Selector._bruteQuery;
        if (G && M) {
          if (!F && (!H || N.tagName)) {
            J = B._splitQueries(G, N);
          }
          for (I = 0;
            (L = J[I++]);) {
            P = M(L[0], L[1], O);
            if (!O) {
              P = E.Array(P, 0, true);
            }
            if (P) {
              K = K.concat(P);
            }
          }
          if (J.length > 1) {
            K = B._sort(B._deDupe(K));
          }
        }
        return (O) ? (K[0] || null) : K;
      },
      _splitQueries: function(H, K) {
        var G = H.split(","),
          I = [],
          L = "",
          J, F;
        if (K) {
          if (K.tagName) {
            K.id = K.id || E.guid();
            L = '[id="' + K.id + '"] ';
          }
          for (J = 0, F = G.length; J < F; ++J) {
            H = L + G[J];
            I.push([H, K]);
          }
        }
        return I;
      },
      _nativeQuery: function(F, G, H) {
        if (E.UA.webkit && F.indexOf(":checked") > -1 && (E.Selector.pseudos && E.Selector.pseudos.checked)) {
          return E.Selector.query(F, G, H, true);
        }
        try {
          return G["querySelector" + (H ? "" : "All")](F);
        } catch (I) {
          return E.Selector.query(F, G, H, true);
        }
      },
      filter: function(G, F) {
        var H = [],
          I, J;
        if (G && F) {
          for (I = 0;
            (J = G[I++]);) {
            if (E.Selector.test(J, F)) {
              H[H.length] = J;
            }
          }
        } else {}
        return H;
      },
      test: function(H, I, N) {
        var L = false,
          G = I.split(","),
          F = false,
          O, R, M, Q, K, J, P;
        if (H && H.tagName) {
          if (!N && !E.DOM.inDoc(H)) {
            O = H.parentNode;
            if (O) {
              N = O;
            } else {
              Q = H[D].createDocumentFragment();
              Q.appendChild(H);
              N = Q;
              F = true;
            }
          }
          N = N || H[D];
          if (!H.id) {
            H.id = E.guid();
          }
          for (K = 0;
            (P = G[K++]);) {
            P += '[id="' + H.id + '"]';
            M = E.Selector.query(P, N);
            for (J = 0; R = M[J++];) {
              if (R === H) {
                L = true;
                break;
              }
            }
            if (L) {
              break;
            }
          }
          if (F) {
            Q.removeChild(H);
          }
        }
        return L;
      },
      ancestor: function(G, F, H) {
        return E.DOM.ancestor(G, function(I) {
          return E.Selector.test(I, F);
        }, H);
      }
    };
    E.mix(E.Selector, B, true);
  })(A);
}, "3.2.0", {
  requires: ["dom-base"]
});
YUI.add("selector-css2", function(G) {
  var H = "parentNode",
    D = "tagName",
    E = "attributes",
    A = "combinator",
    F = "pseudos",
    C = G.Selector,
    B = {
      _reRegExpTokens: /([\^\$\?\[\]\*\+\-\.\(\)\|\\])/,
      SORT_RESULTS: true,
      _children: function(M, I) {
        var J = M.children,
          L, K = [],
          N, O;
        if (M.children && I && M.children.tags) {
          K = M.children.tags(I);
        } else {
          if ((!J && M[D]) || (J && I)) {
            N = J || M.childNodes;
            J = [];
            for (L = 0;
              (O = N[L++]);) {
              if (O.tagName) {
                if (!I || I === O.tagName) {
                  J.push(O);
                }
              }
            }
          }
        }
        return J || [];
      },
      _re: {
        attr: /(\[[^\]]*\])/g,
        pseudos: /:([\-\w]+(?:\(?:['"]?(.+)['"]?\)))*/i
      },
      shorthand: {
        "\\#(-?[_a-z]+[-\\w]*)": "[id=$1]",
        "\\.(-?[_a-z]+[-\\w]*)": "[className~=$1]"
      },
      operators: {
        "": function(J, I) {
          return G.DOM.getAttribute(J, I) !== "";
        },
        "~=": "(?:^|\\s+){val}(?:\\s+|$)",
        "|=": "^{val}-?"
      },
      pseudos: {
        "first-child": function(I) {
          return G.Selector._children(I[H])[0] === I;
        }
      },
      _bruteQuery: function(N, R, T) {
        var O = [],
          I = [],
          Q = C._tokenize(N),
          M = Q[Q.length - 1],
          S = G.DOM._getDoc(R),
          K, J, P, L;
        if (M) {
          J = M.id;
          P = M.className;
          L = M.tagName || "*";
          if (R.getElementsByTagName) {
            if (J && (R.all || (R.nodeType === 9 || G.DOM.inDoc(R)))) {
              I = G.DOM.allById(J, R);
            } else {
              if (P) {
                I = R.getElementsByClassName(P);
              } else {
                I = R.getElementsByTagName(L);
              }
            }
          } else {
            K = R.firstChild;
            while (K) {
              if (K.tagName) {
                I.push(K);
              }
              K = K.nextSilbing || K.firstChild;
            }
          }
          if (I.length) {
            O = C._filterNodes(I, Q, T);
          }
        }
        return O;
      },
      _filterNodes: function(R, N, P) {
        var W = 0,
          V, X = N.length,
          Q = X - 1,
          M = [],
          T = R[0],
          a = T,
          Y = G.Selector.getters,
          L, U, K, O, I, S, J, Z;
        for (W = 0;
          (a = T = R[W++]);) {
          Q = X - 1;
          O = null;
          testLoop: while (a && a.tagName) {
            K = N[Q];
            J = K.tests;
            V = J.length;
            if (V && !I) {
              while ((Z = J[--V])) {
                L = Z[1];
                if (Y[Z[0]]) {
                  S = Y[Z[0]](a, Z[0]);
                } else {
                  S = a[Z[0]];
                  if (S === undefined && a.getAttribute) {
                    S = a.getAttribute(Z[0]);
                  }
                }
                if ((L === "=" && S !== Z[2]) || (typeof L !== "string" && L.test && !L.test(S)) || (!L.test && typeof L === "function" && !L(a, Z[0]))) {
                  if ((a = a[O])) {
                    while (a && (!a.tagName || (K.tagName && K.tagName !== a.tagName))) {
                      a = a[O];
                    }
                  }
                  continue testLoop;
                }
              }
            }
            Q--;
            if (!I && (U = K.combinator)) {
              O = U.axis;
              a = a[O];
              while (a && !a.tagName) {
                a = a[O];
              }
              if (U.direct) {
                O = null;
              }
            } else {
              M.push(T);
              if (P) {
                return M;
              }
              break;
            }
          }
        }
        T = a = null;
        return M;
      },
      combinators: {
        " ": {
          axis: "parentNode"
        },
        ">": {
          axis: "parentNode",
          direct: true
        },
        "+": {
          axis: "previousSibling",
          direct: true
        }
      },
      _parsers: [{
        name: E,
        re: /^\[(-?[a-z]+[\w\-]*)+([~\|\^\$\*!=]=?)?['"]?([^\]]*?)['"]?\]/i,
        fn: function(K, L) {
          var J = K[2] || "",
            I = G.Selector.operators,
            M;
          if ((K[1] === "id" && J === "=") || (K[1] === "className" && G.config.doc.documentElement.getElementsByClassName && (J === "~=" || J === "="))) {
            L.prefilter = K[1];
            L[K[1]] = K[3];
          }
          if (J in I) {
            M = I[J];
            if (typeof M === "string") {
              K[3] = K[3].replace(G.Selector._reRegExpTokens, "\\$1");
              M = G.DOM._getRegExp(M.replace("{val}", K[3]));
            }
            K[2] = M;
          }
          if (!L.last || L.prefilter !== K[1]) {
            return K.slice(1);
          }
        }
      }, {
        name: D,
        re: /^((?:-?[_a-z]+[\w-]*)|\*)/i,
        fn: function(J, K) {
          var I = J[1].toUpperCase();
          K.tagName = I;
          if (I !== "*" && (!K.last || K.prefilter)) {
            return [D, "=", I];
          }
          if (!K.prefilter) {
            K.prefilter = "tagName";
          }
        }
      }, {
        name: A,
        re: /^\s*([>+~]|\s)\s*/,
        fn: function(I, J) {}
      }, {
        name: F,
        re: /^:([\-\w]+)(?:\(['"]?(.+)['"]?\))*/i,
        fn: function(I, J) {
          var K = C[F][I[1]];
          if (K) {
            return [I[2], K];
          } else {
            return false;
          }
        }
      }],
      _getToken: function(I) {
        return {
          tagName: null,
          id: null,
          className: null,
          attributes: {},
          combinator: null,
          tests: []
        };
      },
      _tokenize: function(K) {
        K = K || "";
        K = C._replaceShorthand(G.Lang.trim(K));
        var J = C._getToken(),
          P = K,
          O = [],
          Q = false,
          M, N, L, I;
        outer: do {
          Q = false;
          for (L = 0;
            (I = C._parsers[L++]);) {
            if ((M = I.re.exec(K))) {
              if (I.name !== A) {
                J.selector = K;
              }
              K = K.replace(M[0], "");
              if (!K.length) {
                J.last = true;
              }
              if (C._attrFilters[M[1]]) {
                M[1] = C._attrFilters[M[1]];
              }
              N = I.fn(M, J);
              if (N === false) {
                Q = false;
                break outer;
              } else {
                if (N) {
                  J.tests.push(N);
                }
              }
              if (!K.length || I.name === A) {
                O.push(J);
                J = C._getToken(J);
                if (I.name === A) {
                  J.combinator = G.Selector.combinators[M[1]];
                }
              }
              Q = true;
            }
          }
        } while (Q && K.length);
        if (!Q || K.length) {
          O = [];
        }
        return O;
      },
      _replaceShorthand: function(J) {
        var K = C.shorthand,
          L = J.match(C._re.attr),
          O = J.match(C._re.pseudos),
          N, M, I;
        if (O) {
          J = J.replace(C._re.pseudos, "!!REPLACED_PSEUDO!!");
        }
        if (L) {
          J = J.replace(C._re.attr, "!!REPLACED_ATTRIBUTE!!");
        }
        for (N in K) {
          if (K.hasOwnProperty(N)) {
            J = J.replace(G.DOM._getRegExp(N, "gi"), K[N]);
          }
        }
        if (L) {
          for (M = 0, I = L.length; M < I; ++M) {
            J = J.replace("!!REPLACED_ATTRIBUTE!!", L[M]);
          }
        }
        if (O) {
          for (M = 0, I = O.length; M < I; ++M) {
            J = J.replace("!!REPLACED_PSEUDO!!", O[M]);
          }
        }
        return J;
      },
      _attrFilters: {
        "class": "className",
        "for": "htmlFor"
      },
      getters: {
        href: function(J, I) {
          return G.DOM.getAttribute(J, I);
        }
      }
    };
  G.mix(G.Selector, B, true);
  G.Selector.getters.src = G.Selector.getters.rel = G.Selector.getters.href;
  if (G.Selector.useNative && G.config.doc.querySelector) {
    G.Selector.shorthand["\\.(-?[_a-z]+[-\\w]*)"] = "[class~=$1]";
  }
}, "3.2.0", {
  requires: ["selector-native"]
});
YUI.add("selector", function(A) {}, "3.2.0", {
  use: ["selector-native", "selector-css2"]
});
YUI.add("dom", function(A) {}, "3.2.0", {
  use: ["dom-base", "dom-style", "dom-screen", "selector"]
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
(function() {
  var d, b = YUI.Env,
    c = YUI.config,
    h = c.doc,
    e = h && h.documentElement,
    i = e && e.doScroll,
    k = YUI.Env.add,
    f = YUI.Env.remove,
    g = (i) ? "onreadystatechange" : "DOMContentLoaded",
    a = c.pollInterval || 40,
    j = function(l) {
      b._ready();
    };
  if (!b._ready) {
    b._ready = function() {
      if (!b.DOMReady) {
        b.DOMReady = true;
        f(h, g, j);
      }
    };
    /*! DOMReady: based on work by: Dean Edwards/John Resig/Matthias Miller/Diego Perini */
    if (i) {
      if (self !== self.top) {
        d = function() {
          if (h.readyState == "complete") {
            f(h, g, d);
            j();
          }
        };
        k(h, g, d);
      } else {
        b._dri = setInterval(function() {
          try {
            e.doScroll("left");
            clearInterval(b._dri);
            b._dri = null;
            j();
          } catch (l) {}
        }, a);
      }
    } else {
      k(h, g, j);
    }
  }
})();
YUI.add("event-base", function(a) {
  (function() {
    var c = YUI.Env,
      b = function() {
        a.fire("domready");
      };
    a.publish("domready", {
      fireOnce: true,
      async: true
    });
    if (c.DOMReady) {
      b();
    } else {
      a.before(b, c, "_ready");
    }
  })();
  (function() {
    var c = a.UA,
      b = {
        63232: 38,
        63233: 40,
        63234: 37,
        63235: 39,
        63276: 33,
        63277: 34,
        25: 9,
        63272: 46,
        63273: 36,
        63275: 35
      },
      d = function(g) {
        try {
          if (g && 3 == g.nodeType) {
            g = g.parentNode;
          }
        } catch (f) {
          return null;
        }
        return a.one(g);
      };
    a.DOMEventFacade = function(m, g, f) {
      f = f || {};
      var i = m,
        h = g,
        j = a.config.doc,
        n = j.body,
        o = i.pageX,
        l = i.pageY,
        k, r, p = j.documentElement,
        q = f.overrides || {};
      this.altKey = i.altKey;
      this.ctrlKey = i.ctrlKey;
      this.metaKey = i.metaKey;
      this.shiftKey = i.shiftKey;
      this.type = q.type || i.type;
      this.clientX = i.clientX;
      this.clientY = i.clientY;
      if (("clientX" in i) && (!o) && (0 !== o)) {
        o = i.clientX;
        l = i.clientY;
        if (c.ie) {
          o += (p.scrollLeft || n.scrollLeft || 0);
          l += (p.scrollTop || n.scrollTop || 0);
        }
      }
      this._yuifacade = true;
      this._event = i;
      this.pageX = o;
      this.pageY = l;
      k = i.keyCode || i.charCode || 0;
      if (c.webkit && (k in b)) {
        k = b[k];
      }
      this.keyCode = k;
      this.charCode = k;
      this.button = i.which || i.button;
      this.which = this.button;
      this.target = d(i.target || i.srcElement);
      this.currentTarget = d(h);
      r = i.relatedTarget;
      if (!r) {
        if (i.type == "mouseout") {
          r = i.toElement;
        } else {
          if (i.type == "mouseover") {
            r = i.fromElement;
          }
        }
      }
      this.relatedTarget = d(r);
      if (i.type == "mousewheel" || i.type == "DOMMouseScroll") {
        this.wheelDelta = (i.detail) ? (i.detail * -1) : Math.round(i.wheelDelta / 80) || ((i.wheelDelta < 0) ? -1 : 1);
      }
      this.stopPropagation = function() {
        if (i.stopPropagation) {
          i.stopPropagation();
        } else {
          i.cancelBubble = true;
        }
        f.stopped = 1;
        this.stopped = 1;
      };
      this.stopImmediatePropagation = function() {
        if (i.stopImmediatePropagation) {
          i.stopImmediatePropagation();
        } else {
          this.stopPropagation();
        }
        f.stopped = 2;
        this.stopped = 2;
      };
      this.preventDefault = function(e) {
        if (i.preventDefault) {
          i.preventDefault();
        }
        i.returnValue = e || false;
        f.prevented = 1;
        this.prevented = 1;
      };
      this.halt = function(e) {
        if (e) {
          this.stopImmediatePropagation();
        } else {
          this.stopPropagation();
        }
        this.preventDefault();
      };
      if (this._touch) {
        this._touch(i, g, f);
      }
    };
  })();
  (function() {
    a.Env.evt.dom_wrappers = {};
    a.Env.evt.dom_map = {};
    var j = a.Env.evt,
      c = a.config,
      g = c.win,
      l = YUI.Env.add,
      e = YUI.Env.remove,
      i = function() {
        YUI.Env.windowLoaded = true;
        a.Event._load();
        e(g, "load", i);
      },
      b = function() {
        a.Event._unload();
        e(g, "unload", b);
      },
      d = "domready",
      f = "~yui|2|compat~",
      h = function(n) {
        try {
          return (n && typeof n !== "string" && a.Lang.isNumber(n.length) && !n.tagName && !n.alert);
        } catch (m) {
          return false;
        }
      },
      k = function() {
        var o = false,
          p = 0,
          n = [],
          q = j.dom_wrappers,
          m = null,
          r = j.dom_map;
        return {
          POLL_RETRYS: 1000,
          POLL_INTERVAL: 40,
          lastError: null,
          _interval: null,
          _dri: null,
          DOMReady: false,
          startInterval: function() {
            if (!k._interval) {
              k._interval = setInterval(a.bind(k._poll, k), k.POLL_INTERVAL);
            }
          },
          onAvailable: function(s, w, A, t, x, z) {
            var y = a.Array(s),
              u, v;
            for (u = 0; u < y.length; u = u + 1) {
              n.push({
                id: y[u],
                fn: w,
                obj: A,
                override: t,
                checkReady: x,
                compat: z
              });
            }
            p = this.POLL_RETRYS;
            setTimeout(a.bind(k._poll, k), 0);
            v = new a.EventHandle({
              _delete: function() {
                if (v.handle) {
                  v.handle.detach();
                  return;
                }
                var C, B;
                for (C = 0; C < y.length; C++) {
                  for (B = 0; B < n.length; B++) {
                    if (y[C] === n[B].id) {
                      n.splice(B, 1);
                    }
                  }
                }
              }
            });
            return v;
          },
          onContentReady: function(w, t, v, u, s) {
            return this.onAvailable(w, t, v, u, true, s);
          },
          attach: function(v, u, t, s) {
            return k._attach(a.Array(arguments, 0, true));
          },
          _createWrapper: function(y, x, s, t, w) {
            var v, z = a.stamp(y),
              u = "event:" + z + x;
            if (false === w) {
              u += "native";
            }
            if (s) {
              u += "capture";
            }
            v = q[u];
            if (!v) {
              v = a.publish(u, {
                silent: true,
                bubbles: false,
                contextFn: function() {
                  if (t) {
                    return v.el;
                  } else {
                    v.nodeRef = v.nodeRef || a.one(v.el);
                    return v.nodeRef;
                  }
                }
              });
              v.overrides = {};
              v.el = y;
              v.key = u;
              v.domkey = z;
              v.type = x;
              v.fn = function(A) {
                v.fire(k.getEvent(A, y, (t || (false === w))));
              };
              v.capture = s;
              if (y == g && x == "load") {
                v.fireOnce = true;
                m = u;
              }
              q[u] = v;
              r[z] = r[z] || {};
              r[z][u] = v;
              l(y, x, v.fn, s);
            }
            return v;
          },
          _attach: function(y, x) {
            var D, F, v, C, s, u = false,
              w, z = y[0],
              A = y[1],
              t = y[2] || g,
              G = x && x.facade,
              E = x && x.capture,
              B = x && x.overrides;
            if (y[y.length - 1] === f) {
              D = true;
            }
            if (!A || !A.call) {
              return false;
            }
            if (h(t)) {
              F = [];
              a.each(t, function(I, H) {
                y[2] = I;
                F.push(k._attach(y, x));
              });
              return new a.EventHandle(F);
            } else {
              if (a.Lang.isString(t)) {
                if (D) {
                  v = a.DOM.byId(t);
                } else {
                  v = a.Selector.query(t);
                  switch (v.length) {
                    case 0:
                      v = null;
                      break;
                    case 1:
                      v = v[0];
                      break;
                    default:
                      y[2] = v;
                      return k._attach(y, x);
                  }
                }
                if (v) {
                  t = v;
                } else {
                  w = this.onAvailable(t, function() {
                    w.handle = k._attach(y, x);
                  }, k, true, false, D);
                  return w;
                }
              }
            }
            if (!t) {
              return false;
            }
            if (a.Node && t instanceof a.Node) {
              t = a.Node.getDOMNode(t);
            }
            C = this._createWrapper(t, z, E, D, G);
            if (B) {
              a.mix(C.overrides, B);
            }
            if (t == g && z == "load") {
              if (YUI.Env.windowLoaded) {
                u = true;
              }
            }
            if (D) {
              y.pop();
            }
            s = y[3];
            w = C._on(A, s, (y.length > 4) ? y.slice(4) : null);
            if (u) {
              C.fire();
            }
            return w;
          },
          detach: function(z, A, u, x) {
            var y = a.Array(arguments, 0, true),
              C, v, B, w, s, t;
            if (y[y.length - 1] === f) {
              C = true;
            }
            if (z && z.detach) {
              return z.detach();
            }
            if (typeof u == "string") {
              if (C) {
                u = a.DOM.byId(u);
              } else {
                u = a.Selector.query(u);
                v = u.length;
                if (v < 1) {
                  u = null;
                } else {
                  if (v == 1) {
                    u = u[0];
                  }
                }
              }
            }
            if (!u) {
              return false;
            }
            if (u.detach) {
              y.splice(2, 1);
              return u.detach.apply(u, y);
            } else {
              if (h(u)) {
                B = true;
                for (w = 0, v = u.length; w < v; ++w) {
                  y[2] = u[w];
                  B = (a.Event.detach.apply(a.Event, y) && B);
                }
                return B;
              }
            }
            if (!z || !A || !A.call) {
              return this.purgeElement(u, false, z);
            }
            s = "event:" + a.stamp(u) + z;
            t = q[s];
            if (t) {
              return t.detach(A);
            } else {
              return false;
            }
          },
          getEvent: function(v, t, s) {
            var u = v || g.event;
            return (s) ? u : new a.DOMEventFacade(u, t, q["event:" + a.stamp(t) + v.type]);
          },
          generateId: function(s) {
            var t = s.id;
            if (!t) {
              t = a.stamp(s);
              s.id = t;
            }
            return t;
          },
          _isValidCollection: h,
          _load: function(s) {
            if (!o) {
              o = true;
              if (a.fire) {
                a.fire(d);
              }
              k._poll();
            }
          },
          _poll: function() {
            if (this.locked) {
              return;
            }
            if (a.UA.ie && !YUI.Env.DOMReady) {
              this.startInterval();
              return;
            }
            this.locked = true;
            var t, s, x, u, w, y, v = !o;
            if (!v) {
              v = (p > 0);
            }
            w = [];
            y = function(B, C) {
              var A, z = C.override;
              if (C.compat) {
                if (C.override) {
                  if (z === true) {
                    A = C.obj;
                  } else {
                    A = z;
                  }
                } else {
                  A = B;
                }
                C.fn.call(A, C.obj);
              } else {
                A = C.obj || a.one(B);
                C.fn.apply(A, (a.Lang.isArray(z)) ? z : []);
              }
            };
            for (t = 0, s = n.length; t < s; ++t) {
              x = n[t];
              if (x && !x.checkReady) {
                u = (x.compat) ? a.DOM.byId(x.id) : a.Selector.query(x.id, null, true);
                if (u) {
                  y(u, x);
                  n[t] = null;
                } else {
                  w.push(x);
                }
              }
            }
            for (t = 0, s = n.length; t < s; ++t) {
              x = n[t];
              if (x && x.checkReady) {
                u = (x.compat) ? a.DOM.byId(x.id) : a.Selector.query(x.id, null, true);
                if (u) {
                  if (o || (u.get && u.get("nextSibling")) || u.nextSibling) {
                    y(u, x);
                    n[t] = null;
                  }
                } else {
                  w.push(x);
                }
              }
            }
            p = (w.length === 0) ? 0 : p - 1;
            if (v) {
              this.startInterval();
            } else {
              clearInterval(this._interval);
              this._interval = null;
            }
            this.locked = false;
            return;
          },
          purgeElement: function(v, s, z) {
            var x = (a.Lang.isString(v)) ? a.Selector.query(v, null, true) : v,
              B = this.getListeners(x, z),
              w, y, A, u, t;
            if (s && x) {
              B = B || [];
              u = a.Selector.query("*", x);
              w = 0;
              y = u.length;
              for (; w < y; ++w) {
                t = this.getListeners(u[w], z);
                if (t) {
                  B = B.concat(t);
                }
              }
            }
            if (B) {
              w = 0;
              y = B.length;
              for (; w < y; ++w) {
                A = B[w];
                A.detachAll();
                e(A.el, A.type, A.fn, A.capture);
                delete q[A.key];
                delete r[A.domkey][A.key];
              }
            }
          },
          getListeners: function(w, v) {
            var x = a.stamp(w, true),
              s = r[x],
              u = [],
              t = (v) ? "event:" + x + v : null,
              y = j.plugins;
            if (!s) {
              return null;
            }
            if (t) {
              if (y[v] && y[v].eventDef) {
                t += "_synth";
              }
              if (s[t]) {
                u.push(s[t]);
              }
              t += "native";
              if (s[t]) {
                u.push(s[t]);
              }
            } else {
              a.each(s, function(A, z) {
                u.push(A);
              });
            }
            return (u.length) ? u : null;
          },
          _unload: function(s) {
            a.each(q, function(u, t) {
              u.detachAll();
              e(u.el, u.type, u.fn, u.capture);
              delete q[t];
              delete r[u.domkey][t];
            });
          },
          nativeAdd: l,
          nativeRemove: e
        };
      }();
    a.Event = k;
    if (c.injected || YUI.Env.windowLoaded) {
      i();
    } else {
      l(g, "load", i);
    }
    if (a.UA.ie) {
      a.on(d, k._poll, k, true);
    }
    a.on("unload", b);
    k.Custom = a.CustomEvent;
    k.Subscriber = a.Subscriber;
    k.Target = a.EventTarget;
    k.Handle = a.EventHandle;
    k.Facade = a.EventFacade;
    k._poll();
  })();
  a.Env.evt.plugins.available = {
    on: function(d, c, f, e) {
      var b = arguments.length > 4 ? a.Array(arguments, 4, true) : [];
      return a.Event.onAvailable.call(a.Event, f, c, e, b);
    }
  };
  a.Env.evt.plugins.contentready = {
    on: function(d, c, f, e) {
      var b = arguments.length > 4 ? a.Array(arguments, 4, true) : [];
      return a.Event.onContentReady.call(a.Event, f, c, e, b);
    }
  };
}, "3.2.0", {
  requires: ["event-custom-base"]
});
YUI.add("event-delegate", function(g) {
  var d = g.Array,
    b = g.Lang,
    a = b.isString,
    f = g.Selector.test,
    c = g.Env.evt.handles;

  function e(q, s, j, i) {
    var o = d(arguments, 0, true),
      p = a(j) ? j : null,
      n = q.split(/\|/),
      l, h, k, r, m;
    if (n.length > 1) {
      r = n.shift();
      q = n.shift();
    }
    l = g.Node.DOM_EVENTS[q];
    if (b.isObject(l) && l.delegate) {
      m = l.delegate.apply(l, arguments);
    }
    if (!m) {
      if (!q || !s || !j || !i) {
        return;
      }
      h = (p) ? g.Selector.query(p, null, true) : j;
      if (!h && a(j)) {
        m = g.on("available", function() {
          g.mix(m, g.delegate.apply(g, o), true);
        }, j);
      }
      if (!m && h) {
        o.splice(2, 2, h);
        if (a(i)) {
          i = g.delegate.compileFilter(i);
        }
        m = g.on.apply(g, o);
        m.sub.filter = i;
        m.sub._notify = e.notifySub;
      }
    }
    if (m && r) {
      k = c[r] || (c[r] = {});
      k = k[q] || (k[q] = []);
      k.push(m);
    }
    return m;
  }
  e.notifySub = function(l, q, j) {
    q = q.slice();
    if (this.args) {
      q.push.apply(q, this.args);
    }
    var o = q[0],
      k = e._applyFilter(this.filter, q),
      h = o.currentTarget,
      m, p, n;
    if (k) {
      k = d(k);
      for (m = k.length - 1; m >= 0; --m) {
        n = k[m];
        q[0] = new g.DOMEventFacade(o, n, j);
        q[0].container = h;
        l = this.context || n;
        p = this.fn.apply(l, q);
        if (p === false) {
          break;
        }
      }
      return p;
    }
  };
  e.compileFilter = g.cached(function(h) {
    return function(j, i) {
      return f(j._node, h, i.currentTarget._node);
    };
  });
  e._applyFilter = function(k, j) {
    var m = j[0],
      h = m.currentTarget,
      l = m.target,
      i = [];
    j.unshift(l);
    while (l && l !== h) {
      if (k.apply(l, j)) {
        i.push(l);
      }
      j[0] = l = l.get("parentNode");
    }
    if (i.length <= 1) {
      i = i[0];
    }
    j.shift();
    return i;
  };
  g.delegate = g.Event.delegate = e;
}, "3.2.0", {
  requires: ["node-base"]
});
YUI.add("event-synthetic", function(b) {
  var h = b.Env.evt.dom_map,
    d = b.Array,
    g = b.Lang,
    j = g.isObject,
    c = g.isString,
    e = b.Selector.query,
    i = function() {};

  function f(l, k) {
    this.handle = l;
    this.emitFacade = k;
  }
  f.prototype.fire = function(q) {
    var k = d(arguments, 0, true),
      o = this.handle,
      p = o.evt,
      m = o.sub,
      r = m.context,
      l = m.filter,
      n = q || {};
    if (this.emitFacade) {
      if (!q || !q.preventDefault) {
        n = p._getFacade();
        if (j(q) && !q.preventDefault) {
          b.mix(n, q, true);
          k[0] = n;
        } else {
          k.unshift(n);
        }
      }
      n.type = p.type;
      n.details = k.slice();
      if (l) {
        n.container = p.host;
      }
    } else {
      if (l && j(q) && q.currentTarget) {
        k.shift();
      }
    }
    m.context = r || n.currentTarget || p.host;
    p.fire.apply(p, k);
    m.context = r;
  };

  function a() {
    this._init.apply(this, arguments);
  }
  b.mix(a, {
    Notifier: f,
    getRegistry: function(q, p, n) {
      var o = q._node,
        m = b.stamp(o),
        l = "event:" + m + p + "_synth",
        k = h[m] || (h[m] = {});
      if (!k[l] && n) {
        k[l] = {
          type: "_synth",
          fn: i,
          capture: false,
          el: o,
          key: l,
          domkey: m,
          notifiers: [],
          detachAll: function() {
            var r = this.notifiers,
              s = r.length;
            while (--s >= 0) {
              r[s].detach();
            }
          }
        };
      }
      return (k[l]) ? k[l].notifiers : null;
    },
    _deleteSub: function(l) {
      if (l && l.fn) {
        var k = this.eventDef,
          m = (l.filter) ? "detachDelegate" : "detach";
        this.subscribers = {};
        this.subCount = 0;
        k[m](l.node, l, this.notifier, l.filter);
        k._unregisterSub(l);
        delete l.fn;
        delete l.node;
        delete l.context;
      }
    },
    prototype: {
      constructor: a,
      _init: function() {
        var k = this.publishConfig || (this.publishConfig = {});
        this.emitFacade = ("emitFacade" in k) ? k.emitFacade : true;
        k.emitFacade = false;
      },
      processArgs: i,
      on: i,
      detach: i,
      delegate: i,
      detachDelegate: i,
      _on: function(m, o) {
        var n = [],
          k = m[2],
          q = o ? "delegate" : "on",
          l, p;
        l = (c(k)) ? e(k) : d(k);
        if (!l.length && c(k)) {
          p = b.on("available", function() {
            b.mix(p, b[q].apply(b, m), true);
          }, k);
          return p;
        }
        b.each(l, function(t) {
          var u = m.slice(),
            r, s;
          t = b.one(t);
          if (t) {
            r = this.processArgs(u, o);
            if (o) {
              s = u.splice(3, 1)[0];
            }
            u.splice(0, 4, u[1], u[3]);
            if (!this.preventDups || !this.getSubs(t, m, null, true)) {
              p = this._getNotifier(t, u, r, s);
              this[q](t, p.sub, p.notifier, s);
              n.push(p);
            }
          }
        }, this);
        return (n.length === 1) ? n[0] : new b.EventHandle(n);
      },
      _getNotifier: function(n, q, o, m) {
        var s = new b.CustomEvent(this.type, this.publishConfig),
          p = s.on.apply(s, q),
          r = new f(p, this.emitFacade),
          l = a.getRegistry(n, this.type, true),
          k = p.sub;
        p.notifier = r;
        k.node = n;
        k.filter = m;
        k._extra = o;
        b.mix(s, {
          eventDef: this,
          notifier: r,
          host: n,
          currentTarget: n,
          target: n,
          el: n._node,
          _delete: a._deleteSub
        }, true);
        l.push(p);
        return p;
      },
      _unregisterSub: function(m) {
        var k = a.getRegistry(m.node, this.type),
          l;
        if (k) {
          for (l = k.length - 1; l >= 0; --l) {
            if (k[l].sub === m) {
              k.splice(l, 1);
              break;
            }
          }
        }
      },
      _detach: function(m) {
        var r = m[2],
          p = (c(r)) ? e(r) : d(r),
          q, o, k, n, l;
        m.splice(2, 1);
        for (o = 0, k = p.length; o < k; ++o) {
          q = b.one(p[o]);
          if (q) {
            n = this.getSubs(q, m);
            if (n) {
              for (l = n.length - 1; l >= 0; --l) {
                n[l].detach();
              }
            }
          }
        }
      },
      getSubs: function(l, q, k, n) {
        var r = a.getRegistry(l, this.type),
          s = [],
          m, p, o;
        if (r) {
          if (!k) {
            k = this.subMatch;
          }
          for (m = 0, p = r.length; m < p; ++m) {
            o = r[m];
            if (k.call(this, o.sub, q)) {
              if (n) {
                return o;
              } else {
                s.push(r[m]);
              }
            }
          }
        }
        return s.length && s;
      },
      subMatch: function(l, k) {
        return !k[1] || l.fn === k[1];
      }
    }
  }, true);
  b.SyntheticEvent = a;
  b.Event.define = function(m, l, o) {
    if (!l) {
      l = {};
    }
    var n = (j(m)) ? m : b.merge({
        type: m
      }, l),
      p, k;
    if (o || !b.Node.DOM_EVENTS[n.type]) {
      p = function() {
        a.apply(this, arguments);
      };
      b.extend(p, a, n);
      k = new p();
      m = k.type;
      b.Node.DOM_EVENTS[m] = b.Env.evt.plugins[m] = {
        eventDef: k,
        on: function() {
          return k._on(d(arguments));
        },
        delegate: function() {
          return k._on(d(arguments), true);
        },
        detach: function() {
          return k._detach(d(arguments));
        }
      };
    }
    return k;
  };
}, "3.2.0", {
  requires: ["node-base", "event-custom"]
});
YUI.add("event-mousewheel", function(c) {
  var b = "DOMMouseScroll",
    a = function(e) {
      var d = c.Array(e, 0, true),
        f;
      if (c.UA.gecko) {
        d[0] = b;
        f = c.config.win;
      } else {
        f = c.config.doc;
      }
      if (d.length < 3) {
        d[2] = f;
      } else {
        d.splice(2, 0, f);
      }
      return d;
    };
  c.Env.evt.plugins.mousewheel = {
    on: function() {
      return c.Event._attach(a(arguments));
    },
    detach: function() {
      return c.Event.detach.apply(c.Event, a(arguments));
    }
  };
}, "3.2.0", {
  requires: ["node-base"]
});
YUI.add("event-mouseenter", function(c) {
  function b(h, d) {
    var g = h.currentTarget,
      f = h.relatedTarget;
    if (g !== f && !g.contains(f)) {
      d.fire(h);
    }
  }
  var a = {
    proxyType: "mouseover",
    on: function(f, d, e) {
      d.onHandle = f.on(this.proxyType, b, null, e);
    },
    detach: function(e, d) {
      d.onHandle.detach();
    },
    delegate: function(g, e, f, d) {
      e.delegateHandle = c.delegate(this.proxyType, b, g, d, null, f);
    },
    detachDelegate: function(e, d) {
      d.delegateHandle.detach();
    }
  };
  c.Event.define("mouseenter", a, true);
  c.Event.define("mouseleave", c.merge(a, {
    proxyType: "mouseout"
  }), true);
}, "3.2.0", {
  requires: ["event-synthetic"]
});
YUI.add("event-key", function(a) {
  a.Env.evt.plugins.key = {
    on: function(e, g, b, k, c) {
      var i = a.Array(arguments, 0, true),
        f, j, h, d;
      f = k && k.split(":");
      if (!k || k.indexOf(":") == -1 || !f[1]) {
        i[0] = "key" + ((f && f[0]) || "press");
        return a.on.apply(a, i);
      }
      j = f[0];
      h = (f[1]) ? f[1].split(/,|\+/) : null;
      d = (a.Lang.isString(b) ? b : a.stamp(b)) + k;
      d = d.replace(/,/g, "_");
      if (!a.getEvent(d)) {
        a.on(e + j, function(p) {
          var q = false,
            m = false,
            n, l, o;
          for (n = 0; n < h.length; n = n + 1) {
            l = h[n];
            o = parseInt(l, 10);
            if (a.Lang.isNumber(o)) {
              if (p.charCode === o) {
                q = true;
              } else {
                m = true;
              }
            } else {
              if (q || !m) {
                q = (p[l + "Key"]);
                m = !q;
              }
            }
          }
          if (q) {
            a.fire(d, p);
          }
        }, b);
      }
      i.splice(2, 2);
      i[0] = d;
      return a.on.apply(a, i);
    }
  };
}, "3.2.0", {
  requires: ["node-base"]
});
YUI.add("event-focus", function(e) {
  var d = e.Event,
    c = e.Lang,
    a = c.isString,
    b = c.isFunction(e.DOM.create('<p onbeforeactivate=";">').onbeforeactivate);

  function f(h, g, j) {
    var i = "_" + h + "Notifiers";
    e.Event.define(h, {
      _attach: function(l, m, k) {
        if (e.DOM.isWindow(l)) {
          return d._attach([h, function(n) {
            m.fire(n);
          }, l]);
        } else {
          return d._attach([g, this._proxy, l, this, m, k], {
            capture: true
          });
        }
      },
      _proxy: function(o, s, p) {
        var m = o.target,
          q = m.getData(i),
          t = e.stamp(o.currentTarget._node),
          k = (b || o.target !== o.currentTarget),
          l = s.handle.sub,
          r = [m, o].concat(l.args || []),
          n;
        s.currentTarget = (p) ? m : o.currentTarget;
        s.container = (p) ? o.currentTarget : null;
        if (!l.filter || l.filter.apply(m, r)) {
          if (!q) {
            q = {};
            m.setData(i, q);
            if (k) {
              n = d._attach([j, this._notify, m._node]).sub;
              n.once = true;
            }
          }
          if (!q[t]) {
            q[t] = [];
          }
          q[t].push(s);
          if (!k) {
            this._notify(o);
          }
        }
      },
      _notify: function(p, l) {
        var m = p.currentTarget,
          r = m.getData(i),
          s = m.get("ownerDocument") || m,
          q = m,
          k = [],
          t, n, o;
        if (r) {
          while (q && q !== s) {
            k.push.apply(k, r[e.stamp(q)] || []);
            q = q.get("parentNode");
          }
          k.push.apply(k, r[e.stamp(s)] || []);
          for (n = 0, o = k.length; n < o; ++n) {
            t = k[n];
            p.currentTarget = k[n].currentTarget;
            if (t.container) {
              p.container = t.container;
            } else {
              delete p.container;
            }
            t.fire(p);
          }
          m.clearData(i);
        }
      },
      on: function(m, k, l) {
        k.onHandle = this._attach(m._node, l);
      },
      detach: function(l, k) {
        k.onHandle.detach();
      },
      delegate: function(n, l, m, k) {
        if (a(k)) {
          l.filter = e.delegate.compileFilter(k);
        }
        l.delegateHandle = this._attach(n._node, m, true);
      },
      detachDelegate: function(l, k) {
        k.delegateHandle.detach();
      }
    }, true);
  }
  if (b) {
    f("focus", "beforeactivate", "focusin");
    f("blur", "beforedeactivate", "focusout");
  } else {
    f("focus", "focus", "focus");
    f("blur", "blur", "blur");
  }
}, "3.2.0", {
  requires: ["event-synthetic"]
});
YUI.add("event-resize", function(a) {
  (function() {
    var c, b, e = "window:resize",
      d = function(f) {
        if (a.UA.gecko) {
          a.fire(e, f);
        } else {
          if (b) {
            b.cancel();
          }
          b = a.later(a.config.windowResizeDelay || 40, a, function() {
            a.fire(e, f);
          });
        }
      };
    a.Env.evt.plugins.windowresize = {
      on: function(h, g) {
        if (!c) {
          c = a.Event._attach(["resize", d]);
        }
        var f = a.Array(arguments, 0, true);
        f[0] = e;
        return a.on.apply(a, f);
      }
    };
  })();
}, "3.2.0", {
  requires: ["node-base"]
});
YUI.add("event", function(a) {}, "3.2.0", {
  use: ["event-base", "event-delegate", "event-synthetic", "event-mousewheel", "event-mouseenter", "event-key", "event-focus", "event-resize"]
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("node-base", function(C) {
  var G = ".",
    E = "nodeName",
    J = "nodeType",
    B = "ownerDocument",
    I = "tagName",
    D = "_yuid",
    F = C.DOM,
    H = function(M) {
      var L = (M.nodeType !== 9) ? M.uniqueID : M[D];
      if (L && H._instances[L] && H._instances[L]._node !== M) {
        M[D] = null;
      }
      L = L || C.stamp(M);
      if (!L) {
        L = C.guid();
      }
      this[D] = L;
      this._node = M;
      H._instances[L] = this;
      this._stateProxy = M;
      C.EventTarget.call(this, {
        emitFacade: true
      });
      if (this._initPlugins) {
        this._initPlugins();
      }
    },
    K = function(M) {
      var L = null;
      if (M) {
        L = (typeof M === "string") ? function(N) {
          return C.Selector.test(N, M);
        } : function(N) {
          return M(C.one(N));
        };
      }
      return L;
    };
  H.NAME = "node";
  H.re_aria = /^(?:role$|aria-)/;
  H.DOM_EVENTS = {
    abort: 1,
    beforeunload: 1,
    blur: 1,
    change: 1,
    click: 1,
    close: 1,
    command: 1,
    contextmenu: 1,
    dblclick: 1,
    DOMMouseScroll: 1,
    drag: 1,
    dragstart: 1,
    dragenter: 1,
    dragover: 1,
    dragleave: 1,
    dragend: 1,
    drop: 1,
    error: 1,
    focus: 1,
    key: 1,
    keydown: 1,
    keypress: 1,
    keyup: 1,
    load: 1,
    message: 1,
    mousedown: 1,
    mouseenter: 1,
    mouseleave: 1,
    mousemove: 1,
    mousemultiwheel: 1,
    mouseout: 1,
    mouseover: 1,
    mouseup: 1,
    mousewheel: 1,
    reset: 1,
    resize: 1,
    select: 1,
    selectstart: 1,
    submit: 1,
    scroll: 1,
    textInput: 1,
    unload: 1
  };
  C.mix(H.DOM_EVENTS, C.Env.evt.plugins);
  H._instances = {};
  H.getDOMNode = function(L) {
    if (L) {
      return (L.nodeType) ? L : L._node || null;
    }
    return null;
  };
  H.scrubVal = function(M, L) {
    if (L && M) {
      if (typeof M === "object" || typeof M === "function") {
        if (J in M || F.isWindow(M)) {
          M = C.one(M);
        } else {
          if ((M.item && !M._nodes) || (M[0] && M[0][J])) {
            M = C.all(M);
          }
        }
      }
    } else {
      if (M === undefined) {
        M = L;
      } else {
        if (M === null) {
          M = null;
        }
      }
    }
    return M;
  };
  H.addMethod = function(L, N, M) {
    if (L && N && typeof N === "function") {
      H.prototype[L] = function() {
        M = M || this;
        var P = C.Array(arguments, 0, true),
          O;
        if (P[0] && P[0] instanceof H) {
          P[0] = P[0]._node;
        }
        if (P[1] && P[1] instanceof H) {
          P[1] = P[1]._node;
        }
        P.unshift(this._node);
        O = H.scrubVal(N.apply(M, P), this);
        return O;
      };
    } else {}
  };
  H.importMethod = function(N, L, M) {
    if (typeof L === "string") {
      M = M || L;
      H.addMethod(M, N[L], N);
    } else {
      C.Array.each(L, function(O) {
        H.importMethod(N, O);
      });
    }
  };
  H.one = function(O) {
    var L = null,
      N, M;
    if (O) {
      if (typeof O === "string") {
        if (O.indexOf("doc") === 0) {
          O = C.config.doc;
        } else {
          if (O.indexOf("win") === 0) {
            O = C.config.win;
          } else {
            O = C.Selector.query(O, null, true);
          }
        }
        if (!O) {
          return null;
        }
      } else {
        if (O instanceof H) {
          return O;
        }
      }
      if (O.nodeType || C.DOM.isWindow(O)) {
        M = (O.uniqueID && O.nodeType !== 9) ? O.uniqueID : O._yuid;
        L = H._instances[M];
        N = L ? L._node : null;
        if (!L || (N && O !== N)) {
          L = new H(O);
        }
      }
    }
    return L;
  };
  H.get = function() {
    return H.one.apply(H, arguments);
  };
  H.create = function() {
    return C.one(F.create.apply(F, arguments));
  };
  H.ATTRS = {
    text: {
      getter: function() {
        return F.getText(this._node);
      },
      setter: function(L) {
        F.setText(this._node, L);
        return L;
      }
    },
    "options": {
      getter: function() {
        return this._node.getElementsByTagName("option");
      }
    },
    "children": {
      getter: function() {
        var O = this._node,
          N = O.children,
          P, M, L;
        if (!N) {
          P = O.childNodes;
          N = [];
          for (M = 0, L = P.length; M < L; ++M) {
            if (P[M][I]) {
              N[N.length] = P[M];
            }
          }
        }
        return C.all(N);
      }
    },
    value: {
      getter: function() {
        return F.getValue(this._node);
      },
      setter: function(L) {
        F.setValue(this._node, L);
        return L;
      }
    },
    data: {
      getter: function() {
        return this._dataVal;
      },
      setter: function(L) {
        this._dataVal = L;
        return L;
      },
      value: null
    }
  };
  H.DEFAULT_SETTER = function(L, N) {
    var M = this._stateProxy,
      O;
    if (L.indexOf(G) > -1) {
      O = L;
      L = L.split(G);
      C.Object.setValue(M, L, N);
    } else {
      if (M[L] !== undefined) {
        M[L] = N;
      }
    }
    return N;
  };
  H.DEFAULT_GETTER = function(L) {
    var M = this._stateProxy,
      N;
    if (L.indexOf && L.indexOf(G) > -1) {
      N = C.Object.getValue(M, L.split(G));
    } else {
      if (M[L] !== undefined) {
        N = M[L];
      }
    }
    return N;
  };
  C.mix(H, C.EventTarget, false, null, 1);
  C.mix(H.prototype, {
    toString: function() {
      var O = this[D] + ": not bound to a node",
        N = this._node,
        L, P, M;
      if (N) {
        L = N.attributes;
        P = (L && L.id) ? N.getAttribute("id") : null;
        M = (L && L.className) ? N.getAttribute("className") : null;
        O = N[E];
        if (P) {
          O += "#" + P;
        }
        if (M) {
          O += "." + M.replace(" ", ".");
        }
        O += " " + this[D];
      }
      return O;
    },
    get: function(L) {
      var M;
      if (this._getAttr) {
        M = this._getAttr(L);
      } else {
        M = this._get(L);
      }
      if (M) {
        M = H.scrubVal(M, this);
      } else {
        if (M === null) {
          M = null;
        }
      }
      return M;
    },
    _get: function(L) {
      var M = H.ATTRS[L],
        N;
      if (M && M.getter) {
        N = M.getter.call(this);
      } else {
        if (H.re_aria.test(L)) {
          N = this._node.getAttribute(L, 2);
        } else {
          N = H.DEFAULT_GETTER.apply(this, arguments);
        }
      }
      return N;
    },
    set: function(L, N) {
      var M = H.ATTRS[L];
      if (this._setAttr) {
        this._setAttr.apply(this, arguments);
      } else {
        if (M && M.setter) {
          M.setter.call(this, N);
        } else {
          if (H.re_aria.test(L)) {
            this._node.setAttribute(L, N);
          } else {
            H.DEFAULT_SETTER.apply(this, arguments);
          }
        }
      }
      return this;
    },
    setAttrs: function(L) {
      if (this._setAttrs) {
        this._setAttrs(L);
      } else {
        C.Object.each(L, function(M, N) {
          this.set(N, M);
        }, this);
      }
      return this;
    },
    getAttrs: function(M) {
      var L = {};
      if (this._getAttrs) {
        this._getAttrs(M);
      } else {
        C.Array.each(M, function(N, O) {
          L[N] = this.get(N);
        }, this);
      }
      return L;
    },
    create: H.create,
    compareTo: function(L) {
      var M = this._node;
      if (L instanceof H) {
        L = L._node;
      }
      return M === L;
    },
    inDoc: function(M) {
      var L = this._node;
      M = (M) ? M._node || M : L[B];
      if (M.documentElement) {
        return F.contains(M.documentElement, L);
      }
    },
    getById: function(N) {
      var M = this._node,
        L = F.byId(N, M[B]);
      if (L && F.contains(M, L)) {
        L = C.one(L);
      } else {
        L = null;
      }
      return L;
    },
    ancestor: function(L, M) {
      return C.one(F.ancestor(this._node, K(L), M));
    },
    previous: function(M, L) {
      return C.one(F.elementByAxis(this._node, "previousSibling", K(M), L));
    },
    next: function(M, L) {
      return C.one(F.elementByAxis(this._node, "nextSibling", K(M), L));
    },
    siblings: function(L) {
      return C.all(F.siblings(this._node, K(L)));
    },
    one: function(L) {
      return C.one(C.Selector.query(L, this._node, true));
    },
    query: function(L) {
      return this.one(L);
    },
    all: function(L) {
      var M = C.all(C.Selector.query(L, this._node));
      M._query = L;
      M._queryRoot = this._node;
      return M;
    },
    queryAll: function(L) {
      return this.all(L);
    },
    test: function(L) {
      return C.Selector.test(this._node, L);
    },
    remove: function(M) {
      var N = this._node,
        L = N.parentNode;
      if (L) {
        L.removeChild(N);
      }
      if (M) {
        this.destroy(true);
      }
      return this;
    },
    replace: function(L) {
      var M = this._node;
      M.parentNode.replaceChild(H.getDOMNode(L), M);
      return this;
    },
    purge: function(M, L) {
      C.Event.purgeElement(this._node, M, L);
      return this;
    },
    destroy: function(L) {
      delete H._instances[this[D]];
      this.purge(L);
      if (this.unplug) {
        this.unplug();
      }
      this._node._yuid = null;
      this._node = null;
      this._stateProxy = null;
    },
    invoke: function(S, M, L, R, Q, P) {
      var O = this._node,
        N;
      if (M && M instanceof H) {
        M = M._node;
      }
      if (L && L instanceof H) {
        L = L._node;
      }
      N = O[S](M, L, R, Q, P);
      return H.scrubVal(N, this);
    },
    each: function(M, L) {
      L = L || this;
      return M.call(L, this);
    },
    item: function(L) {
      return this;
    },
    size: function() {
      return this._node ? 1 : 0;
    },
    insert: function(N, L) {
      var M = this._node;
      if (N) {
        if (typeof L === "number") {
          L = this._node.childNodes[L];
        } else {
          if (L && L._node) {
            L = L._node;
          }
        }
        if (typeof N !== "string") {
          if (N._node) {
            N = N._node;
          } else {
            if (N._nodes || (!N.nodeType && N.length)) {
              N = C.all(N);
              C.each(N._nodes, function(O) {
                F.addHTML(M, O, L);
              });
              return this;
            }
          }
        }
        F.addHTML(M, N, L);
      } else {}
      return this;
    },
    prepend: function(L) {
      return this.insert(L, 0);
    },
    append: function(L) {
      return this.insert(L, null);
    },
    setContent: function(L) {
      if (L) {
        if (L._node) {
          L = L._node;
        } else {
          if (L._nodes) {
            L = F._nl2frag(L._nodes);
          }
        }
      }
      F.addHTML(this._node, L, "replace");
      return this;
    },
    swap: C.config.doc.documentElement.swapNode ? function(L) {
      this._node.swapNode(H.getDOMNode(L));
    } : function(L) {
      L = H.getDOMNode(L);
      var N = this._node,
        M = L.parentNode,
        O = L.nextSibling;
      if (O === N) {
        M.insertBefore(N, L);
      } else {
        if (L === N.nextSibling) {
          M.insertBefore(L, N);
        } else {
          N.parentNode.replaceChild(L, N);
          F.addHTML(M, N, O);
        }
      }
      return this;
    },
    getData: function(M) {
      var L;
      this._data = this._data || {};
      if (arguments.length) {
        L = this._data[M];
      } else {
        L = this._data;
      }
      return L;
    },
    setData: function(L, M) {
      this._data = this._data || {};
      if (arguments.length > 1) {
        this._data[L] = M;
      } else {
        this._data = L;
      }
      return this;
    },
    clearData: function(L) {
      if (this._data && arguments.length) {
        delete this._data[L];
      } else {
        this._data = {};
      }
      return this;
    },
    hasMethod: function(M) {
      var L = this._node;
      return !!(L && M in L && typeof L[M] !== "unknown" && (typeof L[M] === "function" || String(L[M]).indexOf("function") === 1));
    }
  }, true);
  C.Node = H;
  C.get = C.Node.get;
  C.one = C.Node.one;
  var A = function(L) {
    var M = [];
    if (typeof L === "string") {
      this._query = L;
      L = C.Selector.query(L);
    } else {
      if (L.nodeType || F.isWindow(L)) {
        L = [L];
      } else {
        if (L instanceof C.Node) {
          L = [L._node];
        } else {
          if (L[0] instanceof C.Node) {
            C.Array.each(L, function(N) {
              if (N._node) {
                M.push(N._node);
              }
            });
            L = M;
          } else {
            L = C.Array(L, 0, true);
          }
        }
      }
    }
    this._nodes = L;
  };
  A.NAME = "NodeList";
  A.getDOMNodes = function(L) {
    return L._nodes;
  };
  A.each = function(L, O, N) {
    var M = L._nodes;
    if (M && M.length) {
      C.Array.each(M, O, N || L);
    } else {}
  };
  A.addMethod = function(L, N, M) {
    if (L && N) {
      A.prototype[L] = function() {
        var P = [],
          O = arguments;
        C.Array.each(this._nodes, function(U) {
          var T = (U.uniqueID && U.nodeType !== 9) ? "uniqueID" : "_yuid",
            R = C.Node._instances[U[T]],
            S, Q;
          if (!R) {
            R = A._getTempNode(U);
          }
          S = M || R;
          Q = N.apply(S, O);
          if (Q !== undefined && Q !== R) {
            P[P.length] = Q;
          }
        });
        return P.length ? P : this;
      };
    } else {}
  };
  A.importMethod = function(N, L, M) {
    if (typeof L === "string") {
      M = M || L;
      A.addMethod(L, N[L]);
    } else {
      C.Array.each(L, function(O) {
        A.importMethod(N, O);
      });
    }
  };
  A._getTempNode = function(M) {
    var L = A._tempNode;
    if (!L) {
      L = C.Node.create("<div></div>");
      A._tempNode = L;
    }
    L._node = M;
    L._stateProxy = M;
    return L;
  };
  C.mix(A.prototype, {
    item: function(L) {
      return C.one((this._nodes || [])[L]);
    },
    each: function(N, M) {
      var L = this;
      C.Array.each(this._nodes, function(P, O) {
        P = C.one(P);
        return N.call(M || P, P, O, L);
      });
      return L;
    },
    batch: function(M, L) {
      var N = this;
      C.Array.each(this._nodes, function(Q, P) {
        var O = C.Node._instances[Q[D]];
        if (!O) {
          O = A._getTempNode(Q);
        }
        return M.call(L || O, O, P, N);
      });
      return N;
    },
    some: function(N, M) {
      var L = this;
      return C.Array.some(this._nodes, function(P, O) {
        P = C.one(P);
        M = M || P;
        return N.call(M, P, O, L);
      });
    },
    toFrag: function() {
      return C.one(C.DOM._nl2frag(this._nodes));
    },
    indexOf: function(L) {
      return C.Array.indexOf(this._nodes, C.Node.getDOMNode(L));
    },
    filter: function(L) {
      return C.all(C.Selector.filter(this._nodes, L));
    },
    modulus: function(N, M) {
      M = M || 0;
      var L = [];
      A.each(this, function(P, O) {
        if (O % N === M) {
          L.push(P);
        }
      });
      return C.all(L);
    },
    odd: function() {
      return this.modulus(2, 1);
    },
    even: function() {
      return this.modulus(2);
    },
    destructor: function() {},
    refresh: function() {
      var O, M = this._nodes,
        N = this._query,
        L = this._queryRoot;
      if (N) {
        if (!L) {
          if (M && M[0] && M[0].ownerDocument) {
            L = M[0].ownerDocument;
          }
        }
        this._nodes = C.Selector.query(N, L);
      }
      return this;
    },
    _prepEvtArgs: function(O, N, M) {
      var L = C.Array(arguments, 0, true);
      if (L.length < 2) {
        L[2] = this._nodes;
      } else {
        L.splice(2, 0, this._nodes);
      }
      L[3] = M || this;
      return L;
    },
    on: function(N, M, L) {
      return C.on.apply(C, this._prepEvtArgs.apply(this, arguments));
    },
    after: function(N, M, L) {
      return C.after.apply(C, this._prepEvtArgs.apply(this, arguments));
    },
    size: function() {
      return this._nodes.length;
    },
    isEmpty: function() {
      return this._nodes.length < 1;
    },
    toString: function() {
      var O = "",
        N = this[D] + ": not bound to any nodes",
        L = this._nodes,
        M;
      if (L && L[0]) {
        M = L[0];
        O += M[E];
        if (M.id) {
          O += "#" + M.id;
        }
        if (M.className) {
          O += "." + M.className.replace(" ", ".");
        }
        if (L.length > 1) {
          O += "...[" + L.length + " items]";
        }
      }
      return O || N;
    }
  }, true);
  A.importMethod(C.Node.prototype, ["append", "detach", "detachAll", "insert", "prepend", "remove", "set", "setContent"]);
  A.prototype.get = function(M) {
    var P = [],
      O = this._nodes,
      N = false,
      Q = A._getTempNode,
      L, R;
    if (O[0]) {
      L = C.Node._instances[O[0]._yuid] || Q(O[0]);
      R = L._get(M);
      if (R && R.nodeType) {
        N = true;
      }
    }
    C.Array.each(O, function(S) {
      L = C.Node._instances[S._yuid];
      if (!L) {
        L = Q(S);
      }
      R = L._get(M);
      if (!N) {
        R = C.Node.scrubVal(R, L);
      }
      P.push(R);
    });
    return (N) ? C.all(P) : P;
  };
  C.NodeList = A;
  C.all = function(L) {
    return new A(L);
  };
  C.Node.all = C.all;
  C.Array.each(["replaceChild", "appendChild", "insertBefore", "removeChild", "hasChildNodes", "cloneNode", "hasAttribute", "removeAttribute", "scrollIntoView", "getElementsByTagName", "focus", "blur", "submit", "reset", "select"], function(L) {
    C.Node.prototype[L] = function(P, N, M) {
      var O = this.invoke(L, P, N, M);
      return O;
    };
  });
  C.Node.importMethod(C.DOM, ["contains", "setAttribute", "getAttribute"]);
  C.NodeList.importMethod(C.Node.prototype, ["getAttribute", "setAttribute", "removeAttribute"]);
  (function(M) {
    var L = ["hasClass", "addClass", "removeClass", "replaceClass", "toggleClass"];
    M.Node.importMethod(M.DOM, L);
    M.NodeList.importMethod(M.Node.prototype, L);
  })(C);
  if (!C.config.doc.documentElement.hasAttribute) {
    C.Node.prototype.hasAttribute = function(L) {
      if (L === "value") {
        if (this.get("value") !== "") {
          return true;
        }
      }
      return !!(this._node.attributes[L] && this._node.attributes[L].specified);
    };
  }
  C.Node.ATTRS.type = {
    setter: function(M) {
      if (M === "hidden") {
        try {
          this._node.type = "hidden";
        } catch (L) {
          this.setStyle("display", "none");
          this._inputType = "hidden";
        }
      } else {
        try {
          this._node.type = M;
        } catch (L) {}
      }
      return M;
    },
    getter: function() {
      return this._inputType || this._node.type;
    },
    _bypassProxy: true
  };
  if (C.config.doc.createElement("form").elements.nodeType) {
    C.Node.ATTRS.elements = {
      getter: function() {
        return this.all("input, textarea, button, select");
      }
    };
  }
  C.mix(C.Node.ATTRS, {
    offsetHeight: {
      setter: function(L) {
        C.DOM.setHeight(this._node, L);
        return L;
      },
      getter: function() {
        return this._node.offsetHeight;
      }
    },
    offsetWidth: {
      setter: function(L) {
        C.DOM.setWidth(this._node, L);
        return L;
      },
      getter: function() {
        return this._node.offsetWidth;
      }
    }
  });
  C.mix(C.Node.prototype, {
    sizeTo: function(L, M) {
      var N;
      if (arguments.length < 2) {
        N = C.one(L);
        L = N.get("offsetWidth");
        M = N.get("offsetHeight");
      }
      this.setAttrs({
        offsetWidth: L,
        offsetHeight: M
      });
    }
  });
}, "3.2.0", {
  requires: ["dom-base", "selector-css2", "event-base"]
});
YUI.add("node-style", function(A) {
  (function(C) {
    var B = ["getStyle", "getComputedStyle", "setStyle", "setStyles"];
    C.Node.importMethod(C.DOM, B);
    C.NodeList.importMethod(C.Node.prototype, B);
  })(A);
}, "3.2.0", {
  requires: ["dom-style", "node-base"]
});
YUI.add("node-screen", function(A) {
  A.each(["winWidth", "winHeight", "docWidth", "docHeight", "docScrollX", "docScrollY"], function(B) {
    A.Node.ATTRS[B] = {
      getter: function() {
        var C = Array.prototype.slice.call(arguments);
        C.unshift(A.Node.getDOMNode(this));
        return A.DOM[B].apply(this, C);
      }
    };
  });
  A.Node.ATTRS.scrollLeft = {
    getter: function() {
      var B = A.Node.getDOMNode(this);
      return ("scrollLeft" in B) ? B.scrollLeft : A.DOM.docScrollX(B);
    },
    setter: function(C) {
      var B = A.Node.getDOMNode(this);
      if (B) {
        if ("scrollLeft" in B) {
          B.scrollLeft = C;
        } else {
          if (B.document || B.nodeType === 9) {
            A.DOM._getWin(B).scrollTo(C, A.DOM.docScrollY(B));
          }
        }
      } else {}
    }
  };
  A.Node.ATTRS.scrollTop = {
    getter: function() {
      var B = A.Node.getDOMNode(this);
      return ("scrollTop" in B) ? B.scrollTop : A.DOM.docScrollY(B);
    },
    setter: function(C) {
      var B = A.Node.getDOMNode(this);
      if (B) {
        if ("scrollTop" in B) {
          B.scrollTop = C;
        } else {
          if (B.document || B.nodeType === 9) {
            A.DOM._getWin(B).scrollTo(A.DOM.docScrollX(B), C);
          }
        }
      } else {}
    }
  };
  A.Node.importMethod(A.DOM, ["getXY", "setXY", "getX", "setX", "getY", "setY", "swapXY"]);
  A.Node.ATTRS.region = {
    getter: function() {
      var B = A.Node.getDOMNode(this),
        C;
      if (B && !B.tagName) {
        if (B.nodeType === 9) {
          B = B.documentElement;
        }
      }
      if (B.alert) {
        C = A.DOM.viewportRegion(B);
      } else {
        C = A.DOM.region(B);
      }
      return C;
    }
  };
  A.Node.ATTRS.viewportRegion = {
    getter: function() {
      return A.DOM.viewportRegion(A.Node.getDOMNode(this));
    }
  };
  A.Node.importMethod(A.DOM, "inViewportRegion");
  A.Node.prototype.intersect = function(B, D) {
    var C = A.Node.getDOMNode(this);
    if (B instanceof A.Node) {
      B = A.Node.getDOMNode(B);
    }
    return A.DOM.intersect(C, B, D);
  };
  A.Node.prototype.inRegion = function(B, D, E) {
    var C = A.Node.getDOMNode(this);
    if (B instanceof A.Node) {
      B = A.Node.getDOMNode(B);
    }
    return A.DOM.inRegion(C, B, D, E);
  };
}, "3.2.0", {
  requires: ["dom-screen"]
});
YUI.add("node-pluginhost", function(A) {
  A.Node.plug = function() {
    var B = A.Array(arguments);
    B.unshift(A.Node);
    A.Plugin.Host.plug.apply(A.Base, B);
    return A.Node;
  };
  A.Node.unplug = function() {
    var B = A.Array(arguments);
    B.unshift(A.Node);
    A.Plugin.Host.unplug.apply(A.Base, B);
    return A.Node;
  };
  A.mix(A.Node, A.Plugin.Host, false, null, 1);
  A.NodeList.prototype.plug = function() {
    var B = arguments;
    A.NodeList.each(this, function(C) {
      A.Node.prototype.plug.apply(A.one(C), B);
    });
  };
  A.NodeList.prototype.unplug = function() {
    var B = arguments;
    A.NodeList.each(this, function(C) {
      A.Node.prototype.unplug.apply(A.one(C), B);
    });
  };
}, "3.2.0", {
  requires: ["node-base", "pluginhost"]
});
YUI.add("node-event-delegate", function(A) {
  A.Node.prototype.delegate = function(E, D, B) {
    var C = A.Array(arguments, 0, true);
    C.splice(2, 0, this._node);
    return A.delegate.apply(A, C);
  };
}, "3.2.0", {
  requires: ["node-base", "event-delegate"]
});
YUI.add("node", function(A) {}, "3.2.0", {
  requires: ["dom", "event-base", "event-delegate", "pluginhost"],
  use: ["node-base", "node-style", "node-screen", "node-pluginhost", "node-event-delegate"],
  skinnable: false
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("cookie", function(C) {
  var K = C.Lang,
    I = C.Object,
    G = null,
    D = K.isString,
    P = K.isObject,
    F = K.isUndefined,
    E = K.isFunction,
    H = encodeURIComponent,
    B = decodeURIComponent,
    N = C.config.doc;

  function J(L) {
    throw new TypeError(L);
  }

  function M(L) {
    if (!D(L) || L === "") {
      J("Cookie name must be a non-empty string.");
    }
  }

  function A(L) {
    if (!D(L) || L === "") {
      J("Subcookie name must be a non-empty string.");
    }
  }
  C.Cookie = {
    _createCookieString: function(Q, T, R, O) {
      O = O || {};
      var V = H(Q) + "=" + (R ? H(T) : T),
        L = O.expires,
        U = O.path,
        S = O.domain;
      if (P(O)) {
        if (L instanceof Date) {
          V += "; expires=" + L.toUTCString();
        }
        if (D(U) && U !== "") {
          V += "; path=" + U;
        }
        if (D(S) && S !== "") {
          V += "; domain=" + S;
        }
        if (O.secure === true) {
          V += "; secure";
        }
      }
      return V;
    },
    _createCookieHashString: function(L) {
      if (!P(L)) {
        J("Cookie._createCookieHashString(): Argument must be an object.");
      }
      var O = [];
      I.each(L, function(R, Q) {
        if (!E(R) && !F(R)) {
          O.push(H(Q) + "=" + H(String(R)));
        }
      });
      return O.join("&");
    },
    _parseCookieHash: function(S) {
      var R = S.split("&"),
        T = G,
        Q = {};
      if (S.length) {
        for (var O = 0, L = R.length; O < L; O++) {
          T = R[O].split("=");
          Q[B(T[0])] = B(T[1]);
        }
      }
      return Q;
    },
    _parseCookieString: function(W, Y) {
      var X = {};
      if (D(W) && W.length > 0) {
        var L = (Y === false ? function(Z) {
            return Z;
          } : B),
          U = W.split(/;\s/g),
          V = G,
          O = G,
          R = G;
        for (var Q = 0, S = U.length; Q < S; Q++) {
          R = U[Q].match(/([^=]+)=/i);
          if (R instanceof Array) {
            try {
              V = B(R[1]);
              O = L(U[Q].substring(R[1].length + 1));
            } catch (T) {}
          } else {
            V = B(U[Q]);
            O = "";
          }
          X[V] = O;
        }
      }
      return X;
    },
    _setDoc: function(L) {
      N = L;
    },
    exists: function(L) {
      M(L);
      var O = this._parseCookieString(N.cookie, true);
      return O.hasOwnProperty(L);
    },
    get: function(O, L) {
      M(O);
      var S, Q, R;
      if (E(L)) {
        R = L;
        L = {};
      } else {
        if (P(L)) {
          R = L.converter;
        } else {
          L = {};
        }
      }
      S = this._parseCookieString(N.cookie, !L.raw);
      Q = S[O];
      if (F(Q)) {
        return G;
      }
      if (!E(R)) {
        return Q;
      } else {
        return R(Q);
      }
    },
    getSub: function(L, Q, O) {
      var R = this.getSubs(L);
      if (R !== G) {
        A(Q);
        if (F(R[Q])) {
          return G;
        }
        if (!E(O)) {
          return R[Q];
        } else {
          return O(R[Q]);
        }
      } else {
        return G;
      }
    },
    getSubs: function(L) {
      M(L);
      var O = this._parseCookieString(N.cookie, false);
      if (D(O[L])) {
        return this._parseCookieHash(O[L]);
      }
      return G;
    },
    remove: function(O, L) {
      M(O);
      L = C.merge(L || {}, {
        expires: new Date(0)
      });
      return this.set(O, "", L);
    },
    removeSub: function(O, S, L) {
      M(O);
      A(S);
      L = L || {};
      var R = this.getSubs(O);
      if (P(R) && R.hasOwnProperty(S)) {
        delete R[S];
        if (!L.removeIfEmpty) {
          return this.setSubs(O, R, L);
        } else {
          for (var Q in R) {
            if (R.hasOwnProperty(Q) && !E(R[Q]) && !F(R[Q])) {
              return this.setSubs(O, R, L);
            }
          }
          return this.remove(O, L);
        }
      } else {
        return "";
      }
    },
    set: function(O, Q, L) {
      M(O);
      if (F(Q)) {
        J("Cookie.set(): Value cannot be undefined.");
      }
      L = L || {};
      var R = this._createCookieString(O, Q, !L.raw, L);
      N.cookie = R;
      return R;
    },
    setSub: function(O, R, Q, L) {
      M(O);
      A(R);
      if (F(Q)) {
        J("Cookie.setSub(): Subcookie value cannot be undefined.");
      }
      var S = this.getSubs(O);
      if (!P(S)) {
        S = {};
      }
      S[R] = Q;
      return this.setSubs(O, S, L);
    },
    setSubs: function(O, Q, L) {
      M(O);
      if (!P(Q)) {
        J("Cookie.setSubs(): Cookie value must be an object.");
      }
      var R = this._createCookieString(O, this._createCookieHashString(Q), false, L);
      N.cookie = R;
      return R;
    }
  };
}, "3.2.0", {
  requires: ["yui-base"]
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("transition-native", function(B) {
  var I = "-webkit-transition",
    G = "WebkitTransition",
    C = "-webkit-transition-property",
    F = "-webkit-transition-duration",
    A = "-webkit-transition-timing-function",
    D = "-webkit-transition-delay",
    J = "webkitTransitionEnd",
    K = "WebkitTransform",
    H = {},
    E = function() {
      this.init.apply(this, arguments);
    };
  E._toCamel = function(L) {
    L = L.replace(/-([a-z])/gi, function(N, M) {
      return M.toUpperCase();
    });
    return L;
  };
  E._toHyphen = function(L) {
    L = L.replace(/([A-Z]?)([a-z]+)([A-Z]?)/g, function(P, O, N, M) {
      var Q = "";
      if (O) {
        Q += "-" + O.toLowerCase();
      }
      Q += N;
      if (M) {
        Q += "-" + M.toLowerCase();
      }
      return Q;
    });
    return L;
  };
  E._reKeywords = /^(?:node|duration|iterations|easing|delay)$/;
  E.useNative = false;
  if (I in B.config.doc.documentElement.style) {
    E.useNative = true;
    E.supported = true;
  }
  B.Node.DOM_EVENTS[J] = 1;
  E.NAME = "transition";
  E.DEFAULT_EASING = "ease";
  E.DEFAULT_DURATION = 0.5;
  E.DEFAULT_DELAY = 0;
  E._nodeAttrs = {};
  E.prototype = {
    constructor: E,
    init: function(M, L) {
      var N = this;
      if (!N._running) {
        N._node = M;
        N._config = L;
        M._transition = N;
        N._duration = ("duration" in L) ? L.duration : N.constructor.DEFAULT_DURATION;
        N._delay = ("delay" in L) ? L.delay : N.constructor.DEFAULT_DELAY;
        N._easing = L.easing || N.constructor.DEFAULT_EASING;
        N._count = 0;
        N._running = false;
        N.initAttrs(L);
      }
      return N;
    },
    addProperty: function(S, N) {
      var Q = this,
        P = this._node,
        O = B.stamp(P),
        M = E._nodeAttrs[O],
        L, R;
      if (!M) {
        M = E._nodeAttrs[O] = {};
      }
      L = M[S];
      if (N && N.value !== undefined) {
        R = N.value;
      } else {
        if (N !== undefined) {
          R = N;
          N = H;
        }
      }
      if (typeof R === "function") {
        R = R.call(P, P);
      }
      if (L && L.transition && L.transition !== Q) {
        L.transition._count--;
      }
      Q._count++;
      M[S] = {
        value: R,
        duration: ((typeof N.duration !== "undefined") ? N.duration : Q._duration) || 0.0001,
        delay: (typeof N.delay !== "undefined") ? N.delay : Q._delay,
        easing: N.easing || Q._easing,
        transition: Q
      };
    },
    removeProperty: function(N) {
      var M = this,
        L = E._nodeAttrs[B.stamp(M._node)];
      if (L && L[N]) {
        delete L[N];
        M._count--;
      }
    },
    initAttrs: function(M) {
      var L;
      if (M.transform && !M[K]) {
        M[K] = M.transform;
        delete M.transform;
      }
      for (L in M) {
        if (M.hasOwnProperty(L) && !E._reKeywords.test(L)) {
          this.addProperty(L, M[L]);
        }
      }
    },
    run: function(M) {
      var L = this;
      if (!L._running) {
        L._running = true;
        L._node.fire("transition:start", {
          type: "transition:start",
          config: L._config
        });
        L._start();
        L._callback = M;
      }
      return L;
    },
    _start: function() {
      this._runNative();
    },
    _prepDur: function(L) {
      L = parseFloat(L);
      return L + "s";
    },
    _runNative: function(O) {
      var T = this,
        P = T._node,
        W = B.stamp(P),
        U = P._node,
        M = U.style,
        R = getComputedStyle(U),
        a = E._nodeAttrs[W],
        N = "",
        b = R[C],
        Z = C + ": ",
        S = F + ": ",
        Y = A + ": ",
        V = D + ": ",
        Q, X, L;
      if (b !== "all") {
        Z += b + ",";
        S += R[F] + ",";
        Y += R[A] + ",";
        V += R[D] + ",";
      }
      for (L in a) {
        Q = E._toHyphen(L);
        X = a[L];
        if (a.hasOwnProperty(L) && X.transition === T) {
          if (L in U.style) {
            S += T._prepDur(X.duration) + ",";
            V += T._prepDur(X.delay) + ",";
            Y += (X.easing) + ",";
            Z += Q + ",";
            N += Q + ": " + X.value + "; ";
          } else {
            this.removeProperty(L);
          }
        }
      }
      Z = Z.replace(/,$/, ";");
      S = S.replace(/,$/, ";");
      Y = Y.replace(/,$/, ";");
      V = V.replace(/,$/, ";");
      if (!P._hasTransitionEnd) {
        T._detach = P.on(J, T._onNativeEnd);
        P._hasTransitionEnd = true;
      }
      M.cssText += Z + S + Y + V + N;
    },
    _end: function(L) {
      var O = this,
        M = O._node,
        P = O._callback,
        N = {
          type: "transition:end",
          config: O._config,
          elapsedTime: L
        };
      O._running = false;
      if (P) {
        O._callback = null;
        setTimeout(function() {
          P.call(M, N);
        }, 1);
      }
      M.fire("transition:end", N);
    },
    _endNative: function(L) {
      var M = this._node,
        N = M.getComputedStyle(C);
      if (typeof N === "string") {
        N = N.replace(new RegExp("(?:^|,\\s)" + L + ",?"), ",");
        N = N.replace(/^,|,$/, "");
        M.setStyle(G, N);
      }
    },
    _onNativeEnd: function(Q) {
      var N = this,
        P = B.stamp(N),
        L = Q._event,
        M = E._toCamel(L.propertyName),
        T = L.elapsedTime,
        S = E._nodeAttrs[P],
        R = S[M],
        O = (R) ? R.transition : null;
      if (O) {
        O.removeProperty(M);
        O._endNative(M);
        N.fire("transition:propertyEnd", {
          type: "propertyEnd",
          propertyName: M,
          elapsedTime: T
        });
        if (O._count <= 0) {
          O._end(T);
        }
      }
    },
    destroy: function() {
      var L = this;
      if (L._detach) {
        L._detach.detach();
      }
      L._node = null;
    }
  };
  B.Transition = E;
  B.TransitionNative = E;
  B.Node.prototype.transition = function(L, N) {
    var M = this._transition;
    if (M && !M._running) {
      M.init(this, L);
    } else {
      M = new E(this, L);
    }
    M.run(N);
    return this;
  };
  B.NodeList.prototype.transition = function(L, M) {
    this.each(function(N) {
      N.transition(L, M);
    });
    return this;
  };
}, "3.2.0", {
  requires: ["node-base"]
});
YUI.add("transition-timer", function(B) {
  var A = B.Transition;
  B.mix(A.prototype, {
    _start: function() {
      if (A.useNative) {
        this._runNative();
      } else {
        this._runTimer();
      }
    },
    _runTimer: function() {
      var C = this;
      C._initAttrs();
      A._running[B.stamp(C)] = C;
      C._startTime = new Date();
      A._startTimer();
    },
    _endTimer: function() {
      var C = this;
      delete A._running[B.stamp(C)];
      C._startTime = null;
    },
    _runFrame: function() {
      var C = new Date() - this._startTime;
      this._runAttrs(C);
    },
    _runAttrs: function(G) {
      var J = this,
        H = J._node,
        N = B.stamp(H),
        Q = A._nodeAttrs[N],
        F = A.behaviors,
        K = false,
        D = false,
        C, E, I, P, M, O, R, L;
      for (C in Q) {
        E = Q[C];
        if ((E && E.transition === J)) {
          O = E.duration;
          M = E.delay;
          P = (G - M) / 1000;
          R = G;
          I = (L in F && "set" in F[L]) ? F[L].set : A.DEFAULT_SETTER;
          K = (R >= O);
          if (R > O) {
            R = O;
          }
          if (!M || G >= M) {
            I(J, C, E.from, E.to, R - M, O - M, E.easing, E.unit);
            if (K) {
              delete Q[C];
              J._count--;
              H.fire("transition:propertyEnd", {
                type: "propertyEnd",
                propertyName: C,
                config: J._config,
                elapsedTime: P
              });
              if (!D && J._count <= 0) {
                D = true;
                J._end(P);
                J._endTimer();
              }
            }
          }
        }
      }
    },
    _initAttrs: function() {
      var J = this,
        E = A.behaviors,
        L = B.stamp(J._node),
        Q = A._nodeAttrs[L],
        D, I, K, N, G, C, M, O, P, F, H;
      for (C in Q) {
        D = Q[C];
        if (Q.hasOwnProperty(C) && (D && D.transition === J)) {
          I = D.duration * 1000;
          K = D.delay * 1000;
          N = D.easing;
          G = D.value;
          if (C in J._node._node.style || C in B.DOM.CUSTOM_STYLES) {
            F = (C in E && "get" in E[C]) ? E[C].get(J, C) : A.DEFAULT_GETTER(J, C);
            O = A.RE_UNITS.exec(F);
            M = A.RE_UNITS.exec(G);
            F = O ? O[1] : F;
            H = M ? M[1] : G;
            P = M ? M[2] : O ? O[2] : "";
            if (!P && A.RE_DEFAULT_UNIT.test(C)) {
              P = A.DEFAULT_UNIT;
            }
            if (typeof N === "string") {
              if (N.indexOf("cubic-bezier") > -1) {
                N = N.substring(13, N.length - 1).split(",");
              } else {
                if (A.easings[N]) {
                  N = A.easings[N];
                }
              }
            }
            D.from = Number(F);
            D.to = Number(H);
            D.unit = P;
            D.easing = N;
            D.duration = I + K;
            D.delay = K;
          } else {
            delete Q[C];
            J._count--;
          }
        }
      }
    },
    destroy: function() {
      this.detachAll();
      this._node = null;
    }
  }, true);
  B.mix(B.Transition, {
    _runtimeAttrs: {},
    RE_DEFAULT_UNIT: /^width|height|top|right|bottom|left|margin.*|padding.*|border.*$/i,
    DEFAULT_UNIT: "px",
    intervalTime: 20,
    behaviors: {
      left: {
        get: function(D, C) {
          return B.DOM._getAttrOffset(D._node._node, C);
        }
      }
    },
    DEFAULT_SETTER: function(F, G, I, J, L, E, H, K) {
      I = Number(I);
      J = Number(J);
      var D = F._node,
        C = A.cubicBezier(H, L / E);
      C = I + C[0] * (J - I);
      if (G in D._node.style || G in B.DOM.CUSTOM_STYLES) {
        K = K || "";
        D.setStyle(G, C + K);
      } else {
        if (D._node.attributes[G]) {
          D.setAttribute(G, C);
        } else {
          D.set(G, C);
        }
      }
    },
    DEFAULT_GETTER: function(E, C) {
      var D = E._node,
        F = "";
      if (C in D._node.style || C in B.DOM.CUSTOM_STYLES) {
        F = D.getComputedStyle(C);
      } else {
        if (D._node.attributes[C]) {
          F = D.getAttribute(C);
        } else {
          F = D.get(C);
        }
      }
      return F;
    },
    _startTimer: function() {
      if (!A._timer) {
        A._timer = setInterval(A._runFrame, A.intervalTime);
      }
    },
    _stopTimer: function() {
      clearInterval(A._timer);
      A._timer = null;
    },
    _runFrame: function() {
      var C = true,
        D;
      for (D in A._running) {
        if (A._running[D]._runFrame) {
          C = false;
          A._running[D]._runFrame();
        }
      }
      if (C) {
        A._stopTimer();
      }
    },
    cubicBezier: function(X, S) {
      var b = 0,
        L = 0,
        a = X[0],
        K = X[1],
        Z = X[2],
        J = X[3],
        Y = 1,
        I = 0,
        W = Y - 3 * Z + 3 * a - b,
        V = 3 * Z - 6 * a + 3 * b,
        U = 3 * a - 3 * b,
        T = b,
        R = I - 3 * J + 3 * K - L,
        Q = 3 * J - 6 * K + 3 * L,
        P = 3 * K - 3 * L,
        O = L,
        N = (((W * S) + V) * S + U) * S + T,
        M = (((R * S) + Q) * S + P) * S + O;
      return [N, M];
    },
    easings: {
      ease: [0.25, 0, 1, 0.25],
      linear: [0, 0, 1, 1],
      "ease-in": [0.42, 0, 1, 1],
      "ease-out": [0, 0, 0.58, 1],
      "ease-in-out": [0.42, 0, 0.58, 1]
    },
    _running: {},
    _timer: null,
    RE_UNITS: /^(-?\d*\.?\d*){1}(em|ex|px|in|cm|mm|pt|pc|%)*$/
  }, true);
  A.behaviors.top = A.behaviors.bottom = A.behaviors.right = A.behaviors.left;
  B.Transition = A;
}, "3.2.0", {
  requires: ["transition-native", "node-style"]
});
YUI.add("transition", function(A) {}, "3.2.0", {
  use: ["transition-native", "transition-timer"]
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("anim-base", function(B) {
  var C = "running",
    N = "startTime",
    L = "elapsedTime",
    J = "start",
    I = "tween",
    M = "end",
    D = "node",
    K = "paused",
    O = "reverse",
    H = "iterationCount",
    A = Number;
  var F = {},
    E;
  B.Anim = function() {
    B.Anim.superclass.constructor.apply(this, arguments);
    B.Anim._instances[B.stamp(this)] = this;
  };
  B.Anim.NAME = "anim";
  B.Anim._instances = {};
  B.Anim.RE_DEFAULT_UNIT = /^width|height|top|right|bottom|left|margin.*|padding.*|border.*$/i;
  B.Anim.DEFAULT_UNIT = "px";
  B.Anim.DEFAULT_EASING = function(Q, P, S, R) {
    return S * Q / R + P;
  };
  B.Anim._intervalTime = 20;
  B.Anim.behaviors = {
    left: {
      get: function(Q, P) {
        return Q._getOffset(P);
      }
    }
  };
  B.Anim.behaviors.top = B.Anim.behaviors.left;
  B.Anim.DEFAULT_SETTER = function(S, T, V, W, Y, R, U, X) {
    var Q = S._node,
      P = U(Y, A(V), A(W) - A(V), R);
    if (T in Q._node.style || T in B.DOM.CUSTOM_STYLES) {
      X = X || "";
      Q.setStyle(T, P + X);
    } else {
      if (Q._node.attributes[T]) {
        Q.setAttribute(T, P);
      } else {
        Q.set(T, P);
      }
    }
  };
  B.Anim.DEFAULT_GETTER = function(R, P) {
    var Q = R._node,
      S = "";
    if (P in Q._node.style || P in B.DOM.CUSTOM_STYLES) {
      S = Q.getComputedStyle(P);
    } else {
      if (Q._node.attributes[P]) {
        S = Q.getAttribute(P);
      } else {
        S = Q.get(P);
      }
    }
    return S;
  };
  B.Anim.ATTRS = {
    node: {
      setter: function(P) {
        P = B.one(P);
        this._node = P;
        if (!P) {}
        return P;
      }
    },
    duration: {
      value: 1
    },
    easing: {
      value: B.Anim.DEFAULT_EASING,
      setter: function(P) {
        if (typeof P === "string" && B.Easing) {
          return B.Easing[P];
        }
      }
    },
    from: {},
    to: {},
    startTime: {
      value: 0,
      readOnly: true
    },
    elapsedTime: {
      value: 0,
      readOnly: true
    },
    running: {
      getter: function() {
        return !!F[B.stamp(this)];
      },
      value: false,
      readOnly: true
    },
    iterations: {
      value: 1
    },
    iterationCount: {
      value: 0,
      readOnly: true
    },
    direction: {
      value: "normal"
    },
    paused: {
      readOnly: true,
      value: false
    },
    reverse: {
      value: false
    }
  };
  B.Anim.run = function() {
    var Q = B.Anim._instances;
    for (var P in Q) {
      if (Q[P].run) {
        Q[P].run();
      }
    }
  };
  B.Anim.pause = function() {
    for (var P in F) {
      if (F[P].pause) {
        F[P].pause();
      }
    }
    B.Anim._stopTimer();
  };
  B.Anim.stop = function() {
    for (var P in F) {
      if (F[P].stop) {
        F[P].stop();
      }
    }
    B.Anim._stopTimer();
  };
  B.Anim._startTimer = function() {
    if (!E) {
      E = setInterval(B.Anim._runFrame, B.Anim._intervalTime);
    }
  };
  B.Anim._stopTimer = function() {
    clearInterval(E);
    E = 0;
  };
  B.Anim._runFrame = function() {
    var P = true;
    for (var Q in F) {
      if (F[Q]._runFrame) {
        P = false;
        F[Q]._runFrame();
      }
    }
    if (P) {
      B.Anim._stopTimer();
    }
  };
  B.Anim.RE_UNITS = /^(-?\d*\.?\d*){1}(em|ex|px|in|cm|mm|pt|pc|%)*$/;
  var G = {
    run: function() {
      if (this.get(K)) {
        this._resume();
      } else {
        if (!this.get(C)) {
          this._start();
        }
      }
      return this;
    },
    pause: function() {
      if (this.get(C)) {
        this._pause();
      }
      return this;
    },
    stop: function(P) {
      if (this.get(C) || this.get(K)) {
        this._end(P);
      }
      return this;
    },
    _added: false,
    _start: function() {
      this._set(N, new Date() - this.get(L));
      this._actualFrames = 0;
      if (!this.get(K)) {
        this._initAnimAttr();
      }
      F[B.stamp(this)] = this;
      B.Anim._startTimer();
      this.fire(J);
    },
    _pause: function() {
      this._set(N, null);
      this._set(K, true);
      delete F[B.stamp(this)];
      this.fire("pause");
    },
    _resume: function() {
      this._set(K, false);
      F[B.stamp(this)] = this;
      this._set(N, new Date() - this.get(L));
      B.Anim._startTimer();
      this.fire("resume");
    },
    _end: function(P) {
      var Q = this.get("duration") * 1000;
      if (P) {
        this._runAttrs(Q, Q, this.get(O));
      }
      this._set(N, null);
      this._set(L, 0);
      this._set(K, false);
      delete F[B.stamp(this)];
      this.fire(M, {
        elapsed: this.get(L)
      });
    },
    _runFrame: function() {
      var T = this._runtimeAttr.duration,
        R = new Date() - this.get(N),
        Q = this.get(O),
        P = (R >= T),
        S, U;
      this._runAttrs(R, T, Q);
      this._actualFrames += 1;
      this._set(L, R);
      this.fire(I);
      if (P) {
        this._lastFrame();
      }
    },
    _runAttrs: function(Z, Y, V) {
      var W = this._runtimeAttr,
        R = B.Anim.behaviors,
        X = W.easing,
        P = Y,
        T = false,
        Q, S, U;
      if (Z >= Y) {
        T = true;
      }
      if (V) {
        Z = Y - Z;
        P = 0;
      }
      for (U in W) {
        if (W[U].to) {
          Q = W[U];
          S = (U in R && "set" in R[U]) ? R[U].set : B.Anim.DEFAULT_SETTER;
          if (!T) {
            S(this, U, Q.from, Q.to, Z, Y, X, Q.unit);
          } else {
            S(this, U, Q.from, Q.to, P, Y, X, Q.unit);
          }
        }
      }
    },
    _lastFrame: function() {
      var P = this.get("iterations"),
        Q = this.get(H);
      Q += 1;
      if (P === "infinite" || Q < P) {
        if (this.get("direction") === "alternate") {
          this.set(O, !this.get(O));
        }
        this.fire("iteration");
      } else {
        Q = 0;
        this._end();
      }
      this._set(N, new Date());
      this._set(H, Q);
    },
    _initAnimAttr: function() {
      var W = this.get("from") || {},
        V = this.get("to") || {},
        P = {
          duration: this.get("duration") * 1000,
          easing: this.get("easing")
        },
        R = B.Anim.behaviors,
        U = this.get(D),
        T, S, Q;
      B.each(V, function(a, Y) {
        if (typeof a === "function") {
          a = a.call(this, U);
        }
        S = W[Y];
        if (S === undefined) {
          S = (Y in R && "get" in R[Y]) ? R[Y].get(this, Y) : B.Anim.DEFAULT_GETTER(this, Y);
        } else {
          if (typeof S === "function") {
            S = S.call(this, U);
          }
        }
        var X = B.Anim.RE_UNITS.exec(S);
        var Z = B.Anim.RE_UNITS.exec(a);
        S = X ? X[1] : S;
        Q = Z ? Z[1] : a;
        T = Z ? Z[2] : X ? X[2] : "";
        if (!T && B.Anim.RE_DEFAULT_UNIT.test(Y)) {
          T = B.Anim.DEFAULT_UNIT;
        }
        if (!S || !Q) {
          B.error('invalid "from" or "to" for "' + Y + '"', "Anim");
          return;
        }
        P[Y] = {
          from: S,
          to: Q,
          unit: T
        };
      }, this);
      this._runtimeAttr = P;
    },
    _getOffset: function(Q) {
      var S = this._node,
        T = S.getComputedStyle(Q),
        R = (Q === "left") ? "getX" : "getY",
        U = (Q === "left") ? "setX" : "setY";
      if (T === "auto") {
        var P = S.getStyle("position");
        if (P === "absolute" || P === "fixed") {
          T = S[R]();
          S[U](T);
        } else {
          T = 0;
        }
      }
      return T;
    },
    destructor: function() {
      delete B.Anim._instances[B.stamp(this)];
    }
  };
  B.extend(B.Anim, B.Base, G);
}, "3.2.0", {
  requires: ["base-base", "node-style"]
});
/*
Copyright (c) 2010, Yahoo! Inc. All rights reserved.
Code licensed under the BSD License:
http://developer.yahoo.com/yui/license.html
version: 3.2.0
build: 2676
*/
YUI.add("anim-easing", function(B) {
  var A = {
    easeNone: function(D, C, F, E) {
      return F * D / E + C;
    },
    easeIn: function(D, C, F, E) {
      return F * (D /= E) * D + C;
    },
    easeOut: function(D, C, F, E) {
      return -F * (D /= E) * (D - 2) + C;
    },
    easeBoth: function(D, C, F, E) {
      if ((D /= E / 2) < 1) {
        return F / 2 * D * D + C;
      }
      return -F / 2 * ((--D) * (D - 2) - 1) + C;
    },
    easeInStrong: function(D, C, F, E) {
      return F * (D /= E) * D * D * D + C;
    },
    easeOutStrong: function(D, C, F, E) {
      return -F * ((D = D / E - 1) * D * D * D - 1) + C;
    },
    easeBothStrong: function(D, C, F, E) {
      if ((D /= E / 2) < 1) {
        return F / 2 * D * D * D * D + C;
      }
      return -F / 2 * ((D -= 2) * D * D * D - 2) + C;
    },
    elasticIn: function(E, C, I, H, D, G) {
      var F;
      if (E === 0) {
        return C;
      }
      if ((E /= H) === 1) {
        return C + I;
      }
      if (!G) {
        G = H * 0.3;
      }
      if (!D || D < Math.abs(I)) {
        D = I;
        F = G / 4;
      } else {
        F = G / (2 * Math.PI) * Math.asin(I / D);
      }
      return -(D * Math.pow(2, 10 * (E -= 1)) * Math.sin((E * H - F) * (2 * Math.PI) / G)) + C;
    },
    elasticOut: function(E, C, I, H, D, G) {
      var F;
      if (E === 0) {
        return C;
      }
      if ((E /= H) === 1) {
        return C + I;
      }
      if (!G) {
        G = H * 0.3;
      }
      if (!D || D < Math.abs(I)) {
        D = I;
        F = G / 4;
      } else {
        F = G / (2 * Math.PI) * Math.asin(I / D);
      }
      return D * Math.pow(2, -10 * E) * Math.sin((E * H - F) * (2 * Math.PI) / G) + I + C;
    },
    elasticBoth: function(E, C, I, H, D, G) {
      var F;
      if (E === 0) {
        return C;
      }
      if ((E /= H / 2) === 2) {
        return C + I;
      }
      if (!G) {
        G = H * (0.3 * 1.5);
      }
      if (!D || D < Math.abs(I)) {
        D = I;
        F = G / 4;
      } else {
        F = G / (2 * Math.PI) * Math.asin(I / D);
      }
      if (E < 1) {
        return -0.5 * (D * Math.pow(2, 10 * (E -= 1)) * Math.sin((E * H - F) * (2 * Math.PI) / G)) + C;
      }
      return D * Math.pow(2, -10 * (E -= 1)) * Math.sin((E * H - F) * (2 * Math.PI) / G) * 0.5 + I + C;
    },
    backIn: function(D, C, G, F, E) {
      if (E === undefined) {
        E = 1.70158;
      }
      if (D === F) {
        D -= 0.001;
      }
      return G * (D /= F) * D * ((E + 1) * D - E) + C;
    },
    backOut: function(D, C, G, F, E) {
      if (typeof E === "undefined") {
        E = 1.70158;
      }
      return G * ((D = D / F - 1) * D * ((E + 1) * D + E) + 1) + C;
    },
    backBoth: function(D, C, G, F, E) {
      if (typeof E === "undefined") {
        E = 1.70158;
      }
      if ((D /= F / 2) < 1) {
        return G / 2 * (D * D * (((E *= (1.525)) + 1) * D - E)) + C;
      }
      return G / 2 * ((D -= 2) * D * (((E *= (1.525)) + 1) * D + E) + 2) + C;
    },
    bounceIn: function(D, C, F, E) {
      return F - B.Easing.bounceOut(E - D, 0, F, E) + C;
    },
    bounceOut: function(D, C, F, E) {
      if ((D /= E) < (1 / 2.75)) {
        return F * (7.5625 * D * D) + C;
      } else {
        if (D < (2 / 2.75)) {
          return F * (7.5625 * (D -= (1.5 / 2.75)) * D + 0.75) + C;
        } else {
          if (D < (2.5 / 2.75)) {
            return F * (7.5625 * (D -= (2.25 / 2.75)) * D + 0.9375) + C;
          }
        }
      }
      return F * (7.5625 * (D -= (2.625 / 2.75)) * D + 0.984375) + C;
    },
    bounceBoth: function(D, C, F, E) {
      if (D < E / 2) {
        return B.Easing.bounceIn(D * 2, 0, F, E) * 0.5 + C;
      }
      return B.Easing.bounceOut(D * 2 - E, 0, F, E) * 0.5 + F * 0.5 + C;
    }
  };
  B.Easing = A;
}, "3.2.0", {
  requires: ["anim-base"]
});