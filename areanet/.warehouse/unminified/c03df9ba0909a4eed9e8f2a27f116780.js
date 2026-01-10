YUI.add("async-queue", function(e, t) {
  e.AsyncQueue = function() {
    this._init(), this.add.apply(this, arguments)
  };
  var n = e.AsyncQueue,
    r = "execute",
    i = "shift",
    s = "promote",
    o = "remove",
    u = e.Lang.isObject,
    a = e.Lang.isFunction;
  n.defaults = e.mix({
    autoContinue: !0,
    iterations: 1,
    timeout: 10,
    until: function() {
      return this.iterations |= 0, this.iterations <= 0
    }
  }, e.config.queueDefaults || {}), e.extend(n, e.EventTarget, {
    _running: !1,
    _init: function() {
      e.EventTarget.call(this, {
        prefix: "queue",
        emitFacade: !0
      }), this._q = [], this.defaults = {}, this._initEvents()
    },
    _initEvents: function() {
      this.publish({
        execute: {
          defaultFn: this._defExecFn,
          emitFacade: !0
        },
        shift: {
          defaultFn: this._defShiftFn,
          emitFacade: !0
        },
        add: {
          defaultFn: this._defAddFn,
          emitFacade: !0
        },
        promote: {
          defaultFn: this._defPromoteFn,
          emitFacade: !0
        },
        remove: {
          defaultFn: this._defRemoveFn,
          emitFacade: !0
        }
      })
    },
    next: function() {
      var e;
      while (this._q.length) {
        e = this._q[0] = this._prepare(this._q[0]);
        if (!e || !e.until()) break;
        this.fire(i, {
          callback: e
        }), e = null
      }
      return e || null
    },
    _defShiftFn: function(e) {
      this.indexOf(e.callback) === 0 && this._q.shift()
    },
    _prepare: function(t) {
      if (a(t) && t._prepared) return t;
      var r = e.merge(n.defaults, {
          context: this,
          args: [],
          _prepared: !0
        }, this.defaults, a(t) ? {
          fn: t
        } : t),
        i = e.bind(function() {
          i._running || i.iterations--, a(i.fn) && i.fn.apply(i.context || e, e.Array(i.args))
        }, this);
      return e.mix(i, r)
    },
    run: function() {
      var e, t = !0;
      if (this._executing) return this._running = !0, this;
      for (e = this.next(); e && !this.isRunning(); e = this.next()) {
        t = e.timeout < 0 ? this._execute(e) : this._schedule(e);
        if (!t) break
      }
      return e || this.fire("complete"), this
    },
    _execute: function(e) {
      this._running = e._running = !0, this._executing = e, e.iterations--, this.fire(r, {
        callback: e
      });
      var t = this._running && e.autoContinue;
      return this._running = e._running = !1, this._executing = !1, t
    },
    _schedule: function(t) {
      return this._running = e.later(t.timeout, this, function() {
        this._execute(t) && this.run()
      }), !1
    },
    isRunning: function() {
      return !!this._running
    },
    _defExecFn: function(e) {
      e.callback()
    },
    add: function() {
      return this.fire("add", {
        callbacks: e.Array(arguments, 0, !0)
      }), this
    },
    _defAddFn: function(t) {
      var n = this._q,
        r = [];
      e.Array.each(t.callbacks, function(e) {
        u(e) && (n.push(e), r.push(e))
      }), t.added = r
    },
    pause: function() {
      return this._running && u(this._running) && this._running.cancel(), this._running = !1, this
    },
    stop: function() {
      return this._q = [], this._running && u(this._running) && (this._running.cancel(), this._running = !1), this._executing || this.run(), this
    },
    indexOf: function(e) {
      var t = 0,
        n = this._q.length,
        r;
      for (; t < n; ++t) {
        r = this._q[t];
        if (r === e || r.id === e) return t
      }
      return -1
    },
    getCallback: function(e) {
      var t = this.indexOf(e);
      return t > -1 ? this._q[t] : null
    },
    promote: function(e) {
      var t = {
          callback: e
        },
        n;
      return this.isRunning() ? n = this.after(i, function() {
        this.fire(s, t), n.detach()
      }, this) : this.fire(s, t), this
    },
    _defPromoteFn: function(e) {
      var t = this.indexOf(e.callback),
        n = t > -1 ? this._q.splice(t, 1)[0] : null;
      e.promoted = n, n && this._q.unshift(n)
    },
    remove: function(e) {
      var t = {
          callback: e
        },
        n;
      return this.isRunning() ? n = this.after(i, function() {
        this.fire(o, t), n.detach()
      }, this) : this.fire(o, t), this
    },
    _defRemoveFn: function(e) {
      var t = this.indexOf(e.callback);
      e.removed = t > -1 ? this._q.splice(t, 1)[0] : null
    },
    size: function() {
      return this.isRunning() || this.next(), this._q.length
    }
  })
}, "@VERSION@", {
  requires: ["event-custom"]
});

