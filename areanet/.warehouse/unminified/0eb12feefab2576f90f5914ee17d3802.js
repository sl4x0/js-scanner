YUI.add("mediaCenter-base", function(e) {
  function t() {}
  t.ATTRS = {
    switchHandler: {
      value: "fade"
    },
    id: {
      value: null
    },
    video: {
      value: {
        width: 794,
        height: 447
      }
    },
    sharing: {
      value: {
        baseUrl: null,
        facebook: !1,
        twitter: !1,
        reddit: !1,
        embed: !1
      }
    }
  }, t.prototype = {
    _handles: [],
    contentHandlers: {},
    itemAnimations: {},
    initializer: function() {},
    _setupBaseDisplay: function(e, t) {
      var n = this;
      e.one(".nclb-next").on("click", function() {
        var e = n.sourceMgr.getSiblingItem(n.currentItem, !0, n);
        e && n._switchToMediaItem(e, !1)
      }), e.one(".nclb-prev").on("click", function() {
        var e = n.sourceMgr.getSiblingItem(n.currentItem, !1, n);
        e && n._switchToMediaItem(e, !1)
      }), e.all(".nclb-social-button, .nclb-dialogue-close").on("click", function() {
        n._setupPopupDisplay(e)
      }), e.on("hover", function() {
        n._showHideOverlaysBase(!0, e)
      }, function() {
        n._showHideOverlaysBase(!1, e)
      }), this.mainEl = e, t()
    },
    _setupPopupDisplay: function(e) {
      var t = "none" !== e.one(".nclb-dialogue").getStyle("display"),
        n = t ? "none" : "block";
      e.one(".nclb-dialogue").setStyle("display", n), this.showingDialog = !t, this._showHideOverlaysBase(t, e)
    },
    _showHideOverlaysBase: function(e, t) {
      this.showingDialog && (e = !1), this._showHideOverlays(e, t), this.currentItem && (t = this._calcItemType(this.currentItem.item), this.contentHandlers[t].showHideOverlays(e))
    },
    _showHideOverlays: function() {},
    _setupContentManager: function() {},
    _domItemSelected: function(e, t) {
      this.sourceMgr && (e = this.sourceMgr.getMediaInfo(e)) && this._switchToMediaItem(e, t)
    },
    _setupItemFields: function(e) {
      var t, n, i = this._getMainContentArea();
      for (t in this._setupShares(i, e), i.one(".nclb-curIndex") && (i.one(".nclb-curIndex").setContent(e.index + 1), i.one(".nclb-totalCount").setContent(e.total)), e.item)
        if ("info" === t)
          for (n in e.item.info) "" !== e.item.info[n] && (i.one(".nclb-field-" + n) ? i.one(".nclb-field-" + n).setContent(e.item.info[n]) : i.one(".nclb-field-" + n) && i.one(".nclb-field-" + n).hide());
      i.one(".nclb-prev") && (e.item.singleItem || 0 === e.index || e.total <= 1 ? i.one(".nclb-prev").addClass("nclb-button-disabled") : i.one(".nclb-prev").removeClass("nclb-button-disabled"), e.item.singleItem || e.index === e.total - 1 || e.total <= 1 ? i.one(".nclb-next").addClass("nclb-button-disabled") : i.one(".nclb-next").removeClass("nclb-button-disabled"))
    },
    _setupShares: function(e, t) {
      var n, i, o = e.one(".link-url"),
        s = this.get("sharing");
      s.baseUrl ? (n = this.get("sharing").baseUrl, i = (n += `#${this.get("id")}/` + t.item.id).replace("#", "%23"), o && o.setAttribute("value", n), (o = e.one(".nclb-facebook")) && s.facebook && o.setAttribute("href", "https://www.facebook.com/share.php?u=" + i), (o = e.one(".facebox-fblike")) && s.facebook && (o.setAttribute("href", i), FB.XFBML.parse()), (o = e.one(".nclb-twitter")) && s.twitter && o.setAttribute("href", "https://twitter.com/share?url=" + i), (o = e.one(".twitter-share-button")) && s.twitter && (o.setAttribute("data-url", i), twttr.widgets.load()), (o = e.one(".nclb-reddit")) && s.reddit && o.setAttribute("href", "https://www.reddit.com/submit?url=" + i), (o = e.one(".embed-url")) && s.embed ? o.setAttribute("value", `<iframe width='560' height='315' src='https://www.youtube.com/embed/${t.item.id}' frameborder='0' allowfullscreen></iframe>`) : e.all(".nclb-dialogue-embed").setStyle("visibility", "hidden"), (i = e.one(".nclb-dialogue-email a")) && s.email ? i.setAttribute("href", `mailto:?body=${n}&subject=Guild Wars 2`) : i && i.setStyle("visibility", "hidden")) : e.all(".nclb-social-button").setStyle("visibility", "hidden")
    },
    _switchToMediaItem: function(t, n) {
      var i = this,
        o = this._calcItemType(t.item),
        e = this._getCoreMediaLocation();
      this.contentHandlers[o].getDomElementPreShow(t, e, function(e) {
        i._setupItemFields(t), i.itemAnimations[i.get("switchHandler")].animate(i.currentItemEl, e, function() {
          i.contentHandlers[o].setupDomElementAfterShow(e, n), i.currentItemType && i.contentHandlers[o].handleDomElementPostShow(i.currentItem, i.currentItemEl), i.currentItemEl = e, i.currentItem = t, i.currentItemType = o
        })
      })
    },
    _calcItemType: function(e) {
      var t;
      if (void 0 === e) return null;
      if (!(t = e._type))
        for (var n in this.contentHandlers)
          if (this.contentHandlers[n].isMyType(e)) {
            e._type = t = n;
            break
          } return t
    },
    _checkForContentAutoplay: function() {
      var e, t, n, i = window.location.hash,
        o = this.get("id");
      if (i && "" !== i && o)
        for (e = (i = i.substr(1)).split("/"), t = 0; t < e.length; t++)
          if (e[t] === o && (n = this.sourceMgr.getMediaItemFromMediaId(e[t + 1]))) return void this.displayMediaItem(n)
    }
  }, e.MediaCenterBase = t
}, "@VERSION@", {
  requires: ["mediaCenter-base", "base-build", "widget-base", "dom-screen", "node-base", "node-event-delegate", "selector-css3", "transition"]
});