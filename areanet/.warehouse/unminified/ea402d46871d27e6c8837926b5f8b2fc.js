YUI.add("sticky-nav", function(n) {
  var a = "fixed",
    i = n.one("body > .gw2-footer"),
    e = n.all(".fixable-menu"),
    l = "topPos",
    s = parseInt(e.getStyle("paddingTop"), 10);

  function t() {
    e.each(function(e) {
      n.DOM.docScrollY() + s > e.getData(l) ? e.addClass(a) : e.removeClass(a);
      var t = i.getY() - n.DOM.docScrollY(),
        o = e.get("offsetHeight") + parseInt(e.getStyle("top"), 10);
      t < o ? e.setStyle("margin-top", t - o + "px") : e.setStyle("margin-top", 0)
    })
  }
  e.each(function(e) {
    e.setData(l, e.getY())
  }), t(), n.Node(n.config.win).on("scroll", function() {
    t()
  })
}, "@VERSION", {
  requires: ["node", "dom-base"]
});