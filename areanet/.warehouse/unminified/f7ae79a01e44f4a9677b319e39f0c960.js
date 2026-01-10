YUI.add("retailers", function(s) {
  var t, n, i, o = /\s+|\//g,
    l = s.one("#country-select"),
    r = s.all(".where-to-buy"),
    a = s.one("#retailers-list"),
    c = {
      AE: "United Arab Emirates",
      AT: "Austria",
      AU: "Australia",
      BE: "Belgium",
      BG: "Bulgaria",
      CA: "Canada",
      CH: "Switzerland",
      CY: "Cyprus",
      CZ: "Czech Republic",
      DE: "Germany",
      DK: "Denmark",
      EE: "Estonia",
      ES: "Spain",
      FI: "Finland",
      FR: "France",
      GB: "United Kingdom",
      GR: "Greece",
      HR: "Croatia",
      HU: "Hungary",
      IE: "Ireland",
      IL: "Israel",
      IS: "Iceland",
      IT: "Italy",
      LT: "Lithuania",
      LV: "Latvia",
      SA: "LATAM/South America",
      MT: "Malta",
      NL: "Netherlands",
      NO: "Norway",
      NZ: "New Zealand",
      PL: "Poland",
      PT: "Portugal",
      RO: "Romania",
      RS: "Serbia",
      SE: "Sweden",
      SK: "Slovakia",
      TR: "Turkey",
      US: "United States",
      ZA: "South Africa"
    };

  function e() {
    var a = s.HistoryHash.getHash().split("-");
    t = a[0], i = a[1]
  }

  function u(a, e) {
    var a = s.one("#" + a),
      t = a.all(".tabs .active"),
      n = a.one(`.tabs .${e} a`),
      i = a.all(".tabs-content .active"),
      a = a.one(".tabs-content ." + e);
    n && a && (t && t.removeClass("active"), i && i.removeClass("active"), n.addClass("active"), a.addClass("active"))
  }

  function d(a) {
    t && a !== t && t !== n && (n = t), t = a
  }

  function h(a, e) {
    a = a || t || l.one("option").getAttribute("value"), i = e || i || "physical", d(a), l.set("value", t), s.HistoryHash.setHash(t + "-" + i), e = t, a = s.one("#" + n) || r, e = s.one("#" + e), a.addClass("inactive"), e && e.removeClass("inactive"), u(t, i)
  }
  e(), t && s.Object.hasValue(c, t) ? h() : s.io("/ws/country", {
    on: {
      success: function(a, e) {
        d((e.responseText && c[e.responseText]).replace(o, ""))
      },
      end: function() {
        h()
      }
    }
  }), l.on("change", function() {
    h(this.get("value"))
  }), a.delegate("click", function(a) {
    var e = this.hasClass("physical") ? "physical" : this.hasClass("digital") && "digital";
    a.preventDefault(), u(t, e)
  }, ".tabs li"), s.on("hashchange", function() {
    e(), h()
  }, s.config.win)
}, "@VERSION", {
  requires: ["node", "history-hash", "io-base"]
});