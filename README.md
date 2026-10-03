<p align="center">
  <a href="https://nextjs.org/docs"><img src="https://img.shields.io/badge/Next.js-16+-000000?logo=next.js&logoColor=white" alt="Next.js 16+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/blakee-marcus/nextjs-skill" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/version-0.1.12-blue" alt="Version 0.1.12">
</p>

# Next.js Agent Skill

A version-aware agent skill for building, modifying, migrating, and debugging Next.js applications against the installed version and current official documentation.

[Install](#installation) · [Usage](#usage) · [SKILL.md](SKILL.md)

## About the skill

This skill teaches an agent to do reliable Next.js work. It is triggered whenever a task touches Next.js routing, server/client boundaries, caching, Server Actions, Turbopack, or migration to Next.js 16.

What it changes:

- **Detects before directing.** Reads `package.json`, installed versions, `next.config.*`, and `app/`/`pages/` structure before applying version-sensitive advice.
- **Picks the smallest fix.** Prefers boundary corrections, Suspense wrappers, and narrow `"use client"` islands over architectural rewrites.
- **Sources claims.** Implementation-sensitive guidance points at official Next.js documentation or the installed package docs.

[SKILL.md](SKILL.md) is the operational artifact. This README is the human-facing orientation.

## Why this skill

Next.js conventions change quickly. Without grounding, agents default to stale training data and common failure modes:

| Without the skill | With the skill |
|---|---|
| Adds `"use client"` to an entire page | Fetches data in a Server Component, wraps only the interactive island as a Client Component |
| Applies v16 `use cache` APIs to a Next.js 14 project | Detects the installed version and uses the matching caching model |
| Clears `.next/` as a diagnosis | Reproduces the failure, reads the exact error / docs message URL, then fixes the root cause |
| Rewrites `@next/bundle-analyzer` or `next/third-parties` as local file references | Treats them as the NPM packages they are |

## Coverage

The skill covers the parts of Next.js where version and convention mistakes are most expensive:

- **Routing & boundaries** — App Router file-system routing, layouts, Server/Client Component boundaries, Route Handlers, and the v16+ Proxy.
- **Data & caching** — fetching, streaming, Server Functions / Server Actions, Cache Components (`use cache`, `cacheLife`, `cacheTag`), and revalidation.
- **Build & dev tooling** — Turbopack vs. Webpack, build output interpretation, prerender errors, and the Next.js MCP server.
- **Assets & styling** — images, fonts, metadata, CSS, and Tailwind integration boundaries.
- **Testing & deployment** — Jest, Vitest, Playwright, Cypress, Node.js, Docker, static export, and adapters.
- **Migration** — upgrades to Next.js 16, Cache Components adoption, and Pages → App Router moves.

## Getting Started

### Prerequisites

- An agent runtime capable of loading Agent Skills. Hermes Agent is currently runtime-verified; other installation paths are listed below with their verification status.
- A target project with a `package.json` so the skill can detect the installed `next` version.

### Installation

**Recommended — one command:**

```bash
npx skills add blakee-marcus/nextjs-skill
```

This is the recommended distribution command for Agent Skills-compatible runtimes.

<details>
<summary>Manual install per runtime</summary>

**Hermes Agent**

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  ~/.hermes/skills/software-development/nextjs
```

**Claude Code — personal**

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  ~/.claude/skills/nextjs
```

**Claude Code — project**

```bash
git clone git@github.com:blakee-marcus/nextjs-skill.git \
  .claude/skills/nextjs
```

Any Agent Skills–compatible runtime can load this directory directly. It contains only `SKILL.md`, `README.md`, `LICENSE`, and `references/`. No build step or dependencies.

</details>

## Supported Runtimes

The recommended distribution path is:

```bash
npx skills add blakee-marcus/nextjs-skill
```

That install path has been exercised. Runtime-specific behavior is only marked verified where it has actually been tested.

| Runtime        | Install path              | Verified |
| -------------- | ------------------------- | -------- |
| Hermes Agent   | Manual clone              | ✅        |
| Claude Code    | skills.sh or manual clone | Not yet  |
| Codex          | skills.sh                 | Not yet  |
| Cursor         | skills.sh                 | Not yet  |
| Windsurf       | skills.sh                 | Not yet  |
| GitHub Copilot | skills.sh                 | Not yet  |
| Gemini CLI     | skills.sh                 | Not yet  |
| OpenCode       | skills.sh                 | Not yet  |

## Usage

Load the skill, then ask for Next.js work. Good prompts:

### Add an interactive island to a Server Component page

> "Add a like button to this App Router blog post page."

The agent keeps data fetching server-side and creates a narrow Client Component for the button, passing serializable props instead of marking the whole page `"use client"`.

### Debug stale fetched data

> "Why is my fetched data stale?"

The agent checks the installed Next.js version and `cacheComponents` flag, then applies `"use cache"` + `cacheLife()` only when appropriate, or explains the previous caching model for older projects.

### Fix a dev-server failure

> "My dev server is missing `/_next/static/chunks/...` HMR scripts."

The agent inspects dev-server state, `.next/`, and whether Turbopack or Webpack is active, then fixes the bundler/runtime mismatch rather than editing components at random.

### Migrate or upgrade

> "Upgrade this project to Next.js 16 and adopt Cache Components."

The agent detects the current version, runs the appropriate codemods, rewrites `middleware.ts` → `proxy.ts` if needed, and verifies through `next build`.

## How it works

```text
.
├── SKILL.md                          → operational workflow loaded by the agent
├── references/
│   ├── docs-index.md                 → source inventory + ownership map
│   ├── source-manifest.md            → provenance and authority order
│   ├── app-router.md                 → App Router fundamentals
│   ├── server-client-components.md   → boundary rules
│   ├── caching-and-revalidation.md   → Cache Components and legacy caching
│   ├── turbopack-and-build.md        → bundler, build output, prerender errors
│   └── ...                           → one canonical owner per concept
├── LICENSE                           → MIT
└── README.md                         → this file
```

The skill drives a fixed workflow in `SKILL.md`:

1. **Detect** — installed versions, config, router, CSS pipeline, test setup.
2. **Classify** — version, router, package manager, bundler, deployment target.
3. **Root-cause-first debugging** — reproduce, read exact errors, classify failure.
4. **Smallest fix** — change the smallest coherent surface and verify.
5. **Verify** — run project scripts, inspect build output, use the Next.js MCP server when available.

## Source grounding

This skill compiles official Next.js documentation into agent-operational knowledge, not a website mirror.

- **Authority order** (highest first): installed `next` version → observed runtime/build behavior → current official Next.js docs → Next.js source/release notes → bundled references → existing project code → remembered behavior.
- **Provenance**: the docs index was initially seeded from the official Next.js 16.3.3 `llms.txt`; operational rules were extracted from `https://nextjs.org/docs/app/*` pages.
- **Ownership**: each concept has one canonical reference file. Cross-links, don't duplicate.
- **Verification**: version-sensitive claims should carry a source URL. If one is missing, the bundled reference is treated as a navigation aid, not the final authority.

This is an independent agent skill, not an official Vercel project. Next.js is a Vercel trademark and open-source project.

## Contributing

1. Fork or branch.
2. Make the smallest coherent change to `SKILL.md` or the correct canonical reference file.
3. Update `references/docs-index.md` source metadata if you ingest new docs.
4. Keep one concept per owner file; cross-link duplicates rather than copying.
5. Run the repository's verification checks if present.
6. Open a PR explaining the source and the behavior change.

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
