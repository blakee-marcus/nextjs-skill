# Caching and Revalidation

Reference: https://nextjs.org/docs/app/getting-started/caching

## Version-sensitive model

Next.js 16+ introduces **Cache Components** behind the `cacheComponents: true` flag in `next.config.*`. Older projects use the previous model (`fetch` options, `unstable_cache`, route segment configs). **Detect the installed version and config before choosing APIs.**

## Cache Components model (v16+)

### Enable

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

When Cache Components is enabled, `GET` Route Handlers follow the same prerendering model as pages.

### `use cache`

- Data fetching and asynchronous work are uncached by default; opt in at file, component, or function level. Cached functions/components must be async. Predictable synchronous work and stable module-scope reads can still prerender automatically.
- `use cache` cannot be used directly inside a Route Handler body; extract it to a helper function.

```ts
export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM products')
}
```

- `use cache` scope must be async; can be file-level, component-level, or function-level.
- At file level, all exported functions are cached and must be async; framework exports like `generateMetadata` and `generateStaticParams` must also be async.
- Arguments and captured parent-scope values become part of the cache key; different inputs get separate entries.
- Always pair with `cacheLife` or accept the implicit `default` profile.
- Do not read `cookies()`, `headers()`, or `searchParams` inside a plain `use cache` scope; read them outside and pass values as arguments, or use `use cache: private`/`use cache: remote`.
- Arguments and return values must be serializable. Arguments use RSC serialization (stricter); return values allow JSX. Class instances, functions (except pass-through), symbols, WeakMaps, WeakSets, and URL instances are not supported.
- `React.cache` values stored outside a `use cache` boundary are not visible inside it; pass data via arguments.
- **Closure capture:** When a cached function references variables from outer scopes, those variables are automatically captured and bound as arguments, making them part of the cache key. ([use-cache](https://nextjs.org/docs/app/api-reference/directives/use-cache))
- **Pass-through pattern:** You can accept non-serializable values (e.g. `children`, Server Action references) as arguments **as long as you don't introspect them**. This enables composition patterns where dynamic content passes through a cached wrapper. Functions are pass-through only — they cannot be called inside the cached scope. ([use-cache](https://nextjs.org/docs/app/api-reference/directives/use-cache))
- **Arguments vs return serialization:** Arguments use React Server Components serialization (stricter — no functions, class instances, URL instances). Return values use React Client Components serialization (allows JSX). You can return JSX but cannot accept it as an argument unless using pass-through. ([use-cache](https://nextjs.org/docs/app/api-reference/directives/use-cache))
- **Draft Mode + `use cache`:** You can read `isEnabled` from `draftMode()` inside a `use cache` scope to branch rendering, but `enable()`/`disable()` cannot be called inside the scope — they throw. Other runtime APIs (`cookies()`, `headers()`) remain prohibited even in Draft Mode. ([use-cache](https://nextjs.org/docs/app/api-reference/directives/use-cache))
- Draft Mode bypasses `use cache` scopes for the request; `isEnabled` can be read inside the scope but `enable()`/`disable()` cannot.
- Cached output is serialized as an RSC payload and reused in three places: prerendered HTML, a server/remote cache, and the browser's client cache. `cacheLife` governs the relevant copies.
- With the default in-memory handler, serverless environments typically do not reuse entries across requests; self-hosted/persistent memory does. `use cache: remote` moves entries to a durable shared handler, while `use cache: private` results live only in the browser.
- Every cache store is deployment-scoped. A new deployment starts fresh because the cache key includes the build/`deploymentId` ID, including entries held by a durable remote handler.
- An App Shell that reads `cookies()` or `headers()` is session-specific and cached per session in the browser, not in the shared server cache.
- `NEXT_PRIVATE_DEBUG_CACHE=1` enables verbose cache logging in dev and production.
- A cache is considered "short-lived" when it uses the `seconds` profile, `revalidate: 0`, or `expire` under 5 minutes. Short-lived caches are automatically excluded from prerenders and become dynamic holes instead. See [Prerendering behavior](https://nextjs.org/docs/app/api-reference/functions/cacheLife#prerendering-behavior).
- Nesting a short-lived `use cache` inside one without an explicit `cacheLife` fails the build during prerendering.
- Client-side cached content is stored in browser memory for the `stale` duration, with a minimum 30-second stale time enforced by the router regardless of configuration.

### Streaming uncached data

For data that must be fresh on every request, do not use `'use cache'`. Wrap the fetching component in `<Suspense>` instead:

```tsx
<Suspense fallback={<p>Loading posts...</p>}>
  <LatestPosts />
</Suspense>
```

Without a `Suspense` boundary, uncached async work blocks the route and surfaces a `blocking-route` insight in dev. `<Suspense>` is a containment boundary, not a dynamic-rendering switch: synchronous work inside it still completes during prerendering.

### Working with runtime APIs

Runtime APIs (`cookies()`, `headers()`, `searchParams`, `params`) must not be read inside a plain `use cache` scope. Options:

1. Extract the runtime value and pass it as a prop to a cached component/function. This is the default recommended pattern.
2. Use `use cache: private` to read cookies, headers, or `searchParams` directly, with results cached in browser memory only. This allows the result to be included in a prefetch.
3. Use `use cache: remote` to store the result in a durable shared cache handler.
4. Use `generateStaticParams` or ISR with Cache Components for dynamic params.
5. Call `connection()` before synchronous IO such as `Date.now()`, `Math.random()`, or `crypto.randomUUID()`, and wrap the component in `<Suspense>`. (Under Cache Components prefer `io()` from `next/cache`, which suspends during prerendering so the following code can still be cached/prefetched.)

```tsx
async function ProfileContent() {
  const session = (await cookies()).get('session')?.value
  return <CachedContent sessionId={session} />
}

async function CachedContent({ sessionId }: { sessionId: string }) {
  'use cache'
  const data = await fetchUserData(sessionId) // sessionId is part of the cache key
  return <div>{data}</div>
}
```

### `cacheLife`

Controls freshness. Requires `cacheComponents: true` in `next.config.*` (Cache Components). Must be called inside a `use cache` scope — `cacheLife` cannot be used at module scope (calling it at the top level throws). Only one `cacheLife` call may execute per function invocation (you may call it in different control-flow branches, but only one runs per request). Recommended in every `use cache` scope; omitting it applies the implicit `default` profile.

Built-in profiles:

| Profile | Use case | stale | revalidate | expire |
|---|---|---|---|---|
| `default` | Standard content | 5m | 15m | never |
| `seconds` | Real-time data | 30s | 1s | 60s |
| `minutes` | Frequently updated content | 5m | 1m | 1h |
| `hours` | Content updated multiple times/day | 5m | 1h | 1d |
| `days` | Content updated daily | 5m | 1d | 1w |
| `weeks` | Content updated weekly | 5m | 1w | 30d |
| `max` | Stable content that rarely changes | 5m | 30d | 1y |

The three timing properties (all in seconds):
- `stale` — client-side: how long the client serves cached content without checking the server (router shows it instantly, no network request). Defaults to the `default` profile's stale (5m). Also determines whether content can join the route's App Shell.
- `revalidate` — after this, the next request serves the cached version and regenerates in the background (like ISR). Defaults to the `default` profile's revalidate (15m).
- `expire` — max age; after this with no traffic, the next request regenerates synchronously. Defaults to the `default` profile's expire (never). When both `revalidate` and `expire` are set, `expire` must be longer than `revalidate` or Next.js raises a config error.

For fine-grained control, pass an object with `stale`, `revalidate`, and `expire`:

```ts
cacheLife({ stale: 3600, revalidate: 7200, expire: 86400 })
```

Inline profiles apply only to that function/component. `cacheLife({})` (empty object) applies the `default` profile. Any omitted property inherits from `default` (also true for inline objects).
- **Prerendering thresholds:** `revalidate: 0` or `expire` under 5 minutes excludes a cache from prerenders (dynamic hole). `stale` under 30 seconds also excludes it. `stale` ≥30s but <5 minutes is included in prerenders but excluded from the App Shell. Of presets, only `seconds` is fully excluded.

Define reusable **custom profiles** in `next.config.ts` under the `cacheLife` key (alongside `cacheComponents: true`); built-in names keep working with editor autocomplete, and an overridden profile's type signature/JSDoc is regenerated from `next.config.ts` during `next dev`/`next build`/`next typegen`:

```ts
const nextConfig = {
  cacheComponents: true,
  cacheLife: {
    biweekly: { stale: 60 * 60 * 24 * 14, revalidate: 60 * 60 * 24, expire: 60 * 60 * 24 * 14 },
  },
}
```

You can also redefine any built-in (including `default` and `max`); redefining `default` also changes the lifetime applied when a `use cache` scope calls no `cacheLife`. `stale` here differs from `staleTimes` (global config): `staleTimes.static` also updates the `default` profile's `stale`.

**Client cache behavior:** `stale` controls the Client Cache, not the `Cache-Control` header — the server sends the stale time via the `x-nextjs-stale-time` response header, and the router uses it to decide when to revalidate. A **minimum 30s stale time is enforced** (time-based expiration only) so prefetched links stay usable. Calling a revalidation function from a Server Action (`revalidateTag`, `revalidatePath`, `updateTag`, `refresh`) immediately clears the entire client cache, bypassing `stale`.

**Prerendering behavior:** `revalidate` of `0` or `expire` under 5m → excluded from prerenders (dynamic hole); `stale` under 30s → excluded from prerenders (a prefetch would expire before click); `stale` ≥30s but <5m → included in prerenders but excluded from the route's App Shell. Of the presets, only `seconds` (expire 1m) is excluded from prerenders.

**Nested caching:** With an explicit outer `cacheLife`, the outer cache uses its own lifetime regardless of inner lifetimes (explicit always wins). Without an explicit outer `cacheLife`, the outer uses `default` (15m revalidate); inner caches with *shorter* lifetimes can reduce the outer lifetime, but longer ones cannot extend it beyond `default`. Nesting a short-lived `use cache` inside a scope without an explicit `cacheLife` throws during prerendering — add an explicit `cacheLife()` to fix.

A cache is considered **short-lived** when it uses the `seconds` profile, `revalidate: 0`, or `expire` under 5 minutes. Short-lived caches are automatically excluded from prerenders and become dynamic holes instead.

### `cacheLife` static revalidation column

The `next build` route table prints `Revalidate` and `Expire` columns for routes that contain caches. The reported `revalidate` is the shortest revalidation time across all caches in that route. This applies even without an explicit `cacheLife` call, since caches fall back to the `default` profile. The `Expire` column caps at one year (`1y`).

### `cacheTag`

Tag cached data for on-demand invalidation. Requires `cacheComponents: true`. Call `cacheTag` inside a `use cache` scope (function or component). It takes **one or more string values**; you can assign multiple tags in one call (`cacheTag('a', 'b')`).

```ts
'use cache'
cacheTag('products')
```

- **Idempotent:** applying the same tag multiple times has no additional effect.
- **Limits:** a single `cacheTag()` call accepts up to **128 tags**, each max **256 characters**. Tags longer than 256 chars are skipped; tags past the 128th are dropped. Both cases log a console warning.
- Tags may be derived from returned data (e.g. `cacheTag('bookings', data.id)`).

You can combine `use cache`, `cacheLife`, and `cacheTag` in a single component to define cache scope, lifetime, and invalidation tags.

**Invalidation:** purge tagged entries on demand from a Server Action or Route Handler:
- `updateTag(tag)` — immediate expiration for read-your-own-writes (forms, user-triggered mutations). **Server Actions only.**
- `revalidateTag(tag, profile)` — stale-while-revalidate when passed a profile; works in Server Actions and Route Handlers. The legacy no-profile call is deprecated; see the API rules below.

### Revalidation APIs

- `revalidateTag(tag, profile)` — stale-while-revalidate when passed a cache-life profile such as the recommended `'max'`; use another named profile or `{ expire: number }` to control how long stale content may be served. In Next.js 16.3.8, the single-argument form is deprecated regardless of caching model and behaves like `{ expire: 0 }`; migrate immediate Server Action invalidation to `updateTag`, or pass `{ expire: 0 }` when a Route Handler/webhook must block on fresh data. ([revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag))
- `updateTag(tag)` — immediate expiration; **Server Actions only**. Use case: read-your-own-writes. ([updateTag](https://nextjs.org/docs/app/api-reference/functions/updateTag))
- `revalidatePath(path)` — invalidate by path; regenerates on the next request. Use case: tagging is overkill. ([revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath))
- `refresh()` — refetch current route RSC Payload without invalidating cache. Use case: state outside cache changed. ([refresh](https://nextjs.org/docs/app/api-reference/functions/refresh))

When `updateTag`, `revalidatePath`, or `refresh` runs, Next.js re-renders the current route server-side and includes a newly rendered RSC Payload in the action's response, so the page reflects the change in the same roundtrip. `revalidateTag` with a stale-while-revalidate profile intentionally skips that immediate re-render. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))

- `revalidateTag` accepts a `profile` argument that sets how long stale content can be served while fresh content generates in the background. Using `'max'` gives the longest stale window. Once the stale window expires, subsequent requests block until fresh content is ready. `revalidatePath` invalidates the cache entries but regeneration happens on the next request (lazy regeneration). If you need eager regeneration for the Pages Router, use `res.revalidate`.
- **Cache handler `getExpiration()`** — returns the most recent revalidation timestamp across provided tags, or `0` if none have been revalidated. Can return `Infinity` to signal that soft tags should instead be passed to `get()` and checked for expiration there. Treat an entry as stale if the returned timestamp is newer than the entry's timestamp.
- **Cache handler `refreshTags()`** — called periodically before starting a new request to sync tag state from shared storage. Must catch errors so requests continue with last-known local tag state rather than failing.
- **Soft tags** — automatically generated from route paths, prefixed `_N_T_`. Each segment gets a layout tag plus the leaf route tag. Passed to the cache handler `get()` method as the `softTags` parameter. `revalidatePath` works by invalidating these soft tags. Source: [How revalidation works](https://nextjs.org/docs/app/guides/how-revalidation-works)
- **`prefetch={true}` trade-offs** (Cache Components + Partial Prefetching): Each visible `<Link prefetch={true}>` can wake a server. Use when part of the tree depends on URL data (searchParams/params) AND that part has a known cache lifetime. Skip when the route has little URL-data dependency, content must be fresh on every request, or the route is rarely navigated to. On grids of many links, prefer intent-based (hover) prefetching instead. (Source: https://nextjs.org/docs/app/guides/optimizing-prefetching)
- **App Shell definition**: the generic, reusable part of the page that doesn't depend on URL data. For routes with `params`/`searchParams` not resolved by `generateStaticParams`, the App Shell still ships instantly while the rest streams in. (Source: https://nextjs.org/docs/app/guides/prefetching)
- In a **Route Handler** or webhook where `updateTag` is unavailable, use `revalidateTag(tag, { expire: 0 })` for immediate blocking revalidation.
- `revalidateTag` and `updateTag` are **not** for use in Client Components; call them only in Server Actions/Route Handlers.

> **Good to know:** Prefer **tag-based** revalidation (`revalidateTag` / `updateTag` / `cacheTag`) over **path-based** (`revalidatePath`) whenever practical — it is more precise and avoids over-invalidating unrelated routes that share a path prefix. Reach for `revalidatePath` only when tagging is awkward (an entire route tree, or data with no convenient tag). ([revalidating](https://nextjs.org/docs/app/getting-started/revalidating))

> **Good to know:** `updateTag` can only be called from a Server Action; calling it elsewhere throws. In Route Handlers or webhooks, use `revalidateTag(tag, profile)` instead. The single-argument form `revalidateTag(tag)` is **deprecated outright** (not only under Cache Components): it behaves like `{ expire: 0 }`, still works if TypeScript errors are suppressed, and may be removed in a future version — migrate to `updateTag` in Server Actions or `profile="max"` elsewhere. `revalidatePath` likewise cannot be called in Client Components or Proxy (server environments only). Likewise, `refresh()` can **only** be called from a Server Action and throws in Route Handlers, Client Components, or any other context — it refreshes the client router (not the server cache). ([refresh](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/refresh.mdx))

> **Good to know:** In serverless environments, in-memory cache entries may not persist across revalidations. See [runtime caching considerations](https://nextjs.org/docs/app/api-reference/directives/use-cache#runtime-caching-considerations).

## ISR with Cache Components

With `cacheComponents: true` and `partialPrefetching: true`, dynamic routes get an instant first visit even for URLs not listed in `generateStaticParams`:

- **App Shell**: generic reusable part of the page, prerendered at build time.
- **Listed params**: fully prerendered at build time (served from cache).
- **Unlisted params**: App Shell served instantly, then upgraded in the background with the now-known params. Subsequent visits get the upgraded result from the cache.

This is the Cache Components equivalent of Pages Router ISR / `fallback: true`. The `generateStaticParams` function receives parent params for nested dynamic routes. ([incremental-static-regeneration-cache-components](https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components))

## Draft Mode internals

Draft Mode sets the `__prerender_bypass` cookie. When enabled:
- `fetch()` skips the Next.js fetch cache and hits the network directly.
- `'use cache'` scopes re-execute on every request; results are not saved.
- `unstable_cache` reads/writes are bypassed.
- Page is excluded from ISR cache, served with `Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate`.
- Works with Cache Components: read `isEnabled` from `draftMode()` and branch rendering or pass the flag into a `'use cache'` scope.

Draft Mode entry handler uses `GET` (CMS preview opens URL in new tab); exit flow uses `POST` (Server Action or POST Route Handler). ([draft-mode](https://nextjs.org/docs/app/guides/draft-mode))

## Offline support (experimental)

With `experimental.useOffline` enabled:
- Failed soft navigations, RSC data fetches, prefetches, and Server Actions no longer throw when the network is down; Next.js keeps them pending and retries once the connection returns.
- The UI remains in its loading state while offline.
- Use the `useOffline` hook from `next/offline` to communicate connectivity state to users.
- `useOffline` returns `false` during SSR/initial hydration; the first accurate value is reported after the app mounts. It returns `true` only after a network request has actually failed **or** the browser fired an `offline` event. Without `experimental.useOffline` enabled the hook **always returns `false`** — it is not a general-purpose `navigator.onLine` wrapper. ([useOffline](https://nextjs.org/docs/app/api-reference/functions/use-offline))
- Client-side `fetch()` or data libraries (React Query, SWR) stay under their own retry policies.
- Test offline behavior with `next build && next start`; dev mode is not a reliable reference.

Source: [Offline support](https://nextjs.org/docs/app/guides/offline-support)

### revalidateTag / updateTag / revalidatePath signatures

```ts
revalidateTag(tag: string, profile: string | { expire?: number }): void
updateTag(tag: string): void
revalidatePath(path: string, type?: 'page' | 'layout'): void
```

- `revalidateTag` `profile` accepts a named `cacheLife` profile **or** an object with an `expire` property (seconds). Only `expire` is read — it controls how long stale content may still be served. `profile="max"` is a ~1-year window, so requests are effectively always served stale while revalidation runs. `{ expire: 0 }` means stale content is never served, so the next request is a blocking revalidate/cache miss — the right choice in Route Handlers/webhooks where `updateTag` is unavailable. ([revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag))
- Revalidation is triggered **by a request**, not by the `revalidateTag` call itself: pages using the tag revalidate as they are visited, not all at once. ([revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag))
- `revalidateTag` with no profile is legacy behavior **equivalent to `updateTag`** (immediate expiration). ([updateTag](https://nextjs.org/docs/app/api-reference/functions/updateTag))
- Tags are **case-sensitive** and capped at **256 characters**. A tag over the limit is never assigned to cached data, so revalidating it silently does nothing. ([revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag), [updateTag](https://nextjs.org/docs/app/api-reference/functions/updateTag))
- `revalidatePath` `path`: a route-file-structure string — a literal path (`/product/123`) or a route pattern with dynamic segments (`/product/[slug]`). Never append `/page` or `/layout`; use `type` instead. Max **1024 characters**, **case-sensitive**, no trailing slash needed regardless of `trailingSlash`. ([revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath))
- `revalidatePath` `type` is **required when `path` contains a dynamic segment** and must be **omitted for a literal path**. `'layout'` invalidates that layout plus all nested layouts and pages beneath it (`revalidatePath('/blog/[slug]', 'layout')` also invalidates `/blog/[slug]/[another]`); `revalidatePath('/', 'layout')` purges the Client Cache and invalidates all cached data. ([revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath))
- With `rewrites`, pass the **destination** route path (the actual file location), not the browser-visible source path — the source will not match the cache entry. ([revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath))
- From a **Server Function**, `revalidatePath` updates the UI immediately if you are viewing the affected path; **currently it also causes all previously visited pages to refresh when navigated to again** (temporary behavior, planned to scope to the specific path in a future release). From a **Route Handler**, it only marks the path and revalidates on the next visit to that path — a dynamic route segment does not trigger many revalidations at once. ([revalidatePath](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/revalidatePath.mdx))
- `revalidatePath` can also invalidate **Route Handlers**: `revalidatePath('/api/data')` invalidates cached data accessed within that GET handler. ([revalidatePath](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/revalidatePath.mdx))
- **Server Actions dispatch sequentially per client.** Next.js dispatches Server Actions one at a time per client; do not rely on `Promise.all` to parallelize actions from the client. Parallel work belongs inside a single Server Action, a Server Component, or a Route Handler. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))
- **Choosing a cache update after mutation.** After a Server Action mutates data, use `updateTag` for immediate read-your-own-writes, `revalidateTag` for stale-while-revalidate, `revalidatePath` when tagging is awkward, and `refresh` when state outside the cache changed. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))

### Tag architecture and multi-instance coordination

Next.js uses explicit and soft tags for invalidation:

- **Explicit tags** — set by `cacheTag()` or `next: { tags: [...] }` on `fetch`.
- **Soft tags** — automatically generated from route paths, prefixed with `_N_T_`. Each segment gets a layout tag plus the leaf route tag. `revalidatePath()` works by invalidating these soft tags.
- `revalidateTag(tag, profile)` regenerates both the HTML response and the RSC payload from the same React component tree and stores them together. Cache HTML and RSC responses together with the same TTL and invalidation policy to avoid mismatched client-side navigation content.

For custom cache handlers:

- `getExpiration()` returns the most recent revalidation timestamp across provided tags, or `0` if none have been revalidated. It can also return `Infinity` to signal that soft tags should instead be passed to `get()` and checked for expiration there. Treat an entry as stale if the returned timestamp is newer than the entry's timestamp.
- `updateTags()` is called when `revalidateTag()` is invoked; write the invalidation event to shared storage (e.g. Redis) so other instances can discover it.
- `refreshTags()` is called periodically before starting a new request; read shared storage and update local tag state. Catch errors in `refreshTags()` so requests continue with the last known local tag state rather than failing.

### Migrating from route segment configs

When `cacheComponents` is enabled, replace route segment configs with Cache Components APIs:

- `dynamic = 'force-dynamic'` — not needed; pages are dynamic by default.
- `dynamic = 'force-static'` — remove it; cache data with `'use cache'` and wrap runtime reads in `<Suspense>`.
- `revalidate` — replace with `cacheLife()` inside a cached scope.
- `fetchCache` — not needed; fetches inside `'use cache'` are cached automatically.
- `fetch` `cache`/`next.tags`/`next.revalidate` options — move into `'use cache'` + `cacheLife`/`cacheTag`.
- `unstable_cache` — replace with `'use cache'`. `unstable_cache` persists across deployments/serverless instances; `use cache` defaults to in-memory and is scoped to one deployment.
- `unstable_noStore` / `noStore()` — not needed; everything is uncached by default. If a component must run at request time, call `connection()` and wrap it in `<Suspense>`.
- `runtime = 'edge'` — not supported with Cache Components; use Node.js runtime (default) or Proxy for edge-like behavior.
- `experimental_ppr` / `experimental.ppr` — removed; Partial Prerendering is part of `cacheComponents`. A [codemod](/docs/app/guides/upgrading/codemods#remove-experimental_ppr-route-segment-config-from-app-router-pages-and-layouts) removes the segment config for you.
- `generateStaticParams` under Cache Components must return **at least one param** for dynamic routes; **empty arrays cause a build error** (`empty-generate-static-params`). This is what lets Cache Components validate the route does not incorrectly access `cookies()`, `headers()`, or `searchParams` at runtime. If param values are unknown at build time you *can* return a placeholder (e.g. `[{ slug: '__placeholder__' }]`) and handle it with `notFound()`, but this defeats build-time validation and may cause runtime errors. (Without Cache Components, returning `[]` is the documented way to render all paths at runtime; you must always return *an* array or the route renders dynamically.) ([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))
- ISR-at-runtime requires either returning `[]` from `generateStaticParams` **or** `export const dynamic = 'force-static'`; otherwise paths are not revalidated at runtime. `generateStaticParams` runs on navigation in `next dev`, before Layouts/Pages in `next build`, and is **not** called again during ISR revalidation. ([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))
- `dynamicParams` is not supported; delete the export. Unknown params render on request; reject them manually with `notFound()` if needed.
- `maxDuration` sets the maximum execution time (seconds) for server-side logic in a route segment. For Server Actions, set it at the page level to change the timeout of all actions on the page.
- `runtime` and `preferredRegion` route segment configs are deprecated. Use Node.js runtime and remove these exports.
- Synchronous IO such as `new Date()`, `Date.now()`, `Math.random()`, and `crypto.randomUUID()` during prerender throws a build error that `instant = false` does not clear. Move it under `<Suspense>` with `connection()` or `io()` (Cache Components) or into a Client Component.
- Client hooks that read the route (`usePathname`, `useParams`, `useSelectedLayoutSegment(s)`) suspend when params are not yet known; wrap them in `<Suspense>`. `useSearchParams` always needs a `<Suspense>` boundary.
- `instant = false` opts a segment out of instant-navigation validation but does **not** clear synchronous-IO build errors; move synchronous IO under `<Suspense>` with `connection()` or `io()` (Cache Components) or into a Client Component.
- Run the `cache-components-instant-false` codemod to opt every `page`, `layout`, and `default` out of validation in one pass when adopting incrementally.

Source: [Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components)

### Graceful degradation

- Cache write failures still serve the response; the entry is lost and the next request triggers a fresh render.
- Cache read failures should return `undefined` (the cache miss signal), not throw.
- Set `deploymentId` to mitigate cross-deployment skew during rolling deployments.

### Draft Mode

Draft Mode lets editors preview unpublished content by bypassing the Next.js fetch cache, `'use cache'` scopes, and `unstable_cache` for the request. The affected page is excluded from the ISR response cache and served with `Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate`. Draft Mode also works with Cache Components; read `isEnabled` from `draftMode()` and use it to branch rendering or pass the flag into a `'use cache'` scope.

### `use cache: private`

Allows runtime APIs (`cookies()`, `headers()`, `searchParams`) inside a cached scope, but stores results **only in browser memory**, not on the server. Use when refactoring to pass runtime values as arguments is impractical. This is also the pattern when you cannot extract the runtime data at the call site, such as auth helpers that check `Date.now()` against a token's expiry. Colocate the directive as close to the runtime access as possible. It does **not** accept `connection()`. ([use-cache-private](https://nextjs.org/docs/app/api-reference/directives/use-cache-private))

- **Client stale time contribution:** Private Cache Functions contribute their `stale` time to the route's Client Cache. If a function only needs request-scoped deduplication, use `cacheLife({ stale: Infinity })` to keep it from lowering the route's stale time. Next.js uses the shortest stale time from the route's cache entries, so another cache or route setting can still set a finite value. Setting `stale` to `Infinity` does not store the private result on the server across production requests. Use a finite value when the client router should revalidate personalized output after a known interval. ([use-cache-private](https://nextjs.org/docs/app/api-reference/directives/use-cache-private))
- **Stale thresholds:** The `stale` time must be at least **30 seconds** for per-link prefetching to work, and at least **5 minutes** for the content to be included in the route's App Shell. See [cacheLife prerendering behavior](https://nextjs.org/docs/app/api-reference/functions/cacheLife#prerendering-behavior). ([use-cache-private](https://nextjs.org/docs/app/api-reference/directives/use-cache-private))

### `use cache: remote`

Uses a remote cache handler. Requires a network roundtrip; only worthwhile at high hit rates.

- **Nesting rules:**
  - Remote caches **can** be nested inside other remote caches or regular caches.
  - Remote caches **cannot** be nested inside private caches.
  - Private caches **cannot** be nested inside remote caches. ([use-cache-remote](https://nextjs.org/docs/app/api-reference/directives/use-cache-remote))
- **When to use:** Rate-limited APIs, slow/expensive backends, costly computations, or flaky external services where a shared cache across instances improves hit rates and reduces load. For request-time components that access runtime data inside `<Suspense>`, `use cache: remote` provides a shared cache across all server instances in serverless environments. ([use-cache-remote](https://nextjs.org/docs/app/api-reference/directives/use-cache-remote))
- **When NOT to use:** If you already have a KV store wrapping your data layer; if operations are already fast (<50ms); if cache keys are nearly unique per request; if data changes every few seconds. ([use-cache-remote](https://nextjs.org/docs/app/api-reference/directives/use-cache-remote))
- **Cache key design:** Pick dimensions with few unique values (e.g. category, language) to maximize utilization; avoid high-cardinality values (e.g. per-user, per-price-filter). ([use-cache-remote](https://nextjs.org/docs/app/api-reference/directives/use-cache-remote))

### Prerendering with Cache Components

- Static shell is built at build time from cached/predictable content.
- Module imports, pure computations, synchronous local I/O such as `fs.readFileSync`, and synchronous embedded-database queries are predictable and prerender automatically. Call `connection()`/`io()` first when a synchronous source must be evaluated per request.
- For stable asynchronous local resources such as configuration files, prefer one module-scope read. An async local-resource read during rendering is uncached work and must be inside `use cache` or behind `<Suspense>`.
- Push `params`, `searchParams`, `cookies()`, `headers()`, and async data access down to the smallest subtree that needs them. Awaiting dynamic `params` at layout top level prevents that layout from joining the static shell; await beneath `<Suspense>` instead when possible.
- Uncached or runtime data must be wrapped in `Suspense` or behind `connection()`/`io()` so it streams at request time.
- `Math.random()`, `Date.now()`, `crypto.randomUUID()` require explicit handling; use `connection()` + `Suspense` for unique per-request values, or cache the value with `use cache` so all users see the same value until revalidation. Under Cache Components, prefer `io()` (which suspends during prerender) so the surrounding component can still be cached/prefetched.
- `performance.now()` is allowed for telemetry.
- Bots and crawlers receive fully rendered HTML rather than the streamed shell. Because the shell is re-rendered for crawlers, data the shell relies on must also be available at request time.
- Direct navigations can be served from a CDN without hitting the upstream server.
- With Partial Prefetching enabled, `<Link>` prefetches each route's App Shell by default. For URL-specific cached content (`searchParams`, dynamic `params`), set `prefetch={true}` on the link.
- Partial Prefetching is the default behavior with Cache Components. See [Adopting Partial Prefetching](/docs/app/guides/adopting-partial-prefetching) for migration patterns.
- Reading `cookies()` or `headers()` outside `<Suspense>` prevents the route from prerendering (`blocking-prerender-runtime`).

### `io()`

`io()` (from `next/cache`, added in v16.3.0) tells Next.js that a synchronous IO operation follows, keeping that value out of the static shell. Its effect requires `cacheComponents: true`; in every other context it is a no-op. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))

- Signature: `function io(): Promise<void>` — no parameters; returns `Promise<void>`. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- With Cache Components enabled, `await io()` **suspends during prerendering**, excluding the code that follows from the prerender/static-shell output. Call it before reading a synchronous value such as `new Date()`, `Math.random()`, `crypto.randomUUID()`, or a synchronous database driver like `node:sqlite`. The component must sit inside a `<Suspense>` boundary so the fallback ships in the static shell. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- In a Client Component, call `use(io())` before reading a synchronous source (e.g. `Date.now()`) so the read is not captured into the SSR static shell. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- Contexts where `io()` resolves immediately (no-op): during a real request, inside cached (`'use cache'`) scopes, in the browser, and in apps without Cache Components (including the Pages Router). ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- No `io()` needed when the component already uses a Request-time API (`cookies()`, `headers()` — itself the suspension point) or when data comes from an awaited `fetch`/async DB query wrapped in `<Suspense>` (the `await` is the suspension point). ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- `io()` vs `connection()`: `connection()` also excludes following code from the static shell but stays suspended until a full user navigation reaches the server, which **blocks prefetches**. `io()` suspends like any async function, so the code after it can be wrapped in `'use cache'` and prefetched/cached on the client. **Prefer `io()` over `connection()`**; reach for `connection()` only when you must wait for a real user request. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))

### Offline support (experimental)

With `experimental.useOffline` enabled:
- Failed soft navigations, RSC data fetches, prefetches, and Server Actions no longer throw when the network is down; Next.js keeps them pending and retries once the connection returns.
- The UI remains in its loading state while offline.
- Use the `useOffline` hook from `next/offline` to communicate connectivity state to users.
- `useOffline` returns `false` during SSR/initial hydration; the first accurate value is reported after the app mounts. It returns `true` only after a network request has actually failed **or** the browser fired an `offline` event. Without `experimental.useOffline` enabled the hook **always returns `false`** — it is not a general-purpose `navigator.onLine` wrapper. ([useOffline](https://nextjs.org/docs/app/api-reference/functions/use-offline))
- Client-side `fetch()` or data libraries (React Query, SWR) stay under their own retry policies.
- Test offline behavior with `next build && next start`; dev mode is not a reliable reference.

### Preserving UI state (Cache Components + React Activity)

With Cache Components enabled, Next.js preserves up to 3 routes across navigations using React's `<Activity>` component. The DOM is kept in the document (hidden with `display: none`), so React state and DOM state such as form drafts, scroll positions, expanded `<details>` elements, and video progress are retained.

To reset transient state when a page is hidden (e.g. dropdowns, status messages, dialog open state), use a `useLayoutEffect` cleanup:

```tsx
useLayoutEffect(() => {
  return () => {
    setIsOpen(false)
    setStatus('idle')
  }
}, [])
```

Use `useRouter().bfcacheId` as a React `key` on a fragment to reset an entire subtree on push/replace navigations while still restoring state on browser back/forward. For new code, prefer per-pattern resets.

For state that should reset when the authenticated user changes, key the component by `userId` or reset explicitly in an effect.

### Progressive Web Apps

- Next.js provides built-in web app manifest support via `app/manifest.ts` / `app/manifest.json`.
- Implement service workers and push notifications in Client Components using standard Web APIs (`navigator.serviceWorker`, `PushManager`).
- PWAs allow instant updates without app-store approval, cross-platform single codebase, and native-like features such as home screen installation and push notifications.
- iOS 16.4+ home screen apps, Safari 16 macOS 13+, Chromium, and Firefox support web push; install prompts can work without offline support. ([PWAs](https://nextjs.org/docs/app/guides/progressive-web-apps))

### Blocking routes and the `instant` segment config

Cache Components validates pages in development for instant navigation. If a page cannot prerender because it accesses runtime/uncached data outside `Suspense`, Next.js surfaces a `blocking-prerender-dynamic` or `blocking-prerender-runtime` error with three fix options: stream (wrap in `Suspense`), cache (add `"use cache"`), or block (set `export const instant = false` to opt out of validation and allow a blocking route). Use `--debug-prerender` to get source-mapped server stack traces; do not deploy builds produced with `--debug-prerender`.

### Migrating from route segment configs

When `cacheComponents` is enabled, replace route segment configs with Cache Components APIs:

- `dynamic = 'force-dynamic'` — not needed; pages are dynamic by default.
- `dynamic = 'force-static'` — remove it; cache data with `'use cache'` and wrap runtime reads in `<Suspense>`.
- `revalidate` — replace with `cacheLife()` inside a cached scope.
- `fetchCache` — not needed; fetches inside `'use cache'` are cached automatically.
- `fetch` `cache`/`next.tags`/`next.revalidate` options — move into `'use cache'` + `cacheLife`/`cacheTag`.
- `unstable_cache` — replace with `'use cache'`. `unstable_cache` persists across deployments/serverless instances; `use cache` defaults to in-memory and is scoped to one deployment.
- `unstable_noStore` / `noStore()` — not needed; everything is uncached by default. If a component must run at request time, call `connection()` and wrap it in `<Suspense>`. Under Cache Components prefer `io()` from `next/cache`.
- `runtime = 'edge'` — not supported with Cache Components; use Node.js runtime (default) or Proxy for edge-like behavior.
- `experimental_ppr` / `experimental.ppr` — removed; Partial Prerendering is part of `cacheComponents`.
- `generateStaticParams` under Cache Components must return **at least one param** for dynamic routes; **empty arrays cause a build error** (`empty-generate-static-params`). This is what lets Cache Components validate the route does not incorrectly access `cookies()`, `headers()`, or `searchParams` at runtime. If param values are unknown at build time you *can* return a placeholder (e.g. `[{ slug: '__placeholder__' }]`) and handle it with `notFound()`, but this defeats build-time validation and may cause runtime errors. (Without Cache Components, returning `[]` is the documented way to render all paths at runtime; you must always return *an* array or the route renders dynamically.) ([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))
- ISR-at-runtime requires either returning `[]` from `generateStaticParams` **or** `export const dynamic = 'force-static'`; otherwise paths are not revalidated at runtime. `generateStaticParams` runs on navigation in `next dev`, before Layouts/Pages in `next build`, and is **not** called again during ISR revalidation. ([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))
- `dynamicParams` is not supported; delete the export. Unknown params render on request; reject them manually with `notFound()` if needed.
- `maxDuration` sets the maximum execution time (seconds) for server-side logic in a route segment. For Server Actions, set it at the page level to change the timeout of all actions on the page.
- `runtime` and `preferredRegion` route segment configs are deprecated. Use Node.js runtime and remove these exports.
- Synchronous IO such as `new Date()`, `Date.now()`, `Math.random()`, and `crypto.randomUUID()` during prerender throws a build error that `instant = false` does not clear. Move it under `<Suspense>` with `connection()` or `io()` (Cache Components) or into a Client Component.
- Client hooks that read the route (`usePathname`, `useParams`, `useSelectedLayoutSegment(s)`) suspend when params are not yet known; wrap them in `<Suspense>`. `useSearchParams` always needs a `<Suspense>` boundary.

## Previous caching model (pre-v16 / no Cache Components)

When `cacheComponents` is not enabled, Next.js uses the previous caching model:

- `fetch` requests are **not cached by default**. Opt in with `cache: 'force-cache'`.
- Time-based revalidation with `fetch`: `next: { revalidate: 3600 }`.
- Non-`fetch` async work can be wrapped with `unstable_cache` from `next/cache`:

  ```ts
  import { unstable_cache } from 'next/cache'

  export const getCachedUser = unstable_cache(
    async (id: string) => db.select().from(users).where(eq(users.id, id)).then(r => r[0]),
    ['user'],
    { tags: ['user'], revalidate: 3600 }
  )
  ```

  - `keyParts` (2nd arg) is **required** whenever the cached function closes over external variables that are not passed as parameters — otherwise the cache key is wrong and entries collide. `options.tags` are for **invalidation only** and never identify the function uniquely. ([unstable_cache](https://nextjs.org/docs/app/api-reference/functions/unstable_cache)) `unstable_cache` was introduced in v14.0.0 and is **replaced by `use cache` in Next.js 16** (opt into Cache Components and migrate to the `use cache` directive). ([unstable_cache](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_cache.mdx))
  - Reading uncached request data (`headers()`, `cookies()`) **inside** an `unstable_cache` scope is unsupported — read them outside and pass the values in as arguments. (Same rule as `'use cache'`.) ([unstable_cache](https://nextjs.org/docs/app/api-reference/functions/unstable_cache))
  - `unstable_noStore()` is equivalent to `cache: 'no-store'` on a `fetch`, and is preferred over `export const dynamic = 'force-dynamic'` because it is per-component/granular. Calling it **inside** `unstable_cache` does **not** opt out of static generation — the cache configuration wins. ([unstable_noStore](https://nextjs.org/docs/app/api-reference/functions/unstable_noStore)) In v15.0.0 `unstable_noStore` was **deprecated in favor of `connection()`** (introduced in v14.0.0); prefer `connection()` over `noStore()` when on v15+. ([unstable_noStore](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_noStore.mdx))

- Route segment config controls route-level behavior:
  - `export const dynamic = 'auto' | 'force-dynamic' | 'error' | 'force-static'`
    - `'auto'` (default): cache as much as possible without preventing components from opting into dynamic behavior.
    - `'force-dynamic'`: force dynamic rendering; equivalent to setting every `fetch()` to `{ cache: 'no-store', next: { revalidate: 0 } }` and `fetchCache = 'force-no-store'`.
    - `'error'`: force prerendering and error if request-time APIs or uncached data are used; equivalent to `getStaticProps` and `fetchCache = 'only-cache'`.
    - `'force-static'`: force prerendering and cache data by forcing `cookies()`, `headers()`, and `useSearchParams()` to return empty values. It is possible to revalidate, `revalidatePath`, or `revalidateTag` in pages or layouts rendered with `force-static`.
  - `export const fetchCache = 'auto' | 'default-cache' | 'only-cache' | 'force-cache' | 'default-no-store' | 'only-no-store' | 'force-no-store'`
    - `'auto'` (default): fetch before Request-time APIs uses its `cache` option; fetches after Request-time APIs are not cached.
    - `'default-cache'`: allow any `cache` option; default no-option fetches to `'force-cache'`, so fetches after Request-time APIs are considered static.
    - `'only-cache'`: default no-option fetches to `'force-cache'` and error if any `fetch` uses `'no-store'`.
    - `'force-cache'`: set all `fetch` requests to `'force-cache'`.
    - `'default-no-store'`: allow any `cache` option; default no-option fetches to `'no-store'`, so fetches before Request-time APIs are considered dynamic.
    - `'only-no-store'`: default no-option fetches to `'no-store'` and error if any `fetch` uses `'force-cache'`.
    - `'force-no-store'`: set all `fetch` requests to `'no-store'` and re-fetch every request even if they request `'force-cache'`.
    - Cross-route behavior: a `force-*` option wins over an `only-*` option on the same route. `'only-cache'` and `'only-no-store'` cannot be mixed in one route; `'force-cache'` and `'force-no-store'` cannot be mixed in one route. A parent cannot provide `'default-no-store'` if a child provides `'auto'` or `'*-cache'`, because the same fetch could behave differently. Leave shared parent layouts as `'auto'` and customize where child segments diverge.
  - `export const revalidate = false | 0 | number`
    - `false` (default): cache `fetch` requests that opt into `'force-cache'` or are discovered before a Request-time API; equivalent to `Infinity` but individual fetches can opt out. Individual fetches can set a lower positive `revalidate` to increase frequency.
    - `0`: always dynamically render; changes default `fetch` to `'no-store'` but leaves explicit `'force-cache'` or positive `revalidate` fetches as is.
    - `number`: set default revalidation frequency in seconds.
    - The lowest `revalidate` across each layout and page of a single route determines the revalidation frequency of the entire route. Individual `fetch` requests can set a lower `revalidate` than the route default to increase frequency.
    - The value must be statically analyzable (e.g. `revalidate = 600` is valid, but `revalidate = 60 * 10` is not). Not available with deprecated `runtime = 'edge'`. In development, pages are always rendered on-demand and never cached.
- On-demand revalidation uses `revalidateTag` and `revalidatePath`.
- Deduplicate non-`fetch` requests within a render pass with React `cache`.
- Do not apply Cache Components APIs (`'use cache'`, `cacheLife`, `cacheTag`, `updateTag`) to projects still on this model.

## Route Handlers and `GET` caching

- Route Handlers are not cached by default. `GET` methods can be cached using route segment configs in the previous model (e.g. `export const dynamic = 'force-static'`).
- With Cache Components enabled, `GET` Route Handlers follow the same prerendering model as pages and can use `use cache` in a helper function for caching. `use cache` cannot be used directly inside a Route Handler body.
- Prerendering stops if the `GET` handler accesses network requests, DB queries, async filesystem operations, request object properties (`request.url`, `request.headers`, `request.cookies`, `request.body`), runtime APIs (`cookies()`, `headers()`, `connection()`), or non-deterministic operations like `Math.random()`.

## CDN caching

Next.js sets standard `Cache-Control` headers for static, ISR, and dynamic routes. CDNs that honor `s-maxage` and `stale-while-revalidate` can cache static/ISR pages at the edge. On-demand revalidation invalidates the Next.js server cache; to propagate to a CDN, call your CDN purge API alongside `revalidateTag()`/`revalidatePath()` (include both HTML and RSC variants). Static assets under `/_next/static/` are hashed and served with a one-year `immutable` directive. Use `assetPrefix` to serve static assets from a separate CDN origin.

### Current request headers

App Router responses vary on these request headers; Next.js sets a `Vary` header to signal them:

- `rsc` — return RSC payload instead of HTML (must be forwarded by CDNs)
- `next-router-state-tree` — current router state for targeted segment updates
- `next-router-prefetch` — prefetch request indicator
- `next-router-segment-prefetch` — specific segment being prefetched
- `next-url` — only for interception routes; carries the URL being intercepted

Many CDNs do not support `Vary` on custom headers. Next.js addresses this with the `_rsc` search parameter, a hash of the relevant header values that acts as a cache-key discriminator. The `_rsc` parameter must be included in the cache key.

### Static prefetches (PPR-enabled routes)

For PPR-enabled routes, when `next-router-prefetch` is set the response is deterministic and the `next-router-state-tree` header is not parsed. CDNs can cache static prefetch responses if they include `_rsc` in the cache key and respect `Cache-Control`.

### Pathname-based cache keying (direction)

The Next.js team is moving all cache-affecting inputs into the URL pathname, eliminating custom-header `Vary` and the `_rsc` search parameter. Under this model:

- Full-page RSC: `/my/page.rsc`
- Segment RSC: `/my/page.segments/path/to/segment.segment.rsc`

The pathname becomes the cache key, search parameters can be dropped, and standard HTTP cache headers are sufficient. This is in active design and already used by segment prefetches and `output: 'export'`.

## Common mistakes to prevent

- Assuming `fetch` is cached by default.
- Applying v16 Cache Components APIs to a v14/v15 project.
- Using `revalidatePath` everywhere instead of precise `cacheTag` invalidation.
- Putting runtime API reads inside a plain `use cache` scope.
- Clearing `.next` as a diagnosis instead of identifying the caching mismatch.

## What to cache

- Cache data that doesn't depend on runtime request data and that you're OK serving from cache for a period of time.
- For content that doesn't need time-based revalidation (e.g. CMS data), use a long `cacheLife` like `max` with `cacheTag`, and trigger `revalidateTag` from a webhook when the content changes. This avoids unnecessary time-based revalidation.
- In serverless environments, in-memory cache entries may not persist across revalidations; reach for `use cache: remote` if durable shared caching is needed.

## Source URLs

- Caching overview: https://nextjs.org/docs/app/getting-started/caching
- Revalidating: https://nextjs.org/docs/app/getting-started/revalidating
- Draft Mode: https://nextjs.org/docs/app/guides/draft-mode
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
- `draftMode()`: https://nextjs.org/docs/app/api-reference/functions/draft-mode
- How revalidation works: https://nextjs.org/docs/app/guides/how-revalidation-works
- `cacheHandlers`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandlers
- `use cache` directive: https://nextjs.org/docs/app/api-reference/directives/use-cache
- `use cache: private`: https://nextjs.org/docs/app/api-reference/directives/use-cache-private
- `use cache: remote`: https://nextjs.org/docs/app/api-reference/directives/use-cache-remote
- `use client` directive: https://nextjs.org/docs/app/api-reference/directives/use-client
- `use server` directive: https://nextjs.org/docs/app/api-reference/directives/use-server
- `cacheComponents`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `cacheLife`: https://nextjs.org/docs/app/api-reference/functions/cacheLife
- `cacheTag`: https://nextjs.org/docs/app/api-reference/functions/cacheTag
- `revalidateTag`: https://nextjs.org/docs/app/api-reference/functions/revalidateTag
- `updateTag`: https://nextjs.org/docs/app/api-reference/functions/updateTag
- `revalidatePath`: https://nextjs.org/docs/app/api-reference/functions/revalidatePath
- `refresh`: https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/refresh.mdx
- `io`: https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx
- `connection`: https://nextjs.org/docs/app/api-reference/functions/connection
- `next/after` (`after()`): https://nextjs.org/docs/app/api-reference/functions/after
- `unstable_cache`: https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_cache.mdx
- `unstable_noStore`: https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_noStore.mdx
- `generateStaticParams`: https://nextjs.org/docs/app/api-reference/functions/generate-static-params
- `instant` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant
- `dynamicParams` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/dynamicParams
- `maxDuration` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/maxDuration
- `runtime` segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime
- Route segment config index: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config
- Previous model: https://nextjs.org/docs/app/guides/caching-without-cache-components
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
- Partial Prefetching: https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching
- Instant navigation: https://nextjs.org/docs/app/guides/instant-navigation
- Optimizing prefetching: https://nextjs.org/docs/app/guides/optimizing-prefetching
- CDN caching: https://nextjs.org/docs/app/guides/cdn-caching
- ISR with Cache Components: https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components
- ISR (previous model): https://nextjs.org/docs/app/guides/incremental-static-regeneration
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
- `partialPrefetching` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching
- Building: https://nextjs.org/docs/app/guides/building
- `--debug-prerender`: https://nextjs.org/docs/app/api-reference/cli/next#debugging-prerender-errors
- `--debug-build-paths`: https://nextjs.org/docs/app/api-reference/cli/next#building-specific-routes
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- Progressive Web Apps: https://nextjs.org/docs/app/guides/progressive-web-apps
- Web app manifest convention: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- Preserving UI state: https://nextjs.org/docs/app/guides/preserving-ui-state
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — caching additions (ingest 2026-08-30)

Sourced from `docs/01-app/02-guides/` on canary. Merge of operational rules not already in this reference.

**Caching without Cache Components (`caching-without-cache-components`)**
- `revalidate = 600` is valid, but `revalidate = 60 * 10` is NOT — the revalidate value must be statically analyzable at build time. (Source: https://nextjs.org/docs/app/guides/caching-without-cache-components)
- `revalidate` is unavailable when using the deprecated `runtime = 'edge'`. (Source: above)
- In development, pages are always rendered on-demand and are never cached. (Source: above)

**Incremental Static Regeneration (without Cache Components) (`incremental-static-regeneration`)**
- `generateStaticParams` enables ISR for a dynamic route by returning the list of params to prerender; the `revalidate` export then controls the refresh window. (Source: https://nextjs.org/docs/app/guides/incremental-static-regeneration)
- If using `cacheComponents`, use the "ISR with Cache Components" guide instead — the non-Cache-Components guide does not apply. (Source: above)

**ISR with Cache Components (`incremental-static-regeneration-cache-components`)**
- With `cacheComponents` enabled, `fallback: true` in `getStaticParams` is the default behavior: visitors get a `<Suspense>` fallback instantly and content streams in for unknown params. (Source: https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components)
- The App Shell for unlisted params is served from Next.js 16.3+; earlier versions wait for a full server render before responding. (Source: above)

**CDN caching (`cdn-caching`)**
- For routes without PPR, the `next-router-state-tree` header is read during prefetch requests to determine which segments to send. (Source: https://nextjs.org/docs/app/guides/cdn-caching)
- When using a CDN, include `next-router-prefetch` and `next-router-state-tree` headers in the cache key, or use the `_rsc` query parameter as a cache-key discriminator. (Source: above)

**Partial Prefetching + Cache Components (`adopting-partial-prefetching`)**
- Partial Prefetching only works when `cacheComponents` is enabled (Source: https://nextjs.org/docs/app/guides/adopting-partial-prefetching).
- `cookies()` and `headers()` do NOT tie a prefetch to a URL — they vary per session, not per link, so the App Shell still carries session content. Only `params` and `searchParams` are URL data that varies per link. (Source: above)
- The App Shell carries cached content whose `stale` time is at least 5 minutes (the `default` profile and every preset except `seconds`). Shorter-lived content streams in after navigation. (Source: above)
- The Link prop `prefetch={true}` in a layout/component cannot force deeper segments to prefetch; prefetching happens at the boundary where the link is rendered and is limited to segments already in the visible tree. (Source: above)
