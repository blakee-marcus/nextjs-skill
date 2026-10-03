# Error Handling

Reference: https://nextjs.org/docs/app/getting-started/error-handling

## Expected errors

Model expected errors as return values, not thrown exceptions:

```ts
'use server'

export async function createPost(prevState: unknown, formData: FormData) {
  const title = formData.get('title')
  const res = await fetch('...', { method: 'POST', body: JSON.stringify({ title }) })
  const json = await res.json()
  if (!res.ok) return { message: 'Failed to create post' }
}
```

- Use `useActionState` in Client Components to read the returned `state` and show feedback.
- In Server Components, use the response status to conditionally render an error message or call `redirect()` from `next/navigation`.

## Uncaught exceptions

Use error boundaries to catch unexpected errors during rendering and show fallback UI.

### `error.tsx`

```tsx
'use client'

export default function ErrorPage({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}
```

- Must be a Client Component.
- The `error.tsx` component receives an `error` object (`Error & { digest?: string }`) and a `retry()` function.
- `retry()` re-fetches and re-renders the error boundary's children; if it succeeds the fallback is replaced.
- `reset()` clears the error state and re-renders without re-fetching. Prefer `retry()` unless you specifically need to skip re-fetching.
- In production, errors forwarded from Server Components show a generic message with a `digest` identifier to avoid leaking sensitive details. Match `digest` to server-side logs.
- Errors bubble to the nearest parent error boundary.
- In the component hierarchy, `error.js` wraps `loading.js`, `not-found.js`, `page.js`, and nested `layout.js` files in a React error boundary. It does **not** wrap the `layout.js` or `template.js` above it in the same segment.
- For component-level error recovery that isn't tied to route segments, use `catchError` from `next/error`.
- `global-error.js` handles errors in the root layout/template and must define its own `<html>` and `<body>` tags. It does not inherit app-level theme classes/attributes, so apply your theme inside the component.
- `metadata` and `generateMetadata` exports are not supported in `global-error` because it is a Client Component.

### `catchError`

Component-level error boundaries for wrapping any subtree:

```tsx
'use client'

import { catchError, type ErrorInfo } from 'next/error'

function ErrorFallback(props: { title: string }, { error, retry }: ErrorInfo) {
  return (
    <div>
      <h2>{props.title}</h2>
      <p>{error.message}</p>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}

export default catchError(ErrorFallback)
```

Use the returned wrapper anywhere in a layout or page, passing props to the fallback.

- `catchError` accepts a single `fallback` argument; the fallback receives `(props, errorInfo)` where `props` are the wrapper's props excluding `children`, and `errorInfo` holds `error` (`Error`), `retry` (`() => void`, re-fetches and re-renders inside a Transition, preserving Client Component state outside the boundary), and `reset` (`() => void`, clears error state and re-renders without re-fetching).
- The fallback function must be a Client Component (or live in a `'use client'` module).
- Compared to a custom React error boundary, `catchError` handles `redirect()` and `notFound()` (which throw special errors) seamlessly so they aren't accidentally swallowed, and its error state auto-clears on client navigation to a different route.
- You do **not** need to wrap `error.js` default exports with `catchError` — `error.js` already renders inside a built-in boundary.
- Version: `catchError` became stable in `v16.3.0`; `unstable_catchError` introduced in `v16.2.0`.
- In the App Router, the fallback can also receive server-rendered content passed as a prop; this pattern eagerly renders the fallback on every render, so use it only when data-driven fallback UI is worth the cost.

### `global-error.tsx`

Root-level error UI; must define its own `<html>` and `<body>` tags.

## `notFound`

Call `notFound()` from `next/navigation` to trigger the nearest `not-found.tsx`:

```tsx
import { notFound } from 'next/navigation'
import { getPostBySlug } from '@/lib/posts'

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = getPostBySlug(slug)

  if (!post) notFound()

  return <div>{post.title}</div>
}
```

> **Good to know:** Once streaming has started, `notFound()` mid-stream injects a `noindex` meta tag rather than returning a `404`, and `redirect()` becomes a client-side redirect. The nearest `not-found` boundary still renders in place of the streamed content, but the route stays `200` (a soft 404); ensure 404 detection happens before streaming starts to return a real `404`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/not-found.mdx)

### `not-found.js` file convention

