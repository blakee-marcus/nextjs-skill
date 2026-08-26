# Routing and Navigation

Reference: https://nextjs.org/docs/app/getting-started/linking-and-navigating

## File-system routing

- Folders in `app/` are route segments.
- `page.tsx` / `route.ts` makes a segment public.
- Layouts nest automatically and preserve state across navigation.

## Dynamic segments

- `[slug]` — single param
- `[...slug]` — catch-all
- `[[...slug]]` — optional catch-all
- `params` is a promise in v15+; await it.

## Route groups and private folders

- `(group)` — URL-less organization; can share layouts or opt routes into/out of layouts.
- `_folder` — not routable; safe for co-located components/lib.

## Parallel and intercepting routes

- `@slot` — named slot rendered by parent layout.
- `(.)folder` — intercept same level.
- `(..)folder` — intercept parent.
- `(..)(..)folder` — intercept two levels.
- `(...)folder` — intercept from root.

## Navigation APIs

### `Link`

```tsx
import Link from 'next/link'

<Link href="/blog/post-1">Read</Link>
```

- Prefetches when entering viewport by default.
- Use `prefetch={true}` for per-link URL data with Partial Prefetching.
- Use `prefetch={false}` to disable.

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
```

### `redirect` / `permanentRedirect`

Server-side redirects from `next/navigation`:

```tsx
import { redirect } from 'next/navigation'

if (!user) redirect('/login')
```

`redirect()` throws a control-flow exception; code after it does not run.

### `notFound`

```tsx
import { notFound } from 'next/navigation'

if (!post) notFound()
```

Triggers the nearest `not-found.tsx`.

## Route Handlers (`route.ts`)

- Custom request handlers using Web Request/Response APIs.
- Supported methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`.
- `GET` default is dynamic since v15.
- `params` is a promise; await it.
- `NextRequest` from `next/server` extends Web Request with `nextUrl`, cookies helpers.

## Proxy (`proxy.ts`)

- In Next.js 16+, `middleware.ts` is deprecated and renamed to `proxy.ts`.
- Runs before routes are rendered; can rewrite, redirect, set headers/cookies, respond directly.
- Use a `matcher` config to avoid running on every request (including `_next/static`, `public/` assets).
- Prefer `next.config.js` `redirects` for simple redirects.
- Migration codemod: `npx @next/codemod@canary middleware-to-proxy .`

## Source URLs

- Linking and Navigating: https://nextjs.org/docs/app/getting-started/linking-and-navigating
- Dynamic Routes: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes
- Route Groups: https://nextjs.org/docs/app/api-reference/file-conventions/route-groups
- Parallel Routes: https://nextjs.org/docs/app/api-reference/file-conventions/parallel-routes
- Intercepting Routes: https://nextjs.org/docs/app/api-reference/file-conventions/intercepting-routes
- `Link`: https://nextjs.org/docs/app/api-reference/components/link
- `useRouter`: https://nextjs.org/docs/app/api-reference/functions/use-router
- `redirect`: https://nextjs.org/docs/app/api-reference/functions/redirect
- `notFound`: https://nextjs.org/docs/app/api-reference/functions/not-found
- `route` convention: https://nextjs.org/docs/app/api-reference/file-conventions/route
- `proxy` convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Getting Started Proxy: https://nextjs.org/docs/app/getting-started/proxy
