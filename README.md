# Next.js Agent Skill

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16+-000000?logo=next.js&logoColor=white" alt="Next.js 16+">
  <img src="https://img.shields.io/badge/Agent_Skills-open-6f42c1" alt="Agent Skills">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version 0.1.0">
  <img src="https://img.shields.io/github/license/blakee-marcus/nextjs-skill" alt="MIT License">
  <img src="https://img.shields.io/badge/source-official_Next.js_docs-0ea5e9" alt="Official Next.js docs">
</p>

An open Agent Skill for Next.js — version-aware implementation, modification, migration, debugging, and verification. Works with **Hermes Agent, Claude Code, Codex, Cursor, Windsurf, GitHub Copilot, Gemini CLI, OpenCode, and any Agent Skills–compatible runtime**.

## Why this exists

Next.js changes fast. Training data and muscle memory are frequently stale, especially across the App Router, Cache Components, Turbopack, and the Server/Client Component model. This skill interrupts specific failure modes:

- **Blindly adding `"use client"`** to an entire page or layout instead of isolating the interactive island.
- **Applying v16 Cache Components APIs** (`"use cache"`, `cacheLife`, `cacheTag`) to projects still on the previous caching model.
- **Treating Turbopack failures as Webpack problems** — or vice versa — without checking the actual bundler path.
- **Rewriting architecture** when a narrow boundary fix or a Suspense wrapper would solve the problem.
- **Clearing `.next` caches as a final diagnosis** without identifying the root cause.
- **Misidentifying package names** like `@next/bundle-analyzer` or `next/third-parties` as local file references.
- **Guessing current Next.js behavior from memory** instead of reading the installed version's docs.

## How it works

The skill drives a fixed workflow defined in `SKILL.md`:

1. **Detect** — read `package.json`, lockfile, installed versions, `next.config.*`, `app/`/`pages/` layout, CSS pipeline, and test setup.
2. **Classify** — pin version, router, package manager, bundler, deployment target, and task type.
3. **Root-cause-first debugging** — reproduce, read exact errors, and classify the failure before editing.
4. **Smallest fix** — change the smallest coherent surface and verify through the original user-visible path.
5. **Verify** — run project scripts, inspect build output, and use the Next.js MCP server when available.

## Major capabilities

- App Router file-system routing, layouts, dynamic segments, route groups, parallel/intercepting routes
- Server Components as the default; narrow Client Component boundaries
- Data fetching and streaming with `Suspense`, `loading.js`, React `cache`, and the `use` API
- Server Functions / Server Actions: forms, event handlers, pending states, optimistic UI, security
- Caching with Cache Components (`use cache`, `cacheLife`, `cacheTag`, `use cache: private`, `use cache: remote`)
- Revalidation (`revalidateTag`, `updateTag`, `revalidatePath`, `refresh`) matched to use case
- Route Handlers (`route.ts`) using Web Request/Response APIs
- Proxy (`proxy.ts`) — the v16+ replacement for Middleware
- Images, fonts, metadata, CSS, and Tailwind integration boundaries
- Turbopack (default in v16) and Webpack opt-out (`--webpack`)
- Build output interpretation, prerender errors, `--debug-prerender`
- Local development, HMR, debugging, and the Next.js MCP server
- Deployment: Node.js, Docker, static export, adapters
- Testing with Jest, Vitest, Playwright, Cypress
- Migration / upgrade to Next.js 16, including codemods and Cache Components adoption

## Installation

The repository root **is** the skill. No nested `nextjs/` folder inside the repository.

### One command — works everywhere (recommended)

```bash
npx skills add blakee-marcus/nextjs-skill
```

This installs the skill to `~/.agents/skills/nextjs` and automatically symlinks it into supported agents.

