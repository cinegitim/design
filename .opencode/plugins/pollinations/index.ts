import { mkdir, readFile, writeFile } from "node:fs/promises"
import path from "node:path"

// Note: intentionally no plugin-SDK import (see .opencode/plugins/gpt-image).
// This module exports the plain OpenCode v2 contract object { id, setup }.

/**
 * brand-studio-pollinations-free — project-local OpenCode v2 adapter.
 *
 * Exposes `gen_edit_image_free`: no-key free image generation AND 1–3
 * image editing through the Pollinations free playground. Endpoints and
 * rules below are ported from the actual upstream source
 * (fkom13/opencode-pollinations-plugin
 *  src/tools/pollinations/gen_edit_image_free.ts, v6.5.5):
 *   GET  /api/generation-status   -> { count, max, remaining, canGenerate }
 *   POST /api/generate-image      -> { success, imageUrl }
 *   POST /api/generate-image-edit -> { success, imageUrl }
 *
 * No account, no API key, no login: quota is enforced per-IP server-side
 * and read live. No credentials of any kind are used, stored, or logged.
 */

const PLAYGROUND = "https://p-image-playground-production.up.railway.app"
const STATUS_URL = `${PLAYGROUND}/api/generation-status`
const GEN_URL = `${PLAYGROUND}/api/generate-image`
const EDIT_URL = `${PLAYGROUND}/api/generate-image-edit`

const ASPECTS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "custom", "match_input_image"] as const
const MAX_EDIT_IMAGES = 3
const ACCEPTED_MIME = ["image/jpeg", "image/png", "image/webp"]

type Quota = { count: number; max: number; remaining: number; canGenerate: boolean }

async function getQuota(): Promise<Quota | null> {
  try {
    const res = await fetch(STATUS_URL)
    if (!res.ok) return null
    const q = (await res.json()) as Partial<Quota>
    return typeof q?.canGenerate === "boolean" ? (q as Quota) : null
  } catch {
    return null
  }
}

const MIME_BY_EXT: Record<string, string> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
}

async function toDataUri(absPath: string): Promise<string> {
  const mime = MIME_BY_EXT[path.extname(absPath).toLowerCase()]
  if (!mime || !ACCEPTED_MIME.includes(mime)) {
    throw new Error(`Unsupported image type for ${absPath}; use JPEG, PNG or WebP.`)
  }
  const bytes = await readFile(absPath)
  return `data:${mime};base64,${bytes.toString("base64")}`
}

/** Detect real image format from magic bytes (never trust the extension). */
function detectFormat(bytes: Uint8Array): "png" | "jpg" | "webp" | "gif" | null {
  if (bytes.length > 8 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) return "png"
  if (bytes.length > 2 && bytes[0] === 0xff && bytes[1] === 0xd8) return "jpg"
  if (
    bytes.length > 12 &&
    bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46 &&
    bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50
  ) return "webp"
  if (bytes.length > 5 && bytes[0] === 0x47 && bytes[1] === 0x49 && bytes[2] === 0x46) return "gif"
  return null
}

async function saveBytes(bytes: Uint8Array, baseDir: string, rawOut?: string): Promise<{ filePath: string; format: string }> {
  let targetDir = baseDir
  let baseName = `polli-${Date.now()}`
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
  const format = detectFormat(bytes) ?? "jpg"
  await mkdir(targetDir, { recursive: true })
  const filePath = path.join(targetDir, `${baseName}.${format}`)
  await writeFile(filePath, bytes)
  return { filePath, format }
}

function validateCustomSize(width?: number, height?: number): string | null {
  if (width === undefined || height === undefined) return "custom aspect_ratio requires both width and height"
  for (const [name, value] of [["width", width], ["height", height]] as const) {
    if (!Number.isInteger(value) || value < 256 || value > 1440 || value % 16 !== 0) {
      return `${name} must be 256..1440 and a multiple of 16`
    }
  }
  return null
}

