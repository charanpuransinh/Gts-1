
"use strict";
async function getJSON(path) {
  const r = await fetch(path);
  const d = await r.json();
  if (!r.ok) throw new Error(d.error || ("HTTP " + r.status));
  return d;
}
async function refresh() {
  try {
    const h = await getJSON("http://127.0.0.1:8765/health");
    document.querySelector("#health").textContent =
      "Health: " + h.status + " | " + h.system + " | " + h.component;
    const m = await getJSON("http://127.0.0.1:8765/market/status");
    document.querySelector("#market").textContent =
      "Market: " + m.exchange + " | " + m.state + " | Feed: " + m.feed_status;
    const t = await getJSON("http://127.0.0.1:8765/market/tick?symbol=NIFTY");
    document.querySelector("#tick").textContent =
      "NIFTY LTP: " + t.ltp + " | Volume: " + t.volume;
  } catch (e) {
    document.querySelector("#health").textContent = "API error: " + e.message;
  }
}
refresh();
setInterval(refresh, 2000);
