// Cloudflare Pages Function: sender /api/* videre til konto-API-et som fortsatt kjører hos Netlify.
// Kontoene (Netlify Blobs) blir liggende der de er – ingen brukerdata flyttes eller slettes.
// Nettleseren snakker bare med dypdykk.net, så det trengs ingen CORS.
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const origin = (env && env.API_ORIGIN) || "https://dypdykk.netlify.app";
  const headers = { "content-type": request.headers.get("content-type") || "application/json" };
  const auth = request.headers.get("authorization");
  if (auth) headers.authorization = auth;
  const init = { method: request.method, headers, redirect: "manual" };
  if (!["GET", "HEAD"].includes(request.method)) init.body = await request.text();
  try {
    const r = await fetch(origin + url.pathname + url.search, init);
    return new Response(r.body, { status: r.status,
      headers: { "content-type": r.headers.get("content-type") || "application/json; charset=utf-8", "cache-control": "no-store" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Kontotjenesten svarer ikke akkurat nå. Prøv igjen litt senere." }),
      { status: 502, headers: { "content-type": "application/json; charset=utf-8" } });
  }
}