const plugin = {
  id: "brand-studio-pollinations-free",
  async setup(ctx: any) {
    await ctx.tool.transform((editor: any) => {
      editor.add({
        name: "gen_edit_image_free",
        description:
          "FREE image generation and 1-3 image editing via the Pollinations free playground. No API key, no login; per-IP quota enforced server-side and reported back. Aspect ratios, custom 256-1440 dimensions, seed, prompt upsampling, edit turbo. Saves the result into the project and returns the file path.",
        input: {
          type: "object",
          properties: {
            prompt: { type: "string", minLength: 1, description: "Text description of the image to generate or edit." },
            images: {
              type: "array",
              items: { type: "string" },
              description:
                "Optional 1-3 input image file(s) for editing (JPEG/PNG/WebP). Omit for pure generation. Relative paths resolve against the session directory.",
            },
            aspect_ratio: {
              type: "string",
              enum: [...ASPECTS],
              description: "Aspect ratio. Default '16:9' for generation, 'match_input_image' for editing. 'custom' is generation-only.",
            },
            width: { type: "integer", minimum: 256, maximum: 1440, description: "Custom width (with height), 256-1440, multiple of 16. Generation-only." },
            height: { type: "integer", minimum: 256, maximum: 1440, description: "Custom height (with width), 256-1440, multiple of 16. Generation-only." },
            seed: { type: "integer", minimum: 0, maximum: 2147483647, description: "Seed for reproducibility. Default random." },
            prompt_upsampling: { type: "boolean", description: "Enhance the prompt automatically. Generation-only." },
            turbo: { type: "boolean", description: "Faster edit pass. Edit-only." },
            output_path: {
              type: "string",
              description:
                "Where to save. A directory, or a file path used as the base name. Relative paths resolve against the session directory. Defaults to the session directory.",
            },
          },
          required: ["prompt"],
          additionalProperties: false,
        },
        execute: async (input: any, context: any) => {
          const args = input as {
            prompt: string
            images?: string[]
            aspect_ratio?: string
            width?: number
            height?: number
            seed?: number
            prompt_upsampling?: boolean
            turbo?: boolean
            output_path?: string
          }
          const baseDir = (context as { directory?: string } | undefined)?.directory || process.cwd()
          const isEdit = Array.isArray(args.images) && args.images.length > 0
          if (isEdit && args.images!.length > MAX_EDIT_IMAGES) {
            throw new Error(`At most ${MAX_EDIT_IMAGES} input images are supported.`)
          }
          const aspect = args.aspect_ratio || (isEdit ? "match_input_image" : "16:9")
          if (!isEdit && aspect === "match_input_image") throw new Error("match_input_image is edit-only.")
          if (isEdit && aspect === "custom") throw new Error("custom width/height is generation-only.")
          if (!isEdit && aspect === "custom") {
            const err = validateCustomSize(args.width, args.height)
            if (err) throw new Error(err)
          }

          const quota = await getQuota()
          if (quota && !quota.canGenerate) {
            throw new Error(`Free image quota exhausted (${quota.count}/${quota.max} used). Try again later; no key or login can bypass the per-IP quota.`)
          }

          const payload: Record<string, unknown> = {
            prompt: args.prompt,
            aspect_ratio: aspect,
            disable_safety_checker: false,
          }
          if (args.seed !== undefined) payload["seed"] = args.seed
          if (!isEdit && args.prompt_upsampling !== undefined) payload["prompt_upsampling"] = args.prompt_upsampling
          if (!isEdit && aspect === "custom") {
            payload["width"] = args.width
            payload["height"] = args.height
          }
          if (isEdit) {
            payload["images"] = await Promise.all(
              args.images!.map(async (p) => {
                const abs = path.isAbsolute(p) ? p : path.join(baseDir, p)
                try {
                  return await toDataUri(abs)
                } catch {
                  throw new Error(`Input image not found or unsupported: ${abs}`)
                }
              }),
            )
            if (args.turbo !== undefined) payload["turbo"] = args.turbo
          }

          const res = await fetch(isEdit ? EDIT_URL : GEN_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          })
          if (!res.ok) throw new Error(`Free image backend error (HTTP ${res.status}). Try again later.`)
          const apiResp = (await res.json()) as { success?: boolean; imageUrl?: string; error?: string; details?: string }
          if (!apiResp?.success || !apiResp.imageUrl) {
            throw new Error(`Free image backend: ${String(apiResp?.error || apiResp?.details || "unknown response").slice(0, 240)}`)
          }
          const dl = await fetch(apiResp.imageUrl)
          if (!dl.ok) throw new Error(`Could not download generated image (HTTP ${dl.status}).`)
          const bytes = new Uint8Array(await dl.arrayBuffer())
          const saved = await saveBytes(bytes, baseDir, args.output_path)
          const after = await getQuota()
          return {
            content: [
              `Free image ${isEdit ? "edit" : "generation"} complete (${aspect}, seed ${args.seed ?? "random"}).`,
              `  - ${saved.filePath} (${saved.format.toUpperCase()})`,
              after ? `Quota: ${after.remaining}/${after.max} remaining.` : "Quota: unknown (status check failed).",
            ].join("\n"),
          }
        },
      })
    })
  },
}

export default plugin