YUI.add("gesture-simulate", function(e, t) {
  function T(n) {
    n || e.error(t + ": invalid target node"), this.node = n, this.target = e.Node.getDOMNode(n);
    var r = this.node.getXY(),
      i = this._getDims();
    a = r[0] + i[0] / 2, f = r[1] + i[1] / 2
  }
  var t = "gesture-simulate",
    n = e.config.win && "ontouchstart" in e.config.win && !e.UA.phantomjs && !(e.UA.chrome && e.UA.chrome < 6),
    r = {
      tap: 1,
      doubletap: 1,
      press: 1,
      move: 1,
      flick: 1,
      pinch: 1,
      rotate: 1
    },
    i = {
      touchstart: 1,
      touchmove: 1,
      touchend: 1,
      touchcancel: 1
    },
    s = e.config.doc,
    o, u = 20,
    a, f, l = {
      HOLD_TAP: 10,
      DELAY_TAP: 10,
      HOLD_PRESS: 3e3,
      MIN_HOLD_PRESS: 1e3,
      MAX_HOLD_PRESS: 6e4,
      DISTANCE_MOVE: 200,
      DURATION_MOVE: 1e3,
      MAX_DURATION_MOVE: 5e3,
      MIN_VELOCITY_FLICK: 1.3,
      DISTANCE_FLICK: 200,
      DURATION_FLICK: 1e3,
      MAX_DURATION_FLICK: 5e3,
      DURATION_PINCH: 1e3
    },
    c = "touchstart",
    h = "touchmove",
    p = "touchend",
    d = "gesturestart",
    v = "gesturechange",
    m = "gestureend",
    g = "mouseup",
    y = "mousemove",
    b = "mousedown",
    w = "click",
    E = "dblclick",
    S = "x",
    x = "y";
  T.prototype = {
    _toRadian: function(e) {
      return e * (Math.PI / 180)
    },
    _getDims: function() {
      var e, t, n;
      return this.target.getBoundingClientRect ? (e = this.target.getBoundingClientRect(), "height" in e ? n = e.height : n = Math.abs(e.bottom - e.top), "width" in e ? t = e.width : t = Math.abs(e.right - e.left)) : (e = this.node.get("region"), t = e.width, n = e.height), [t, n]
    },
    _calculateDefaultPoint: function(t) {
      var n;
      return !e.Lang.isArray(t) || t.length === 0 ? t = [a, f] : (t.length == 1 && (n = this._getDims[1], t[1] = n / 2), t[0] = this.node.getX() + t[0], t[1] = this.node.getY() + t[1]), t
    },
    rotate: function(n, r, i, s, o, u, a) {
      var f, l = i,
        c = s;
      if (!e.Lang.isNumber(l) || !e.Lang.isNumber(c) || l < 0 || c < 0) f = this.target.offsetWidth < this.target.offsetHeight ? this.target.offsetWidth / 4 : this.target.offsetHeight / 4, l = f, c = f;
      e.Lang.isNumber(a) || e.error(t + "Invalid rotation detected."), this.pinch(n, r, l, c, o, u, a)
    },
    pinch: function(n, r, i, s, o, a, f) {
      var g, y, b = u,
        w, E = 0,
        S = i,
        x = s,
        T, N, C, k, L, A, O, M, _, D = {
          start: [],
          end: []
        },
        P = {
          start: [],
          end: []
        },
        H, B;
      r = this._calculateDefaultPoint(r), (!e.Lang.isNumber(S) || !e.Lang.isNumber(x) || S < 0 || x < 0) && e.error(t + "Invalid startRadius and endRadius detected.");
      if (!e.Lang.isNumber(o) || o <= 0) o = l.DURATION_PINCH;
      if (!e.Lang.isNumber(a)) a = 0;
      else {
        a %= 360;
        while (a < 0) a += 360
      }
      e.Lang.isNumber(f) || (f = 0), e.AsyncQueue.defaults.timeout = b, g = new e.AsyncQueue, N = r[0], C = r[1], O = a, M = a + f, D.start = [N + S * Math.sin(this._toRadian(O)), C - S * Math.cos(this._toRadian(O))], D.end = [N + x * Math.sin(this._toRadian(M)), C - x * Math.cos(this._toRadian(M))], P.start = [N - S * Math.sin(this._toRadian(O)), C + S * Math.cos(this._toRadian(O))], P.end = [N - x * Math.sin(this._toRadian(M)), C + x * Math.cos(this._toRadian(M))], k = 1, L = s / i, g.add({
        fn: function() {
          var t, n, r, i;
          t = {
            pageX: D.start[0],
            pageY: D.start[1],
            clientX: D.start[0],
            clientY: D.start[1]
          }, n = {
            pageX: P.start[0],
            pageY: P.start[1],
            clientX: P.start[0],
            clientY: P.start[1]
          }, i = this._createTouchList([e.merge({
            identifier: E++
          }, t), e.merge({
            identifier: E++
          }, n)]), r = {
            pageX: (D.start[0] + P.start[0]) / 2,
            pageY: (D.start[0] + P.start[1]) / 2,
            clientX: (D.start[0] + P.start[0]) / 2,
            clientY: (D.start[0] + P.start[1]) / 2
          }, this._simulateEvent(this.target, c, e.merge({
            touches: i,
            targetTouches: i,
            changedTouches: i,
            scale: k,
            rotation: O
          }, r)), e.UA.ios >= 2 && this._simulateEvent(this.target, d, e.merge({
            scale: k,
            rotation: O
          }, r))
        },
        timeout: 0,
        context: this
      }), H = Math.floor(o / b), T = (x - S) / H, A = (L - k) / H, _ = (M - O) / H, B = function(t) {
        var n = S + T * t,
          r = N + n * Math.sin(this._toRadian(O + _ * t)),
          i = C - n * Math.cos(this._toRadian(O + _ * t)),
          s = N - n * Math.sin(this._toRadian(O + _ * t)),
          o = C + n * Math.cos(this._toRadian(O + _ * t)),
          u = (r + s) / 2,
          a = (i + o) / 2,
          f, l, c, p;
        f = {
          pageX: r,
          pageY: i,
          clientX: r,
          clientY: i
        }, l = {
          pageX: s,
          pageY: o,
          clientX: s,
          clientY: o
        }, p = this._createTouchList([e.merge({
          identifier: E++
        }, f), e.merge({
          identifier: E++
        }, l)]), c = {
          pageX: u,
          pageY: a,
          clientX: u,
          clientY: a
        }, this._simulateEvent(this.target, h, e.merge({
          touches: p,
          targetTouches: p,
          changedTouches: p,
          scale: k + A * t,
          rotation: O + _ * t
        }, c)), e.UA.ios >= 2 && this._simulateEvent(this.target, v, e.merge({
          scale: k + A * t,
          rotation: O + _ * t
        }, c))
      };
      for (y = 0; y < H; y++) g.add({
        fn: B,
        args: [y],
        context: this
      });
      g.add({
        fn: function() {
          var t = this._getEmptyTouchList(),
            n, r, i, s;
          n = {
            pageX: D.end[0],
            pageY: D.end[1],
            clientX: D.end[0],
            clientY: D.end[1]
          }, r = {
            pageX: P.end[0],
            pageY: P.end[1],
            clientX: P.end[0],
            clientY: P.end[1]
          }, s = this._createTouchList([e.merge({
            identifier: E++
          }, n), e.merge({
            identifier: E++
          }, r)]), i = {
            pageX: (D.end[0] + P.end[0]) / 2,
            pageY: (D.end[0] + P.end[1]) / 2,
            clientX: (D.end[0] + P.end[0]) / 2,
            clientY: (D.end[0] + P.end[1]) / 2
          }, e.UA.ios >= 2 && this._simulateEvent(this.target, m, e.merge({
            scale: L,
            rotation: M
          }, i)), this._simulateEvent(this.target, p, e.merge({
            touches: t,
            targetTouches: t,
            changedTouches: s,
            scale: L,
            rotation: M
          }, i))
        },
        context: this
      }), n && e.Lang.isFunction(n) && g.add({
        fn: n,
        context: this.node
      }), g.run()
    },
    tap: function(t, r, i, s, o) {
      var u = new e.AsyncQueue,
        a = this._getEmptyTouchList(),
        f, h, d, v, m;
      r = this._calculateDefaultPoint(r);
      if (!e.Lang.isNumber(i) || i < 1) i = 1;
      e.Lang.isNumber(s) || (s = l.HOLD_TAP), e.Lang.isNumber(o) || (o = l.DELAY_TAP), h = {
        pageX: r[0],
        pageY: r[1],
        clientX: r[0],
        clientY: r[1]
      }, f = this._createTouchList([e.merge({
        identifier: 0
      }, h)]), v = function() {
        this._simulateEvent(this.target, c, e.merge({
          touches: f,
          targetTouches: f,
          changedTouches: f
        }, h))
      }, m = function() {
        this._simulateEvent(this.target, p, e.merge({
          touches: a,
          targetTouches: a,
          changedTouches: f
        }, h))
      };
      for (d = 0; d < i; d++) u.add({
        fn: v,
        context: this,
        timeout: d === 0 ? 0 : o
      }), u.add({
        fn: m,
        context: this,
        timeout: s
      });
      i > 1 && !n && u.add({
        fn: function() {
          this._simulateEvent(this.target, E, h)
        },
        context: this
      }), t && e.Lang.isFunction(t) && u.add({
        fn: t,
        context: this.node
      }), u.run()
    },
    flick: function(n, r, i, s, o) {
      var u;
      r = this._calculateDefaultPoint(r), e.Lang.isString(i) ? (i = i.toLowerCase(), i !== S && i !== x && e.error(t + "(flick): Only x or y axis allowed")) : i = S, e.Lang.isNumber(s) || (s = l.DISTANCE_FLICK), e.Lang.isNumber(o) ? o > l.MAX_DURATION_FLICK && (o = l.MAX_DURATION_FLICK) : o = l.DURATION_FLICK, Math.abs(s) / o < l.MIN_VELOCITY_FLICK && (o = Math.abs(s) / l.MIN_VELOCITY_FLICK), u = {
        start: e.clone(r),
        end: [i === S ? r[0] + s : r[0], i === x ? r[1] + s : r[1]]
      }, this._move(n, u, o)
    },
    move: function(t, n, r) {
      var i;
      e.Lang.isObject(n) ? (e.Lang.isArray(n.point) ? n.point = this._calculateDefaultPoint(n.point) : n.point = this._calculateDefaultPoint([]), e.Lang.isNumber(n.xdist) || (n.xdist = l.DISTANCE_MOVE), e.Lang.isNumber(n.ydist) || (n.ydist = 0)) : n = {
        point: this._calculateDefaultPoint([]),
        xdist: l.
        DISTANCE_MOVE,
        ydist: 0
      }, e.Lang.isNumber(r) ? r > l.MAX_DURATION_MOVE && (r = l.MAX_DURATION_MOVE) : r = l.DURATION_MOVE, i = {
        start: e.clone(n.point),
        end: [n.point[0] + n.xdist, n.point[1] + n.ydist]
      }, this._move(t, i, r)
    },
    _move: function(t, n, r) {
      var i, s, o = u,
        d, v, m, g = 0,
        y;
      e.Lang.isNumber(r) ? r > l.MAX_DURATION_MOVE && (r = l.MAX_DURATION_MOVE) : r = l.DURATION_MOVE, e.Lang.isObject(n) ? (e.Lang.isArray(n.start) || (n.start = [a, f]), e.Lang.isArray(n.end) || (n.end = [a + l.DISTANCE_MOVE, f])) : n = {
        start: [a, f],
        end: [a + l.DISTANCE_MOVE, f]
      }, e.AsyncQueue.defaults.timeout = o, i = new e.AsyncQueue, i.add({
        fn: function() {
          var t = {
              pageX: n.start[0],
              pageY: n.start[1],
              clientX: n.start[0],
              clientY: n.start[1]
            },
            r = this._createTouchList([e.merge({
              identifier: g++
            }, t)]);
          this._simulateEvent(this.target, c, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: r
          }, t))
        },
        timeout: 0,
        context: this
      }), d = Math.floor(r / o), v = (n.end[0] - n.start[0]) / d, m = (n.end[1] - n.start[1]) / d, y = function(t) {
        var r = n.start[0] + v * t,
          i = n.start[1] + m * t,
          s = {
            pageX: r,
            pageY: i,
            clientX: r,
            clientY: i
          },
          o = this._createTouchList([e.merge({
            identifier: g++
          }, s)]);
        this._simulateEvent(this.target, h, e.merge({
          touches: o,
          targetTouches: o,
          changedTouches: o
        }, s))
      };
      for (s = 0; s < d; s++) i.add({
        fn: y,
        args: [s],
        context: this
      });
      i.add({
        fn: function() {
          var t = {
              pageX: n.end[0],
              pageY: n.end[1],
              clientX: n.end[0],
              clientY: n.end[1]
            },
            r = this._createTouchList([e.merge({
              identifier: g
            }, t)]);
          this._simulateEvent(this.target, h, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: r
          }, t))
        },
        timeout: 0,
        context: this
      }), i.add({
        fn: function() {
          var t = {
              pageX: n.end[0],
              pageY: n.end[1],
              clientX: n.end[0],
              clientY: n.end[1]
            },
            r = this._getEmptyTouchList(),
            i = this._createTouchList([e.merge({
              identifier: g
            }, t)]);
          this._simulateEvent(this.target, p, e.merge({
            touches: r,
            targetTouches: r,
            changedTouches: i
          }, t))
        },
        context: this
      }), t && e.Lang.isFunction(t) && i.add({
        fn: t,
        context: this.node
      }), i.run()
    },
    _getEmptyTouchList: function() {
      return o || (o = this._createTouchList([])), o
    },
    _createTouchList: function(n) {
      var r = [],
        i, o = this;
      return !!n && e.Lang.isArray(n) ? e.UA.android && e.UA.android >= 4 || e.UA.ios && e.UA.ios >= 2 ? (e.each(n, function(t) {
        t.identifier || (t.identifier = 0), t.pageX || (t.pageX = 0), t.pageY || (t.pageY = 0), t.screenX || (t.screenX = 0), t.screenY || (t.screenY = 0), r.push(s.createTouch(e.config.win, o.target, t.identifier, t.pageX, t.pageY, t.screenX, t.screenY))
      }), i = s.createTouchList.apply(s, r)) : e.UA.ios && e.UA.ios < 2 ? e.error(t + ": No touch event simulation framework present.") : (i = [], e.each(n, function(e) {
        e.identifier || (e.identifier = 0), e.clientX || (e.clientX = 0), e.clientY || (e.clientY = 0), e.pageX || (e.pageX = 0), e.pageY || (e.pageY = 0), e.screenX || (e.screenX = 0), e.screenY || (e.screenY = 0), i.push({
          target: o.target,
          identifier: e.identifier,
          clientX: e.clientX,
          clientY: e.clientY,
          pageX: e.pageX,
          pageY: e.pageY,
          screenX: e.screenX,
          screenY: e.screenY
        })
      }), i.item = function(e) {
        return i[e]
      }) : e.error(t + ": Invalid touchPoints passed"), i
    },
    _simulateEvent: function(t, r, s) {
      var o;
      i[r] ? n ? e.Event.simulate(t, r, s) : this._isSingleTouch(s.touches, s.targetTouches, s.changedTouches) ? (r = {
        touchstart: b,
        touchmove: y,
        touchend: g
      } [r], s.button = 0, s.relatedTarget = null, o = r === g ? s.changedTouches : s.touches, s = e.mix(s, {
        screenX: o.item(0).screenX,
        screenY: o.item(0).screenY,
        clientX: o.item(0).clientX,
        clientY: o.item(0).clientY
      }, !0), e.Event.simulate(t, r, s), r == g && e.Event.simulate(t, w, s)) : e.error("_simulateEvent(): Event '" + r + "' has multi touch objects that can't be simulated in your platform.") : e.Event.simulate(t, r, s)
    },
    _isSingleTouch: function(e, t, n) {
      return e && e.length <= 1 && t && t.length <= 1 && n && n.length <= 1
    }
  }, e.GestureSimulation = T, e.GestureSimulation.defaults = l, e.GestureSimulation.GESTURES = r, e.Event.simulateGesture = function(n, i, s, o) {
    n = e.one(n);
    var u = new e.GestureSimulation(n);
    i = i.toLowerCase(), !o && e.Lang.isFunction(s) && (o = s, s = {}), s = s || {};
    if (r[i]) switch (i) {
      case "tap":
        u.tap(o, s.point, s.times, s.hold, s.delay);
        break;
      case "doubletap":
        u.tap(o, s.point, 2);
        break;
      case "press":
        e.Lang.isNumber(s.hold) ? s.hold < l.MIN_HOLD_PRESS ? s.hold = l.MIN_HOLD_PRESS : s.hold > l.MAX_HOLD_PRESS && (s.hold = l.MAX_HOLD_PRESS) : s.hold = l.HOLD_PRESS, u.tap(o, s.point, 1, s.hold);
        break;
      case "move":
        u.move(o, s.path, s.duration);
        break;
      case "flick":
        u.flick(o, s.point, s.axis, s.distance, s.duration);
        break;
      case "pinch":
        u.pinch(o, s.center, s.r1, s.r2, s.duration, s.start, s.rotation);
        break;
      case "rotate":
        u.rotate(o, s.center, s.r1, s.r2, s.duration, s.start, s.rotation)
    } else e.error(t + ": Not a supported gesture simulation: " + i)
  }
}, "@VERSION@", {
  requires: ["async-queue", "event-simulate", "node-screen"]
});

YUI.add("node-event-simulate", function(e, t) {
  e.Node.prototype.simulate = function(t, n) {
    e.Event.simulate(e.Node.getDOMNode(this), t, n)
  }, e.Node.prototype.simulateGesture = function(t, n, r) {
    e.Event.simulateGesture(this, t, n, r)
  }
}, "@VERSION@", {
  requires: ["node-base", "event-simulate", "gesture-simulate"]
});

YUI.add("event-key", function(e, t) {
  var n = "+alt",
    r = "+ctrl",
    i = "+meta",
    s = "+shift",
    o = e.Lang.trim,
    u = {
      KEY_MAP: {
        enter: 13,
        space: 32,
        esc: 27,
        backspace: 8,
        tab: 9,
        pageup: 33,
        pagedown: 34
      },
      _typeRE: /^(up|down|press):/,
      _keysRE: /^(?:up|down|press):|\+(alt|ctrl|meta|shift)/g,
      processArgs: function(t) {
        var n = t.splice(3, 1)[0],
          r = e.Array.hash(n.match(/\+(?:alt|ctrl|meta|shift)\b/g) || []),
          i = {
            type: this._typeRE.test(n) ? RegExp.$1 : null,
            mods: r,
            keys: null
          },
          s = n.replace(this._keysRE, ""),
          u, a, f, l;
        if (s) {
          s = s.split(","), i.keys = {};
          for (l = s.length - 1; l >= 0; --l) {
            u = o(s[l]);
            if (!u) continue; + u == u ? i.keys[u] = r : (f = u.toLowerCase(), this.KEY_MAP[f] ? (i.keys[this.KEY_MAP[f]] = r, i.type || (i.type = "down")) : (u = u.charAt(0), a = u.toUpperCase(), r["+shift"] && (u = a), i.keys[u.charCodeAt(0)] = u === a ? e.merge(r, {
              "+shift": !0
            }) : r))
          }
        }
        return i.type || (i.type = "press"), i
      },
      on: function(e, t, o, u) {
        var a = t._extra,
          f = "key" + a.type,
          l = a.keys,
          c = u ? "delegate" : "on";
        t._detach = e[c](f, function(e) {
          var t = l ? l[e.which] : a.mods;
          t && (!t[n] || t[n] && e.altKey) && (!t[r] || t[r] && e.ctrlKey) && (!t[i] || t[i] && e.metaKey) && (!t[s] || t[s] && e.shiftKey) && o.fire(e)
        }, u)
      },
      detach: function(e, t, n) {
        t._detach.detach()
      }
    };
  u.delegate = u.on, u.detachDelegate = u.detach, e.Event.define("key", u, !0)
}, "@VERSION@", {
  requires: ["event-synthetic"]
});