<details>
<summary>Per-runtime manual install (only if skills.sh isn't an option)</summary>

### Hermes Agent

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  ~/.hermes/skills/software-development/nextjs
```

### Claude Code — personal

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  ~/.claude/skills/nextjs
```

### Claude Code — project

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  .claude/skills/nextjs
```

### Generic Agent Skills

Any runtime that implements the Agent Skills standard can load this directory directly. It contains `SKILL.md`, `README.md`, `LICENSE`, and `references/`. No build step or dependencies are required.

</details>

## Supported Runtimes

| Runtime | Load | Install | Notes |
|---|---|---|---|
| **skills.sh (universal)** | ✅ Verified | ✅ Verified | `npx skills add blakee-marcus/nextjs-skill` installs to `~/.agents/skills/nextjs` and symlinks to agents |
| **Hermes Agent** | ✅ Verified | ✅ Verified | `~/.hermes/skills/software-development/nextjs` |
| **Claude Code** | ✅ Verified | ⏳ Pending | Via skills.sh or manual clone |
| **Codex** | ✅ Verified | ⏳ Pending | Via skills.sh |
| **Cursor** | ✅ Verified | ⏳ Pending | Via skills.sh |
| **Windsurf** | ✅ Verified | ⏳ Pending | Via skills.sh |
| **GitHub Copilot** | ✅ Verified | ⏳ Pending | Via skills.sh |
| **Gemini CLI** | ✅ Verified | ⏳ Pending | Via skills.sh |
| **OpenCode** | ✅ Verified | ⏳ Pending | Via skills.sh |

## Usage

Load the skill, then ask for any Next.js task:

- **New project** — scaffold with App Router, set up Tailwind, fonts, images, metadata.
- **Modify existing app** — add a page, route, component, or feature while preserving architecture.
- **Debug** — routing, hydration, build, caching, Server Action, or Turbopack failures.
- **Migrate** — upgrade to Next.js 16, adopt Cache Components, move Pages → App Router.
- **Review** — flag stale patterns, unnecessary `"use client"`, and version-incompatible caching assumptions.

## Quick demo scenarios

### 1. Server/Client boundary mistake prevention
> "Add an interactive like button to this App Router blog post page."

**Without skill:** Agent marks the whole page `"use client"` and loses server-side data fetching.
**With skill:** Agent detects the App Router default, fetches the post in a Server Component, and adds a narrow Client Component island for the like button, passing serializable props.

### 2. Cache Components version awareness
> "Why is my fetched data stale?"

**Without skill:** Agent assumes legacy default caching and adds `cache: 'force-cache'` everywhere.
**With skill:** Agent checks the installed Next.js version and `cacheComponents` flag, then applies `"use cache"` + `cacheLife()` only when appropriate, or explains the previous model for older projects.

### 3. Turbopack failure diagnosis
> "My dev server is missing `/_next/static/chunks/...` HMR scripts."

**Without skill:** Agent starts editing application components or randomly clears caches.
**With skill:** Agent inspects dev-server state, `.next/`, and whether Turbopack or Webpack is active, then fixes the bundler/runtime mismatch rather than the components.

### 4. Package identifier safety
> "Set up bundle analysis with `@next/bundle-analyzer` and `next/third-parties`."

**Without skill:** Agent might rewrite them as local `@file:` references and break the project.
**With skill:** Identifiers stay as NPM packages and are installed correctly.

### 5. Version mismatch awareness
> "This project is on Next.js 14. How do I add caching?"

**Without skill:** Agent applies v16 Cache Components guidance blindly.
**With skill:** Agent recognizes v14, explains the previous caching model (`fetch` options, `unstable_cache`, route segment configs), and only suggests Cache Components if the project is being upgraded.

## Repository structure

- **`SKILL.md`** — operational workflow: detect → classify → root-cause → smallest fix → verify.
- **`references/*.md`** — durable technical knowledge compiled from official Next.js docs, one canonical owner per concept.
- **`references/docs-index.md`** — source provenance + ownership map: which URL was ingested and which reference owns it.
- **`LICENSE`** — MIT.

## Documentation ingestion model

This skill compiles official Next.js documentation into agent-operational knowledge, not a mirror of the website.

- **Single-page boundary.** One documentation page ingested at a time. Only claims the page supports are extracted.
- **Merge, don't append.** New information is consolidated into existing sections.
- **Canonical local ownership.** Each concept has exactly one owner file. Other files summarize or cross-link.
- **Provenance.** Implementation-sensitive facts carry source URLs.
- **Conflict handling.** Contradictions are noted with both source URLs; resolution follows the authority order in `SKILL.md`.

## Source / provenance policy

- Next.js is a Vercel trademark and open-source project. This repository is an independent agent skill, not affiliated with or endorsed by Vercel.
- References are original summaries and operational compilations derived from the official Next.js documentation at [https://nextjs.org/docs](https://nextjs.org/docs), licensed under the [Next.js documentation license](https://github.com/vercel/next.js/blob/canary/license.md) where applicable.
- Bundled references are navigation aids and derived guidance. The official documentation remains the authority.

## License

MIT — see [LICENSE](LICENSE).
