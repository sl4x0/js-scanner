"use strict";
fetch(`/pita/v1/gs?container=${window.appName}`).then((t => t.json().then((({
  scripts: s,
  msg: e
}) => ({
  scripts: s,
  msg: e,
  status: t.status
}))))).then((({
  scripts: t,
  msg: s,
  status: e
}) => {
  if (500 === e) throw new Error(s || "unknown error");
  t.forEach((t => {
    const s = document.createElement("script");
    s.setAttribute("src", t), document.body.append(s)
  }))
})).catch((t => {
  console.log(t)
}));