- Renders UI when `notFound()` is thrown within a route segment. Returns `200` for streamed responses and `404` for non-streamed responses (SEO-relevant).
- In the component hierarchy it renders between `loading.js` and `page.js`, wrapped by the `<Suspense>` boundary from `loading.js` and the error boundary from `error.js` in the same segment.
- `not-found.js` / `global-not-found.js` components do **not** accept any props.
- By default `not-found` is a Server Component; mark it `async` to fetch and display data. If you need Client Component hooks (e.g. `usePathname`), fetch data on the client instead.
- The default not-found UI follows the OS color scheme via `prefers-color-scheme` and does **not** read an app-level theme; match an explicit theme with higher-specificity global stylesheet rules scoped to your theme selector (e.g. `html[data-theme='light'] body`).
- Root `app/not-found.js` and `app/global-not-found.js` also handle any unmatched URL for the whole app.

### `global-not-found.js` (experimental)

- Defines a 404 page for the entire app for URLs that match no route at all. Next.js **skips rendering** and directly returns this global page — you must import global styles, fonts, and other dependencies (including your theme) inside the file.
- Must return a full HTML document including `<html>` and `<body>` tags.
- Enable with `experimental.globalNotFound: true` in `next.config.ts`.
- Can export `metadata` or `generateMetadata`; Next.js auto-injects `<meta name="robots" content="noindex" />` for any 404-status page, including `global-not-found.js`.
- Useful when multiple root layouts or top-level dynamic segments make a single composed 404 impossible.
- Version: `global-not-found.js` introduced in `v15.4.0` (experimental); root `app/not-found` global handling in `v13.3.0`; `not-found` in `v13.0.0`.

### `unauthorized.js` file convention

- Renders UI when the `unauthorized()` function (from `next/navigation`) is invoked during authentication. Next.js returns a `401` status code.
- `unauthorized.js` components do **not** accept any props.
- Version: `unauthorized.js` introduced in `v15.1.0`.
- The `unauthorized()` function requires `experimental.authInterrupts` in `next.config.js` and **cannot** be called from the root layout. ([unauthorized](https://nextjs.org/docs/app/api-reference/functions/unauthorized))
- With `experimental.authInterrupts: true`, `unauthorized()` can interrupt a server-rendered tree to render the `unauthorized.js` login UI for unauthenticated users. It can be invoked from Server Components, **Server Actions**, and **Route Handlers** (but never the root layout). `forbidden()` has the same rules and renders `forbidden.js` with a `403` status. ([unauthorized](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unauthorized.mdx))

- Authorization failures (authenticated but lacking permission): use `forbidden()` from `next/navigation` to render a 403 page. The function, its required `experimental.authInterrupts` flag, and where it may legally be called are documented in `references/data-security.md`.

### `unstable_rethrow` (rethrow framework errors)

- Use `unstable_rethrow` to avoid accidentally catching Next.js-internal control-flow errors inside your own `try/catch`. It rethrows throws from `notFound()`, `redirect()`, `permanentRedirect()`, and Request-time APIs called in a route marked static (also relevant under PPR): `cookies()`, `headers()`, `searchParams`, `fetch(..., { cache: 'no-store' })`, and `fetch(..., { next: { revalidate: 0 } })`.
- Call it at the **top** of the `catch` block, passing the error: `catch (err) { unstable_rethrow(err); /* app handling */ }`. Also usable in a promise `.catch`.
- Any resource cleanup (clearing intervals/timers) must run **before** the `unstable_rethrow(err)` call or in a `finally` block — code after the rethrow never executes.
- Only use it when a `catch` may receive both application errors and framework-controlled exceptions; if you can let the **caller** handle exceptions, you may not need it.
- Version: `unstable_rethrow` is **deprecated** in favor of `isNextNotFound`, `isNextRedirect`, `isNextUnauthorized`, and `isNextForbidden` from `next/navigation`. It may still work, but prefer the type-safe helpers. ([unstable_rethrow](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/unstable_rethrow.mdx))

### Internal control-flow error tokens (debugging)

These are the strings you will see in logs when a framework throw is swallowed or left un-awaited — recognize them instead of treating them as application bugs:

| Function | Thrown token |
| --- | --- |
| `notFound()` | `NEXT_HTTP_ERROR_FALLBACK;404` |
| `unauthorized()` | `NEXT_HTTP_ERROR_FALLBACK;401` |
| `forbidden()` | `NEXT_HTTP_ERROR_FALLBACK;403` |
| `redirect()` / `permanentRedirect()` | `NEXT_REDIRECT` |

An un-awaited call surfaces in dev as `⨯ unhandledRejection: NEXT_HTTP_ERROR_FALLBACK;404` with **no 404 UI rendered** — always `await` (or let the throw propagate from) these functions.

- `notFound()`'s `never` return type preserves earlier type narrowing: after `if (!user) notFound()`, `user` is still treated as defined below.
- With Cache Components every dynamic route streams a static shell first, so a `notFound()` after streaming starts cannot set a real `404` status. Do the existence check in `proxy` if the HTTP status matters (e.g. for crawlers).
- For nested catches, import `isNextNotFound`, `isNextRedirect`, `isNextUnauthorized`, or `isNextForbidden` from `next/navigation` and rethrow when the caught error matches, so Next.js control-flow throws are not swallowed. ([not-found](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/not-found.mdx)) ([unauthorized](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unauthorized.mdx))

## `redirect` and `permanentRedirect`

Both imported from `next/navigation`. `redirect(path, type)` issues a **307 (temporary)** redirect and `permanentRedirect(path, type)` issues a **308 (permanent)** redirect. Both use the TypeScript `never` return type, so `return redirect(...)` / `return permanentRedirect(...)` is **not** required — the call throws and halts execution. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/redirect.mdx) (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/permanentRedirect.mdx)

- By default `redirect`/`permanentRedirect` use `push` (new browser-history entry) in Server Actions and `replace` (swap the current URL) everywhere else. Override with the `type` argument or the `RedirectType` enum:
  - `redirect('/x', RedirectType.replace)` — replaces the current URL in the history stack.
  - `redirect('/x', RedirectType.push)` — adds a new entry to the history stack.
  - The `type`/`RedirectType` argument has **no effect in Server Components**. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/redirect.mdx)
