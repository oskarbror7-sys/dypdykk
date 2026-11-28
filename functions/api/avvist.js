// Anonym telling av svar som ikke ble godkjent (Cloudflare Pages Function + D1).
// Lagrer bare dag, spørsmåls-id, svartekst og et antall. Ingen bruker, IP eller klokkeslett.
// POST /api/avvist {q, a}
// GET  /api/avvist?dager=7  -> {dager, avvist: {q: {svar: antall}}}
const json = (status, body) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const SKJEMA = "CREATE TABLE IF NOT EXISTS avvist (dag TEXT NOT NULL, q TEXT NOT NULL, a TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 1, PRIMARY KEY (dag, q, a))";
const dagFor = ms => new Date(ms).toISOString().slice(0, 10);

async function run(db, fn) {
  try { return await fn(); }
  catch (e) { if (/no such table/i.test(String(e))) { await db.prepare(SKJEMA).run(); return await fn(); } throw e; }
}

export async function onRequestPost({ request, env }) {
  const db = env.AVVIST_DB;
  if (!db) return json(200, { ok: true, lagret: false });
  let body = {};
  try { body = JSON.parse((await request.text()).slice(0, 2000) || "{}"); } catch { return json(400, { error: "Ugyldig" }); }
  const q = String(body.q || ""), a = String(body.a || "").replace(/[\u0000-\u001f<>]/g, "").trim().toLowerCase().slice(0, 40);
  if (!/^[a-z0-9-]{1,40}$/.test(q) || a.length < 2) return json(400, { error: "Ugyldig" });
  const dag = dagFor(Date.now());
  await run(db, () => db.prepare("INSERT INTO avvist (dag, q, a, n) VALUES (?1, ?2, ?3, 1) ON CONFLICT(dag, q, a) DO UPDATE SET n = n + 1")
    .bind(dag, q, a).run());
  return json(200, { ok: true });
}

export async function onRequestGet({ request, env }) {
  const db = env.AVVIST_DB;
  if (!db) return json(200, { dager: 0, avvist: {}, merknad: "Ingen database koblet til" });
  const dager = Math.min(31, Math.max(1, +new URL(request.url).searchParams.get("dager") || 7));
  const fra = dagFor(Date.now() - (dager - 1) * 864e5);
  // Tellinger eldre enn 90 dager slettes
  await run(db, () => db.prepare("DELETE FROM avvist WHERE dag < ?1").bind(dagFor(Date.now() - 90 * 864e5)).run());
  const { results } = await run(db, () => db.prepare("SELECT q, a, SUM(n) AS n FROM avvist WHERE dag >= ?1 GROUP BY q, a ORDER BY n DESC LIMIT 20000").bind(fra).all());
  const out = {};
  for (const r of results || []) (out[r.q] || (out[r.q] = {}))[r.a] = r.n;
  return json(200, { dager, avvist: out });
}
