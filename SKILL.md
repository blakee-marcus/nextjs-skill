---
name: nextjs
description: Build, modify, review, migrate, and debug Next.js applications using installed-version evidence and current official documentation.
version: 0.1.12
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
- `next.config.*` — router, output, turbopack, cacheComponents, serverActions, deploymentId, etc.
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

### New-project scaffolding discipline

When no project exists yet:

- Use the package manager selected by the user or surrounding workspace; otherwise choose one explicitly and use the matching `--use-*` flag.
- Prefer explicit flags over a bare `--yes` when configuration matters. In Next.js 16.3.8, `--yes` may reuse stored preferences, so it is not deterministic across machines.
- `create-next-app` initializes Git unless `--disable-git` is passed. If Git initialization or repository metadata changes are not already authorized, pass `--disable-git`.
- The current default includes `AGENTS.md` and `CLAUDE.md`; opt out with `--no-agents-md` only when those files are unwanted.
- Treat `--example <github-url>` as third-party code. Inspect the source/revision and generated manifest before trusting it or running further scripts.
- After scaffolding, inspect the generated `package.json` and config, then exercise the selected linter/type/build and browser-visible dev path. The generator exiting successfully is not end-to-end verification.

Source: [create-next-app v16.3.8](https://nextjs.org/docs/app/api-reference/cli/create-next-app), updated 2026-08-25.

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
- **Start server-first. Introduce `'use client'` at the smallest interactive boundary, and never promote a page/layout to client merely because one descendant needs browser behavior.**
- Keep client boundaries narrow. Interactive islands (`<Search />`, `<Modal />`, `<LikeButton />`) should be Client Components; surrounding static UI stays server-rendered.
- Pass data from Server Components to Client Components via serializable props. Functions (including event handlers) cannot cross as props.
- Use `children` / props to interleave Server Components inside Client Components without importing the Server Component into the client graph.
- Browser-only APIs / `window` / `document` / `localStorage` require a Client Component or a guarded hook.
- Server-only secrets and data access must stay out of the client bundle. Use `server-only` package when necessary.
- When a third-party component needs client features, wrap it in a thin Client Component rather than marking the whole page tree `"use client"`.
- Client Components render on the server too. A Client Component renders to HTML on the initial request, then hydrates in the browser. On client-side navigation it renders from the RSC payload without server-rendered HTML.
- A Server Component can start a fetch and pass the pending Promise to a Client Component, which unwraps it with React's `use()` inside a `<Suspense>` boundary.
- **Environment protection:** use `import 'server-only'` to enforce at build time that a module is never imported by client code; use `import 'client-only'` to enforce that a module requires browser APIs. Next.js handles these imports internally; explicit packages are optional.
- **Server Actions dispatch sequentially per client.** Next.js dispatches Server Actions one at a time per client; do not rely on `Promise.all` to parallelize actions from the client. Parallel work belongs inside a single Server Action, a Server Component, or a Route Handler. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))
- `useLinkStatus` from `next/link` returns `{ pending: boolean }` for visual feedback while a link transition is in flight; must be a descendant of a `<Link>` and is skipped if the target is already prefetched. Not supported in the Pages Router. Introduced in v15.3.0. ([use-link-status](https://nextjs.org/docs/app/api-reference/functions/use-link-status))
- `io()` from `next/cache` (v16.3.0+) marks a synchronous IO operation so it is excluded from the static shell. Prefer it over `connection()` because the code after it can still be cached/prefetched. Call before `new Date()`, `Math.random()`, `crypto.randomUUID()`, or synchronous drivers like `node:sqlite`. In a Client Component, use `use(io())`. No-op without `cacheComponents: true`. ([io](https://nextjs.org/docs/app/api-reference/functions/io))
- `connection()` from `next/server` indicates rendering should wait for an incoming request. Replaces `unstable_noStore`. Use when a component needs per-request output but doesn't use Request-time APIs (e.g., `Math.random()`, `new Date()`, `better-sqlite3`). With Cache Components, prefer `io()`. ([connection](https://nextjs.org/docs/app/api-reference/functions/connection))

## Phase 6: Data / caching discipline

Inspect the installed version and `next.config.*` before reasoning about caching.

**Next.js 16+ with `cacheComponents: true`:**

- Data fetching and asynchronous work are uncached by default; opt into reuse with `"use cache"`. Predictable synchronous work, module imports, and stable module-scope local-resource reads can still prerender automatically.
- Use `cacheLife()` inside a cached scope to set lifetime. Set it **explicitly in every `"use cache"` scope**: omitting it silently applies the `default` profile (`stale` 5m / `revalidate` 15m / `expire` never), and a nested short-lived cache under an unset parent throws during prerendering. `cacheLife()` must be called inside the cached function (not at module scope), at most once per invocation, and requires `cacheComponents: true`. ([cacheLife](https://nextjs.org/docs/app/api-reference/functions/cacheLife))
- Use `cacheTag()` + `revalidateTag()` / `updateTag()` for on-demand invalidation.
- Prefer tag-based revalidation over path-based.
- `updateTag` is Server Actions only and immediately expires cache (read-your-own-writes).
- `revalidateTag(tag, profile)` works in Server Actions and Route Handlers. Pass `'max'` for the recommended stale-while-revalidate behavior, or another profile / `{ expire: number }` to control the stale window. The single-argument form is deprecated in Next.js 16.3.8 and behaves like `{ expire: 0 }`; use `updateTag` for immediate Server Action read-your-own-writes.
- `revalidatePath` invalidates by route path; use when tagging is overkill. Regeneration is lazy on the next request.
- `refresh()` refetches the current route's RSC Payload without invalidating tagged data.
- `use cache: private` allows runtime APIs (`cookies()`, `headers()`, `searchParams`) but stores only in browser memory. It does **not** accept `connection()`.
- `use cache: remote` uses a remote cache handler; only worthwhile at high hit rates.
- `fetch` is not cached by default. Use `"use cache"` to opt in.
- Prevent avoidable waterfalls: start independent requests before awaiting them, then join with `Promise.all` (`Promise.allSettled` when partial failure is acceptable). Preload only through a function that deduplicates matching calls (`fetch`, `React.cache` for non-`fetch` work, or a Cache Function); calling an ordinary async function twice performs the work twice.
- `<Suspense>` contains async/runtime work; it does not itself make synchronous work dynamic. Push runtime API reads and async work into the smallest subtree that needs them so the surrounding static shell can still prerender.
- Nesting a short-lived `use cache` inside one without an explicit `cacheLife` fails the build during prerendering.
- The `next build` route table prints `Revalidate`/`Expire` columns for cached routes, using the shortest lifetime across all caches in the route.
- If uncached/runtime data is accessed outside `Suspense`, the build surfaces a `blocking-prerender-dynamic` / `blocking-prerender-runtime` error. Fix by streaming under `<Suspense>`, caching the value, or moving it into a Client Component. `export const instant = false` opts a segment out of instant-navigation validation but does **not** clear synchronous-IO build errors.
- **Short-lived caches create dynamic holes:** `revalidate: 0` or `expire` under 5 minutes excludes content from prerenders. `stale` under 30 seconds also excludes it; `stale` ≥30s but <5 minutes is included in prerenders but excluded from the route's App Shell. Of the presets, only `seconds` is fully excluded from prerenders.
- Synchronous IO (`new Date()`, `Date.now()`, `Math.random()`, `crypto.randomUUID()`) during prerender throws a build error that `instant = false` does not clear. Move it under `<Suspense>` with `connection()` or `io()` (Cache Components), or into a Client Component.
- Under `cacheComponents`, client hooks that read URL data (`useParams`, `usePathname`, `useSearchParams`, `useSelectedLayoutSegment`, `useSelectedLayoutSegments`) suspend during prerendering for dynamic params **not** covered by `generateStaticParams`. Wrap the calling component (or a parent) in `<Suspense>` or the build fails with `blocking-prerender-client-hook`. Static routes and params covered by `generateStaticParams` resolve on the server and need no Suspense. `useSelectedLayoutSegment`/`useSelectedLayoutSegments` accept a `parallelRouteKey` to read the active segment within a slot (e.g. `useSelectedLayoutSegment('auth')` returns `"login"` for `app/@auth/login`). `useParams` returns `null` on the initial render in the Pages Router, then updates once the router is ready. ([useParams](https://nextjs.org/docs/app/api-reference/functions/use-params))
- A `generateStaticParams` that returns an empty array is allowed: the route is dynamically rendered, or ISR-at-runtime with `export const dynamic = 'force-static'`. Under Cache Components, a **root parameter** must have at least one value or the build fails. With Cache Components, dynamic-route `generateStaticParams` must also return at least one param (not empty) so the build can prerender a static shell; unknown params still render at request time. ([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))
- Client-side cached content is stored in browser memory for the `stale` duration, with a minimum 30-second stale time enforced by the router regardless of configuration.
- `NEXT_PRIVATE_DEBUG_CACHE=1` enables verbose cache logging.

**Without Cache Components (older projects):**

- Caching uses `fetch` options (`cache`, `next.revalidate`, `next.tags`), `unstable_cache`, and route segment configs (`revalidate`, `dynamic`, etc.).
- Do not blindly apply `"use cache"` / `cacheLife` / `cacheTag` to older projects.
- When migrating, follow the [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components) guide.

## Phase 7: Navigation / routing discipline

- File-system routing in `app/`: folders are segments; `page.tsx` / `route.ts` makes a segment public.
- Layouts nest automatically and preserve state across navigations. Root layout must include `<html>` and `<body>`. Layouts are cached on the client and do not re-render, so they cannot access the raw request object, `searchParams`, or child route segments; use `headers()`/`cookies()` in Server Components and the appropriate client hooks for those values.
- Dynamic segments: `[slug]`, `[...slug]`, `[[...slug]]`; `params` is a promise — await it.
- Route groups `(group)` organize code without changing URLs; private folders `_folder` are not routable.
- Parallel routes use `@slot`; intercepting routes use `(.)`, `(..)`, `(..)(..)`, `(...)`. Intercepting-route matchers are based on **route segments, not the file system** (`@slot` folders do not count). Intercepting routes are not supported with `output: 'export'`.
- Prefer `<Link>` from `next/link` over raw `<a>` for client-side transitions and prefetching.
- Use `redirect()` / `permanentRedirect()` from `next/navigation` for server-side redirects; use `useRouter()` for programmatic navigation in Client Components.
- Use `notFound()` + `not-found.tsx` for 404 UI.
- Route handlers (`route.ts`) use Web Request/Response APIs. Without Cache Components, Route Handlers are uncached by default and only `GET` can opt into caching (for example with `dynamic = 'force-static'`); mutation methods remain uncached even when colocated with a cached `GET`.
- A `route.ts` file **cannot** exist at the same route segment as `page.ts`.
- With Cache Components enabled, `GET` Route Handlers run at request time by default but deterministic handlers can prerender. Request properties, uncached/network/DB/async-filesystem work, runtime APIs, or nondeterministic operations stop prerendering. Cache uncached work in an extracted `use cache` helper; `use cache` cannot appear directly in the handler body. ([route-handlers](https://nextjs.org/docs/app/getting-started/route-handlers))
- Proxy (`proxy.ts`) is the v16+ name for the former `middleware.ts`; create a single file at project root, export `proxy` or default, and use a `matcher` to avoid running on static assets.
- `window.history.pushState` / `replaceState` integrate with the Next.js Router and sync `usePathname` / `useSearchParams`.
- `useRouter().push` / `replace` must never receive untrusted or unsanitized URLs — `javascript:` URLs execute in the page context (XSS). Validate/encode any user input before navigating programmatically. ([useRouter](https://nextjs.org/docs/app/api-reference/functions/use-router))
- `useRouter().prefetch(href, { kind })` supports `kind: 'full' | 'partial' | 'auto'` (default `'auto'`) as of v15.4.0; `router.prefetch(href, { onInvalidate })` fires when prefetched data goes stale. `router.bfcacheId` is an opaque per-segment id that changes on push/replace and stays stable across back/forward and `router.refresh()`; key a component on it only as a last resort. ([useRouter](https://nextjs.org/docs/app/api-reference/functions/use-router))
- `router.push(href, { scroll: false })` disables the default scroll-to-top on navigation. `router.push`/`router.replace` accept an optional `transitionTypes` array (e.g. `['nav-forward']`) passed to `React.addTransitionType` for view-transition animations. ([useRouter](https://nextjs.org/docs/app/api-reference/functions/use-router))
- App Router Web Vitals reporting uses `useReportWebVitals` imported from `next/web-vitals` (not `next/navigation`); wrap it in a small `'use client'` component imported by the root layout so the client boundary stays narrow. ([useReportWebVitals](https://nextjs.org/docs/app/api-reference/functions/use-report-web-vitals))
- `<Link>` supports `transitionTypes` to drive React `<ViewTransition>` directional animations (e.g. `['nav-forward']`, `['nav-back']`).
- `useLinkStatus` from `next/link` returns `{ pending: boolean }` for visual feedback while a link transition is in flight; must be a descendant of a `<Link>` and is skipped if the target is already prefetched. Not supported in the Pages Router.
- With Partial Prefetching enabled, `<Link>` prefetches each route's App Shell by default. For URL-specific cached content (`searchParams`, dynamic `params`), set `prefetch={true}` on the link.
- Partial Prefetching is the default behavior with Cache Components. See [Adopting Partial Prefetching](/docs/app/guides/adopting-partial-prefetching) for migration patterns.
- When `prefetch={true}` resolves URL-specific cached content before navigation, the destination must use Partial Prefetching (global `partialPrefetching` or segment `prefetch = 'partial'`). Each visible `<Link prefetch={true}>` incurs a server invocation per prefetchable link; only opt in when the traffic justifies resolving more content before the click. ([optimizing-prefetching](https://nextjs.org/docs/app/guides/optimizing-prefetching))
- `<Link>` App Router props: `href` (required, string or URL object), `replace` (default `false`), `scroll` (default `true`), `prefetch` (`boolean`, `"auto"`, or `null`; default `"auto"`/null), `onNavigate` (called during client-side navigation, can `preventDefault()`), `transitionTypes` (`string[]` for React `<ViewTransition>`). ([link](https://nextjs.org/docs/app/api-reference/components/link))
- `<Form>` from `next/form` with a string `action` uses `GET`, encodes data as search params, and navigates via client-side transition in the App Router (prefetching shared UI when `prefetch` is true); with a Server Action it behaves like a React form. `method`, `encType`, `target`, and their `form*` equivalents are not supported. ([form](https://nextjs.org/docs/app/api-reference/components/form))
- `next/script` strategies: `beforeInteractive` (server-rendered in `<head>`, executes before Next.js code but does not block hydration), `afterInteractive` (default, client-side after some hydration), `lazyOnload` (idle), `worker` (experimental; not supported in App Router). `beforeInteractive` must be in a root layout (App Router) or `_document` (Pages Router) and runs once per document load; not re-executed on client-side navigations. ([script](https://nextjs.org/docs/app/api-reference/components/script))
- Route Segment Config exports: `dynamicParams` (boolean, default `true`; not available when Cache Components is enabled), `runtime` (`'nodejs'` default, `'edge'` deprecated), `preferredRegion` (deprecated), `maxDuration` (seconds). As of v16.0.0, `dynamic`, `dynamicParams`, `revalidate`, and `fetchCache` are removed when Cache Components is enabled. ([route-segment-config](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config))
- `instant` segment config only works when `cacheComponents` is enabled; cannot be used in Client Components. Accepts `true`, `false`, or `{ level: 'warning' }`. ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))
- `prefetch` segment config only works when `cacheComponents` is enabled; cannot be used in Client Components. Values: `'auto'` (default/omit), `'partial'`, `'force-disabled'`. ([prefetch](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch))
- `instrumentation-client.js|ts` runs client-side before the app becomes interactive; only synchronous top-level code is guaranteed before hydration. Export `onRouterTransitionStart(url, navigationType)` to observe App Router navigation starts; enable `experimental.instrumentationClientRouterTransitionEvents` for a third `event` argument. ([instrumentation-client](https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client))
- `error.js` / `error.tsx` must be Client Components; wraps `loading.js`, `not-found.js`, `page.js`, and nested `layout.js` in a React error boundary; does not wrap the `layout.js` or `template.js` in the same segment. Receives `error`, `retry()` (stable since v16.3.0), and `reset()`. ([error](https://nextjs.org/docs/app/api-reference/file-conventions/error))
- `forbidden.js` / `forbidden.tsx` renders UI when `forbidden()` is invoked; returns 403. Introduced v15.1.0. ([forbidden](https://nextjs.org/docs/app/api-reference/file-conventions/forbidden))
- `default.js` is the parallel-route fallback when a slot has no matching active state on hard navigation; for implicit `children`, missing `default.js` returns 404. ([default](https://nextjs.org/docs/app/api-reference/file-conventions/default))

## Phase 8: Build / debug verification

Use the project's package manager and existing scripts. Typical checks may include:

```bash
npm run build
npm run lint
npm test
npx tsc --noEmit
```

but do not invent these commands if the project does not define them.

- For dev-only failures, verify through `next dev` + browser console / network / Next.js MCP (`get_errors`, `get_compilation_issues`, `compile_route`).
- For build failures, run `next build` cleanly and read the route table / prerender errors. Use `--debug-prerender` when server source maps are needed.
- Treat `--debug-build-paths` as a narrowing tool only; finish verification with a full build because a selected-route build does not validate the rest of the application.
- `next experimental-analyze` does not produce deployable build artifacts and cannot substitute for `next build`.
- `--experimental-upload-trace` transmits a debugging trace to a remote URL. Do not invoke it without approval for that external transmission.
- With `npm run`, insert `--` before Next.js CLI flags so npm forwards them; pnpm, Yarn, and Bun do not require the separator.
- Use `NEXT_PRIVATE_DEBUG_CACHE=1` for verbose cache logging.
- Test offline behavior with `next build && next start`, not `next dev`.
- For version-sensitive APIs, consult the docs for the installed version before deciding.

For build failures, read the route table symbols:

- `○` Static
- `◐` Partial Prerender
- `●` SSG
- `ƒ` Dynamic

Use `next build --debug-prerender` for source-mapped prerender errors. Do not deploy `--debug-prerender` builds.

When a build fails because a route reads `params`, `searchParams`, `cookies()`, `headers()`, `connection()`, or uncached `fetch`/DB calls outside `Suspense`, the fix is one of: (1) wrap the data access in `Suspense` (or add `loading.tsx`), (2) cache the access with `"use cache"`, or (3) set `export const instant = false` to explicitly allow a blocking route. Validate instant navigation in development when Cache Components is enabled; set `validationLevel` to control automatic vs manual validation.

After a fix, rerun the original failing command and verify through the original user-visible path. A passing component-level probe is not an end-to-end fix.

## Phase 9: Migration / upgrade discipline

- Detect installed version first.
- For installed Next.js 16.1+, use the built-in upgrade command: `npx next upgrade --revision latest`. For earlier versions, use `npx @next/codemod@latest upgrade latest`.
- Also run the async request API codemod if applicable: `npx @next/codemod@latest next-async-request-api .`
- Migrate `middleware.ts` → `proxy.ts` via `npx @next/codemod@canary middleware-to-proxy .`
- Replace `experimental.turbopack` / `experimental.ppr` / `experimental.useCache` / `experimental.dynamicIO` with their v16 equivalents per the [Version 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16).
- Update `package.json` scripts to remove `--turbopack` / `--turbo`; Turbopack is default in v16.
- Set `output: 'export'` for static/SPA exports; be aware that Server Actions, dynamic routes without `generateStaticParams`, Rewrites/Redirects/Headers/Proxy, ISR, and default `next/image` loader are unsupported.
- Keep Webpack only with explicit `--webpack` flag if a custom webpack config is required.
- When migrating to Cache Components, follow [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components): enable `cacheComponents: true`, remove `dynamic`/`revalidate`/`fetchCache` segment configs, replace `unstable_cache` with `'use cache'`, wrap runtime data in `Suspense`, and ensure `generateStaticParams` returns at least one param under Cache Components.
- The `cache-components-instant-false` codemod can opt every `page`, `layout`, and `default` out of instant-navigation validation in one pass during incremental adoption.
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
- Once streaming has started, the HTTP status code and headers are committed. `notFound()` mid-stream injects a `noindex` meta tag rather than returning `404`, and `redirect()` becomes a client-side redirect.
- Under Cache Components, a **root parameter** must have at least one value in `generateStaticParams` or the build fails; `dynamicParams` is not supported with Cache Components (unknown params render on request — reject with `notFound()` if needed).
- `redirect()` / `permanentRedirect()` from `next/navigation` throw; call them outside `try/catch` blocks.
- `next/root-params` getters are **Server Components only** — importing them in a Client Component or using them in a Server Action/Route Handler is a build/runtime error. Root segment names must be valid JS identifiers (kebab-cased `[post-slug]` is unsupported and errors). Do **not** use `next/root-params` inside `unstable_cache` (throws at runtime); use `"use cache"` instead. ([next/root-params](https://nextjs.org/docs/app/api-reference/functions/next-root-params))
- `await cookies()` from `next/headers` — it is async since v15.0.0-RC (synchronous in v14 and earlier). Cookies can only be **set/deleted inside a Server Action or Route Handler**, never during Server Component render, and never after streaming has started. Reading `cookies()` opts the route into dynamic rendering. ([cookies](https://nextjs.org/docs/app/api-reference/functions/cookies))
- `cacheTag()` accepts one or more strings and is idempotent, but tags are capped at 128 per call and 256 characters each; over-limit tags are dropped with a console warning. ([cacheTag](https://nextjs.org/docs/app/api-reference/functions/cacheTag))
- Intercepting-route matchers work on **route segments, not the file system** — `(..)` means one route level up, and parallel-route slots do not count as a segment. ([intercepting-routes](https://nextjs.org/docs/app/api-reference/file-conventions/intercepting-routes))
- Proxy runs on **every** request when no `matcher` is set (including `_next/static`, `_next/image`, and `public/`); use a negative-match pattern. Note that Proxy still runs for `_next/data` routes even when a negative matcher excludes them. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- A Proxy `matcher` that excludes a path also **skips Server Function (Server Action) calls** on that path — Server Functions are `POST` requests to the route where they are used, not separate routes in the Proxy chain. A `matcher` change or refactor can silently drop Proxy authz for those actions. **Always verify authentication and authorization inside each Server Function**; never rely on Proxy as the sole gate. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Treat every Server Action as a public mutation endpoint.** Keep actions thin; validate input, authenticate, authorize the specific resource, and delegate database work to a `server-only` DAL. Return only fields the UI needs, and consider rate limiting for expensive or abuse-prone operations. ([data-security](https://nextjs.org/docs/app/guides/data-security))
- **Classify errors before choosing control flow.** Return expected operational failures (validation errors, failed requests) as explicit values and surface them with `useActionState` or conditional Server Component UI. Throw unexpected failures so the nearest error boundary can handle them. Error boundaries do not catch event-handler or post-render async failures; catch those manually and store UI state. Unhandled errors thrown inside `startTransition` do bubble to the nearest boundary. ([error-handling](https://nextjs.org/docs/app/getting-started/error-handling))
- **`loading.js` fallback gap with runtime data in layouts.** If a layout accesses uncached or runtime data (e.g. `cookies()`, `headers()`, or uncached fetches), `loading.js` will **not** show a fallback for it — without Cache Components, navigation blocks until the layout finishes rendering; with Cache Components, uncached/runtime data access in the layout must be explicitly wrapped in `<Suspense>` (otherwise Next.js raises a build-time error), and the static shell streams first while the uncached content fills in. To ensure instant navigation, move uncached data fetching from `layout.js` into `page.js`, or wrap the runtime data access in the layout in its own `<Suspense>` boundary. `loading.js` wraps `not-found.js`, `page.js`, and nested `layout.js` files in a `<Suspense>` boundary; it does **not** wrap `layout.js`, `template.js`, or `error.js` in the same segment. ([loading](https://nextjs.org/docs/app/api-reference/file-conventions/loading))
- In Server Actions, `redirect()` / `permanentRedirect()` use client-side navigation when JavaScript is available and fall back to a `303` form submission without JavaScript.
- Test offline behavior with `next build && next start`, not `next dev`.
- `serverComponentsHmrCache` caches `fetch` responses across HMR refreshes in dev; enabled by default since the option exists. Caching applies to all fetches, including `cache: 'no-store'`; clear the cache by navigating or reloading.
- For slow local dev, prefer local `next dev` over Docker on macOS/Windows, scope Tailwind `content` to source files, and avoid broad barrel imports.
- Turbopack tracing: use `next dev --internal-trace`, then `npx next internal trace .next-profiles/trace-turbopack.bin` and view at https://trace.nextjs.org/.
- `mdx-components.tsx` is required for App Router MDX support; place it at project root (or `src/` root) and export `useMDXComponents`.
- `next/dynamic` is for Client Components only in App Router; Server Components are automatically code-split. Use `ssr: false` only inside Client Components.
- `webpackIgnore` / `turbopackIgnore` skip bundling a dynamic import for runtime-only modules.
- `turbopackOptional` suppresses build errors when a module might not exist (runtime throws if executed).
- Turbopack supports `import.meta.glob()` (Vite-compatible). Not available with webpack.
- The `instant` and `prefetch` route segment exports only work when `cacheComponents` is enabled and cannot be used in Client Components.
- `dynamicParams` is not available when `cacheComponents` is enabled.
- `runtime = 'edge'` and `preferredRegion` are deprecated; remove those exports from route files. `runtime = 'edge'` is not supported with Cache Components.
- **Edge Runtime constraints.** Edge code (deprecated `runtime = 'edge'` and Proxy) uses a Web-standard API subset only: `fetch`, Web Streams, `crypto` (Web Crypto), `URL`/`URLPattern`, `WebSocket`, `TextEncoder`/`TextDecoder`, etc. Node.js APIs such as `fs`, `path`, `http`, `net`, `crypto` (Node module), `Buffer`, `child_process`, `stream`, `zlib`, `dns`, and direct `require()` are **not supported**. Dynamic code evaluation (`eval`, `new Function(...)`, `WebAssembly.compile`/`instantiate`) is disabled unless opted out per file via `unstable_allowDynamic`. Fetches and redirects must use absolute URLs.
- **`after()` from `next/server` is **not** a Request-time API — calling it does **not** make a route dynamic. If used inside a static page or layout, the callback runs at build time (or on revalidation), not per request. It runs even on unsuccessful responses and can be nested. Server Components cannot call `cookies()`/`headers()` inside the `after` callback (throws at runtime) — read request data during render and pass values into the callback via closure. Can be used in Server Components (including `generateMetadata`), Server Functions, Route Handlers, and Proxy. Use React `cache` to deduplicate functions called inside `after`. Duration controlled by platform default or `maxDuration`. ([after](https://nextjs.org/docs/app/api-reference/functions/after))
- **Synchronous IO build errors** (`new Date()`, `Date.now()`, `Math.random()`, `crypto.randomUUID()` during prerender) are **not** cleared by `instant = false`; move the call under a `<Suspense>` boundary with `connection()`/`io()`, or into a Client Component.
- **Proxy execution order:** (1) `headers` from `next.config.js` → (2) `redirects` from `next.config.js` → (3) **Proxy** (rewrites/redirects) → (4) `beforeFiles` rewrites → (5) filesystem routes (`public/`, `_next/static/`, `pages/`, `app/`) → (6) `afterFiles` rewrites → (7) dynamic routes → (8) `fallback` rewrites. A Proxy `matcher` that excludes a path also skips Server Function (Server Action) calls on that path — always verify authz inside each Server Function. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Proxy + custom fetch rewrites:** during RSC requests Next.js strips internal Flight headers (`rsc`, `next-router-state-tree`, `next-router-prefetch`) from the `request` instance in Proxy. If you implement custom rewrite logic with `fetch()` instead of `NextResponse.rewrite()`, forward those headers manually or enable `skipProxyUrlNormalize`. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Proxy advanced flags** (v13.1+): `skipTrailingSlashRedirect` disables Next.js' trailing-slash redirects for incremental migration; `skipProxyUrlNormalize` disables URL normalization so direct visits and client transitions receive the same (original) URL. For backward compatibility, Next.js always treats `/public` as `/public/index`, so a matcher of `/public/:path` will match. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Proxy runtime:** in v16, Proxy defaults to the Node.js runtime; `runtime` segment config is not available in Proxy and throws if set. `middleware.js|ts` is deprecated and renamed to `proxy.js|ts`; migrate with `npx @next/codemod@canary middleware-to-proxy .`. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Template remounting:** `template.js` receives a unique key per segment. It remounts when that segment (including its dynamic params) changes; navigations within deeper segments do NOT remount higher-level templates; search params do NOT trigger remounts. Use this to reset Client Component state (form inputs) and re-synchronize `useEffect` on navigation. Unlike `layout.js`, Suspense boundaries inside templates show their fallback on every navigation, not just first load. ([template](https://nextjs.org/docs/app/api-reference/file-conventions/template))
- `updateTag(tag)` is **Server-Action-only** and *immediately expires* the tag so the next request waits for fresh data (read-your-own-writes); it throws in Route Handlers. `revalidateTag(tag, profile)` works in Server Actions **and** Route Handlers; `profile="max"` gives stale-while-revalidate (recommended). Tags are case-sensitive and capped at 256 characters. The single-argument `revalidateTag(tag)` form is **deprecated** (equivalent to `{ expire: 0 }`) — migrate to `updateTag` in Actions or `revalidateTag(tag, "max")` elsewhere. ([updateTag](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/updateTag.mdx), [revalidateTag](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/revalidateTag.mdx))
- `unstable_cache` is **replaced by `use cache` in Next.js 16**. It persists across deployments; `use cache` defaults to in-memory and is scoped to one deployment. The cached function cannot call `connection()`, enable/disable draft mode, call revalidation APIs, or use `use cache: private`. ([unstable_cache](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_cache.mdx))
- `unstable_noStore` is **deprecated in v15** in favor of `connection()`. Equivalent to `cache: 'no-store'` on fetch. Calling it inside `unstable_cache` does NOT opt out of static generation. ([unstable_noStore](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_noStore.mdx))
- `forbidden()` and `unauthorized()` from `next/navigation` require `experimental.authInterrupts: true` in `next.config.*`. Both throw (`never` return type), cannot be called in root layout, and must be called outside `try/catch` (or use `unstable_rethrow`). `forbidden()` renders `forbidden.js` with 403; `unauthorized()` renders `unauthorized.js` with 401. Introduced in v15.1.0. ([forbidden](https://nextjs.org/docs/app/api-reference/functions/forbidden), [unauthorized](https://nextjs.org/docs/app/api-reference/functions/unauthorized))
- `forbidden()`/`unauthorized()` left in an un-awaited promise throw where nothing catches it — no UI renders. In dev: `⨯ unhandledRejection: NEXT_HTTP_ERROR_FALLBACK;403` / `;401`. Always `await` the function that may call them. ([forbidden](https://nextjs.org/docs/app/api-reference/functions/forbidden), [unauthorized](https://nextjs.org/docs/app/api-reference/functions/unauthorized))
- `permanentRedirect(path, type)` issues a **308 permanent** redirect; `redirect(path, type)` issues a **307 temporary**. Both throw (`never` return type). Default type is `replace` (everywhere except Server Actions, where default is `push`). The `type` argument has **no effect in Server Components**. In Server Actions, `redirect` performs client-side navigation when JS is available, or serves `303` for form submissions. ([permanentRedirect](https://nextjs.org/docs/app/api-reference/functions/permanentRedirect), [redirect](https://nextjs.org/docs/app/api-reference/functions/redirect))
- `notFound()` throws `NEXT_HTTP_ERROR_FALLBACK;404` and terminates rendering of the route segment. Next.js injects `<meta name="robots" content="noindex" />`. Cannot be called in root layout. A `try/catch` around it suppresses the interrupt — use `unstable_rethrow` or `isNextNotFound` from `next/navigation`. ([notFound](https://nextjs.org/docs/app/api-reference/functions/not-found))
- **`cookies().delete` domain/protocol rules:** `.delete()` can only be called from a Server Function or Route Handler, must belong to the **same domain** from which `.set()` was called (wildcard domains require an exact subdomain match), and must run on the same protocol (HTTP/HTTPS) as the cookie being deleted. ([cookies](https://nextjs.org/docs/app/api-reference/functions/cookies))
- **`serverComponentsHmrCache` default-on gotcha.** The experimental `serverComponentsHmrCache` option defaults to `true`. It caches all `fetch` responses in Server Components across HMR refreshes in dev, including fetches with `cache: 'no-store'`. Navigation or a full-page reload clears it; disable with `serverComponentsHmrCache: false` if you need fresh data on every HMR refresh. ([serverComponentsHmrCache](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverComponentsHmrCache))
- **`cacheHandler` (singular) ≠ `cacheHandlers` (plural).** `cacheHandler` is the server ISR / route-handler / image cache (renamed from the deprecated `incrementalCacheHandlerPath` — do **not** use `incrementalCacheHandlerPath` on v14.1.0+). It is **not** the handler for `'use cache'` Cache Components; that is `cacheHandlers` (plural). Confusing the two points cache config at the wrong layer and silently no-ops. `cacheHandlers` stores `ReadableStream` entries and is not supported with static export; adapter support is platform-specific. ([cacheHandler](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandler), [cacheHandlers](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandlers))
- **`deploymentId` affects version skew and `'use cache'` keys.** Set it per deployment for rolling/multi-server deploys. It appends `?dpl=<id>` to static assets, adds `x-deployment-id`/`x-nextjs-deployment-id` headers, injects `data-dpl-id` on `<html>`, and participates in the `'use cache'` cache key. `config.deploymentId` takes precedence over `NEXT_DEPLOYMENT_ID`; on mismatch the client hard reloads. `generateBuildId` has no effect on version-skew detection when `deploymentId` is set. ([deploymentId](https://nextjs.org/docs/app/api-reference/config/next-config-js/deploymentId))
- **`next.config.*` extension support:** only `.js`, `.mjs`, and `.ts` are supported. `.cjs` and `.cts` are NOT supported. ([next.config](https://nextjs.org/docs/app/api-reference/config/next-config-js))
- **Sass `functions` are webpack-only.** Custom Sass functions via `sassOptions.functions` are only supported with webpack; Turbopack's Rust architecture cannot execute JavaScript functions passed via this option. ([sassOptions](https://nextjs.org/docs/app/api-reference/config/next-config-js/sassOptions))
- **Immutable-asset `Cache-Control` cannot be overridden.** For assets whose filenames contain a SHA hash (e.g. static image imports), Next.js forces `public, max-age=31536000, immutable`; you cannot set `Cache-Control` for them in `next.config.js` (the `headers()` key is ignored for those files). ([headers](https://nextjs.org/docs/app/api-reference/config/next-config-js/headers))
- **Server Action wildcard rules.** `serverActions.allowedOrigins` patterns use `*` for one label and `**` for one or more labels (only at the start of a pattern). Ports must be literal (`my-proxy.com:8443`); partial replacement (`app-*.my-proxy.com`) is invalid. Requests without an `Origin` header are allowed with a warning. The default `bodySizeLimit` of 1MB applies to the **raw HTTP body** including `multipart/form-data` boundaries, headers, and metadata. ([serverActions](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions))
- **`reactMaxHeadersLength` (App Router only).** Default 6000 bytes. Lower it if a reverse proxy truncates long React preloading headers. ([reactMaxHeadersLength](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactMaxHeadersLength))
- **`trailingSlash` exceptions.** `trailingSlash: true` redirects `/about` → `/about/` but does not touch static file URLs (extensions) or paths under `.well-known/`. ([trailingSlash](https://nextjs.org/docs/app/api-reference/config/next-config-js/trailingSlash))
- **`typescript.ignoreBuildErrors` bypasses type checks entirely.** It skips the TypeScript step, not just suppresses errors. Run type checks elsewhere in the deploy pipeline when disabled. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- **`urlImports` lockfile must be committed.** `next.lock` is created when using `urlImports`; do not `.gitignore` it — builds rely on the lockfile. ([urlImports](https://nextjs.org/docs/app/api-reference/config/next-config-js/urlImports))
- **`instrumentationClientInject`** (v16.3.0) is for `next.config.js` plugins (e.g. `withSentry`) to inject client instrumentation modules before the project's `instrumentation-client.{js,ts}`. Application code should use the `instrumentation-client.{js,ts}` file convention directly. Each injected module may export `onRouterTransitionStart(url, navigationType)`. ([instrumentationClientInject](https://nextjs.org/docs/app/api-reference/config/next-config-js/instrumentationClientInject))
- **`typedRoutes` is stable.** Use `typedRoutes: true` at top-level, not under `experimental`. Requires TypeScript. ([typedRoutes](https://nextjs.org/docs/app/api-reference/config/next-config-js/typedRoutes))
- **`transpilePackages`/`serverExternalPackages` are mutually exclusive.** A package cannot appear in both; the build throws. ([transpilePackages](https://nextjs.org/docs/app/api-reference/config/next-config-js/transpilePackages), [serverExternalPackages](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverExternalPackages))
- **`supportsImmutableAssets` is adapter-author territory.** It omits the `?dpl` query from content-addressed static assets, enabling indefinite browser caching and deploy-time skipping of unchanged assets. Enabling without provider/adapter support can break deployments. ([supportsImmutableAssets](https://nextjs.org/docs/app/api-reference/config/next-config-js/supportsImmutableAssets))
- **`staleTimes` defaults changed.** `dynamic` default is `0s` (changed from 30s in v15.0.0); `static` default is 5 minutes. Only affects client cache TTLs for pages. ([staleTimes](https://nextjs.org/docs/app/api-reference/config/next-config-js/staleTimes))
- **`turbopackMemoryEviction` (experimental, v16.3.0).** Controls in-memory Turbopack cache eviction after persistent storage has been written. Three options: `false` (never evict), `'auto'` (default; evict after a snapshot once enough memory allocated), `'full'` (evict all possible data on every disk save). ([turbopackMemoryEviction](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackMemoryEviction))
- **`turbopackIgnoreIssue` path matching.** Suppresses Turbopack issues when `path` matches; prefer `path` over `title`/`description` because issue titles/descriptions change between versions. Only works when using Turbopack. ([turbopackIgnoreIssue](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackIgnoreIssue))
- **`turbopackChunking` knobs.** Production client chunker: `minChunkSize` (50000), `maxChunkCountPerGroup` (40), `maxMergeChunkSize` (200000); app-only `generateComponentChunks`/`minComponentChunkSize`; heuristic options `clusters`, `firstPageLoadPriority`, `priorityRoutes`, `priorityBoost`, `requestCost`. ([turbopackChunking](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackChunking))
- **`redirects` matching semantics.** `redirects()` is sync or async; each rule supports `source` (path matching with regex), `destination`, `permanent` (default false, controls 308 vs 307), `has` and `missing` header/cookie/query conditions, and `locale`/`basePath` handling. Rewrites are checked first, then redirects, then `beforeFiles`/`afterFiles`/`fallback` rewrites. ([redirects](https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects))
- **`proxyClientMaxBodySize` per-request limit.** Buffers request bodies in memory when Proxy is used; default 10MB. Set as string or bytes. Exceeding the limit logs a warning and continues with a partial body. ([proxyClientMaxBodySize](https://nextjs.org/docs/app/api-reference/config/next-config-js/proxyClientMaxBodySize))
- **`lightningCssFeatures` include/exclude groups.** Works with both Turbopack and webpack (when `useLightningcss: true`). Values can be feature names (e.g. `nesting`, `oklab-colors`) or composite groups (`selectors`, `media-queries`, `colors`). ([useLightningcss](https://nextjs.org/docs/app/api-reference/config/next-config-js/useLightningcss))
- **`reactStrictMode` app-default since v13.5.1.** Strict Mode is enabled by default for the app router; only set the option explicitly for `pages` or to opt out with `false`. ([reactStrictMode](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactStrictMode))
- **`taint` isn't a DAL substitute.** Enables React Taint APIs; copying a tainted object or deriving values from it removes taint. Values are only tainted while the original reference is in scope. ([taint](https://nextjs.org/docs/app/api-reference/config/next-config-js/taint))
- **`staticGeneration` worker tuning.** `staticGenerationRetryCount`, `staticGenerationMaxConcurrency`, `staticGenerationMinPagesPerWorker`. ([staticGeneration](https://nextjs.org/docs/app/api-reference/config/next-config-js/staticGeneration))
- **`serverExternalPackages` renamed and stabilized.** Was `serverComponentsExternalPackages` (deprecated). Next.js auto-externalizes many popular packages; see `server-external-packages.jsonc` before adding entries. ([serverExternalPackages](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverExternalPackages))

- **Pages Router API Routes are same-origin by default.** They do not emit CORS headers unless you add them explicitly. ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes), [forms](https://nextjs.org/docs/pages/guides/forms))
- **Pages Router Draft Mode uses `res.setDraftMode`, not `draftMode()` from `next/headers`.** In an API Route, call `res.setDraftMode({ enable: true })` to set the `__prerender_bypass` cookie; read it in `getStaticProps`/`getServerSideProps` via `context.draftMode` and in API Routes via `req.draftMode`. Linking to a route that disables draft mode requires `prefetch={false}` on `next/link` so prefetch doesn't delete the cookie. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- **Custom `.babelrc` must include `next/babel` and keep `preset-env.modules: false`.** A custom Babel config becomes the source of truth; omitting `next/babel` breaks compilation, and setting `preset-env.modules` to anything other than `false` disables webpack code splitting. ([babel](https://nextjs.org/docs/pages/guides/babel))
- **Pages Router i18n is configured under the top-level `i18n` key in `next.config.js`, not via dynamic root segments.** It supports ≤100 locales and ≤100 domain items, does not work with `output: 'export'`, and uses `NEXT_LOCALE` cookie priority over `Accept-Language`. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- **Pages Router API Routes are same-origin only by default.** They do not emit CORS headers unless you add them explicitly. Use `res.setHeader('Access-Control-Allow-Origin', '*')` or a CORS helper for cross-origin access. ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes))
- **Pages Router API Route `bodyParser.sizeLimit`** controls the maximum parsed body size (e.g., `'1mb'`, `'500kb'`). Disable `bodyParser` entirely to consume the body as a Stream (useful for webhook verification). ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes))
- **Pages Router API Route `responseLimit`** warns when response body exceeds 4MB. Set to `false` to disable (only if not serverless). Can take byte count or string (`'8mb'`). ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes))
- **Pages Router API Route `externalResolver: true`** tells Next.js the route is handled by an external resolver (express/connect) and disables unresolved-request warnings. ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes))
- **Pages Router API Route route precedence:** predefined > dynamic > catch-all. `pages/api/post/create.js` matches `/api/post/create` before `pages/api/post/[pid].js`. ([api-routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes))
- **Pages Router `pages/_document` event handlers don't work.** `_document` only renders on the server; `onClick` and similar props are ignored. Use `next/head` in pages/components for per-page `<head>` changes. ([custom-document](https://nextjs.org/docs/pages/building-your-application/routing/custom-document))
- **Pages Router `pages/_error.js` is production-only.** In dev, the error overlay shows instead. It handles both client and server errors via the `Error` component. ([custom-error](https://nextjs.org/docs/pages/building-your-application/routing/custom-error))
- **Pages Router `pages/404.js` and `pages/500.js` are statically generated at build time** and can use `getStaticProps` if build-time data is needed. ([custom-error](https://nextjs.org/docs/pages/building-your-application/routing/custom-error))
- **Pages Router `getInitialProps` in `App` disables Automatic Static Optimization** for pages without `getStaticProps`. This pattern is not recommended; prefer App Router for page/layout data fetching. ([custom-app](https://nextjs.org/docs/pages/building-your-application/routing/custom-app))

## References

- `references/docs-index.md` — navigation + source inventory + ownership map
- `references/app-router.md` — App Router fundamentals and conventions
- `references/server-client-components.md` — Server/Client Component rules, boundary, interleaving, **Edge Runtime constraints**
- `references/data-fetching-and-streaming.md` — fetching, streaming, Suspense, React.cache
- `references/mutations-and-server-actions.md` — Server Functions, Server Actions, forms, security
- `references/data-security.md` — DAL, tainting, Server Action security, audit checklist
- `references/caching-and-revalidation.md` — Cache Components, `use cache`, `cacheLife`, `cacheTag`, revalidation
- `references/routing-and-navigation.md` — routing, layouts, Link, redirects, route handlers, Proxy
- `references/error-handling.md` — expected errors, error boundaries, `catchError`, `notFound`
- `references/configuration.md` — `next.config.*`, Turbopack config, serverActions, cacheComponents, **webpack / TypeScript 7 CLI / ESLint flat config / web vitals attribution**
- `references/css-images-fonts-metadata.md` — CSS, images, fonts, metadata, OG images
- `references/turbopack-and-build.md` — Turbopack, build output, prerender errors, bundle analysis, **CLI flags / `next typegen` / CPU profiling**
- `references/debugging-and-development.md` — dev server, HMR, debugging, MCP, local performance
- `references/deployment-and-production.md` — deploying, adapters, static export, Docker, self-hosting, **adapter output types / PPR resume protocol / immutable static assets**
- `references/testing.md` — Jest, Vitest, Playwright, Cypress
- `references/migration-and-upgrades.md` — v16 upgrade, codemods, Cache Components migration
- `references/ai-agents.md` — bundled docs, `AGENTS.md`, MCP, Next.js skills
- `references/pages-router.md` — Pages Router API Routes, error boundaries, custom app/document, automatic static optimization
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

<!-- CANARY-GUIDES-2026-08-30 -->
## Canary guides ingest — agent rules (2026-08-30)

Operational rules distilled from `docs/01-app/02-guides/` (canary). Treat as hard constraints when generating Next.js App Router code:

- **Cache Components gate**: Partial Prefetching, `use cache`, and ISR-with-Cache-Components behavior require `cacheComponents: true` in `next.config`. Without it, those guides do not apply.
- **Prefetch URL-data rule**: `cookies()` and `headers()` do NOT make a prefetch URL-specific — only `params`/`searchParams` are URL data. Do not assume session cookies scope a prefetched App Shell.
- **Statically-analyzable `revalidate`**: `revalidate = 600` is valid; `revalidate = 60 * 10` is NOT (must be statically analyzable). `revalidate` is unavailable under deprecated `runtime = 'edge'`.
- **Backend boundary**: Route Handlers/Server Actions are a public API layer, NOT a full backend. Validate input before calling other systems; use `POST` (not `GET`) for sensitive payloads.
- **Custom server**: only when the integrated router cannot meet requirements — it opts out of automatic optimizations.
- **Never deploy `--debug-prerender` builds** — they skip production optimizations.
- **`generateStaticParams` must return ≥1 param** or the build fails.
- **Secrets**: cache keys/tags are stored in plain text — never put secrets in cache arguments or `cacheTag` values; expose only narrow fields from session helpers.
- **Build output route table**: `○` static, `◐` Partial Prerender, `●` SSG, `ƒ` Dynamic. Read these to diagnose build results.
- **Per-link prefetching**: `<Link prefetch={true}>` resolves URL-specific cached content before navigation; requires `partialPrefetching` (global or segment `prefetch = 'partial'`). Each such link incurs a server invocation per prefetchable link.
- **Draft Mode entry/exit asymmetry**: entry uses `GET` (CMS opens preview URL in new tab), exit uses `POST` (Server Action or POST Route Handler). Draft Mode sets `__prerender_bypass` cookie.
- **CDN caching gap**: `revalidateTag`/`revalidatePath` invalidate only the Next.js server cache. CDNs keep serving until `s-maxage` expires; call your CDN purge API alongside revalidation for HTML + RSC variants.
- **Multi-instance revalidation**: `revalidateTag()` is local by default. For multi-instance coordination, implement `updateTags()` (write to shared storage) and `refreshTags()` (periodically read before a new request) in the custom cache handler. Catch errors in `refreshTags()` so requests continue with last-known local tag state.
- **`validationLevel`**: `'warning'` (default) validates every Page/Default segment in dev. Set `'manual-warning'` to only validate segments explicitly exporting `instant`.

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
## Canary architecture / Pages Router ingest — agent rules (2026-09-02)

Hard constraints distilled from `docs/03-architecture/` and substantive `docs/02-pages/02-guides/` pages (canary):

- **Custom PostCSS config disables all defaults.** Creating any PostCSS config file replaces Next.js's built-in PostCSS behavior entirely; you must manually add Autoprefixer and required plugins. Do not assume default transforms still run.
- **Preview Mode is legacy and uses `res.setPreviewData`.** For Pages Router only; the equivalent modern feature is Draft Mode. `setPreviewData` stores data in a 2 KB cookie; clearing it on a `next/link` requires `prefetch={false}`.
- **Relay `artifactDirectory` must live outside `pages/`.** Otherwise generated `__generated__` files are treated as routes and break production builds.
- **Polyfills in App Router go in `instrumentation-client` (synchronous).** Dynamic/conditional imports there may run after hydration.
- **SWC minification cannot be customized since v15.** The `swcMinify` option is removed.
- **Fast Refresh state preservation fails for anonymous default arrow components.** Use the `name-default-component` codemod or name the component.
