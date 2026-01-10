! function(e) {
  var a = {};

  function t(n) {
    if (a[n]) return a[n].exports;
    var o = a[n] = {
      i: n,
      l: !1,
      exports: {}
    };
    return e[n].call(o.exports, o, o.exports, t), o.l = !0, o.exports
  }
  t.m = e, t.c = a, t.i = function(e) {
    return e
  }, t.d = function(e, a, n) {
    t.o(e, a) || Object.defineProperty(e, a, {
      configurable: !1,
      enumerable: !0,
      get: n
    })
  }, t.n = function(e) {
    var a = e && e.__esModule ? function() {
      return e.default
    } : function() {
      return e
    };
    return t.d(a, "a", a), a
  }, t.o = function(e, a) {
    return Object.prototype.hasOwnProperty.call(e, a)
  }, t.p = "", t(t.s = 75)
}([function(e, a) {
  e.exports = m
}, function(e, a, t) {
  "use strict";
  const n = {};
  n.init = function(e) {
    Object.keys(n).forEach((e => {
      "init" !== e && delete n[e]
    })), e && Object.keys(e).forEach((a => {
      n[a] = e[a]
    }))
  }, a.a = n
}, function(e, a, t) {
  "use strict";
  a.a = function(e) {
    return e.replaceAll("<br>", "-").replace(/[^a-zA-Z0-9]/g, "-").replace(/-{2,}/g, "-").replace(/^-+|-+$/g, "")
  }
}, function(e, a, t) {
  "use strict";
  var n = t(65);
  a.a = {
    view: ({
      attrs: e,
      children: a
    }) => m(e.element || "a", {
      class: n.a.button,
      href: e.href,
      type: e.type,
      disabled: e.disabled,
      "data-ga-event": "",
      "data-ga-label": e.gaLabel,
      "data-ga-category": e.gaCategory
    }, m("div", a), m("div", {
      "data-icon": e.icon || "cross"
    }))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(104),
    s = t.n(r),
    c = t(23);
  a.a = {
    view: () => [o()(c.a), o()(s.a, {
      lang: i.a.l10n.lang,
      showNav: i.a.hideFooterNav,
      curDate: new Date(i.a.timestamp).getFullYear(),
      routeLink: !0
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(9),
    r = t.n(i),
    s = t(1),
    c = t(67),
    l = t(6),
    d = t(10),
    u = t(21);
  const m = {};
  let g, p, f, h, b;
  a.a = {
    oninit: e => {
      g = s.a.l10n.lang, p = s.a.i18n.nav, f = s.a.l10n.langs, h = p.navlinks, b = !1, e.state.link = window.location.pathname.split("/")[2] || ""
    },
    oncreate: () => {
      t.i(l.b)()
    },
    view(e) {
      const a = o.a.route.get().split("#")[0];
      return [o()("button", {
        onclick: () => {
          b = !b
        },
        class: [b ? c.a.btnOpen : null, c.a.mobileMenuBtn].join(" "),
        "aria-label": b ? s.a.i18n.misc.buttons.labels.close : s.a.i18n.misc.buttons.labels.openmenu
      }, o()("span"), o()("span"), o()("span"), o()("span")), o()("nav", {
        class: [b ? c.a.menuOpen : null, c.a.primaryNavContainer].join(" "),
        "data-title": p.pageTitle,
        "aria-label": "main navigation"
      }, o()("ul", {
        class: c.a.primaryNav
      }, o()("li", {
        class: c.a.logo
      }, o()("a", {
        href: `/${g}`,
        oncreate: o.a.route.link,
        "data-ga-event": "",
        "data-ga-category": "Header"
      }, "ArenaNet")), Object.keys(h).map((e => o()("li", {
        class: h[e].dropdown ? c.a.mainNavLi : "",
        onmouseenter() {
          const a = h[e].slug;
          m[a] || (t.i(d.a)(s.a.preloadImages[a]), m[a] = !0)
        }
      }, o()("a", {
        href: `/${g}/${h[e].slug}`,
        oncreate: o.a.route.link,
        onclick: a === `/${g}/${h[e].slug}` ? e => {
          r.a.toY(0), e.preventDefault()
        } : void 0,
        "data-ga-event": "",
        "data-ga-category": "Header",
        "data-selected": s.a.pageName === h[e].slug ? "current" : ""
      }, h[e].name), h[e].dropdown ? o()("ul", {
        class: c.a.navChildBar
      }, Object.keys(h[e].dropdown).map((a => o()("li", {
        class: c.a.navChild
      }, h[e].dropdown[a].url ? o()("a", {
        class: c.a.ext,
        href: h[e].dropdown[a].url,
        target: "_blank",
        rel: "noopener"
      }, h[e].dropdown[a].name) : o()(u.a, {
        href: `/${g}/${h[e].dropdown[a].slug}`
      }, h[e].dropdown[a].name))))) : null))), o()("li", o()("a", {
        href: p.shoplink.slug,
        target: "_blank",
        rel: "noreferrer",
        "data-ga-event": "",
        "data-ga-category": "Header"
      }, p.shoplink.name))), o()("ul", {
        class: c.a.supportInfo
      }, o()("li", o()("a", {
        href: p.supportlink.slug,
        target: "_blank",
        rel: "noreferrer",
        "data-ga-event": "",
        "data-ga-category": "Header"
      }, p.supportlink.name)), o()("li", {
        class: c.a.langSelectBar
      }, f.map((e => o()("a", {
        class: e === g ? c.a.currentLang : c.a.langChild,
        href: window.location.pathname.replace(g, e)
      }, e))))))]
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = o, a.b = function() {
    const e = document.querySelectorAll("[data-ga-event]");
    Array.prototype.forEach.call(e, (e => {
      e.addEventListener("click", (e => {
        o(e.target.dataset.gaAction || "click", e.target.dataset.gaLabel || e.target.text, e.target.dataset.gaValue || 1, e.target.dataset.gaCategory)
      }))
    }))
  }, a.c = function(e, a) {
    const t = window.dataLayer || [];
    e = `/${n.a.l10n.lang}/${e}`, t.push({
      event: "pageview",
      url: e,
      title: a
    })
  }, a.d = function(e) {
    const a = document.getElementsByTagName("section");
    Array.prototype.forEach.call(a, (a => {
      const t = Date.now(),
        n = a.getBoundingClientRect().top < window.innerHeight,
        i = !a.dataset.gaTriggered || parseInt(a.dataset.gaTriggered, 10) + 3e4 < t;
      n && i && (a.dataset.gaTriggered = t, o("Section view", `${a.id.charAt(0).toUpperCase()+a.id.slice(1)}`, "", `${e} Page`))
    }))
  }, a.e = function(e, a) {
    const t = document.getElementById(a),
      n = Date.now(),
      i = t.getBoundingClientRect().top < window.innerHeight,
      r = !t.dataset.gaTriggered || parseInt(t.dataset.gaTriggered, 10) + 3e4 < n;
    i && r && (t.dataset.gaTriggered = n, o("Section view", `${t.id.charAt(0).toUpperCase()+t.id.slice(1)}`, "", `${e} Page`))
  };
  var n = t(1);

  function o(e, a, t, n) {
    (window.dataLayer || []).push({
      event: "event",
      eventCategory: n || "anet2",
      eventAction: e,
      eventLabel: a,
      eventValue: t
    })
  }
}, function(e, a) {
  e.exports = function(e, a, {
    timeout: t = 5e3,
    add: n = !1
  } = {}) {
    return e && a ? new Promise(((o, i) => {
      let r = !1;
      const s = setTimeout((() => {
        r || (console.error(`Timeout occurred before animation completed: ${a}`), r = !0, i(!1))
      }), t);
      e.addEventListener("animationend", (() => {
        r || (clearTimeout(s), r = !0, o(!0))
      }), {
        once: !0,
        passive: !0
      }), "http://www.w3.org/2000/svg" !== e.namespaceURI ? n ? e.classList.add(a) : e.className = a : n ? e.className.baseVal += ` ${a}` : e.className.baseVal = a
    })) : Promise.reject(!1)
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(66);
  const s = {
    view: e => o()("a", Object.assign({
      oncreate: o.a.route.link,
      onupdate: o.a.route.link
    }, e.attrs), e.children)
  };
  let c, l;
  a.a = {
    oninit: () => {
      c = i.a.l10n.lang, l = i.a.i18n.nav.navlinks
    },
    view: () => o()("nav", {
      class: r.a.footerNav,
      "aria-label": "footer navigation"
    }, o()("ul", Object.keys(l).map((e => o()("li", {
      class: r.a.navItem
    }, o()(s, {
      href: `/${c}/${l[e].slug}`,
      "data-ga-event": "",
      "data-ga-category": "Footer"
    }, l[e].name), o()("div", {
      class: r.a.bg,
      style: {
        "background-image": `url(${l[e].bg})`
      }
    }))))))
  }
}, function(e, a) {
  e.exports = zenscroll
}, function(e, a, t) {
  "use strict";
  a.a = e => {
    const a = (window.matchMedia && window.matchMedia("(min-width: 1200px)").matches ? e.desktop : e.mobile).map((e => new Promise((a => {
      const t = new Image;
      t.onload = () => {
        a()
      }, t.src = e
    }))));
    return Promise.all(a)
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(69);
  a.a = {
    view: e => {
      let a = "";
      return e.attrs.show && (a = i.a.maskCheck ? r.a.maskwipe : r.a.noMaskWipe), o()("div", {
        class: `${r.a.masklayer} ${a}`
      })
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mcfd584d06_container",
    logoLight: "mcfd584d06_logoLight",
    logoDark: "mcfd584d06_logoDark",
    taglineLight: "mcfd584d06_taglineLight",
    taglineDark: "mcfd584d06_taglineDark",
    panel: "mc86cc65a1_panel mcfd584d06_panel",
    jw: "jw",
    midgroundLayer: "mcfd584d06_midgroundLayer",
    soto: "soto",
    eod: "eod",
    pof: "pof",
    hot: "hot",
    gw2: "gw2",
    gw1: "gw1",
    playAnim: "mcfd584d06_playAnim",
    noInkMask: "mcfd584d06_noInkMask",
    inkMask: "mcfd584d06_inkMask",
    backgroundLayer: "mcfd584d06_backgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer",
    headline: "mca0efd9d2_headline mcfd584d06_headline",
    logo: "mcfd584d06_logo",
    exit: "mc86cc65a1_exit mcfd584d06_exit",
    noPanelMask: "mcfd584d06_noPanelMask"
  }
}, function(e, a, t) {
  "use strict";
  Object.defineProperty(a, "__esModule", {
    value: !0
  }), t.d(a, "footer", (function() {
    return n
  })), t.d(a, "halfFooter", (function() {
    return o
  })), t.d(a, "footerLight", (function() {
    return i
  })), t.d(a, "pageFooterNav", (function() {
    return r
  })), t.d(a, "navChildBar", (function() {
    return s
  })), t.d(a, "socialBar", (function() {
    return c
  })), t.d(a, "followUs", (function() {
    return l
  })), t.d(a, "socialIcon", (function() {
    return d
  })), t.d(a, "youtube", (function() {
    return u
  })), t.d(a, "facebook", (function() {
    return m
  })), t.d(a, "twitter", (function() {
    return g
  })), t.d(a, "twitch", (function() {
    return p
  })), t.d(a, "instagram", (function() {
    return f
  })), t.d(a, "tumblr", (function() {
    return h
  })), t.d(a, "flickr", (function() {
    return b
  })), t.d(a, "rss", (function() {
    return w
  })), t.d(a, "pof", (function() {
    return y
  })), t.d(a, "legalFooter", (function() {
    return v
  })), t.d(a, "logos", (function() {
    return _
  })), t.d(a, "logo", (function() {
    return k
  })), t.d(a, "nc", (function() {
    return L
  })), t.d(a, "anet", (function() {
    return M
  })), t.d(a, "anetpof", (function() {
    return x
  })), t.d(a, "rating", (function() {
    return I
  })), t.d(a, "pegi", (function() {
    return C
  })), t.d(a, "esrb", (function() {
    return N
  })), t.d(a, "usk", (function() {
    return T
  })), t.d(a, "navCleanup", (function() {
    return j
  })), t.d(a, "ncFooter", (function() {
    return S
  })), t.d(a, "pageFooterNavContainer", (function() {
    return A
  })), a.default = {
    footer: "mc392bf0ce_footer",
    halfFooter: "mc392bf0ce_footer mc392bf0ce_halfFooter",
    footerLight: "mc392bf0ce_footerLight",
    pageFooterNav: "mc392bf0ce_pageFooterNav",
    navChildBar: "mc392bf0ce_navChildBar",
    socialBar: "mc392bf0ce_socialBar",
    followUs: "mc392bf0ce_followUs",
    socialIcon: "mc392bf0ce_socialIcon",
    youtube: "mc392bf0ce_socialIcon mc392bf0ce_youtube",
    facebook: "mc392bf0ce_socialIcon mc392bf0ce_facebook",
    twitter: "mc392bf0ce_socialIcon mc392bf0ce_twitter",
    twitch: "mc392bf0ce_socialIcon mc392bf0ce_twitch",
    instagram: "mc392bf0ce_socialIcon mc392bf0ce_instagram",
    tumblr: "mc392bf0ce_socialIcon mc392bf0ce_tumblr",
    flickr: "mc392bf0ce_socialIcon mc392bf0ce_flickr",
    rss: "mc392bf0ce_socialIcon mc392bf0ce_rss",
    pof: "mc392bf0ce_pof",
    legalFooter: "mc392bf0ce_legalFooter",
    logos: "mc392bf0ce_logos",
    logo: "mc392bf0ce_logo",
    nc: "mc392bf0ce_logo mc392bf0ce_nc",
    anet: "mc392bf0ce_logo mc392bf0ce_anet",
    anetpof: "mc392bf0ce_logo mc392bf0ce_anet mc392bf0ce_anetpof",
    rating: "mc392bf0ce_rating",
    pegi: "mc392bf0ce_pegi",
    esrb: "mc392bf0ce_esrb",
    usk: "mc392bf0ce_usk",
    navCleanup: "mc392bf0ce_navCleanup",
    ncFooter: "mc392bf0ce_ncFooter",
    pageFooterNavContainer: "mc392bf0ce_pageFooterNavContainer"
  };
  var n = "mc392bf0ce_footer",
    o = "mc392bf0ce_footer mc392bf0ce_halfFooter",
    i = "mc392bf0ce_footerLight",
    r = "mc392bf0ce_pageFooterNav",
    s = "mc392bf0ce_navChildBar",
    c = "mc392bf0ce_socialBar",
    l = "mc392bf0ce_followUs",
    d = "mc392bf0ce_socialIcon",
    u = "mc392bf0ce_socialIcon mc392bf0ce_youtube",
    m = "mc392bf0ce_socialIcon mc392bf0ce_facebook",
    g = "mc392bf0ce_socialIcon mc392bf0ce_twitter",
    p = "mc392bf0ce_socialIcon mc392bf0ce_twitch",
    f = "mc392bf0ce_socialIcon mc392bf0ce_instagram",
    h = "mc392bf0ce_socialIcon mc392bf0ce_tumblr",
    b = "mc392bf0ce_socialIcon mc392bf0ce_flickr",
    w = "mc392bf0ce_socialIcon mc392bf0ce_rss",
    y = "mc392bf0ce_pof",
    v = "mc392bf0ce_legalFooter",
    _ = "mc392bf0ce_logos",
    k = "mc392bf0ce_logo",
    L = "mc392bf0ce_logo mc392bf0ce_nc",
    M = "mc392bf0ce_logo mc392bf0ce_anet",
    x = "mc392bf0ce_logo mc392bf0ce_anet mc392bf0ce_anetpof",
    I = "mc392bf0ce_rating",
    C = "mc392bf0ce_pegi",
    N = "mc392bf0ce_esrb",
    T = "mc392bf0ce_usk",
    j = "mc392bf0ce_navCleanup",
    S = "mc392bf0ce_ncFooter",
    A = "mc392bf0ce_pageFooterNavContainer"
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(28),
    r = t.n(i),
    s = t(1),
    c = t(70),
    l = t(23);
  a.a = {
    oninit: e => {
      e.state.flooding = r()(), e.state.mediaId = l.b.addMedia(e.attrs)
    },
    onremove: e => {
      l.b.removeMedia(e.state.mediaId)
    },
    view: e => o()("div", {
      class: c.a.video
    }, o()("button", {
      class: c.a.button,
      "aria-label": e.attrs.label || s.a.i18n.misc.buttons.play,
      title: e.attrs.label || s.a.i18n.misc.buttons.play,
      onclick: () => {
        l.b.open(e.state.mediaId, !1), e.state.flooding(!0)
      }
    }, e.children, o()("div", {
      class: c.a[`playBtn${e.state.fullscreen?"Fs":""}${e.children.length?"Abs":""}`]
    })), e.state.flooding() ? o()("div", {
      class: c.a.flood,
      onanimationend: () => {
        e.state.flooding(!1), l.b.showLightbox(!0)
      }
    }) : null)
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mcfc263cc3_container",
    panel: "mc86cc65a1_panel mcfc263cc3_panel",
    stickyPanel: "mcfc263cc3_stickyPanel",
    playAnim: "mcfc263cc3_playAnim",
    noInkMask: "mcfc263cc3_noInkMask",
    inkMask: "mcfc263cc3_inkMask",
    headline: "mca0efd9d2_headlineH2 mcfc263cc3_headline",
    exit: "mc86cc65a1_exit mcfc263cc3_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mc369d696c_container",
    panel: "mc86cc65a1_panel mc369d696c_panel",
    playAnim: "mc369d696c_playAnim",
    noInkMask: "mc369d696c_noInkMask",
    inkMask: "mc369d696c_inkMask",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline",
    bodyText: "mca0efd9d2_bodyText mc369d696c_bodyText",
    exit: "mc86cc65a1_exit mc369d696c_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mce9070436_container",
    panel: "mc86cc65a1_panel mce9070436_panel",
    noPanelMask: "mce9070436_noPanelMask",
    stickyPanel: "mce9070436_stickyPanel",
    playAnim: "mce9070436_playAnim",
    playAnim_Mask: "mce9070436_playAnim_Mask",
    playAnim_Fade: "mce9070436_playAnim_Fade",
    panelMask: "mce9070436_panelMask",
    preload: "mce9070436_preload",
    panelHeadlineContainer: "mce9070436_panelHeadlineContainer",
    panelImageContainer: "mce9070436_panelImageContainer",
    ctaContainer: "mce9070436_ctaContainer",
    scrollborder: "mce9070436_scrollborder",
    scrollborderActive: "mce9070436_scrollborder mce9070436_scrollborderActive",
    stickybutton: "mc05566e52_button mc05566e52_scrollButton mce9070436_stickybutton",
    fixedHomeElements: "mce9070436_fixedHomeElements",
    pageNumAndTagline: "mce9070436_pageNumAndTagline",
    pageNumContainer: "mce9070436_pageNumContainer",
    pagenum: "mce9070436_pagenum",
    taglineContainer: "mce9070436_taglineContainer",
    tagline: "mce9070436_tagline",
    headerText: "mca0efd9d2_headlineH1 mce9070436_headerText",
    subheader: "mca0efd9d2_bodyText mce9070436_subheader",
    loaded: "mce9070436_loaded",
    observer: "mce9070436_observer"
  }
}, function(e, a) {
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
}, function(e, a, t) {
  "use strict";
  a.a = {
    radius: "0.2em",
    border: "1px solid #e1e1e1",
    container: "mc86cc65a1_container mc8f74fda3_container",
    playAnim: "mc8f74fda3_playAnim",
    noInkMask: "mc8f74fda3_noInkMask",
    inkMask: "mc8f74fda3_inkMask",
    headline: "mca0efd9d2_headlineH2 mc8f74fda3_headline",
    bodyText: "mca0efd9d2_bodyText mc8f74fda3_bodyText",
    formContent: "mc8f74fda3_formContent",
    header: "mc8f74fda3_header",
    submitting: "mc8f74fda3_submitting",
    message: "mc8f74fda3_message",
    fieldset: "mc8f74fda3_fieldset",
    row: "mc8f74fda3_row",
    field: "mc8f74fda3_field",
    description: "mc8f74fda3_description",
    disclaimer: "mc8f74fda3_disclaimer",
    label: "mc8f74fda3_label",
    input: "mc8f74fda3_input",
    select: "mc8f74fda3_input mc8f74fda3_select",
    inputError: "mc8f74fda3_input mc8f74fda3_inputError",
    selectError: "mc8f74fda3_input mc8f74fda3_inputError mc8f74fda3_selectError",
    checkbox: "mc8f74fda3_checkbox",
    checkboxError: "mc8f74fda3_checkbox mc8f74fda3_checkboxError",
    errorText: "mc8f74fda3_errorText",
    submit: "mc8f74fda3_submit",
    exit: "mc8f74fda3_exit",
    errorContent: "mc8f74fda3_errorContent"
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(9),
    r = (t.n(i), t(1)),
    s = t(51),
    c = t(2),
    l = t(21);
  let d, u;
  a.a = {
    oninit: () => {
      d = r.a.i18n, u = r.a.l10n.lang
    },
    view() {
      const e = d.careers.panels.recruitmentScameWarning.header,
        a = t.i(c.a)(e),
        n = `/${u}/careers#${a}`;
      return !0 === r.a.scamWarningBannerHidden ? null : o()("div", {
        class: s.a.banner
      }, o()("div", {
        class: s.a.bannerContent
      }, o()("span", {
        class: s.a.informational
      }, "i"), o()("strong", e), o()(l.a, {
        href: n
      }, d.misc.buttons.labels.readmore), o()("a", {
        class: s.a.close,
        onclick: e => {
          r.a.scamWarningBannerHidden = !0, e.preventDefault()
        }
      }, "\u2718")))
    }
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(9),
    r = t.n(i);
  a.a = {
    view({
      attrs: e,
      children: a
    }) {
      const t = o.a.route.get().split("#")[0],
        [n, i] = e.href.split("#");
      return t === n ? o()("a", {
        href: e.href,
        onclick(a) {
          a.preventDefault(), window.history.replaceState({}, "", e.href);
          const t = document.getElementById(i);
          t && r.a.to(t)
        }
      }, a) : o()("a", {
        href: e.href,
        oncreate: o.a.route.link,
        onupdate: o.a.route.link
      }, a)
    }
  }
}, function(e, a, t) {
  "use strict";
  a.b = function({
    body: e
  }) {
    if (!e.jobs) throw new Error("No jobs returned in greenhouse response");
    return {
      jobs: e.jobs.map((e => ({
        title: e.title,
        absolute_url: e.absolute_url,
        id: `${e.id}`,
        content: e.content,
        departments: e.departments
      })))
    }
  }, a.a = function({
    body: e
  }) {
    if (!e.jobs) throw new Error("No jobs returned in ashby response");
    return {
      jobs: e.jobs.map((e => ({
        title: e.title,
        absolute_url: e.applyUrl,
        id: `${e.id}`,
        content: e.descriptionHtml,
        departments: [{
          name: e.department
        }]
      })))
    }
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(72),
    s = t(96);
  let c = {};

  function l(e, a, t) {
    const n = {};
    return e = e || window.innerWidth, (a = a || window.innerHeight) / e >= (t = t || .5625) ? (n.width = e, n.height = n.width * t) : (n.height = a, n.width = n.height / t), n
  }
  const d = {
    addMedia: e => s.a.addMedia(e),
    open: (e, a) => {
      s.a.open(e), !1 !== a && s.a.showLightbox(!0)
    },
    showLightbox: e => s.a.showLightbox(e),
    removeMedia: e => s.a.removeMedia(e),
    oninit: e => {
      e.state.mediaId = s.a.addMedia(e.attrs), e.state.attrs = {
        onclick: a => {
          a.preventDefault(), s.a.open(e.state.mediaId), s.a.showLightbox(!0)
        },
        href: e.attrs.ytId ? `https://www.youtube.com/watch?v=${e.attrs.ytId}` : e.attrs.src,
        class: r.a.lightboxButton
      }
    },
    onremove: e => {
      s.a.removeMedia(e.state.mediaId)
    },
    view: e => o()("a", e.state.attrs, e.children)
  };
  a.b = d;
  const u = {
    oninit: () => {
      c = l(), window.addEventListener("resize", (() => {
        c = l(), o.a.redraw()
      }), {
        passive: !0
      })
    },
    oncreate: e => {
      e.state.scrollWidth = e.dom.offsetWidth - e.dom.clientWidth
    },
    view: () => s.a.renderLightbox() ? o()("div", {
      class: s.a.showLightbox() ? r.a.overlay : r.a.overlayHidden,
      onclick: e => {
        e.target === e.currentTarget && (s.a.showLightbox(!1), s.a.close())
      }
    }, o()("div", {
      class: r.a.contentControls
    }, o()("button", {
      class: r.a.close,
      onclick: () => {
        s.a.showLightbox(!1), s.a.close()
      }
    }, i.a.i18n.misc.buttons.labels.close), o()("div", {
      class: r.a.content,
      style: {
        width: `${c.width}px`,
        height: `${c.height}px`
      }
    }, s.a.attrs().ytId ? o()("iframe", {
      class: r.a.iframe,
      id: s.a.iframeId,
      width: c.width,
      height: c.height,
      frameborder: 0,
      allowfullscreen: "",
      src: `https://www.youtube.com/embed/${s.a.attrs().ytId}?enablejsapi=1&autoplay=0`,
      oncreate: () => {
        s.a.createPlayer()
      },
      onremove: () => {
        s.a.destroyPlayer()
      }
    }) : null))) : o()("div", {
      class: r.a.preload
    })
  };
  a.a = u
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(73);
  const r = [0, 1, 2, 3];
  a.a = {
    view({
      attrs: e
    }) {
      const a = o()("div", {
        class: i.a.loading,
        "data-test": "loading"
      }, r.map((() => o()("div"))));
      return e.boxed ? o()("div", {
        class: i.a.boxed
      }, a) : a
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = function() {
    const e = document.location.hash.substring(1),
      a = e && document.getElementById(e);
    if (!a) return;
    setTimeout((() => {
      o.a.to(a)
    }), 400)
  };
  var n = t(9),
    o = t.n(n)
}, function(e, a, t) {
  "use strict";
  e.exports = function(e, a) {
    const {
      jobs: t
    } = e, n = a.reduce(((e, {
      from: a,
      to: t
    }) => (e[a] = t, e))), o = {}, i = {};
    return t.sort(((e, a) => e.title >= a.title ? 1 : -1)).forEach((e => {
      const a = {
        href: e.absolute_url,
        title: e.title.trim(),
        id: e.id
      };
      if ("General Applications" === a.title) return i.title = "Didn\u2019t Find a Role that Matches your Experience?", void(i.href = a.href);
      e.departments.forEach((e => {
        const t = n[e.name] || e.name;
        o[t] || (o[t] = []), o[t].push(a)
      }))
    })), {
      jobsByDept: Object.keys(o).sort().reduce(((e, a) => (e[a] = o[a], e)), {}),
      general: i
    }
  }
}, function(e, a, t) {
  "use strict";
  (function(e) {
    Object.defineProperty(a, "__esModule", {
      value: !0
    });
    var n = t(101);
    const o = {
        type: "xstate.init"
      },
      i = "xstate.assign";

    function r(e) {
      return void 0 === e ? [] : [].concat(e)
    }

    function s(e, a) {
      return "string" == typeof(e = "string" == typeof e && a && a[e] ? a[e] : e) ? {
        type: e
      } : "function" == typeof e ? {
        type: e.name,
        exec: e
      } : e
    }
    const c = "production" === e.env.NODE_ENV;

    function l(e) {
      return a => e === a
    }

    function d(e) {
      return "string" == typeof e ? {
        type: e
      } : e
    }

    function u(e, a) {
      return {
        value: e,
        context: a,
        actions: [],
        changed: !1,
        matches: l(e)
      }
    }

    function m(e, a, t) {
      let n = a,
        o = !1;
      return [e.filter((e => {
        if (e.type === i) {
          o = !0;
          let a = Object.assign({}, n);
          return "function" == typeof e.assignment ? a = e.assignment(n, t) : Object.keys(e.assignment).forEach((o => {
            a[o] = "function" == typeof e.assignment[o] ? e.assignment[o](n, t) : e.assignment[o]
          })), n = a, !1
        }
        return !0
      })), n, o]
    }
    const g = (e, a) => e.actions.forEach((({
      exec: t
    }) => t && t(e.context, a)));
    Object.defineProperty(a, "InterpreterStatus", {
      enumerable: !0,
      get: function() {
        return n.InterpreterStatus
      }
    }), a.assign = function(e) {
      return {
        type: i,
        assignment: e
      }
    }, a.createMachine = function(e, a = {}) {
      c || Object.keys(e.states).forEach((a => {
        if (e.states[a].states) throw new Error(`Nested finite states not supported.\n            Please check the configuration for the "${a}" state.`)
      }));
      const [t, n] = m(r(e.states[e.initial].entry).map((e => s(e, a.actions))), e.context, o), i = {
        config: e,
        _options: a,
        initialState: {
          value: e.initial,
          actions: t,
          context: n,
          matches: l(e.initial)
        },
        transition: (a, t) => {
          var n, o;
          const {
            value: g,
            context: p
          } = "string" == typeof a ? {
            value: a,
            context: e.context
          } : a, f = d(t), h = e.states[g];
          if (!c && !h) throw new Error(`State '${g}' not found on machine ${null!==(n=e.id)&&void 0!==n?n:""}`);
          if (h.on) {
            const a = r(h.on[f.type]);
            for (const t of a) {
              if (void 0 === t) return u(g, p);
              const {
                target: a,
                actions: n = [],
                cond: d = (() => !0)
              } = "string" == typeof t ? {
                target: t
              } : t, b = void 0 === a, w = null != a ? a : g, y = e.states[w];
              if (!c && !y) throw new Error(`State '${w}' not found on machine ${null!==(o=e.id)&&void 0!==o?o:""}`);
              if (d(p, f)) {
                const e = (b ? r(n) : [].concat(h.exit, n, y.entry).filter((e => e))).map((e => s(e, i._options.actions))),
                  [t, o, c] = m(e, p, f),
                  d = null != a ? a : g;
                return {
                  value: d,
                  context: o,
                  actions: t,
                  changed: a !== g || t.length > 0 || c,
                  matches: l(d)
                }
              }
            }
          }
          return u(g, p)
        }
      };
      return i
    }, a.interpret = function(e) {
      let a = e.initialState,
        t = n.InterpreterStatus.NotStarted;
      const i = new Set,
        r = {
          _machine: e,
          send: o => {
            t === n.InterpreterStatus.Running && (a = e.transition(a, o), g(a, d(o)), i.forEach((e => e(a))))
          },
          subscribe: e => (i.add(e), e(a), {
            unsubscribe: () => i.delete(e)
          }),
          start: i => {
            if (i) {
              const t = "object" == typeof i ? i : {
                context: e.config.context,
                value: i
              };
              if (a = {
                  value: t.value,
                  actions: [],
                  context: t.context,
                  matches: l(t.value)
                }, !c && !(a.value in e.config.states)) throw new Error(`Cannot start service in state '${a.value}'. The state is not found on machine${e.config.id?` '${e.config.id}'`:""}.`)
            } else a = e.initialState;
            return t = n.InterpreterStatus.Running, g(a, o), r
          },
          stop: () => (t = n.InterpreterStatus.Stopped, i.clear(), r),
          get state() {
            return a
          },
          get status() {
            return t
          }
        };
      return r
    }
  }).call(a, t(74))
}, function(e, a) {
  e.exports = stream
}, function(e, a) {
  var t;
  t = function() {
    return this
  }();
  try {
    t = t || Function("return this")() || (0, eval)("this")
  } catch (e) {
    "object" == typeof window && (t = window)
  }
  e.exports = t
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(42),
    l = t(5),
    d = t(8),
    u = t(4);
  let m;
  a.a = {
    name: "404",
    oninit: () => {
      s.a.hideFooterNav = !1, m = s.a.i18n.errors.fourohfour
    },
    onbeforeremove: e => r()(e.dom, c.a.exit).then((() => window.scrollTo(0, 0))),
    view: () => o()("main", {
      class: c.a.container
    }, o()(l.a), o()("section", {
      class: c.a.errorContent
    }, o()("div", o()("h1", {
      class: c.a.headline
    }, m.errorTitle), o()("p", {
      class: c.a.bodyText
    }, o.a.trust(m.errorMsg))), o()("img", {
      class: c.a.errorImage,
      src: "https://cdn.arena.net/wp-content/uploads/2013/08/404-Quaggan.jpg",
      alt: "404 quaggan"
    })), o()(d.a), o()(u.a))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(15),
    l = t(5),
    d = t(11),
    u = t(8),
    m = t(4),
    g = t(6),
    p = t(25),
    f = t(76),
    h = t(77),
    b = t(10);
  const w = [f.a, h.a];
  a.a = {
    oninit: e => {
      s.a.about = {}, s.a.loaded = !1, s.a.pageName = "about", s.a.hideFooterNav = !1, e.state.panelHeights = [], t.i(b.a)(s.a.preloadImages.about).then((() => {
        e.state.imagesLoaded = !0, o.a.redraw()
      }))
    },
    oncreate: () => {
      t.i(g.c)("about", "About Us"), t.i(p.a)()
    },
    onbeforeremove: () => r()(s.a.mainVnode, c.a.exit).then((() => window.scrollTo(0, 0))),
    view: e => [o()(l.a), o()("main", {
      oncreate: e => {
        s.a.mainVnode = e.dom
      },
      class: [c.a.container, s.a.maskCheck ? c.a.inkMask : c.a.noInkMask].join(" ")
    }, w.map(((e, a) => o()("section", {
      id: e.name,
      class: c.a.panel
    }, o()(w[a])))), o()(u.a), o()(m.a), o()(d.a, {
      show: e.state.imagesLoaded
    }))]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(16),
    l = t(5),
    d = t(11),
    u = t(8),
    m = t(4),
    g = t(6),
    p = t(10),
    f = t(25),
    h = t(80),
    b = t(79),
    w = t(82),
    y = t(81),
    v = t(83),
    _ = t(20);
  const k = [h.a, b.a, w.a, y.a, v.a];

  function L() {
    t.i(g.d)("Careers")
  }
  a.a = {
    oninit: e => {
      s.a.careers = {}, s.a.loaded = !1, s.a.pageName = "careers", s.a.hideFooterNav = !1, e.state.fixedSlides = k.length, t.i(p.a)(s.a.preloadImages.careers).then((() => {
        e.state.imagesLoaded = !0, o.a.redraw()
      }))
    },
    oncreate: () => {
      t.i(g.c)("careers", "Careers"), window.addEventListener("scroll", L, {
        passive: !0
      }), t.i(f.a)()
    },
    onbeforeremove: () => (window.removeEventListener("scroll", L, {
      passive: !0
    }), r()(s.a.mainVnode, c.a.exit).then((() => window.scrollTo(0, 0)))),
    view: e => [o()(l.a), o()("main", {
      oncreate: ({
        dom: e
      }) => {
        s.a.mainVnode = e
      },
      class: [c.a.container, s.a.maskCheck ? c.a.inkMask : c.a.noInkMask].join(" ")
    }, k.map(((e, a) => o()("section", {
      id: e.name,
      class: c.a.panel,
      "aria-labelledby": e.name
    }, o()(k[a])))), o()(d.a, {
      show: e.state.imagesLoaded
    }), o()(u.a), o()(m.a)), o()(_.a)]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(45),
    l = t(5),
    d = t(8),
    u = t(4),
    m = t(24),
    g = t(3),
    p = (t(6), t(22)),
    f = t(20),
    h = t(26);
  t.n(h);
  let b, w;

  function y(e) {
    const a = document.createElement("textarea");
    return a.innerHTML = e, a.value
  }
  a.a = {
    oninit: e => {
      s.a.job = {}, s.a.pageName = "careers", o.a.request(`${s.a.jobs.url}?content=true`).then((e => {
        let a;
        a = s.a.jobs.useAshby ? t.i(p.a)({
          body: e
        }) : t.i(p.b)({
          body: e
        });
        const n = o.a.route.param("id");
        b = a.jobs.find((e => e.id === n))
      })).catch((e => {
        w = !0
      }))
    },
    onbeforeremove: e => r()(e.dom, c.a.exit).then((() => window.scrollTo(0, 0))),
    view: e => [o()(l.a), o()("main", {
      class: c.a.container
    }, o()(l.a), o()("section", {
      id: o.a.route.param("id"),
      class: c.a.panel
    }, o()("div", {
      class: c.a.textWrapper
    }, b ? [o()("h1", {
      class: c.a.headline
    }, b.title), o.a.trust(y(b.content)), o()("div", {
      class: c.a.applyNow
    }, o()(g.a, {
      href: `${b.absolute_url}#app`,
      target: "_blank"
    }, "Apply Now"))] : null, b || w ? null : o()(m.a), w ? o()("div", {
      class: c.a.error
    }, o()("p", "Sorry, we couldn't find that job listing."), o()("p", "See current job openings: ", o()("a", {
      href: s.a.jobs.boardUrl
    }, s.a.jobs.boardUrl))) : null)), o()(d.a), o()(u.a)), o()(f.a)]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(52),
    l = t(5),
    d = t(11),
    u = t(8),
    m = t(4),
    g = t(6),
    p = t(10),
    f = t(2);
  let h;
  a.a = {
    oninit: e => {
      s.a.contact = {}, s.a.loaded = !1, s.a.pageName = "contact", s.a.hideFooterNav = !1, e.state.panelHeights = [], h = s.a.i18n.contact, e.state.followLinks = Object.keys(s.a.i18n.footer.socials), t.i(p.a)(s.a.preloadImages.contact).then((() => {
        e.state.imagesLoaded = !0, o.a.redraw()
      }))
    },
    oncreate: () => {
      t.i(g.c)("contact", "Contact Us")
    },
    onbeforeremove: () => r()(s.a.mainVnode, c.a.exit).then((() => window.scrollTo(0, 0))),
    view: e => [o()(l.a), o()("main", {
      oncreate: e => {
        s.a.mainVnode = e.dom
      },
      class: [c.a.container, s.a.maskCheck ? c.a.inkMask : c.a.noInkMask].join(" ")
    }, o()("section", {
      class: c.a.contactContainer
    }, o()("div", {
      class: c.a.contactContent
    }, o()("h1", {
      class: c.a.headline,
      id: t.i(f.a)(h.primary.heading),
      "data-test": "header"
    }, h.primary.heading), o()("h2", {
      class: c.a.heading
    }, h.cs.heading), o()("p", {
      class: c.a.bodyText
    }, h.cs.body), o()("a", {
      class: c.a.contactLink,
      href: h.cs.url,
      target: "_blank"
    }, h.cs.url), o()("h2", {
      class: c.a.heading
    }, h.press.heading), o()("p", {
      class: c.a.bodyText
    }, h.press.body), o()("a", {
      class: c.a.contactLink,
      href: `mailto:${h.press.url}`
    }, h.press.url), o()("p", {
      class: c.a.bodyText
    }, h.address.heading), o()("ul", {
      class: c.a.bodyText
    }, o()("li", "ArenaNet, LLC."), o()("li", "3180 139th Ave SE"), o()("li", "5th Floor"), o()("li", "Bellevue, WA 98005")), o()("h2", {
      class: c.a.heading
    }, h.social.heading), o()("div", {
      class: c.a.socialBar
    }, e.state.followLinks.map((e => o()("a", {
      onclick: () => {
        t.i(g.a)("SocialMedia", s.a.i18n.footer.socials[e].label, 1)
      },
      class: c.a[e],
      href: s.a.i18n.footer.socials[e].href,
      target: "_blank",
      rel: "noreferrer",
      "aria-label": s.a.i18n.footer.socials[e].label
    })))))), o()(d.a, {
      show: e.state.imagesLoaded
    }), o()(u.a), o()(m.a))]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(12),
    l = t(5),
    d = t(11),
    u = t(8),
    m = t(4),
    g = t(91),
    p = t(88),
    f = t(90),
    h = t(84),
    b = t(89),
    w = t(87),
    y = t(86),
    v = t(85),
    _ = t(10);
  const k = [g.a, p.a, f.a, h.a, b.a, w.a, y.a, v.a];
  a.a = {
    oninit: e => {
      s.a.games = {}, s.a.loaded = !1, s.a.hideFooterNav = !1, s.a.pageName = "games", e.state.panelHeights = [], t.i(_.a)(s.a.preloadImages.games).then((() => {
        e.state.imagesLoaded = !0, o.a.redraw()
      }))
    },
    onbeforeremove: () => r()(s.a.mainVnode, c.a.exit).then((() => window.scrollTo(0, 0))),
    view: e => [o()(l.a), o()("main", {
      oncreate: e => {
        s.a.mainVnode = e.dom
      },
      class: [c.a.container, s.a.maskCheck ? c.a.inkMask : c.a.noInkMask].join(" ")
    }, k.map(((e, a) => o()("section", {
      id: e.name,
      class: c.a.panel
    }, o()(k[a])))), o()(u.a), o()(m.a), o()(d.a, {
      key: "games",
      show: e.state.imagesLoaded
    }))]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(9),
    r = t.n(i),
    s = t(7),
    c = t.n(s),
    l = t(1),
    d = t(17),
    u = t(71),
    m = t(95),
    g = t(5),
    p = t(4),
    f = t(6),
    h = t(92),
    b = t(94),
    w = t(93),
    y = t(10);
  const v = [h.a, b.a, w.a];

  function _(e) {
    l.a.homepanels.forEach((a => {
      e === a.vnode.dom.id && (l.a.homepanels[l.a.activeIndex].playAnim = !0, l.a.stickyCheck ? t.i(f.e)("Home", l.a.activeIndex) : t.i(f.d)("Home"))
    }))
  }
  const k = {
      root: l.a.observer,
      threshold: [.175, .825]
    },
    L = Math.round(.2 * window.innerHeight);
  let M, x;
  const I = new IntersectionObserver((e => {
    e.forEach((e => {
      l.a.stickyCheck ? (e.intersectionRatio < k.threshold[0] && (l.a.activeIndex = Number(e.target.id) + 1), e.intersectionRatio > k.threshold[1] && (l.a.activeIndex = l.a.activeIndex > Number(e.target.id) ? Number(e.target.id) : l.a.activeIndex), _(e.target.id)) : e.intersectionRatio >= .75 && (l.a.activeIndex = Number(e.target.id), _(e.target.id)), l.a.finalPanel = l.a.activeIndex + 1 === l.a.keys.length, o.a.redraw()
    }))
  }), k);
  a.a = {
    oninit: () => {
      l.a.keys = Object.keys(v), l.a.home = {}, l.a.imgCount = 0, l.a.loaded = !1, l.a.pageName = "home", l.a.preload = !0, l.a.hideFooterNav = !0, l.a.activeIndex = 0, M = l.a.i18n.home.panels, l.a.homepanels = v.map(((e, a) => ({
        playAnim: !1,
        num: a
      }))), t.i(y.a)(l.a.preloadImages.home).then((() => {
        window.scrollTo(0, 0), l.a.preload = !1, setTimeout((() => {
          l.a.loaded = !0, sessionStorage.setItem("loader", "false"), o.a.redraw()
        }), 10)
      }))
    },
    oncreate: e => {
      l.a.home.dom = e, t.i(f.c)("", "Home")
    },
    onbeforeremove: () => (I.disconnect(), c()(l.a.home.dom.dom, u.a.exit, {
      add: !0,
      timeout: 5e4
    })),
    view: e => o()("main", {
      class: [l.a.preload ? d.a.preload : null, l.a.loaded ? d.a.loaded : null, d.a.container].join(" ")
    }, o()(m.a), o()(g.a), v.map(((a, t) => o()("section", {
      oncreate: a => {
        l.a.homepanels[t].vnode = a, I.observe(a.dom), e.state.panelsHeight = a.dom.offsetHeight
      },
      id: t,
      "aria-label": v[t].name,
      "data-ga-section": "",
      class: [l.a.homepanels[t].playAnim ? d.a.playAnim : "", l.a.maskCheck ? d.a.panelMask : d.a.noPanelMask, l.a.stickyCheck ? d.a.stickyPanel : "", d.a.panel].join(" "),
      style: {
        marginBottom: l.a.stickyCheck ? `${L}px` : 0
      }
    }, o()(v[t])))), o()("div", {
      class: d.a.fixedHomeElements
    }, o()("div", {
      class: d.a.scrollborderActive,
      style: `transform: scaleY(${1/l.a.homepanels.length})`
    }), o()("div", {
      onupdate: () => {
        x = (l.a.activeIndex + 1) / l.a.homepanels.length, o.a.redraw()
      },
      class: d.a.scrollborderActive,
      style: `transform: scaleY(${x})`
    }), o()("div", {
      class: d.a.scrollborder
    }), o()("div", {
      oncreate: e => {
        l.a.observer = e.dom
      },
      class: d.a.observer
    }), l.a.desktopSize ? o()("div", {
      class: d.a.pageNumAndTagline
    }, o()("div", {
      class: d.a.pageNumContainer
    }, o()("ul", {
      style: `transform: translateY(-${70*l.a.activeIndex}px)`
    }, v.map(((e, a) => o()("li", {
      class: d.a.pagenum
    }, `0${a+1}`))))), o()("div", {
      class: d.a.taglineContainer
    }, o()("ul", {
      style: `transform: translateY(-${40*l.a.activeIndex}px)`
    }, v.map(((e, a) => o()("li", {
      class: d.a.tagline
    }, M[v[a].name].tagline)))))) : null, l.a.desktopSize ? o()("button", {
      onclick: () => {
        const a = l.a.stickyCheck ? L : 1,
          t = l.a.finalPanel ? 0 : (l.a.activeIndex + 1) * e.state.panelsHeight + (l.a.activeIndex + 1) * a;
        r.a.toY(t)
      },
      class: d.a.stickybutton
    }, o()("div", l.a.finalPanel ? M[v[0].name].tagline : M[v[l.a.activeIndex + 1].name].tagline), o()("div", {
      "data-icon": l.a.finalPanel ? "arrowUp" : "arrowDown"
    })) : null), o()(p.a))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(7),
    r = t.n(i),
    s = t(1),
    c = t(64),
    l = t(5),
    d = t(11),
    u = t(8),
    m = t(4),
    g = t(6),
    p = t(10),
    f = t(2),
    h = t(24);
  let b;
  a.a = {
    oninit: e => {
      s.a.loaded = !1, s.a.pageName = "legal", s.a.hideFooterNav = !1, e.state.panelHeights = [], b = s.a.i18n.legal, e.state.followLinks = Object.keys(s.a.i18n.footer.socials), t.i(p.a)(s.a.preloadImages.contact).then((() => {
        e.state.imagesLoaded = !0, o.a.redraw()
      })), s.a.tripleEscape = e => {
        let {
          keyQueue: a
        } = s.a;
        a || (a = s.a.keyQueue = []), "Escape" === e.code ? (a.push(Date.now()), a.length > 3 && a.shift(), 3 === a.length && a[2] - a[0] < 1e3 && (s.a.allowUnlisted = !s.a.allowUnlisted, o.a.redraw())) : s.a.keyQueue = []
      }
    },
    oncreate: () => {
      t.i(g.c)("legal", "Legal"), window.addEventListener("keydown", s.a.tripleEscape)
    },
    onbeforeremove: () => r()(s.a.mainVnode, c.a.exit).then((() => window.scrollTo(0, 0))),
    onremove: () => {
      window.removeEventListener("keydown", s.a.tripleEscape)
    },
    view: e => {
      const a = o.a.route.param("path"),
        n = a ? s.a.legal[a].title : b.primary.heading;
      return a && !s.a.legal[a].body && fetch(`/${s.a.l10n.lang}/legal/${a}/json`).then((e => e.json())).then((e => {
        if (!e.body) throw new Error("No legal body");
        s.a.legal[a].body = e.body
      })).catch((e => {
        console.error(e), s.a.legal[a].body = s.a.i18n.errors.fourohfour.errorMsg
      })).finally((() => o.a.redraw())), [o()(l.a), o()("main", {
        oncreate: e => {
          s.a.mainVnode = e.dom
        },
        class: [c.a.container, s.a.maskCheck ? c.a.inkMask : c.a.noInkMask].join(" ")
      }, o()("section", {
        class: a ? c.a.legalContainerPage : c.a.legalContainer
      }, o()("div", {
        class: c.a.legalContent
      }, a ? o()("a", {
        href: `/${s.a.l10n.lang}/legal`,
        oncreate: o.a.route.link,
        onupdate: o.a.route.link,
        class: c.a.backLink,
        "data-test": "back-link"
      }, b.primary.heading) : null, o()("h1", {
        class: c.a.headline,
        id: t.i(f.a)(n),
        "data-test": "header"
      }, n), a ? o()("div", {
        class: c.a.legalBody,
        "data-test": "legal-body"
      }, s.a.legal[a].body ? o.a.trust(s.a.legal[a].body) : o()(h.a, {
        boxed: !0
      })) : o()("ul", {
        class: c.a.nav,
        "data-test": "legal-list"
      }, Object.entries(s.a.legal).filter((([e, a]) => a.title && (!a.unlisted || s.a.allowUnlisted))).map((([e, a]) => o()("li", o()("a", {
        href: `/${s.a.l10n.lang}/legal/${e}`,
        oncreate: o.a.route.link,
        onupdate: o.a.route.link
      }, a.title))))))), o()(d.a, {
        show: e.state.imagesLoaded
      }), o()(u.a), o()(m.a))]
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = function(e, a, t) {
    let n;
    return function() {
      clearTimeout(n), n = setTimeout((() => {
        n = null, t || e.apply(this, arguments)
      }), a), t && !n && e.apply(this, arguments)
    }
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(9),
    r = t.n(i),
    s = t(7),
    c = t.n(s),
    l = t(109),
    d = t.n(l),
    u = t(108),
    m = t(1),
    g = t(19),
    p = t(5),
    f = t(8),
    h = t(4),
    b = t(3),
    w = t(98),
    y = t(97),
    v = (t.n(y), t(100));
  let _, k, L, M, x = {
    errors: {}
  };
  a.a = {
    name: "Vendor apply",
    oninit: () => {
      m.a.hideFooterNav = !1, _ = m.a.i18n.vendorForm
    },
    onbeforeremove: e => c()(e.dom, g.a.exit).then((() => window.scrollTo(0, 0))),
    view: () => o()("main", {
      class: g.a.container
    }, o()(p.a), o()("section", {
      class: g.a.formContent
    }, o()("h1", {
      class: g.a.headline,
      "data-test": "header"
    }, _.header), k || L ? o()("p", {
      class: g.a.message,
      "data-test": "vendor-form-" + (k ? "error" : "success")
    }, k ? [o()("img", {
      src: "https://2arenanet2.staticwars.com/img/icons/alert.b3969867.svg",
      alt: ""
    }), o()("span", _.error)] : null, k || L) : [o()("p", {
      class: g.a.bodyText
    }, _.subHeader), o()("form", {
      action: `${m.a.wapiUrl}/api/vendor/form`,
      method: "POST",
      class: M ? g.a.submitting : "",
      oncreate({
        dom: e
      }) {
        m.a.formDom = e
      },
      async onsubmit(e) {
        e.preventDefault();
        const a = t.i(u.a)(e.target);
        if (x = d.a.validate(a, v.a), Object.keys(x.errors).length) {
          const e = Object.keys(x.errors)[0];
          return void m.a.formDom.querySelector(`[name=${e}]`).scrollIntoView({
            behavior: "smooth"
          })
        }
        const n = new FormData;
        Object.entries(t.i(y.kabobToCamel)(a)).forEach((([e, a]) => {
          "file" !== e ? n.append(e, a) : n.append(e, m.a.fileToSave)
        }));
        try {
          M = !0, o.a.redraw();
          const e = await fetch(this.action, {
            method: this.method,
            body: n
          });
          if (e.ok) return void(L = _.success);
          const {
            message: a
          } = await e.json();
          if (k = _.errors[a], !k) throw new Error("Unknown error")
        } catch (e) {
          k = _.errors.unknownError
        } finally {
          o.a.redraw(), r.a.toY(0)
        }
      }
    }, Object.entries(v.b).map((([e, a]) => {
      if (a.condition) {
        if (!m.a.formDom) return null;
        const {
          field: e,
          value: t
        } = a.condition, n = m.a.formDom.querySelector(`[name=${e}]`);
        if (!n || n.value !== t) return null
      }
      return o()("fieldset", {
        class: g.a.fieldset,
        "data-test": "vendor-form-fieldset"
      }, o()("h3", {
        class: g.a.header
      }, a.label), a.description ? o()("p", {
        class: g.a.description
      }, a.description) : null, o()(w.a, {
        fields: a.fields,
        results: x
      }), a.disclaimer ? o()("p", {
        class: g.a.disclaimer
      }, a.disclaimer) : null)
    })), o()("div", {
      class: g.a.submit
    }, o()(b.a, {
      element: "button",
      type: "submit",
      icon: "arrowRight"
    }, _.submit)))]), o()(f.a), o()(h.a))
  }
}, function(e, a) {
  ! function(e, a) {
    "use strict";
    if ("IntersectionObserver" in e && "IntersectionObserverEntry" in e && "intersectionRatio" in e.IntersectionObserverEntry.prototype) "isIntersecting" in e.IntersectionObserverEntry.prototype || Object.defineProperty(e.IntersectionObserverEntry.prototype, "isIntersecting", {
      get: function() {
        return this.intersectionRatio > 0
      }
    });
    else {
      var t = [];
      o.prototype.THROTTLE_TIMEOUT = 100, o.prototype.POLL_INTERVAL = null, o.prototype.USE_MUTATION_OBSERVER = !0, o.prototype.observe = function(e) {
        if (!this._observationTargets.some((function(a) {
            return a.element == e
          }))) {
          if (!e || 1 != e.nodeType) throw new Error("target must be an Element");
          this._registerInstance(), this._observationTargets.push({
            element: e,
            entry: null
          }), this._monitorIntersections(), this._checkForIntersections()
        }
      }, o.prototype.unobserve = function(e) {
        this._observationTargets = this._observationTargets.filter((function(a) {
          return a.element != e
        })), this._observationTargets.length || (this._unmonitorIntersections(), this._unregisterInstance())
      }, o.prototype.disconnect = function() {
        this._observationTargets = [], this._unmonitorIntersections(), this._unregisterInstance()
      }, o.prototype.takeRecords = function() {
        var e = this._queuedEntries.slice();
        return this._queuedEntries = [], e
      }, o.prototype._initThresholds = function(e) {
        var a = e || [0];
        return Array.isArray(a) || (a = [a]), a.sort().filter((function(e, a, t) {
          if ("number" != typeof e || isNaN(e) || e < 0 || e > 1) throw new Error("threshold must be a number between 0 and 1 inclusively");
          return e !== t[a - 1]
        }))
      }, o.prototype._parseRootMargin = function(e) {
        var a = (e || "0px").split(/\s+/).map((function(e) {
          var a = /^(-?\d*\.?\d+)(px|%)$/.exec(e);
          if (!a) throw new Error("rootMargin must be specified in pixels or percent");
          return {
            value: parseFloat(a[1]),
            unit: a[2]
          }
        }));
        return a[1] = a[1] || a[0], a[2] = a[2] || a[0], a[3] = a[3] || a[1], a
      }, o.prototype._monitorIntersections = function() {
        this._monitoringIntersections || (this._monitoringIntersections = !0, this.POLL_INTERVAL ? this._monitoringInterval = setInterval(this._checkForIntersections, this.POLL_INTERVAL) : (i(e, "resize", this._checkForIntersections, !0), i(a, "scroll", this._checkForIntersections, !0), this.USE_MUTATION_OBSERVER && "MutationObserver" in e && (this._domObserver = new MutationObserver(this._checkForIntersections), this._domObserver.observe(a, {
          attributes: !0,
          childList: !0,
          characterData: !0,
          subtree: !0
        }))))
      }, o.prototype._unmonitorIntersections = function() {
        this._monitoringIntersections && (this._monitoringIntersections = !1, clearInterval(this._monitoringInterval), this._monitoringInterval = null, r(e, "resize", this._checkForIntersections, !0), r(a, "scroll", this._checkForIntersections, !0), this._domObserver && (this._domObserver.disconnect(), this._domObserver = null))
      }, o.prototype._checkForIntersections = function() {
        var a = this._rootIsInDom(),
          t = a ? this._getRootRect() : {
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            width: 0,
            height: 0
          };
        this._observationTargets.forEach((function(o) {
          var i = o.element,
            r = s(i),
            c = this._rootContainsTarget(i),
            l = o.entry,
            d = a && c && this._computeTargetAndRootIntersection(i, t),
            u = o.entry = new n({
              time: e.performance && performance.now && performance.now(),
              target: i,
              boundingClientRect: r,
              rootBounds: t,
              intersectionRect: d
            });
          l ? a && c ? this._hasCrossedThreshold(l, u) && this._queuedEntries.push(u) : l && l.isIntersecting && this._queuedEntries.push(u) : this._queuedEntries.push(u)
        }), this), this._queuedEntries.length && this._callback(this.takeRecords(), this)
      }, o.prototype._computeTargetAndRootIntersection = function(t, n) {
        if ("none" != e.getComputedStyle(t).display) {
          for (var o, i, r, c, d, u, m, g, p = s(t), f = l(t), h = !1; !h;) {
            var b = null,
              w = 1 == f.nodeType ? e.getComputedStyle(f) : {};
            if ("none" == w.display) return;
            if (f == this.root || f == a ? (h = !0, b = n) : f != a.body && f != a.documentElement && "visible" != w.overflow && (b = s(f)), b && (o = b, i = p, r = void 0, c = void 0, d = void 0, u = void 0, m = void 0, g = void 0, r = Math.max(o.top, i.top), c = Math.min(o.bottom, i.bottom), d = Math.max(o.left, i.left), u = Math.min(o.right, i.right), g = c - r, !(p = (m = u - d) >= 0 && g >= 0 && {
                top: r,
                bottom: c,
                left: d,
                right: u,
                width: m,
                height: g
              }))) break;
            f = l(f)
          }
          return p
        }
      }, o.prototype._getRootRect = function() {
        var e;
        if (this.root) e = s(this.root);
        else {
          var t = a.documentElement,
            n = a.body;
          e = {
            top: 0,
            left: 0,
            right: t.clientWidth || n.clientWidth,
            width: t.clientWidth || n.clientWidth,
            bottom: t.clientHeight || n.clientHeight,
            height: t.clientHeight || n.clientHeight
          }
        }
        return this._expandRectByRootMargin(e)
      }, o.prototype._expandRectByRootMargin = function(e) {
        var a = this._rootMarginValues.map((function(a, t) {
            return "px" == a.unit ? a.value : a.value * (t % 2 ? e.width : e.height) / 100
          })),
          t = {
            top: e.top - a[0],
            right: e.right + a[1],
            bottom: e.bottom + a[2],
            left: e.left - a[3]
          };
        return t.width = t.right - t.left, t.height = t.bottom - t.top, t
      }, o.prototype._hasCrossedThreshold = function(e, a) {
        var t = e && e.isIntersecting ? e.intersectionRatio || 0 : -1,
          n = a.isIntersecting ? a.intersectionRatio || 0 : -1;
        if (t !== n)
          for (var o = 0; o < this.thresholds.length; o++) {
            var i = this.thresholds[o];
            if (i == t || i == n || i < t != i < n) return !0
          }
      }, o.prototype._rootIsInDom = function() {
        return !this.root || c(a, this.root)
      }, o.prototype._rootContainsTarget = function(e) {
        return c(this.root || a, e)
      }, o.prototype._registerInstance = function() {
        t.indexOf(this) < 0 && t.push(this)
      }, o.prototype._unregisterInstance = function() {
        var e = t.indexOf(this); - 1 != e && t.splice(e, 1)
      }, e.IntersectionObserver = o, e.IntersectionObserverEntry = n
    }

    function n(e) {
      this.time = e.time, this.target = e.target, this.rootBounds = e.rootBounds, this.boundingClientRect = e.boundingClientRect, this.intersectionRect = e.intersectionRect || {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        width: 0,
        height: 0
      }, this.isIntersecting = !!e.intersectionRect;
      var a = this.boundingClientRect,
        t = a.width * a.height,
        n = this.intersectionRect,
        o = n.width * n.height;
      this.intersectionRatio = t ? Number((o / t).toFixed(4)) : this.isIntersecting ? 1 : 0
    }

    function o(e, a) {
      var t, n, o, i = a || {};
      if ("function" != typeof e) throw new Error("callback must be a function");
      if (i.root && 1 != i.root.nodeType) throw new Error("root must be an Element");
      this._checkForIntersections = (t = this._checkForIntersections.bind(this), n = this.THROTTLE_TIMEOUT, o = null, function() {
        o || (o = setTimeout((function() {
          t(), o = null
        }), n))
      }), this._callback = e, this._observationTargets = [], this._queuedEntries = [], this._rootMarginValues = this._parseRootMargin(i.rootMargin), this.thresholds = this._initThresholds(i.threshold), this.root = i.root || null, this.rootMargin = this._rootMarginValues.map((function(e) {
        return e.value + e.unit
      })).join(" ")
    }

    function i(e, a, t, n) {
      "function" == typeof e.addEventListener ? e.addEventListener(a, t, n || !1) : "function" == typeof e.attachEvent && e.attachEvent("on" + a, t)
    }

    function r(e, a, t, n) {
      "function" == typeof e.removeEventListener ? e.removeEventListener(a, t, n || !1) : "function" == typeof e.detatchEvent && e.detatchEvent("on" + a, t)
    }

    function s(e) {
      var a;
      try {
        a = e.getBoundingClientRect()
      } catch (e) {}
      return a ? (a.width && a.height || (a = {
        top: a.top,
        right: a.right,
        bottom: a.bottom,
        left: a.left,
        width: a.right - a.left,
        height: a.bottom - a.top
      }), a) : {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        width: 0,
        height: 0
      }
    }

    function c(e, a) {
      for (var t = a; t;) {
        if (t == e) return !0;
        t = l(t)
      }
      return !1
    }

    function l(e) {
      var a = e.parentNode;
      return a && 11 == a.nodeType && a.host ? a.host : a
    }
  }(window, document)
}, function(e, a) {
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
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mc71d2a2ed_container",
    playAnim: "mc71d2a2ed_playAnim",
    noInkMask: "mc71d2a2ed_noInkMask",
    inkMask: "mc71d2a2ed_inkMask",
    headline: "mca0efd9d2_headlineH2 mc71d2a2ed_headline",
    bodyText: "mca0efd9d2_bodyText mc71d2a2ed_bodyText",
    errorContent: "mc71d2a2ed_errorContent",
    exit: "mc71d2a2ed_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    contentGutters: "mcee341e05_contentGutters",
    heroPanel: "mcee341e05_heroPanel",
    heroContainer: "mcee341e05_heroContainer",
    backgroundAccents: "mcee341e05_backgroundAccents",
    headline: "mca0efd9d2_headlineH2 mcfc263cc3_headline mcee341e05_headline",
    tagline: "mca0efd9d2_taglineFont mcee341e05_tagline",
    panelHeadlineContainer: "mcee341e05_panelHeadlineContainer",
    button: "mc05566e52_button mcee341e05_button",
    principles: "mca0efd9d2_bodyText mcee341e05_principles",
    principlesHeader: "mca0efd9d2_headlineH4 mcee341e05_principlesHeader",
    principlesContent: "mcee341e05_principlesContent",
    top: "mcee341e05_top",
    statements: "mcee341e05_statements",
    accordionButton: "mcee341e05_accordionButton",
    close: "mcee341e05_close",
    paragraph: "mca0efd9d2_bodyText mcee341e05_paragraph",
    messageBox: "mcee341e05_messageBox",
    accordionContent: "mca0efd9d2_bodyText mcee341e05_accordionContent",
    expanded: "mcee341e05_expanded",
    videoContainer: "mcee341e05_videoContainer",
    figureCaption: "mcee341e05_figureCaption"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    contentGutters: "mc2cf86643_contentGutters",
    timelinePanel: "mc2cf86643_timelinePanel",
    headline: "mca0efd9d2_headlineH2 mcfc263cc3_headline mc2cf86643_headline",
    tagline: "mca0efd9d2_taglineFont mc2cf86643_tagline",
    timelineNavWrapper: "mc2cf86643_timelineNavWrapper",
    yearlist: "mc2cf86643_yearlist",
    items: "mc2cf86643_items",
    timelineNavYear: "mc2cf86643_timelineNavYear",
    expanded: "mc2cf86643_expanded",
    timelineNavHeading: "mc2cf86643_timelineNavHeading",
    selected: "mc2cf86643_selected",
    timelineContentContainer: "mc2cf86643_timelineContentContainer",
    content: "mc2cf86643_content",
    media: "mc2cf86643_media",
    mediabg: "mc2cf86643_mediabg",
    date: "mca0efd9d2_timelineXL mc2cf86643_date",
    caption: "mca0efd9d2_timelineCaption mc2cf86643_caption",
    controls: "mc2cf86643_controls",
    button: "mc05566e52_button mc2cf86643_button"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mcb47257a0_container",
    panel: "mc86cc65a1_panel mcb47257a0_panel",
    headline: "mca0efd9d2_headlineH3 mcb47257a0_headline",
    textWrapper: "mcb47257a0_textWrapper",
    "pay-range": "pay-range",
    applyNow: "mcb47257a0_applyNow"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    tiles: "mc86cc65a1_grid mc6772a4dc_tiles",
    tile: "mc6772a4dc_tile",
    staticCaption: "mc6772a4dc_staticCaption",
    hoverCaption: "mc6772a4dc_hoverCaption",
    bgimg: "mc6772a4dc_bgimg",
    empty: "mc6772a4dc_empty",
    expanded: "mc6772a4dc_expanded",
    tile2x: "mc6772a4dc_tile2x",
    benefitsPanel: "mc6772a4dc_benefitsPanel",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline mc6772a4dc_headline",
    bodyText: "mca0efd9d2_bodyText mc369d696c_bodyText mc6772a4dc_bodyText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    contentGutters: "mc430db7c3_contentGutters",
    heroPanel: "mc430db7c3_heroPanel",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline mc430db7c3_headline",
    tagline: "mca0efd9d2_taglineFont mc430db7c3_tagline",
    panelHeadlineContainer: "mc430db7c3_panelHeadlineContainer",
    button: "mc05566e52_button mc430db7c3_button",
    bodyText: "mca0efd9d2_bodyText mc369d696c_bodyText mc430db7c3_bodyText",
    backgroundAccents1: "mc430db7c3_backgroundAccents1",
    backgroundAccents2: "mc430db7c3_backgroundAccents2"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    contentGutters: "mc6438cd64_contentGutters",
    lifePanel: "mc6438cd64_lifePanel",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline mc6438cd64_headline",
    tagline: "mca0efd9d2_taglineFont mc6438cd64_tagline",
    bodyText: "mca0efd9d2_bodyText mc369d696c_bodyText mc6438cd64_bodyText",
    carousel: "mc6438cd64_carousel",
    slide: "mc6438cd64_slide",
    controls: "mc6438cd64_controls",
    button: "mc05566e52_button mc6438cd64_button",
    slideNum: "mc6438cd64_slideNum",
    slideInfo: "mc6438cd64_slideInfo",
    slideCol: "mc6438cd64_slideCol",
    slideTitle: "mca0efd9d2_headlineH3 mc6438cd64_slideTitle",
    slideBody: "mc6438cd64_slideBody",
    legal: "mc6438cd64_legal"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    listingsPanel: "mc5fe12b60_listingsPanel",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline mc5fe12b60_headline",
    tagline: "mca0efd9d2_taglineFont mc5fe12b60_tagline",
    jobsList: "mc5fe12b60_jobsList",
    allJobs: "mc5fe12b60_allJobs",
    jobCat: "mca0efd9d2_headlineH4 mc5fe12b60_jobCat",
    listing: "mca0efd9d2_taglineFont mc5fe12b60_listing",
    general: "mca0efd9d2_headlineH4 mc5fe12b60_general",
    noJobRes: "mca0efd9d2_headlineH4 mc5fe12b60_noJobRes",
    intro: "mca0efd9d2_bodyText mc5fe12b60_intro"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    scamWarnPanel: "mcdf39ced5_scamWarnPanel",
    playAnim: "mcdf39ced5_playAnim",
    noInkMask: "mcdf39ced5_noInkMask",
    inkMask: "mcdf39ced5_inkMask",
    headline: "mca0efd9d2_headlineH2 mc369d696c_headline mcdf39ced5_headline"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    playAnim: "mc80ef6a7d_playAnim",
    noInkMask: "mc80ef6a7d_noInkMask",
    inkMask: "mc80ef6a7d_inkMask",
    banner: "mc80ef6a7d_banner",
    bannerContent: "mc80ef6a7d_bannerContent",
    informational: "mc80ef6a7d_informational",
    close: "mc80ef6a7d_close"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mc8a3049e8_container",
    panel: "mc86cc65a1_panel mc8a3049e8_panel",
    playAnim: "mc8a3049e8_playAnim",
    noInkMask: "mc8a3049e8_noInkMask",
    inkMask: "mc8a3049e8_inkMask",
    contactContainer: "mc8a3049e8_contactContainer",
    contactContent: "mc8a3049e8_contactContent",
    headline: "mca0efd9d2_headlineH2 mc8a3049e8_headline",
    heading: "mca0efd9d2_headlineH4 mc8a3049e8_heading",
    bodyText: "mca0efd9d2_bodyText mc8a3049e8_bodyText",
    contactLink: "mca0efd9d2_bodyText mc8a3049e8_contactLink",
    socialBar: "mc8a3049e8_socialBar",
    followUs: "mc8a3049e8_followUs",
    socialIcon: "mc8a3049e8_socialIcon",
    youtube: "mc8a3049e8_socialIcon mc8a3049e8_youtube",
    facebook: "mc8a3049e8_socialIcon mc8a3049e8_facebook",
    twitter: "mc8a3049e8_socialIcon mc8a3049e8_twitter",
    twitch: "mc8a3049e8_socialIcon mc8a3049e8_twitch",
    instagram: "mc8a3049e8_socialIcon mc8a3049e8_instagram",
    tumblr: "mc8a3049e8_socialIcon mc8a3049e8_tumblr",
    flickr: "mc8a3049e8_socialIcon mc8a3049e8_flickr",
    exit: "mc86cc65a1_exit mc8a3049e8_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc5840c833_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc5840c833_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc5840c833_foregroundLayer",
    logo: "mcfd584d06_logo mc5840c833_logo",
    quoteText: "mca0efd9d2_headlineH4 mc5840c833_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mce710e00f_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mce710e00f_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mce710e00f_foregroundLayer",
    logo: "mcfd584d06_logo mce710e00f_logo",
    gw1logo: "mce710e00f_gw1logo",
    quoteText: "mca0efd9d2_headlineH4 mce710e00f_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc8d853ede_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc8d853ede_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc8d853ede_foregroundLayer",
    logo: "mcfd584d06_logo mc8d853ede_logo",
    quoteText: "mca0efd9d2_headlineH4 mc8d853ede_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc7b712c54_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc7b712c54_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc7b712c54_foregroundLayer",
    logo: "mcfd584d06_logo mc7b712c54_logo",
    quoteText: "mca0efd9d2_headlineH4 mc7b712c54_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc687df63d_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc687df63d_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc687df63d_foregroundLayer",
    logo: "mcfd584d06_logo mcfd584d06_logoLight mc687df63d_logo",
    quoteText: "mca0efd9d2_headlineH4 mc687df63d_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc0c784f67_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc0c784f67_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc0c784f67_foregroundLayer",
    logo: "mcfd584d06_logo mc0c784f67_logo",
    quoteText: "mca0efd9d2_headlineH4 mc0c784f67_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mc63719d2e_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mc63719d2e_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mc63719d2e_foregroundLayer",
    logo: "mcfd584d06_logo mcfd584d06_logoLight mc63719d2e_logo",
    quoteText: "mca0efd9d2_headlineH4 mc63719d2e_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    backgroundLayer: "mcfd584d06_backgroundLayer mca9c4756c_backgroundLayer",
    midgroundLayer: "mcfd584d06_midgroundLayer mca9c4756c_midgroundLayer",
    foregroundLayer: "mcfd584d06_foregroundLayer mca9c4756c_foregroundLayer",
    logo: "mcfd584d06_logo mcfd584d06_logoDark mca9c4756c_logo",
    quoteText: "mca0efd9d2_headlineH4 mca9c4756c_quoteText"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    panelHeadlineContainer: "mce9070436_panelHeadlineContainer mc7ddf2549_panelHeadlineContainer",
    subheader: "mc7ddf2549_subheader",
    tagline: "mca0efd9d2_taglineFont mc7ddf2549_tagline",
    panelImageContainer: "mce9070436_panelImageContainer mc7ddf2549_panelImageContainer",
    intro: "mc7ddf2549_intro",
    ctaContainer: "mce9070436_ctaContainer mc7ddf2549_ctaContainer",
    showAnims: "mc7ddf2549_showAnims",
    headerText: "mca0efd9d2_headlineH1 mce9070436_headerText mc7ddf2549_headerText",
    backgroundlayer: "mc7ddf2549_backgroundlayer",
    birdslayer: "mc7ddf2549_birdslayer",
    headlayer: "mc7ddf2549_headlayer",
    bodylayer: "mc7ddf2549_bodylayer",
    lowerleglayer: "mc7ddf2549_lowerleglayer",
    baselayer: "mc7ddf2549_baselayer",
    radialGlow: "mc7ddf2549_radialGlow",
    maskLayer: "mc7ddf2549_maskLayer",
    particles: "mc86cc65a1_particles mc7ddf2549_particles"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    panelHeadlineContainer: "mce9070436_panelHeadlineContainer mc596ecf9a_panelHeadlineContainer",
    button: "mc596ecf9a_button",
    showAnims: "mc596ecf9a_showAnims",
    tagline: "mca0efd9d2_taglineFont mc596ecf9a_tagline",
    headerText: "mca0efd9d2_headlineH1 mce9070436_headerText mc596ecf9a_headerText",
    ctaContainer: "mce9070436_ctaContainer mc596ecf9a_ctaContainer",
    panelImageContainer: "mce9070436_panelImageContainer mc596ecf9a_panelImageContainer",
    subheader: "mca0efd9d2_bodyText mce9070436_subheader mc596ecf9a_subheader",
    imageOverlay: "mc596ecf9a_imageOverlay",
    maskLayer: "mc596ecf9a_maskLayer",
    fadeLayer: "mc596ecf9a_fadeLayer",
    headlineH1: "mc596ecf9a_headlineH1",
    headerOverlay: "mc596ecf9a_headerOverlay",
    parallax1: "mc596ecf9a_parallax1",
    parallax2: "mc596ecf9a_parallax2",
    parallax3: "mc596ecf9a_parallax3",
    parallax4: "mc596ecf9a_parallax4",
    particles: "mc86cc65a1_particles mc596ecf9a_particles"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    panelHeadlineContainer: "mce9070436_panelHeadlineContainer mccb50df05_panelHeadlineContainer",
    button: "mccb50df05_button",
    showAnims: "mccb50df05_showAnims",
    tagline: "mca0efd9d2_taglineFont mccb50df05_tagline",
    headerText: "mca0efd9d2_headlineH1 mce9070436_headerText mccb50df05_headerText",
    ctaContainer: "mce9070436_ctaContainer mccb50df05_ctaContainer",
    subheader: "mccb50df05_subheader",
    panelImageContainer: "mce9070436_panelImageContainer mccb50df05_panelImageContainer",
    foregroundImage: "mccb50df05_foregroundImage",
    backgroundImage: "mccb50df05_backgroundImage",
    wipeout: "mccb50df05_wipeout",
    gameTitle: "mccb50df05_gameTitle",
    wipein: "mccb50df05_wipein",
    controlsContainer: "mccb50df05_controlsContainer",
    controls: "mccb50df05_controls",
    prevBtn: "mccb50df05_prevBtn",
    nextBtn: "mccb50df05_nextBtn"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    container: "mc86cc65a1_container mc61738ab6_container",
    playAnim: "mc61738ab6_playAnim",
    noInkMask: "mc61738ab6_noInkMask",
    inkMask: "mc61738ab6_inkMask",
    legalContainer: "mc61738ab6_legalContainer",
    legalContainerPage: "mc61738ab6_legalContainer mc61738ab6_legalContainerPage",
    legalContent: "mc61738ab6_legalContent",
    backLink: "mc61738ab6_backLink",
    headline: "mca0efd9d2_headlineH2 mc61738ab6_headline",
    bodyText: "mca0efd9d2_bodyText mc61738ab6_bodyText",
    legalBody: "mc61738ab6_legalBody",
    border: "border",
    nav: "mca0efd9d2_bodyText mc61738ab6_bodyText mc61738ab6_nav",
    exit: "mc86cc65a1_exit mc61738ab6_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    button: "mc05566e52_button",
    scrollButton: "mc05566e52_button mc05566e52_scrollButton",
    mediaButton: "mc05566e52_mediaButton"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    footerNav: "mca0efd9d2_headlineH3 mca0efd9d2_headlineH4 mc1a503fc7_footerNav",
    bg: "mc1a503fc7_bg"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    primaryNavContainer: "mc8166557b_primaryNavContainer",
    navChildBar: "mc8166557b_navChildBar",
    mainNavLi: "mc8166557b_mainNavLi",
    supportInfo: "mc8166557b_supportInfo",
    primaryNav: "mc8166557b_primaryNav",
    navChild: "mc8166557b_navChild",
    ext: "mc8166557b_ext",
    logo: "mc8166557b_logo",
    langSelectBar: "mc8166557b_langSelectBar",
    currentLang: "mc8166557b_currentLang",
    mobileMenuBtn: "mc8166557b_mobileMenuBtn",
    menuOpen: "mc8166557b_menuOpen",
    btnOpen: "mc8166557b_btnOpen"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    preloader: "mcef995ca3_preloader",
    preloaded: "mcef995ca3_preloaded",
    preloadLogo: "mcef995ca3_preloadLogo",
    loader: "mcef995ca3_loader"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    masklayer: "mc5c95c941_masklayer",
    maskwipe: "mc5c95c941_maskwipe",
    noMaskWipe: "mc5c95c941_noMaskWipe"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    btnSize: "35%",
    video: "mc3b303a85_video",
    button: "mc3b303a85_button",
    playBtn: "mc3b303a85_playBtn",
    playBtnAbs: "mc3b303a85_playBtn mc3b303a85_playBtnAbs",
    playBtnFs: "mc3b303a85_playBtn mc3b303a85_playBtnFs",
    playBtnFsAbs: "mc3b303a85_playBtn mc3b303a85_playBtnFs mc3b303a85_playBtnFsAbs",
    flood: "mc3b303a85_flood",
    videoStacked: "mc3b303a85_videoStacked"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    transitionProps: "all cubic-bezier(0.34, 0, 0.23, 1) 0.3s",
    contentGutters: "0 4.5vw",
    contentGuttersV: "4.5vw 0",
    leftGutter: "4.5vw",
    navMarginLg: "85px",
    navMarginSm: "50px",
    mount: "mc86cc65a1_mount",
    container: "mc86cc65a1_container",
    panel: "mc86cc65a1_panel",
    grid: "mc86cc65a1_grid",
    particles: "mc86cc65a1_particles",
    exit: "mc86cc65a1_exit"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    lightboxButton: "mcef14bd05_lightboxButton",
    overlay: "mcef14bd05_overlay",
    overlayHidden: "mcef14bd05_overlay mcef14bd05_overlayHidden",
    contentControls: "mcef14bd05_contentControls",
    control: "mcef14bd05_control",
    close: "mcef14bd05_control mcef14bd05_close",
    content: "mcef14bd05_content",
    preload: "mcef14bd05_preload"
  }
}, function(e, a, t) {
  "use strict";
  a.a = {
    boxed: "mc941a22b2_boxed",
    loading: "mc941a22b2_loading"
  }
}, function(e, a) {
  var t, n, o = e.exports = {};

  function i() {
    throw new Error("setTimeout has not been defined")
  }

  function r() {
    throw new Error("clearTimeout has not been defined")
  }

  function s(e) {
    if (t === setTimeout) return setTimeout(e, 0);
    if ((t === i || !t) && setTimeout) return t = setTimeout, setTimeout(e, 0);
    try {
      return t(e, 0)
    } catch (a) {
      try {
        return t.call(null, e, 0)
      } catch (a) {
        return t.call(this, e, 0)
      }
    }
  }! function() {
    try {
      t = "function" == typeof setTimeout ? setTimeout : i
    } catch (e) {
      t = i
    }
    try {
      n = "function" == typeof clearTimeout ? clearTimeout : r
    } catch (e) {
      n = r
    }
  }();
  var c, l = [],
    d = !1,
    u = -1;

  function m() {
    d && c && (d = !1, c.length ? l = c.concat(l) : u = -1, l.length && g())
  }

  function g() {
    if (!d) {
      var e = s(m);
      d = !0;
      for (var a = l.length; a;) {
        for (c = l, l = []; ++u < a;) c && c[u].run();
        u = -1, a = l.length
      }
      c = null, d = !1,
        function(e) {
          if (n === clearTimeout) return clearTimeout(e);
          if ((n === r || !n) && clearTimeout) return n = clearTimeout, clearTimeout(e);
          try {
            n(e)
          } catch (a) {
            try {
              return n.call(null, e)
            } catch (a) {
              return n.call(this, e)
            }
          }
        }(e)
    }
  }

  function p(e, a) {
    this.fun = e, this.array = a
  }

  function f() {}
  o.nextTick = function(e) {
    var a = new Array(arguments.length - 1);
    if (arguments.length > 1)
      for (var t = 1; t < arguments.length; t++) a[t - 1] = arguments[t];
    l.push(new p(e, a)), 1 !== l.length || d || s(g)
  }, p.prototype.run = function() {
    this.fun.apply(null, this.array)
  }, o.title = "browser", o.browser = !0, o.env = {}, o.argv = [], o.version = "", o.versions = {}, o.on = f, o.addListener = f, o.once = f, o.off = f, o.removeListener = f, o.removeAllListeners = f, o.emit = f, o.prependListener = f, o.prependOnceListener = f, o.listeners = function(e) {
    return []
  }, o.binding = function(e) {
    throw new Error("process.binding is not supported")
  }, o.cwd = function() {
    return "/"
  }, o.chdir = function(e) {
    throw new Error("process.chdir is not supported")
  }, o.umask = function() {
    return 0
  }
}, function(e, a, t) {
  "use strict";
  Object.defineProperty(a, "__esModule", {
      value: !0
    }),
    function(e) {
      var a = t(0),
        n = t.n(a),
        o = t(9),
        i = t.n(o),
        r = t(40),
        s = t.n(r),
        c = (t(17), t(16), t(15), t(38)),
        l = t(1),
        d = t(36),
        u = t(31),
        m = t(32),
        g = t(33),
        p = t(35),
        f = t(34),
        h = t(37),
        b = t(30),
        w = t(39);
      const y = t.i(c.a)((() => {
        Object.assign(l.a, window.appState, {
          mobileSize: window.matchMedia("(min-width: 768px)").matches,
          tabletSize: window.matchMedia("(min-width: 1082px)").matches,
          desktopSize: window.matchMedia("(min-width: 1200px)").matches,
          oriLandscape: window.matchMedia("(orientation: landscape)").matches,
          oriPortrait: window.matchMedia("(orientation: portrait)").matches
        }), n.a.redraw()
      }), 500);

      function v(e) {
        return {
          onmatch({
            lang: a,
            path: t
          }, o, i) {
            const r = !l.a.l10n.langs.includes(a),
              s = "legal" === o.split("/")[2] && t && !l.a.legal[t];
            return (r || s) && (l.a.code = 404), "en" !== a && o.includes("/legal/event-terms-of-attendance") && n.a.route.set(`/${a}/legal`), 404 === l.a.code ? b.a : e
          },
          render({
            tag: e
          }) {
            const a = l.a.code ? `${l.a.i18n.errors.fourohfour.errorTitle} | ` : "";
            return document.title = `${a}ArenaNet`, delete l.a.code, n()(e)
          }
        }
      }
      Object.assign(l.a, window.appState, {
          i18n: window.strings,
          stickyCheck: (!Boolean(window.MSInputMethodContext) || !Boolean(document.documentMode)) && CSS.supports("(position: sticky)"),
          maskCheck: (!Boolean(window.MSInputMethodContext) || !Boolean(document.documentMode)) && (CSS.supports("(-webkit-mask-image: url())") || CSS.supports(!CSS.supports("(-ms-ime-align: auto)"))),
          safariCheck: navigator.vendor && navigator.vendor.indexOf("Apple") > -1 && navigator.userAgent && -1 === navigator.userAgent.indexOf("FxiOS"),
          mobileSize: window.matchMedia("(min-width: 768px)").matches,
          tabletSize: window.matchMedia("(min-width: 1082px)").matches,
          desktopSize: window.matchMedia("(min-width: 1200px)").matches,
          oriLandscape: window.matchMedia("(orientation: landscape)").matches,
          oriPortrait: window.matchMedia("(orientation: portrait)").matches
        }), l.a.mq = {
          sm: "32em",
          md: "48em",
          lg: "67.625em",
          xl: "1200px",
          minSm: "(min-width: 32em)",
          minMd: "(min-width: 48em)",
          minLg: "(min-width: lg)",
          minXL: "(min-width: xl)",
          p: "(orientation: portrait)",
          l: "(orientation: landscape)",
          dpi: "(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)"
        }, n.a.route.prefix(""), n.a.route(document.getElementById("mount"), "/", {
          "/:lang": v(d.a),
          "/:lang/careers": v(m.a),
          "/:lang/careers/job/:id": v(g.a),
          "/:lang/about": v(u.a),
          "/:lang/games": v(p.a),
          "/:lang/contact": v(f.a),
          "/:lang/legal": v(h.a),
          "/:lang/legal/:path": v(h.a),
          "/:lang/vendor-form": v(w.a),
          "/:lang/:path...": b.a
        }), window.addEventListener("resize", y),
        function() {
          const a = [];
          "IntersectionObserver" in e && "IntersectionObserverEntry" in e && "intersectionRatio" in IntersectionObserverEntry.prototype || a.push(s.a), Promise.all(a)
        }(), i.a.setup(null, 120)
    }.call(a, t(29))
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(43),
    s = t(14),
    c = t(2);
  let l;
  a.a = {
    id: "hero",
    name: "hero",
    oninit: () => {
      i.a.about = {}, l = i.a.i18n.about.panels.hero
    },
    oncreate: e => {
      i.a.about = e.dom, e.state.accordion = !1
    },
    view: () => o()("div", {
      class: r.a.heroPanel
    }, o()("section", {
      class: r.a.heroContainer
    }, o()("div", {
      class: r.a.panelHeadlineContainer
    }, o()("div", {
      class: r.a.tagline
    }, l.tagline), o()("h1", {
      class: r.a.headline,
      id: t.i(c.a)(l.header)
    }, o.a.trust(l.header)), o()("p", {
      class: r.a.paragraph
    }, o.a.trust(l.body)), o()("div", {
      class: r.a.videoContainer
    }, o()(s.a, {
      label: i.a.i18n.misc.buttons.labels.play,
      ytId: l.ytId
    }, o()("img", {
      src: "https://2arenanet2.staticwars.com/img/pages/about/culture_vid_thumb.55df33d1.jpg"
    })))), i.a.desktopSize && i.a.maskCheck ? o()("div", {
      class: r.a.backgroundAccents
    }) : null), o()("section", {
      class: r.a.principles
    }, o()("div", {
      class: r.a.principlesContent
    }, o()("div", {
      class: r.a.top
    }, Object.keys(l.principle).map((e => o()("div", o()("h4", {
      class: r.a.principlesHeader
    }, l.principle[e].heading), o()("p", l.principle[e].body))))), o()("div", {
      class: r.a.statements
    }, ["culture", "dei", "ai"].map((e => [o()("h4", {
      class: r.a.principlesHeader,
      id: l[`${e}StatementSlug`]
    }, l[`${e}StatementHeader`]), Object.values(l[`${e}Statement`]).map((e => o()("p", e)))]))))))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(27),
    r = (t.n(i), t(1)),
    s = t(44),
    c = t(78);
  let l, d;
  a.a = {
    id: "timeline",
    name: "timeline",
    oninit: e => {
      d = r.a.l10n.lang, l = r.a.i18n.about.panels.timeline;
      const a = t.i(c.a)({
        items: l.items,
        lang: d
      });
      e.state.timelineService = t.i(i.interpret)(a), e.state.timelineService.subscribe((({
        context: a
      }) => {
        e.state.timeline = a
      })), e.state.timelineService.start()
    },
    onremove(e) {
      e.state.timelineService.stop()
    },
    view(e) {
      const {
        timeline: a,
        timelineService: t
      } = e.state;
      return o()("div", {
        class: s.a.timelinePanel
      }, o()("div", {
        class: s.a.tagline
      }, l.subheader), o()("h1", {
        class: s.a.headline,
        id: l.slug
      }, o.a.trust(l.header)), o()("nav", {
        class: s.a.timelineNavWrapper
      }, o()("ul", {
        class: s.a.yearlist,
        style: {
          transform: r.a.desktopSize ? "none" : `translateX(-${75*a.yearIdx}px)`
        }
      }, a.items.map(((e, n, i) => 0 === n || e.year !== i[n - 1].year ? o()("li", {
        onclick() {
          t.send({
            type: "SELECT",
            idx: n
          })
        },
        role: "button",
        class: [s.a.timelineNavYear, a.currItem.year === e.year ? s.a.expanded : ""].join(" ")
      }, o()("span", e.year), o()("ul", {
        class: s.a.items
      }, a.items.map(((n, i) => e.year === n.year ? o()("li", {
        onclick(e) {
          e.stopPropagation(), t.send({
            type: "SELECT",
            idx: i
          })
        },
        role: "button",
        class: a.currItem === n ? s.a.selected : ""
      }, new Date(n.date).toLocaleString(d, {
        month: "long"
      })) : null)))) : null)))), o()("div", {
        class: s.a.timelineContentContainer
      }, o()("div", {
        class: s.a.content
      }, o()("h3", {
        class: s.a.date
      }, new Date(a.currItem.date).toLocaleString(d, {
        month: "short"
      }), r.a.desktopSize ? o()("br") : " ", new Date(a.currItem.date).toLocaleString(d, {
        year: "numeric"
      })), o()("p", {
        class: s.a.caption
      }, o.a.trust(a.currItem.caption))), o()("div", {
        class: s.a.mediabg
      }, o()("img", {
        class: s.a.media,
        alt: a.currItem.caption,
        src: a.currItem.media
      }))), o()("div", {
        class: s.a.controls
      }, o()("button", {
        onclick: () => {
          t.send({
            type: "DECREMENT"
          })
        },
        class: s.a.button,
        "aria-label": r.a.i18n.misc.buttons.labels.prev
      }, o()("div", {
        "data-icon": "arrowLeft"
      })), o()("button", {
        onclick: () => {
          t.send({
            type: "INCREMENT"
          })
        },
        class: s.a.button,
        "aria-label": r.a.i18n.misc.buttons.labels.next
      }, o()("div", {
        "data-icon": "arrowRight"
      }))))
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = function({
    items: e
  }) {
    const a = [...new Set(e.map((e => e.year)))];
    return t.i(n.createMachine)({
      id: "timeline",
      initial: "idle",
      context: {
        items: e,
        itemIdx: 0,
        currItem: e[0],
        years: a,
        yearIdx: 0,
        currYear: a[0]
      },
      states: {
        idle: {
          on: {
            SELECT: {
              target: "idle",
              actions: ["select", "setYear"]
            },
            INCREMENT: {
              target: "idle",
              actions: ["increment", "setYear"]
            },
            DECREMENT: {
              target: "idle",
              actions: ["decrement", "setYear"]
            }
          }
        }
      }
    }, {
      actions: {
        select: t.i(n.assign)(((e, {
          idx: a
        }) => (e.itemIdx = a, e.currItem = e.items[e.itemIdx], e))),
        increment: t.i(n.assign)((e => (e.itemIdx = e.itemIdx + 1 === e.items.length ? 0 : e.itemIdx + 1, e.currItem = e.items[e.itemIdx], e))),
        decrement: t.i(n.assign)((e => (e.itemIdx = e.itemIdx - 1 < 0 ? e.items.length - 1 : e.itemIdx - 1, e.currItem = e.items[e.itemIdx], e))),
        setYear: t.i(n.assign)((e => (e.currYear = e.currItem.year, e.yearIdx = e.years.indexOf(e.currYear), e)))
      }
    })
  };
  var n = t(27);
  t.n(n)
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(46),
    s = t(14);
  let c, l, d;
  a.a = {
    id: "benefits",
    name: "benefits",
    oninit: () => {
      i.a.careers = {}, c = i.a.i18n.careers.panels.benefits, l = c.tiles, d = Object.entries(l).filter((([e, a]) => a))
    },
    oncreate: e => {
      i.a.careers = e.dom
    },
    view: e => o()("div", {
      class: r.a.benefitsPanel
    }, o()("h1", {
      class: r.a.headline,
      id: c.slug
    }, c.header), o()("p", {
      class: r.a.bodyText
    }, c.intro), o()("div", {
      class: r.a.tiles
    }, d.map((([a, t]) => o()("figure", {
      oninit: () => {
        e.state.benefitsNodes = {}
      },
      oncreate: t => {
        e.state.benefitsNodes[a] = t.dom
      },
      onclick: () => {
        Object.keys(e.state.benefitsNodes).forEach((a => {
          e.state.benefitsNodes[a].classList.remove(r.a.expanded)
        })), e.state.benefitsNodes[a].classList.add(r.a.expanded)
      },
      class: [r.a.tile, r.a[t.size ? `tile${t.size}` : ""]].join(" ")
    }, o()("figcaption", {
      style: {
        "background-image": t.bgimage ? `url(${t.bgimage})` : "none"
      },
      class: [r.a.staticCaption, r.a[t.bgimage ? "bgimg" : ""], r.a[t.ytid || t.title ? "" : "empty"]].join(" ")
    }, t.size ? null : o()("p", `${t.title}`), t.ytId ? o()(s.a, {
      label: i.a.i18n.misc.buttons.labels.play,
      ytId: i.a.i18n.about.panels.hero.ytId
    }, o()("div")) : null), t.content ? o()("figcaption", {
      class: r.a.hoverCaption
    }, o()("p", t.title), o()("ul", o.a.trust(t.content))) : null)))))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(47),
    s = (t(14), t(2));
  let c;
  a.a = {
    id: "hero",
    name: "hero",
    oninit: () => {
      i.a.careers = {}, c = i.a.i18n.careers.panels.hero
    },
    oncreate: e => {
      i.a.careers = e.dom
    },
    view: () => [o()("div", {
      class: r.a.heroPanel
    }, o()("div", {
      class: r.a.panelHeadlineContainer
    }, o()("div", {
      class: r.a.tagline
    }, c.tagline), o()("h1", {
      class: r.a.headline,
      id: t.i(s.a)(c.header)
    }, c.header), o()("p", {
      class: r.a.bodyText
    }, c.intro), o()("div", {
      class: r.a.imgVideo
    }, o()("img", {
      src: "https://2arenanet2.staticwars.com/img/pages/careers/Arenanet-Group.1f68076e.jpg",
      style: {
        "max-width": "550px"
      }
    })))), i.a.desktopSize ? o()("div", {
      class: r.a.backgroundAccents1
    }) : null, i.a.desktopSize ? o()("div", {
      class: r.a.backgroundAccents2
    }) : null]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(48);
  const s = {
    fmlaen: "https://cdn.arena.net/arenanet/fmlaen.pdf",
    eeopost: "https://cdn.arena.net/arenanet/eeopost.pdf",
    eppac: "https://cdn.arena.net/arenanet/eppac.pdf",
    rtw: "https://cdn.arena.net/arenanet/Right_to_Work.pdf",
    pev: "https://cdn.arena.net/arenanet/E-Verify_Participation_Poster_ES.pdf"
  };
  let c;

  function l(e) {
    return Object.entries(e).map((([e, {
      label: a
    }], t) => [t ? ", " : "", o()("a", {
      href: s[e]
    }, a)]))
  }
  a.a = {
    id: "life",
    name: "life",
    oninit: e => {
      i.a.careers = {}, c = i.a.i18n.careers.panels.life, e.state.keys = Object.keys(c.carousel), e.state.currentSlide = 1
    },
    oncreate: e => {
      i.a.careers = e.dom
    },
    view: e => o()("div", {
      class: [r.a.lifePanel, r.a.contentGutters].join(" ")
    }, o()("div", {
      class: r.a.tagline
    }, c.tagline), o()("h1", {
      class: r.a.headline,
      id: c.slug
    }, c.header), o()("p", {
      class: r.a.bodyText
    }, c.intro), o()("div", {
      class: r.a.carousel
    }, o()("div", {
      class: r.a.slideInfo
    }, o()("div", {
      class: r.a.slideCol
    }, o()("img", {
      class: r.a.slide,
      alt: c.carousel[e.state.currentSlide - 1].title,
      src: c.carousel[e.state.currentSlide - 1].img
    }), o()("div", {
      class: r.a.controls
    }, o()("button", {
      onclick: () => {
        ! function(e) {
          e.state.currentSlide = e.state.currentSlide % e.state.keys.length == 1 ? e.state.keys.length : e.state.currentSlide - 1
        }(e)
      },
      class: r.a.button,
      "aria-label": i.a.i18n.misc.buttons.labels.prev
    }, o()("div", {
      "data-icon": "arrowLeft"
    })), o()("div", {
      class: r.a.slideNum
    }, `${e.state.currentSlide} / ${e.state.keys.length}`), o()("button", {
      onclick: () => {
        ! function(e) {
          e.state.currentSlide = e.state.currentSlide % e.state.keys.length + 1
        }(e)
      },
      class: r.a.button,
      "aria-label": i.a.i18n.misc.buttons.labels.next
    }, o()("div", {
      "data-icon": "arrowRight"
    })))), o()("div", {
      class: r.a.slideCol
    }, o()("h3", {
      class: r.a.slideTitle
    }, o.a.trust(c.carousel[e.state.currentSlide - 1].title)), o()("p", {
      class: r.a.slideBody
    }, c.carousel[e.state.currentSlide - 1].body)))), o()("div", {
      class: r.a.legal
    }, o()("p", o.a.trust(c.transparency)), o()("p", c.lawsDesc, l(c.laws)), o()("p", c.everifyDesc, l(c.everify))))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(49),
    s = t(26),
    c = t.n(s),
    l = t(22),
    d = t(6);
  let u, m, g, p, f;
  const h = {
    view: ({
      attrs: e
    }) => e.jobsError ? o()("a", {
      class: r.a.allJobs,
      href: e.boardUrl
    }, "See all open positions") : "Loading..."
  };
  a.a = {
    id: "listings",
    name: "listings",
    oninit: () => {
      i.a.careers = {}, u = i.a.i18n.careers.panels.listings, p = !0, o.a.request(`${i.a.jobs.url}?content=true`).then((e => {
        let a;
        a = i.a.jobs.useAshby ? t.i(l.a)({
          body: e
        }) : t.i(l.b)({
          body: e
        }), ({
          jobsByDept: m,
          general: g
        } = c()(a, i.a.jobs.departments))
      })).catch((e => {
        f = !0
      }))
    },
    oncreate: e => {
      i.a.careers = e.dom
    },
    view() {
      const e = i.a.l10n.lang;
      return o()("div", {
        class: r.a.listingsPanel
      }, o()("div", {
        class: r.a.tagline
      }, u.tagline), o()("h1", {
        class: r.a.headline,
        id: u.slug
      }, u.header), o()("p", {
        class: r.a.intro
      }, u.intro), o()("ul", {
        class: r.a.jobsList
      }, m ? [Object.entries(m).map((([a, n]) => o()("li", {
        class: r.a.jobCat
      }, a, o()("ul", {
        class: r.a.listing
      }, n.map((({
        title: a,
        href: n,
        id: i
      }) => o()("li", o()("a", {
        href: `/${e}/careers/job/${i}`,
        oncreate: o.a.route.link,
        onupdate: o.a.route.link,
        "data-testid": "job-listing",
        onclick() {
          t.i(d.a)("click", a, 1, "Jobs Listing")
        }
      }, a)))))))), g ? o()("a", {
        href: g.href,
        class: r.a.general
      }, g.title) : null] : o()("div", {
        class: r.a.noJobRes
      }, p ? o()(h, {
        jobsError: f,
        boardUrl: i.a.jobs.boardUrl,
        "data-testid": "careers-error"
      }) : "Whoops, looks like something went wrong.")))
    }
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(50),
    s = t(2);
  let c;
  a.a = {
    oninit: () => {
      c = i.a.i18n.careers.panels.recruitmentScameWarning
    },
    view: () => o()("div", {
      class: r.a.scamWarnPanel
    }, o()("h1", {
      class: r.a.headline,
      id: t.i(s.a)(c.header)
    }, c.header), o()("p", {
      class: r.a.bodyText
    }, c.p1), o()("p", {
      class: r.a.bodyText
    }, c.p2), o()("ul", o()("li", o.a.trust(c.li1)), o()("li", c.li2), o()("li", c.li3), o()("li", c.li4)), o()("p", {
      class: r.a.bodyText
    }, o.a.trust(c.p3)))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(53),
    s = t(3),
    c = t(2);
  let l;
  a.a = {
    id: "eod",
    name: "eod",
    oninit() {
      i.a.games = {}, l = i.a.i18n.games.panels.eod
    },
    oncreate(e) {
      i.a.games = e.dom
    },
    view: () => [o()("div", {
      class: r.a.foregroundLayer
    }, o()("h1", {
      class: r.a.logo,
      id: t.i(c.a)(l.title)
    }, l.title), o()("p", l.tagline), o()(s.a, {
      href: l.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, l.ctaText)), i.a.desktopSize ? o()("div", {
      class: r.a.midgroundLayer
    }) : null, o()("div", {
      class: r.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(54),
    s = t(3);
  let c;
  a.a = {
    id: "gw1",
    name: "gw1",
    oninit: () => {
      c = i.a.i18n.games.panels.gw1
    },
    view: () => [o()("div", {
      class: r.a.foregroundLayer
    }, o()("h1", {
      class: r.a.logo,
      id: "Guild\xa0Wars"
    }, o()("figure", {
      class: r.a.gw1logo,
      style: {
        "background-image": "url(https://2arenanet2.staticwars.com/img/icons/guild-wars-logo.f416802e.png)"
      }
    }), o()("figure", {
      class: r.a.gw1logo,
      style: {
        "background-image": "url(https://2arenanet2.staticwars.com/img/icons/gw-nightfall-logo.2cd5d948.png)"
      }
    }), o()("figure", {
      class: r.a.gw1logo,
      style: {
        "background-image": "url(https://2arenanet2.staticwars.com/img/icons/gw-eotn-logo.23a6996e.png)"
      }
    }), o()("figure", {
      class: r.a.gw1logo,
      style: {
        "background-image": "url(https://2arenanet2.staticwars.com/img/icons/gw-factions-logo.47d7dd77.png)"
      }
    })), o()("p", c.tagline), o()(s.a, {
      href: c.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, c.ctaText)), i.a.desktopSize ? o()("div", {
      class: r.a.midgroundLayer
    }) : null, o()("div", {
      class: r.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(55),
    s = t(3),
    c = t(2);
  let l;
  a.a = {
    id: "gw2",
    name: "gw2",
    oninit: () => {
      l = i.a.i18n.games.panels.gw2
    },
    view: () => [o()("div", {
      class: r.a.foregroundLayer
    }, o()("h1", {
      class: r.a.logo,
      id: t.i(c.a)(l.title)
    }, l.title), o()("p", l.tagline), o()(s.a, {
      href: l.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, l.ctaText)), i.a.desktopSize ? o()("div", {
      class: r.a.midgroundLayer
    }) : null, o()("div", {
      class: r.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(56),
    s = t(3),
    c = t(2);
  let l;
  a.a = {
    id: "hot",
    name: "hot",
    oninit: () => {
      l = i.a.i18n.games.panels.hot
    },
    view: () => [o()("div", {
      class: r.a.foregroundLayer
    }, o()("h1", {
      class: r.a.logo,
      id: t.i(c.a)(l.title)
    }, l.title), o()("p", l.tagline), o()(s.a, {
      href: l.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, l.ctaText)), i.a.desktopSize ? o()("div", {
      class: r.a.midgroundLayer
    }) : null, o()("div", {
      class: r.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(3),
    r = t(2),
    s = t(1),
    c = t(57),
    l = t(12);
  let d;
  a.a = {
    id: "jw",
    name: "jw",
    oninit() {
      s.a.games = {}, d = s.a.i18n.games.panels.jw
    },
    oncreate(e) {
      s.a.games = e.dom
    },
    view: () => [o()("div", {
      class: c.a.foregroundLayer
    }, o()("h1", {
      class: c.a.logo,
      id: t.i(r.a)(d.title)
    }, d.title), o()("p", {
      class: l.a.taglineLight
    }, d.tagline), o()(i.a, {
      href: d.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, d.ctaText)), s.a.desktopSize ? o()("div", {
      class: c.a.midgroundLayer
    }) : null, o()("div", {
      class: c.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(58),
    s = t(3),
    c = t(2);
  let l;
  a.a = {
    id: "pof",
    name: "pof",
    oninit: () => {
      i.a.games = {}, l = i.a.i18n.games.panels.pof
    },
    oncreate: e => {
      i.a.games = e.dom
    },
    view: () => [o()("div", {
      class: r.a.foregroundLayer
    }, o()("h1", {
      class: r.a.logo,
      id: t.i(c.a)(l.title)
    }, l.title), o()("p", l.tagline), o()(s.a, {
      href: l.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, l.ctaText)), i.a.desktopSize ? o()("div", {
      class: r.a.midgroundLayer
    }) : null, o()("div", {
      class: r.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(3),
    r = t(2),
    s = t(1),
    c = t(59),
    l = t(12);
  let d;
  a.a = {
    id: "soto",
    name: "soto",
    oninit() {
      s.a.games = {}, d = s.a.i18n.games.panels.soto
    },
    oncreate(e) {
      s.a.games = e.dom
    },
    view: () => [o()("div", {
      class: c.a.foregroundLayer
    }, o()("h1", {
      class: c.a.logo,
      id: t.i(r.a)(d.title)
    }, d.title), o()("p", {
      class: l.a.taglineDark
    }, d.tagline), o()(i.a, {
      href: d.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, d.ctaText)), s.a.desktopSize ? o()("div", {
      class: c.a.midgroundLayer
    }) : null, o()("div", {
      class: c.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(3),
    r = t(2),
    s = t(1),
    c = t(60),
    l = t(12);
  let d;
  a.a = {
    id: "voe",
    name: "voe",
    oninit() {
      s.a.games = {}, d = s.a.i18n.games.panels.voe
    },
    oncreate(e) {
      s.a.games = e.dom
    },
    view: () => [o()("div", {
      class: c.a.foregroundLayer
    }, o()("h1", {
      class: c.a.logo,
      id: t.i(r.a)(d.title)
    }, d.title), o()("p", {
      class: l.a.taglineDark
    }, d.tagline), o()(i.a, {
      href: d.ctaUrl,
      target: "_blank",
      rel: "noreferrer"
    }, d.ctaText)), s.a.desktopSize ? o()("div", {
      class: c.a.midgroundLayer
    }) : null, o()("div", {
      class: c.a.backgroundLayer
    })]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(61),
    s = t(3);
  const c = ["bodylayer", "headlayer", "baselayer", "lowerleglayer", "radialGlow", i.a.maskCheck ? null : "birdslayer"];
  let l, d;
  a.a = {
    id: "about",
    name: "about",
    oninit: () => {
      l = i.a.i18n.home.panels.about, d = l.header.split(". ")
    },
    view: () => [o()("div", {
      class: r.a.panelImageContainer
    }, o()("div", {
      class: r.a.backgroundlayer
    }), i.a.desktopSize ? c.map((e => o()("div", {
      class: r.a[e]
    }))) : null), o()("div", {
      oncreate: e => {
        e.dom.addEventListener("animationend", (() => {
          e.dom.parentNode.removeChild(e.dom)
        }))
      },
      class: r.a.maskLayer
    }), o()("div", {
      class: [r.a.panelHeadlineContainer, i.a.safariCheck ? null : r.a.showAnims].join(" ")
    }, o()("div", {
      class: [i.a.stickyCheck ? "" : r.a.headerFix, r.a.headerText].join(" ")
    }, o()("a", {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/about`,
      "aria-hidden": "true",
      role: "presentation",
      "data-ga-event": "",
      "data-ga-label": "about button",
      "data-ga-category": "Home Page"
    }, o()("h1", {
      "data-text1": `${d[0]}.`
    }, `${d[0]}.`), o()("h1", {
      "data-text2": `${d[1]}.`
    }, `${d[1]}.`))), o()("div", {
      class: r.a.intro
    }, l.intro), o()("div", {
      class: r.a.ctaContainer
    }, o()(s.a, {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/about`,
      gaLabel: "about button",
      gaCategory: "Home Page"
    }, l.cta)))]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(62),
    s = t(3);
  const c = ["parallax1", "parallax2", "parallax3", "parallax4"];
  let l;
  a.a = {
    id: "careers",
    name: "careers",
    oninit: () => {
      i.a.careers = {}, l = i.a.i18n.home.panels.careers
    },
    oncreate: e => {
      i.a.careers = e.dom
    },
    view: () => [o()("div", {
      class: r.a.panelImageContainer
    }, o()("div", {
      class: r.a.imageOverlay
    }), i.a.desktopSize ? c.map((e => o()("div", {
      id: e,
      class: r.a[e]
    }))) : null), o()("div", {
      oncreate({
        dom: e
      }) {
        e.addEventListener("animationend", (() => {
          e.parentNode.removeChild(e)
        }))
      },
      class: i.a.maskCheck ? r.a.maskLayer : r.a.fadeLayer
    }), o()("div", {
      class: [r.a.panelHeadlineContainer, r.a.showAnims].join(" ")
    }, o()("div", {
      class: r.a.tagline
    }, l.tagline), o()("div", {
      class: r.a.headerText
    }, o()("a", {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/careers`,
      "aria-hidden": "true",
      role: "presentation",
      "data-ga-event": "",
      "data-ga-label": "careers button",
      "data-ga-category": "Home Page"
    }, o()("h1", {
      id: l.header
    }, l.header))), o()("div", {
      class: r.a.ctaContainer
    }, o()(s.a, {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/careers`,
      gaLabel: "careers button",
      gaCategory: "Home Page"
    }, l.cta))), i.a.maskCheck ? o()("canvas", {
      oncreate: ({
        dom: e
      }) => {
        i.a.particlesElem = e
      },
      id: "careersParticles",
      class: r.a.particles
    }) : null]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(63),
    s = t(3),
    c = t(2);
  let l, d;

  function u(e) {
    e.state.curGameImgs.bgImg = e.state.currentGame - 1, e.dom.classList.add(r.a.wipeout), setTimeout((() => {
      e.state.curGameImgs.titleImg = e.state.currentGame - 1, e.state.curGameImgs.fgImg = e.state.currentGame - 1, e.dom.classList.remove(r.a.wipeout), e.dom.classList.add(r.a.wipein), o.a.redraw()
    }), 1250)
  }
  a.a = {
    id: "games",
    name: "games",
    oninit: e => {
      i.a.games = {}, l = i.a.i18n.home.panels.games, d = l.gamelist, e.state.desktop = window.matchMedia(i.a.mq.minLg).matches, e.state.keys = Object.keys(d), e.state.currentGame = 1, e.state.curGameImgs = {
        bgImg: 0,
        fgImg: 0,
        titleImg: 0
      }
    },
    oncreate: e => {
      i.a.games = e.dom
    },
    view: e => [o()("div", {
      class: r.a.panelImageContainer
    }, i.a.desktopSize ? o()("div", {
      class: [r.a.controlsContainer, i.a.safariCheck ? null : r.a.showAnims].join(" ")
    }, o()("div", {
      class: r.a.controls
    }, o()("button", {
      onclick: () => {
        ! function(e) {
          e.state.currentGame = e.state.currentGame % e.state.keys.length + 1, u(e)
        }(e)
      },
      "data-icon": "arrowLeft",
      class: r.a.prevBtn,
      "aria-label": i.a.i18n.misc.buttons.labels.prev
    }), o()("div", {
      style: {
        "background-image": `url(${d[e.state.curGameImgs.titleImg].logoImg})`
      },
      class: r.a.gameTitle
    }), o()("button", {
      onclick: () => {
        ! function(e) {
          e.state.currentGame = e.state.currentGame % e.state.keys.length == 1 ? e.state.keys.length : e.state.currentGame - 1, u(e)
        }(e)
      },
      "data-icon": "arrowRight",
      class: r.a.nextBtn,
      "aria-label": i.a.i18n.misc.buttons.labels.next
    }))) : null, o()("div", {
      class: r.a.backgroundImage,
      style: {
        "background-image": `url(${d[e.state.curGameImgs.fgImg].onImg})`
      }
    }), o()("div", {
      class: r.a.foregroundImage,
      style: {
        "background-image": `url(${d[e.state.curGameImgs.bgImg].offImg})`
      }
    })), o()("div", {
      class: [r.a.panelHeadlineContainer, i.a.safariCheck ? null : r.a.showAnims].join(" ")
    }, o()("div", {
      class: r.a.tagline
    }, l.tagline), o()("div", {
      class: r.a.headerText
    }, o()("a", {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/games`,
      "aria-hidden": "true",
      role: "presentation",
      "data-ga-event": "",
      "data-ga-label": "games button",
      "data-ga-category": "Home Page"
    }, o()("h1", {
      id: t.i(c.a)(l.header)
    }, l.header))), o()("div", {
      class: r.a.ctaContainer
    }, o()(s.a, {
      oncreate: o.a.route.link,
      onupdate: o.a.route.link,
      href: `/${i.a.l10n.lang}/games`,
      gaLabel: "games button",
      gaCategory: "Home Page"
    }, l.cta)))]
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(68);
  a.a = {
    oninit: () => {
      i.a.preload = {}
    },
    oncreate: e => {
      i.a.preload.dom = e.dom, e.state.checkLoader = sessionStorage.getItem("loader")
    },
    view: e => o()("div", {
      class: e.state.checkLoader ? r.a.preloaded : r.a.preloader
    }, o()("img", {
      class: r.a.preloadLogo,
      src: "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyMi4xLjAsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiA2LjAwIEJ1aWxkIDApICAtLT4NCjxzdmcgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeD0iMHB4IiB5PSIwcHgiDQoJIHZpZXdCb3g9IjAgMCA0NjEuNSAxODcuNCIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNDYxLjUgMTg3LjQ7IiB4bWw6c3BhY2U9InByZXNlcnZlIj4NCjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+DQoJLnN0MHtmaWxsOiNGRTAwMDA7fQ0KPC9zdHlsZT4NCjx0aXRsZT5BcmVuYU5ldDwvdGl0bGU+DQo8cGF0aCBpZD0iYXJlbmEiIGNsYXNzPSJzdDAiIGQ9Ik00LjksNjkuM1Y0My44YzE1LjEtNi4zLDMwLjQtMTIsNDYuMS0xN3Y5LjhjMTIuMy00LDI0LjktNy42LDM3LjYtMTAuOHYtOS42DQoJYzEzLjMtMy4zLDI2LjktNi4xLDQwLjYtOC40djkuNWMxMi40LTIuMSwyNC45LTMuOSwzNy42LTUuMlYyLjdjMTMuNC0xLjQsMjYuOS0yLjMsNDAuNi0yLjd2OS4zYzYuMi0wLjIsMTIuNS0wLjMsMTguOC0wLjMNCglzMTIuNiwwLjEsMTguOCwwLjNWMGMxMy43LDAuNCwyNy4yLDEuNCw0MC42LDIuN3Y5LjRjMTIuNywxLjMsMjUuMiwzLjEsMzcuNiw1LjJWNy44YzEzLjcsMi4zLDI3LjIsNS4xLDQwLjYsOC40djkuNg0KCWMxMi43LDMuMiwyNS4yLDYuOCwzNy42LDEwLjh2LTkuOWMxNS43LDUsMzEuMSwxMC43LDQ2LjEsMTd2MjUuNEMzMDYuNCw3LjgsMTQ2LjEsNy44LDQuOSw2OS4zTDQuOSw2OS4zTDQuOSw2OS4zeiBNMjI2LjIsMzUuMw0KCWMtNzYuMy0wLjEtMTUxLjcsMTYtMjIxLjMsNDcuMnYzOS44aDQ2LjF2LTIzYzAuMi0xMC40LDguOC0xOC42LDE5LjItMTguNGMxMCwwLjIsMTguMSw4LjMsMTguNCwxOC40djIzaDQwLjZWOTAuNA0KCWMwLTEwLjQsOC40LTE4LjgsMTguOC0xOC44czE4LjgsOC40LDE4LjgsMTguOHYzMS45aDQwLjZWODUuNWMwLTEwLjQsOC40LTE4LjgsMTguOC0xOC44YzEwLjQsMCwxOC44LDguNCwxOC44LDE4LjhjMCwwLDAsMCwwLDANCgl2MzYuOGg0MC42VjkwLjRjMC4yLTEwLjQsOC44LTE4LjYsMTkuMi0xOC40YzEwLDAuMiwxOC4xLDguMywxOC40LDE4LjR2MzEuOWg0MC42di0yM2MwLTEwLjQsOC40LTE4LjgsMTguOC0xOC44DQoJYzEwLjQsMCwxOC44LDguNCwxOC44LDE4LjhjMCwwLDAsMCwwLDB2MjNoNDYuMVY4Mi41QzM3Ny45LDUxLjIsMzAyLjQsMzUuMSwyMjYuMiwzNS4zTDIyNi4yLDM1LjNMMjI2LjIsMzUuM3oiLz4NCjxwYXRoIGlkPSJ0ZXh0MSIgZD0iTTI3NS43LDE4Mi4xaDEwTDI2NSwxNDIuMmgtOS45bC0yMC40LDM5LjloOS44bDMuNS03LjZoMjQuMUwyNzUuNywxODIuMUwyNzUuNywxODIuMXogTTI1MS4xLDE2Ny45bDguOC0xOS4zDQoJbDkuMSwxOS4zTDI1MS4xLDE2Ny45TDI1MS4xLDE2Ny45eiIvPg0KPHBhdGggaWQ9InRleHQyIiBkPSJNOTQuNSwxNjcuNmg2LjhjMy4yLDAuMiw1LjktMi4yLDYuMS01LjRjMC0wLjEsMC0wLjMsMC0wLjR2LTEyLjNjMCwwLDAtNS42LTYuNy01LjZINjguOHYzOC4yaDguMXYtMTQuNmg3LjkNCglsMTQuNywxNC42SDExMUw5NC41LDE2Ny42TDk0LjUsMTY3LjZMOTQuNSwxNjcuNnogTTk3LDE1MC41YzIuOCwwLDIuOCwzLjQsMi44LDMuNHY0LjNjMC4xLDEuNi0xLjEsMi45LTIuNiwzLjFjLTAuMSwwLTAuMiwwLTAuNCwwDQoJSDc2Ljl2LTEwLjdIOTd6IE0xMjcsMTgyLjFoMzcuN3YtNi44aC0yOS4zdi0xMGgxNy4xVjE1OWgtMTcuMXYtOC41aDI5VjE0NGgtMzcuNSBNMzYwLDE4Mi4xaDM3LjV2LTYuNWgtMjkuM3YtMTAuMmgxNy4xdi02LjMNCgloLTE3LjF2LTguNmgyOXYtNi40aC0zNy40IE0xODEuNywxODIuMVYxNDRoNi4xbDI3LjUsMjUuNFYxNDRoNi41djM4LjFoLTUuNGwtMjguMi0yNnYyNiBNMjk2LjYsMTg2LjlsNi45LDAuMXYtMzUuMWwzNC40LDM1LjENCglsNi0wLjF2LTQ4LjJoLTYuNXYzNC44bC0zMy45LTM0LjhoLTYuOSBNNDA3LjQsMTQ0LjFoNDEuMnY2LjRoLTE2LjV2MzEuNmgtOC42di0zMS42aC0xNi4xIE00NTguMywxNDcuOGMwLjYtMC4yLDEtMC43LDAuOS0xLjMNCgljMC0wLjQtMC4yLTAuOC0wLjUtMS4xYy0wLjQtMC4zLTAuOS0wLjQtMS40LTAuNEg0NTV2NS4xaDFWMTQ4aDEuNGwwLjksMi4xaDFMNDU4LjMsMTQ3LjhMNDU4LjMsMTQ3LjhMNDU4LjMsMTQ3LjhMNDU4LjMsMTQ3Ljh6DQoJIE00NTcuMiwxNDcuM2gtMS4ydi0xLjZoMS4zYzAuNC0wLjEsMC44LDAuMSwxLDAuNWMwLDAuMSwwLDAuMiwwLDAuM2MwLDAuNS0wLjQsMC44LTAuOSwwLjhDNDU3LjMsMTQ3LjMsNDU3LjMsMTQ3LjMsNDU3LjIsMTQ3LjMNCglMNDU3LjIsMTQ3LjNMNDU3LjIsMTQ3LjN6Ii8+DQo8cGF0aCBpZD0idGV4dDMiIGQ9Ik00NjAuMiwxNDQuNGMtMC44LTAuOS0yLTEuNC0zLjItMS40Yy0yLjUsMC00LjUsMi00LjUsNC41YzAsMi41LDIsNC41LDQuNSw0LjVjMS4yLDAsMi4zLTAuNSwzLjEtMS4zDQoJQzQ2MS45LDE0OC45LDQ2MS45LDE0Ni4xLDQ2MC4yLDE0NC40TDQ2MC4yLDE0NC40TDQ2MC4yLDE0NC40eiBNNDU5LjcsMTUwLjNjLTEuNCwxLjUtMy44LDEuNS01LjIsMC4xYzAsMC0wLjEtMC4xLTAuMS0wLjENCgljLTEuNS0xLjUtMS41LTQsMC01LjVjMC43LTAuNywxLjctMS4yLDIuNy0xLjFjMSwwLDIsMC40LDIuNiwxLjFDNDYxLjIsMTQ2LjMsNDYxLjIsMTQ4LjcsNDU5LjcsMTUwLjNMNDU5LjcsMTUwLjNMNDU5LjcsMTUwLjN6DQoJIE00Ny44LDE4Ny40aDkuOUwzMywxMzhoLTguNkwwLDE4Ny40aDEwLjFsNC44LTEwLjJoMjcuOUw0Ny44LDE4Ny40TDQ3LjgsMTg3LjR6IE0xNy45LDE3MC42bDEwLjctMjIuOWwxMS4xLDIyLjlIMTcuOXoiLz4NCjwvc3ZnPg0K",
      title: "ArenaNet"
    }))
  }
}, function(e, a, t) {
  "use strict";
  var n = t(28),
    o = t.n(n),
    i = t(6);
  const r = o()(!1),
    s = "ytIframe";
  let c;

  function l() {
    const e = o()(),
      a = {},
      n = {},
      r = o()(),
      l = o()(),
      d = o()(),
      u = o()();
    let g, p;
    return e.map((e => {
      u(!!e)
    })), o.a.merge([r, l]).map((e => {
      e[0] && e[1] && g && g.playVideo()
    })), d.map((e => {
      if (e) return r(!0);
      r(!1)
    })), {
      renderLightbox: u,
      showLightbox: d,
      iframeId: s,
      attrs: () => a[e()],
      addMedia: e => {
        const t = `ytVideo-${Math.random().toString().split(".")[1]}`,
          o = e.mediaList || "default";
        return a[t] = Object.assign({
          mediaList: o
        }, e), n[o] = n[o] || [], n[o].push(t), t
      },
      removeMedia: e => {
        const t = a[e].mediaList,
          o = n[t].indexOf(e);
        n[t].splice(o, 1), delete a[e]
      },
      backbuttonHandler: () => {
        c.showLightbox(!1), c.close(), window.removeEventListener("popstate", c.backbuttonHandler, !1)
      },
      open: n => {
        e(n);
        const o = {
          8: () => {
            c.showLightbox(!1), c.close()
          },
          27: () => {
            c.showLightbox(!1), c.close()
          },
          37: () => {
            c.prev()
          },
          39: () => {
            c.next()
          }
        };
        c.prevOnkeydown = window.onkeydown, window.onkeydown = e => {
            o[e.keyCode] && (o[e.keyCode](), m.redraw())
          }, window.addEventListener("popstate", c.backbuttonHandler, !1),
          function() {
            const n = a[e()];
            t.i(i.a)("media open", n.ytId || n.src || n.base, 0, "Media View")
          }()
      },
      close: () => {
        ! function() {
          const n = a[e()],
            o = n.ytId && p ? Math.round(p.getCurrentTime()) : 1,
            r = n.ytId || n.src || n.base;
          t.i(i.a)("media close", r, o, "Media View")
        }(), e(void 0), r(!1), window.onkeydown = c.prevOnkeydown
      },
      createPlayer: () => {
        p = new YT.Player(s, {
          events: {
            onReady: e => {
              g = e.target, l(!0)
            },
            onError: () => {}
          }
        })
      },
      destroyPlayer: () => {
        l(!1), p = void 0
      }
    }
  }
  window.onYouTubeIframeAPIReady = function() {
    r(!0)
  }, c = l(), a.a = c
}, function(e, a) {
  a.kabobToCamel = function(e) {
    const a = {};
    return Object.keys(e).forEach((t => {
      const n = t.replaceAll(/-([a-z0-9])/g, ((e, a) => a.toUpperCase()));
      a[n] = e[t]
    })), a
  }
}, function(e, a, t) {
  "use strict";
  var n = t(0),
    o = t.n(n),
    i = t(1),
    r = t(19);
  let s;
  const c = {
      view({
        attrs: e
      }) {
        const {
          key: a,
          field: t,
          error: n,
          clearError: s
        } = e;
        let c, {
          type: l,
          attrs: d
        } = t;
        if (void 0 === d && (d = {}), "object" == typeof l) {
          const e = document.getElementById(l.field);
          l = l.value(e && e.value)
        }
        return t.disabled && (c = t.disabled.some((e => {
          const a = document.getElementById(e.field);
          return !a || !a.value.match(e.value)
        }))), "select" === l ? o()("select", Object.assign({
          class: n ? r.a.selectError : r.a.select,
          id: a,
          name: a,
          onfocus: s,
          onchange: s
        }, d), [o()("option", {
          selected: !0,
          disabled: !0
        }, t.label), t.options.map((e => o()("option", {
          value: e
        }, e)))]) : "checkbox" === l ? o()("label", {
          class: r.a.checkbox
        }, o()("input", Object.assign({
          type: "checkbox",
          name: a,
          class: n ? r.a.checkboxError : r.a.checkbox,
          onfocus: s,
          onclick: s
        }, d)), o.a.trust(t.label)) : "file" === l ? o()("input", Object.assign({
          class: n ? r.a.inputError : r.a.input,
          id: a,
          name: a,
          type: l,
          accept: t.accept,
          onfocus: s,
          onclick: s,
          disabled: c,
          onchange(e) {
            const a = e.target.files[0];
            i.a.fileToSave = a
          }
        }, d)) : o()("input", Object.assign({
          class: n ? r.a.inputError : r.a.input,
          id: a,
          name: a,
          type: l,
          placeholder: t.label,
          onfocus: s,
          onclick: s,
          disabled: c
        }, d))
      }
    },
    l = {
      oninit: () => {
        i.a.hideFooterNav = !1, s = i.a.i18n.vendorForm
      },
      view({
        attrs: e
      }) {
        const {
          key: a,
          field: t,
          results: n
        } = e, i = function(e, a) {
          return a.errors && a.errors[e]
        }(a, n);
        return o()("div", {
          class: r.a.field
        }, "checkbox" !== t.type ? o()("label", {
          for: a,
          class: r.a.label
        }, t.label) : null, o()(c, {
          key: a,
          field: t,
          error: i,
          clearError: function() {
            n.errors[a] = !1
          }
        }), i && o()("div", {
          class: r.a.errorText,
          "data-test": "error-text"
        }, s.error))
      }
    },
    d = {
      view({
        attrs: e
      }) {
        const {
          fields: a,
          results: t
        } = e;
        return Object.entries(a).map((([e, a]) => a.fields ? o()("div", {
          class: r.a.row
        }, o()(d, {
          fields: a.fields,
          results: t
        })) : o()(l, {
          key: e,
          field: a,
          results: t
        })))
      }
    };
  a.a = d
}, function(e, a, t) {
  "use strict";
  a.b = function(e) {
    return a => e.includes(a._value)
  }, a.g = function(e) {
    return "on" === e._value
  };
  a.a = ["EIN", "SSN"];
  a.c = ["New Vendor Setup", "Update Existing Vendor Information"];
  a.d = ["Afghanistan", "Aland Islands", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island", "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo, The Democratic Republic of the", "Cook Islands", "Costa Rica", "Cote D &#x27;Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands (Malvinas)", "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia", "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Heard Island and Mcdonald Islands", "Holy See (Vatican City State)", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran, Islamic Republic Of", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, Republic of", "Kuwait", "Kyrgyzstan", "Lao People &#x27;s Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao", "Macedonia, The Former Yugoslav Republic of", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico", "Micronesia, Federated States of", "Moldova, Republic of", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestinian Territories", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania", "Russian Federation", "Rwanda", "Saint Helena", "Saint Kitts and Nevis", "Saint Lucia", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "Spain", "Sri Lanka", "Sudan", "Suriname", "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland", "Syrian Arab Republic", "Taiwan", "Tajikistan", "Tanzania, United Republic of", "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "United States Minor Outlying Islands", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Viet Nam", "Virgin Islands, British", "Virgin Islands, U.S.", "Wallis and Futuna", "Western Sahara", "Yemen", "Zambia", "Zimbabwe"];
  a.e = ["Alabama", "Alaska", "American Samoa", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "District of Columbia", "Federated States of Micronesia", "Florida", "Georgia", "Guam", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Marshall Islands", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Northern Mariana Islands", "Ohio", "Oklahoma", "Oregon", "Palau", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virgin Island", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"];
  a.f = ["Checking", "Savings"]
}, function(e, a, t) {
  "use strict";
  var n = t(99);
  const o = {
    "vendor-information": {
      label: "Vendor Information",
      fields: {
        "legal-name": {
          label: "Legal Name",
          type: "text",
          schema: "value"
        },
        "dba-name": {
          label: "DBA Name",
          type: "text",
          schema: "value"
        },
        taxes: {
          fields: {
            "tax-id-type": {
              label: "Tax ID Type",
              type: "select",
              options: n.a,
              schema: t.i(n.b)(n.a)
            },
            "tax-id": {
              label: "Tax ID",
              type: "text",
              schema: "value",
              disabled: [{
                field: "tax-id-type",
                value: /.*/
              }]
            }
          }
        },
        "purpose-of-agreement": {
          label: "Purpose of Agreement",
          type: "select",
          options: n.c,
          schema: t.i(n.b)(n.c)
        }
      }
    },
    "existing-vendor": {
      label: "Existing Vendor (Changes only)",
      description: "If you are an existing vendor and wish to change your banking instructions, please complete this section",
      condition: {
        field: "purpose-of-agreement",
        value: n.c[1]
      },
      fields: {
        "routing-number-old": {
          label: "Previous Routing Number/Swift Code",
          type: "text",
          schema: {
            test: "value",
            optional: !0
          }
        },
        "account-number-old": {
          label: "Previous Account Number/IBAN",
          type: "text",
          schema: {
            test: "value",
            optional: !0
          }
        }
      }
    },
    "payment-verification": {
      label: "Payment Verification",
      description: "To protect your account, please provide the last payments received from NC West Holding Co (NC Interactive, LLC and ArenaNet, LLC)",
      condition: {
        field: "purpose-of-agreement",
        value: n.c[1]
      },
      fields: {
        "payment-1": {
          fields: {
            "payment-date-1": {
              label: "Payment 1 Date (MM/DD/YYYY)",
              type: "text",
              schema: {
                optional: !0,
                test: "value"
              }
            },
            "payment-amount-1": {
              label: "Payment 1 Amount",
              type: "number",
              attrs: {
                step: ".01"
              },
              schema: {
                optional: !0,
                test: "value"
              }
            }
          }
        },
        "payment-2": {
          fields: {
            "payment-date-2": {
              label: "Payment 2 Date (MM/DD/YYYY)",
              type: "text",
              schema: {
                optional: !0,
                test: "value"
              }
            },
            "payment-amount-2": {
              label: "Payment 2 Amount",
              type: "number",
              attrs: {
                step: ".01"
              },
              schema: {
                optional: !0,
                test: "value"
              }
            }
          }
        },
        "payment-3": {
          fields: {
            "payment-date-3": {
              label: "Payment 3 Date (MM/DD/YYYY)",
              type: "text",
              schema: {
                optional: !0,
                test: "value"
              }
            },
            "payment-amount-3": {
              label: "Payment 3 Amount",
              type: "number",
              attrs: {
                step: ".01"
              },
              schema: {
                optional: !0,
                test: "value"
              }
            }
          }
        }
      }
    },
    "contact-information": {
      label: "Contact Information",
      fields: {
        "accounting-contact-name": {
          label: "Accounting Contact Name",
          type: "text",
          schema: "value"
        },
        "contact-types": {
          fields: {
            "phone-number": {
              label: "Phone Number",
              type: "tel",
              schema: "value"
            },
            "contact-email": {
              label: "Email Address",
              type: "email",
              schema: "email"
            },
            "remittance-email": {
              label: "Remittance Email Address",
              type: "email",
              schema: "email"
            }
          }
        },
        "street-address": {
          label: "Street Address",
          type: "text",
          schema: "value"
        },
        address: {
          fields: {
            country: {
              label: "Country",
              type: "select",
              options: n.d,
              schema: t.i(n.b)(n.d)
            },
            state: {
              label: "State",
              type: {
                field: "country",
                value: e => e && "United States" !== e ? "text" : "select"
              },
              options: n.e,
              schema: "value"
            },
            city: {
              label: "City",
              type: "text",
              schema: "value"
            },
            "postal-code": {
              label: "Postal Code",
              type: "text",
              schema: "value"
            }
          }
        }
      }
    },
    upload: {
      label: "W9/W8BEN",
      description: "Please upload your form in PDF format, and the maximum file size is 1MB",
      fields: {
        file: {
          label: "W9/W8BEN",
          type: "file",
          accept: ".pdf",
          schema: "value"
        }
      }
    },
    payment: {
      label: "Payment Information",
      fields: {
        "bank-name": {
          label: "Bank Name",
          type: "text",
          schema: "value"
        },
        "bank-account-info": {
          fields: {
            "bank-account-type": {
              label: "Bank Account Type",
              type: "select",
              options: n.f,
              schema: t.i(n.b)(n.f)
            },
            "bank-routing-number": {
              label: "Routing Number/SWIFT Code",
              type: "text",
              schema: "value"
            },
            "bank-account-number": {
              label: "Account Number/IBAN",
              type: "text",
              schema: "value"
            }
          }
        }
      },
      disclaimer: "For payments made to entities outside of the US, the Company utilizes a third-party payment system which completes the payment using a local payment network in the vendor's country, in the country's local currency."
    },
    "requestor-information": {
      label: "Requestor Information",
      fields: {
        "requestor-name": {
          label: "Requestor Name",
          type: "text",
          schema: "value"
        },
        "requestor-title": {
          label: "Requestor Title",
          type: "text",
          schema: "value"
        }
      }
    },
    checks: {
      fields: {
        certify: {
          label: "I hereby certify, to the best of my knowledge, that the information provided above is complete and correct.",
          type: "checkbox",
          schema: n.g
        },
        "privacy-policy": {
          label: 'By clicking Submit Application, I agree to ArenaNet\'s <a href="https://arena.net/legal/privacy-policy">Privacy Policy</a>.',
          type: "checkbox",
          schema: n.g
        }
      }
    }
  };
  a.b = o;
  const i = {};
  const r = function e(a) {
    return Object.entries(a).forEach((([a, t]) => {
      t.schema ? i[a] = t.schema : e(t.fields)
    })), i
  }(o);
  a.a = r
}, function(e, a, t) {
  "use strict";
  var n;
  Object.defineProperty(a, "__esModule", {
    value: !0
  }), a.InterpreterStatus = void 0, (n = a.InterpreterStatus || (a.InterpreterStatus = {}))[n.NotStarted = 0] = "NotStarted", n[n.Running = 1] = "Running", n[n.Stopped = 2] = "Stopped"
}, function(e, a) {
  e.exports = {
    dimebar: {
      forums: {
        en: "https://en-forum.guildwars2.com",
        de: "https://de-forum.guildwars2.com",
        es: "https://es-forum.guildwars2.com",
        fr: "https://fr-forum.guildwars2.com",
        "en-gb": "https://en-forum.guildwars2.com"
      },
      support: {
        en: "https://help.guildwars2.com/hc/en",
        de: "https://help.guildwars2.com/hc/de",
        es: "https://help.guildwars2.com/hc/es",
        fr: "https://help.guildwars2.com/hc/fr",
        "en-gb": "https://help.guildwars2.com/hc/en"
      },
      wiki: {
        en: "https://wiki-en.guildwars2.com",
        de: "https://wiki-de.guildwars2.com",
        es: "https://wiki-es.guildwars2.com",
        fr: "https://wiki-fr.guildwars2.com",
        "en-gb": "https://wiki-en.guildwars2.com"
      },
      login: {
        en: "https://account.arena.net",
        de: "https://account.arena.net",
        es: "https://account.arena.net",
        fr: "https://account.arena.net",
        "en-gb": "https://account.arena.net"
      }
    },
    download: "https://account.arena.net/welcome",
    socials: {
      youtube: {
        en: "https://www.youtube.com/GuildWars2",
        de: "https://www.youtube.com/GuildWars2",
        es: "https://www.youtube.com/GuildWars2",
        fr: "https://www.youtube.com/GuildWars2",
        "en-gb": "https://www.youtube.com/GuildWars2"
      },
      facebook: {
        en: "https://www.facebook.com/GuildWars2",
        de: "https://www.facebook.com/GuildWars2",
        es: "https://www.facebook.com/GuildWars2",
        fr: "https://www.facebook.com/GuildWars2",
        "en-gb": "https://www.facebook.com/GuildWars2"
      },
      twitter: {
        en: "https://twitter.com/GuildWars2",
        de: "https://twitter.com/GuildWars2_DE",
        es: "https://twitter.com/GuildWars2_ES",
        fr: "https://twitter.com/GuildWars2_FR",
        "en-gb": "https://twitter.com/GuildWars2"
      },
      twitch: {
        en: "https://twitch.tv/guildwars2",
        de: "https://twitch.tv/guildwars2",
        es: "https://twitch.tv/guildwars2",
        fr: "https://twitch.tv/guildwars2",
        "en-gb": "https://twitch.tv/guildwars2"
      },
      instagram: {
        en: "https://instagram.com/guildwars2",
        de: "https://instagram.com/guildwars2",
        es: "https://instagram.com/guildwars2",
        fr: "https://instagram.com/guildwars2",
        "en-gb": "https://instagram.com/guildwars2"
      },
      tumblr: {
        en: "https://guildwars2.tumblr.com",
        de: "https://guildwars2.tumblr.com",
        es: "https://guildwars2.tumblr.com",
        fr: "https://guildwars2.tumblr.com",
        "en-gb": "https://guildwars2.tumblr.com"
      },
      flickr: {
        en: "https://www.flickr.com/photos/arenanet",
        de: "https://www.flickr.com/photos/arenanet",
        es: "https://www.flickr.com/photos/arenanet",
        fr: "https://www.flickr.com/photos/arenanet",
        "en-gb": "https://www.flickr.com/photos/arenanet"
      }
    },
    footer: {
      gw2: {
        privacy: "https://arena.net/legal/privacy-policy",
        legal: "https://arena.net/legal"
      },
      gw1: {
        partners: "/{lang}/partners",
        privacy: "/{lang}/privacy-policy",
        legal: "https://arena.net/legal"
      }
    }
  }
}, function(e, a, t) {
  "use strict";
  const n = t(0),
    o = t(18),
    i = t(13);
  e.exports = {
    view(e) {
      const a = o[e.attrs.lang].footer.esrb[e.attrs.footerLinks];
      return n("div", {
        class: i.rating,
        "data-test": "esrb-rating"
      }, n("a", {
        class: i.esrb,
        href: "https://www.esrb.org",
        target: "_blank",
        "aria-label": "esrb"
      }, "esrb"), n("div", n("ul", a.upper.split(",").map((e => n("li", e.trim())))), a.lower && [n("hr"), n("ul", a.lower.split(",").map((e => n("li", e.trim()))))]))
    }
  }
}, function(e, a, t) {
  "use strict";
  const n = t(0),
    o = t(103),
    i = t(105),
    r = t(106),
    s = t(13),
    c = t(107).event,
    l = t(18),
    d = t(41),
    u = t(102),
    m = {
      esrb: o,
      pegi: i,
      usk: r
    };
  let g;
  const p = {
    view(e) {
      const a = g ? n.route.link : null;
      return n("a", Object.assign({
        oncreate: a,
        onupdate: a
      }, e.attrs), e.children)
    }
  };
  e.exports = {
    oninit(e) {
      const {
        lang: a,
        curDate: t,
        routeLink: n
      } = e.attrs;
      g = n;
      const o = l[a] || l.en,
        i = d[a] || d.en;
      e.state.i18n = o, e.state.navs = o.nav.navlinks, e.state.followLinks = Object.keys(o.footer.socials), e.state.copyrightWithYear = i.copyright.replace("{year}", t)
    },
    oncreate() {
      document.dispatchEvent(new Event("anetfooter-loaded"))
    },
    view(e) {
      const {
        lang: a,
        rating: t,
        routeLink: o,
        noSocial: i,
        showNav: r,
        theme: l = "",
        light: d = !1,
        footerLinks: g = "gw2",
        nc: f = !1
      } = e.attrs, {
        followLinks: h,
        i18n: b,
        navs: w,
        copyrightWithYear: y
      } = e.state;
      return n("div", {
        class: [r || i ? null : s.navCleanup, !r && i ? s.halfFooter : s.footer, d ? s.footerLight : "", f ? s.ncFooter : ""].join(" "),
        "data-test": "footer"
      }, r || !i ? [n("ul", {
        class: s.pageFooterNav
      }, Object.keys(w).map((e => n("li", n(p, {
        href: `${o?"":"https://www.arena.net"}/${a}/${w[e].slug}`,
        "data-ga-event": "",
        "data-ga-category": "Footer"
      }, w[e].name)))), n("li", n("a", {
        href: b.nav.shoplink.slug,
        target: "_blank",
        rel: "noreferrer",
        "data-ga-event": "",
        "data-ga-category": "Footer"
      }, b.nav.shoplink.name))), i ? null : n("div", {
        class: `${s[l]} ${s.socialBar}`
      }, n("p", {
        class: s.followUs
      }, b.footer.followUs), h.map((e => n("a", {
        onclick() {
          c("Social Media", b.footer.socials[e].label, 1, "Footer")
        },
        class: s[e],
        href: u.socials[e][a],
        target: "_blank",
        rel: "noreferrer",
        "aria-label": b.footer.socials[e].label
      }))))] : null, n("div", {
        class: s.logos
      }, f ? n(p, {
        class: s.nc,
        href: "" + (o ? "" : "https://www.ncsoft.com"),
        "data-ga-event": "",
        "data-ga-category": "Footer",
        "aria-label": "NCSoft Home"
      }, "NCSoft") : null, n(p, {
        class: `${s.anet} ${s[`anet${l}`]}`,
        href: "" + (o ? "" : "https://www.arena.net"),
        "data-ga-event": "",
        "data-ga-category": "Footer",
        "aria-label": "ArenaNet Home"
      }, "ArenaNet")), n("div", {
        class: s.legalFooter
      }, n("div", n("a", {
        href: "#ShowCookiePreferences",
        onclick: function(e) {
          e.preventDefault();
          const a = window.arenanetCookieNotification;
          a && a.toggle && a.toggle()
        }
      }, b.footer.links.cookiepreferences), Object.entries(u.footer[g]).map((([e, t]) => {
        const o = t.replace("{lang}", a),
          i = b.footer.links[g][e];
        return n(t.includes("https") ? "a" : p, {
          href: o
        }, i)
      }))), n("p", y)), t && m[t] ? n(m[t], {
        lang: a,
        theme: l,
        footerLinks: g
      }) : null)
    }
  }
}, function(e, a, t) {
  "use strict";
  const n = t(0),
    o = t(13);
  e.exports = {
    view: () => n("div", {
      class: o.rating,
      "data-test": "pegi-rating"
    }, n("a", {
      class: o.pegi,
      href: "https://www.pegi.info",
      target: "_blank",
      "aria-label": "pegi"
    }, "pegi"))
  }
}, function(e, a, t) {
  "use strict";
  const n = t(0),
    o = t(13);
  e.exports = {
    view: e => n("div", {
      class: o.rating,
      "data-test": "usk-rating"
    }, n("a", {
      class: o.usk,
      href: "https://www.usk.de",
      target: "_blank",
      "aria-label": "usk"
    }, "usk"))
  }
}, function(e, a, t) {
  "use strict";

  function n(e, a, t, n) {
    (window.dataLayer || []).push({
      event: "event",
      eventCategory: n || "anet2",
      eventAction: e,
      eventLabel: a,
      eventValue: t
    })
  }
  e.exports = {
    event: n,
    clickTracker: function() {
      const e = document.querySelectorAll("[data-ga-event]");
      Array.prototype.forEach.call(e, (e => {
        e.addEventListener("click", (e => {
          n(e.target.dataset.gaAction || "click", e.target.dataset.gaLabel || e.target.text, e.target.dataset.gaValue || 1, e.target.dataset.gaCategory)
        }))
      }))
    },
    pageView: function(e, a) {
      (window.dataLayer || []).push({
        event: "pageview",
        url: e,
        title: a
      })
    },
    scrollHandler: function(e) {
      const a = document.getElementsByTagName("section");
      Array.prototype.forEach.call(a, (a => {
        const t = Date.now(),
          o = a.getBoundingClientRect().top < window.innerHeight,
          i = !a.dataset.gaTriggered || parseInt(a.dataset.gaTriggered, 10) + 3e4 < t;
        o && i && (a.dataset.gaTriggered = t, n("Section view", `${a.id.charAt(0).toUpperCase()+a.id.slice(1)}`, "", `${e} Page`))
      }))
    }
  }
}, function(e, a, t) {
  "use strict";
  a.a = function(e) {
    const a = {};
    if ("form" !== e.nodeName.toLowerCase()) return !1;
    return Array.prototype.forEach.call(e.elements, (e => {
      const t = function(e) {
        const a = e.getAttribute("type"),
          t = null !== e.getAttribute("data-checkbox2"),
          o = {
            type: `${e.nodeName.toLowerCase()}:${a?a.toLowerCase():""}`,
            name: e.getAttribute("name")
          };
        n.includes(o.type) ? o.value = e.value : "select:select-multiple" === o.type ? o.value = Array.prototype.filter.call(e.options, (e => e.selected)) : "input:radio" === o.type || "input:checkbox" === o.type && !t ? e.checked ? o.value = e.value : delete o.name : "input:checkbox" === o.type && t && (o.value = e.checked.toString());
        return o
      }(e);
      t.value && t.name in a ? (Array.isArray(a[t.name]) || (a[t.name] = [a[t.name]]), a[t.name].push(t.value)) : t.name && (a[t.name] = t.value)
    })), a
  };
  const n = ["input:", "input:tel", "input:text", "input:hidden", "input:file", "input:password", "input:number", "input:email", "textarea:", "textarea:textarea", "select:", "select:select-one"]
}, function(e, a, t) {
  ! function(a, t) {
    "use strict";
    var n = function(e) {
        var a = typeof e;
        switch (null === e && (a = "null"), a) {
          case "number":
            return isFinite(e);
          case "null":
          case "undefined":
            return !1;
          default:
            return Boolean(a)
        }
      },
      o = function() {
        for (var e, a, t = 0, n = arguments.length, o = {}; t < n; ++t)
          for (e in a = arguments[t]) a.hasOwnProperty(e) && (o[e] = a[e]);
        return o
      };

    function i() {
      return !1
    }

    function r(e) {
      return "function" == typeof e ? e : t._tests[e] ? t._tests[e] : ((console.error || console.log)("Unknown test " + JSON.stringify(e) + "\n{" + (new Error).stack + "}"), i)
    }

    function s(e) {
      return "string" == typeof e._value && t.regexes[e.test].test(e._value)
    }

    function c(e) {
      return e.optional && (!n(e._value) || "" === e._value)
    }
    t = {
      regexes: {
        email: /\S+@\S+\.\S{2,}$/,
        guid: /^[A-Fa-f0-9]{32}$|^(\{|\()?[A-Fa-f0-9]{8}-([A-Fa-f0-9]{4}-){3}[A-Fa-f0-9]{12}(\}|\))?$/,
        login: /\S+@(?:\S+\.\S+|ncsoft|plaync|ncjapan)$|\\/,
        digits: /^\d+$/
      },
      _error: "__gw2-error__",
      _tests: {
        email: s,
        guid: s,
        login: s,
        digits: s,
        int: function(e) {
          return !isNaN(parseInt(e._value, 10))
        },
        number: function(e) {
          return !isNaN(Number(e._value))
        },
        compare: function(e) {
          var a, t = e._value,
            o = n(e.compare) ? e.compare : this[e.field];
          if (e.optional && !n(o)) return !0;
          switch (e.comparison) {
            case "<":
              a = t < o;
              break;
            case "<=":
              a = t <= o;
              break;
            case ">":
              a = t > o;
              break;
            case ">=":
              a = t >= o;
              break;
            case "!=":
              a = t != o;
              break;
            case "===":
              a = t === o;
              break;
            default:
              a = t == o
          }
          return a
        },
        length: function(e) {
          var a, t = e._value,
            n = e.length;
          switch (e.comparison) {
            case "<":
              a = t.length < n;
              break;
            case "<=":
              a = t.length <= n;
              break;
            case "==":
              a = t.length == n;
              break;
            case ">":
              a = t.length > n;
              break;
            default:
              a = t.length >= n
          }
          return a
        },
        passthrough: function() {
          return !0
        },
        value: function(e) {
          return !!n(e._value) && ("string" != typeof e._value || Boolean(e._value.length))
        },
        boolString: function(e) {
          return !!n(e._value) && ("string" == typeof e._value && ("true" === e._value.toLowerCase() || "false" === e._value.toLowerCase()))
        },
        schema: function(e) {
          return !(!e._value || !e.schema) && t.validate(e._value, e.schema).valid
        }
      },
      validate: function(e, a) {
        var t = {
          valid: !1,
          data: {},
          errors: {}
        };
        return e && "object" == typeof a && "object" == typeof e ? (Object.keys(a).forEach((function(o) {
          var i = e[o],
            s = a[o];
          if (n(i))
            if (t.data[o] = i, Array.isArray(s) || Array.isArray(s.tests))(s.tests || s).some((function(a) {
              if ("string" == typeof a || "function" == typeof a ? a = {
                  test: a,
                  _value: i
                } : "object" == typeof a && (a._value = i), !c(a)) return !r(a.test).call(e, a) && (t.errors[o] = a, !0)
            }));
            else if ("object" == typeof s) {
            if (s.test || (s = {
                test: s
              }), s._value = i, c(s)) return;
            r(s.test).call(e, s) || (t.errors[o] = s)
          } else r((s = {
            test: s,
            _value: i
          }).test).call(e, s) || (t.errors[o] = s);
          else s.optional || (t.errors[o] = "invalid-data")
        })), t.valid = !Object.keys(t.errors).length, t) : t
      },
      error: function(e, a, t) {
        return "object" != typeof e || (e.errors || (e.errors = {}), e.valid = !1, e.errors[a] = {
          test: t || "force",
          _value: e.data && n(e.data[a]) ? e.data[a] : null
        }), e
      },
      test: function(e, a, t) {
        var n = o(t || {}, {
          test: e,
          _value: a
        });
        return r(e).call(this, n)
      },
      add: function(e, a) {
        return !(e in t._tests) && (t._tests[e] = a, !0)
      },
      addRegex: function(e, a) {
        var n = t.add(e, s);
        return n && (t.regexes[e] = a), n
      }
    }, e.exports = t
  }()
}]);