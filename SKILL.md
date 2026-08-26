---
name: nextjs
description: Build, modify, review, migrate, and debug Next.js applications using installed-version evidence and current official documentation.
version: 0.1.0
author: Blake Marcus
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: nextjs, react, app-router, server-components, server-actions, turbopack, typescript, frontend, fullstack, web
  hermes-tags: nextjs, react, app-router, server-components, server-actions, turbopack, typescript, frontend, fullstack, web
---

# Next.js Skill

Use this skill to build, modify, review, migrate, and debug Next.js applications against the installed Next.js version and current official documentation. It is optimized for the App Router and Next.js 16+, but version-detects before applying version-sensitive guidance.

## When to use

- Building or modifying a Next.js application (App Router preferred; Pages Router handled when present)
- Routing, layout, page, navigation, or route-handler work
- Server / Client Component decisions and boundary bugs
- Data fetching, streaming, Suspense, or mutation with Server Functions / Server Actions
- Cache / revalidation / ISR behavior, including Cache Components (`cacheComponents`)
- Route handlers, Proxy (formerly Middleware), metadata, images, fonts, CSS integration
- Turbopack, HMR, dev-server, build, and deployment failures
- Testing setup (unit, integration, E2E)
- Migration / upgrade work (especially to Next.js 16)
- Review of generated Next.js code for version-specific mistakes

**Don't use for** generic React, generic CSS, or Tailwind internals unless Next.js integration materially affects the answer. When Tailwind behavior is the question, defer to the installed Tailwind skill.

## Authority order (highest first)

1. Installed `next` package version in the target project
2. Observed runtime / build behavior (terminal, browser, Next.js MCP if available)
3. Current official Next.js documentation for that installed version
4. Current Next.js source / release information where necessary
5. Bundled references in this skill
6. Existing project code as evidence of current assumptions
7. Remembered framework behavior (lowest — easily stale)

**Do not infer current Next.js behavior from model memory when exact semantics matter.** Inspect the installed `next` version and read the docs for that version before applying version-sensitive guidance. Prefer bundled `node_modules/next/dist/docs/` when present, or fetch `https://nextjs.org/docs` with `Accept: text/markdown`. Do not blindly apply v16-only APIs to older projects.

## Phase 1: Detect

Inspect before changing. Gather:

- `package.json` — `next`, `react`, `react-dom` versions; scripts; package manager
- Lockfile — `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lock`, `bun.lockb`
- Installed versions: `npm ls next react react-dom` (or pnpm/yarn/bun equivalent)
- `next.config.*` — router, output, turbopack, cacheComponents, serverActions, etc.
- `app/` vs `pages/` vs mixed; `src/` folder if used
- `proxy.ts` / `middleware.ts` / route handlers / instrumentation
- `tsconfig.json` / `jsconfig.json`
- CSS pipeline — global CSS, CSS Modules, Tailwind, PostCSS, Sass, CSS-in-JS
- Test setup — Jest / Vitest / Playwright / Cypress
- Deployment config / adapter hints / static export / Docker
- Current git status

Determine explicitly:

- Next.js version (major/minor/patch)
- App Router / Pages Router / mixed
- Package manager
- TypeScript or JavaScript
- Turbopack or Webpack build path
- Deployment target (Vercel, Node, Docker, static export, adapter)
- Whether `cacheComponents` / Cache Components is in use
- Existing architecture and conventions

Completion criterion: you can state all of the above without guessing before making version-sensitive edits.

## Phase 2: Classify

Classify the task and the failure before changing code.

**Task type:** new feature / modify existing / debug / migrate / review.

**Failure category (when debugging):**

- dev-server / runtime failure
- stale `.next` artifacts
- HMR / Turbopack chunk mismatch
- browser cache / service-worker behavior
- missing static asset / font / image
- server/client boundary violation
- hydration mismatch
- routing / navigation problem
- caching / revalidation problem
- Server Action problem
- route-handler / API issue
- config mismatch
- build-time failure
- dependency / version mismatch
- deployment / runtime mismatch
- CSS pipeline issue
- external infrastructure issue

Do not "fix" a runtime failure by randomly changing framework configuration.

## Phase 3: Root-cause-first debugging

For any failure:

