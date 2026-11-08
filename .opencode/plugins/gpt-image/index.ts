import { mkdir, readFile, writeFile } from "node:fs/promises"
import os from "node:os"
import path from "node:path"

// Note: intentionally no plugin-SDK import. OpenCode 2.0.15 does not
// resolve "@opencode/plugin" for project-local plugins (verified via the
// server log), so this module exports the plain v2 contract object
// { id, setup } directly instead of going through a SDK helper.

/**
 * brand-studio-gpt-image — project-local OpenCode v2 adapter.
 *
 * Exposes `image_generate` and `image_edit` (default model gpt-image-2)
 * while reusing the OpenAI credential OpenCode itself already manages.
 * No new OAuth flow, no API key file, no token persistence: tokens live
 * only in memory for the Authorization header of the current call and are
 * never printed, logged, or written to disk by this plugin.
 *
 * Subscription-route limits (omitted rather than faked):
 * - PNG output only (no output_format arg, no mask_path arg).
 * - Model fixed to OPENCODE_IMAGE_MODEL or gpt-image-2 (no model arg).
 */

const DEFAULT_MODEL = "gpt-image-2"
const CHATGPT_IMAGE_ENDPOINT = "https://chatgpt.com/backend-api/codex/images/generations"
const CHATGPT_IMAGE_EDIT_ENDPOINT = "https://chatgpt.com/backend-api/codex/images/edits"
const OPENAI_IMAGE_ENDPOINT = "https://api.openai.com/v1/images/generations"
const OPENAI_IMAGE_EDIT_ENDPOINT = "https://api.openai.com/v1/images/edits"

const OAUTH_INTEGRATION_ID = "openai"

type ApiCredential = { mode: "api"; key: string }
type OAuthCredential = { mode: "oauth"; access: string; accountId?: string }
type OpenAICredential = ApiCredential | OAuthCredential

/**
 * Resolve the OpenAI credential, native-first:
 *   1. OpenCode V2 managed connection (integration id "openai") via
 *      ctx.integration.connection.active + .resolve — verified at runtime
 *      in this installation (active oauth connection, server-managed
 *      refresh). Works regardless of where the app stores credentials.
 *   2. OPENAI_API_KEY env override (explicit, API-key users).
 *   3. Key file fallback (API-key users; never created by this plugin).
 *
 * The legacy auth.json/OPENCODE_AUTH_CONTENT file parsing was removed:
 * it cannot see credentials managed elsewhere (e.g. the desktop app) and
 * wrongly concluded "No OpenAI credential found". Resolved tokens live in
 * memory only — never persisted, logged, or returned from a tool.
 */
async function resolveCredential(integration?: any): Promise<OpenAICredential> {
  try {
    const connApi = integration?.connection
    if (connApi && typeof connApi.active === "function" && typeof connApi.resolve === "function") {
      const conn = await connApi.active(OAUTH_INTEGRATION_ID)
      if (conn) {
        const cred = await connApi.resolve(conn)
        if (cred?.type === "oauth" && typeof cred.access === "string" && cred.access.length > 0) {
          const meta = cred.metadata && typeof cred.metadata === "object" ? cred.metadata : undefined
          const accountId =
            typeof meta?.accountID === "string"
              ? meta.accountID
              : typeof meta?.accountId === "string"
                ? meta.accountId
                : undefined
          return { mode: "oauth", access: cred.access, ...(accountId ? { accountId } : {}) }
        }
        if (
          (cred?.type === "key" || cred?.type === "api") &&
          typeof cred.key === "string" &&
          cred.key.trim()
        ) {
          return { mode: "api", key: cred.key.trim() }
        }
      }
    }
  } catch {
    // fall through to safe fallbacks below
  }

  const fromEnv = process.env["OPENAI_API_KEY"]?.trim()
  if (fromEnv) return { mode: "api", key: fromEnv }

  const keyFile =
    process.env["OPENCODE_OPENAI_KEY_FILE"]?.trim() ||
    path.join(os.homedir(), ".config", "opencode", "openai.key")
  try {
    const fromFile = (await readFile(keyFile, "utf8")).trim()
    if (fromFile) return { mode: "api", key: fromFile }
  } catch {
    // missing/unreadable -> fall through
  }
  throw new Error(
    "No OpenAI credential found. Connect OpenAI/ChatGPT in OpenCode, or set OPENAI_API_KEY.",
  )
}

