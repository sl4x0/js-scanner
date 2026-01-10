YUI.add("yulb", function(r) {
  var e = r.all(".yulb-launcher"),
    t = window.document.body.clientWidth,
    t = t < 1e3 ? t - 60 : 1e3,
    s = {
      width: t,
      height: .5625 * t,
      params: {
        autoplay: 1,
        modestbranding: 1,
        showinfo: 0,
        rel: 0,
        autohide: 1,
        wmode: "transparent",
        enablejsapi: 1
      }
    },
    t = new URLSearchParams(location.search).get("play"),
    i = r.one(".yulb-launcher"),
    a = r.one(`[data-vidid=${t}]`);
  r.yulb = {
    defaults: s,
    launchers: e
  }, e.isEmpty() || (e.each(function(o) {
    o.on("click", function(e) {
      var t = {
          vidid: o.getData("vidid"),
          width: parseInt(o.getData("vidwidth"), 10) || s.width,
          height: parseInt(o.getData("vidheight"), 10) || s.height,
          params: r.Array.map(r.Object.keys(s.params), function(e) {
            return e + "=" + s.params[e]
          }).join("&")
        },
        i = {
          width: r.DOM.winWidth(),
          height: r.DOM.winHeight()
        },
        a = {
          width: t.width,
          height: t.height
        },
        d = {
          launcher: o,
          vidid: t.vidid
        },
        n = r.Node.create(r.Lang.sub("<div class='yulb-overlay' style='width:{width}px; height: {height}px;'></div>", i)),
        h = r.Node.create(r.Lang.sub("<div class='yulb-container' style='width:{width}px; height:{height}px;'></div>", a));
      e.preventDefault(), h.appendTo(n), r.Node.create("<div class='yulb-close'>close</div>").appendTo(h), r.Node.create(r.Lang.sub("<iframe type='text/html' width='{width}' height='{height}' src='https://www.youtube.com/embed/{vidid}?{params}' frameborder='0' allow='autoplay'/>", t)).appendTo(h), n.appendTo(document.body), r.fire("yulb:open", d), s.params.mute = 0, n.on("click", function() {
        var e = this;
        h.getDOMNode().getElementsByTagName("iframe")[0].contentWindow.postMessage(JSON.stringify({
          event: "command",
          func: "stopVideo"
        }), "*"), setTimeout(function() {
          e.remove(!0)
        }, 100), r.fire("yulb:close", d)
      }), r.on("windowresize", function() {
        n.setStyles({
          width: r.DOM.winWidth(),
          height: r.DOM.winHeight()
        })
      })
    })
  }), t && (i || a) && (s.params.mute = 1, (i || a).getDOMNode().click()))
}, "@VERSION@", {
  requires: ["node", "event", "array-extras"]
});