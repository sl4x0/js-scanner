YUI.add("sticky-buy", function(o) {
  var s = o.one(".stickyBuy"),
    o = s.one(".stickyBuy-close"),
    c = s.one(".stickyBuy-open");
  s && (o.on("click", function() {
    s.removeClass("stickyBuy-show")
  }), c.on("click", function() {
    s.addClass("stickyBuy-show")
  }))
}, "@VERSION", {
  requires: ["node", "event", "dom-base"]
});