// Dypdykk konto-API (Netlify Function + Netlify Blobs).
// POST /api/register {user, pass}   POST /api/login {user, pass}
// GET  /api/me                      POST /api/save {items:{key:value}}   (Authorization: Bearer <token>)
// Passord lagres aldri i klartekst (scrypt med salt). Ingen e-post eller andre persondata lagres.
import crypto from "node:crypto";

let _store = null;
export function _setStore(s) { _store = s; }            // brukes av testene
async function store() {
  if (_store) return _store;
  const { getStore } = await import("@netlify/blobs");
  return (_store = getStore({ name: "dypdykk-kontoer", consistency: "strong" }));
}

const json = (status, body) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const norm = u => String(u || "").trim().toLowerCase();
const USER_RE = /^[a-zA-Z0-9æøåÆØÅ._-]{3,20}$/;
const KEY_RE = /^dypdykk-(\d{4}-\d\d-\d\d|arkiv-\d{4}-\d\d-\d\d|stats|buddy|buddies-extra|name|endless-best|venner|settings|pack-[a-z0-9-]+)$/;
const DAY_RE = /^dypdykk-(arkiv-)?\d{4}-\d\d-\d\d$/;
const MAX_BYTES = 3_000_000;

async function secret(s) {
  let v = await s.get("meta/secret");
  if (!v) { v = crypto.randomBytes(32).toString("hex"); await s.set("meta/secret", v); }
  return v;
}
const b64 = x => Buffer.from(x).toString("base64url");
async function makeToken(s, u) {
  const body = b64(JSON.stringify({ u, exp: Date.now() + 180 * 864e5 }));
  const sig = crypto.createHmac("sha256", await secret(s)).update(body).digest("base64url");
  return body + "." + sig;
}
async function readToken(s, req) {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  const [body, sig] = t.split(".");
  if (!body || !sig) return null;
  const want = crypto.createHmac("sha256", await secret(s)).update(body).digest("base64url");
  if (want.length !== sig.length || !crypto.timingSafeEqual(Buffer.from(want), Buffer.from(sig))) return null;
  try { const p = JSON.parse(Buffer.from(body, "base64url").toString()); return p.exp > Date.now() ? p.u : null; } catch { return null; }
}
const hashPw = (pw, salt) => new Promise((ok, bad) =>
  crypto.scrypt(pw, salt, 64, { N: 16384, r: 8, p: 1 }, (e, k) => e ? bad(e) : ok(k.toString("hex"))));

// Slår sammen lagrede verdier. Et dykk som allerede er lagret, blir aldri overskrevet.
export function merge(old, inc) {
  const out = { ...old };
  for (const [k, v] of Object.entries(inc || {})) {
    if (!KEY_RE.test(k) || v === null || v === undefined) continue;
    if (DAY_RE.test(k)) { if (!(k in out)) out[k] = v; continue; }
    if (k === "dypdykk-stats" && out[k] && typeof v === "object") {
      const a = out[k], m = { ...a, ...v };
      for (const f of ["played", "best", "bestStreak"]) m[f] = Math.max(a[f] || 0, v[f] || 0);
      if ((a.lastDaily || "") > (v.lastDaily || "")) { m.lastDaily = a.lastDaily; m.streak = a.streak; }
      out[k] = m; continue;
    }
    if (k === "dypdykk-endless-best") { out[k] = Math.max(+out[k] || 0, +v || 0); continue; }
    if (k.startsWith("dypdykk-pack-") && out[k] && typeof v === "object" && typeof out[k] === "object") { out[k] = { ...out[k], ...v }; continue; }
    out[k] = v;
  }
  return out;
}

