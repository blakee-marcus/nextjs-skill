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

### `use cache`

Default is dynamic/uncached. Opt in at file, component, or function level. Cached functions/components must be async.

```ts
export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM products')
}
```

### `cacheLife`

Controls freshness. Built-in profiles:

| Profile | stale | revalidate | expire |
|---|---|---|---|
| `default` | 5m | 15m | never |
| `seconds` | 30s | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `weeks` | 5m | 1w | 30d |
| `max` | 5m | 30d | 1y |

Custom object form:

```ts
cacheLife({ stale: 3600, revalidate: 7200, expire: 86400 })
```

### `cacheTag`

Tag cached data for on-demand invalidation:

```ts
'use cache'
cacheTag('products')
```

### Revalidation APIs

| API | Where | Behavior | Use case |
|---|---|---|---|
| `revalidateTag(tag, profile?)` | Server Actions, Route Handlers | stale-while-revalidate | background refresh, slight delay OK |
| `updateTag(tag)` | Server Actions only | immediate expiration | read-your-own-writes |
| `revalidatePath(path)` | Server Actions, Route Handlers | invalidate by path | tagging is overkill |
| `refresh()` | Server Actions | refetch current route | state outside cache changed |

### `use cache: private`

Allows runtime APIs (`cookies()`, `headers()`, `searchParams`) inside a cached scope, but stores results **only in browser memory**, not on the server. Use when refactoring to pass runtime values as arguments is impractical.

### `use cache: remote`

Uses a remote cache handler. Requires a network roundtrip; only worthwhile at high hit rates.

### Prerendering with Cache Components

- Static shell is built at build time from cached/predictable content.
- Uncached or runtime data must be wrapped in `Suspense` or behind `connection()` so it streams at request time.
- `Math.random()`, `Date.now()`, `crypto.randomUUID()` require explicit handling; use `connection()` + `Suspense` for unique per-request values.
- `performance.now()` is allowed for telemetry.

## Previous caching model (pre-v16 / no Cache Components)

- `fetch` options: `cache: 'force-cache' | 'no-store'`, `next.revalidate`, `next.tags`.
- `unstable_cache` for wrapping arbitrary functions.
- Route segment config: `export const revalidate = 60`, `export const dynamic = 'force-dynamic'`, etc.
- Do not apply Cache Components APIs to projects still on this model.

## Common mistakes to prevent

- Assuming `fetch` is cached by default.
- Applying v16 Cache Components APIs to a v14/v15 project.
- Using `revalidatePath` everywhere instead of precise `cacheTag` invalidation.
- Putting runtime API reads inside a plain `use cache` scope.
- Clearing `.next` as a diagnosis instead of identifying the caching mismatch.

## Source URLs

- Caching overview: https://nextjs.org/docs/app/getting-started/caching
- Revalidating: https://nextjs.org/docs/app/getting-started/revalidating
- `use cache` directive: https://nextjs.org/docs/app/api-reference/directives/use-cache
- `use cache: private`: https://nextjs.org/docs/app/api-reference/directives/use-cache-private
- `use cache: remote`: https://nextjs.org/docs/app/api-reference/directives/use-cache-remote
- `cacheComponents`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `cacheLife`: https://nextjs.org/docs/app/api-reference/functions/cacheLife
- `cacheTag`: https://nextjs.org/docs/app/api-reference/functions/cacheTag
- `revalidateTag`: https://nextjs.org/docs/app/api-reference/functions/revalidateTag
- `updateTag`: https://nextjs.org/docs/app/api-reference/functions/updateTag
- `revalidatePath`: https://nextjs.org/docs/app/api-reference/functions/revalidatePath
- Previous model: https://nextjs.org/docs/app/guides/caching-without-cache-components
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