1. Inspect Phase 1 context.
2. Reproduce through the original user-visible path (page load, navigation, build, test).
3. Read the exact error, stack trace, and any linked `/docs/messages/` URL.
4. Distinguish root cause from symptom using the failure categories above.
5. For dev-only failures, verify against `next dev` and browser console / network. A passing production build does not prove a dev HMR bug is fixed.
6. For build failures, run `next build` cleanly and read the route table / prerender errors. Use `--debug-prerender` when server source maps are needed.
7. For version-sensitive APIs, consult the docs for the installed version before deciding.

## Phase 4: Smallest-fix rule

Inspect → reproduce → identify root cause → change the smallest coherent surface → run focused checks → verify through the original user-visible path.

Do not:

- rewrite working architecture
- add dependencies without a clear need
- convert Server Components to Client Components to silence errors
- disable framework checks merely to get a build
- clear caches as the final diagnosis without identifying why the failure occurred
- treat a successful component-level probe as an end-to-end fix

## Phase 5: Server / Client boundary discipline

The App Router defaults to Server Components. Treat Client Components as an explicit opt-in.

- Server Components are the default for `page.tsx`, `layout.tsx`, and most UI in `app/`.
- Add `"use client"` only where a client boundary is actually required: state/event handlers, lifecycle logic, browser-only APIs, custom hooks that depend on them.
- Keep client boundaries narrow. Interactive islands (`<Search />`, `<Modal />`, `<LikeButton />`) should be Client Components; surrounding static UI stays server-rendered.
- Pass data from Server Components to Client Components via serializable props. Functions (including event handlers) cannot cross as props.
- Use `children` / props to interleave Server Components inside Client Components without importing the Server Component into the client graph.
- Browser-only APIs / `window` / `document` / `localStorage` require a Client Component or a guarded hook.
- Server-only secrets and data access must stay out of the client bundle. Use `server-only` package when necessary.
- When a third-party component needs client features, wrap it in a thin Client Component rather than marking the whole page tree `"use client"`.

## Phase 6: Data / caching discipline

Inspect the installed version and `next.config.*` before reasoning about caching.

**Next.js 16+ with `cacheComponents: true`:**

- Default is dynamic / uncached. Opt into caching explicitly with `"use cache"`.
- Use `cacheLife()` inside a cached scope to set lifetime.
- Use `cacheTag()` + `revalidateTag()` / `updateTag()` for on-demand invalidation.
- Prefer tag-based revalidation over path-based.
- `updateTag` is Server Actions only and immediately expires cache (read-your-own-writes).
- `revalidateTag` is stale-while-revalidate and works in Server Actions and Route Handlers.
- `revalidatePath` invalidates by route path; use when tagging is overkill.
- `refresh()` refetches the current route's RSC Payload without invalidating tagged data.
- `use cache: private` allows runtime APIs (`cookies()`, `headers()`, `searchParams`) but stores only in browser memory.
- `use cache: remote` uses a remote cache handler; only worthwhile at high hit rates.
- `fetch` is not cached by default. Use `"use cache"` to opt in.

**Without Cache Components (older projects):**

- Caching uses `fetch` options (`cache`, `next.revalidate`, `next.tags`), `unstable_cache`, and route segment configs (`revalidate`, `dynamic`, etc.).
- Do not blindly apply `"use cache"` / `cacheLife` / `cacheTag` to older projects.
- When migrating, follow the [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components) guide.

## Phase 7: Navigation / routing discipline

- File-system routing in `app/`: folders are segments; `page.tsx` / `route.ts` makes a segment public.
- Layouts nest automatically and preserve state across navigations. Root layout must include `<html>` and `<body>`.
- Dynamic segments: `[slug]`, `[...slug]`, `[[...slug]]`; `params` is a promise — await it.
- Route groups `(group)` organize code without changing URLs; private folders `_folder` are not routable.
- Parallel routes use `@slot`; intercepting routes use `(.)`, `(..)`, `(..)(..)`, `(...)`.
- Prefer `<Link>` from `next/link` over raw `<a>` for client-side transitions and prefetching.
- Use `redirect()` / `permanentRedirect()` from `next/navigation` for server-side redirects; use `useRouter()` for programmatic navigation in Client Components.
- Use `notFound()` + `not-found.tsx` for 404 UI.
- Route handlers (`route.ts`) use Web Request/Response APIs; `GET` default is dynamic since v15.
- Proxy (`proxy.ts`) is the v16+ name for the former `middleware.ts`; use a `matcher` to avoid running on static assets.