- In a streaming context, these insert a meta tag to emit the redirect on the client. In a **Server Action** they perform a client-side navigation when JavaScript is available; for progressive-enhancement form submissions they serve a `303` response. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/redirect.mdx)
- In a **Client Component during SSR on initial page load**, `redirect()` performs a server-side redirect. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/redirect.mdx)

## Error boundaries do not catch

- Errors in event handlers or async code that runs after rendering. Catch these manually and store the failure with `useState` or `useReducer` so the UI can respond.
- Errors in `useEffect` or other async work outside `startTransition`.
- Exception: an unhandled error thrown inside `startTransition` bubbles to the nearest error boundary.

## Source URLs

- Error Handling: https://nextjs.org/docs/app/getting-started/error-handling
- `error.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/error
- `catchError`: https://nextjs.org/docs/app/api-reference/functions/catchError
- `notFound`: https://nextjs.org/docs/app/api-reference/functions/not-found
- `not-found.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/not-found
- `forbidden.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/forbidden
- `unauthorized.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/unauthorized
- `default.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/default
- Content Security Policy: https://nextjs.org/docs/app/guides/content-security-policy
- Redirecting: https://nextjs.org/docs/app/guides/redirecting
- `redirect`: https://nextjs.org/docs/app/api-reference/functions/redirect
- `unauthorized` function: https://nextjs.org/docs/app/api-reference/functions/unauthorized
- `unstable_rethrow`: https://nextjs.org/docs/app/api-reference/functions/unstable-rethrow
- `forbidden` function (see `references/data-security.md`): https://nextjs.org/docs/app/api-reference/functions/forbidden
- `notFound` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/not-found.mdx
- `redirect` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/redirect.mdx
- `permanentRedirect` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/permanentRedirect.mdx
- `unauthorized` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unauthorized.mdx
- `unstable_rethrow` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unstable_rethrow.mdx

<!-- CANARY-API-REFERENCE-2026-08-31 -->
### Canary API reference additions (ingest 2026-08-31)

**`error.js` file convention**
- Must be a Client Component. Wraps `loading.js`, `not-found.js`, `page.js`, and nested `layout.js` in a React error boundary; does **not** wrap the `layout.js` or `template.js` in the same segment.
- Receives `error` (`Error & { digest?: string }`), `retry()` (re-fetches and re-renders the boundary's children; stable since v16.3.0), and `reset()` (re-renders without re-fetching; prefer `retry()`).
- In production, errors forwarded from Server Components show a generic message plus a `digest` identifier to avoid leaking sensitive details.
- `global-error.js` handles errors in the root layout/template, must define its own `<html>` and `<body>`, and does not inherit app-level theme classes/attributes.
- `metadata` / `generateMetadata` exports are not supported in `global-error` because it is a Client Component. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/error.mdx)

**`forbidden.js` file convention**
- Renders UI when the `forbidden()` function is invoked during authentication. Next.js returns a `403` status code. The component does not accept any props. Introduced in v15.1.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/forbidden.mdx)