YUI.add("node-focusmanager", function(e, t) {
  var n = "activeDescendant",
    r = "id",
    i = "disabled",
    s = "tabIndex",
    o = "focused",
    u = "focusClass",
    a = "circular",
    f = "UI",
    l = "key",
    c = n + "Change",
    h = "host",
    p = {
      37: !0,
      38: !0,
      39: !0,
      40: !0
    },
    d = {
      a: !0,
      button: !0,
      input: !0,
      object: !0
    },
    v = e.Lang,
    m = e.UA,
    g = function() {
      g.superclass.constructor.apply(this, arguments)
    };
  g.ATTRS = {
    focused: {
      value: !1,
      readOnly: !0
    },
    descendants: {
      getter: function(e) {
        return this.get(h).all(e)
      }
    },
    activeDescendant: {
      setter: function(t) {
        var n = v.isNumber,
          i = e.Attribute.INVALID_VALUE,
          s = this._descendantsMap,
          o = this._descendants,
          u, a, f;
        return n(t) ? (u = t, a = u) : t instanceof e.Node && s ? (u = s[t.get(r)], n(u) ? a = u : a = i) : a = i, o && (f = o.item(u), f && f.get("disabled") && (a = i)), a
      }
    },
    keys: {
      value: {
        next: null,
        previous: null
      }
    },
    focusClass: {},
    circular: {
      value: !0
    }
  }, e.extend(g, e.Plugin.Base, {
    _stopped: !0,
    _descendants: null,
    _descendantsMap: null,
    _focusedNode: null,
    _lastNodeIndex: 0,
    _eventHandlers: null,
    _initDescendants: function() {
      var t = this.get("descendants"),
        o = {},
        u = -1,
        a, f = this.get(n),
        l, c, h = 0;
      v.isUndefined(f) && (f = -1);
      if (t) {
        a = t.size();
        for (h = 0; h < a; h++) l = t.item(h), u === -1 && !l.get(i) && (u = h), f < 0 && parseInt(l.getAttribute(s, 2), 10) === 0 && (f = h), l && l.set(s, -1), c = l.get(r), c || (c = e.guid(), l.set(r, c)), o[c] = h;
        f < 0 && (f = 0), l = t.item(f);
        if (!l || l.get(i)) l = t.item(u), f = u;
        this._lastNodeIndex = a - 1, this._descendants = t, this._descendantsMap = o, this.set(n, f), l && l.set(s, 0)
      }
    },
    _isDescendant: function(e) {
      return e.get(r) in this._descendantsMap
    },
    _removeFocusClass: function() {
      var e = this._focusedNode,
        t = this.get(u),
        n;
      t && (n = v.isString(t) ? t : t.className), e && n && e.removeClass(n)
    },
    _detachKeyHandler: function() {
      var e = this._prevKeyHandler,
        t = this._nextKeyHandler;
      e && e.detach(), t && t.detach()
    },
    _preventScroll: function(e) {
      p[e.keyCode] && this._isDescendant(e.target) && e.preventDefault()
    },
    _fireClick: function(e) {
      var t = e.target,
        n = t.get("nodeName").toLowerCase();
      e.keyCode === 13 && (!d[n] || n === "a" && !t.getAttribute("href")) && t.simulate("click")
    },
    _attachKeyHandler: function() {
      this._detachKeyHandler();
      var t = this.get("keys.next"),
        n = this.get("keys.previous"),
        r = this.get(h),
        i = this._eventHandlers;
      n && (this._prevKeyHandler = e.on(l, e.bind(this._focusPrevious, this), r, n)), t && (this._nextKeyHandler = e.on(l, e.bind(this._focusNext, this), r, t)), m.opera && i.push(r.on("keypress", this._preventScroll, this)), m.opera || i.push(r.on("keypress", this._fireClick, this))
    },
    _detachEventHandlers: function() {
      this._detachKeyHandler();
      var t = this._eventHandlers;
      t && (e.Array.each(t, function(e) {
        e.detach()
      }), this._eventHandlers = null)
    },
    _attachEventHandlers: function() {
      var t = this._descendants,
        n, r, i;
      t && t.size() && (n = this._eventHandlers || [], r = this.get(h).get("ownerDocument"), n.length === 0 && (n.push(r.on("focus", this._onDocFocus, this)), n.push(r.on("mousedown", this._onDocMouseDown, this)), n.push(this.after("keysChange", this._attachKeyHandler)), n.push(this.after("descendantsChange", this._initDescendants)), n.push(this.after(c, this._afterActiveDescendantChange)), i = this.after("focusedChange", e.bind(function(e) {
        e.newVal && (this._attachKeyHandler(), i.detach())
      }, this)), n.push(i)), this._eventHandlers = n)
    },
    _onDocMouseDown: function(e) {
      var t = this.get(h),
        n = e.target,
        r = t.contains(n),
        i, s = function(e) {
          var n = !1;
          return e.compareTo(t) || (n = this._isDescendant(e) ? e : s.call(this, e.get("parentNode"))), n
        };
      r && (i = s.call(this, n), i ? n = i : !i && this.get(o) && (this._set(o, !1), this._onDocFocus(e))), r && this._isDescendant(n) ? this.focus(n) : m.webkit && this.get(o) && (!r || r && !this._isDescendant(n)) && (this._set(o, !1), this._onDocFocus(e))
    },
    _onDocFocus: function(e) {
      var t = this._focusTarget || e.target,
        n = this.get(o),
        r = this.get(u),
        i = this._focusedNode,
        s;
      this._focusTarget && (this._focusTarget = null), this.get(h).contains(t) ? (s = this._isDescendant(t), !n && s ? n = !0 : n && !s && (n = !1)) : n = !1, r && (i && (!i.compareTo(t) || !n) && this._removeFocusClass(), s && n && (r.fn ? (t = r.fn(t), t.addClass(r.className)) : t.addClass(r), this._focusedNode = t)), this._set(o, n)
    },
    _focusNext: function(e, t) {
      var r = t || this.get(n),
        i;
      this._isDescendant(e.target) && r <= this._lastNodeIndex && (r += 1, r === this._lastNodeIndex + 1 && this.get(a) && (r = 0), i = this._descendants.item(r), i && (i.get("disabled") ? this._focusNext(e, r) : this.focus(r))), this._preventScroll(e)
    },
    _focusPrevious: function(e, t) {
      var r = t || this.get(n),
        i;
      this._isDescendant(e.target) && r >= 0 && (r -= 1, r === -1 && this.get(a) && (r = this._lastNodeIndex), i = this._descendants.item(r), i && (i.get("disabled") ? this._focusPrevious(e, r) : this.focus(r))), this._preventScroll(e)
    },
    _afterActiveDescendantChange: function(e) {
      var t = this._descendants.item(e.prevVal);
      t && t.set(s, -1), t = this._descendants.item(e.newVal), t && t.set(s, 0)
    },
    initializer: function(e) {
      this.start()
    },
    destructor: function() {
      this.stop(), this.get(h).focusManager = null
    },
    focus: function(e) {
      v.isUndefined(e) && (e = this.get(n)), this.set(n, e, {
        src: f
      });
      var t = this._descendants.item(this.get(n));
      t && (t.focus(), m.opera && t.get("nodeName").toLowerCase() === "button" && (this._focusTarget = t))
    },
    blur: function() {
      var e;
      this.get(o) && (e = this._descendants.item(this.get(n)), e && (e.blur(), this._removeFocusClass()), this._set(o, !1, {
        src: f
      }))
    },
    start: function() {
      this._stopped && (this._initDescendants(), this._attachEventHandlers(), this._stopped = !1)
    },
    stop: function() {
      this._stopped || (this._detachEventHandlers(), this._descendants = null, this._focusedNode = null, this._lastNodeIndex = 0, this._stopped = !0)
    },
    refresh: function() {
      this._initDescendants(), this._eventHandlers || this._attachEventHandlers()
    }
  }), g.NAME = "nodeFocusManager", g.NS = "focusManager", e.namespace("Plugin"), e.Plugin.NodeFocusManager = g
}, "@VERSION@", {
  requires: ["attribute", "node", "plugin", "node-event-simulate", "event-key", "event-focus"]
});

