/**
 * Brandstudio Cloudflare staging: read-only mirror and optional D1 product index.
 * STATIC_SOURCE_PROXY is a temporary migration bridge, not the final assets host.
 * Write APIs are intentionally disabled until Access and private storage are ready.
 */
const STAGING_ORIGIN = "https://cinegitim.github.io/design";
const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "x-robots-tag": "noindex, nofollow",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });
}

function isStaticPath(pathname) {
  if (pathname.includes("\\") || pathname.includes("\0")) return false;
  if (pathname.startsWith("//")) return false;
  // URL normalizes traversal before pathname is read. Never accept a cross-origin URL.
  return pathname.startsWith("/");
}

async function staticMirror(request) {
  const incoming = new URL(request.url);
  if (!isStaticPath(incoming.pathname)) return json({ error: "invalid_path" }, 400);
  const upstream = new URL(STAGING_ORIGIN + incoming.pathname + incoming.search);
  // No user credentials or cookies are forwarded to GitHub Pages.
  const accept = request.headers.get("accept");
  const headers = new Headers();
  if (accept) headers.set("accept", accept);
  let upstreamResponse;
  try {
    upstreamResponse = await fetch(upstream.toString(), {
      method: request.method,
      headers,
      redirect: "manual",
    });
  } catch (_) {
    return json({ error: "static_origin_unavailable" }, 503);
  }
  const responseHeaders = new Headers(upstreamResponse.headers);
  for (const name of ["set-cookie", "content-security-policy-report-only", "server"]) {
    responseHeaders.delete(name);
  }
  const redirect = responseHeaders.get("location");
  if (redirect) {
    const target = new URL(redirect, upstream);
    if (target.origin === "https://cinegitim.github.io" &&
        target.pathname.startsWith("/design/")) {
      responseHeaders.set("location", target.pathname.slice("/design".length) + target.search + target.hash);
    } else {
      // Do not transparently redirect to an arbitrary destination.
      responseHeaders.delete("location");
    }
  }
  responseHeaders.set("x-brandstudio-stage", "personal-cloudflare-read-only");
  responseHeaders.set("x-robots-tag", "noindex, nofollow");
  responseHeaders.set("x-content-type-options", "nosniff");
  // API cache semantics never leak into the static mirror.
  responseHeaders.set("cache-control", "public, max-age=60");
  return new Response(request.method === "HEAD" ? null : upstreamResponse.body,
    { status: upstreamResponse.status, headers: responseHeaders });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/health") {
      if (request.method !== "GET") return json({ error: "method_not_allowed" }, 405);
      let db = "unavailable";
      try {
        const row = await env.DB.prepare(
          "SELECT value FROM system_meta WHERE key = ?"
        ).bind("schema_version").first();
        db = row?.value === "1" ? "ready" : "schema_missing";
      } catch (_) {
        db = "unavailable";
      }
      return json({
        app: "brandstudio",
        account: "personal",
        mode: "staging-read-only",
        origin: "github-pages-mirror",
        database: db,
        mutations_enabled: false,
      });
    }
    if (url.pathname === "/api/products") {
      if (request.method !== "GET") return json({ error: "method_not_allowed" }, 405);
      try {
        const query = await env.DB.prepare(
          "SELECT id, title, brand, category, current_version FROM products " +
          "WHERE visibility = ? ORDER BY created_at DESC LIMIT 100"
        ).bind("public").all();
        return json({ products: query.results || [], mutation_enabled: false });
      } catch (_) {
        return json({ error: "index_unavailable" }, 503);
      }
    }
    if (url.pathname.startsWith("/api/")) {
      return json({ error: "not_found", mutations_enabled: false }, 404);
    }
    if (!["GET", "HEAD"].includes(request.method)) {
      return json({ error: "read_only_staging" }, 405);
    }
    return staticMirror(request);
  },
};
