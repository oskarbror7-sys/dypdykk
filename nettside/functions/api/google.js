// Cloudflare Pages Function: «Fortsett med Google».
// Nettleseren får et ID-token fra Google. Her sjekker vi at tokenet er ekte (signatur, utsteder, mottaker, utløp),
// og gjør det om til en vanlig Dypdykk-konto i konto-API-et (Netlify), uten at brukeren trenger passord.
//   brukernavn = "g-" + HMAC(hemmelighet, Google-ID)   (Google-ID-en kan ikke leses ut av brukernavnet)
//   passord    = HMAC(hemmelighet, brukernavn)         (kjent bare av denne funksjonen)
// Vi lagrer verken e-post eller navn; fornavnet sendes bare tilbake til nettleseren for visning.
// Miljøvariabler (Cloudflare Pages → Settings → Variables): GOOGLE_CLIENT_ID og GOOGLE_PW_SECRET (hemmelig).

const ISS = ["accounts.google.com", "https://accounts.google.com"];
let JWKS = null, JWKS_AT = 0;

const json = (status, body) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const enc = new TextEncoder();
const b64u = s => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4)), c => c.charCodeAt(0));

async function hmac(secret, msg) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", k, enc.encode(msg)));
}
const B32 = "abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes) { let bits = 0, val = 0, out = "";
  for (const b of bytes) { val = (val << 8) | b; bits += 8; while (bits >= 5) { out += B32[(val >>> (bits - 5)) & 31]; bits -= 5; } }
  return out; }
const hex = bytes => [...bytes].map(b => b.toString(16).padStart(2, "0")).join("");

async function keys(env) {
  if (env.__JWKS) return env.__JWKS;                                  // brukes av testene
  if (JWKS && Date.now() - JWKS_AT < 3600e3) return JWKS;
  const r = await fetch("https://www.googleapis.com/oauth2/v3/certs");
  JWKS = (await r.json()).keys; JWKS_AT = Date.now(); return JWKS;
}

export async function verifyGoogle(token, env) {
  const parts = String(token || "").split(".");
  if (parts.length !== 3) throw new Error("Ugyldig innlogging fra Google.");
  const head = JSON.parse(new TextDecoder().decode(b64u(parts[0])));
  const body = JSON.parse(new TextDecoder().decode(b64u(parts[1])));
  const jwk = (await keys(env)).find(k => k.kid === head.kid);
  if (!jwk || head.alg !== "RS256") throw new Error("Ugyldig innlogging fra Google.");
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const ok = await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, b64u(parts[2]), enc.encode(parts[0] + "." + parts[1]));
  if (!ok) throw new Error("Ugyldig innlogging fra Google.");
  if (!ISS.includes(body.iss) || body.aud !== env.GOOGLE_CLIENT_ID) throw new Error("Innloggingen var ikke ment for Dypdykk.");
  if (!body.exp || body.exp * 1000 < Date.now() - 60e3) throw new Error("Innloggingen er utløpt. Prøv igjen.");
  if (!body.sub) throw new Error("Ugyldig innlogging fra Google.");
  return body;
}

export async function credentialsFor(sub, secret) {
  const user = "g-" + base32(await hmac(secret, "bruker:" + sub)).slice(0, 16);
  const pass = hex(await hmac(secret, "passord:" + user)).slice(0, 48);
  return { user, pass };
}

async function callApi(env, path, body, token) {
  const origin = env.API_ORIGIN || "https://dypdykk.netlify.app";
  const headers = { "content-type": "application/json" };
  if (token) headers.authorization = "Bearer " + token;
  const r = await fetch(origin + "/api/" + path, { method: body ? "POST" : "GET", headers, body: body ? JSON.stringify(body) : undefined, redirect: "manual" });
  let j = {}; try { j = await r.json(); } catch (e) {}
  return { status: r.status, j };
}

export async function onRequestPost({ request, env }) {
  if (!env.GOOGLE_CLIENT_ID || !env.GOOGLE_PW_SECRET) return json(503, { error: "Google-innlogging er ikke satt opp ennå." });
  let body = {};
  try { body = await request.json(); } catch (e) { return json(400, { error: "Ugyldig forespørsel" }); }

  // Slette en Google-konto: krever gyldig innlogging (token), passordet regner vi ut selv
  if (body.action === "delete") {
    const token = (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
    const me = await callApi(env, "me", null, token);
    if (me.status !== 200 || !/^g-[a-z2-7]{16}$/.test(String(me.j.user || ""))) return json(401, { error: "Du er logget ut. Logg inn på nytt." });
    const pass = hex(await hmac(env.GOOGLE_PW_SECRET, "passord:" + me.j.user)).slice(0, 48);
    const del = await callApi(env, "delete", { pass }, token);
    return json(del.status, del.j);
  }

  let g;
  try { g = await verifyGoogle(body.credential, env); } catch (e) { return json(401, { error: /^(Ugyldig|Innloggingen)/.test(e.message) ? e.message : "Ugyldig innlogging fra Google." }); }
  const { user, pass } = await credentialsFor(g.sub, env.GOOGLE_PW_SECRET);
  const items = body.items || {};
  let r = await callApi(env, "login", { user, pass, items });
  let fresh = false;
  if (r.status === 401) { r = await callApi(env, "register", { user, pass, items }); fresh = true; }
  if (r.status !== 200) return json(r.status, { error: r.j.error || "Innloggingen feilet. Prøv igjen." });
  return json(200, { ...r.j, display: g.given_name || g.name || "Google-bruker", google: true, fresh });
}