## Phase 8: Build / debug verification

Use the project's package manager and existing scripts. Typical checks may include:

```bash
npm run build
npm run lint
npm test
npx tsc --noEmit
```

but do not invent these commands if the project does not define them.

For dev-only failures, verify through `next dev` + browser console / network / Next.js MCP (`get_errors`, `get_compilation_issues`, `compile_route`).

For build failures, read the route table symbols:

- `○` Static
- `◐` Partial Prerender
- `●` SSG
- `ƒ` Dynamic

Use `next build --debug-prerender` for source-mapped prerender errors. Do not deploy `--debug-prerender` builds.

## Phase 9: Migration / upgrade discipline

- Detect installed version first.
- For v16 upgrades, run the official codemod: `npx @next/codemod@latest upgrade latest`.
- Also run the async request API codemod if applicable: `npx @next/codemod@latest next-async-request-api .`
- Migrate `middleware.ts` → `proxy.ts` via `npx @next/codemod@canary middleware-to-proxy .`
- Replace `experimental.turbopack` / `experimental.ppr` / `experimental.useCache` / `experimental.dynamicIO` with their v16 equivalents per the [Version 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16).
- Update `package.json` scripts to remove `--turbopack` / `--turbo`; Turbopack is default in v16.
- Keep Webpack only with explicit `--webpack` flag if a custom webpack config is required.
- After upgrade, verify `AGENTS.md` points to `node_modules/next/dist/docs/` if available.

## Phase 10: Documentation hygiene

When an implementation-sensitive detail matters:

1. Prefer the bundled docs in `node_modules/next/dist/docs/` (version-matched).
2. Otherwise fetch the official page with `Accept: text/markdown` or append `.md` to the nextjs.org/docs URL.
3. Record the source URL beside version-sensitive claims.
4. If the Next.js MCP server (`next-devtools-mcp`) is available, use it for runtime state before guessing.
5. Do not claim the bundled references in this skill are permanently exhaustive or current.

## Critical anti-hallucination rules

- URLs are URLs, not local files. NPM package identifiers like `@next/bundle-analyzer` or `next/third-parties` are packages, not `@file:` references.
- Never rewrite package identifiers into pseudo-file references.
- If documentation extraction returns no content, treat it as an extraction failure and retry via the official page or another supported retrieval path. Do not interpret "no content" as proof the feature does not exist.
- Preserve contradictions between sources until resolved by a higher authority.
- Never claim a single ingested page makes the skill "complete" or "exhaustive."

## References

- `references/docs-index.md` — navigation + source inventory + ownership map
- `references/app-router.md` — App Router fundamentals and conventions
- `references/server-client-components.md` — Server/Client Component rules, boundary, interleaving
- `references/data-fetching-and-streaming.md` — fetching, streaming, Suspense, React.cache
- `references/mutations-and-server-actions.md` — Server Functions, Server Actions, forms, security
- `references/caching-and-revalidation.md` — Cache Components, `use cache`, `cacheLife`, `cacheTag`, revalidation
- `references/routing-and-navigation.md` — routing, layouts, Link, redirects, route handlers, Proxy
- `references/error-handling.md` — expected errors, error boundaries, `catchError`, `notFound`
- `references/configuration.md` — `next.config.*`, Turbopack config, serverActions, cacheComponents
- `references/css-images-fonts-metadata.md` — CSS, images, fonts, metadata, OG images
- `references/turbopack-and-build.md` — Turbopack, build output, prerender errors, bundle analysis
- `references/debugging-and-development.md` — dev server, HMR, debugging, MCP, local performance
- `references/deployment-and-production.md` — deploying, adapters, static export, Docker, self-hosting
- `references/testing.md` — Jest, Vitest, Playwright, Cypress
- `references/migration-and-upgrades.md` — v16 upgrade, codemods, Cache Components migration
- `references/source-manifest.md` — source provenance and authority notes

## Contributing to the skill

When ingesting a new Next.js documentation page:

1. Read the page completely.
2. Compare against existing references.
3. Extract only claims supported by that page.
4. Classify: operational rule → `SKILL.md`; durable knowledge → canonical reference; navigation → `docs-index.md`; duplicate → no change.
5. Merge, don't append.
6. Preserve contradictions and source URLs.
7. Keep each concept owned by one reference file; cross-link duplicates.
8. Report exactly what changed and why.
