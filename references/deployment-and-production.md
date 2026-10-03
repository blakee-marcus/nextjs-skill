# Deployment and Production

Reference: https://nextjs.org/docs/app/getting-started/deploying

## Deployment options

|| Option | Feature support |
||---|---|
|| Node.js server | All |
|| Docker container | All |
|| Static export | Limited |
|| Adapters | Varies |

## Platform capabilities

Next.js treats static and dynamic content as a spectrum. A platform needs only a Node.js server to achieve **functional fidelity** (every feature works correctly); the [adapter test suite](/docs/app/api-reference/adapters/testing-adapters) is the contract. **Performance fidelity** (e.g. CDN-latency PPR shells, sub-second ISR propagation) is a spectrum that improves with additional infrastructure such as CDN caching, edge compute, and a shared/remote cache for multi-instance tag coordination.

Infrastructure requirements for full fidelity:
- **Streaming** — required because static and dynamic content are served in a single response; without it, responses are buffered but features still work.
- **Cache coordination** — needed when running multiple instances so `revalidateTag()` / `revalidatePath()` propagate across instances.
- **Cache consistency** — revalidation regenerates both the HTML response and the RSC payload; keep them aligned to avoid inconsistent data during navigation.
- **PPR shell delivery** — for CDN-latency PPR shells, platforms may need bespoke integration to store the static shell separately and resume dynamic rendering correctly.

See the [PPR platform guide](/docs/app/guides/ppr-platform-guide) for the resume protocol:
- Store the static HTML shell and `postponedState` blob atomically.
- Serve the shell immediately on request.
- Resume dynamic portions by sending a `POST` request with the `next-resume: 1` header and the `postponedState` as the body. For adapter-based deployments, pass `requestMeta: { postponed: postponedState }` to the handler directly.
- When a Server Action is combined with a PPR resume, the request body contains the postponed state followed by the action body; the `x-next-resume-state-length` header carries the byte length of the postponed-state prefix.
- Update cached shell + `postponedState` atomically via `requestMeta.onCacheEntryV2`.

## Functional vs performance fidelity

- **Functional fidelity** is binary: the adapter test suite passes or it doesn't. A platform that passes is a fully supported deployment target.
- **Performance fidelity** is a spectrum: PPR static shell from CDN, stale-while-revalidate propagation speed, edge request handling, etc. Platforms differentiate here.

## Node.js server

Ensure `package.json` has:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

Run `npm run build` then `npm run start`.

## Docker

Use `output: 'standalone'` for a minimal production image. See the official `with-docker` example. Docker supports all Next.js features; for local development on macOS/Windows, prefer `next dev` over Docker for better performance.

## OpenTelemetry

Use `@vercel/otel` with an `instrumentation.ts` file at the project root (or `src/` root, next to `app`/`pages`, not inside them). Export a `register()` function that calls `registerOTel({ serviceName: '...' })`. Set `NEXT_OTEL_VERBOSE=1` to emit additional spans. For a manual `NodeSDK` setup, keep the SDK import in a separate `instrumentation.node.ts` file and conditionally import it only when `process.env.NEXT_RUNTIME === 'nodejs'`; `NodeSDK` is not compatible with the Edge runtime.

## Multi-zone routing

