# Configuration

Reference: https://nextjs.org/docs/app/api-reference/config/next-config-js

## `next.config.*`

Supported extensions: `.js`, `.mjs`, `.ts`. TypeScript config is recommended:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // options
}

export default nextConfig
```

## Version-sensitive config (v16+)

### `cacheComponents`

Enables Cache Components, component/function-level caching with the `use cache` directive, Partial Prerendering (PPR) as the default, `cacheLife`, `cacheTag`, and `cacheHandlers`. Data fetching is dynamic by default under Cache Components; you explicitly choose what to cache at the page, component, or function level.

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
}
```

- Requires the **Node.js runtime**. Routes that use the deprecated `runtime = 'edge'` export must be migrated; other server-side JavaScript runtimes are not guaranteed to work.
- If you previously used `experimental.useCache` or `experimental.dynamicIO`, migrate using the [Version 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16#experimentaldynamicio-and-experimentalusecache).
- `experimental.ppr` and the `experimental_ppr` route segment config are removed; PPR is the default behavior when `cacheComponents` is enabled.
- `cacheComponents` also enables React's `<Activity>` mode to preserve component state during client-side navigation (routes stay "hidden" instead of unmounting; effects clean up on hide and recreate on show). See the [Preserving UI state guide](https://nextjs.org/docs/app/guides/preserving-ui-state) for patterns around dropdowns, dialogs, and testing.
- Introduced in Next.js 16.0.0. ([cacheComponents](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents))

### `turbopack`

Turbopack is the default bundler in v16 for `next dev` and `next build`. Configure it at top level:

```ts
const nextConfig: NextConfig = {
  turbopack: {
    // root, rules, resolveAlias, resolveExtensions, debugIds
  },
}
```

- Remove `--turbopack` / `--turbo` from scripts.
- Keep Webpack with `--webpack` if a custom webpack config is required.
- `experimental.turbopack` is deprecated; migrate to top-level `turbopack`.
- Top-level `turbopack` options: `root` (absolute path; auto-detected via lockfiles), `rules` (file glob → loaders), `resolveAlias`, `resolveExtensions`, `debugIds`. ([turbopack config](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack))
- Individual imports can specify Turbopack loaders via `with { turbopackLoader, turbopackLoaderOptions, turbopackAs, turbopackModuleType }` attributes. Turbopack-only; webpack ignores them. Requires the `with` keyword (not `assert`). ([turbopack](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack))

### `partialPrefetching`

Requires `cacheComponents` (introduced in Next.js 16.3.0). When enabled, the default `<Link>` prefetch fetches only the route's App Shell; use `prefetch={true}` per link to also resolve URL-specific content (`params`, `searchParams`).

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
}
```

Without `cacheComponents`, `next dev` and `next build` throw at config validation.

A segment can override the app default by exporting `prefetch`:

```ts
export const prefetch = 'partial' // or 'full', 'none'
```

**Session-scoped App Shells:** Routes that read `cookies()` or `headers()` produce an App Shell that includes session data. The framework auto-detects this and caches the shell **per session** on the client. This means the App Shell is NOT shared across sessions even though it's not URL-specific in the `params`/`searchParams` sense. ([partialPrefetching](https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching))

### `serverActions`

Server Actions are stable since Next.js 14 (enabled by default). v13 used `experimental.serverActions: true`. Configure under `experimental.serverActions`:

```ts
const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
      bodySizeLimit: '2mb',
    },
  },
}
```

- `allowedOrigins` — extra safe hosts for the CSRF check. Wildcard rules: `*` = exactly one label, `**` = one or more labels (pattern start only); ports can't be wildcarded; partial replacement not supported. Write the host visible in the browser address bar, not the internal proxy host. Requests with no `Origin` header are allowed with a warning.
- `bodySizeLimit` — default **1MB**; applies to the **raw HTTP body** including `multipart/form-data` overhead (boundaries, headers, metadata). Leave ~10–20 KB headroom. Values like `'2mb'`, `'500kb'`, or byte numbers.
- CSRF check compares the request's `Origin` header against the app's own host (`x-forwarded-host` or `host`). The check runs in **production and development**.
- For reverse proxies, set `allowedDevOrigins` (dev-server assets) **and** `allowedOrigins` (Server Actions) for the same tunnel host.

### `useOffline`

Experimental (introduced in v16.x.0). Enables offline connectivity detection and automatic retry of failed navigations, prefetches, and Server Actions. Also exposes the `useOffline` hook from `next/offline` for Client Components to read connectivity state and render UI.

```ts
const nextConfig: NextConfig = {
  experimental: {
    useOffline: true,
  },
}
```

- Enters offline state either via the browser `offline` event or when a navigation/prefetch/Server Action `fetch()` rejects with a non-abort, non-timeout network error (covers captive portals/broken DNS while `navigator.onLine` still reports `true`). ([useOffline](https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline))
- While offline, Next.js polls connectivity with a single `HEAD` request to the current page's RSC endpoint, aborted after 200 ms. A normal resolution or a 200 ms timeout counts as online; any other rejection schedules the next check. ([useOffline](https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline))
- Backoff is stepped and capped: 500 ms → 1 s → 2 s → 3 s for all subsequent attempts. The browser `online` event short-circuits the wait and runs an immediate check. ([useOffline](https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline))
- The polling loop **never gives up** on its own; it continues at the 3-second cap until a check succeeds or the page unloads. ([useOffline](https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline))
- Blocked framework requests wait for the next successful connectivity check, then run once. If they fail with a network error, the app re-enters offline state and polling resumes. Only the last pending navigation is kept, Server Actions remain pending while buttons are typically disabled, and prefetches use the existing prefetch queue. ([useOffline](https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline))

### `useTypeScriptCli`

Experimental. By default, `next build` runs the project-local `tsc` CLI instead of loading the TypeScript JavaScript compiler API. This supports TypeScript 6 and enables TypeScript 7 (which does not currently expose the JS API). Install `typescript@^7` in the project; no extra config is needed.

```ts
const nextConfig: NextConfig = {
  experimental: {
    useTypeScriptCli: false,
  },
}
```

- Set `experimental.useTypeScriptCli: false` to opt back into the JavaScript compiler API. If you opt out while using TypeScript 7, `next build` exits because that API is unavailable. ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))
- Next.js still generates `next-env.d.ts`, route types, and applies recommended `tsconfig` settings before running the checker. ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))
- TypeScript diagnostics are printed directly from `tsc`; Next.js-specific code frames and error rewriting are not applied. ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))
- The complete project selected by the configured `tsconfig` is checked, including test files and `.next/dev/types` when included. `next build --debug-build-paths` does not narrow this set and produces a warning when combined with the CLI checker. ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))
- `typescript.tsconfigPath` selects the project passed to `tsc`; `typescript.ignoreBuildErrors` skips type checking, including the CLI checker. ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))

### `serverComponentsHmrCache`

Experimental. Caches `fetch` responses in Server Components across Hot Module Replacement (HMR) refreshes in local development. Reduces repeated API calls and billed API usage.

**Default is `true`** — HMR cache applies to **all** `fetch` requests, including those with `cache: 'no-store'`. Uncached requests may not show fresh data between HMR refreshes. The cache is cleared on navigation or full-page reloads. Set `false` to disable.

```ts
const nextConfig: NextConfig = {
  experimental: {
    serverComponentsHmrCache: true,
  },
}
```

## Additional `next.config` options (canary-sourced)

These options are not in the common table above. Source index: https://nextjs.org/docs/app/api-reference/config/next-config-js

### `cacheLife` (custom profiles)
Enable `cacheComponents: true`, then define named profiles under `cacheLife`. Each profile has `stale`, `revalidate`, `expire` (seconds; `expire` must be longer than `revalidate`) and is used via `cacheLife('name')` inside a `'use cache'` scope. You can override built-ins (`default`, `seconds`, `minutes`, `hours`, `days`, `weeks`, `max`). Use custom profiles to match domain cache lifetimes (e.g. a `blog` profile with `stale: 3600`, `revalidate: 900`, `expire: 86400`). ([cacheLife config](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheLife))

### `cacheHandlers`
Map handler file paths (use `require.resolve`) to cache storage for `'use cache'` (`default`) and `'use cache: remote'` (`remote`); you can also register named handlers (`'use cache: <name>'`). A handler implements the `CacheHandler` interface (`get`, `set`, `refreshTags`, `getExpiration`, `updateTags`) with types from `next/cache` (`import type { CacheHandler, CacheEntry } from 'next/cache'`). Without config, Next.js uses an in-memory LRU for both. Use custom handlers to share cache across instances or store externally (Redis/DB/disk); most apps don't need them. `'use cache: private'` is not configurable.

A `CacheEntry` has `value: ReadableStream<Uint8Array>`, `tags`, `stale`, `timestamp`, `expire`, `revalidate`. In `set()`, await `pendingEntry`, consume the value stream exactly once, and persist the bytes (do not keep the stream, to avoid holding the request alive). In `get()`, wrap stored bytes in a fresh stream on every call and return `undefined` for missing entries; Next.js checks `timestamp` against `expire`/`revalidate` itself. `get()` receives `softTags` (implicit tags derived from the route path) as a second parameter. `getExpiration()` returns the most recent revalidation timestamp across the provided tags, `0` if none, or `Infinity` to defer soft-tag checks to `get()`. `updateTags()` marks tags invalidated (e.g. delete matching entries) and receives an optional `durations` object with `expire` in seconds. `refreshTags()` periodically syncs tag state from shared storage before starting a new request. For distributed tag coordination, write invalidation timestamps in `updateTags()` and read them in `refreshTags()` / `getExpiration()`. **Error handling:** `set()` failure does NOT fail the response (the stream is already flowing); the entry is lost and the next request re-renders. Catch errors in `set()` anyway — a rejected `set()` joins the request's pending revalidation work and surfaces as a failed background task. `get()` failure is NOT wrapped by the framework — an unhandled exception propagates as a render error, so catch and return `undefined` (cache miss). For external stores, use atomic writes or write-then-rename to avoid serving partial entries. Not supported with static export; adapter support is platform-specific. Introduced in v16.0.0. ([cacheHandlers](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandlers))


Bytes of in-memory cache per server instance; default `50 * 1024 * 1024` (50 MB). Sizes both the server cache (prerendered pages, route-handler responses, optimized images) and the built-in `'use cache'` handler. Set `0` to disable both in-memory caches (mimics serverless, where entries rarely survive between requests). If you register your own `cacheHandlers`, this option no longer applies to that handler. `next dev` keeps its own in-memory cache regardless. ([cacheMaxMemorySize](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheMaxMemorySize))

### `authInterrupts` (experimental)
Enables the `forbidden()` / `unauthorized()` APIs. Set `experimental: { authInterrupts: true }` in `next.config.*` before calling either function. ([authInterrupts](https://nextjs.org/docs/app/api-reference/config/next-config-js/authInterrupts))

### `allowedDevOrigins`
- `allowedDevOrigins`: array of origin **hostnames** (no scheme/port) allowed to request the dev server for cross-origin dev assets (e.g. tunnels). Wildcards: `*` = exactly one label, `**` = one or more labels, only at the start. Default-allowed: `localhost`, its subdomains, and the started hostname. The **started hostname** is automatically allowed in addition to `localhost`, so only add non-default hosts. A no-cors cross-site request (e.g. a script tag loading a dev asset) sends no `Origin` header — those are matched on the `Referer` hostname instead. Partial replacement is not supported (write `*.local-origin.dev`, not `team-*.local-origin.dev`). ([allowedDevOrigins](https://nextjs.org/docs/app/api-reference/config/next-config-js/allowedDevOrigins))

### `adapterPath`
Path to a custom adapter module (`require.resolve('./my-adapter.js')`) or the `NEXT_ADAPTER_PATH` env, to hook the Next.js build for deployment platforms. ([adapterPath](https://nextjs.org/docs/app/api-reference/config/next-config-js/adapterPath))

### `assetPrefix`
CDN prefix applied to `/_next/static` JS/CSS requests (e.g. `https://cdn.example.com`). Does **not** affect `public/` files or `/_next/data/` (Pages Router). Set per phase via async config. Vercel configures this automatically. ([assetPrefix](https://nextjs.org/docs/app/api-reference/config/next-config-js/assetPrefix))