function authHeaders(credential: OpenAICredential): Record<string, string> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${credential.mode === "oauth" ? credential.access : credential.key}`,
  }
  if (credential.mode === "oauth" && credential.accountId) {
    headers["ChatGPT-Account-Id"] = credential.accountId
  }
  return headers
}

type ImageData = { b64_json?: string; url?: string }

async function requestImages(url: string, headers: Record<string, string>, init: RequestInit): Promise<ImageData[]> {
  const res = await fetch(url, { ...init, headers: { ...headers, ...((init.headers as Record<string, string>) || {}) } })
  if (!res.ok) {
    const text = await res.text()
    let message = text
    try {
      message = (JSON.parse(text) as { error?: { message?: string } })?.error?.message ?? text
    } catch {
      // keep raw text (truncated to avoid leaking large payloads)
    }
    throw new Error(`Image request failed (HTTP ${res.status}): ${message.slice(0, 500)}`)
  }
  const json = (await res.json()) as { data?: ImageData[] }
  const data = json.data ?? []
  if (data.length === 0) throw new Error("No image data returned.")
  return data
}

const MIME_BY_EXT: Record<string, string> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
}

async function toDataUrl(absPath: string): Promise<string> {
  const mime = MIME_BY_EXT[path.extname(absPath).toLowerCase()] || "image/png"
  const bytes = await readFile(absPath)
  return `data:${mime};base64,${bytes.toString("base64")}`
}

async function saveImages(data: ImageData[], baseDir: string, rawOut?: string): Promise<string[]> {
  let targetDir = baseDir
  let baseName = `image-${Date.now()}`
  const out = rawOut?.trim()
  if (out) {
    const resolved = path.isAbsolute(out) ? out : path.join(baseDir, out)
    if (path.extname(resolved) !== "") {
      targetDir = path.dirname(resolved)
      baseName = path.basename(resolved, path.extname(resolved))
    } else {
      targetDir = resolved
    }
  }
  await mkdir(targetDir, { recursive: true })
  const saved: string[] = []
  for (let i = 0; i < data.length; i++) {
    const b64 = data[i]?.b64_json
    if (!b64) continue
    const suffix = data.length > 1 ? `-${i + 1}` : ""
    const filePath = path.join(targetDir, `${baseName}${suffix}.png`)
    await writeFile(filePath, Buffer.from(b64, "base64"))
    saved.push(filePath)
  }
  if (saved.length === 0) throw new Error("Response contained no base64 image payloads to save.")
  return saved
}

async function loadReferenceImages(paths: string[], baseDir: string): Promise<{ image_url: string }[]> {
  return Promise.all(
    paths.map(async (p) => {
      const abs = path.isAbsolute(p) ? p : path.join(baseDir, p)
      try {
        await readFile(abs)
      } catch {
        throw new Error(`Reference image not found: ${abs}`)
      }
      return { image_url: await toDataUrl(abs) }
    }),
  )
}

const SIZE_ENUM = ["auto", "1024x1024", "1536x1024", "1024x1536"]
const QUALITY_ENUM = ["auto", "low", "medium", "high"]
const BACKGROUND_ENUM = ["auto", "transparent", "opaque"]

const COMMON_PROPS = {
  size: { type: "string", enum: SIZE_ENUM, description: "Image dimensions. Default 'auto'." },
  quality: { type: "string", enum: QUALITY_ENUM, description: "Rendering quality. Default 'auto'." },
  background: { type: "string", enum: BACKGROUND_ENUM, description: "Background. Default 'auto'." },
  n: { type: "integer", minimum: 1, maximum: 10, description: "How many images. Default 1." },
  output_path: {
    type: "string",
    description:
      "Where to save. A directory, or a file path used as a base name when n>1. Relative paths resolve against the session directory. Defaults to the session directory.",
  },
}

const plugin = {
  id: "brand-studio-gpt-image",
  async setup(ctx: any) {
    // Capture the native integration domain once; tool executions reuse it
    // to resolve the managed OpenAI connection (no file parsing, no SDK import).
    const integration = ctx?.integration
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "image_generate",
        description:
          "Generate one or more images from a text prompt (default gpt-image-2) and save them as PNG to disk. Optionally provide reference image(s) to guide generation. Returns the saved file path(s). Uses the already-connected OpenAI/ChatGPT credential; PNG output only.",
        input: {
          type: "object",
          properties: {
            prompt: { type: "string", minLength: 1, description: "Text description of the image to generate." },
            image_paths: {
              type: "array",
              items: { type: "string" },
              description:
                "Optional reference image file(s) to guide generation. Relative paths resolve against the session directory.",
            },
            ...COMMON_PROPS,
          },
          required: ["prompt"],
          additionalProperties: false,
        },
        execute: async (input, context) => {
          const args = input as {
            prompt: string
            image_paths?: string[]
            size?: string
            quality?: string
            background?: string
            n?: number
            output_path?: string
          }
          const credential = await resolveCredential(integration)
          const baseDir = (context as { directory?: string } | undefined)?.directory || process.cwd()
          const model = process.env["OPENCODE_IMAGE_MODEL"] || DEFAULT_MODEL
          const n = args.n ?? 1
          const hasRefs = !!args.image_paths && args.image_paths.length > 0
          const headers = authHeaders(credential)

          let data: ImageData[]
          if (hasRefs && credential.mode === "oauth") {
            const images = await loadReferenceImages(args.image_paths!, baseDir)
            data = await requestImages(CHATGPT_IMAGE_EDIT_ENDPOINT, headers, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ model, prompt: args.prompt, images, n, size: args.size || "auto", quality: args.quality || "auto" }),
            })
          } else if (hasRefs) {
            const form = new FormData()
            form.append("model", model)
            form.append("prompt", args.prompt)
            form.append("n", String(n))
            form.append("size", args.size || "auto")
            form.append("quality", args.quality || "auto")
            form.append("output_format", "png")
            if (args.background) form.append("background", args.background)
            for (const p of args.image_paths!) {
              const abs = path.isAbsolute(p) ? p : path.join(baseDir, p)
              try {
                await readFile(abs)
              } catch {
                throw new Error(`Reference image not found: ${abs}`)
              }
              form.append("image[]", new Blob([await readFile(abs)]), path.basename(abs))
            }
            data = await requestImages(OPENAI_IMAGE_EDIT_ENDPOINT, headers, { method: "POST", body: form })
          } else {
            const body: Record<string, unknown> = {
              model,
              prompt: args.prompt,
              n,
              size: args.size || "auto",
              quality: args.quality || "auto",
              output_format: "png",
            }
            if (args.background) body["background"] = args.background
            data = await requestImages(
              credential.mode === "oauth" ? CHATGPT_IMAGE_ENDPOINT : OPENAI_IMAGE_ENDPOINT,
              headers,
              { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
            )
          }

          const saved = await saveImages(data, baseDir, args.output_path)
          return {
            content: [
              `Generated ${saved.length} image(s) with ${model} via ${
                credential.mode === "oauth" ? "the connected ChatGPT subscription" : "the OpenAI API"
              } (${args.size || "auto"}, ${args.quality || "auto"} quality)${
                hasRefs ? ` from ${args.image_paths!.length} reference image(s)` : ""
              }.`,
              ...saved.map((p) => `  - ${p}`),
            ].join("\n"),
          }
        },
      })

      editor.add({
        name: "image_edit",
        description:
          "Edit or transform existing image(s) with a text prompt (default gpt-image-2) and save the result(s) as PNG to disk. Returns the saved file path(s). Uses the already-connected OpenAI/ChatGPT credential; PNG output only, no mask support.",
        input: {
          type: "object",
          properties: {
            prompt: { type: "string", minLength: 1, description: "Instruction describing the desired edit." },
            image_paths: {
              type: "array",
              items: { type: "string" },
              minItems: 1,
              description: "Input image file(s). Relative paths resolve against the session directory.",
            },
            ...COMMON_PROPS,
          },
          required: ["prompt", "image_paths"],
          additionalProperties: false,
        },
        execute: async (input, context) => {
          const args = input as {
            prompt: string
            image_paths: string[]
            size?: string
            quality?: string
            background?: string
            n?: number
            output_path?: string
          }
          const credential = await resolveCredential(integration)
          const baseDir = (context as { directory?: string } | undefined)?.directory || process.cwd()
          const model = process.env["OPENCODE_IMAGE_MODEL"] || DEFAULT_MODEL
          const n = args.n ?? 1
          const headers = authHeaders(credential)

          let data: ImageData[]
          if (credential.mode === "oauth") {
            const images = await loadReferenceImages(args.image_paths, baseDir)
            data = await requestImages(CHATGPT_IMAGE_EDIT_ENDPOINT, headers, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ model, prompt: args.prompt, images, n, size: args.size || "auto", quality: args.quality || "auto" }),
            })
          } else {
            const form = new FormData()
            form.append("model", model)
            form.append("prompt", args.prompt)
            form.append("n", String(n))
            form.append("size", args.size || "auto")
            form.append("quality", args.quality || "auto")
            form.append("output_format", "png")
            if (args.background) form.append("background", args.background)
            for (const p of args.image_paths) {
              const abs = path.isAbsolute(p) ? p : path.join(baseDir, p)
              try {
                await readFile(abs)
              } catch {
                throw new Error(`Input image not found: ${abs}`)
              }
              form.append("image[]", new Blob([await readFile(abs)]), path.basename(abs))
            }
            data = await requestImages(OPENAI_IMAGE_EDIT_ENDPOINT, headers, { method: "POST", body: form })
          }

          const saved = await saveImages(data, baseDir, args.output_path)
          return {
            content: [
              `Edited image(s) with ${model} via ${
                credential.mode === "oauth" ? "the connected ChatGPT subscription" : "the OpenAI API"
              } from ${args.image_paths.length} input(s). Saved ${saved.length}:`,
              ...saved.map((p) => `  - ${p}`),
            ].join("\n"),
          }
        },
      })
    })
  }
}

export default plugin
