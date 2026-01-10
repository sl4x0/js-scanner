YUI.add("skip-to-main-content", function(e) {
  var n = e.one("#skip-to-main-content");
  n && n.on("keydown", function(e) {
    32 === e.keyCode && (e.preventDefault(), n.simulate("click"))
  })
}, "@VERSION", {
  requires: ["node", "event", "dom-base"]
});