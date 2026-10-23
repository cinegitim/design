import assert from "node:assert/strict";
import fs from "node:fs";
import { test } from "node:test";
import worker from "../src/worker.mjs";

const fakeDb = {
  prepare(sql) {
    return {
      bind(...args) {
        if (sql.includes("system_meta")) return { first: async () => ({ value: "1" }) };
        if (sql.includes("FROM products")) return { all: async () => ({ results: [] }) };
        throw new Error("unexpected SQL " + sql);
      },
    };
  },
};
const req = (path, method = "GET") =>
  new Request("https://brandstudio-stage.example" + path, { method });
test("health reports actual read-only mode", async () => {
  const r = await worker.fetch(req("/api/health"), { DB: fakeDb });
  assert.equal(r.status, 200);
  const x = await r.json();
  assert.equal(x.database, "ready");
  assert.equal(x.mutations_enabled, false);
  assert.equal(x.mode, "staging-read-only");
});
test("products read D1 and do not expose private drafts", async () => {
  const r = await worker.fetch(req("/api/products"), { DB: fakeDb });
  assert.equal(r.status, 200);
  assert.deepEqual((await r.json()).products, []);
});
test("mutations cannot write to API or origin", async () => {
  for (const path of ["/api/products", "/api/product/demo/save", "/"]) {
    const r = await worker.fetch(req(path, "POST"), { DB: fakeDb });
    assert.ok([404,405].includes(r.status));
  }
});
test("unexpected API endpoints are not proxied", async () => {
  const r = await worker.fetch(req("/api/private-file"), { DB: fakeDb });
  assert.equal(r.status, 404);
});
test("static asset mirror does not forward request secrets", async () => {
  const original = globalThis.fetch;
  let input = null;
  globalThis.fetch = async (url, opts) => {
    input = { url, opts };
    return new Response("<h1>Brandstudio</h1>", {
      status: 200, headers: { "content-type": "text/html; charset=utf-8" },
    });
  };
  try {
    const request = new Request("https://stage.example/workspaces/asyada-egitim/",
      { headers: { cookie: "session=secret", authorization: "Bearer secret" } });
    const response = await worker.fetch(request, { DB: fakeDb });
    assert.equal(response.status, 200);
    assert.equal(input.url, "https://cinegitim.github.io/design/workspaces/asyada-egitim/");
    assert.equal(input.opts.headers.get("cookie"), null);
    assert.equal(input.opts.headers.get("authorization"), null);
    assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow");
  } finally {
    globalThis.fetch = original;
  }
});