export default async (req) => {
  const s = await store();
  const path = new URL(req.url).pathname.replace(/^\/api\/?/, "").replace(/\/$/, "");
  let body = {};
  if (req.method === "POST") {
    const txt = await req.text();
    if (txt.length > MAX_BYTES) return json(413, { error: "For mye data" });
    try { body = JSON.parse(txt || "{}"); } catch { return json(400, { error: "Ugyldig forespørsel" }); }
  }

  // Avviste svar (anonymt): bare spørsmåls-id, svarteksten og en teller per dag. Ingen bruker, IP eller tidspunkt lagres.
  // Brukes til å finne riktige svar og stavemåter som mangler.
  if (path === "avvist" && req.method === "POST") {
    const q = String(body.q || ""), a = String(body.a || "").replace(/[\u0000-\u001f<>]/g, "").trim().toLowerCase().slice(0, 40);
    if (!/^[a-z0-9-]{1,40}$/.test(q) || a.length < 2) return json(400, { error: "Ugyldig" });
    const key = "avvist/" + new Date().toISOString().slice(0, 10);
    const d = (await s.get(key, { type: "json" })) || { n: 0, q: {} };
    const m = d.q[q] || (d.q[q] = {});
    if (m[a] || d.n < 20000) { if (!m[a]) d.n++; m[a] = (m[a] || 0) + 1; await s.setJSON(key, d); }
    if (d.n === 1) await s.delete("avvist/" + new Date(Date.now() - 91 * 864e5).toISOString().slice(0, 10));   // tellinger eldre enn 90 dager slettes
    return json(200, { ok: true });
  }
  if (path === "avvist-sammendrag" && req.method === "GET") {
    const days = Math.min(31, Math.max(1, +new URL(req.url).searchParams.get("dager") || 7)), out = {};
    for (let i = 0; i < days; i++) {
      const key = "avvist/" + new Date(Date.now() - i * 864e5).toISOString().slice(0, 10);
      const d = await s.get(key, { type: "json" }); if (!d) continue;
      for (const [q, m] of Object.entries(d.q)) { const o = out[q] || (out[q] = {}); for (const [a, c] of Object.entries(m)) o[a] = (o[a] || 0) + c; }
    }
    return json(200, { dager: days, avvist: out });
  }

  if (path === "register" && req.method === "POST") {
    const name = String(body.user || "").trim(), u = norm(name), pw = String(body.pass || "");
    if (!USER_RE.test(name)) return json(400, { error: "Brukernavnet må ha 3–20 tegn: bokstaver, tall, punktum, bindestrek eller understrek." });
    if (pw.length < 6 || pw.length > 200) return json(400, { error: "Passordet må ha minst 6 tegn." });
    if (await s.get("u/" + u)) return json(409, { error: "Brukernavnet er tatt." });
    const salt = crypto.randomBytes(16).toString("hex");
    await s.setJSON("u/" + u, { name, salt, hash: await hashPw(pw, salt), created: new Date().toISOString(), fails: 0 });
    const data = merge({}, body.items);
    await s.setJSON("d/" + u, { items: data, updated: new Date().toISOString() });
    return json(200, { token: await makeToken(s, u), user: name, items: data });
  }

  if (path === "login" && req.method === "POST") {
    const u = norm(body.user), acc = await s.get("u/" + u, { type: "json" });
    if (!acc) return json(401, { error: "Feil brukernavn eller passord." });
    if (acc.lockUntil && acc.lockUntil > Date.now()) return json(429, { error: "For mange forsøk. Prøv igjen om noen minutter." });
    const h = await hashPw(String(body.pass || ""), acc.salt);
    if (!crypto.timingSafeEqual(Buffer.from(h), Buffer.from(acc.hash))) {
      acc.fails = (acc.fails || 0) + 1;
      if (acc.fails >= 8) { acc.lockUntil = Date.now() + 15 * 60e3; acc.fails = 0; }
      await s.setJSON("u/" + u, acc);
      return json(401, { error: "Feil brukernavn eller passord." });
    }
    if (acc.fails || acc.lockUntil) { acc.fails = 0; delete acc.lockUntil; await s.setJSON("u/" + u, acc); }
    const d = (await s.get("d/" + u, { type: "json" })) || { items: {} };
    const items = merge(d.items, body.items);
    await s.setJSON("d/" + u, { items, updated: new Date().toISOString() });
    return json(200, { token: await makeToken(s, u), user: acc.name, items });
  }

  const u = await readToken(s, req);
  if (!u) return json(401, { error: "Du er logget ut. Logg inn på nytt." });
  const acc = await s.get("u/" + u, { type: "json" });
  if (!acc) return json(401, { error: "Kontoen finnes ikke lenger." });

  if (path === "me" && req.method === "GET") {
    const d = (await s.get("d/" + u, { type: "json" })) || { items: {} };
    return json(200, { user: acc.name, items: d.items, updated: d.updated || null });
  }
  if (path === "save" && req.method === "POST") {
    const d = (await s.get("d/" + u, { type: "json" })) || { items: {} };
    const items = merge(d.items, body.items);
    if (JSON.stringify(items).length > MAX_BYTES) return json(413, { error: "Kontoen er full." });
    await s.setJSON("d/" + u, { items, updated: new Date().toISOString() });
    return json(200, { user: acc.name, items });
  }
  if (path === "delete" && req.method === "POST") {
    const h = await hashPw(String(body.pass || ""), acc.salt);
    if (!crypto.timingSafeEqual(Buffer.from(h), Buffer.from(acc.hash))) return json(401, { error: "Feil passord." });
    await s.delete("u/" + u); await s.delete("d/" + u);
    return json(200, { ok: true });
  }
  return json(404, { error: "Ukjent forespørsel" });
};

export const config = { path: "/api/*" };
