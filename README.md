<p align="center">
  <a href="https://github.com/blakee-marcus/nextjs-skill/actions/workflows/verify.yml"><img src="https://github.com/blakee-marcus/nextjs-skill/actions/workflows/verify.yml/badge.svg" alt="Verification"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/blakee-marcus/nextjs-skill" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/version-0.1.12-blue" alt="Version 0.1.12">
</p>

# Next.js Agent Skill

**Version-aware Next.js guidance for coding agents.**

The skill inspects the installed Next.js version, router, configuration, and build behavior before changing code. It grounds version-sensitive decisions in the installed package or current official documentation.

```bash
npx skills add blakee-marcus/nextjs-skill
```

- Detects the project's actual Next.js setup before recommending APIs
- Keeps Server and Client Component boundaries narrow
- Prefers the smallest verified fix over speculative rewrites

Optimized for the App Router and Next.js 16+, with version detection before applying version-sensitive guidance.

[Installation](#installation) · [Usage](#usage) · [Source grounding](#source-grounding) · [SKILL.md](SKILL.md)

## Why this skill

Next.js conventions change quickly. Advice that is correct for one release can break another:

| Without the skill | With the skill |
|---|---|
| Adds `"use client"` to an entire page | Fetches data in a Server Component and keeps the interactive Client Component narrow |
| Applies v16 `use cache` APIs to a Next.js 14 project | Detects the installed version and uses the matching caching model |
| Clears `.next/` as a diagnosis | Reproduces the failure, reads the exact error, and fixes the root cause |
| Rewrites `@next/bundle-analyzer` or `next/third-parties` as local file references | Preserves valid NPM package identifiers |

## Source-grounded by design

- The installed `next` version and observed behavior take priority.
- Version-sensitive guidance points back to [official Next.js sources](references/source-manifest.md).
- Bundled references are navigation aids, not substitutes for current upstream documentation.
- This is an independent open-source skill. It is not affiliated with or endorsed by Vercel.

See the [source manifest](references/source-manifest.md), [documentation index](references/docs-index.md), and [caching reference](references/caching-and-revalidation.md) for representative provenance.

## Coverage

- **Routing and boundaries:** App Router, Pages Router, layouts, Server and Client Components, Route Handlers, and Proxy
- **Data and caching:** fetching, streaming, Server Actions, Cache Components, and revalidation
- **Build and development:** Turbopack, Webpack, HMR, build output, prerender errors, and Next.js MCP
- **Assets and styling:** images, fonts, metadata, CSS, and Tailwind integration boundaries
- **Testing and deployment:** Jest, Vitest, Playwright, Cypress, Node.js, Docker, static export, and adapters
- **Migration:** Next.js 16 upgrades, Cache Components adoption, and Pages Router to App Router moves

## Installation

### Recommended

```bash
npx skills add blakee-marcus/nextjs-skill
```

After installation, load the `nextjs` skill in your agent runtime and ask it to work on a Next.js project. The skill reads the project before applying version-sensitive guidance.

### Manual clone

Use HTTPS so no GitHub SSH configuration is required:

```bash
git clone https://github.com/blakee-marcus/nextjs-skill.git
```

Then place or link the cloned directory in the skill location used by your agent runtime.

## Runtime evidence

The CI workflow checks that the `skills` CLI can discover this skill from a repository checkout. Runtime behavior is tested separately.

- **Hermes Agent:** maintainer-tested on 2026-10-03 for local discovery and Agent Skills loading
- **Other Agent Skills-compatible runtimes:** may load the directory, but runtime-specific behavior has not been exercised by the maintainer

Installer support is not treated as proof of runtime compatibility.

## Usage

### Debug stale fetched data

> "Why is my fetched data stale?"

The agent checks the installed Next.js version and `cacheComponents` flag. It uses Cache Components APIs only when the project supports them, otherwise it follows the matching earlier caching model.

### Fix a dev-server failure

> "My dev server is missing `/_next/static/chunks/...` HMR scripts."

The agent inspects dev-server state, build artifacts, and whether Turbopack or Webpack is active before changing application code.

### Migrate or upgrade

> "Upgrade this project to Next.js 16 and adopt Cache Components."

The agent detects the current version, applies the appropriate migration path, and verifies the result through the project's real build and runtime paths.

## How it works

The operational workflow lives in [SKILL.md](SKILL.md):

1. **Detect:** installed versions, configuration, router, CSS pipeline, tests, and deployment target
2. **Classify:** task type and failure category
3. **Diagnose:** reproduce the original behavior and read exact errors
4. **Fix narrowly:** change the smallest coherent surface
5. **Verify:** rerun the original failing path, not just a component-level check

The `references/` directory contains source-grounded guidance organized by topic. Each concept has one canonical owner file to reduce contradictory advice.

## Maintenance

Version-sensitive references are refreshed from official Next.js documentation. Bundled material may lag upstream, so installed-version evidence and current official documentation remain authoritative.

Run the public verification gate locally:

```bash
python3 scripts/verify_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
npx --yes skills@1.7.0 add . --list
```

## Contributing

1. Make the smallest coherent change to `SKILL.md` or the correct reference file.
2. Link version-sensitive claims to official Next.js documentation.
3. Update the source manifest or documentation index when ingesting new sources.
4. Run the verification commands above.
5. Open a pull request explaining the source and behavior change.

See [SECURITY.md](SECURITY.md) for responsible disclosure.

## License

Distributed under the MIT License. See [LICENSE](LICENSE).
