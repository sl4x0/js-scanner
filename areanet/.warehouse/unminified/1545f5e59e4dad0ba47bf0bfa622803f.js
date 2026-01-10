YUI.add("native-call", (function(a) {
  "use strict";
  var n = window.native,
    r = n.call;
  n.call = function() {
    return a.when(r.apply(n, a.Array(arguments)))
  }
}), "@VERSION@", {
  requires: ["promise"]
});
YUI.add("native-stats", (function(t) {
  "use strict";
  var s, e = window.native,
    a = {
      bubbles: !1,
      preventable: !1
    };
  (s = function() {
    if (this._events = {
        change: this.publish("change", a),
        stats: this.publish("stats", {
          bubbles: !1,
          preventable: !1,
          fireOnce: !0
        })
      }, e.on("stats", this._statsChanged.bind(this, !1)), e._stats) return this._statsChanged(!0, e._stats);
    e.call("GetStats").then(this._statsChanged.bind(this, !0))
  }).prototype = {
    change: function(t) {
      this._statsChanged(!1, t)
    },
    _statsChanged: function(t, s) {
      var e = this;
      Object.keys(s).forEach((function(t) {
        var n = s[t],
          i = e[t];
        e[t] = n, e._events[t] || (e._events[t] = e.publish(t + "Change", a)), e.fire(t + "Change", {
          stat: t,
          prevVal: i,
          newVal: n
        })
      })), this.fire(t ? "stats" : "change", s)
    }
  }, t.augment(s, t.EventTarget), e.stats = new s
}), "@VERSION@", {
  requires: ["event-custom-base"]
});
YUI.add("native-api-ime", (function(e) {
  "use strict";
  if ("zh" === window.native.stats.language) {
    var t, n = window.native,
      i = e.namespace("GW2");
    t = Object.create({
      sendEnabled: function(e) {
        n.call("Ime" + (e.enabled ? "Enable" : "Disable"))
      },
      sendRect: function(e) {
        var t = n.scale || 1,
          i = t * e.width,
          a = t * e.height;
        n.call("ImeSetRectDim", {
          left: e.left ? Number(e.left) : 0,
          top: e.top ? Number(e.top) : 0,
          width: i || 0,
          height: a || 0
        })
      },
      sendSelection: function(e) {
        var t = "backward" === e.direction,
          i = t ? e.end : e.start,
          a = t ? e.start : e.end;
        n.call("ImeSetSelection", i, a)
      },
      sendText: function(e) {
        n.call("ImeSetText", e.text)
      },
      schema: {
        enabled: {
          type: "bool",
          value: !1
        },
        text: {
          type: "string",
          value: ""
        },
        start: {
          type: "int",
          value: 0
        },
        end: {
          type: "int",
          value: 0
        },
        direction: {
          type: "string",
          value: "forward"
        },
        width: {
          type: "int",
          value: 0
        },
        height: {
          type: "int",
          value: 0
        },
        top: {
          type: "int",
          value: 0
        },
        left: {
          type: "int",
          value: 0
        }
      },
      groups: {
        Enabled: ["enabled"],
        Text: ["text"],
        Selection: ["start", "end", "direction"],
        Rect: ["width", "height", "top", "left"]
      },
      group: function(n) {
        var i;
        return e.Object.each(t.groups, (function(e, t) {
          e.indexOf(n) >= 0 && (i = t)
        })), i
      },
      stage: function(e) {
        var n = Object.keys(t).every((function(e) {
          return !1 === t[e]
        }));
        t.groups[e].staged || (t.groups[e].staged = !0), n && setTimeout(t.commit, 0)
      },
      commit: function() {
        e.each(t.groups, (function(e, n) {
          if (e.staged) {
            var i = t["send" + n],
              a = {};
            e.forEach((function(e) {
              a[e] = t[e]
            })), i(a), e.staged = !1
          }
        }))
      }
    }), e.Object.each(t.schema, (function(e, n) {
      e.group = t.group(n), Object.defineProperty(t, n, {
        get: function() {
          return e.value
        },
        set: function(n) {
          return n = function(e, t) {
            switch (t) {
              case "int":
                return parseInt(e, 10);
              case "bool":
                return Boolean(e)
            }
            return e instanceof Object && (e = JSON.stringify(e)), String(e)
          }(n, e.type), e.value === n ? n : (t.stage(e.group), e.value = n)
        }
      })
    })), n.on("ImeTextStore", (function(e) {
      window.postMessage(["ime:native", {
        direction: e.caret === e.selStart ? "backward" : "forward",
        text: e.text,
        start: e.selStart,
        end: e.selEnd
      }], "*")
    })), window.addEventListener("message", (function(e) {
      if (e.source === window) {
        var t = e.data,
          n = t && t.length && "ime:client" === t[0] && t[0] && t[1];
        i.Ime = n
      }
    }), !0), Object.defineProperty(i, "Ime", {
      get: function() {
        return t
      },
      set: function(n) {
        return n && e.mix(t, n, !0)
      }
    })
  }
}), "@VERSION@", {
  requires: ["native-stats"]
});
YUI.add("native-scale", (function(e) {
  "use strict";
  var t = window.native,
    n = document.documentElement,
    i = e.namespace("GW2");
  i.setScale = function() {
    var e = Math.min(window.innerWidth / n.offsetWidth, window.innerHeight / n.offsetHeight);
    t.scale = e, n.style["transform-origin"] = "top left", n.style.transform = "scale(" + e + ")"
  }, window.addEventListener("resize", i.setScale, !1), i.setScale()
}), "@VERSION@", {
  condition: {
    test: function() {
      "use strict";
      return window.self === window.top
    }
  }
});
YUI.add("gw2-enums", (function(e) {
  "use strict";
  e.namespace("GW2").Enums = {
    reverse: function(e, n) {
      var r, t = this[e];
      return Object.keys(t).some((function(e) {
        return t[e] == n && (r = e), r
      })), r
    },
    Profession: {
      guardian: 1,
      warrior: 2,
      engineer: 3,
      ranger: 4,
      thief: 5,
      elemental: 6,
      mesmer: 7,
      necro: 8,
      revenant: 9
    },
    Rarity: {
      basic: 1,
      fine: 2,
      masterwork: 3,
      rare: 4,
      exotic: 5,
      ascended: 6,
      legendary: 7
    },
    ItemLocationType: {
      none: 0,
      agent: 1,
      equipment: 2,
      inventory: 3,
      "inventory-account": 4,
      "inventory-bag-slot": 5,
      "inventory-overflow": 6,
      lootable: 7,
      vendor: 8,
      "inventory-quickslot": 9
    }
  }
}));
YUI.add("filter-types", (function(a) {
  "use strict";
  var e = a.namespace("GW2");
  e.armorstats = ["power", "precision", "toughness", "vitality", "criticaldamage", "healing", "conditiondamage", "conditionduration", "boonduration", "defense"], e.weaponstats = ["power", "precision", "toughness", "vitality", "criticaldamage", "healing", "conditiondamage", "conditionduration", "boonduration", "attackpowermin", "attackpowermax"], e.FilterOptions = {
    weaponstats1: e.weaponstats,
    weaponstats2: e.weaponstats,
    weaponstats3: e.weaponstats,
    armorstats1: e.armorstats,
    armorstats2: e.armorstats,
    armorstats3: e.armorstats,
    discipline: ["huntsman", "cook", "enchanter", "jeweler", "leatherworker", "tailor", "weaponsmith", "armorsmith", "scribe"]
  }, e.professionMappings = {
    armor: {
      guardian: "Heavy",
      necro: "Light",
      engineer: "Medium",
      elemental: "Light",
      thief: "Medium",
      warrior: "Heavy",
      mesmer: "Light",
      ranger: "Medium",
      revenant: "Heavy"
    },
    weapon: {
      guardian: ["sword", "hammer", "greatsword", "staff", "mace", "scepter", "focus", "shield", "torch", "harpoon", "trident"],
      necro: ["staff", "scepter", "axe", "dagger", "focus", "warhorn", "harpoon", "trident"],
      engineer: ["rifle", "pistol", "shield", "speargun"],
      elemental: ["staff", "scepter", "dagger", "focus", "trident"],
      thief: ["sword", "bowshort", "dagger", "pistol", "harpoon", "speargun"],
      warrior: ["hammer", "greatsword", "bowlong", "rifle", "axe", "sword", "mace", "shield", "warhorn", "harpoon", "speargun"],
      mesmer: ["greatsword", "staff", "scepter", "sword", "focus", "pistol", "torch", "harpoon", "trident"],
      ranger: ["greatsword", "bowlong", "bowshort", "sword", "axe", "dagger", "torch", "warhorn", "harpoon", "speargun"],
      revenant: ["mace", "sword", "axe", "hammer", "staff", "harpoon"]
    }
  }, e.FilterAttributes = {
    armorsmith: "MinRatingArmorsmith",
    cook: "MinRatingCook",
    enchanter: "MinRatingEnchanter",
    huntsman: "MinRatingHuntsman",
    jeweler: "MinRatingJeweler",
    leatherworker: "MinRatingLeatherworker",
    tailor: "MinRatingTailor",
    weaponsmith: "MinRatingWeaponsmith",
    scribe: "MinRatingFabricator",
    power: "Power",
    precision: "Precision",
    toughness: "Toughness",
    vitality: "Vitality",
    criticaldamage: "CriticalDamage",
    healing: "Healing",
    conditiondamage: "ConditionDamage",
    conditionduration: "ConditionDuration",
    boonduration: "BoonDuration",
    agonyresistance: "AgonyResistance",
    bagsize: "BagSize",
    defense: "Defense",
    attackpowermin: "AttackPowerMin",
    attackpowermax: "AttackPowerMax"
  }, e.FilterCategories = {
    sell: ["text", "rarity", "level"],
    transactions: ["text", "rarity", "level"],
    null: ["text", "rarity", "level", "available", "locked"],
    armor: ["text", "armorstats1", "armorstats2", "armorstats3", "profession", "rarity", "level", "available", "locked"],
    bags: ["text", "bagsize", "rarity", "level", "available"],
    craftingmaterial: ["text", "discipline", "rarity", "level", "available"],
    other: ["text", "rarity", "level", "available", "locked"],
    jadebot: ["text", "rarity", "level", "available"],
    skins: ["text", "rarity", "available", "locked"],
    upgradecomponent: ["text", "rarity", "level", "available"],
    weapon: ["text", "weaponstats1", "weaponstats2", "weaponstats3", "profession", "rarity", "level", "available", "locked"],
    favorites: ["text", "rarity", "level", "available", "locked"]
  }
}), "@VERSION@", {
  requires: ["gw2-enums"]
});
YUI.add("util-log", (function(t) {
  "use strict";
  var e;
  e = function() {
    function t() {
      return (65536 * (1 + Math.random()) | 0).toString(16).substring(1)
    }
    return (t() + t() + "-" + t() + "-" + t() + "-" + t() + "-" + t() + t() + t()).toUpperCase()
  }(), t.namespace("GW2.Util").log = function(n) {
    var i = t.merge({
      s: window.native.stats.sessionId,
      action: "navigation",
      gems: window.native.stats.gems,
      shoppingSession: e
    }, n);
    return t.each(i, (function(t, e) {
      null == t && delete i[e]
    })), i.filters && (i.filters = JSON.stringify(i.filters)), i.page && "/" === i.page.charAt(0) && (i.page = i.page.slice(1, i.page.length)), m.request({
      url: "/log",
      data: i
    })
  }
}));
YUI.add("app-state", (function(e) {
  var t, o, r = e.namespace("GW2"),
    s = e.namespace("GW2.Enums"),
    a = e.namespace("GW2.Util").log,
    n = r.FilterCategories,
    i = r.armorstats.filter((function(e) {
      return -1 !== r.weaponstats.indexOf(e)
    }));
  window.localStorage.power || (window.localStorage.power = "off"), window.state = e.merge(window.state, {
    section: m.prop(),
    setSection: function(t, o) {
      window.state.sections.transactions.offset(0), window.state.section(e.merge(window.state.sections[t], {
        name: t
      })), o || "order" === t || window.state.refresh({
        from: "section"
      })
    },
    _synced: m.prop(!1),
    synced: function(t) {
      return "boolean" == typeof t && (window.state._synced(t), t && e.fire("items:synced"), window.setTimeout(m.redraw, 0)), window.state._synced()
    },
    powerMode: function(e) {
      return "boolean" == typeof e && (window.localStorage.power = e ? "on" : "off"), "on" === window.localStorage.power
    },
    refresh: function(t) {
      var o = t && t.from,
        r = window.state.section();
      if ("home" === r.name && "section" !== o) return window.state.setSection("browse");
      "transactions" !== r.name || "filter" !== o ? (r.results([]), e.GW2[r.name].get()) : r.results(e.GW2.transactions.filter(r.unfiltered()))
    },
    canReset: function() {
      var e = window.state.section().params();
      return !(!e.category || "skins" === e.category || 0 === e.levelMin && 80 === e.levelMax) || (!(!e.profession || e.profession === s.reverse("Profession", window.native.stats.profession)) || ("browse" === window.state.section().name && !e.available || Object.keys(e).some((function(e) {
        return -1 === ["category", "subcategory", "available", "profession", "levelMin", "levelMax"].indexOf(e)
      }))))
    },
    refreshOnDialogClose: m.prop(!1),
    sections: {
      order: {},
      home: {
        trades: m.prop(),
        viewed: m.prop()
      },
      browse: {
        params: m.prop({
          category: null,
          levelMin: 0,
          levelMax: 80,
          available: !0
        }),
        results: m.prop([]),
        sortField: m.prop(),
        sortDesc: m.prop(!1)
      },
      sell: {
        params: m.prop({
          category: null,
          levelMin: 0,
          levelMax: 80
        }),
        results: m.prop([]),
        sortField: m.prop(),
        sortDesc: m.prop(!1)
      },
      transactions: (t = m.stream([]), o = t.map((function(e) {
        return r.transactions ? r.transactions.filter(e) : []
      })), {
        params: m.prop({
          category: "current",
          levelMin: 0,
          levelMax: 80
        }),
        results: o,
        unfiltered: t,
        sortField: m.prop("date"),
        sortDesc: m.prop(!1),
        loadMore: m.prop(!1),
        totalResults: m.prop(0),
        total: m.prop(200),
        offset: m.prop(0)
      })
    },
    sort: function(e) {
      var t = window.state.section(),
        o = e === t.sortField();
      "favorite" === t.sortField() && o && !t.sortDesc() ? (t.sortField(null), t.sortDesc(!1)) : (t.sortField(e), t.sortDesc(!!o && !t.sortDesc())), window.state.refresh({
        from: "filter"
      })
    },
    setCategory: function(t, o) {
      var r = window.state.section();
      if ("transactions" === r.name && r.offset(0), !o) return "sell" === r.name || "transactions" === r.name ? r.params(e.merge(r.params(), {
        category: t || null,
        subcategory: null
      })) : r.params(e.merge(function(t) {
        var o = window.state.section(),
          r = o.params(),
          a = e.merge(o.params()),
          l = n[r.category || null],
          c = n[t || null].slice(0),
          m = "armor" === t || "weapon" === t;
        return c.push("levelMin", "levelMax"), -1 === c.indexOf("level") && (a.levelMin = 0, a.levelMax = 80), e.Object.each(a, (function(e, t) {
          (!m || -1 === t.indexOf("armorstats") && -1 === t.indexOf("weaponstats") || -1 === i.indexOf(e.selected)) && -1 === c.indexOf(t) && delete a[t]
        })), m && (a.profession = -1 !== l.indexOf("profession") ? r.profession : s.reverse("Profession", window.native.stats.profession)), a
      }(t), {
        category: t || null
      })), a({
        page: "/" === m.route() ? "browse" : m.route(),
        filters: r.params()
      }), void window.state.refresh();
      r.params(e.merge(r.params(), {
        category: t || null,
        subcategory: o
      })), a({
        page: m.route(),
        filters: r.params()
      }), window.state.refresh()
    },
    setFilter: function(t, o, r) {
      var s = {},
        a = window.state.section();
      s[t] = r ? {
        selected: r,
        value: o
      } : o, a.params(e.merge(a.params(), s)), window.state.refresh({
        from: "filter"
      })
    },
    removeFilter: function(t) {
      var o = window.state.section(),
        s = o.params();
      "category" !== t && "subcategory" !== t ? (s[t] ? delete s[t] : "level" === t ? (s.levelMin = 0, s.levelMax = 80) : e.Object.each(r.FilterOptions, (function(e, o) {
        -1 !== e.indexOf(t) && s[o] && s[o].selected === t && delete s[o]
      })), o.params(s), window.state.refresh({
        from: "filter"
      })) : window.state.setCategory("category" === t ? null : s.category, null)
    },
    resetFilters: function(e) {
      var t = {},
        o = window.state.section(),
        r = o.params();
      (r.category || null === r.category) && (t.category = r.category, "browse" !== o.name && "home" !== o.name || (t.available = !0)), r.subcategory && (t.subcategory = r.subcategory), -1 !== n["browse" === o.name || "home" === o.name ? r.category : o.name].indexOf("level") && (t.levelMin = 0, t.levelMax = 80), "armor" !== r.category && "weapon" !== r.category || (t.profession = s.reverse("Profession", window.native.stats.profession)), o.sortField("transactions" === o.name ? "date" : null), o.params(t), e.skipSearch || window.state.refresh({
        from: "filter"
      })
    }
  }), window.state.sections.home = e.merge(window.state.sections.home, window.state.sections.browse)
}), "@VERSION@", {
  requires: ["gw2-enums", "filter-types", "util-log"]
});
YUI.add("sts-http", (function(o) {
  "use strict";
  o.namespace("STS")._http = function(e, t) {
    return new o.Promise((function(t, s) {
      o.io("/stsRequest?" + e.protocol + "/" + e.command, {
        method: "POST",
        data: JSON.stringify(e),
        headers: {
          "Content-Type": "application/json"
        },
        on: {
          success: function(o, e) {
            var n;
            try {
              n = JSON.parse(e.responseText)
            } catch (o) {
              s("Could not parse response body")
            }
            if (200 === e.status || 400 === e.status && !n.body.code) return t(n.body);
            s(n)
          },
          failure: function(o, t) {
            var n = {};
            try {
              n = JSON.parse(t.responseText)
            } catch (o) {
              console.log("Couldn't parse failure response body: " + e.protocol + "/" + e.command)
            }
            s(n.body)
          }
        }
      })
    }))
  }
}), "@VERSION@", {
  requires: ["io-base", "promise"]
});
YUI.add("sts-request", (function(e) {
  "use strict";
  var r = e.Lang.isNumber,
    o = e.namespace("STS"),
    t = window.native;
  o.request = function(e) {
    return e.headers || (e.headers = {}), e.type || (e.type = "One"), e.protocol = e.protocol.replace(".gw2.", "." + t.stats.gameCode + "."), o._request(e)
  }, o.netError = function(e) {
    e && r(e.code) && r(e.product) && r(e.module) && r(e.line) && t.call("ShowNetErrorBasic", e.code, e.product, e.module, e.line)
  }
}), "@VERSION@", {
  requires: ["promise"]
});
YUI.add("sts-request-jssrv", (function(t) {
  "use strict";
  var e = t.namespace("STS"),
    s = window.native;
  e._request = function(t) {
    return t.headers.m = s.stats.sessionId, e._http(t)
  }
}), "@VERSION@", {
  requires: ["promise", "sts-http", "native-stats"],
  condition: {
    trigger: "sts-request",
    when: "after",
    test: function(t) {
      "use strict";
      return !window.native || window.native.stubbed || !GW2.config.features.cliGate
    }
  }
});
YUI.add("sts-userinfo", (function(e) {
  "use strict";
  var s = e.namespace("STS");
  s.getUserInfo = s.request({
    protocol: "Auth",
    command: "GetUserInfo"
  })
}), "@VERSION@", {
  requires: ["sts-request"]
});
YUI.add("micro-gw2-unauthorized", (function(e) {
  var r = e.namespace("Templates");
  e.namespace("Templates.Helpers");
  r["gw2-unauthorized"] = (new e.Template).revive((function(e, r, a) {
    var n = '<div class="unauthorized notice">\r\n    \x3c!-- program:!live --\x3e\r\n    <h1>You must <a href="/login">login</a> to view this page</h1>\r\n    \x3c!-- /program:!live --\x3e\r\n\r\n    \x3c!-- program:live\r\n    <h1>ERROR: Invalid authorization</h1>\r\n    /program:live --\x3e\r\n</div>\r\n';
    return n
  }))
}), "@VERSION@", {
  requires: ["template"]
});
YUI.add("unauthorized", (function(e) {
  "use strict";
  e.namespace("STS").getUserInfo.then((function(e) {
    GW2.user = e
  }), (function() {
    var u = e.one("body");
    u.addClass("unauthorized"), u.append(e.Templates["gw2-unauthorized"]())
  }))
}), "@VERSION@", {
  requires: ["sts-userinfo", "sts-request", "css-unauthorized", "micro-gw2-unauthorized"]
});
YUI.add("util-text-keys", (function(t) {
  "use strict";
  var e, i = window.native;
  (e = function() {
    this.injected = {}, this.keys = {}
  }).prototype = {
    register: function(t, e) {
      "string" == typeof t && (t = parseInt(t, 10)), !isNaN(t) && Array.isArray(e) && e.length && (this.keys[t] = e)
    },
    inject: function(t) {
      var e;
      "string" == typeof t && (t = parseInt(t, 10)), e = this.keys[t], !isNaN(t) && !(t in this.injected) && Array.isArray(e) && e.length && (e.forEach((function(t) {
        i.call("SetTextEncryptionKey", parseInt(t.id, 10), t.password)
      })), this.injected[t] = 1)
    }
  }, t.namespace("GW2.Util").keys = new e
}));
YUI.add("account-status", (function(t) {
  "use strict";
  var e = window.native,
    s = t.namespace("GW2"),
    i = GW2.config.features,
    r = Boolean(t.Object.getValue(e.stats.features, ["2", "current"])),
    a = Boolean(t.Object.getValue(e.stats.features, ["51", "current"])),
    n = ["full", "free", "trial", "restricted"];

  function u() {
    var t = this;
    if (this.status = !1, this.full = !1, this.free = !1, this.trial = !1, this.restricted = !1, this.publish("status", {
        fireOnce: !0
      }), !r) return t._setFlags(a ? "free" : "trial");
    e.import("gw2/player", (function(e) {
      if (e.isEconomyRestricted) return t._setFlags("restricted");
      t._setFlags("full")
    }))
  }
  u.prototype = {
    expansions: {
      hot: Boolean(t.Object.getValue(e.stats.features, ["45", "current"])),
      hotUltimate: Boolean(t.Object.getValue(e.stats.features, ["47", "current"]))
    },
    check: function(t) {
      return Boolean(i[t]) && (this.full || Boolean(i[t + "-" + this.status]))
    },
    tooltip: function(t, e) {
      var s = window.tp_strings.common.disabled;
      return e = e || !1, t in i && !i[t] ? s.feature : this.restricted ? s[this.status + (e.link ? "-link" : "")] : s[this.status]
    },
    _setFlags: function(t, e) {
      void 0 === e && (e = !0), n.forEach(function(s) {
        this[s] = s === t && e
      }.bind(this)), this.status = t, this.fire("status")
    }
  }, t.augment(u, t.EventTarget), s.Account = new u
}), "@VERSION@", {
  requires: ["event", "sts-request"]
});
YUI.add("util-items", (function(t) {
  "use strict";
  var e = t.namespace("STS"),
    i = t.namespace("GW2.Util").keys,
    a = t.namespace("GW2.Util.items"),
    r = t.namespace("GW2.Util.log"),
    n = t.namespace("GW2.Account"),
    o = window.native,
    s = "numFavorites";

  function u(t, e) {
    e in t && (t[e] = parseInt(t[e], 10))
  }
  a.load = function(t) {
    return Array.isArray(t) || (t = [t]), e.request({
      protocol: "Game.gw2.ItemSearch",
      command: "TradeSearch",
      body: {
        buildId: o.stats.buildId,
        language: o.stats.language,
        items: t.map((function(t) {
          return "string" != typeof t && "number" != typeof t || (t = {
            dataId: t
          }), {
            TypeId: t.typeId || t.type_id || 3,
            DataId: t.dataId || t.data_id
          }
        }))
      }
    }).then((function(t) {
      return a.parse(t.items).then((function(e) {
        return t.items = e, t
      }))
    }), (function(t) {
      e.netError(t)
    }))
  }, a.loadFavorites = function() {
    return new t.Promise((function(t, e) {
      o.import("gw2/datastore", (function(i) {
        i.prepare().then((function() {
          var e = i.favorites ? JSON.parse(i.favorites) : {};
          a.setNumFavorites(e), t(e)
        }), (function(t) {
          e(t)
        }))
      }))
    }))
  }, a.getNumFavorites = function() {
    return Number(localStorage.getItem(s))
  }, a.setNumFavorites = function(t) {
    return localStorage.setItem(s, Object.keys(t).length)
  }, a.maxFavoritesReached = function() {
    return a.getNumFavorites() >= window.maxFavorites
  }, a.editFavorite = function(t) {
    o.import("gw2/datastore", (function(e) {
      var i = JSON.parse(e.favorites || "{}");
      e.remove("favorites"), i[t.item.guid] ? (delete i[t.item.guid], r({
        action: "interaction",
        interaction: "unfavorite",
        itemDataId: t.item.data_id
      })) : (i[t.item.guid] = {
        TypeId: t.item.type_id,
        DataId: t.item.data_id
      }, r({
        action: "interaction",
        interaction: "favorite",
        itemDataId: t.item.data_id
      })), a.setNumFavorites(i), a.maxFavoritesReached() && r({
        action: "interaction",
        interaction: "maxFavoritesReached"
      }), e.store("favorites", JSON.stringify(i), {
        persist: !0
      })
    })), t.item.favorite = !t.item.favorite
  }, a.parse = function(e) {
    return Array.isArray(e) || (e = [e]), a.loadFavorites().then((function(a) {
      return t.Promise.all(e.map((function(t) {
        return u(t, "buy_count"), u(t, "buy_price"), u(t, "data_id"), u(t, "level"), u(t, "rarity"), u(t, "sell_count"), u(t, "sell_price"), u(t, "type_id"), u(t, "vendor"), a[t.guid] && (t.favorite = !0), t.whitelisted = !("whitelisted" in t) || (!!n.check("ignore-whitelist") || "1" === t.whitelisted), i.register(t.data_id, t.passwords), i.inject(t.data_id), t
      })))
    }))
  }, a.rarityMatches = function(t, e) {
    return t.rarityWord.match(new RegExp(e, "i"))
  }
}), "@VERSION@", {
  requires: ["sts-request", "util-text-keys", "account-status"]
});
YUI.add("navigation", (function(e) {
  "use strict";
  var o = e.namespace("navigation");
  o.browse = {
    armor: {
      noSubCat: {
        armor: [],
        trinket: [],
        back: []
      },
      coat: {
        armor: ["coat"]
      },
      leggings: {
        armor: ["leggings"]
      },
      gloves: {
        armor: ["gloves"]
      },
      helm: {
        armor: ["helm"]
      },
      helmaquatic: {
        armor: ["helmaquatic"]
      },
      boots: {
        armor: ["boots"]
      },
      shoulders: {
        armor: ["shoulders"]
      },
      back: {
        back: []
      },
      accessory: {
        trinket: ["accessory"]
      },
      amulet: {
        trinket: ["amulet"]
      },
      ring: {
        trinket: ["ring"]
      }
    },
    weapon: {
      noSubCat: {
        weapon: []
      },
      axe: {
        weapon: ["axe"]
      },
      dagger: {
        weapon: ["dagger"]
      },
      focus: {
        weapon: ["focus"]
      },
      greatsword: {
        weapon: ["greatsword"]
      },
      hammer: {
        weapon: ["hammer"]
      },
      bowlong: {
        weapon: ["bowlong"]
      },
      sword: {
        weapon: ["sword"]
      },
      bowshort: {
        weapon: ["bowshort"]
      },
      mace: {
        weapon: ["mace"]
      },
      pistol: {
        weapon: ["pistol"]
      },
      rifle: {
        weapon: ["rifle"]
      },
      scepter: {
        weapon: ["scepter"]
      },
      staff: {
        weapon: ["staff"]
      },
      torch: {
        weapon: ["torch"]
      },
      warhorn: {
        weapon: ["warhorn"]
      },
      shield: {
        weapon: ["shield"]
      },
      harpoon: {
        weapon: ["harpoon"]
      },
      speargun: {
        weapon: ["speargun"]
      },
      trident: {
        weapon: ["trident"]
      }
    },
    upgradecomponent: {
      noSubCat: {
        upgradecomponent: [],
        relic: []
      },
      upgradeweapon: {
        upgradecomponent: ["sigil"]
      },
      upgradearmor: {
        upgradecomponent: ["rune"]
      },
      infusion: {
        category: {
          upgradecomponent: ["default"]
        },
        InfusionFlags: ["Infusion"]
      },
      relic: {
        category: {
          relic: []
        }
      },
      trinket: {
        category: {
          upgradecomponent: ["default", "gem"]
        },
        InfusionFlags: []
      }
    },
    skins: {
      noSubCat: {
        consumable: ["transmutation"]
      },
      armorskins: {
        category: {
          consumable: ["transmutation"]
        },
        ConsumableTransmutations: ["Armor", "Back"]
      },
      weaponskins: {
        category: {
          consumable: ["transmutation"]
        },
        ConsumableTransmutations: ["Weapon"]
      }
    },
    craftingmaterial: {
      noSubCat: {
        craftingmaterial: [],
        trophy: []
      },
      materials: {
        craftingmaterial: []
      },
      salvage: {
        category: {
          trophy: []
        },
        Attributes: {
          salvageable: {
            exact: 1
          }
        }
      },
      recipes: {
        category: {
          consumable: ["unlock"]
        },
        ConsumableUnlocks: ["CraftingRecipe"]
      }
    },
    jadebot: {
      noSubCat: {
        powercore: [],
        jadetechmodule: ["sensoryarray", "servicechip"]
      },
      powercore: {
        powercore: []
      },
      sensoryarray: {
        jadetechmodule: ["sensoryarray"]
      },
      servicechip: {
        jadetechmodule: ["servicechip"]
      }
    },
    other: {
      noSubCat: {
        container: [],
        minipet: [],
        gizmo: ["default"],
        consumable: ["booze", "food", "generic", "unlock", "utility"]
      },
      food: {
        consumable: ["booze", "food"]
      },
      utility: {
        consumable: ["utility"]
      },
      container: {
        container: []
      },
      minis: {
        minipet: []
      },
      dyes: {
        category: {
          consumable: ["unlock"]
        },
        ConsumableUnlocks: ["Dye"]
      },
      misc: {
        consumable: ["generic"],
        gizmo: ["default"]
      }
    },
    bags: {
      noSubCat: {
        bag: []
      }
    },
    favorites: {}
  }, o.transactions = {
    current: {
      noSubCat: {
        category: {
          current: []
        }
      },
      buy: {
        category: {
          current: ["buy"]
        }
      },
      sell: {
        category: {
          current: ["sell"]
        }
      }
    },
    history: {
      noSubCat: {
        category: {
          history: []
        }
      },
      buy: {
        category: {
          history: ["buy"]
        }
      },
      sell: {
        category: {
          history: ["sell"]
        }
      }
    }
  }, o.sell = {}
}), "@VERSION@");
YUI.add("sell", (function(e) {
  "use strict";
  const t = e.namespace("STS"),
    n = e.namespace("navigation"),
    a = e.namespace("GW2.Util").items,
    s = e.namespace("GW2.Enums"),
    i = window.native;
  let o, r = [];

  function l(e, t) {
    var n = window.state.sections.sell.sortDesc(),
      a = window.state.sections.sell.sortField() || "slot",
      s = n ? t : e,
      i = n ? e : t;
    return "name" === a ? s.name.localeCompare(i.name) : void 0 === s[a] || s[a] < i[a] ? -1 : 1
  }

  function c() {
    var e, t, i = window.state.sections.sell.params();
    return r.filter((function(o) {
      return (!("text" in i) || -1 !== o.name.toLowerCase().indexOf(i.text.toLowerCase())) && ((!("levelMin" in i) || !(o.level < i.levelMin || o.level > i.levelMax)) && (!(i.category && (e = parseInt(i.category.split("bag")[1], 10), t = Object.keys(n.sell).slice(0, e).map((function(e) {
        return n.sell[e]
      })).reduce((function(e) {
        return e + 20
      }), 0), o.slot < t || o.slot >= t + 20)) && (!(i.rarity && !a.rarityMatches(o, i.rarity)) && o.location === s.ItemLocationType.inventory)))
    })).sort(l)
  }

  function d(e) {
    var t = e.newVal.filter((function(e) {
      return Object.keys(e).length > 0
    }));
    window.native.call("QueryItemInfo", {
      items: t.map((function(e) {
        return e.dataId
      }))
    }).then((function(e) {
      t.forEach((function(t, a) {
        t.name = e[t.dataId] ? e[t.dataId].name : "", n.sell["bag" + a] = t
      }))
    }))
  }

  function u(n) {
    var s;
    if (!(s = e.Array.dedupe(n.map((function(e) {
        return parseInt(e.dataId, 10)
      })))).length) return r = [], window.state.sections.sell.results([]), void("sell" === window.state.section().name && m.redraw());
    e.Promise.all([a.load(s), i.call("QueryItemInfo", {
      items: s
    })]).then((function(t) {
      var a = {};
      t[0].items.forEach((function(e) {
        a[e.data_id] = e
      })), r = n.map((function(n) {
        return e.merge(t[1][n.dataId], a[n.dataId], n, {
          id: n.itemId
        })
      })).reverse(), window.state.sections.sell.results(c()), "sell" === window.state.section().name && m.redraw()
    }), t.netError)
  }

  function w(t) {
    clearTimeout(o), o = setTimeout(u.bind(null, t.newVal), 50), window.state.section() && "sell" === window.state.section().name && e.fire("items:synced", {
      saveScrollPosition: !0
    })
  }
  e.GW2.sell = {
    get: function() {
      window.state.sections.sell.results(c()), window.state.synced(!0)
    }
  }, i.stats.on("bagsChange", d), d({
    newVal: i.stats.bags || []
  }), i.stats.after("inventoryChange", w, this), w({
    newVal: i.stats.inventory
  })
}), "@VERSION@", {
  requires: ["sts-request", "gw2-enums", "util-items", "navigation"]
});
YUI.add("browse", (function(e) {
  "use strict";
  const t = e.namespace("GW2"),
    n = window.enums,
    a = e.namespace("GW2.Enums"),
    r = e.namespace("navigation").browse,
    o = e.namespace("STS"),
    i = e.namespace("GW2.Util").items,
    s = window.state.sections.browse,
    c = window.native;
  let u, l, d = !1;

  function m() {
    return new e.Promise((function(e, t) {
      var a, o, c = s.params(),
        u = {};
      if (c.category) {
        u.Categories = {};
        const e = c.subcategory || "noSubCat";
        a = r[c.category][e] || {}, o = a.category || a, Object.keys(o).forEach((function(e) {
          var t = n.categories[e];
          u.Categories[t] = o[e].map((function(t) {
            return n.subcategories[e][t]
          }))
        })), a.category && Object.keys(a).forEach((function(e) {
          "category" !== e && (u[e] = a[e])
        }))
      }
      return "favorites" === c.category ? i.loadFavorites().then((function(t) {
        u.Items = Object.keys(t).map((function(e) {
          return {
            TypeId: t[e].TypeId,
            DataId: t[e].DataId
          }
        })), u.SpecifiedItemsOnly = !0, u.FilterSpecifiedItems = !0, e(u)
      })) : e(u)
    })).then((function(r) {
      var o = e.merge(r, function() {
        var e = s.params(),
          n = {};
        return ["armorstats1", "armorstats2", "armorstats3", "weaponstats1", "weaponstats2", "weaponstats3", "discipline", "bagsize"].forEach((function(a) {
          var r = "bagsize" !== a ? e[a] : {
            selected: "bagsize",
            value: e.bagsize
          };
          r && void 0 !== r.value && r.selected && (n.Attributes || (n.Attributes = {}), n.Attributes[t.FilterAttributes[r.selected]] = {
            min: Math.max(r.value, "discipline" === a ? 0 : 1)
          })
        })), n
      }(), function() {
        var e = s.params(),
          r = {};
        return e.profession && ("armor" === e.category ? (!e.subcategory || !["back", "accessory", "amulet", "ring"].filter((function(t) {
          return t === e.subcategory
        })).length) && (r.ArmorWeightClasses = [t.professionMappings.armor[e.profession], "None"]) : "weapon" !== e.category || e.subcategory || (r.Categories = {}, r.Categories[n.categories.weapon] = t.professionMappings.weapon[e.profession].map((function(e) {
          return n.subcategories.weapon[e]
        })))), void 0 !== e.levelMin && (r.LevelMin = e.levelMin), void 0 !== e.levelMax && (r.LevelMax = e.levelMax), e.rarity && (r.Rarity = a.Rarity[e.rarity]), e.available && (r.AvailableOnly = 1), e.text && (r.Text = e.text), r
      }(), {
        Language: window.native.stats.language,
        BuildId: window.native.stats.buildId,
        Sort: s.sortField()
      });
      return s.sortDesc() && (o.Descending = s.sortDesc()), o.Count = 500, o
    })).then((function(e) {
      return "favorite" !== s.sortField() || "favorites" === s.params().category ? e : i.loadFavorites().then((function(t) {
        return e.Items = Object.keys(t).map((function(e) {
          return {
            Guid: e
          }
        })), e.PrioritizeSpecifiedItems = !0, e.FilterSpecifiedItems = !0, e.SpecifiedItemsOnly = !1, e
      }))
    }))
  }

  function f() {
    var t;
    l = null, d = !0, window.state.synced(!1), m().then((function(e) {
      return "favorites" !== s.params().category || (e.Items || []).length ? o.request({
        protocol: "Game.gw2.ItemSearch",
        command: "TradeSearch",
        headers: {},
        body: e
      }) : {
        items: []
      }
    })).then((function(e) {
      if (d = !1, !l) return i.parse(e.items)
    })).then((function(n) {
      var a = n.filter((function(e) {
        return !u[e.data_id]
      })).map((function(e) {
        return e.data_id
      }));
      return t = n, a.length ? window.native.call("QueryItemInfo", {
        items: a,
        checkUnlock: !0
      }).then((function(t) {
        return e.Object.each(t, (function(e) {
          u[e.dataId] = {
            name: e.name,
            unlockType: e.unlockType,
            unlockDataId: e.unlockDataId,
            skinId: e.skinId
          }
        })), setTimeout((function() {
          localStorage.itemNameCache = JSON.stringify(u)
        }), 10), u
      }), o.netError) : u
    })).then((function(e) {
      t = t.map((function(t) {
        var n = e[t.data_id];
        return t.name = n.name, t.unlockType = n.unlockType, t.unlockDataId = n.unlockDataId, t
      }))
    })).then((function() {
      if (!s.params().locked) return t;
      var e = t.reduce((function(e, t) {
        return void 0 !== t.unlockType && (e[t.unlockType] || (e[t.unlockType] = []), e[t.unlockType].push(t.unlockDataId)), e
      }), {});
      return Promise.all(Object.keys(e).map((function(t) {
        var n = e[t];
        return c.call(window.enums.content[t], [{
          dataIds: n
        }]).then((function(e) {
          return {
            unlockType: t,
            unlockValues: e
          }
        }))
      }))).then((function(e) {
        return t.filter((function(t) {
          if (void 0 === t.unlockType) return !1;
          for (var n = 0; n < e.length; n++) {
            var a = e[n];
            if (t.unlockType == a.unlockType && a.unlockValues[t.unlockDataId]) return !1
          }
          return !0
        }))
      }))
    })).then((function(e) {
      l || d || (s.results(e), window.state.synced(!0))
    }), o.netError).catch((function() {
      d = !1, window.state.synced(!0)
    }))
  }
  u = localStorage.itemNameCache ? JSON.parse(localStorage.itemNameCache) : {}, u["@LANGUAGE@"] !== window.native.stats.language && (u = {
    "@LANGUAGE@": window.native.stats.language
  }, localStorage.itemNameCache = JSON.stringify(u)), e.namespace("GW2").browse = {
    get: function() {
      d || l ? (window.clearTimeout(l), l = window.setTimeout(f, 300)) : f()
    }
  }
}), "@VERSION@", {
  requires: ["app-state", "gw2-enums", "filter-types", "navigation", "util-items"]
});
YUI.add("transactions", (function(t) {
  "use strict";
  const e = t.namespace("STS"),
    n = t.namespace("GW2.Util").items,
    a = window.tp_strings.category.transaction,
    i = window.state.sections.transactions,
    r = window.native;
  let s;

  function o(t) {
    return e.request({
      protocol: "Game.gw2.Trade",
      command: "current" === t.section ? "GetMyListings" : "GetHistory",
      body: {
        isBuy: "buy" === t.type,
        count: 200,
        offset: i.offset() + 1
      }
    }).then((function(e) {
      return e.listings = e.listings.map((function(e) {
        return e.id = (e.type_id || 3) + "-" + e.data_id + "-" + e.listing_id, e.section = t.section, e.isBuy = "buy" === t.type, e.cancelable = "current" === e.section, e.unit_price = parseInt(e.unit_price, 10), e.quantity = parseInt(e.quantity, 10), e
      })), e
    }))
  }

  function c(t, e) {
    var n = i.sortDesc(),
      r = i.sortField(),
      s = n ? e : t,
      o = n ? t : e;
    return "name" === r ? s.name.localeCompare(o.name) : "isBuy" === r ? a[s.section + (s.isBuy ? "-buy" : "-sell")].localeCompare(a[o.section + (o.isBuy ? "-buy" : "-sell")]) : "date" === r ? s.date.getTime() > o.date.getTime() ? -1 : 1 : "cancelable" === r ? s[r] ? -1 : 1 : s[r] < o[r] ? -1 : 1
  }

  function u(e) {
    return t.Promise.all(e.map(o)).then((function(t) {
      var e = window.state.section(),
        n = 0,
        a = 0,
        i = t.reduce((function(t, e) {
          return a += parseInt(e.total_matches, 10), n = Math.max(n, parseInt(e.total_matches, 10)), t.concat(e.listings)
        }), []);
      return "transactions" === e.name && (e.totalResults(a), e.offset(e.offset() + 200), e.loadMore(e.offset() < n)), i
    })).then((function(e) {
      var a = t.Array.dedupe(e.map((function(t) {
          return parseInt(t.data_id, 10)
        }))),
        i = {};
      return a.length ? n.load(a).then((function(t) {
        if (!s) return t.items.forEach((function(t) {
          i[t.data_id] = t
        })), r.call("QueryItemInfo", {
          items: a
        })
      })).then((function(n) {
        if (!s) return e.map((function(e) {
          return t.merge(e, n[e.data_id], i[e.data_id], {
            date: new Date(Date.parse(e.purchased || e.created))
          })
        }))
      })) : e
    }))
  }
  t.GW2.transactions = {
    filter: function(t) {
      var e = window.state.section().params();
      return t.filter((function(t) {
        return (!("text" in e) || -1 !== t.name.toLowerCase().indexOf(e.text.toLowerCase())) && ((!("levelMin" in e) || !(t.level < e.levelMin || t.level > e.levelMax)) && !(e.rarity && !n.rarityMatches(t, e.rarity)))
      })).sort(c)
    },
    getTransactions: u,
    get: function(t) {
      function n() {
        return u((a = i.params().category, r = i.params().subcategory, a || (n = ["current/buy", "current/sell", "history/buy", "history/sell"]), a && !r && (n = [a + "/buy", a + "/sell"]), a && r && (n = [a + "/" + r]), n.map((function(t) {
          var e = t.split("/");
          return {
            section: e[0],
            type: e[1]
          }
        })))).then((function(e) {
          s || (t && t.more && (e = i.unfiltered().concat(e)), i.unfiltered(e), window.state.synced(!0))
        })).catch((function(t) {
          window.state.synced(!0), e.netError(t)
        }));
        var n, a, r
      }
      if (t && t.more) return window.state.synced(!1), n();
      window.clearTimeout(s), s = setTimeout((function() {
        window.state.synced(!1), s = null, n()
      }), !s && window.state.synced() ? 0 : 300)
    }
  }
}), "@VERSION@", {
  requires: ["app-state", "navigation", "sts-request", "util-items"]
});
YUI.add("util-optional", (function(t) {
  "use strict";
  t.namespace("Util").optional = function(t, n, i) {
    return t ? n : i || ""
  }
}));
YUI.add("element-item", (function(e) {
  "use strict";
  var t = e.namespace("Elements"),
    n = e.namespace("GW2.Enums"),
    i = e.namespace("GW2.Util").keys,
    o = e.namespace("Util").optional,
    a = window.native;

  function r(e, t) {
    if (m.redraw.strategy("none"), !t.relatedTarget || !(t.relatedTarget === t.currentTarget || t.currentTarget.compareDocumentPosition(t.relatedTarget) & Node.DOCUMENT_POSITION_CONTAINED_BY)) {
      if ("mouseover" !== t.type) return a.call("HideTextTooltip"), void a.call("HideItemTooltip");
      i.inject(e), a.call("ShowItemTooltip", parseInt(e, 10))
    }
  }
  t.item = function(e) {
    var c, l = parseInt(e.count, 10);
    return "tooltip" in e || (e.tooltip = !0), e.tooltip && (c = r.bind(null, e.guid)), l = l > 1 ? String(l) : "", m("div.item", {
      "data-guid": e.guid,
      "data-locked": o(e.locked, "true"),
      "data-count": l,
      onmouseover: c,
      onmouseout: c,
      oncontextmenu: function(t) {
        i.inject(e.guid), t.clientX && t.clientY ? a.call("ShowItemContextMenu", parseInt(e.guid, 10), parseFloat(t.clientX), parseFloat(t.clientY)) : a.call("HideItemContextMenu")
      },
      onclick: function(t) {
        m.redraw.strategy("none"), (t.shiftKey || t.ctrlKey) && (a.call(t.shiftKey ? "ChatItemInsert" : "ChatItemSend", parseInt(l || "1", 10), parseInt(e.guid || 0, 10)), t.preventDefault(), t.stopPropagation())
      }
    }, m("div.icon", {
      "data-count": o(l.length > 5, "99999+", l)
    }, m("img", {
      config: function(t) {
        t.src !== "coui://item/" + e.guid && (t.src = "coui://item/" + e.guid)
      }
    })), o(e.name || "number" == typeof e.coins, m("div.details", o(e.name, m(".name.rarity", {
      class: n.reverse("Rarity", e.rarity)
    }, e.name)), o("coins" in e, t.coins(e.coins)))))
  }
}), "@VERSION@", {
  requires: ["gw2-enums", "util-optional", "util-text-keys", "css-item"]
});
YUI.add("home", (function(e) {
  "use strict";
  var t = e.namespace("GW2.Extensions"),
    n = e.namespace("GW2.Components"),
    o = e.namespace("Elements"),
    i = e.namespace("GW2.Util"),
    s = e.namespace("STS"),
    r = e.namespace("Util").optional,
    a = window.tp_strings,
    c = !1,
    u = {
      section: "history",
      type: "buy",
      total: 3,
      offset: 0
    },
    h = {
      section: "history",
      type: "sell",
      total: 3,
      offset: 0
    };
  e.GW2.home = {
    get: function() {
      e.GW2.home.getViewed(), e.GW2.home.getTrades(), e.GW2.home.getSkins()
    },
    getViewed: function(n) {
      t.LastViewed.getRecent().then((function(t) {
        t.length ? i.items.load(t).then((function(n) {
          var o = {};
          n.items.forEach((function(e) {
            o[e.data_id] = e
          })), window.state.sections.home.viewed(t.map((function(t) {
            var n = o[t.data_id];
            return e.merge(t, n, {
              type: "buy",
              count: n.sell_count,
              coins: n.sell_price
            })
          })).reverse()), m.redraw()
        }), s.netError) : n._viewed = []
      }))
    },
    getTrades: function() {
      e.GW2.transactions.getTransactions([u, h]).then((function(e) {
        e = (e = e.sort((function(e, t) {
          return Date.parse(t.purchased) - Date.parse(e.purchased)
        }))).slice(0, 3).map((function(e) {
          return e.type = e.isBuy ? "buy" : "sell", e.coins = e.unit_price, e.count = e.quantity, e
        })), window.state.sections.home.trades(e), m.redraw()
      })).catch(s.netError)
    },
    getSkins: function() {}
  }, n.Home = {
    controller: function() {
      var t = {
        itemList: function(t, i) {
          return t ? r(!t.length, m(".noresults.hbox", m("p", a.home.sections.recent[i].noresults)), t.map((function(t, s) {
            return m(".hbox.row", {
              class: t.type + " " + r(s % 2, "odd"),
              onclick: function() {
                n.OrderMithril.showDialog("buy", t)
              }
            }, o.item(e.merge(t, {
              guid: t.dataId
            })), r("trades" === i, m(".type", a.category.transaction["history-" + t.type])))
          }))) : null
        }
      };
      return t
    },
    view: function(e) {
      return c ? "home" !== window.state.section().name ? {
        subtree: "retain"
      } : m(".vbox.home", m(".contents.vbox", m(".navigation", m(".greeting", m("h1.title", a.home.welcome.title), m("p", a.home.welcome.message)), m(".actions.hbox", m(".action.sell", m("a[href=/sell]", {
        config: m.route
      }, m("i.icon"), m("button.btn", a.home.buttons.sell))), m(".action.buyArmor", m("a[href=/browse/armor]", {
        config: m.route
      }, m("i.icon"), m("button.btn", a.home.buttons.armor))), m(".action.buyWeapons", m("a[href=/browse/weapon]", {
        config: m.route
      }, m("i.icon"), m("button.btn", a.home.buttons.weapons))))), m(".recent.hbox", m("section.views.vbox", m("h3.title", a.home.sections.recent.views.heading), m(".rows.vbox", e.itemList(window.state.sections.home.viewed(), "views"))), m("section.trades.vbox", m("h3.title", a.home.sections.recent.trades.heading), m(".rows.vbox", e.itemList(window.state.sections.home.trades(), "trades")))))) : (c = !0, m(".vbox.home"))
    }
  }
}), "@VERSION@", {
  requires: ["util-items", "util-optional", "transactions", "element-item", "css-home"]
});
YUI.add("prompt", (function(p) {
  "use strict";
  p.namespace("GW2").prompt = function(p, r) {
    return m(".prompt-overlay", [m(".prompt", {
      className: r || ""
    }, [m(".prompt-inner", p)])])
  }
}), "@VERSION@", {
  requires: ["css-prompt"]
});
YUI.add("util-coins", (function(e) {
  "use strict";
  var t;
  t = {
    toObject: function(e) {
      var t, o = typeof e;
      return "object" === o ? e : ("string" === o && (e = parseInt(e, 10)), isNaN(e) && (e = 0), t = Math.floor(e / 1e4), {
        total: e,
        copper: e % 100,
        silver: Math.floor(e % 1e4 / 100),
        gold: t,
        digits: String(t).length > 3 ? "4+" : ""
      })
    },
    toInteger: function(e) {
      return "number" === typeof e ? e : e.copper + 100 * e.silver + 1e4 * e.gold
    },
    toNodes: function(e, o) {
      var i, r;
      e && (i = t.toObject(o), r = e.getData("hide-empty"), r = Boolean(r.length), e.toggleClass("empty", !i.total), e.one(".gold").setHTML(i.gold).toggleClass("hide", r && i.total && !i.gold), e.one(".silver").setHTML(i.silver).toggleClass("hide", r && i.total && !i.gold && !i.silver), e.one(".copper").setHTML(i.copper).removeClass("hide"), e.setAttribute("data-coins", i.total), e.setAttribute("data-digits", i.digits))
    },
    toInputs: function(e, o) {
      var i;
      e && (i = t.toObject(o), e.one("[name='gold']").set("value", i.gold), e.one("[name='silver']").set("value", i.silver), e.one("[name='copper']").set("value", i.copper))
    },
    toHTML: function(o, i) {
      var r = t.toObject(o),
        l = Boolean(i.hide),
        s = 0 === r.total,
        a = l && (s || 0 === r.gold) ? "hide" : "",
        n = l && (s || a && 0 === r.silver) ? "hide" : "",
        d = l && s ? "hide" : "",
        c = i.css || "";
      return r.total || (c += (c.length ? " " : "") + "empty"), e.Lang.sub("<div class='coins serif {css}' data-hide-empty='{hide}' data-coins='{total}' data-digits='{digits}'><div class='gold {hideGold}'>{gold}</div><div class='silver {hideSilver}'>{silver}</div><div class='copper {hideCopper}'>{copper}</div></div>", e.merge(r, {
        css: c,
        hide: l,
        hideGold: a,
        hideSilver: n,
        hideCopper: d
      }))
    },
    fromInputs: function(e) {
      var o, i = {
        copper: 0,
        silver: 0,
        gold: 0,
        total: 0,
        error: null
      };
      return e ? (o = {
        copper: Math.floor(Number(e.one("[name='copper']").get("value"))),
        silver: Math.floor(Number(e.one("[name='silver']").get("value"))),
        gold: Math.floor(Number(e.one("[name='gold']").get("value")))
      }, isNaN(o.copper) || isNaN(o.silver) || isNaN(o.gold) ? (o = i).error = "coins.parse" : o.total = t.toInteger(o), o) : (i.error = "coins.node", i)
    }
  }, e.namespace("GW2.Util").Coins = t
}), "@VERSION@", {
  requires: ["node-base"]
});
YUI.add("util-restricted", (function(t) {
  "use strict";
  var i = window.native;
  t.namespace("GW2.Util").restricted = function() {
    i.import("gw2/ui/dialog", (function(t) {
      t.toggleNative("EconRestrict")
    }))
  }
}));