YUI.add("tabview", function(e, t) {
  var n = ".",
    r = e.Base.create("tabView", e.Widget, [e.WidgetParent], {
      _afterChildAdded: function() {
        this.get("contentBox").focusManager.refresh()
      },
      _defListNodeValueFn: function() {
        var t = e.Node.create(this.LIST_TEMPLATE);
        return t.addClass(e.TabviewBase._classNames.tabviewList), t
      },
      _defPanelNodeValueFn: function() {
        var t = e.Node.create(this.PANEL_TEMPLATE);
        return t.addClass(e.TabviewBase._classNames.tabviewPanel), t
      },
      _afterChildRemoved: function(e) {
        var t = e.index,
          n = this.get("selection");
        n || (n = this.item(t - 1) || this.item(0), n && n.set("selected", 1)), this.get("contentBox").focusManager.refresh()
      },
      _initAria: function(t) {
        var n = t.one(e.TabviewBase._queries.tabviewList);
        n && n.setAttrs({
          role: "tablist"
        })
      },
      bindUI: function() {
        this.get("contentBox").plug(e.Plugin.NodeFocusManager, {
          descendants: n + e.TabviewBase._classNames.tabLabel,
          keys: {
            next: "down:39",
            previous: "down:37"
          },
          circular: !0
        }), this.after("render", this._setDefSelection), this.after("addChild", this._afterChildAdded), this.after("removeChild", this._afterChildRemoved)
      },
      renderUI: function() {
        var e = this.get("contentBox");
        this._renderListBox(e), this._renderPanelBox(e), this._childrenContainer = this.get("listNode"), this._renderTabs(e), this._initAria(e)
      },
      _setDefSelection: function() {
        var e = this.get("selection") || this.item(0);
        this.some(function(t) {
          if (t.get("selected")) return e = t, !0
        }), e && (this.set("selection", e), e.set("selected", 1))
      },
      _renderListBox: function(e) {
        var t = this.get("listNode");
        t.inDoc() || e.append(t)
      },
      _renderPanelBox: function(e) {
        var t = this.get("panelNode");
        t.inDoc() || e.append(t)
      },
      _renderTabs: function(t) {
        var r = e.TabviewBase._classNames,
          i = e.TabviewBase._queries,
          s = t.all(i.tab),
          o = this.get("panelNode"),
          u = o ? this.get("panelNode").get("children") : null,
          a = this;
        s && (s.addClass(r.tab), t.all(i.tabLabel).addClass(r.tabLabel), t.all(i.tabPanel).addClass(r.tabPanel), s.each(function(e, t) {
          var i = u ? u.item(t) : null;
          a.add({
            boundingBox: e,
            contentBox: e.one(n + r.tabLabel),
            panelNode: i
          })
        }))
      }
    }, {
      ATTRS: {
        defaultChildType: {
          value: "Tab"
        },
        listNode: {
          setter: function(t) {
            return t = e.one(t), t && t.addClass(e.TabviewBase._classNames.tabviewList), t
          },
          valueFn: "_defListNodeValueFn"
        },
        panelNode: {
          setter: function(t) {
            return t = e.one(t), t && t.addClass(e.TabviewBase._classNames.tabviewPanel), t
          },
          valueFn: "_defPanelNodeValueFn"
        },
        tabIndex: {
          value: null
        }
      },
      HTML_PARSER: {
        listNode: function(t) {
          return t.one(e.TabviewBase._queries.tabviewList)
        },
        panelNode: function(t) {
          return t.one(e.TabviewBase._queries.tabviewPanel)
        }
      },
      LIST_TEMPLATE: "<ul></ul>",
      PANEL_TEMPLATE: "<div></div>"
    });
  r.prototype.LIST_TEMPLATE = r.LIST_TEMPLATE, r.prototype.PANEL_TEMPLATE = r.PANEL_TEMPLATE, e.TabView = r, e.Tab = e.Base.create("tab", e.Widget, [e.WidgetChild], {
    BOUNDING_TEMPLATE: "<li></li>",
    CONTENT_TEMPLATE: "<a></a>",
    PANEL_TEMPLATE: "<div></div>",
    _uiSetSelectedPanel: function(t) {
      this.get("panelNode").toggleClass(e.TabviewBase._classNames.selectedPanel, t)
    },
    _afterTabSelectedChange: function(e) {
      this._uiSetSelectedPanel(e.newVal)
    },
    _afterParentChange: function(e) {
      e.newVal ? this._add() : this._remove()
    },
    _initAria: function() {
      var t = this.get("contentBox"),
        n = t.get("id"),
        r = this.get("panelNode");
      n || (n = e.guid(), t.set("id", n)), t.set("role", "tab"), t.get("parentNode").set("role", "presentation"), r.setAttrs({
        role: "tabpanel",
        "aria-labelledby": n
      })
    },
    syncUI: function() {
      var t = e.TabviewBase._classNames;
      this.get("boundingBox").addClass(t.tab), this.get("contentBox").addClass(t.tabLabel), this.set("label", this.get("label")), this.set("content", this.get("content")), this._uiSetSelectedPanel(this.get("selected"))
    },
    bindUI: function() {
      this.after("selectedChange", this._afterTabSelectedChange), this.after("parentChange", this._afterParentChange)
    },
    renderUI: function() {
      this._renderPanel(), this._initAria()
    },
    _renderPanel: function() {
      this.get("parent").get("panelNode").appendChild(this.get("panelNode"))
    },
    _add: function() {
      var e = this.get("parent").get("contentBox"),
        t = e.get("listNode"),
        n = e.get("panelNode");
      t && t.appendChild(this.get("boundingBox")), n && n.appendChild(this.get("panelNode"))
    },
    _remove: function() {
      this.get("boundingBox").remove(), this.get("panelNode").remove()
    },
    _onActivate: function(e) {
      e.target === this && (e.domEvent.preventDefault(), e.target.set("selected", 1))
    },
    initializer: function() {
      this.publish(this.get("triggerEvent"), {
        defaultFn: this._onActivate
      })
    },
    _defLabelGetter: function() {
      return this.get("contentBox").getHTML()
    },
    _defLabelSetter: function(e) {
      var t = this.get("contentBox");
      return t.getHTML() !== e && t.setHTML(e), e
    },
    _defContentSetter: function(e) {
      var t = this.get("panelNode");
      return t.getHTML() !== e && t.setHTML(e), e
    },
    _defContentGetter: function() {
      return this.get("panelNode").getHTML()
    },
    _defPanelNodeValueFn: function() {
      var t = e.TabviewBase._classNames,
        n = this.get("contentBox").get("href") || "",
        r = this.get("parent"),
        i = n.indexOf("#"),
        s;
      return n = n.substr(i), n.charAt(0) === "#" && (s = e.one(n), s && s.addClass(t.tabPanel)), !s && r && (s = r.get("panelNode").get("children").item(this.get("index"))), s || (s = e.Node.create(this.PANEL_TEMPLATE), s.addClass(t.tabPanel)), s
    }
  }, {
    ATTRS: {
      triggerEvent: {
        value: "click"
      },
      label: {
        setter: "_defLabelSetter",
        getter: "_defLabelGetter"
      },
      content: {
        setter: "_defContentSetter",
        getter: "_defContentGetter"
      },
      panelNode: {
        setter: function(t) {
          return t = e.one(t), t && t.addClass(e.TabviewBase._classNames.tabPanel), t
        },
        valueFn: "_defPanelNodeValueFn"
      },
      tabIndex: {
        value: null,
        validator: "_validTabIndex"
      }
    },
    HTML_PARSER: {
      selected: function() {
        var t = this.get("boundingBox").hasClass(e.TabviewBase._classNames.selectedTab) ? 1 : 0;
        return t
      }
    }
  })
}, "@VERSION@", {
  requires: ["widget", "widget-parent", "widget-child", "tabview-base", "node-pluginhost", "node-focusmanager"],
  skinnable: !0
});

YUI.add("transition", function(e, t) {
  var n = "",
    r = "",
    i = e.config.doc,
    s = "documentElement",
    o = i[s].style,
    u = "transition",
    a = "transitionProperty",
    f, l, c, h, p, d, v = {},
    m = ["Webkit", "Moz"],
    g = {
      Webkit: "webkitTransitionEnd"
    },
    y = function() {
      this.init.apply(this, arguments)
    };
  y._TRANSFORM = "transform", y._toCamel = function(e) {
    return e = e.replace(/-([a-z])/gi, function(e, t) {
      return t.toUpperCase()
    }), e
  }, y._toHyphen = function(e) {
    return e = e.replace(/([A-Z]?)([a-z]+)([A-Z]?)/g, function(e, t, n, r) {
      var i = (t ? "-" + t.toLowerCase() : "") + n;
      return r && (i += "-" + r.toLowerCase()), i
    }), e
  }, y.SHOW_TRANSITION = "fadeIn", y.HIDE_TRANSITION = "fadeOut", y.useNative = !1, "transition" in o && "transitionProperty" in o && "transitionDuration" in o && "transitionTimingFunction" in o && "transitionDelay" in o ? (y.useNative = !0, y.supported = !0) : e.Array.each(m, function(e) {
    var t = e + "Transition";
    t in i[s].style && (n = e, r = y._toHyphen(e) + "-", y.useNative = !0, y.supported = !0, y._VENDOR_PREFIX = e)
  }), typeof o.transform == "undefined" && e.Array.each(m, function(e) {
    var t = e + "Transform";
    typeof o[t] != "undefined" && (y._TRANSFORM = t)
  }), n && (u = n + "Transition", a = n + "TransitionProperty"), f = r + "transition-property", l = r + "transition-duration", c = r + "transition-timing-function", h = r + "transition-delay", p = "transitionend", d = "on" + n.toLowerCase() + "transitionend", p = g[n] || p, y.fx = {}, y.toggles = {}, y._hasEnd = {}, y._reKeywords = /^(?:node|duration|iterations|easing|delay|on|onstart|onend)$/i, e.Node.DOM_EVENTS[p] = 1, y.NAME = "transition", y.DEFAULT_EASING = "ease", y.DEFAULT_DURATION = .5, y.DEFAULT_DELAY = 0, y._nodeAttrs = {}, y.prototype = {
    constructor: y,
    init: function(e, t) {
      var n = this;
      return n._node = e, !n._running && t && (n._config = t, e._transition = n, n._duration = "duration" in t ? t.duration : n.constructor.DEFAULT_DURATION, n._delay = "delay" in t ? t.delay : n.constructor.DEFAULT_DELAY, n._easing = t.easing || n.constructor.DEFAULT_EASING, n._count = 0, n._running = !1), n
    },
    addProperty: function(t, n) {
      var r = this,
        i = this._node,
        s = e.stamp(i),
        o = e.one(i),
        u = y._nodeAttrs[s],
        a, f, l, c, h;
      u || (u = y._nodeAttrs[s] = {}), c = u[t], n && n.value !== undefined ? h = n.value : n !== undefined && (h = n, n = v), typeof h == "function" && (h = h.call(o, o)), c && c.transition && c.transition !== r && c.transition._count--, r._count++, l = (typeof n.duration != "undefined" ? n.duration : r._duration) || 1e-4, u[t] = {
        value: h,
        duration: l,
        delay: typeof n.delay != "undefined" ? n.delay : r._delay,
        easing: n.easing || r._easing,
        transition: r
      }, a = e.DOM.getComputedStyle(i, t), f = typeof h == "string" ? a : parseFloat(a), y.useNative && f === h && setTimeout(function() {
        r._onNativeEnd.call(i, {
          propertyName: t,
          elapsedTime: l
        })
      }, l * 1e3)
    },
    removeProperty: function(t) {
      var n = this,
        r = y._nodeAttrs[e.stamp(n._node)];
      r && r[t] && (delete r[t], n._count--)
    },
    initAttrs: function(t) {
      var n, r = this._node;
      t.transform && !t[y._TRANSFORM] && (t[y._TRANSFORM] = t.transform, delete t.transform);
      for (n in t) t.hasOwnProperty(n) && !y._reKeywords.test(n) && (this.addProperty(n, t[n]), r.style[n] === "" && e.DOM.setStyle(r, n, e.DOM.getComputedStyle(r, n)))
    },
    run: function(t) {
      var n = this,
        r = n._node,
        i = n._config,
        s = {
          type: "transition:start",
          config: i
        };
      return n._running || (n._running = !0, i.on && i.on.start && i.on.start.call(e.one(r), s), n.initAttrs(n._config), n._callback = t, n._start()), n
    },
    _start: function() {
      this._runNative()
    },
    _prepDur: function(e) {
      return e = parseFloat(e) * 1e3, e + "ms"
    },
    _runNative: function() {
      var t = this,
        n = t._node,
        r = e.stamp(n),
        i = n.style,
        s = n.ownerDocument.defaultView.getComputedStyle(n),
        o = y._nodeAttrs[r],
        u = "",
        a = s[y._toCamel(f)],
        d = f + ": ",
        v = l + ": ",
        m = c + ": ",
        g = h + ": ",
        b, w, E;
      a !== "all" && (d += a + ",", v += s[y._toCamel(l)] + ",", m += s[y._toCamel(c)] + ",", g += s[y._toCamel(h)] + ",");
      for (E in o) b = y._toHyphen(E), w = o[E], (w = o[E]) && w.transition === t && (E in n.style ? (v += t._prepDur(w.duration) + ",", g += t._prepDur(w.delay) + ",", m += w.easing + ",", d += b + ",", u += b + ": " + w.value + "; ") : this.removeProperty(E));
      d = d.replace(/,$/, ";"), v = v.replace(/,$/, ";"), m = m.replace(/,$/, ";"), g = g.replace(/,$/, ";"), y._hasEnd[r] || (n.addEventListener(p, t._onNativeEnd, ""), y._hasEnd[r] = !0), i.cssText += d + v + m + g + u
    },
    _end: function(t) {
      var n = this,
        r = n._node,
        i = n._callback,
        s = n._config,
        o = {
          type: "transition:end",
          config: s,
          elapsedTime: t
        },
        u = e.one(r);
      n._running = !1, n._callback = null, r && (s.on && s.on.end ? setTimeout(function() {
        s.on.end.call(u, o), i && i.call(u, o)
      }, 1) : i && setTimeout(function() {
        i.call(u, o)
      }, 1))
    },
    _endNative: function(e) {
      var t = this._node,
        n = t.ownerDocument.defaultView.getComputedStyle(t, "")[y._toCamel(f)];
      e = y._toHyphen(e), typeof n == "string" && (n = n.replace(new RegExp("(?:^|,\\s)" + e + ",?"), ","), n = n.replace(/^,|,$/, ""), t.style[u] = n)
    },
    _onNativeEnd: function(t) {
      var n = this,
        r = e.stamp(n),
        i = t,
        s = y._toCamel(i.propertyName),
        o = i.elapsedTime,
        u = y._nodeAttrs[r],
        f = u[s],
        l = f ? f.transition : null,
        c, h;
      l && (l.removeProperty(s), l._endNative(s), h = l._config[s], c = {
        type: "propertyEnd",
        propertyName: s,
        elapsedTime: o,
        config: h
      }, h && h.on && h.on.end && h.on.end.call(e.one(n), c), l._count <= 0 && (l._end(o), n.style[a] = ""))
    },
    destroy: function() {
      var e = this,
        t = e._node;
      t && (t.removeEventListener(p, e._onNativeEnd, !1), e._node = null)
    }
  }, e.Transition = y, e.TransitionNative = y, e.Node.prototype.transition = function(t, n, r) {
    var i = y._nodeAttrs[e.stamp(this._node)],
      s = i ? i.transition || null : null,
      o, u;
    if (typeof t == "string") {
      typeof n == "function" && (r = n, n = null), o = y.fx[t];
      if (n && typeof n == "object") {
        n = e.clone(n);
        for (u in o) o.hasOwnProperty(u) && (u in n || (n[u] = o[u]))
      } else n = o
    } else r = n, n = t;
    return s && !s._running ? s.init(this, n) : s = new y(this._node, n), s.run(r), this
  }, e.Node.prototype.show = function(t, n, r) {
    return this._show(), t && e.Transition && (typeof t != "string" && !t.push && (typeof n == "function" && (r = n, n = t), t = y.SHOW_TRANSITION), this.transition(t, n, r)), this
  }, e.NodeList.prototype.show = function(t, n, r) {
    var i = this._nodes,
      s = 0,
      o;
    while (o = i[s++]) e.one(o).show(t, n, r);
    return this
  };
  var b = function(e, t, n) {
    return function() {
      t && t.call(e), n && typeof n == "function" && n.apply(e._node, arguments)
    }
  };
  e.Node.prototype.hide = function(t, n, r) {
      return t && e.Transition ? (typeof n == "function" && (r = n, n = null), r = b(this, this._hide, r), typeof t != "string" && !t.push && (typeof n == "function" && (r = n, n = t), t = y.HIDE_TRANSITION), this.transition(t, n, r)) : this._hide(), this
    }, e.NodeList.prototype.hide = function(t, n, r) {
      var i = this._nodes,
        s = 0,
        o;
      while (o = i[s++]) e.one(o).hide(t, n, r);
      return this
    }, e.NodeList.prototype
    .transition = function(t, n, r) {
      var i = this._nodes,
        s = this.size(),
        o = 0,
        r = r === !0,
        u;
      while (u = i[o++]) o < s && r ? e.one(u).transition(t) : e.one(u).transition(t, n);
      return this
    }, e.Node.prototype.toggleView = function(t, n, r) {
      this._toggles = this._toggles || [], r = arguments[arguments.length - 1];
      if (typeof t != "string") {
        n = t, this._toggleView(n, r);
        return
      }
      return typeof n == "function" && (n = undefined), typeof n == "undefined" && t in this._toggles && (n = !this._toggles[t]), n = n ? 1 : 0, n ? this._show() : r = b(this, this._hide, r), this._toggles[t] = n, this.transition(e.Transition.toggles[t][n], r), this
    }, e.NodeList.prototype.toggleView = function(t, n, r) {
      var i = this._nodes,
        s = 0,
        o;
      while (o = i[s++]) o = e.one(o), o.toggleView.apply(o, arguments);
      return this
    }, e.mix(y.fx, {
      fadeOut: {
        opacity: 0,
        duration: .5,
        easing: "ease-out"
      },
      fadeIn: {
        opacity: 1,
        duration: .5,
        easing: "ease-in"
      },
      sizeOut: {
        height: 0,
        width: 0,
        duration: .75,
        easing: "ease-out"
      },
      sizeIn: {
        height: function(e) {
          return e.get("scrollHeight") + "px"
        },
        width: function(e) {
          return e.get("scrollWidth") + "px"
        },
        duration: .5,
        easing: "ease-in",
        on: {
          start: function() {
            var e = this.getStyle("overflow");
            e !== "hidden" && (this.setStyle("overflow", "hidden"), this._transitionOverflow = e)
          },
          end: function() {
            this._transitionOverflow && (this.setStyle("overflow", this._transitionOverflow), delete this._transitionOverflow)
          }
        }
      }
    }), e.mix(y.toggles, {
      size: ["sizeOut", "sizeIn"],
      fade: ["fadeOut", "fadeIn"]
    })
}, "@VERSION@", {
  requires: ["node-style"]
});

