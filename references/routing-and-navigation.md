# Routing and Navigation

Reference: https://nextjs.org/docs/app/getting-started/linking-and-navigating

## File-system routing

- Folders in `app/` are route segments.
- `page.tsx` / `route.ts` makes a segment public.
- Layouts nest automatically and preserve state across navigation.

### Dynamic segments

- `[slug]` — single param
- `[...slug]` — catch-all
- `[[...slug]]` — optional catch-all
- `params` is a promise in v15+; await it.
- Dynamic segments are passed to `layout`, `page`, `route`, and `generateMetadata`.
- `generateStaticParams` accepts an optional `options.params` argument containing the populated params from a parent `generateStaticParams` — use this to generate child params based on parent output in routes with multiple dynamic segments.
- Root parameters (segments before the root layout) can also be read with `next/root-params` from any Server Component.
- In Client Components, unwrap `params` with React `use()` or use the `useParams` hook.
- Type helpers `PageProps<'/route'>`, `LayoutProps<'/route'>`, and `RouteContext<'/route'>` generate types for `params` values (`string`, `string[]`, or `undefined`).

### Root parameters (`next/root-params`)

- Root parameters are dynamic segments that appear **before** the root layout (e.g. `app/[lang]/layout.js`). Import the named getter and `await` it: `import { lang } from 'next/root-params'` → `await lang()`.
- **Server Components only.** Cannot be used in Client Components (import fails the build), Server Actions, or Route Handlers (Route Handler support is planned). No `import 'server-only'` is needed — the build already fails in a Client Component.
- Root segment names must be **valid JS identifiers**; kebab-cased segments like `[post-slug]` are not supported and error at dev/build time.
- Do **not** call a root-param getter inside `unstable_cache` (throws at runtime) — use `"use cache"` instead.
- With Cache Components, a `generateStaticParams` is required and each root param must have at least one value or the build fails.
- Root-param getters are tracked **per cached function**: only the root params a `'use cache'` function actually reads become part of its cache key, so entries are not split across unrelated param values.
- With multiple root layouts, a param missing from some of them is typed `string | undefined`, and `await id()` returns `undefined` on routes whose root layout lacks that segment.
- Introduced in **v16.3.0**.
([next/root-params](https://nextjs.org/docs/app/api-reference/functions/next-root-params))

### Route groups and private folders

- `(group)` — URL-less organization; can share layouts or opt routes into/out of layouts.
- `_folder` — not routable; safe for co-located components/lib.
- Caveats: navigating between routes that use different root layouts triggers a full page reload (multiple-root-layout case only).
- Routes in different groups must not resolve to the same URL path (e.g. `(marketing)/about/page.js` and `(shop)/about/page.js` both → `/about` errors).
- With multiple root layouts and no top-level `layout.js`, ensure the home route (`/`) is defined inside one of the groups (e.g. `app/(marketing)/page.js`).

### Route group patterns

- **Multiple root layouts**: remove the top-level `layout.js`, then add a `layout.js` inside each route group. Each root layout must include its own `<html>` and `<body>` tags. Useful for sections with completely different UI.
- **Nested layouts within the existing root layout**: when route groups have layouts beneath an existing top-level `layout.js`, those group layouts nest inside the existing app layout.
- **Opt-in layouts**: move routes that share a layout into a route group (e.g. `(shop)`). Routes outside the group do not share that layout.
- **Loading skeletons on a specific route**: wrap the target route in a route group (e.g. `/(overview)`) and place `loading.tsx` inside the group so it applies only to that route without affecting sibling URLs.

## Parallel and intercepting routes

- `@slot` — named slot rendered by parent layout.
- `(.)folder` — intercept same level.
- `(..)folder` — intercept parent.
- `(..)(..)folder` — intercept two levels.
- `(...)folder` — intercept from root.

## Navigation APIs

### `<Link>` prop summary

App Router props:

| Prop | Type | Notes |
|---|---|---|
| `href` | `string` or `object` | Required. Supports pathname + query object. |
| `replace` | `boolean` | Default `false`; replaces current history entry instead of pushing. |
| `scroll` | `boolean` | Default `true`; scrolls to top on navigation, preserves position for back/forward. `scroll={false}` prevents scrolling to the first Page element. |
| `prefetch` | `boolean`, `"auto"`, or `null` | `null`/ `"auto"` = prefetch on hover. |
| `onNavigate` | `function` | Called before navigation; `event.preventDefault()` cancels it. |
| `transitionTypes` | `string[]` | Drives React `<ViewTransition>` animations (e.g. `['nav-forward']`, `['nav-back']`). |

Pages Router props additionally include `as`, `shallow`, and `locale`.

### `<Link>` prefetch behavior

- Prefetches automatically in production as each `<Link>` enters the viewport.
- **Static routes**: the full route is prefetched.
- **Dynamic routes**: without a `loading.tsx` boundary the full page is not prefetched; with `loading.tsx` only layouts up to the first loading boundary are prefetched.
- Use `prefetch={true}` for per-link eager prefetching that resolves URL-specific content (`params`, `searchParams`, full URL). With Partial Prefetching enabled, this is the only way to prefetch URL-specific data.
- Use `prefetch={false}` to disable prefetching entirely (useful for long lists where prefetching everything is wasteful).
- Use `prefetch={null}` to prefetch only on hover, limiting work to links the user is likely to click.
- In the App Router, `prefetch` accepts `boolean`, `"auto"`, or `null`. `null` is treated as the same as `"auto"`.

### Prefetching side-effects gotcha
If your layouts or pages are not pure and have side-effects (e.g. tracking analytics), Next.js might run them when the route is **prefetched**, not when the user visits the page. To avoid this, move side-effects to a `useEffect` hook or a Server Action triggered from a Client Component. (Source: https://nextjs.org/docs/app/guides/prefetching)

### `useRouter().prefetch()` options
- `router.prefetch(href, { kind: 'auto' })` — v15.4.0+: `kind: 'full' | 'partial' | 'auto'` (default). `partial` prefetches only the App Shell under Partial Prefetching.
- `router.prefetch(href, { onInvalidate })` — v15.4.0: `onInvalidate` fires once when prefetched data goes stale, so you can refresh the prefetch.
- `router.bfcacheId` — opaque per-segment id that changes on push/replace and stays stable across back/forward and `router.refresh()`. With `cacheComponents`, the router preserves Client state via React `<Activity>`, so key a component on `bfcacheId` only as a last resort.

### Partial Prefetching

With `partialPrefetching: true` (requires `cacheComponents`; introduced in Next.js 16.3.0), each visible `<Link>` prefetches the destination's **App Shell** by default. The App Shell contains rendered output that does not depend on a link's URL (no `params`, `searchParams`, or request-time data). Links to the same route share one App Shell prefetch.

A destination segment can opt into Partial Prefetching without enabling the global flag by exporting `prefetch = 'partial'` from its `page.tsx` or `layout.tsx`. A segment can also disable prefetching entirely with `prefetch = 'force-disabled'`. The `prefetch` segment config only works when `cacheComponents` is enabled and cannot be used in Client Components.

With the App Shell, uncached data streams in after navigation behind `<Suspense>` boundaries. Invalidations (`revalidateTag`, `revalidatePath`) silently refresh associated prefetches.

### `default.js` (parallel route fallback)

The `default.js` file renders a fallback for unmatched parallel-route slots during initial load or full-page reload. On soft navigation, Next.js preserves each slot's active state; on hard navigation (full-page reload), it can't recover that state, so it renders `default.js` for unmatched slots. If `default.js` doesn't exist for an unmatched named slot, a `404` is rendered — you can replicate the old 404 behavior by exporting a `default.js` that calls `notFound()`. Since `children` is an implicit slot, you also need a `default.js` to render a fallback for `children` when its state can't be recovered. ([default](https://nextjs.org/docs/app/api-reference/file-conventions/default))

### `template.js` (remount on navigation)

`template.js` is rendered between `layout.js` and its children, and is given a unique key per segment. Unlike `layout.js` (which persists across navigations), templates remount when that segment (including dynamic params) changes. Use templates to: resynchronize `useEffect` on navigation, reset child Client Component state (e.g. form inputs), or make Suspense boundaries inside templates show their fallback on every navigation (not just first load). `template.js` wraps `error.js`, `loading.js`, `not-found.js`, and `page.js`, but does **not** wrap the `layout.js` in the same segment. ([template](https://nextjs.org/docs/app/api-reference/file-conventions/template))

### `proxy.ts` (Middleware renamed in v16+)

In Next.js 16+, the `middleware` file convention has been **deprecated** and renamed to `proxy`. The function signature, capabilities, and `matcher` config are identical — only the file and export names changed. A `proxy.ts` file exports a single `proxy` function (or default export) that receives `request: NextRequest` and optionally `event: NextFetchEvent`. Use `event.waitUntil()` to schedule background work. The file must be at the project root (or `src/` root) at the same level as `pages`/`app`. If `pageExtensions` is customized (e.g. `.page.ts`), name the file `proxy.page.ts`. Without a `matcher`, Proxy runs on **every** request including `_next/static` and `_next/image`. The `runtime` segment config is **not available** in Proxy and throws if set. Proxy defaults to Node.js runtime in v16. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))

### `instrumentation-client.js` (client-side instrumentation)

The `instrumentation-client.js|ts` file runs before the app becomes interactive. It can contain monitoring code directly (no specific exports required). Optionally export `onRouterTransitionStart(url, navigationType, event?)` to observe App Router navigation start; enable `experimental.instrumentationClientRouterTransitionEvents` for a third `event` argument with `id`, `timestamp`, `fromRoutes`, and `prefetchIntent`. Implement try-catch blocks around instrumentation code to prevent individual tracking failures from affecting other features. ([instrumentation-client](https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client))

### `instrumentation.js` (server-side instrumentation)

The `instrumentation.js|ts` file is placed at the root of the application (or inside `src/`). It can export:
- `register()` — called **once** when a new Next.js server instance starts; must complete before the server is ready.
- `onRequestError(err, request, context)` — track server errors to custom observability providers. The `error` may be processed by React (not the original thrown instance); use `digest` to identify the actual error type.

Use this for OpenTelemetry, Sentry, Datadog, etc. ([instrumentation](https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation))

| `<Link>` prop | Behavior |
|---|---|
| `<Link href="/x">` (default) | Loads the shared App Shell. |
| `<Link href="/x" prefetch={true}>` | Loads the App Shell plus URL-specific content (`params`, `searchParams`, full URL). |
| `<Link href="/x" prefetch={false}>` | Disables prefetching. |
| `<Link href="/x" prefetch={null}>` | Prefetches only on hover. |

Audit existing `prefetch={true}` calls when enabling Partial Prefetching and remove the ones that no longer need URL-specific resolution:
- Fully static/cached content → remove redundant `prefetch={true}`.
- Uncached content → cache it with `use cache`, then remove `prefetch={true}`.
- Content behind `cookies()`/`headers()` → pass the session value into a cached function or use `"use cache: private"`; remove `prefetch={true}`.
- URL data (`params`/`searchParams`) → keep `prefetch={true}` to resolve content ahead of the click.
- Real-time content that must stay fresh → remove `prefetch={true}` and let it stream in.

> **Good to know:** If you use `<Link prefetch={true}>` to a route that hasn't opted into Partial Prefetching, a dev console error suggests enabling `partialPrefetching` app-wide or `prefetch = 'partial'` on the segment.

### Optimizing prefetching

Set `prefetch={true}` when:
- Part of the tree depends on URL data (`searchParams`, `params` not covered by `generateStaticParams`, or full URL).
- That part has a known cache lifetime (`"use cache"` or `"use cache: private"`).
- Traffic justifies the per-link server invocation.

Avoid it when:
- The route has little URL-data dependency (App Shell is already instant).
- The dependent content must be fresh on every request (prerender stops at the same `<Suspense>` fallback).
- The route is rarely navigated to (you pay per visible link regardless of click-through).

For grids of many links, prefer intent-based prefetching (hover) instead of per-link `prefetch={true}`.

| | App Shell | Per-link `prefetch={true}` |
|---|---|---|
| Scope | One per route | One per visible `<Link>` |
| Content | Route render minus per-link data | Plus per-link URL data resolved |
| Cost | Bounded by route count | Bounded by visible-link count |
| Role | Default prefetch | More rendered before click |

### Instant navigation

A navigation is **instant** when the browser can start rendering the new page immediately on click, with the static shell/fallback content showing right away and the rest streaming in. Requires Cache Components.

Validation:
- `instant` only works when `cacheComponents` is enabled and cannot be used in Client Components.
- Next.js validates routes in development for instant navigation.
- The `instant` export accepts `true`, `false`, or an object with `level: 'warning'`.
- Set `validationLevel: 'manual-warning'` in `experimental.instantInsights` to opt out of automatic validation and only validate segments that export `instant`.
- Export `instant = true` from a page or layout to assert that navigations into it should be instant.
- Export `instant = false` from a page or layout to opt that segment out of validation (useful when an ancestor blocks but descendants should still be instant).
- Reading `params` or `searchParams` outside `<Suspense>` ties the App Shell to a URL and triggers the URL-data insight; fix by wrapping the URL-specific read in `<Suspense>` or exporting `instant = false`.
- A `false` `instant` config higher in the route tree takes precedence over deeper `true` configs for the static-shell check.
- Framework-synthesized error routes (`/_global-error`, `/_not-found`) are excluded from implicit validation.
- **Status-code caveat for instant-blocking routes:** `instant = false` opts a segment out of instant-navigation validation, but it does not change the streaming status-code behavior. If `notFound()` or a redirect runs after streaming has started, the response status is already committed to `200`; real 404/redirect status codes must be decided before streaming starts (e.g. in Proxy, `next.config.js` redirects, or by wrapping runtime access in `<Suspense>`). ([instant navigation](https://nextjs.org/docs/app/guides/instant-navigation), [loading status codes](https://nextjs.org/docs/app/api-reference/file-conventions/loading#status-codes))

### `<Link>` scroll behavior

`<Link>` performs client-side transitions: shared layouts and UI are preserved, only the page content is replaced. Scroll is reset to the top by default; use the `scroll` prop or CSS `scroll-padding-top` for sticky-header offsets. When `scroll={false}`, Next.js will not attempt to scroll to the first Page element. The default scroll behavior maintains position for back/forward navigation.

### `onNavigate`

`<Link>` accepts an `onNavigate` callback invoked when the link is clicked, before navigation starts. Call `event.preventDefault()` inside it to cancel the navigation.

### `transitionTypes`

`<Link>` supports `transitionTypes` to drive React `<ViewTransition>` directional animations (e.g. `['nav-forward']`, `['nav-back']`).

### `useLinkStatus`

```tsx
'use client'

import { useLinkStatus } from 'next/link'

export default function LoadingIndicator() {
  const { pending } = useLinkStatus()
  return <span className={pending ? 'is-pending' : ''} aria-hidden />
}
```

Use `useLinkStatus` to show immediate visual feedback while a `<Link>` transition is in progress. This is especially useful on slow or unstable networks where prefetching may not finish before the user clicks.

- Must be used in a component that is a **descendant of a `<Link>`**; it reads the enclosing link's transition state.
- The pending state is **skipped entirely** if the target route was already prefetched — so the hook is most useful together with `prefetch={false}` on the `<Link>`.
- On rapid successive clicks across links, only the **last** link's pending state is shown.
- **Not supported in the Pages Router** — it always returns `{ pending: false }` there.
- Inline indicators cause layout shift; prefer a fixed-size element that is always rendered and toggled via opacity/animation.
- Returns exactly one property: `pending: boolean` — `true` before the history entry updates, `false` after. Takes no parameters. Introduced in `v15.3.0`.
- **You might not need it:** if the destination is static and prefetched in production the pending phase may never appear, and a `loading.js` file already gives an instant route-level fallback. Treat `useLinkStatus` as a targeted patch for an identified slow transition, then fix the root cause (prefetching or `loading.js`).
- To avoid a flash on fast navigations, start the hint invisible (`opacity: 0`, `visibility: hidden` to reserve space) and add an animation delay (~100ms).
([use-link-status](https://nextjs.org/docs/app/api-reference/functions/use-link-status))

### `useRouter`

For programmatic navigation in Client Components:

```tsx
'use client'

import { useRouter } from 'next/navigation'

const router = useRouter()
router.push('/dashboard')
router.replace('/dashboard')
router.refresh()
router.back()
router.forward()
router.prefetch('/dashboard', { kind: 'auto' })  // v15.4.0+: kind: 'full' | 'partial' | 'auto' (default)
```

### Client navigation hooks — operational rules (canary)

Import these from `next/navigation` (Client Components only), except `useReportWebVitals` which comes from `next/web-vitals`.

- **`useRouter` security:** never pass untrusted or unsanitized URLs to `router.push` / `router.replace` — `javascript:` URLs execute in the page context (XSS). Validate/encode any user input before navigating. ([useRouter](https://nextjs.org/docs/app/api-reference/functions/use-router))
- **`useRouter` extras:** `router.refresh()` clears the Client Cache for the route but does **not** invalidate server-side cache (use `revalidatePath`/`revalidateTag`). `router.push(href, { scroll: false })` disables scroll-to-top. `router.push`/`router.replace` accept an optional `transitionTypes` array (e.g. `['nav-forward']`) passed to `React.addTransitionType` for view-transition animations. `router.prefetch(href, { onInvalidate })` (v15.4.0) — `onInvalidate` fires once when prefetched data goes stale. `router.bfcacheId` is an opaque per-segment id that changes on push/replace and stays stable across back/forward and `router.refresh()`; with `cacheComponents`, the router preserves Client state via React `<Activity>`, so key a component on `bfcacheId` only as a last resort. ([useRouter](https://nextjs.org/docs/app/api-reference/functions/use-router))
- **`useSearchParams` always needs `<Suspense>` in prod:** a statically prerendered route that calls `useSearchParams` from a Client Component must be wrapped in `<Suspense>` or the production build fails (`Missing Suspense boundary with useSearchParams`). In dev it appears to work without it. Prefer reading the Page `searchParams` prop in a Server Component when possible. **Prerendering behavior:** During prerendering, `searchParams` is an empty `ReadonlyURLSearchParams` — it's only available on the client after hydration. If a page is not statically prerendered (uses `getServerSideProps` or is dynamically rendered), `searchParams` is available during SSR. If the app includes a `/pages` directory, `useSearchParams` returns `ReadonlyURLSearchParams | null` for migration compatibility. ([useSearchParams](https://nextjs.org/docs/app/api-reference/functions/use-search-params))
- **`usePathname` + rewrites:** when a page is reached via a `next.config` rewrite or `proxy` rewrite, `usePathname()` may read the rewritten pathname on the client and cause a hydration mismatch. Isolate the pathname-dependent UI and render a stable server fallback, then update after mount. ([usePathname](https://nextjs.org/docs/app/api-reference/functions/use-pathname))
- **`useReportWebVitals`** is imported from `next/web-vitals` (not `next/navigation`), requires `'use client'`, and is most performant as a small component imported by the root layout so the client boundary stays narrow. The `metric` object includes: `id` (unique per page load), `name` (TTFB, FCP, LCP, FID, CLS, INP), `delta`, `entries`, `value`, `rating` (`"good"` / `"needs-improvement"` / `"poor"`), `navigationType` (`"navigate"`, `"reload"`, `"prerender"`, `"back-forward"`, `"back-forward-cache"`, `"restore"`, `"soft-navigation"`), `navigationId`, `navigationURL`, `navigationStartTime`, and `navigationInteractionId`. Custom metrics: `Next.js-hydration`, `Next.js-route-change-to-render`, `Next.js-render`. ([useReportWebVitals](https://nextjs.org/docs/app/api-reference/functions/use-report-web-vitals))

- **`userAgent`** is a **server** helper from `next/server` (used in `proxy.ts`/Route Handlers), not a client hook. Returns an object with `isBot`, `browser` (name/version), `device` (model/type/vendor), `engine` (name/version), `os` (name/version), `cpu` (architecture). `device.type` can be `'mobile'`, `'tablet'`, `'console'`, `'smarttv'`, `'wearable'`, `'embedded'`, or `undefined` (desktop). ([userAgent](https://nextjs.org/docs/app/api-reference/functions/userAgent))
- **URL-reading hooks need `<Suspense>` under `cacheComponents`:** `useParams`, `usePathname`, `useSearchParams`, `useSelectedLayoutSegment`, `useSelectedLayoutSegments` read URL data. When `cacheComponents` is enabled, for dynamic params **not** covered by `generateStaticParams` these hooks suspend during prerendering — wrap the calling component (or a parent) in `<Suspense>` or the build fails (`blocking-prerender-client-hook`). Static routes and params covered by `generateStaticParams` resolve on the server and need no Suspense. `useSelectedLayoutSegment`/`useSelectedLayoutSegments` accept a `parallelRouteKey` to read the active segment within a slot (e.g. `useSelectedLayoutSegment('auth')` returns `"login"` for `app/@auth/login`). `useParams` returns `null` on the initial render in the Pages Router, then updates once the router is ready. **Important:** This applies even when the component that calls `useSelectedLayoutSegment` is itself static — e.g. a tab bar rendered in a parent layout suspends on any page below it that has an unknown dynamic param. Wrap the component that calls the hook (or a parent) in `<Suspense>` with a fallback to keep the rest of the layout prerendered. The same applies to `usePathname` in a sidebar with active links rendered in a layout — it suspends on any page below it with an unknown dynamic param. ([useSelectedLayoutSegment](https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segment), [useSelectedLayoutSegments](https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segments), [useParams](https://nextjs.org/docs/app/api-reference/functions/use-params))

### Native History API

`window.history.pushState` and `window.history.replaceState` work with the Next.js Router. Calls integrate with `usePathname` and `useSearchParams`, so you can update the URL without a full page reload.

Use `pushState` to add a history entry the user can navigate back to (e.g. updating sort order). Use `replaceState` to replace the current entry (e.g. switching locale).

### `redirect` / `permanentRedirect`

Server-side redirects from `next/navigation`:

```tsx
import { redirect } from 'next/navigation'

if (!user) redirect('/login')
```

| API | Allowed in | JS available | No JS | Normal context |
|---|---|---|---|---|
| `redirect()` | Server Components, Route Handlers, Server Functions/Actions | client-side navigation | `303` (Server Action form submission) | `307` Temporary Redirect |
| `permanentRedirect()` | Server Components, Route Handlers, Server Functions/Actions | client-side navigation | `303` (Server Action form submission) | `308` Permanent Redirect |

- `redirect()` throws a control-flow exception; code after it does not run. Call it outside `try/catch` blocks.
- In Client Components it can only be called during render, not in event handlers (use `useRouter` there).
- Both accept absolute URLs for external links.
- `redirect()` / `permanentRedirect()` have a `never` return type, so `return redirect(...)` is not required (but harmless). `redirect()` uses `307` (temporary) and `permanentRedirect()` uses `308` (permanent) to preserve the request method.
- Both throw the internal `NEXT_REDIRECT` token (distinct from the `NEXT_HTTP_ERROR_FALLBACK;<code>` token used by `notFound`/`unauthorized`/`forbidden`) — never swallow it in a `catch`.
- `permanentRedirect()` is also usable in **Client Components** (during render), not just Server Components/Route Handlers/Server Functions.
- The optional `type` argument (`'push' | 'replace'`) defaults to **`push` in Server Actions** and **`replace` everywhere else**, and has **no effect in Server Components**.
- To redirect before rendering, use `next.config.js` `redirects` (runs before Proxy) or Proxy.
- **Catch + redirect:** in a `try/catch` block, if a called Server Action or nested function might throw `redirect`/`notFound`/`unauthorized`/`forbidden`, import `isNextNotFound`, `isNextRedirect`, `isNextUnauthorized`, or `isNextForbidden` from `next/navigation` and rethrow if the caught error matches. ([not-found](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/not-found.mdx), [unauthorized](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unauthorized.mdx))

### `redirects` in `next.config.js`

- `async redirects()` returns an array of `{ source, destination, permanent?, basePath?, has?, missing? }`.
- `permanent: true` returns `308`; `permanent: false` returns `307`. Next.js uses 307/308 (not 302/301) to **preserve the request method** — a `POST /v1/users` redirect stays `POST /v2/users`, not silently downgraded to `GET`.
- `redirects` runs **before** Proxy and **before** the filesystem (pages + `/public`).
- Path matching uses path-to-regexp: `:slug` (param), `:slug*` (wildcard/catch-all), `:slug(\d{1,})` (regex in parens). Regex-special chars used literally in `source` must be escaped (`\(` etc.).
- `has` / `missing` arrays enable header/cookie/host/query conditional matching. `value` supports regex capture (`first-(?<paramName>.*)` → `:paramName` usable in destination). All `has` items must match and all `missing` items must not match.
- `basePath: false` excludes a redirect from auto-`basePath` prefixing (use for external redirects).
- Query values provided in the request are passed through to the redirect destination.
- Platform limits may apply (e.g. Vercel limits 1,024 redirects). For 1,000+ redirects, use a scalable Proxy solution (Bloom filter + Route Handler/API Route lookup) instead of a large static list.

### `rewrites` in `next.config.js`

- `rewrites` maps an incoming path to a destination **without changing the URL** (URL proxy). Contrast with `redirects`, which change the address bar.
- Returns either an array (applied after filesystem + before dynamic routes) or an object of arrays for fine control:
  - `beforeFiles` — checked after headers/redirects, before all files (including `_next/public`).
  - `afterFiles` — checked after pages/public files, before dynamic routes.
  - `fallback` — checked after dynamic routes, before rendering 404.
- Routing order: headers → redirects → Proxy → `beforeFiles` → filesystem → `afterFiles` → dynamic routes → `fallback`.
- `source` uses path-to-regexp (same as redirects). `has`/`missing` supported. `basePath: false` for external rewrites.
- Parameters not used in `destination` are automatically passed in the query; parameters used in `destination` are not (pass them manually if needed).
- `beforeFiles` rewrites do not stop at the first filesystem match — they continue until all `beforeFiles` entries are checked.

### `NextResponse.redirect` / `NextResponse.rewrite` in Proxy

- Proxy runs **after** `redirects` and **before** rendering.
- Use `NextResponse.redirect(new URL(...))` for dynamic/conditional redirects.
- Use `NextResponse.rewrite(new URL(...))` for A/B testing, feature flags, or multi-zone routing.
- For 1,000+ redirects, keep a redirect map in a fast key-value store and use a Bloom filter to avoid loading the full map into Proxy.

### `notFound`

```tsx
import { notFound } from 'next/navigation'

if (!post) notFound()
```

Triggers the nearest `not-found.tsx`.

### Multi-zones

Multi-zones split a domain into separate Next.js applications. Each zone is a normal Next.js app with an `assetPrefix` to avoid static-asset collisions (the extra rewrite for assets is not needed in Next.js 15+). Route requests between zones with `rewrites` or Proxy. Links between zones must use a native `<a>` tag, not `<Link>`, because `<Link>` tries to soft-navigate relative paths. For Server Actions across zones, add the user-facing origin to `serverActions.allowedOrigins`; use wildcards according to `allowedOrigins` rules (`*` one label, `**` one or more labels at start; ports cannot be wildcarded).

## Route Handlers (`route.ts`)

- Custom request handlers using Web Request/Response APIs.
- Supported methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`. Unsupported methods return `405 Method Not Allowed`.
- Without Cache Components, Route Handlers are uncached by default; only `GET` can opt into caching, for example with `export const dynamic = 'force-static'`. Other methods (`POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`) remain uncached even when exported beside a cached `GET`. This is the default model since v15.0.0-RC. ([route handlers](https://nextjs.org/docs/app/getting-started/route-handlers))
- With Cache Components enabled, `GET` handlers run at request time by default but deterministic handlers can prerender. Prerendering stops when a handler uses network requests, database queries, async filesystem operations, request properties (`request.url`, `.headers`, `.cookies`, `.body`), runtime APIs (`cookies()`, `headers()`, `connection()`), or nondeterministic operations such as `Math.random()`.
- Cache uncached work in an extracted `use cache` helper to include it in the prerendered response; `use cache` cannot be placed directly in a Route Handler body. Cached results revalidate according to their `cacheLife` when a new request arrives.
- A `route.ts` file **cannot** exist at the same route segment as `page.ts`.
- Route Handlers do not participate in layouts or client-side navigation.
- Dynamic `GET` Route Handlers can be statically generated by exporting `generateStaticParams`.
- `params` is a promise in v15+; await it.
- `NextRequest` from `next/server` extends Web Request with `nextUrl`, cookie helpers.
- TypeScript: use the globally available `RouteContext<'/path/[id]'>` helper for the context parameter.
- Special Route Handlers (`sitemap.ts`, `opengraph-image.tsx`, `icon.tsx`, etc.) remain static by default unless they use request-time APIs or dynamic config.
|- `create-next-app --api` scaffolds an example `route.ts` in `app/`.
|- If `OPTIONS` is not explicitly defined, Next.js auto-implements it and sets the `Allow` header based on the other exported methods.
|- `request` is a `NextRequest` (extends the Web `Request`) exposing `nextUrl` and cookie helpers; `context.params` is a Promise.
|- `NextRequest.ip` and `NextRequest.geo` were **removed in v15.0.0** — do not suggest them; read geo/IP from platform-provided headers instead. ([next-request](https://nextjs.org/docs/app/api-reference/functions/next-request))
|- In the App Router, `request.nextUrl` exposes only `basePath`, `buildId`, `pathname`, and `searchParams`. The Pages-Router i18n properties (`locale`, `locales`, `defaultLocale`, `domainLocale`, `url`) are **not** available. ([next-request](https://nextjs.org/docs/app/api-reference/functions/next-request))
|- Cookies: read/set via `cookies()` from `next/headers`, read via `request.cookies`, or set a `Set-Cookie` header on the returned `Response`.
|- Headers: read via `headers()` from `next/headers` (read-only); set by returning a new `Response` with `headers`.
|- Request body: parse with `request.json()`, `request.formData()`, or `request.text()`. No `bodyParser` config is needed (unlike Pages Router API Routes).
|- CORS: set `Access-Control-*` headers via the Web APIs; for many handlers, use Proxy or `next.config.js` `headers` instead.
|- Webhooks: handle `POST` by reading `request.text()`; no `bodyParser` config needed.
|- Streaming: return a `ReadableStream` (or `StreamingTextResponse` from `ai`) as the `Response` body (common for LLM output).
|- Non-UI responses: return `sitemap.xml`, `robots.txt`, app icons, or Open Graph images (built-in support) or custom content like `rss.xml`.
|- Revalidate cached data with the `revalidate` segment config (e.g. `export const revalidate = 60`).
|- Route Handlers were introduced in Next.js 13.2.0. ([route handlers](https://nextjs.org/docs/app/getting-started/route-handlers))

### `NextRequest` / `NextResponse`

- `NextRequest` extends Web `Request` with `nextUrl` (pathname, searchParams, basePath, buildId) and cookie helpers (`get`, `getAll`, `set`, `delete`, `has`, `clear`). `request.nextUrl.searchParams` is a `URLSearchParams`-like object. ([next-request](https://nextjs.org/docs/app/api-reference/functions/next-request))
- `NextResponse.json(body, { status, headers })` produces a JSON response. ([next-response](https://nextjs.org/docs/app/api-reference/functions/next-response))
- `NextResponse.redirect(url)` / `NextResponse.rewrite(url)` are used in Proxy to redirect/rewrite before rendering. ([next-response](https://nextjs.org/docs/app/api-reference/functions/next-response))
- `NextResponse.next({ request: { headers } })` forwards modified request headers upstream. Avoid `NextResponse.next({ headers })` shorthand, which sends headers to the client and can break Server Actions / streaming. Avoid copying all incoming request headers (cookie, authorization, custom `x-*`) to prevent leaking sensitive data. ([next-response](https://nextjs.org/docs/app/api-reference/functions/next-response))

## Route segment config

Named exports from `layout.tsx`, `page.tsx`, or `route.ts`:

| Export | Values | Notes |
|---|---|---|
| `dynamicParams` | `true` (default) / `false` | Controls whether dynamic segments not in `generateStaticParams` are generated at request time or return 404. Not available with `cacheComponents` enabled. |
| `instant` | `true` / `false` / `{ level: 'warning' }` | Cache Components only. Controls instant-navigation validation. Cannot be used in Client Components. |
| `maxDuration` | `number` (seconds) | Max execution time for server-side logic; applies to Server Actions on the page. |
| `prefetch` | `'partial'` / `'force-disabled'` | Cache Components only. Overrides `partialPrefetching` per segment. `'auto'` is the default and should not be written explicitly. Cannot be used in Client Components. |
| `runtime` | `'nodejs'` (default) / `'edge'` | Edge runtime is deprecated; remove the export. Cannot be used in Proxy. |
| `preferredRegion` | `string` / `string[]` | Deprecated. Remove the export from route files. |

## `prefetch` segment config (Cache Components)

Controls how a segment is prefetched during client-side navigation. Only works when `cacheComponents` is enabled; cannot be used in Client Components.

- `'partial'` — Opts the segment into Partial Prefetching without enabling the global `partialPrefetching` flag. A `<Link>` pointing here loads the per-route App Shell instead of the legacy full prefetch. Set on the destination, not the link. ([prefetch](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch))
- `'force-disabled'` — Never prefetch this segment. The client will not request segment data ahead of navigation. Use for pages behind authentication that are rarely visited. Does not prevent metadata prefetching, but actual segment data for this segment and all deeper segments is omitted. ([prefetch](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch))
- `'auto'` (default) — Equivalent to omitting the export; don't write it explicitly.
- **Interaction with `<Link prefetch={true}>`:** A `'partial'` segment uses per-link prefetching that resolves URL data (`params`, `searchParams`, full URL) and cached content. A `'force-disabled'` segment skips segment data entirely. `<Link prefetch={false}>` skips at the link level regardless of destination config. ([prefetch](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch))
- **Static cache serving:** On pages where all content is statically renderable, Next.js serves prefetches from the static cache (or CDN). If a page accesses non-static data like cookies/headers, it's prefetched at runtime with a fresh server render (costs server CPU per page view). ([prefetch](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch))

## `instant` segment config (Cache Components)

Controls how Next.js validates whether a navigation into this segment would produce an instant UI. Only works when `cacheComponents` is enabled; cannot be used in Client Components.

- `true` — Opts the segment into validation at the globally configured level (default: `'warning'`). With framework defaults, validation runs in development only and surfaces errors in the dev overlay. ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))
- `false` — Opts the segment out of instant-navigation validation. Useful when a deeper page should be instant but an ancestor can't be. Also opts out of static-shell validation. A `false` higher in the tree takes precedence over deeper `true` configs for the static-shell check. ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))
- `{ level: 'warning' }` — Validates in development only; errors appear in the dev overlay, build unaffected. (A build-time validation level is planned but not yet available.) ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))
- **How validation works:** `instant` triggers validation at every shared layout boundary. Each error identifies the component that would block navigation; the fix is usually to cache the data with `use cache` or wrap it in `<Suspense>`. ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))
- **Configuring defaults:** `experimental.instantInsights.validationLevel` tunes validation behavior — e.g., to limit validation to segments that opt in explicitly via `instant`. ([instant](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant))

## Proxy (`proxy.ts`)

- In Next.js 16+, Middleware is renamed to Proxy; the functionality remains the same.
- Create a single `proxy.ts` file at the project root (or `src` root) at the same level as `pages` or `app`.
- Only one `proxy.ts` file is supported per project, but logic can be split into modules and imported.
- Runs before routes are rendered; can rewrite, redirect, set headers/cookies, respond directly.
- Export as named `proxy` export or default export.
- Use a `matcher` config to avoid running on every request (including `_next/static`, `public/` assets).
- Proxy is not for slow data fetching or full session/authorization; use it for header modification, A/B test rewrites, or programmatic redirects.
- Prefer `next.config.js` `redirects` for simple redirects.
- `fetch` options (`cache`, `next.revalidate`, `next.tags`) have no effect in Proxy.
- Migration codemod: `npx @next/codemod@canary middleware-to-proxy .`
- `redirects` in `next.config.js` run **before** Proxy; Proxy runs **after** `redirects` and **before** rendering.
- For 1000+ redirects, implement a scalable Proxy solution (e.g. Bloom filter + Route Handler/API Route lookup) instead of a large static list.
- Proxy runs on the `nodejs` runtime in v16; the `edge` runtime is not supported in `proxy`. Keep `middleware` if you must use the `edge` runtime.

## Internationalized routing (Pages Router)

Pages Router internationalized routing is configured under the top-level `i18n` key in `next.config.js`. It has been available since `v10.0.0` and is meant to complement i18n libraries (react-intl, react-i18next, next-intl, etc.), not replace them.

- Configure `locales`, `defaultLocale`, and optional `domains` in `next.config.js`. Locales are UTS Locale Identifiers (`en-US`, `fr`, `nl-NL`). ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Sub-path Routing adds the locale to the URL path (default locale has no prefix). Domain Routing serves locales from different domains; include subdomains in the `domain` value. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Automatic locale detection uses the `Accept-Language` header and the current domain. Disable with `localeDetection: false`; with it disabled, only the domain/path locale is provided. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- A `NEXT_LOCALE=the-locale` cookie takes priority over the `Accept-Language` header when redirecting from `/`. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Access the active locale via `useRouter().locale`, all locales via `.locales`, and the default via `.defaultLocale`. In `getStaticProps`, `getServerSideProps`, and `getStaticPaths` context, `locale`/`locales`/`defaultLocale` are provided. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Transition locales with `next/link` `locale` prop or `router.push(href, as, { locale })`. Pass `locale={false}` to opt-out of automatic prefixing for an href that already includes the locale. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Internationalized Routing does **not** integrate with `output: 'export'` because it needs the Next.js routing layer. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Static generation multiplies by locale: a version of each non-dynamic page is generated for every configured locale. For dynamic routes using `getStaticPaths`, return a `locale` field in each path object to control which variants are prerendered. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Built-in limits: `locales` ≤ 100, `domains` ≤ 100. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))
- Next.js automatically adds the `lang` attribute to the `<html>` tag. Users must add `hreflang` meta tags via `next/head` for variant pages. ([internationalization](https://nextjs.org/docs/pages/guides/internationalization))

## Project structure: `src`, `public`, MDX

### `src` folder
- Alternative to root `app`/`pages`: move them to `src/app` or `src/pages`.
- `/public`, config files (`package.json`, `next.config.js`, `tsconfig.json`), and `.env.*` must stay at the project root.
- `src/app`/`src/pages` is ignored if `app`/`pages` exists at the project root.
- If using Proxy, place `proxy.ts` inside `src`. With `@/*` TS path aliases, update `tsconfig.json` `paths` to include `src/`.

### `public` folder
- Serve static assets from `public/` in the project root; reference them from the base URL `/` (e.g. `public/avatars/me.png` → `/avatars/me.png`).
- Default caching header is `Cache-Control: public, max-age=0` (Next.js cannot safely cache mutable public assets).
- For App Router static metadata (`robots.txt`, `favicon.ico`, etc.), use the special metadata file conventions in `app/` rather than `public/`.

### `mdx-components`
- Required to use `@next/mdx` with the App Router; it will not work without this file.
- Place `mdx-components.tsx`/`.js` at the project root (same level as `pages`/`app`, or inside `src`).
- Must export a single `useMDXComponents()` function (no arguments) that returns an `MDXComponents` map.

## Source URLs

- Routing and navigation overview: https://nextjs.org/docs/app/getting-started/linking-and-navigating
- Prefetching guide: https://nextjs.org/docs/app/guides/prefetching
- Optimizing prefetching: https://nextjs.org/docs/app/guides/optimizing-prefetching
- Partial Prefetching: https://nextjs.org/docs/app/guides/adopting-partial-prefetching
- Instant navigation: https://nextjs.org/docs/app/guides/instant-navigation
- `Link`: https://nextjs.org/docs/app/api-reference/components/link
- `useLinkStatus`: https://nextjs.org/docs/app/api-reference/functions/use-link-status
- `useReportWebVitals`: https://nextjs.org/docs/app/api-reference/functions/use-report-web-vitals
- `useParams`: https://nextjs.org/docs/app/api-reference/functions/use-params
- `usePathname`: https://nextjs.org/docs/app/api-reference/functions/use-pathname
- `useRouter`: https://nextjs.org/docs/app/api-reference/functions/use-router
- `useSearchParams`: https://nextjs.org/docs/app/api-reference/functions/use-search-params
- `useSelectedLayoutSegment`: https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segment
- `useSelectedLayoutSegments`: https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segments
- `userAgent`: https://nextjs.org/docs/app/api-reference/functions/userAgent
- `redirect`: https://nextjs.org/docs/app/api-reference/functions/redirect
- `permanentRedirect`: https://nextjs.org/docs/app/api-reference/functions/permanentRedirect
- `route` convention: https://nextjs.org/docs/app/api-reference/file-conventions/route
- `proxy` convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Project structure: https://nextjs.org/docs/app/getting-started/project-structure
- Dynamic Routes: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes
- Route Groups: https://nextjs.org/docs/app/api-reference/file-conventions/route-groups
- Parallel Routes: https://nextjs.org/docs/app/api-reference/file-conventions/parallel-routes
- Intercepting Routes: https://nextjs.org/docs/app/api-reference/file-conventions/intercepting-routes
- `prefetch` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch
- `instant` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant
- `dynamicParams` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/dynamicParams
- `runtime` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime
- `maxDuration` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/maxDuration
- Route segment config index: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config
- `redirects`: https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects
- `rewrites`: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites
- `onNavigate`: https://nextjs.org/docs/app/api-reference/components/link#onnavigate
- `transitionTypes`: https://nextjs.org/docs/app/api-reference/components/link#transitiontypes
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `next/root-params`: https://nextjs.org/docs/app/api-reference/functions/next-root-params
- `generateStaticParams`: https://nextjs.org/docs/app/api-reference/functions/generate-static-params
- `cacheComponents` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `partialPrefetching` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching
- Dynamic Routes: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes
- Redirecting guide: https://nextjs.org/docs/app/guides/redirecting
- `redirects` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects
- `NextResponse` API: https://nextjs.org/docs/app/api-reference/functions/next-response
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- `src` folder convention: https://nextjs.org/docs/app/api-reference/file-conventions/src-folder
- `public` folder convention: https://nextjs.org/docs/app/api-reference/file-conventions/public-folder
- `mdx-components` convention: https://nextjs.org/docs/app/api-reference/file-conventions/mdx-components

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — navigation additions (ingest 2026-08-30)

**Partial Prefetching adoption (`adopting-partial-prefetching`)**
- Review UI delivered by `<Link prefetch={true}>` before enabling Partial Prefetching — those links use the legacy full prefetch, and enabling Partial Prefetching changes their behavior. (Source: https://nextjs.org/docs/app/guides/adopting-partial-prefetching)
- In a `src/` project, pass `./src/app` to the adoption codemod; a wrong path reports `0 ok` instead of failing — verify the file count. (Source: above)
- A `params`/`searchParams` read inside `generateMetadata` surfaces as URL data in `generateMetadata()` (blocking prerender) rather than as link-scoped prefetch data. (Source: above)

**Client-side data fetching (`client-side-data-fetching`)**
- SWR: the `fallback` key and the `useSWR` key must match exactly; if they drift, SWR ignores the fallback and fetches on the client. (Source: https://nextjs.org/docs/app/guides/client-side-data-fetching/swr)
- TanStack Query + Cache Components: `cacheLife('max')` is used when writes invalidate the tag; within the cache profile, `stale` controls how long the Next.js client cache may reuse a prefetched payload. (Source: https://nextjs.org/docs/app/guides/client-side-data-fetching/tanstack-query)