### `basePath`
Deploy under a sub-path (e.g. `/docs`); inlined into client bundles at build time (cannot change without a rebuild). Auto-applied to `next/link` hrefs and `next/router`; `next/image` `src` needs the prefix added manually. ([basePath](https://nextjs.org/docs/app/api-reference/config/next-config-js/basePath))

### `compress`
`gzip` on by default with `next start` / custom server; set `false` only when compression is already handled externally (e.g. nginx + brotli). Not recommended to disable otherwise. ([compress](https://nextjs.org/docs/app/api-reference/config/next-config-js/compress))

### `crossOrigin`
Adds `crossOrigin` to all `<script>` tags from `next/script` (and in the Pages Router, also `next/head`): `'anonymous'` or `'use-credentials'`. ([crossOrigin](https://nextjs.org/docs/app/api-reference/config/next-config-js/crossOrigin))

### `cssChunking` (experimental)
Controls how CSS is split/re-ordered into chunks so a route loads close to only the CSS it needs.

- **`true` (default)** — both webpack and Turbopack merge CSS to reduce requests.
- **`false`** — webpack only; no merge/reorder.
- **`'strict'`** — webpack only; load CSS in import order, which prevents merges that could violate dependencies but creates more chunks/requests.
- **`'graph'`** — Turbopack only; cost-based graph algorithm that groups CSS across routes. Tune with `{ type: 'graph', requestCost, weightDistribution }`:
  - `requestCost` (default `20000`): estimated byte cost of each extra CSS request. Larger values bias toward fewer, larger shared chunks.
  - `weightDistribution` (default `0.1`): controls how shared-chunk cost is distributed across routes, weighted by how much CSS each route imports.

For most apps the default `true` is correct; reach for `'strict'` only for webpack CSS-order correctness, or `'graph'` to tune Turbopack request/byte trade-offs. ([cssChunking](https://nextjs.org/docs/app/api-reference/config/next-config-js/cssChunking))

### `deploymentId`
Version-skew protection + cache busting for rolling/multi-server deploys.

- Appends `?dpl=<id>` to static-asset URLs (JS, CSS, images).
- Adds an `x-deployment-id` header to client-side navigation requests and an `x-nextjs-deployment-id` header to navigation responses.
- Injects a `data-dpl-id` attribute on the `<html>` element.
- Includes the `deploymentId` in the [`'use cache'` cache key](https://nextjs.org/docs/app/api-reference/directives/use-cache#cache-keys), invalidating cache entries when the deployment ID changes.
- `config.deploymentId` takes precedence over the `NEXT_DEPLOYMENT_ID` environment variable. Set `NEXT_DEPLOYMENT_ID=my-deployment-id next build` as an alternative to config.
- On mismatch the client does a hard reload to ensure assets<AppOnly> and Server Functions</AppOnly> come from a consistent deployment version.
- Next.js does **not** route on `?dpl=`; it is only for cache busting.
- A per-deployment value only avoids skew if the host/CDN also routes by deployment; otherwise mismatches still trigger reloads.
- `generateBuildId` has **no effect when `deploymentId` is set** for version-skew detection (Pages Router uses the response header instead).
- Stabilized as a top-level config option in v14.1.4; introduced as `experimental.deploymentId` in v13.4.10. In v16.2.0, Pages Router detects version skew from the response header rather than the build ID, and the build ID is constant when `deploymentId` is set. ([deploymentId](https://nextjs.org/docs/app/api-reference/config/next-config-js/deploymentId))

### `devIndicators`
Dev on-screen route indicator; `position` (`bottom-left` default | `bottom-right` | `top-left` | `top-right`) or `false` to hide. Confirm prerender vs dynamic with `next build --debug` (`○` static, `ƒ` dynamic). Removed in v16: `appIsrStatus`, `buildActivity`, `buildActivityPosition`. ([devIndicators](https://nextjs.org/docs/app/api-reference/config/next-config-js/devIndicators))

### Unit testing `next.config.js` (experimental, v15.1+)
The `next/experimental/testing/server` package contains `unstable_getResponseFromNextConfig` to unit test `headers`, `redirects`, and `rewrites` from `next.config.js`. It returns a `NextResponse` with routing results. **Caveat**: it ignores Proxy and filesystem routes, so results may differ from production. Also exports `getRedirectUrl(response)` to extract the redirect target. ([next.config index](https://nextjs.org/docs/app/api-reference/config/next-config-js))

### `distDir`
Custom build output dir instead of `.next`; must stay inside the project (e.g. `../build` is invalid). ([distDir](https://nextjs.org/docs/app/api-reference/config/next-config-js/distDir))

### `env` (legacy)
Inlines values into the client bundle at build time; `process.env.<key>` is replaced statically. The `NEXT_PUBLIC_` prefix only matters for `.env`/environment vars, not for the `env` config option. Destructuring `process.env` won't work due to webpack `DefinePlugin`. Prefer `.env` files. The page notes this config is legacy and points to environment variables since Next.js 9.4. ([env](https://nextjs.org/docs/app/api-reference/config/next-config-js/env))

### `appDir` (legacy)
No longer required as of Next.js 13.4 (App Router is stable). ([appDir](https://nextjs.org/docs/app/api-reference/config/next-config-js/appDir))

### `htmlLimitedBots`
Regex of user agents that should receive blocking (non-streaming) metadata instead of streaming metadata. Overrides the Next.js default list (Google crawlers, Bingbot, Twitterbot, Slackbot, etc.). Set `htmlLimitedBots: /.*/` to fully disable streaming metadata. Introduced in v15.2.0. ([htmlLimitedBots](https://nextjs.org/docs/app/api-reference/config/next-config-js/htmlLimitedBots))

### `inlineCss` (experimental)
Inlines CSS into `<head>` as `<style>` tags instead of `<link>` tags. Best for first-time visitors and atomic CSS (Tailwind); hurts returning visitors and large CSS bundles. Prod-only, global, no per-page configuration. Known limitations: styles are duplicated during initial page load (SSR + RSC payload), and prerendered pages still use `<link>` tags on navigation to avoid duplication. ([inlineCss](https://nextjs.org/docs/app/api-reference/config/next-config-js/inlineCss))

### `instrumentationClientInject` (v16.3.0)
Array of client modules imported for side effects before the project's `instrumentation-client.{js,ts}` runs and ahead of React hydration. Intended for `next.config.js` plugins (e.g. `withSentry`, `withAnalytics`) so they can inject client instrumentation without requiring every project to author the file convention. Each entry may be a bare npm package name or a root-relative path. Injected modules may optionally export `onRouterTransitionStart(url, navigationType)`; Next.js composes hooks in array order, with the user file's hook running last. ([instrumentationClientInject](https://nextjs.org/docs/app/api-reference/config/next-config-js/instrumentationClientInject))

## More config options (canary-sourced, continued)

### `cacheHandler` (server ISR / route / image cache) — singular
Stable since 14.1.0; renamed from the experimental `incrementalCacheHandlerPath`, which is now **deprecated — do not use `incrementalCacheHandlerPath` on v14.1.0+**. It caches server data: ISR pages, route-handler responses, and optimized images. It is **not** the handler for `'use cache'` Cache Components — that is `cacheHandlers` (plural, see above). Pair with `cacheMaxMemorySize: 0` to disable default in-memory caching. A handler implements `get`, `set`, `revalidateTag`, `resetRequestCache`; `ctx.kind` is `'APP_PAGE' | 'APP_ROUTE' | 'PAGES' | 'FETCH' | 'IMAGE'`. Enable image-optimization caching with `images.customCacheHandler: true` (becomes default in the next major; v16.2.0+). When handling image cache entries, `kind` is `'IMAGE'` and data includes `buffer`, `etag`, `extension`, `revalidate`. Not supported with static export; adapter support is platform-specific. ([cacheHandler](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheHandler))

### `images` — custom loader
`images.loader: 'custom'` + `images.loaderFile` points to a root-relative module exporting a default function `({ src, width, quality }) => string`. In the App Router the loader file must be a Client Component (`'use client'`) so the function can be serialized. Alternatively pass `loader` per `<Image>`. ([images](https://nextjs.org/docs/app/api-reference/config/next-config-js/images))

### `output` — standalone tracing details
`output: 'standalone'` emits `.next/standalone` plus a minimal `server.js` (run via `node server.js`; honors `PORT`/`HOSTNAME` env vars). It does **not** copy `public/` or `.next/static` — copy them manually (`cp -r public .next/standalone/ && cp -r .next/static .next/standalone/.next/`). Tracing uses `@vercel/nft`. Monorepos: set `outputFileTracingRoot: path.join(__dirname, '../../')` to trace from the monorepo base; use `outputFileTracingIncludes` / `outputFileTracingExcludes` (keys are picomatch route globs like `/api/hello`; values are globs resolved from the project root) to add/remove traced files. Edge Runtime routes and fully static pages are unaffected by these includes/excludes. ([output](https://nextjs.org/docs/app/api-reference/config/next-config-js/output))

### `outputHashSalt` (v16.3.0)
Salt string mixed into every content-addressed output filename (chunks, assets). Changing it forces all output hashes to change, useful for invalidating cached assets across deployments without editing source. Works with Webpack and Turbopack. The `NEXT_HASH_SALT` environment variable concatenates with `outputHashSalt` when both are set. ([outputHashSalt](https://nextjs.org/docs/app/api-reference/config/next-config-js/outputHashSalt))

### `pageExtensions`
Default accepted extensions: `.tsx`, `.ts`, `.jsx`, `.js`. Extend to include `.md` / `.mdx` when using `@next/mdx`. In the Pages Router, changing `pageExtensions` also affects `proxy`, `instrumentation`, `pages/_document`, `pages/_app`, and `pages/api/` — rename all of them (e.g. `proxy.page.ts`) if using a custom extension like `.page.ts`. ([pageExtensions](https://nextjs.org/docs/app/api-reference/config/next-config-js/pageExtensions))

### `headers` — operational rules
`headers()` may be sync or async and returns an array of `{ source, headers, basePath?, locale?, has?, missing? }`. Headers are evaluated **before** the filesystem (pages + `/public`). Duplicate keys on overlapping sources: **last match wins**. `source` uses path-to-regexp — modifiers `*` (0+), `+` (1+), `?` (0–1); regex-special chars must be escaped. `has`/`missing` support `type: 'header' | 'cookie' | 'host' | 'query'`. With `basePath`, each `source` is auto-prefixed unless `basePath: false`. **You cannot set `Cache-Control` in `next.config.js` for immutable assets** (filenames with a SHA hash, e.g. static image imports) — Next.js forces `public, max-age=31536000, immutable` and ignores overrides. ([headers](https://nextjs.org/docs/app/api-reference/config/next-config-js/headers))

### `redirects` — operational rules
`redirects()` may be sync or async and returns an array of `{ source, destination, permanent, basePath?, locale?, has?, missing? }`. Redirects are checked **before the filesystem** (pages + `/public`). **Next.js uses 307 (temporary) and 308 (permanent) to preserve the HTTP method** — unlike 301/302, these do not change `POST` to `GET`. Query values pass through to the destination automatically. `source` uses path-to-regexp: `:param` (single segment), `:param*` (zero or more), `:param+` (one or more), `:param?` (zero or one); regex in parentheses `/post/:slug(\\d{1,})`; special chars `( ) { } : * + ?` must be escaped with `\\`. `has`/`missing` support `type: 'header' | 'cookie' | 'host' | 'query'` with `key` and optional `value` (regex capture supported). `basePath: false` skips auto-prefixing (external redirects). `locale: false` (Pages Router) skips locale auto-prefixing. In the App Router, use hardcoded locale paths or dynamic segments + Proxy for per-request locale redirects. Custom `statusCode` can replace `permanent` (not both); IE11 gets a `Refresh` header for 308. Redirects in the Pages Router are **not** applied to client-side routing (`Link`, `router.push`) unless Proxy is present and matches the path. ([redirects](https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects))

### `rewrites` — operational rules
`rewrites()` may be sync or async and returns either an array or `{ beforeFiles, afterFiles, fallback }`. Rewrites act as a URL proxy — the browser URL does not change. **Evaluation order (App Router):** (1) `headers` → (2) `redirects` → (3) Proxy → (4) `beforeFiles` rewrites → (5) static files (`public/`, `_next/static`, pages) → (6) `afterFiles` rewrites → (7) dynamic routes → (8) `fallback` rewrites (before 404). `beforeFiles` do not check the filesystem immediately after matching — they continue until all `beforeFiles` are checked. `source`/`destination` use path-to-regexp (same as redirects). **Parameter pass-through:** if a parameter is NOT used in `destination`, it is automatically passed as a query param; if used in `destination`, no auto-pass (add manually via `?key=:param`). `has`/`missing` support header/cookie/host/query matching. `basePath: false` for external rewrites. External URL rewrites supported (incremental adoption). With `trailingSlash: true`, insert trailing slashes in `source`/`destination`. Rewrites are **applied to client-side routing**: `<Link href="/about">` will serve content from `/` while keeping the URL as `/about` when a rewrite matches. ([rewrites](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites))

### `logging` — dev logging knobs
`logging.fetches.fullUrl` (log full fetch URL), `logging.fetches.hmrRefreshes` (log HMR-cache-restored fetches), `logging.serverFunctions` (`false` to stop logging Server Function calls), `logging.incomingRequests` (`false` or `{ ignore: [/regex/] }`), `logging.browserToTerminal` (`'warn'` default | `'error'` | `true` | `false` — forwards browser console to terminal with source location), and `logging: false` to disable all dev logging. Dev-only; no production effect. ([logging](https://nextjs.org/docs/app/api-reference/config/next-config-js/logging))

### `reactCompiler`
Set `reactCompiler: true` (or `{ compilationMode: 'annotation' }` for opt-in). Requires the `babel-plugin-react-compiler` dev dependency. Opt-in mode uses the `"use memo"` / `"use no memo"` directives on components/hooks. Next.js applies it only to relevant files (JSX/Hooks) via a custom SWC optimization. ([reactCompiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler))

### Custom Babel config

Next.js includes the `next/babel` preset automatically. To extend Babel, add a `.babelrc` (or `babel.config.js`) at the project root; if present, it becomes the source of truth and must include the `next/babel` preset.

- Custom presets/plugins without options go in the top-level `plugins` array alongside the `next/babel` preset. ([babel](https://nextjs.org/docs/pages/guides/babel))
- To pass options to Next.js's internal Babel plugins, wrap them under the `next/babel` preset object with keys `preset-env`, `transform-runtime`, `styled-jsx`, `class-properties`. ([babel](https://nextjs.org/docs/pages/guides/babel))
- Keep `"preset-env".modules` set to `false`; setting it otherwise disables webpack code splitting. ([babel](https://nextjs.org/docs/pages/guides/babel))
- Server-side compilations use the current Node.js version. ([babel](https://nextjs.org/docs/pages/guides/babel))

### `turbopack` — import attributes & inline loader config (v16.2.0)
In addition to `turbopack.rules` (file-extension → loaders mapping), individual imports can specify loaders via `with { turbopackLoader, turbopackLoaderOptions, turbopackAs, turbopackModuleType }` attributes. These are **Turbopack-only** (webpack ignores them) and require the `with` keyword (not `assert`). Loaders with options pass JSON-encoded strings via `turbopackLoaderOptions`. ([turbopack](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack))

### `turbopackFileSystemCache` (experimental, v16.0+)
Two independent flags, both default `true`: `turbopackFileSystemCacheForDev` (caches `.next/dev/cache/turbopack`) and `turbopackFileSystemCacheForBuild` (caches `.next/cache/turbopack`). Build cache only helps if `.next/cache` is restored between builds (CI, persistent volume). Set `turbopackFileSystemCacheForBuild: false` if builds start from a clean layer. ([turbopackFileSystemCache](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackFileSystemCache))

### `turbopackMemoryEviction` (experimental, v16.3.0)
Only relevant in `next dev` when FileSystem cache is enabled. Controls whether Turbopack evicts in-memory cache copies after persisting to disk. `false` = never evict; `'auto'` (default) = evict after a snapshot once enough memory was allocated; `'full'` = evict all possible data on every disk save. ([turbopackMemoryEviction](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackMemoryEviction))

### `turbopackLocalPostcssConfig` (experimental, v16.3.0)
Reverses PostCSS config resolution: `true` → CSS file's directory first, then project root (per-directory configs win); `false` (default) → project root first. Useful for monorepos with different PostCSS transforms per package. ([turbopackLocalPostcssConfig](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackLocalPostcssConfig))

### `turbopackRustReactCompiler` (experimental, v16.3.0)
Runs the native Rust React Compiler inside Turbopack instead of the Babel transform. **Requires `reactCompiler: true` to be set** (this flag selects implementation, doesn't enable it). **Turbopack-only** — webpack throws an error. When enabled, `babel-plugin-react-compiler` is not needed. ([turbopackRustReactCompiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackRustReactCompiler))

### `turbopackChunking` (experimental)
Tunes Turbopack's production client-side chunker. Size thresholds (bytes of uncompressed, unminified code): `minChunkSize` (50000), `maxChunkCountPerGroup` (40), `maxMergeChunkSize` (200000). App-only: `generateComponentChunks` (false) + `minComponentChunkSize` (20000). Heuristics: `clusters` (arrays of RegExp for routes navigated together), `firstPageLoadPriority` (0–1), `priorityRoutes` (RegExp array), `priorityBoost` (1.5), `requestCost` (200000). ([turbopackChunking](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackChunking))

### `turbopackIgnoreIssue` (experimental, v16.2.0)
Filter Turbopack errors/warnings from CLI output and error overlay. Each rule: `path` (string|RegExp, required), optional `title`, optional `description`. An issue is suppressed when path matches AND all other specified fields match. Prefer `path` over `title`/`description` (titles/descriptions change between Turbopack versions). `turbopack.ignoreIssue` is only available when using Turbopack. ([turbopackIgnoreIssue](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackIgnoreIssue))

### `serverComponentsHmrCache` — default is `true`
The experimental `serverComponentsHmrCache` **defaults to `true`** — `fetch` responses in Server Components are cached across HMR refreshes in dev. This applies to **all** fetches, including those with `cache: 'no-store'`, so uncached requests may not show fresh data between HMR refreshes. The cache is cleared on navigation or full-page reloads. Set `false` to disable. For observability, pair with [`logging.fetches`](/docs/app/api-reference/config/next-config-js/logging) to log fetch cache hits/misses in the dev console. ([serverComponentsHmrCache](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverComponentsHmrCache))

### `reactMaxHeadersLength` (App Router only)
Maximum byte length of React-emitted headers (resource preloads) added to the response during prerendering. Default `6000`. Lower this value if a reverse proxy truncates long headers. ([reactMaxHeadersLength](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactMaxHeadersLength))

### `reactStrictMode`
Since Next.js **13.5.1**, Strict Mode is `true` by default for the **app** router; setting `reactStrictMode: true` is only necessary for `pages`. Can still disable with `reactStrictMode: false`. Strongly recommended to keep it enabled. ([reactStrictMode](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactStrictMode))

### `sassOptions`
Configure the Sass compiler (`additionalData`, `implementation: 'sass-embedded'`, etc.). Note: `sassOptions` are not typed beyond `implementation`. **Turbopack limitation:** the `functions` property (custom Sass functions) is **only supported with webpack** — Turbopack's Rust architecture can't execute JavaScript functions passed via this option. ([sassOptions](https://nextjs.org/docs/app/api-reference/config/next-config-js/sassOptions))

### `typedRoutes` (stable)
Enables statically typed links via TypeScript. Use `typedRoutes: true` (not `experimental.typedRoutes`). Requires TypeScript. ([typedRoutes](https://nextjs.org/docs/app/api-reference/config/next-config-js/typedRoutes))

### `typescript`
- `ignoreBuildErrors`: allow production builds with TypeScript errors. Note: this **completely skips** the type checking step — it does not run TypeScript and suppress errors, it bypasses the check entirely. If disabled, run type checks elsewhere in your deploy pipeline. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- `tsconfigPath`: path to a custom tsconfig file for builds/tooling. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))

### `trailingSlash`
`trailingSlash: true` redirects URLs like `/about` → `/about/`. Exceptions that remain unchanged: static file URLs (with extensions) and any paths under `.well-known/`. With `output: "export"`, the `/about` page outputs `/about/index.html` (instead of `/about.html`). ([trailingSlash](https://nextjs.org/docs/app/api-reference/config/next-config-js/trailingSlash))

### `transpilePackages`
Transpile and bundle a dependency (package names only, including scoped `@scope/pkg`). Replaces `next-transpile-modules`. **A package cannot appear in both `transpilePackages` and `serverExternalPackages`** — Next.js throws at build start. Packages in `optimizePackageImports` and the built-in `default-transpiled-packages.json` are added automatically. ([transpilePackages](https://nextjs.org/docs/app/api-reference/config/next-config-js/transpilePackages))

### `serverExternalPackages` (stable since v15.0.0)
Renamed from `serverComponentsExternalPackages`. Opts dependencies out of Server Components/Route Handler bundling and uses native Node.js `require`. Next.js auto-externalizes ~70+ popular packages (see [`server-external-packages.jsonc`](https://github.com/vercel/next.js/blob/canary/packages/next/src/lib/server-external-packages.jsonc)) — including `@alinea/generated`, `@appsignal/nodejs`, `@aws-sdk/client-s3`, `@aws-sdk/s3-presigned-post`, `@blockfrost/blockfrost-js`, `@highlight-run/node`, `@huggingface/transformers`, `@jpg-store/lucid-cardano`, `@libsql/client`, `@mikro-orm/core`, `@mikro-orm/knex`, `@node-rs/argon2`, `@node-rs/bcrypt`, `@prisma/client`, `@react-pdf/renderer`, `@sentry/profiling-node`, `@sparticuz/chromium`, `@sparticuz/chromium-min`, `@statsig/statsig-node-core`, `@swc/core`, `@xenova/transformers`, `@zenstackhq/runtime`, `argon2`, `autoprefixer`, `aws-crt`, `bcrypt`, `better-sqlite3`, `canvas`, `chromadb-default-embed`, `config`, `cpu-features`, `cypress`, `dd-trace`, `eslint`, `express`, `firebase-admin`, `htmlrewriter`, `import-in-the-middle`, `isolated-vm`, `jest`, `jsdom`, `keyv`, `libsql`, `mdx-bundler`, `mongodb`, `mongoose`, `newrelic`, `next-mdx-remote`, `next-seo`, `node-cron`, `node-pty`, `node-web-audio-api`, `onnxruntime-node`, `oslo`, `pg`, `pino`, `pino-pretty`, `pino-roll`, `playwright`, `playwright-core`, `postcss`, `prettier`, `prisma`, `puppeteer-core`, `puppeteer`, `ravendb`, `require-in-the-middle`, `rimraf`, `sharp`, `shiki`, `sqlite3`, `thread-stream`, `ts-morph`, `ts-node`, `typescript`, `vscode-oniguruma`, `webpack`, `websocket`, `zeromq`. **A package cannot appear in both `serverExternalPackages` and `transpilePackages`** — build throws. ([serverExternalPackages](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverExternalPackages))

### `staleTimes` (experimental, v14.2.0)
Client Cache TTL overrides (seconds). `dynamic` — used when the page is neither statically generated nor fully prefetched (default **0s**, changed from 30s in v15.0.0). `static` — used for statically generated pages, `prefetch={true}`, or `router.prefetch` (default 5 min). Loading boundaries are reusable for the `static` period. Doesn't affect partial rendering (shared layouts aren't refetched on every navigation) or back/forward caching. ([staleTimes](https://nextjs.org/docs/app/api-reference/config/next-config-js/staleTimes))

### `staticGeneration` (experimental)
Tune static-generation parallelism and retry behavior: `staticGenerationRetryCount` (retries before failing the build), `staticGenerationMaxConcurrency` (max pages per worker), `staticGenerationMinPagesPerWorker` (min pages before starting a new worker). ([staticGeneration](https://nextjs.org/docs/app/api-reference/config/next-config-js/staticGeneration))

### `supportsImmutableAssets` (v16.3.0, adapter-oriented)
**Intended for adapter authors.** Allows the `?dpl` query parameter to be omitted for content-addressed static assets so browsers cache them indefinitely and unchanged assets are skipped during subsequent deployments. **Enabling when your provider/adapter doesn't support it can break deployments.** ([supportsImmutableAssets](https://nextjs.org/docs/app/api-reference/config/next-config-js/supportsImmutableAssets))

### `taint` (experimental)
Enables React Taint APIs (`experimental_taintObjectReference`, `experimental_taintUniqueValue`) to prevent sensitive data crossing the Server-Client boundary. **Caveats:** copying a tainted object creates an untainted version (loses guarantees); derived values from tainted values are **not** tainted (you must taint them explicitly); values are tainted only while their lifetime reference is in scope. Not a substitute for filtering data in the DAL. Also enables the React `experimental` channel for `app`. ([taint](https://nextjs.org/docs/app/api-reference/config/next-config-js/taint))

### `urlImports` (experimental)
Import modules directly from external URLs (instead of disk). Security-first: explicitly allow URL prefixes. **Lockfile:** Next.js creates a `next.lock` directory that **must be committed to Git** (do not `.gitignore` it). `next build` uses only the lockfile; `no-cache` resources are fetched on each build. ([urlImports](https://nextjs.org/docs/app/api-reference/config/next-config-js/urlImports))

### `useLightningcss` (experimental)
**webpack-only** — Turbopack has used Lightning CSS by default since Next 14.2 and ignores this flag. With webpack, enables Lightning CSS instead of PostCSS + `postcss-preset-env`. ([useLightningcss](https://nextjs.org/docs/app/api-reference/config/next-config-js/useLightningcss))

### `lightningCssFeatures` (v16.2.0)
Works with both webpack (when `useLightningcss: true`) and Turbopack. Overrides which CSS features Lightning CSS transpiles based on browserslist targets. `include` forces transpilation regardless of browser support; `exclude` prevents transpilation even when targets require it. Use feature names (`nesting`, `not-selector-list`, `dir-selector`, `lang-selector-list`, `is-selector`, `text-decoration-thickness-percent`, `media-interval-syntax`, `media-range-syntax`, `custom-media-queries`, `clamp-function`, `color-function`, `oklab-colors`, `lab-colors`, `p3-colors`, `hex-alpha-colors`, `space-separated-color-notation`, `font-family-system-ui`, `double-position-gradients`, `vendor-prefixes`, `logical-properties`, `light-dark`) or composite groups (`selectors`, `media-queries`, `colors`). ([useLightningcss](https://nextjs.org/docs/app/api-reference/config/next-config-js/useLightningcss))

### `proxyClientMaxBodySize` (experimental)
When Proxy is used, the request body is cloned and buffered in memory (default **10MB**). Set as a string (`'1mb'`) or byte number. If a body exceeds the limit, Next.js buffers only up to the limit, logs a warning naming the route, and **continues processing with the partial body — the request does not fail**. Per-request, not global. ([proxyClientMaxBodySize](https://nextjs.org/docs/app/api-reference/config/next-config-js/proxyClientMaxBodySize))

### `prefetchInlining` (experimental)
App Router bundles small prefetch segment responses into one request by default (`true` since 16.3.0). Set `false` to prefetch each segment separately; pass `{ maxSize, maxBundleSize }` (bytes, gzip-compressed segment response) to tune thresholds (defaults `maxSize: 2048`, `maxBundleSize: 10240`). Only the config flag is experimental; the inlining behavior is permanent. ([prefetchInlining](https://nextjs.org/docs/app/api-reference/config/next-config-js/prefetchInlining))

### `partialPrefetching`
Requires `cacheComponents`. When enabled, the default `<Link>` prefetch fetches only the route's App Shell; use `prefetch={true}` per link to also resolve URL-specific content (`params`, `searchParams`). A segment can override the app default by exporting `prefetch = 'partial'` or `'force-disabled'`. Introduced in v16.3.0. ([partialPrefetching](https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching))

### `poweredByHeader`
Set `false` to drop the default `x-powered-by` header. ([poweredByHeader](https://nextjs.org/docs/app/api-reference/config/next-config-js/poweredByHeader))

### `productionBrowserSourceMaps`
Enable browser source map generation during production builds. Increases build time and memory. ([productionBrowserSourceMaps](https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps))

### `reactCompiler`
Set `reactCompiler: true` (or `{ compilationMode: 'annotation' }` for opt-in). Requires the `babel-plugin-react-compiler` dev dependency. Opt-in mode uses the `"use memo"` / `"use no memo"` directives on components/hooks. Next.js applies it only to relevant files (JSX/Hooks) via a custom SWC optimization. ([reactCompiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler))

### Smaller options
- `expireTime` — custom SWR expire window (seconds) for ISR `Cache-Control`: emitted as `s-maxage=<revalidate>, stale-while-revalidate=<expire - revalidate>`. If revalidate=900 and expireTime=3600, header becomes `s-maxage=900, stale-while-revalidate=2700`. ([expireTime](https://nextjs.org/docs/app/api-reference/config/next-config-js/expireTime))
- `generateBuildId` — async function returning a stable build ID across containers; **no effect when `deploymentId` is set** (deploy ID drives version-skew detection instead). ([generateBuildId](https://nextjs.org/docs/app/api-reference/config/next-config-js/generateBuildId))
- `generateEtags` — set `false` to disable per-page etag generation. ([generateEtags](https://nextjs.org/docs/app/api-reference/config/next-config-js/generateEtags))
- `httpAgentOptions` — `{ keepAlive: false }` disables HTTP Keep-Alive for server-side `fetch` (Node <18 polyfill path). ([httpAgentOptions](https://nextjs.org/docs/app/api-reference/config/next-config-js/httpAgentOptions))
- `mdxRs` (experimental) — Rust MDX compiler via `@next/mdx`. ([mdxRs](https://nextjs.org/docs/app/api-reference/config/next-config-js/mdxRs))
- `onDemandEntries` — dev-only buffer control: `{ maxInactiveAge, pagesBufferLength }`. ([onDemandEntries](https://nextjs.org/docs/app/api-reference/config/next-config-js/onDemandEntries))
- `optimizePackageImports` (experimental) — list of packages to auto tree-shake named-export-heavy modules; many icon/util libraries (lucide-react, date-fns, antd, @mui/*, recharts, react-icons/*, …) are optimized by default. ([optimizePackageImports](https://nextjs.org/docs/app/api-reference/config/next-config-js/optimizePackageImports))
- `exportPathMap` — **legacy / deprecated**, `next export` only; overridden by `getStaticPaths` (Pages) / `generateStaticParams` (App). ([exportPathMap](https://nextjs.org/docs/app/api-reference/config/next-config-js/exportPathMap))

### `webVitalsAttribution`

Experimental. Enables per-metric Web Vitals attribution so you can pinpoint the source of issues (e.g. the first shifted element for CLS, the LCP element/image URL, or event/ navigation/resource timing entries). Disabled by default.

```ts
const nextConfig: NextConfig = {
  experimental: {
    webVitalsAttribution: ['CLS', 'LCP'],
  },
}
```

- Valid values are the metrics defined by the `NextWebVitalsMetric` type (all `web-vitals` metrics). ([webVitalsAttribution](https://nextjs.org/docs/app/api-reference/config/next-config-js/webVitalsAttribution))

### `webpack` (custom webpack config)

Not covered by semver; use only when Next.js doesn't already support the use case. The `webpack` function in `next.config.*` receives `(config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack })` and must return the modified config.

```ts
const nextConfig: NextConfig = {
  webpack: (config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }) => {
    // modify config
    return config
  },
}
```

- Executed three times: once for the client, twice for server-side compilations (`nodejs` and `edge` runtimes). `isServer` is `true` for both server builds. ([webpack](https://nextjs.org/docs/app/api-reference/config/next-config-js/webpack))
- `nextRuntime` is `'edge' | 'nodejs'` for server builds and `undefined` for the client. `'edge'` applies to proxy and Server Components using the Edge runtime. ([webpack](https://nextjs.org/docs/app/api-reference/config/next-config-js/webpack))
- `defaultLoaders.babel` exposes the default `babel-loader` config; use it when chaining custom loaders that depend on Babel (e.g. `@mdx-js/loader`). ([webpack](https://nextjs.org/docs/app/api-reference/config/next-config-js/webpack))
- To keep using Webpack in v16 (where Turbopack is the default), pass `--webpack` to `next dev` / `next build` or keep a custom `webpack` config (Turbopack ignores the `webpack` function). ([turbopack](https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack))

### `typescript` top-level config

Next.js supports TypeScript-first development. Adding TypeScript to an existing project is automatic: rename a file to `.ts`/`.tsx` and run `next dev`/`next build` to install dependencies and scaffold a `tsconfig.json` with recommended settings. Use `next.config.ts` for typed config; supported config extensions are `.js`, `.mjs`, `.ts` (`.cjs`/`.cts` are not supported).

```ts
const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
    tsconfigPath: 'tsconfig.build.json',
  },
}
```

- `typescript.ignoreBuildErrors`: completely skips the production-build type-checking step, not just suppresses errors. If disabled, run type checks elsewhere in the deploy pipeline. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- `typescript.tsconfigPath`: path to a custom `tsconfig` used for `next dev`, `next build`, and `next typegen`. IDEs still usually read `tsconfig.json` for diagnostics; restart the dev server after editing the configured file because only `tsconfig.json` is watched. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- Next.js uses the project-local `tsc` CLI by default; set `experimental.useTypeScriptCli: false` to use the JavaScript compiler API instead (not available with TypeScript 7). ([useTypeScriptCli](https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli))
- TypeScript 7 support: install `typescript@^7`; no extra config is needed because Next.js uses the CLI by default. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- `next-env.d.ts` is auto-generated and managed by Next.js; add it to `.gitignore` and do not edit it manually. It must be in the `tsconfig.json` `include` array. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- Node.js native TypeScript resolver: Next.js detects `process.features.typescript` (Node v22.10.0+). With it enabled, `next.config.ts` can use native ESM including top-level `await` and dynamic `import()`. In CommonJS projects, prefer `next.config.mts` to avoid Node reparsing the file. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- Statically typed links: enable `typedRoutes: true` (not under `experimental`) and ensure `.next/types/**/*.ts` is included in `tsconfig.json`. Works for `next/link` in both routers and for `next/navigation` methods (`push`, `replace`, `prefetch`) in the App Router. Cast non-literal hrefs with `as Route`. ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))
- `experimental.typedEnv`: generates `.next/types` for environment-variable IntelliSense; types reflect variables loaded at dev runtime (excludes `.env.production*` unless you run `next dev` with `NODE_ENV=production`). ([typescript](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript))

### `eslint`

**Removed in Next.js 16.** `next lint` is removed and the `eslint` option in `next.config.*` is no longer needed; use the ESLint CLI directly.

`eslint-config-next` provides:
- Base config `eslint-config-next` with Next.js, React, and React Hooks rules (supports JS and TS).
- `eslint-config-next/core-web-vitals` upgrades rules that affect Core Web Vitals from warnings to errors (recommended; used by `create-next-app` by default).
- `eslint-config-next/typescript` adds TypeScript-specific rules from `typescript-eslint` (use alongside base or core-web-vitals).

Setup with flat config (`eslint.config.mjs`): import `eslint-config-next/core-web-vitals` (and optionally `eslint-config-next/typescript` or `eslint-config-prettier/flat`), spread into `defineConfig`, and add `globalIgnores` for `.next/**`, `out/**`, `build/**`, `next-env.d.ts`. ([eslint](https://nextjs.org/docs/app/api-reference/config/eslint))

- Use `@next/eslint-plugin-next` directly when you already have conflicting plugins (`react`, `react-hooks`, `jsx-a11y`, `import`), custom `parserOptions`/Babel config, or custom `eslint-plugin-import` resolvers. Configure with `plugins: { '@next/next': nextPlugin }` and `rules: { ...nextPlugin.configs.recommended.rules }`. ([eslint](https://nextjs.org/docs/app/api-reference/config/eslint))
- `settings.next.rootDir` tells `@next/eslint-plugin-next` where the Next.js app lives in a monorepo; can be a path, glob, or array. ([eslint](https://nextjs.org/docs/app/api-reference/config/eslint))
- A codemod is available to migrate from `next lint` to the ESLint CLI. ([eslint](https://nextjs.org/docs/app/api-reference/config/eslint))

### `next.config` file form
The config is a regular Node module (not JSON, not parsed by Webpack/Babel). Supported extensions: `.js`, `.mjs`, `.ts`. **`.cjs` and `.cts` are NOT supported.** Function form `(phase, { defaultConfig })`; async since 12.1.0; import phases from `next/constants`. Unit-test `headers`/`redirects`/`rewrites` via `next/experimental/testing/server`'s `unstable_getResponseFromNextConfig` (note: it ignores Proxy and filesystem routes, so results may differ from production). ([next.config index](https://nextjs.org/docs/app/api-reference/config/next-config-js))

## Common options

|| Option | Purpose |
||---|---|
|| `output: 'standalone'` | Minimal server output for Docker/Node. |
|| `output: 'export'` | Static export (limited feature support). |
|| `images.remotePatterns` | Allowed remote image hostnames. |
|| `headers` / `redirects` / `rewrites` | Static routing rules. |
|| `pageExtensions` | Custom page/proxy/route extensions; include `.md` / `.mdx` when using `@next/mdx`. |
|| `logging` | Dev-server logging behavior. |
|| `agentRules` | Set to `false` to opt out of auto-generated `AGENTS.md`. |
|| `serverComponentsHmrCache` | Enable/disable server-component HMR caching for faster local reloads. |
|| `useOffline` | Experimental connectivity-drop retry for navigations/Server Actions. |
|| `useTypeScriptCli` | Run project-local `tsc` during `next build` (default; supports TS 7). |
|| `webVitalsAttribution` | Per-metric Web Vitals attribution debug info. |
|| `webpack` | Custom webpack config (semver-exempt). |
|| `optimizePackageImports` | Webpack-only barrel-package optimization. |
|| `preloadEntriesOnStart` | Disable to reduce server-start memory. |
|| `webpackMemoryOptimizations` | Reduce Webpack memory usage. |
|| `turbopackMemoryEviction` | Memory eviction for Turbopack. |

## Memory & build optimization

- `experimental.webpackMemoryOptimizations: true` (v15.0.0+) reduces max memory usage; may increase compile time.
- `next build --experimental-debug-memory-usage` (v14.2.0+) prints memory usage/GC stats and can take heap snapshots. Incompatible with Webpack build workers.
- Record heap profile: `node --heap-prof node_modules/next/dist/bin/next build` produces `.heapprofile`; load in Chrome DevTools Memory tab.
- Webpack build worker is auto-enabled for apps without custom webpack config from v14.1.0; set `experimental.webpackBuildWorker: true` to opt in on older versions.
- `experimental.preloadEntriesOnStart: false` disables preloading JS modules into memory on server start, reducing initial footprint.

## Package bundling / `optimizePackageImports`

- Avoid broad barrel files; import directly from specific files for icon/utility libraries.
- `optimizePackageImports` is only needed for Webpack; Turbopack analyzes and optimizes imports automatically.
- Magic comments for dynamic imports: `/* webpackIgnore: true */`, `/* turbopackIgnore: true */`, `/* turbopackOptional: true */` work with `import()`, `require()`, `require.resolve()`, `new Worker()`. `webpackOptional` is not supported.

## Proxy file convention (`proxy.ts`) — config & API surface

Replaces `middleware.ts`, deprecated in Next.js 16 (codemod: `npx @next/codemod@canary middleware-to-proxy .`). Runs server-side before a request completes and before routes render (auth, logging, redirects). Runtime & self-hosting notes: see deployment-and-production.md.

- **Location**: project root or `src/`, same level as `pages`/`app`.
- **Custom `pageExtensions`**: if customized (e.g. `.page.ts`), name the file `proxy.page.ts` / `proxy.page.js`.
- **Exports**: a single function as default or named `proxy`. Multiple proxy exports from one file are not supported. Optional `config` export carries `matcher`.

### Matcher
- Values must be **constants** (statically analyzed at build time); dynamic values are ignored.
- Backward compat: `/public` is treated as `/public/index`, so `/public/:path` matches.
- **`_next/data` exception**: even when excluded by a negative matcher, Proxy still runs for `_next/data` routes (intentional — prevents forgetting to protect the data route).

### Params & response

- `request: NextRequest`, `event: NextFetchEvent`. `event.waitUntil(promise)` extends Proxy lifetime so background work finishes after the response is sent. `NextProxy` type infers both.
- `NextResponse` can `redirect`, `rewrite`, set request headers (v13.0.0+), set response cookies, set response headers.
- Produce a response: `rewrite` to a Page/Route Handler, or return `NextResponse`/`Response` directly (v13.1.0+; `Response.redirect` also works).
- Cookies: `request.cookies` → `get`, `getAll`, `set`, `delete`, `has`, `clear`; `response.cookies` → `get`, `getAll`, `set`, `delete`.
- `NextRequest` details: `cookies.get(name)` returns `undefined` when missing and the **first** match when several cookies share a name; `cookies.getAll(name)` returns every value for that name (no arg → all cookies); `cookies.delete(name)` returns `true`/`false` depending on whether anything was deleted; `cookies.clear()` removes all request cookies. `request.nextUrl` extends the Web `URL` API — in the **App Router** only `basePath`, `buildId`, `pathname`, and `searchParams` are available; the i18n properties (`locale`, `locales`, `defaultLocale`, `domainLocale`) are **Pages Router only**. `request.ip` and `request.geo` were **removed in v15.0.0** — read the equivalent values from platform headers instead. ([NextRequest](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/next-request.mdx))
- Set request headers via `NextResponse.next({ request: { headers } })` (forwarded **upstream** to the page/route/Server Action, not exposed to the client). Use caution even here: forwarded headers may reach external services, so forward only an allow-list of known-safe headers.
- `NextResponse.next({ headers })` instead sends headers from Proxy **to the client**. The docs call this **not good practice — avoid it**: setting response headers such as `Content-Type` can override framework expectations (e.g. the `Content-Type` Server Actions rely on), causing failed submissions or broken streaming responses. ([next-response](https://nextjs.org/docs/app/api-reference/functions/next-response))
- RSC requests: Next.js strips internal Flight headers (`rsc`, `next-router-state-tree`, `next-router-prefetch`) from `request` in Proxy; `NextResponse.rewrite()` auto-propagates RSC headers (manual `fetch()` rewrites must forward them).
- CORS: set CORS headers in Proxy for simple and preflighted requests. Avoid large headers (HTTP 431 risk).

### Advanced flags (`next.config.js`)

- `skipTrailingSlashRedirect: true` (v13.1+) — disables Next.js trailing-slash redirects so Proxy can handle them per-path.
- `skipProxyUrlNormalize: true` (v13.1+) — disables URL normalization so direct visits and client transitions match; also helps custom `fetch()` rewrites receive RSC headers.

## Removed / renamed v15 → v16

- `experimental.ppr` removed; PPR is default under `cacheComponents`.
- `experimental.useCache` / `experimental.dynamicIO` removed; use `cacheComponents`.
- `unstable_rootParams` removed; use `next/root-params`.
- `runtime` config edge usage deprecated with Cache Components.
- `publicRuntimeConfig` / `serverRuntimeConfig` removed; use env vars.

## Source URLs

- `next.config.js` overview: https://nextjs.org/docs/app/api-reference/config/next-config-js
- `cacheComponents`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `turbopack`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack
- `serverActions`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `redirects`: https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects
- `rewrites`: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites
- `images`: https://nextjs.org/docs/app/api-reference/config/next-config-js/images
- `partialPrefetching`: https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching
- `logging`: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- `useOffline`: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- `useTypeScriptCli`: https://nextjs.org/docs/app/api-reference/config/next-config-js/useTypeScriptCli
- `webVitalsAttribution`: https://nextjs.org/docs/app/api-reference/config/next-config-js/webVitalsAttribution
- `webpack`: https://nextjs.org/docs/app/api-reference/config/next-config-js/webpack
- `typescript`: https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript
- `eslint`: https://nextjs.org/docs/app/api-reference/config/eslint
- `serverComponentsHmrCache`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverComponentsHmrCache
- Version 16 upgrade guide: https://nextjs.org/docs/app/guides/upgrading/version-16
- MDX: https://nextjs.org/docs/app/guides/mdx
- `mdx-components.tsx` convention: https://nextjs.org/docs/app/api-reference/file-conventions/mdx-components
- Proxy file convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Middleware (deprecated, renamed to Proxy): https://nextjs.org/docs/app/api-reference/file-conventions/middleware
- `serverExternalPackages`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverExternalPackages
- `transpilePackages`: https://nextjs.org/docs/app/api-reference/config/next-config-js/transpilePackages
- `taint`: https://nextjs.org/docs/app/api-reference/config/next-config-js/taint
- `staleTimes`: https://nextjs.org/docs/app/api-reference/config/next-config-js/staleTimes
- `reactStrictMode`: https://nextjs.org/docs/app/api-reference/config/next-config-js/reactStrictMode
- `typescript`: https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript
- `typedRoutes`: https://nextjs.org/docs/app/api-reference/config/next-config-js/typedRoutes
- `trailingSlash`: https://nextjs.org/docs/app/api-reference/config/next-config-js/trailingSlash
- `urlImports`: https://nextjs.org/docs/app/api-reference/config/next-config-js/urlImports
- `useLightningcss`: https://nextjs.org/docs/app/api-reference/config/next-config-js/useLightningcss
- `reactMaxHeadersLength`: https://nextjs.org/docs/app/api-reference/config/next-config-js/reactMaxHeadersLength
- `sassOptions`: https://nextjs.org/docs/app/api-reference/config/next-config-js/sassOptions
- `staticGeneration`: https://nextjs.org/docs/app/api-reference/config/next-config-js/staticGeneration
- `supportsImmutableAssets`: https://nextjs.org/docs/app/api-reference/config/next-config-js/supportsImmutableAssets
- `turbopackFileSystemCache`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackFileSystemCache
- `turbopackMemoryEviction`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackMemoryEviction
- `turbopackLocalPostcssConfig`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackLocalPostcssConfig
- `turbopackRustReactCompiler`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackRustReactCompiler
- `turbopackChunking`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackChunking
- `turbopackIgnoreIssue`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackIgnoreIssue
- `redirects`: https://nextjs.org/docs/app/api-reference/config/next-config-js/redirects
- `rewrites`: https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites
- Adapter immutable-static-assets: https://nextjs.org/docs/app/api-reference/adapters/immutable-static-assets
- `optimizePackageImports`: https://nextjs.org/docs/app/api-reference/config/next-config-js/optimizePackageImports
- `preloadEntriesOnStart`: https://nextjs.org/docs/app/api-reference/config/next-config-js/onDemandEntries
- `webpackMemoryOptimizations`: https://nextjs.org/docs/app/api-reference/config/next-config-js/webpackMemoryOptimizations
- `turbopackMemoryEviction`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackMemoryEviction
- `agentRules`: https://nextjs.org/docs/app/api-reference/config/next-config-js/agentRules
- `serverActions`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `logging`: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- `reactCompiler`: https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler
- `htmlLimitedBots`: https://nextjs.org/docs/app/api-reference/config/next-config-js/htmlLimitedBots
- `inlineCss`: https://nextjs.org/docs/app/api-reference/config/next-config-js/inlineCss
- `instrumentationClientInject`: https://nextjs.org/docs/app/api-reference/config/next-config-js/instrumentationClientInject
- `prefetchInlining`: https://nextjs.org/docs/app/api-reference/config/next-config-js/prefetchInlining
- `outputHashSalt`: https://nextjs.org/docs/app/api-reference/config/next-config-js/outputHashSalt
- `pageExtensions`: https://nextjs.org/docs/app/api-reference/config/next-config-js/pageExtensions
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Multi-tenant: https://nextjs.org/docs/app/guides/multi-tenant
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling

## Canary API reference additions (ingest 2026-08-31, config batch)

**`next.config.js` options (`03-api-reference/05-config/01-next-config-js`)**
- `next.config.*` extensions: only `.js`, `.mjs`, `.ts` supported; `.cjs` and `.cts` are NOT supported. Async config supported since 12.1.0. Unit-test `headers`/`redirects`/`rewrites` with `next/experimental/testing/server`'s `unstable_getResponseFromNextConfig`; it ignores Proxy and filesystem routes, so production behavior may differ. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/index.mdx)
- `htmlLimitedBots`: regex of user agents that receive blocking metadata instead of streaming metadata; overrides default list; `/.*/` disables streaming metadata. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/htmlLimitedBots.mdx)
- `inlineCss` (experimental): inlines CSS into `<head>` as `<style>` tags; prod-only, global, no per-page config; best for first-time visitors / atomic CSS. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/inlineCss.mdx)
- `instrumentationClientInject` (v16.3.0): client modules imported before `instrumentation-client` and ahead of hydration; intended for config plugins; may export `onRouterTransitionStart`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/instrumentationClientInject.mdx)
- `logging`: dev-only knobs including `fetches.fullUrl`, `fetches.hmrRefreshes`, `serverFunctions`, `incomingRequests`, `browserToTerminal`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/logging.mdx)
- `outputHashSalt` (v16.3.0): salt mixed into content-addressed filenames; concatenates with `NEXT_HASH_SALT` env var. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/outputHashSalt.mdx)
- `pageExtensions`: App Router default `.tsx`, `.ts`, `.jsx`, `.js`; extend for `.md`/`.mdx`. Pages Router custom extensions also rename `proxy`, `instrumentation`, `_app`, `_document`, `pages/api` files. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/pageExtensions.mdx)
- `partialPrefetching`: requires `cacheComponents`; default `<Link>` fetches App Shell; per-link `prefetch={true}` resolves URL-specific content; per-segment `prefetch` export overrides app default. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/partialPrefetching.mdx)
- `prefetchInlining` (experimental, default `true` since 16.3.0): bundles small prefetch segment responses; tune with `{ maxSize, maxBundleSize }` (gzip bytes). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/prefetchInlining.mdx)
- `proxyClientMaxBodySize` (experimental, default 10MB): per-request body buffer limit when Proxy is used; excess is truncated with a warning, request continues. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/proxyClientMaxBodySize.mdx)
- `cacheHandler` (formerly `incrementalCacheHandlerPath`): server ISR/route/image cache; methods `get`, `set`, `revalidateTag`, `resetRequestCache`; `ctx.kind` includes `'IMAGE'` for optimized images when `images.customCacheHandler: true`. Not for `'use cache'` (that's `cacheHandlers`). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/incrementalCacheHandlerPath.mdx)
- `headers`: evaluated before filesystem; duplicate keys last-wins; `has`/`missing` support header/cookie/host/query; immutable-asset `Cache-Control` cannot be overridden. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/headers.mdx)
- `output`: standalone output does not copy `public/` or `.next/static`; tracing uses `@vercel/nft`; `outputFileTracingIncludes`/`Excludes` keys are picomatch route globs, values are project-root-relative globs. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/output.mdx)
- `images.loader: 'custom'` requires a root-relative `loaderFile`; in App Router the loader must be a Client Component. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/images.mdx)
- `useOffline` (v16.x.0): offline connectivity detection and automatic retry of navigations/prefetches/Server Actions; polls with 200 ms HEAD requests, stepped backoff capped at 3 s, never gives up; exposes `useOffline` hook from `next/offline`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/useOffline.mdx)
- `useTypeScriptCli`: project-local `tsc` CLI is the default type checker, enabling TypeScript 6/7; set to `false` to use the JS compiler API (unavailable with TS 7). `typescript.tsconfigPath` selects the project; `typescript.ignoreBuildErrors` skips it. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/useTypeScriptCli.mdx)
- `webVitalsAttribution`: array of metric names (`['CLS', 'LCP']`, etc.) to enable per-metric Web Vitals attribution for debugging; disabled by default. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/webVitalsAttribution.mdx)
- `webpack`: custom webpack function receives `{ buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }`; runs three times (client + two server runtimes); must return modified config; semver-exempt. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/01-next-config-js/webpack.mdx)
- TypeScript config (`02-typescript`): auto-installs TS deps and scaffolds `tsconfig.json` when renaming to `.ts`/`.tsx`; TS 7 support via CLI default; `next.config.ts` typed config; `typescript.tsconfigPath` / `ignoreBuildErrors`; `next-env.d.ts` is managed; Node native TS resolver on Node v22.10.0+; `typedRoutes` and `experimental.typedEnv`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/02-typescript.mdx)
- ESLint config (`03-eslint`): `next lint` and the `eslint` next.config option removed in v16; use ESLint CLI flat config with `eslint-config-next/core-web-vitals`, `eslint-config-next/typescript`, optional `eslint-config-prettier/flat`; `@next/eslint-plugin-next` direct for conflicting setups. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/05-config/03-eslint.mdx)

<!-- CANARY-API-REFERENCE-2026-09-01 -->
### Canary API reference additions (ingest 2026-09-01, config batch)

No new top-level options this batch beyond the additions already captured above.

<!-- CANARY-API-REFERENCE-2026-08-31 -->
### Canary API reference additions (ingest 2026-08-31)

**Route Segment Config (`03-api-reference/03-file-conventions/02-route-segment-config`)**
- Supported exports: `dynamicParams` (boolean, default `true`; not available when Cache Components is enabled), `runtime` (`'nodejs'` default, `'edge'` deprecated), `preferredRegion` (deprecated), `maxDuration` (seconds, platform-dependent default).
- As of v16.0.0, `dynamic`, `dynamicParams`, `revalidate`, and `fetchCache` are removed when Cache Components is enabled. `export const experimental_ppr = true` was also removed; a codemod is available.
- `export const runtime = "experimental-edge"` was deprecated as of v15.0.0-RC; use `edge` or remove the export. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/index.mdx)
- `dynamicParams`: `true` (default) means dynamic route segments not in `generateStaticParams` are generated at request time; `false` means they return 404. Not available when Cache Components is enabled. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/dynamicParams.mdx)
- `instant`: only works when `cacheComponents` is enabled; cannot be used in Client Components. Accepts `true`, `false`, or `{ level: 'warning' }`. Default framework validation (`validationLevel: 'warning'`) validates every Page and Default segment in development. Set `validationLevel: 'manual-warning'` to validate only segments that explicitly export `instant`. A `false` value higher in the tree takes precedence over deeper `true` values for the static-shell check. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/instant.mdx)
- `prefetch`: only works when `cacheComponents` is enabled; cannot be used in Client Components. Values are `'auto'` (default, omit), `'partial'`, or `'force-disabled'`. Set on the destination segment, not the link. `'partial'` opts the segment into Partial Prefetching without the global `partialPrefetching` flag; `'force-disabled'` never prefetches segment data. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/prefetch.mdx)
- `maxDuration`: maximum execution time in seconds for server-side logic in a route segment; also changes the default timeout of all Server Actions used on the page. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/maxDuration.mdx)
- `runtime`: `'nodejs'` (default) or `'edge'` (deprecated). Edge Runtime is deprecated; remove the `runtime` export. Cannot be used in Proxy. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/runtime.mdx)
- `preferredRegion`: deprecated. Previously passed region values to the deployment platform; remove the export. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/preferredRegion.mdx)

**File conventions (`03-api-reference/03-file-conventions`)**
- `instrumentation-client.js|ts`: runs before the app becomes interactive; executes after HTML document load but before React hydration. Only synchronous top-level code is guaranteed before hydration; async work (`Promise`, dynamic `import()`, top-level `await`) is fire-and-forget and may resolve after hydration. Export `onRouterTransitionStart(url, navigationType)` to observe App Router navigation starts; enable `experimental.instrumentationClientRouterTransitionEvents` to receive a third `event` argument (`id`, `timestamp`, `fromRoutes`, `prefetchIntent`). Dev warns if initialization exceeds 16ms. Statically import and apply polyfills synchronously after feature detection; conditional/dynamic imports may be too late. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/instrumentation-client.mdx)
- `default.js`: parallel-route fallback when a slot has no matching active state on hard navigation. For named slots, missing `default.js` errors; for the implicit `children` slot, missing `default.js` returns a 404. Can call `notFound()` to preserve old behavior. Receives `params` as a promise. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/default.mdx)
- `dynamic-routes`: dynamic segments `[folderName]`, catch-all `[...folderName]`, optional catch-all `[[...folderName]]`. `params` and `searchParams` are promises in v15+ and must be awaited. With Cache Components and without `generateStaticParams`, param access must be wrapped in `<Suspense>`; in layouts, avoid awaiting `params` at the top level. Type helpers `PageProps<'/route'>`, `LayoutProps<'/route'>`, and `RouteContext<'/route'>` generate types. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/dynamic-routes.mdx)
- `error.js` / `error.tsx`: see `references/error-handling.md` for details. `retry` stable since v16.3.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/error.mdx)
- `forbidden.js` / `forbidden.tsx`: renders UI when `forbidden()` is invoked; returns 403. No props. Introduced v15.1.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/forbidden.mdx)

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — configuration additions (ingest 2026-08-30)

**Environment variables (`environment-variables`)**
- Multiline values are supported in `.env*` files (line breaks or `\n` inside double quotes). (Source: https://nextjs.org/docs/app/guides/environment-variables)
- With a `/src` folder, Next.js loads `.env` files ONLY from the parent folder, not from `/src`. (Source: above)
- A literal `$` in a value must be escaped as `\$`. (Source: above)
- After build, the app no longer responds to changes in env vars (e.g. promoting a slug/Docker image across environments) — all `NEXT_PUBLIC_*` are inlined at build time. (Source: above)
- `.env.test` should be committed; `.env.test.local` should NOT (`.env*.local` is gitignored). (Source: above)
- Allowed `NODE_ENV` values: `production`, `development`, `test`. (Source: above)

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary architecture additions — supported browsers and polyfills (ingest 2026-09-02)

Sourced from `docs/03-architecture/supported-browsers.mdx`. Browser support is a build/runtime concern; merged into the configuration reference.

**Supported browsers**
- Next.js supports modern browsers with zero configuration: Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+. (Source: https://nextjs.org/docs/architecture/supported-browsers)
- Default Browserslist: `["chrome 111", "edge 111", "firefox 111", "safari 16.4"]`. (Source: above)
- Built-in polyfills are injected only for browsers that need them: `fetch()`, `URL`, `Object.assign()`. If dependencies include these polyfills, they are deduplicated/removed from the production build. (Source: above)
- **App Router polyfills**: import them into `instrumentation-client.js|ts`. Only synchronous top-level code is guaranteed before hydration; conditional/dynamic imports may be too late. (Source: above)
- **Pages Router polyfills**: add a top-level import in `pages/_app` or the specific component. (Source: above)
- Conditionally load polyfills only where needed (e.g. test `'structuredClone' in globalThis` before importing a shim). (Source: above)
- **JavaScript features supported out of the box**: async/await (ES2017), Object Rest/Spread (ES2018), dynamic `import()` (ES2020), optional chaining, nullish coalescing, class fields/static properties (ES2022), and more. (Source: above)

### Canary Pages Router additions — API reference: configuration (ingest 2026-09-02)

Sourced from `docs/02-pages/04-api-reference/04-config/01-next-config-js/bundlePagesRouterDependencies.mdx` and the Pages Router `next-config-js` pages.

**`bundlePagesRouterDependencies`**
- When `bundlePagesRouterDependencies: true` (stable since v15.0.0, formerly `bundlePagesExternals`), Next.js bundles all dependencies for the Pages Router, matching the automatic dependency bundling in App Router. (Source: https://nextjs.org/docs/pages/api-reference/config/next-config-js/bundlePagesRouterDependencies)
- This enables deployment on platforms that do not install `node_modules` (e.g. Netlify On-Demand Builders, Cloudflare Pages). (Source: above)
- Opt-out specific packages with `serverExternalPackages`; those remain external even when this option is enabled, and are resolved with native Node.js `require`. (Source: above)
- Next.js auto-externalizes a built-in list of popular packages (see [`server-external-packages.jsonc`](https://github.com/vercel/next.js/blob/canary/packages/next/src/lib/server-external-packages.jsonc)); they remain external even when `bundlePagesRouterDependencies` is enabled. (Source: https://github.com/vercel/next.js/blob/canary/docs/02-pages/04-api-reference/04-config/01-next-config-js/serverExternalPackages.mdx)

**`assetPrefix` / `basePath` / `crossOrigin` (Pages Router notes)**
- `assetPrefix` does **not** affect `/_next/data/` (Pages Router client data requests). (Source: https://nextjs.org/docs/pages/api-reference/config/next-config-js/assetPrefix)
- `basePath` is auto-applied to `next/link` and `next/router`; `next/image` `src` needs the prefix added manually. (Source: https://nextjs.org/docs/pages/api-reference/config/next-config-js/basePath)
- `crossOrigin` applies to `next/script` and `next/head` in the Pages Router. (Source: https://nextjs.org/docs/pages/api-reference/config/next-config-js/crossOrigin)

**`compress`, `devIndicators`, `distDir`, `env`, `generateEtags`, `httpAgentOptions`, `onDemandEntries`, `pageExtensions`, `poweredByHeader`, `productionBrowserSourceMaps`, `reactStrictMode`, `trailingSlash`, `transpilePackages`, `urlImports`, `webpack`, etc.**
- These options behave the same in both routers. See the App Router config reference; the Pages Router docs only add router-specific examples. No contradictory semantics found in this batch.