YUI.add("cookie", function(e, t) {
  function h(e) {
    throw new TypeError(e)
  }

  function p(e) {
    (!s(e) || e === "") && h("Cookie name must be a non-empty string.")
  }

  function d(e) {
    (!s(e) || e === "") && h("Subcookie name must be a non-empty string.")
  }
  var n = e.Lang,
    r = e.Object,
    i = null,
    s = n.isString,
    o = n.isObject,
    u = n.isUndefined,
    a = n.isFunction,
    f = encodeURIComponent,
    l = decodeURIComponent,
    c = e.config.doc;
  e.Cookie = {
    _createCookieString: function(e, t, n, r) {
      r = r || {};
      var i = f(e) + "=" + (n ? f(t) : t),
        u = r.expires,
        a = r.path,
        l = r.domain;
      return o(r) && (u instanceof Date && (i += "; expires=" + u.toUTCString()), s(a) && a !== "" && (i += "; path=" + a), s(l) && l !== "" && (i += "; domain=" + l), r.secure === !0 && (i += "; secure")), i
    },
    _createCookieHashString: function(e) {
      o(e) || h("Cookie._createCookieHashString(): Argument must be an object.");
      var t = [];
      return r.each(e, function(e, n) {
        !a(e) && !u(e) && t.push(f(n) + "=" + f(String(e)))
      }), t.join("&")
    },
    _parseCookieHash: function(e) {
      var t = e.split("&"),
        n = i,
        r = {};
      if (e.length)
        for (var s = 0, o = t.length; s < o; s++) n = t[s].split("="), r[l(n[0])] = l(n[1]);
      return r
    },
    _parseCookieString: function(e, t, n) {
      var r = {};
      if (s(e) && e.length > 0) {
        var o = t === !1 ? function(e) {
            return e
          } : l,
          a = e.split(/;\s/g),
          f = i,
          c = i,
          h = i;
        for (var p = 0, d = a.length; p < d; p++) {
          h = a[p].match(/([^=]+)=/i);
          if (h instanceof Array) try {
            f = l(h[1]), c = o(a[p].substring(h[1].length + 1))
          } catch (v) {} else f = l(a[p]), c = "";
          !u(n) && n.reverseCookieLoading ? u(r[f]) && (r[f] = c) : r[f] = c
        }
      }
      return r
    },
    _setDoc: function(e) {
      c = e
    },
    exists: function(e) {
      p(e);
      var t = this._parseCookieString(c.cookie, !0);
      return t.hasOwnProperty(e)
    },
    get: function(e, t) {
      p(e);
      var n, r, s;
      return a(t) ? (s = t, t = {}) : o(t) ? s = t.converter : t = {}, n = this._parseCookieString(c.cookie, !t.raw, t), r = n[e], u(r) ? i : a(s) ? s(r) : r
    },
    getSub: function(e, t, n, r) {
      var s = this.getSubs(e, r);
      return s !== i ? (d(t), u(s[t]) ? i : a(n) ? n(s[t]) : s[t]) : i
    },
    getSubs: function(e, t) {
      p(e);
      var n = this._parseCookieString(c.cookie, !1, t);
      return s(n[e]) ? this._parseCookieHash(n[e]) : i
    },
    remove: function(t, n) {
      return p(t), n = e.merge(n || {}, {
        expires: new Date(0)
      }), this.set(t, "", n)
    },
    removeSub: function(e, t, n) {
      p(e), d(t), n = n || {};
      var r = this.getSubs(e);
      if (o(r) && r.hasOwnProperty(t)) {
        delete r[t];
        if (!n.removeIfEmpty) return this.setSubs(e, r, n);
        for (var i in r)
          if (r.hasOwnProperty(i) && !a(r[i]) && !u(r[i])) return this.setSubs(e, r, n);
        return this.remove(e, n)
      }
      return ""
    },
    set: function(e, t, n) {
      p(e), u(t) && h("Cookie.set(): Value cannot be undefined."), n = n || {};
      var r = this._createCookieString(e, t, !n.raw, n);
      return c.cookie = r, r
    },
    setSub: function(e, t, n, r) {
      p(e), d(t), u(n) && h("Cookie.setSub(): Subcookie value cannot be undefined.");
      var i = this.getSubs(e);
      return o(i) || (i = {}), i[t] = n, this.setSubs(e, i, r)
    },
    setSubs: function(e, t, n) {
      p(e), o(t) || h("Cookie.setSubs(): Cookie value must be an object.");
      var r = this._createCookieString(e, this._createCookieHashString(t), !1, n);
      return c.cookie = r, r
    }
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("event-mousewheel", function(e, t) {
  var n = "DOMMouseScroll",
    r = function(t) {
      var r = e.Array(t, 0, !0),
        i;
      return e.UA.gecko ? (r[0] = n, i = e.config.win) : i = e.config.doc, r.length < 3 ? r[2] = i : r.splice(2, 0, i), r
    };
  e.Env.evt.plugins.mousewheel = {
    on: function() {
      return e.Event._attach(r(arguments))
    },
    detach: function() {
      return e.Event.detach.apply(e.Event, r(arguments))
    }
  }
}, "@VERSION@", {
  requires: ["node-base"]
});

YUI.add("event-mouseenter", function(e, t) {
  var n = e.Env.evt.dom_wrappers,
    r = e.DOM.contains,
    i = e.Array,
    s = function() {},
    o = {
      proxyType: "mouseover",
      relProperty: "fromElement",
      _notify: function(t, i, s) {
        var o = this._node,
          u = t.relatedTarget || t[i];
        o !== u && !r(o, u) && s.fire(new e.DOMEventFacade(t, o, n["event:" + e.stamp(o) + t.type]))
      },
      on: function(t, n, r) {
        var i = e.Node.getDOMNode(t),
          s = [this.proxyType, this._notify, i, null, this.relProperty, r];
        n.handle = e.Event._attach(s, {
          facade: !1
        })
      },
      detach: function(e, t) {
        t.handle.detach()
      },
      delegate: function(t, n, r, i) {
        var o = e.Node.getDOMNode(t),
          u = [this.proxyType, s, o, null, r];
        n.handle = e.Event._attach(u, {
          facade: !1
        }), n.handle.sub.filter = i, n.handle.sub.relProperty = this.relProperty, n.handle.sub._notify = this._filterNotify
      },
      _filterNotify: function(t, n, s) {
        n = n.slice(), this.args && n.push.apply(n, this.args);
        var o = e.delegate._applyFilter(this.filter, n, s),
          u = n[0].relatedTarget || n[0][this.relProperty],
          a, f, l, c, h;
        if (o) {
          o = i(o);
          for (f = 0, l = o.length && (!a || !a.stopped); f < l; ++f) {
            h = o[0];
            if (!r(h, u)) {
              a || (a = new e.DOMEventFacade(n[0], h, s), a.container = e.one(s.el)), a.currentTarget = e.one(h), c = n[1].fire(a);
              if (c === !1) break
            }
          }
        }
        return c
      },
      detachDelegate: function(e, t) {
        t.handle.detach()
      }
    };
  e.Event.define("mouseenter", o, !0), e.Event.define("mouseleave", e.merge(o, {
    proxyType: "mouseout",
    relProperty: "toElement"
  }), !0)
}, "@VERSION@", {
  requires: ["event-synthetic"]
});

YUI.add("event-resize", function(e, t) {
  e.Event.define("windowresize", {
    on: e.UA.gecko && e.UA.gecko < 1.91 ? function(t, n, r) {
      n._handle = e.Event.attach("resize", function(e) {
        r.fire(e)
      })
    } : function(t, n, r) {
      var i = e.config.windowResizeDelay || 100;
      n._handle = e.Event.attach("resize", function(t) {
        n._timer && n._timer.cancel(), n._timer = e.later(i, e, function() {
          r.fire(t)
        })
      })
    },
    detach: function(e, t) {
      t._timer && t._timer.cancel(), t._handle.detach()
    }
  })
}, "@VERSION@", {
  requires: ["node-base", "event-synthetic"]
});

YUI.add("event-hover", function(e, t) {
  var n = e.Lang.isFunction,
    r = function() {},
    i = {
      processArgs: function(e) {
        var t = n(e[2]) ? 2 : 3;
        return n(e[t]) ? e.splice(t, 1)[0] : r
      },
      on: function(e, t, n, r) {
        var i = t.args ? t.args.slice() : [];
        i.unshift(null), t._detach = e[r ? "delegate" : "on"]({
          mouseenter: function(e) {
            e.phase = "over", n.fire(e)
          },
          mouseleave: function(e) {
            var n = t.context || this;
            i[0] = e, e.type = "hover", e.phase = "out", t._extra.apply(n, i)
          }
        }, r)
      },
      detach: function(e, t, n) {
        t._detach.detach()
      }
    };
  i.delegate = i.on, i.detachDelegate = i.detach, e.Event.define("hover", i)
}, "@VERSION@", {
  requires: ["event-mouseenter"]
});

YUI.add("event-outside", function(e, t) {
  var n = ["blur", "change", "click", "dblclick", "focus", "keydown", "keypress", "keyup", "mousedown", "mousemove", "mouseout", "mouseover", "mouseup", "select", "submit"];
  e.Event.defineOutside = function(t, n) {
    n = n || t + "outside";
    var r = {
      on: function(n, r, i) {
        r.handle = e.one("doc").on(t, function(e) {
          this.isOutside(n, e.target) && (e.currentTarget = n, i.fire(e))
        }, this)
      },
      detach: function(e, t, n) {
        t.handle.detach()
      },
      delegate: function(n, r, i, s) {
        r.handle = e.one("doc").delegate(t, function(e) {
          this.isOutside(n, e.target) && i.fire(e)
        }, s, this)
      },
      isOutside: function(e, t) {
        return t !== e && !t.ancestor(function(t) {
          return t === e
        })
      }
    };
    r.detachDelegate = r.detach, e.Event.define(n, r)
  }, e.Array.each(n, function(t) {
    e.Event.defineOutside(t)
  })
}, "@VERSION@", {
  requires: ["event-synthetic"]
});

YUI.add("event-touch", function(e, t) {
  var n = "scale",
    r = "rotation",
    i = "identifier",
    s = e.config.win,
    o = {};
  e.DOMEventFacade.prototype._touch = function(t, s, o) {
    var u, a, f, l, c;
    if (t.touches) {
      this.touches = [], c = {};
      for (u = 0, a = t.touches.length; u < a; ++u) l = t.touches[u], c[e.stamp(l)] = this.touches[u] = new e.DOMEventFacade(l, s, o)
    }
    if (t.targetTouches) {
      this.targetTouches = [];
      for (u = 0, a = t.targetTouches.length; u < a; ++u) l = t.targetTouches[u], f = c && c[e.stamp(l, !0)], this.targetTouches[u] = f || new e.DOMEventFacade(l, s, o)
    }
    if (t.changedTouches) {
      this.changedTouches = [];
      for (u = 0, a = t.changedTouches.length; u < a; ++u) l = t.changedTouches[u], f = c && c[e.stamp(l, !0)], this.changedTouches[u] = f || new e.DOMEventFacade(l, s, o)
    }
    n in t && (this[n] = t[n]), r in t && (this[r] = t[r]), i in t && (this[i] = t[i])
  }, e.Node.DOM_EVENTS && e.mix(e.Node.DOM_EVENTS, {
    touchstart: 1,
    touchmove: 1,
    touchend: 1,
    touchcancel: 1,
    gesturestart: 1,
    gesturechange: 1,
    gestureend: 1,
    MSPointerDown: 1,
    MSPointerUp: 1,
    MSPointerMove: 1,
    MSPointerCancel: 1,
    pointerdown: 1,
    pointerup: 1,
    pointermove: 1,
    pointercancel: 1
  }), s && "ontouchstart" in s && !(e.UA.chrome && e.UA.chrome < 6) ? (o.start = ["touchstart", "mousedown"], o.end = ["touchend", "mouseup"], o.move = ["touchmove", "mousemove"], o.cancel = ["touchcancel", "mousecancel"]) : s && s.PointerEvent ? (o.start = "pointerdown", o.end = "pointerup", o.move = "pointermove", o.cancel = "pointercancel") : s && "msPointerEnabled" in s.navigator ? (o.start = "MSPointerDown", o.end = "MSPointerUp", o.move = "MSPointerMove", o.cancel = "MSPointerCancel") : (o.start = "mousedown", o.end = "mouseup", o.move = "mousemove", o.cancel = "mousecancel"), e.Event._GESTURE_MAP = o
}, "@VERSION@", {
  requires: ["node-base"]
});

YUI.add("event-move", function(e, t) {
  var n = e.Event._GESTURE_MAP,
    r = {
      start: n.start,
      end: n.end,
      move: n.move
    },
    i = "start",
    s = "move",
    o = "end",
    u = "gesture" + s,
    a = u + o,
    f = u + i,
    l = "_msh",
    c = "_mh",
    h = "_meh",
    p = "_dmsh",
    d = "_dmh",
    v = "_dmeh",
    m = "_ms",
    g = "_m",
    y = "minTime",
    b = "minDistance",
    w = "preventDefault",
    E = "button",
    S = "ownerDocument",
    x = "currentTarget",
    T = "target",
    N = "nodeType",
    C = e.config.win && "msPointerEnabled" in e.config.win.navigator,
    k = "msTouchActionCount",
    L = "msInitTouchAction",
    A = function(t, n, r) {
      var i = r ? 4 : 3,
        s = n.length > i ? e.merge(n.splice(i, 1)[0]) : {};
      return w in s || (s[w] = t.PREVENT_DEFAULT), s
    },
    O = function(e, t) {
      return t._extra.root || e.get(N) === 9 ? e : e.get(S)
    },
    M = function(t) {
      var n = t.getDOMNode();
      return t.compareTo(e.config.doc) && n.documentElement ? n.documentElement : !1
    },
    _ = function(e, t, n) {
      e.pageX = t.pageX, e.pageY = t.pageY, e.screenX = t.screenX, e.screenY = t.screenY, e.clientX = t.clientX, e.clientY = t.clientY, e[T] = e[T] || t[T], e[x] = e[x] || t[x], e[E] = n && n[E] || 1
    },
    D = function(t) {
      var n = M(t) || t.getDOMNode(),
        r = t.getData(k);
      C && (r || (r = 0, t.setData(L, n.style.msTouchAction)), n.style.msTouchAction = e.Event._DEFAULT_TOUCH_ACTION, r++, t.setData(k, r))
    },
    P = function(e) {
      var t = M(e) || e.getDOMNode(),
        n = e.getData(k),
        r = e.getData(L);
      C && (n--, e.setData(k, n), n === 0 && t.style.msTouchAction !== r && (t.style.msTouchAction = r))
    },
    H = function(e, t) {
      t && (!t.call || t(e)) && e.preventDefault()
    },
    B = e.Event.define;
  e.Event._DEFAULT_TOUCH_ACTION = "none", B(f, {
    on: function(e, t, n) {
      D(e), t[l] = e.on(r[i], this._onStart, this, e, t, n)
    },
    delegate: function(e, t, n, s) {
      var o = this;
      t[p] = e.delegate(r[i], function(r) {
        o._onStart(r, e, t, n, !0)
      }, s)
    },
    detachDelegate: function(e, t, n, r) {
      var i = t[p];
      i && (i.detach(), t[p] = null), P(e)
    },
    detach: function(e, t, n) {
      var r = t[l];
      r && (r.detach(), t[l] = null), P(e)
    },
    processArgs: function(e, t) {
      var n = A(this, e, t);
      return y in n || (n[y] = this.MIN_TIME), b in n || (n[b] = this.MIN_DISTANCE), n
    },
    _onStart: function(t, n, i, u, a) {
      a && (n = t[x]);
      var f = i._extra,
        l = !0,
        c = f[y],
        h = f[b],
        p = f.button,
        d = f[w],
        v = O(n, i),
        m;
      t.touches ? t.touches.length === 1 ? _(t, t.touches[0], f) : l = !1 : l = p === undefined || p === t.button, l && (H(t, d), c === 0 || h === 0 ? this._start(t, n, u, f) : (m = [t.pageX, t.pageY], c > 0 && (f._ht = e.later(c, this, this._start, [t, n, u, f]), f._hme = v.on(r[o], e.bind(function() {
        this._cancel(f)
      }, this))), h > 0 && (f._hm = v.on(r[s], e.bind(function(e) {
        (Math.abs(e.pageX - m[0]) > h || Math.abs(e.pageY - m[1]) > h) && this._start(t, n, u, f)
      }, this)))))
    },
    _cancel: function(e) {
      e._ht && (e._ht.cancel(), e._ht = null), e._hme && (e._hme.detach(), e._hme = null), e._hm && (e._hm.detach(), e._hm = null)
    },
    _start: function(e, t, n, r) {
      r && this._cancel(r), e.type = f, t.setData(m, e), n.fire(e)
    },
    MIN_TIME: 0,
    MIN_DISTANCE: 0,
    PREVENT_DEFAULT: !1
  }), B(u, {
    on: function(e, t, n) {
      D(e);
      var i = O(e, t, r[s]),
        o = i.on(r[s], this._onMove, this, e, t, n);
      t[c] = o
    },
    delegate: function(e, t, n, i) {
      var o = this;
      t[d] = e.delegate(r[s], function(r) {
        o._onMove(r, e, t, n, !0)
      }, i)
    },
    detach: function(e, t, n) {
      var r = t[c];
      r && (r.detach(), t[c] = null), P(e)
    },
    detachDelegate: function(e, t, n, r) {
      var i = t[d];
      i && (i.detach(), t[d] = null), P(e)
    },
    processArgs: function(e, t) {
      return A(this, e, t)
    },
    _onMove: function(e, t, n, r, i) {
      i && (t = e[x]);
      var s = n._extra.standAlone || t.getData(m),
        o = n._extra.preventDefault;
      s && (e.touches && (e.touches.length === 1 ? _(e, e.touches[0]) : s = !1), s && (H(e, o), e.type = u, r.fire(e)))
    },
    PREVENT_DEFAULT: !1
  }), B(a, {
    on: function(e, t, n) {
      D(e);
      var i = O(e, t),
        s = i.on(r[o], this._onEnd, this, e, t, n);
      t[h] = s
    },
    delegate: function(e, t, n, i) {
      var s = this;
      t[v] = e.delegate(r[o], function(r) {
        s._onEnd(r, e, t, n, !0)
      }, i)
    },
    detachDelegate: function(e, t, n, r) {
      var i = t[v];
      i && (i.detach(), t[v] = null), P(e)
    },
    detach: function(e, t, n) {
      var r = t[h];
      r && (r.detach(), t[h] = null), P(e)
    },
    processArgs: function(e, t) {
      return A(this, e, t)
    },
    _onEnd: function(e, t, n, r, i) {
      i && (t = e[x]);
      var s = n._extra.standAlone || t.getData(g) || t.getData(m),
        o = n._extra.preventDefault;
      s && (e.changedTouches && (e.changedTouches.length === 1 ? _(e, e.changedTouches[0]) : s = !1), s && (H(e, o), e.type = a, r.fire(e), t.clearData(m), t.clearData(g)))
    },
    PREVENT_DEFAULT: !1
  })
}, "@VERSION@", {
  requires: ["node-base", "event-touch", "event-synthetic"]
});

YUI.add("event-flick", function(e, t) {
  var n = e.Event._GESTURE_MAP,
    r = {
      start: n.start,
      end: n.end,
      move: n.move
    },
    i = "start",
    s = "end",
    o = "move",
    u = "ownerDocument",
    a = "minVelocity",
    f = "minDistance",
    l = "preventDefault",
    c = "_fs",
    h = "_fsh",
    p = "_feh",
    d = "_fmh",
    v = "nodeType";
  e.Event.define("flick", {
    on: function(e, t, n) {
      var s = e.on(r[i], this._onStart, this, e, t, n);
      t[h] = s
    },
    detach: function(e, t, n) {
      var r = t[h],
        i = t[p];
      r && (r.detach(), t[h] = null), i && (i.detach(), t[p] = null)
    },
    processArgs: function(t) {
      var n = t.length > 3 ? e.merge(t.splice(3, 1)[0]) : {};
      return a in n || (n[a] = this.MIN_VELOCITY), f in n || (n[f] = this.MIN_DISTANCE), l in n || (n[l] = this.PREVENT_DEFAULT), n
    },
    _onStart: function(t, n, i, a) {
      var f = !0,
        l, h, m, g = i._extra.preventDefault,
        y = t;
      t.touches && (f = t.touches.length === 1, t = t.touches[0]), f && (g && (!g.call || g(t)) && y.preventDefault(), t.flick = {
        time: (new Date).getTime()
      }, i[c] = t, l = i[p], m = n.get(v) === 9 ? n : n.get(u), l || (l = m.on(r[s], e.bind(this._onEnd, this), null, n, i, a), i[p] = l), i[d] = m.once(r[o], e.bind(this._onMove, this), null, n, i, a))
    },
    _onMove: function(e, t, n, r) {
      var i = n[c];
      i && i.flick && (i.flick.time = (new Date).getTime())
    },
    _onEnd: function(e, t, n, r) {
      var i = (new Date).getTime(),
        s = n[c],
        o = !!s,
        u = e,
        h, p, v, m, g, y, b, w, E = n[d];
      E && (E.detach(), delete n[d]), o && (e.changedTouches && (e.changedTouches.length === 1 && e.touches.length === 0 ? u = e.changedTouches[0] : o = !1), o && (m = n._extra, v = m[l], v && (!v.call || v(e)) && e.preventDefault(), h = s.flick.time, i = (new Date).getTime(), p = i - h, g = [u.pageX - s.pageX, u.pageY - s.pageY], m.axis ? w = m.axis : w = Math.abs(g[0]) >= Math.abs(g[1]) ? "x" : "y", y = g[w === "x" ? 0 : 1], b = p !== 0 ? y / p : 0, isFinite(b) && Math.abs(y) >= m[f] && Math.abs(b) >= m[a] && (e.type = "flick", e.flick = {
        time: p,
        distance: y,
        velocity: b,
        axis: w,
        start: s
      }, r.fire(e)), n[c] = null))
    },
    MIN_VELOCITY: 0,
    MIN_DISTANCE: 0,
    PREVENT_DEFAULT: !1
  })
}, "@VERSION@", {
  requires: ["node-base", "event-touch", "event-synthetic"]
});

YUI.add("event-valuechange", function(e, t) {
  var n = "_valuechange",
    r = "value",
    i = "nodeName",
    s, o = {
      POLL_INTERVAL: 50,
      TIMEOUT: 1e4,
      _poll: function(t, r) {
        var i = t._node,
          s = r.e,
          u = t._data && t._data[n],
          a = 0,
          f, l, c, h, p, d;
        if (!i || !u) {
          o._stopPolling(t);
          return
        }
        l = u.prevVal, h = u.nodeName, u.isEditable ? c = i.innerHTML : h === "input" || h === "textarea" ? c = i.value : h === "select" && (p = i.options[i.selectedIndex], c = p.value || p.text), c !== l && (u.prevVal = c, f = {
          _event: s,
          currentTarget: s && s.currentTarget || t,
          newVal: c,
          prevVal: l,
          target: s && s.target || t
        }, e.Object.some(u.notifiers, function(e) {
          var t = e.handle.evt,
            n;
          a !== 1 ? e.fire(f) : t.el === d && e.fire(f), n = t && t._facade ? t._facade.stopped : 0, n > a && (a = n, a === 1 && (d = t.el));
          if (a === 2) return !0
        }), o._refreshTimeout(t))
      },
      _refreshTimeout: function(e, t) {
        if (!e._node) return;
        var r = e.getData(n);
        o._stopTimeout(e), r.timeout = setTimeout(function() {
          o._stopPolling(e, t)
        }, o.TIMEOUT)
      },
      _startPolling: function(t, s, u) {
        var a, f;
        if (!t.test("input,textarea,select") && !(f = o._isEditable(t))) return;
        a = t.getData(n), a || (a = {
          nodeName: t.get(i).toLowerCase(),
          isEditable: f,
          prevVal: f ? t.getDOMNode().innerHTML : t.get(r)
        }, t.setData(n, a)), a.notifiers || (a.notifiers = {});
        if (a.interval) {
          if (!u.force) {
            a.notifiers[e.stamp(s)] = s;
            return
          }
          o._stopPolling(t, s)
        }
        a.notifiers[e.stamp(s)] = s, a.interval = setInterval(function() {
          o._poll(t, u)
        }, o.POLL_INTERVAL), o._refreshTimeout(t, s)
      },
      _stopPolling: function(t, r) {
        if (!t._node) return;
        var i = t.getData(n) || {};
        clearInterval(i.interval), delete i.interval, o._stopTimeout(t), r ? i.notifiers && delete i.notifiers[e.stamp(r)] : i.notifiers = {}
      },
      _stopTimeout: function(e) {
        var t = e.getData(n) || {};
        clearTimeout(t.timeout), delete t.timeout
      },
      _isEditable: function(e) {
        var t = e._node;
        return t.contentEditable === "true" || t.contentEditable === ""
      },
      _onBlur: function(e, t) {
        o._stopPolling(e.currentTarget, t)
      },
      _onFocus: function(e, t) {
        var s = e.currentTarget,
          u = s.getData(n);
        u || (u = {
          isEditable: o._isEditable(s),
          nodeName: s.get(i).toLowerCase()
        }, s.setData(n, u)), u.prevVal = u.isEditable ? s.getDOMNode().innerHTML : s.get(r), o._startPolling(s, t, {
          e: e
        })
      },
      _onKeyDown: function(e, t) {
        o._startPolling(e.currentTarget, t, {
          e: e
        })
      },
      _onKeyUp: function(e, t) {
        (e.charCode === 229 || e.charCode === 197) && o._startPolling(e.currentTarget, t, {
          e: e,
          force: !0
        })
      },
      _onMouseDown: function(e, t) {
        o._startPolling(e.currentTarget, t, {
          e: e
        })
      },
      _onSubscribe: function(t, s, u, a) {
        var f, l, c, h, p;
        l = {
          blur: o._onBlur,
          focus: o._onFocus,
          keydown: o._onKeyDown,
          keyup: o._onKeyUp,
          mousedown: o._onMouseDown
        }, f = u._valuechange = {};
        if (a) f.delegated = !0, f.getNodes = function() {
          return h = t.all("input,textarea,select").filter(a), p = t.all('[contenteditable="true"],[contenteditable=""]').filter(a), h.concat(p)
        }, f.getNodes().each(function(e) {
          e.getData(n) || e.setData(n, {
            nodeName: e.get(i).toLowerCase(),
            isEditable: o._isEditable(e),
            prevVal: c ? e.getDOMNode().innerHTML : e.get(r)
          })
        }), u._handles = e.delegate(l, t, a, null, u);
        else {
          c = o._isEditable(t);
          if (!t.test("input,textarea,select") && !c) return;
          t.getData(n) || t.setData(n, {
            nodeName: t.get(i).toLowerCase(),
            isEditable: c,
            prevVal: c ? t.getDOMNode().innerHTML : t.get(r)
          }), u._handles = t.on(l, null, null, u)
        }
      },
      _onUnsubscribe: function(e, t, n) {
        var r = n._valuechange;
        n._handles && n._handles.detach(), r.delegated ? r.getNodes().each(function(e) {
          o._stopPolling(e, n)
        }) : o._stopPolling(e, n)
      }
    };
  s = {
    detach: o._onUnsubscribe,
    on: o._onSubscribe,
    delegate: o._onSubscribe,
    detachDelegate: o._onUnsubscribe,
    publishConfig: {
      emitFacade: !0
    }
  }, e.Event.define("valuechange", s), e.Event.define("valueChange", s), e.ValueChange = o
}, "@VERSION@", {
  requires: ["event-focus", "event-synthetic"]
});

YUI.add("event-tap", function(e, t) {
  function a(t, n) {
    n = n || e.Object.values(u), e.Array.each(n, function(e) {
      var n = t[e];
      n && (n.detach(), t[e] = null)
    })
  }
  var n = e.config.doc,
    r = e.Event._GESTURE_MAP,
    i = r.start,
    s = "tap",
    o = /pointer/i,
    u = {
      START: "Y_TAP_ON_START_HANDLE",
      END: "Y_TAP_ON_END_HANDLE",
      CANCEL: "Y_TAP_ON_CANCEL_HANDLE"
    };
  e.Event.define(s, {
    publishConfig: {
      preventedFn: function(e) {
        var t = e.target.once("click", function(e) {
          e.preventDefault()
        });
        setTimeout(function() {
          t.detach()
        }, 100)
      }
    },
    processArgs: function(e, t) {
      if (!t) {
        var n = e[3];
        return e.splice(3, 1), n
      }
    },
    on: function(e, t, n) {
      t[u.START] = e.on(i, this._start, this, e, t, n)
    },
    detach: function(e, t, n) {
      a(t)
    },
    delegate: function(t, n, r, s) {
      n[u.START] = e.delegate(i, function(e) {
        this._start(e, t, n, r, !0)
      }, t, s, this)
    },
    detachDelegate: function(e, t, n) {
      a(t)
    },
    _start: function(e, t, n, i, s) {
      var a = {
          canceled: !1,
          eventType: e.type
        },
        f = n.preventMouse || !1;
      if (e.button && e.button === 3) return;
      if (e.touches && e.touches.length !== 1) return;
      a.node = s ? e.currentTarget : t, e.touches ? a.startXY = [e.touches[0].pageX, e.touches[0].pageY] : a.startXY = [e.pageX, e.pageY], e.touches ? (n[u.END] = t.once("touchend", this._end, this, t, n, i, s, a), n[u.CANCEL] = t.once("touchcancel", this.detach, this, t, n, i, s, a), n.preventMouse = !0) : a.eventType.indexOf("mouse") !== -1 && !f ? (n[u.END] = t.once("mouseup", this._end, this, t, n, i, s, a), n[u.CANCEL] = t.once("mousecancel", this.detach, this, t, n, i, s, a)) : a.eventType.indexOf("mouse") !== -1 && f ? n.preventMouse = !1 : o.test(a.eventType) && (n[u.END] = t.once(r.end, this._end, this, t, n, i, s, a), n[u.CANCEL] = t.once(r.cancel, this.detach, this, t, n, i, s, a))
    },
    _end: function(e, t, n, r, i, o) {
      var f = o.startXY,
        l, c, h = 15;
      n._extra && n._extra.sensitivity >= 0 && (h = n._extra.sensitivity), e.changedTouches ? (l = [e.changedTouches[0].pageX, e.changedTouches[0].pageY], c = [e.changedTouches[0].clientX, e.changedTouches[0].clientY]) : (l = [e.pageX, e.pageY], c = [e.clientX, e.clientY]), Math.abs(l[0] - f[0]) <= h && Math.abs(l[1] - f[1]) <= h && (e.type = s, e.pageX = l[0], e.pageY = l[1], e.clientX = c[0], e.clientY = c[1], e.currentTarget = o.node, r.fire(e)), a(n, [u.END, u.CANCEL])
    }
  })
}, "@VERSION@", {
  requires: ["node-base", "event-base", "event-touch", "event-synthetic"]
});

YUI.add("array-extras", function(e, t) {
  var n = e.Array,
    r = e.Lang,
    i = Array.prototype;
  n.lastIndexOf = r._isNative(i.lastIndexOf) ? function(e, t, n) {
    return n || n === 0 ? e.lastIndexOf(t, n) : e.lastIndexOf(t)
  } : function(e, t, n) {
    var r = e.length,
      i = r - 1;
    if (n || n === 0) i = Math.min(n < 0 ? r + n : n, r);
    if (i > -1 && r > 0)
      for (; i > -1; --i)
        if (i in e && e[i] === t) return i;
    return -1
  }, n.unique = function(e, t) {
    var n = 0,
      r = e.length,
      i = [],
      s, o, u, a;
    e: for (; n < r; n++) {
      a = e[n];
      for (s = 0, u = i.length; s < u; s++) {
        o = i[s];
        if (t) {
          if (t.call(e, a, o, n, e)) continue e
        } else if (a === o) continue e
      }
      i.push(a)
    }
    return i
  }, n.filter = r._isNative(i.filter) ? function(e, t, n) {
    return i.filter.call(e, t, n)
  } : function(e, t, n) {
    var r = 0,
      i = e.length,
      s = [],
      o;
    for (; r < i; ++r) r in e && (o = e[r], t.call(n, o, r, e) && s.push(o));
    return s
  }, n.reject = function(e, t, r) {
    return n.filter(e, function(e, n, i) {
      return !t.call(r, e, n, i)
    })
  }, n.every = r._isNative(i.every) ? function(e, t, n) {
    return i.every.call(e, t, n)
  } : function(e, t, n) {
    for (var r = 0, i = e.length; r < i; ++r)
      if (r in e && !t.call(n, e[r], r, e)) return !1;
    return !0
  }, n.map = r._isNative(i.map) ? function(e, t, n) {
    return i.map.call(e, t, n)
  } : function(e, t, n) {
    var r = 0,
      s = e.length,
      o = i.concat.call(e);
    for (; r < s; ++r) r in e && (o[r] = t.call(n, e[r], r, e));
    return o
  }, n.reduce = r._isNative(i.reduce) ? function(e, t, n, r) {
    return i.reduce.call(e, function(e, t, i, s) {
      return n.call(r, e, t, i, s)
    }, t)
  } : function(e, t, n, r) {
    var i = 0,
      s = e.length,
      o = t;
    for (; i < s; ++i) i in e && (o = n.call(r, o, e[i], i, e));
    return o
  }, n.find = function(e, t, n) {
    for (var r = 0, i = e.length; r < i; r++)
      if (r in e && t.call(n, e[r], r, e)) return e[r];
    return null
  }, n.grep = function(e, t) {
    return n.filter(e, function(e, n) {
      return t.test(e)
    })
  }, n.partition = function(e, t, r) {
    var i = {
      matches: [],
      rejects: []
    };
    return n.each(e, function(n, s) {
      var u = t.call(r, n, s, e) ? i.matches : i.rejects;
      u.push(n)
    }), i
  }, n.zip = function(e, t) {
    var r = [];
    return n.each(e, function(e, n) {
      r.push([e, t[n]])
    }), r
  }, n.flatten = function(e) {
    var t = [],
      i, s, o;
    if (!e) return t;
    for (i = 0, s = e.length; i < s; ++i) o = e[i], r.isArray(o) ? t.push.apply(t, n.flatten(o)) : t.push(o);
    return t
  }
}, "@VERSION@", {
  requires: ["yui-base"]
});

YUI.add("selector-css2", function(e, t) {
  var n = "parentNode",
    r = "tagName",
    i = "attributes",
    s = "combinator",
    o = "pseudos",
    u = e.Selector,
    a = {
      _reRegExpTokens: /([\^\$\?\[\]\*\+\-\.\(\)\|\\])/,
      SORT_RESULTS: !0,
      _isXML: function() {
        var t = e.config.doc.createElement("div").tagName !== "DIV";
        return t
      }(),
      shorthand: {
        "\\#(-?[_a-z0-9]+[-\\w\\uE000]*)": "[id=$1]",
        "\\.(-?[_a-z]+[-\\w\\uE000]*)": "[className~=$1]"
      },
      operators: {
        "": function(t, n) {
          return e.DOM.getAttribute(t, n) !== ""
        },
        "~=": "(?:^|\\s+){val}(?:\\s+|$)",
        "|=": "^{val}-?"
      },
      pseudos: {
        "first-child": function(t) {
          return e.DOM._children(t[n])[0] === t
        }
      },
      _bruteQuery: function(t, n, r) {
        var i = [],
          s = [],
          o, a = u._tokenize(t),
          f = a[a.length - 1],
          l = e.DOM._getDoc(n),
          c, h, p, d, v;
        if (f) {
          h = f.id, p = f.className, d = f.tagName || "*";
          if (n.getElementsByTagName) h && (n.all || n.nodeType === 9 || e.DOM.inDoc(n)) ? s = e.DOM.allById(h, n) : p ? s = n.getElementsByClassName(p) : s = n.getElementsByTagName(d);
          else {
            o = [], c = n.firstChild, v = d === "*";
            while (c) {
              while (c) c.tagName > "@" && (v || c.tagName === d) && s.push(c), o.push(c), c = c.firstChild;
              while (o.length > 0 && !c) c = o.pop().nextSibling
            }
          }
          s.length && (i = u._filterNodes(s, a, r))
        }
        return i
      },
      _filterNodes: function(t, n, r) {
        var i = 0,
          s, o = n.length,
          a = o - 1,
          f = [],
          l = t[0],
          c = l,
          h = e.Selector.getters,
          p, d, v, m, g, y, b, w;
        for (i = 0; c = l = t[i++];) {
          a = o - 1, m = null;
          e: while (c && c.tagName) {
            v = n[a], b = v.tests, s = b.length;
            if (s && !g)
              while (w = b[--s]) {
                p = w[1], h[w[0]] ? y = h[w[0]](c, w[0]) : (y = c[w[0]], w[0] === "tagName" && !u._isXML && (y = y.toUpperCase()), typeof y != "string" && y !== undefined && y.toString ? y = y.toString() : y === undefined && c.getAttribute && (y = c.getAttribute(w[0], 2)));
                if (p === "=" && y !== w[2] || typeof p != "string" && p.test && !p.test(y) || !p.test && typeof p == "function" && !p(c, w[0], w[2])) {
                  if (c = c[m])
                    while (c && (!c.tagName || v.tagName && v.tagName !== c.tagName)) c = c[m];
                  continue e
                }
              }
            a--;
            if (!!g || !(d = v.combinator)) {
              f.push(l);
              if (r) return f;
              break
            }
            m = d.axis, c = c[m];
            while (c && !c.tagName) c = c[m];
            d.direct && (m = null)
          }
        }
        return l = c = null, f
      },
      combinators: {
        " ": {
          axis: "parentNode"
        },
        ">": {
          axis: "parentNode",
          direct: !0
        },
        "+": {
          axis: "previousSibling",
          direct: !0
        }
      },
      _parsers: [{
        name: i,
        re: /^\uE003(-?[a-z]+[\w\-]*)+([~\|\^\$\*!=]=?)?['"]?([^\uE004'"]*)['"]?\uE004/i,
        fn: function(t, n) {
          var r = t[2] || "",
            i = u.operators,
            s = t[3] ? t[3].replace(/\\/g, "") : "",
            o;
          if (t[1] === "id" && r === "=" || t[1] === "className" && e.config.doc.documentElement.getElementsByClassName && (r === "~=" || r === "=")) n.prefilter = t[1], t[3] = s, n[t[1]] = t[1] === "id" ? t[3] : s;
          r in i && (o = i[r], typeof o == "string" && (t[3] = s.replace(u._reRegExpTokens, "\\$1"), o = new RegExp(o.replace("{val}", t[3]))), t[2] = o);
          if (!n.last || n.prefilter !== t[1]) return t.slice(1)
        }
      }, {
        name: r,
        re: /^((?:-?[_a-z]+[\w-]*)|\*)/i,
        fn: function(e, t) {
          var n = e[1];
          u._isXML || (n = n.toUpperCase()), t.tagName = n;
          if (n !== "*" && (!t.last || t.prefilter)) return [r, "=", n];
          t.prefilter || (t.prefilter = "tagName")
        }
      }, {
        name: s,
        re: /^\s*([>+~]|\s)\s*/,
        fn: function(e, t) {}
      }, {
        name: o,
        re: /^:([\-\w]+)(?:\uE005['"]?([^\uE005]*)['"]?\uE006)*/i,
        fn: function(e, t) {
          var n = u[o][e[1]];
          return n ? (e[2] && (e[2] = e[2].replace(/\\/g, "")), [e[2], n]) : !1
        }
      }],
      _getToken: function(e) {
        return {
          tagName: null,
          id: null,
          className: null,
          attributes: {},
          combinator: null,
          tests: []
        }
      },
      _tokenize: function(t) {
        t = t || "", t = u._parseSelector(e.Lang.trim(t));
        var n = u._getToken(),
          r = t,
          i = [],
          o = !1,
          a, f, l, c;
        e: do {
          o = !1;
          for (l = 0; c = u._parsers[l++];)
            if (a = c.re.exec(t)) {
              c.name !== s && (n.selector = t), t = t.replace(a[0], ""), t.length || (n.last = !0), u._attrFilters[a[1]] && (a[1] = u._attrFilters[a[1]]), f = c.fn(a, n);
              if (f === !1) {
                o = !1;
                break e
              }
              f && n.tests.push(f);
              if (!t.length || c.name === s) i.push(n), n = u._getToken(n), c.name === s && (n.combinator = e.Selector.combinators[a[1]]);
              o = !0
            }
        } while (o && t.length);
        if (!o || t.length) i = [];
        return i
      },
      _replaceMarkers: function(e) {
        return e = e.replace(/\[/g, "\ue003"), e = e.replace(/\]/g, "\ue004"), e = e.replace(/\(/g, "\ue005"), e = e.replace(/\)/g, "\ue006"), e
      },
      _replaceShorthand: function(t) {
        var n = e.Selector.shorthand,
          r;
        for (r in n) n.hasOwnProperty(r) && (t = t.replace(new RegExp(r, "gi"), n[r]));
        return t
      },
      _parseSelector: function(t) {
        var n = e.Selector._replaceSelector(t),
          t = n.selector;
        return t = e.Selector._replaceShorthand(t), t = e.Selector._restore("attr", t, n.attrs), t = e.Selector._restore("pseudo", t, n.pseudos), t = e.Selector._replaceMarkers(t), t = e.Selector._restore("esc", t, n.esc), t
      },
      _attrFilters: {
        "class": "className",
        "for": "htmlFor"
      },
      getters: {
        href: function(t, n) {
          return e.DOM.getAttribute(t, n)
        },
        id: function(t, n) {
          return e.DOM.getId(t)
        }
      }
    };
  e.mix(e.Selector, a, !0), e.Selector.getters.src = e.Selector.getters.rel = e.Selector.getters.href, e.Selector.useNative && e.config.doc.querySelector && (e.Selector.shorthand["\\.(-?[_a-z]+[-\\w]*)"] = "[class~=$1]")
}, "@VERSION@", {
  requires: ["selector-native"]
});

YUI.add("selector-css3", function(e, t) {
  e.Selector._reNth = /^(?:([\-]?\d*)(n){1}|(odd|even)$)*([\-+]?\d*)$/, e.Selector._getNth = function(t, n, r, i) {
    e.Selector._reNth.test(n);
    var s = parseInt(RegExp.$1, 10),
      o = RegExp.$2,
      u = RegExp.$3,
      a = parseInt(RegExp.$4, 10) || 0,
      f = [],
      l = e.DOM._children(t.parentNode, r),
      c;
    u ? (s = 2, c = "+", o = "n", a = u === "odd" ? 1 : 0) : isNaN(s) && (s = o ? 1 : 0);
    if (s === 0) return i && (a = l.length - a + 1), l[a - 1] === t ? !0 : !1;
    s < 0 && (i = !!i, s = Math.abs(s));
    if (!i) {
      for (var h = a - 1, p = l.length; h < p; h += s)
        if (h >= 0 && l[h] === t) return !0
    } else
      for (var h = l.length - a, p = l.length; h >= 0; h -= s)
        if (h < p && l[h] === t) return !0;
    return !1
  }, e.mix(e.Selector.pseudos, {
    root: function(e) {
      return e === e.ownerDocument.documentElement
    },
    "nth-child": function(t, n) {
      return e.Selector._getNth(t, n)
    },
    "nth-last-child": function(t, n) {
      return e.Selector._getNth(t, n, null, !0)
    },
    "nth-of-type": function(t, n) {
      return e.Selector._getNth(t, n, t.tagName)
    },
    "nth-last-of-type": function(t, n) {
      return e.Selector._getNth(t, n, t.tagName, !0)
    },
    "last-child": function(t) {
      var n = e.DOM._children(t.parentNode);
      return n[n.length - 1] === t
    },
    "first-of-type": function(t) {
      return e.DOM._children(t.parentNode, t.tagName)[0] === t
    },
    "last-of-type": function(t) {
      var n = e.DOM._children(t.parentNode, t.tagName);
      return n[n.length - 1] === t
    },
    "only-child": function(t) {
      var n = e.DOM._children(t.parentNode);
      return n.length === 1 && n[0] === t
    },
    "only-of-type": function(t) {
      var n = e.DOM._children(t.parentNode, t.tagName);
      return n.length === 1 && n[0] === t
    },
    empty: function(e) {
      return e.childNodes.length === 0
    },
    not: function(t, n) {
      return !e.Selector.test(t, n)
    },
    contains: function(e, t) {
      var n = e.innerText || e.textContent || "";
      return n.indexOf(t) > -1
    },
    checked: function(e) {
      return e.checked === !0 || e.selected === !0
    },
    enabled: function(e) {
      return e.disabled !== undefined && !e.disabled
    },
    disabled: function(e) {
      return e.disabled
    }
  }), e.mix(e.Selector.operators, {
    "^=": "^{val}",
    "$=": "{val}$",
    "*=": "{val}"
  }), e.Selector.combinators["~"] = {
    axis: "previousSibling"
  }
}, "@VERSION@", {
  requires: ["selector-native", "selector-css2"]
});