Split a domain into separate Next.js apps. Each zone may have its own `assetPrefix` (extra rewrite for assets not needed in Next.js 15+). Route between zones with `rewrites` or Proxy. Links between zones must use a native `<a>` tag (not `<Link>`). For Server Actions across zones, add the user-facing origin to `serverActions.allowedOrigins`; follow wildcard/port rules (`*` one label, `**` one or more labels at start; ports can't be wildcarded).

## Offline support / `useOffline`

Experimental. Enable in `next.config.*` under `experimental.useOffline`. When active, failed navigations, RSC fetches, prefetches, and Server Actions are retried automatically when connectivity returns; direct `fetch()` in Client Components still follows its own retry policies. Use `useOffline()` from `next/offline` in a Client Component to read `{ isOffline, wasOffline }` and give the user connectivity feedback.

## Multi-tenant

For tenants accessed by subdomain, use a Proxy rewrite at the project root to rewrite the tenant subdomain to a route parameter (`/app/[tenant]/...`). For path-based tenants, use a route segment such as `/app/[tenant]/...` directly. Store per-tenant data with a unique identifier, never the tenant slug alone. Cache tenant-aware data with a tenant-aware cache tag or private cache.

## Proxy (`proxy.ts`) runtime & platform support

- Proxy defaults to the **Node.js runtime**. The `runtime` config option is **not available** in Proxy files; setting `runtime` in a Proxy file throws an error.
- **Platform support**: Node.js server ✅ · Docker ✅ · Static export ❌ (Proxy unsupported) · Adapters — platform-specific.
- When self-hosting, configure Proxy per the self-hosting Proxy guide.
- Proxy errors are observable via `onRequestError` (`routeType: 'proxy'`) — see debugging-and-development.md.
- Direction: use Proxy as a last resort; prefer dedicated APIs over heavy Proxy use.

## Static export

```ts
const nextConfig: NextConfig = {
  output: 'export',
}
```

Does not support streaming, Server Actions, Route Handlers that need a request, runtime APIs (`cookies`, `headers`), ISR, Proxy, or dynamic routes without `generateStaticParams`. Useful for SPAs or static hosting (S3, Nginx, Apache, GitHub Pages).

## Adapters

The Deployment Adapter API lets platforms customize build output and deployment. Configure an adapter via `adapterPath` in `next.config.js` or the `NEXT_ADAPTER_PATH` environment variable for zero-config platform usage.

### Adapter interface

An adapter module exports an object implementing `NextAdapter` from `next`:

```typescript
type NextAdapter = {
  name: string
  modifyConfig?: (
    config: NextConfigComplete,
    ctx: { phase: PHASE_TYPE; nextVersion: string; projectDir: string }
  ) => Promise<NextConfigComplete> | NextConfigComplete
  onBuildComplete?: (ctx: {
    routing: {
      beforeMiddleware: Route[]
      middlewareMatchers: Route[]
      beforeFiles: Route[]
      afterFiles: Route[]
      dynamicRoutes: Route[]
      onMatch: Route[]
      fallback: Route[]
      shouldNormalizeNextData: boolean
      rsc: RoutesManifest['rsc']
    }
    outputs: AdapterOutputs
    projectDir: string
    repoRoot: string
    distDir: string
    config: NextConfigComplete
    nextVersion: string
    buildId: string
  }) => Promise<void> | void
}
```

- `modifyConfig` runs whenever `next.config.js` is loaded and can adjust config per phase.
- `onBuildComplete` receives the full build routing and output metadata after `next build` finishes.

### Routing information

`onBuildComplete.routing` exposes processed routing phases:

- `beforeMiddleware`: header/redirect routes applied before middleware.
- `middlewareMatchers`: matcher definitions for deciding when to invoke middleware.
- `beforeFiles`: rewrites checked before filesystem route matching.
- `afterFiles`: rewrites checked after filesystem route matching.
- `dynamicRoutes`: dynamic matchers for `[slug]`, catch-all, etc.
- `onMatch`: routes applied after a match (e.g. immutable static-asset cache headers).
- `fallback`: final fallback rewrites.
- `shouldNormalizeNextData`: whether `/_next/data/<buildId>/...` URLs are normalized during matching.
- `rsc`: RSC routing metadata.

Each route entry includes `sourceRegex` (compiled regex), optional `source`, `destination`, `headers`, `has`/`missing` conditions, `status`, and `priority`.

Platforms can also use [`@next/routing`](https://www.npmjs.com/package/@next/routing) `resolveRoutes()` to reproduce Next.js routing at request time. It returns `middlewareResponded`, `externalRewrite`, `redirect`, `resolvedPathname`, `resolvedQuery`, `invocationTarget`, `resolvedHeaders`, `status`, and `routeMatches`.

### Output types

`onBuildComplete.outputs` contains arrays of build outputs:

- `pages`: Pages Router React pages (`type: 'PAGES'`)
- `pagesApi`: Pages Router API routes (`type: 'PAGES_API'`)
- `appPages`: App Router React pages, including `.rsc` variants (`type: 'APP_PAGE'`)
- `appRoutes`: App Router Route Handlers and metadata routes (`type: 'APP_ROUTE'`)
- `prerenders`: ISR-enabled routes and static prerenders (`type: 'PRERENDER'`)
- `staticFiles`: static assets and auto-statically optimized pages (`type: 'STATIC_FILE'`)
- `middleware`: middleware/proxy function (`type: 'MIDDLEWARE'`)

Common fields for route outputs include `id`, `filePath`, `pathname`, `sourcePage`, `runtime`, `assets`, `assetsHashes`, `wasmAssets`, `config` (`maxDuration`, `preferredRegion` (deprecated), `env` for edge), and `edgeRuntime` (deprecated Edge runtime canonical entry metadata: `modulePath`, `entryKey`, `handlerExport`).

Prerender-specific fields:

- `fallback.filePath` / `fallback.postponedState`: static PPR shell and resume state.
- `fallback.initialHeaders` / `initialStatus` / `initialRevalidate` / `initialExpiration`: cache-seed metadata.
- `pprChain.headers`: resume protocol headers (`{ 'next-resume': '1' }`).
- `routeType`: `route` | `page` | `shell` | `fallback`.
- `response`: `empty` | `initial` | `complete`.
- `compute`: `blocking` | `resuming` | `static`.
- `htmlSize`: byte size of the App Router HTML shell (0 means empty).
- `config.renderingMode`: `STATIC` or `PARTIALLY_STATIC`.
- `config.partialFallback`, `bypassToken`, `allowQuery`, `allowHeader`, `bypassFor`.

When `config.output === 'export'`, only `staticFiles` is populated.

### Runtime integration

The adapter API is build-time. Runtime behavior (streaming, caching, request handling) is implemented by Next.js server entrypoints plus cache interfaces:

- `cacheHandler`: ISR/server cache storage and tag coordination across instances.
- `cacheHandlers`: `'use cache'` directive backends and tag coordination.

When invoking an entrypoint, pass a handler context `ctx`:

- `ctx.waitUntil(promise)`: keep the function alive after response for background work like cache revalidation.
- `requestMeta.onCacheEntryV2`: callback fired when a cache entry is generated or looked up. Persist `APP_PAGE` entries (HTML shell + `postponed` state + headers/status/cacheControl) to shared storage. Return `true` only if the adapter already wrote the response itself; otherwise return `false` to continue the normal response flow. `onCacheEntry` is deprecated.

Node.js entrypoints use `handler(req, res, ctx)`. Useful `requestMeta` fields: `relativeProjectDir`, `hostname`, `revalidate`, `render404`. Edge runtime entrypoints (deprecated) use `handler(request, ctx)` returning a `Response`; for `edgeRuntime` outputs use `globalThis._ENTRIES[output.edgeRuntime.entryKey][output.edgeRuntime.handlerExport]`.

### PPR resume in adapters

For PPR routes, seed the static HTML shell and `postponedState` from `outputs.prerenders[].fallback` at build time. At request time:

1. Serve the cached shell immediately.
2. Resume dynamic portions by sending a `POST` request with the `next-resume: 1` header and `postponedState` as the body; in `next start`-style invocation, pass `requestMeta: { postponed: postponedState }` directly.
3. For Server Actions combined with a PPR resume, the request body contains the postponed state followed by the action body; the `x-next-resume-state-length` header carries the byte length of the postponed-state prefix.
4. Update cached shell + `postponedState` atomically via `requestMeta.onCacheEntryV2`.

Use `pprChain.headers` (`{ 'next-resume': '1' }`) from prerender output to construct the internal resume request.

### Immutable static assets

Adapters can opt into immutable content-addressed assets under `/_next/static/immutable/*`:

- In `modifyConfig`, set `config.supportsImmutableAssets = true` (unless the user set `false`).
- Use `config.outputHashSalt` to rotate hashes if needed.
- In `onBuildComplete`, read `outputs.staticFiles[].immutableHash`. Non-null means the asset must be requestable at `output.pathname` without the `?dpl` query parameter and must never be changed or deleted while active deployments reference it. `immutableHash` is the full content hash; Next.js may truncate the filename hash.
- Non-immutable assets continue to be requested with `?dpl` and scoped per deployment.

### Testing adapters

The adapter test harness validates functional fidelity. Provide three scripts as executable files:

- `NEXT_TEST_DEPLOY_SCRIPT_PATH`: builds and deploys the test app; must exit non-zero on failure, print the deployment URL to stdout, and write `BUILD_ID:`, `DEPLOYMENT_ID:`, and `NEXT_SUPPORTS_IMMUTABLE_ASSETS:` markers to files or stderr.
- `NEXT_TEST_DEPLOY_LOGS_SCRIPT_PATH`: returns logs; output must include the same markers and receives `NEXT_TEST_DIR` and `NEXT_TEST_DEPLOY_URL`.
- `NEXT_TEST_CLEANUP_SCRIPT_PATH`: tears down the deployment; receives `NEXT_TEST_DIR` and `NEXT_TEST_DEPLOY_URL`.

Run with `NEXT_TEST_MODE=deploy`, `NEXT_EXTERNAL_TESTS_FILTERS=test/deploy-tests-manifest.json`, `IS_TURBOPACK_TEST=1`, `NEXT_TEST_JOB=1`, etc.

### Verified and community adapters

Verified adapters (Vercel, Bun) run the Next.js compatibility test suite. Cloudflare and Netlify are building verified adapters on the Adapter API. Custom integrations are also available: Appwrite, AWS Amplify, Cloudflare, Deno Deploy, Firebase App Hosting, Netlify.

## CDN compatibility

Many CDNs have primitives for deeper integration (edge compute, key-value storage, blob storage), but end-to-end PPR resume support is still emerging and may require bespoke platform work. See [Deploying to Platforms](/docs/app/guides/deploying-to-platforms) for the full CDN compatibility table and [CDN Caching](/docs/app/guides/cdn-caching) for caching behavior details.

## CI build caching

Next.js caches build outputs in `.next/cache` between CI runs. To avoid rebuilding unchanged code, persist the `.next/cache` directory in your CI workflow (for example, via your CI provider's cache action). Do not cache the full `.next` directory, because it contains build outputs that should be regenerated.

## Self-hosting considerations

Self-hosting with `next start` or Docker requires a few operational choices to keep caching, Server Functions, and rolling deployments consistent.

### Reverse proxy

Use a reverse proxy (e.g. nginx) in front of the Next.js server to handle malformed requests, slow-connection attacks, payload limits, rate limiting, etc. This offloads request validation so the Next.js server can focus on rendering.

### Environment variables

Environment variables are server-only by default. To expose one to the browser, prefix it with `NEXT_PUBLIC_` (it is inlined into the client bundle at build time). For runtime server values in the App Router, read them inside a dynamically rendered Server Component or after calling `connection()`.

### Caching and ISR

Next.js caches ISR/data on the local filesystem and in memory (default 50 MB). In multi-instance or serverless deployments the cache is not shared, so configure a custom cache handler and disable in-memory caching when needed:

```js
module.exports = {
  cacheHandler: require.resolve('./cache-handler.js'),
  cacheMaxMemorySize: 0,
}
```

For Cache Components, use `use cache: remote` or a custom `cacheHandlers` config backed by external storage (Redis, S3, etc.). Coordinate tag invalidation across instances by implementing `refreshTags()` in the cache handler so instances periodically sync tag state from shared storage before a new request.

### Multi-instance Server Functions

- All instances must use the same `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`. It must be a base64-encoded value with a valid AES key length (16, 24, or 32 bytes). Next.js generates 32-byte keys by default.
- Configure a `deploymentId` to protect against version skew during rolling deployments. When a mismatch is detected, Next.js triggers a hard navigation instead of a client-side navigation so clients load assets from a consistent deployment.

### Streaming and PPR

The App Router supports streaming self-hosted. Ensure your reverse proxy, load balancer, and CDN pass through chunked responses without buffering (set `X-Accel-Buffering: no` for nginx). Partial Prerendering requires streaming; without it, the static shell and dynamic content arrive together and PPR's time-to-first-byte advantage is lost.

### `after()`

[`after()`](/docs/app/api-reference/functions/after) is fully supported when self-hosting. On shutdown, send `SIGINT` or `SIGTERM` and allow a 10–30 second drain period so in-flight requests and pending `after()` callbacks complete.

### Static export limitations

Static export does not support streaming, Server Actions, Route Handlers that need a request, runtime APIs (`cookies`, `headers`), ISR, Proxy, or dynamic routes without `generateStaticParams`.

## Source URLs

- Deploying: https://nextjs.org/docs/app/getting-started/deploying
- Self-hosting: https://nextjs.org/docs/app/guides/self-hosting
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- Adapters: https://nextjs.org/docs/app/api-reference/adapters
- Docker examples: https://github.com/vercel/next.js/tree/canary/examples/with-docker
- Deploying to platforms: https://nextjs.org/docs/app/guides/deploying-to-platforms
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- CI build caching: https://nextjs.org/docs/app/guides/ci-build-caching
- How revalidation works: https://nextjs.org/docs/app/guides/how-revalidation-works
- CDN caching: https://nextjs.org/docs/app/guides/cdn-caching
- Self-hosting: https://nextjs.org/docs/app/guides/self-hosting
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- Progressive Web Apps: https://nextjs.org/docs/app/guides/progressive-web-apps
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- `manifest` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Multi-tenant: https://nextjs.org/docs/app/guides/multi-tenant
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- Production checklist: https://nextjs.org/docs/app/guides/production-checklist
- Redirecting: https://nextjs.org/docs/app/guides/redirecting
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Local development: https://nextjs.org/docs/app/guides/local-development
- Proxy self-hosting: https://nextjs.org/docs/app/guides/self-hosting#proxy
- `instrumentation.ts`: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
- Adapter configuration: https://nextjs.org/docs/app/api-reference/adapters/configuration
- Creating an adapter: https://nextjs.org/docs/app/api-reference/adapters/creating-an-adapter
- Adapter API reference: https://nextjs.org/docs/app/api-reference/adapters/api-reference
- Testing adapters: https://nextjs.org/docs/app/api-reference/adapters/testing-adapters
- Routing with `@next/routing`: https://nextjs.org/docs/app/api-reference/adapters/routing-with-next-routing
- Implementing PPR in an adapter: https://nextjs.org/docs/app/api-reference/adapters/implementing-ppr-in-an-adapter
- Adapter runtime integration: https://nextjs.org/docs/app/api-reference/adapters/runtime-integration
- Invoking entrypoints: https://nextjs.org/docs/app/api-reference/adapters/invoking-entrypoints
- Adapter output types: https://nextjs.org/docs/app/api-reference/adapters/output-types
- Adapter routing information: https://nextjs.org/docs/app/api-reference/adapters/routing-information
- Adapter use cases: https://nextjs.org/docs/app/api-reference/adapters/use-cases
- Immutable static assets: https://nextjs.org/docs/app/api-reference/adapters/immutable-static-assets
- `supportsImmutableAssets` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/supportsImmutableAssets

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — build/deploy additions (ingest 2026-08-30)

**Building (`building`)**
- Do NOT deploy builds produced with `--debug-prerender` — they skip production optimizations. (Source: https://nextjs.org/docs/app/guides/building)
- `generateStaticParams` must return at least one param; an empty array causes a build error. (Source: above)
- `next build` prints a route table with symbols: `○` static, `◐` Partial Prerender (Cache Components), `●` server-rendered, etc. `◐` rows appear only for real uncached I/O; a synchronous in-memory value prerenders as `○`. (Source: above)

**Custom server (`custom-server`)**
- Use a custom server ONLY when the integrated Next.js router cannot meet requirements — it opts you out of automatic optimizations. (Source: https://nextjs.org/docs/app/guides/custom-server)
- In `standalone` output mode, custom server files are NOT traced (it outputs a minimal `server.js`). (Source: above)

**Deploying to platforms (`deploying-to-platforms`)**
- A single `next start` process handles every feature correctly: Server Components, ISR, PPR, Cache Components, Server Actions. (Source: https://nextjs.org/docs/app/guides/deploying-to-platforms)
