# Mutations and Server Actions

Reference: https://nextjs.org/docs/app/getting-started/mutating-data

## Server Functions and Server Actions

A **Server Function** is an async function that runs on the server. In a mutation/action context it is called a **Server Action**.

Mark a function or an entire file with `'use server'`:

```ts
'use server'

export async function createPost(formData: FormData) {
  // runs on the server
}
```

- Inline Server Functions inside Server Components are allowed.
- Client Components cannot define Server Functions; they import them from a `'use server'` file.
- Server Actions passed to `<form action>` or `<button formAction>` are automatically invoked inside a `startTransition`.
- Client-invoked Server Actions use `POST`, and only `POST` can invoke the action endpoint. They remain reachable through direct requests, so authenticate and authorize inside every Server Function; a direct server-side call is still an ordinary function call.
- A Server Action reference can cross into a Client Component as a prop and be assigned to `action` or `formAction`; the Client Component still cannot define the Server Function itself.
- The client currently dispatches Server Actions one at a time; do not rely on parallel client calls.
- Server Components support progressive enhancement by default: forms using Server Actions will still submit even if JavaScript is disabled or hasn't loaded.
- In Client Components, queued submissions are prioritized for hydration; after hydration, the browser does not refresh on form submission.
- With the experimental `useOffline` config enabled, a Server Action interrupted by a connectivity drop stays pending and completes when the network returns.
- The server update applies to the current React tree, re-rendering, mounting, or unmounting components, as needed. Client state is preserved for re-rendered components, and effects re-run if their dependencies changed. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))

## Pages Router: API Route forms

In the Pages Router, handle form submissions with API Routes in `pages/api/*` instead of Server Actions.

- Create a handler under `pages/api/submit.ts` receiving `NextApiRequest`/`NextApiResponse`. Read `req.body` and return a response. ([forms](https://nextjs.org/docs/pages/guides/forms))
- Submit from the client with a normal `<form onSubmit>` that calls `event.preventDefault()` and `fetch('/api/submit', { method: 'POST', body: new FormData(event.currentTarget) })`. Use React state for loading and error UI. ([forms](https://nextjs.org/docs/pages/guides/forms))
- API Routes do **not** set CORS headers by default — they are same-origin only. Add explicit CORS headers when cross-origin access is intended. ([forms](https://nextjs.org/docs/pages/guides/forms))
- Because API Routes run on the server, use sensitive values (API keys, DB credentials) via environment variables without exposing them to the client. ([forms](https://nextjs.org/docs/pages/guides/forms))
- Validate `req.body` server-side with a schema library such as Zod or Valibot before mutating data. ([forms](https://nextjs.org/docs/pages/guides/forms))
- Redirect after a successful mutation with `res.redirect(307, '/path')` from inside the API Route. ([forms](https://nextjs.org/docs/pages/guides/forms))

## Invoking Server Actions

- Pass to a `<form action={createPost}>` — receives `FormData` automatically.
- Pass to `<button formAction={createPost}>`.
- Call from an event handler inside a Client Component.
- Call from `useEffect` with `useTransition` for automatic mutations (e.g. view counts).

## Pending state

Use `useActionState` to get a `pending` boolean:

```tsx
'use client'

import { useActionState, startTransition } from 'react'

export function Button({ action }) {
  const [state, formAction, pending] = useActionState(action, null)
  return (
    <button formAction={formAction} disabled={pending}>
      {pending ? 'Saving...' : 'Save'}
    </button>
  )
}
```

For event-handler invocations, wrap the action in `startTransition` and use the returned `isPending` for UI feedback. See the [Building interactive apps guide](/docs/app/guides/interactive-apps) for pending feedback, optimistic UI, transitions, and error handling.

## Refresh / revalidate after mutation

- `refresh()` from `next/cache` re-renders the current route's Server Components (refetching its RSC Payload) so the UI reflects newly mutated data without a full navigation. It does **not** revalidate tagged data. `refresh()` can **only** be called from within a Server Action — it cannot be used in Route Handlers, Client Components, or any other context. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/refresh.mdx)
- `revalidatePath('/path')` invalidates a route.
- `revalidateTag('tag')` invalidates tagged cache stale-while-revalidate.
- `updateTag('tag')` immediately expires tagged cache (Server Actions only, read-your-own-writes).
- `redirect()` throws a control-flow exception; any code after it does not run. Call revalidation before `redirect` if fresh data is needed.

### Tag-based revalidation under Cache Components

Under Cache Components, `revalidateTag` requires a second `profile` argument (for example `'max'`) that controls how long stale content can be served while fresh content generates in the background. `revalidateTag(tag, profile)` is stale-while-revalidate and works in Server Actions and Route Handlers. In Route Handlers or webhooks, prefer `revalidateTag(tag, profile)` instead of `updateTag`, because `updateTag` can only be called from a Server Action. `revalidateTag(tag)` without a profile is deprecated under Cache Components and produces a TypeScript error.

`revalidatePath` invalidates by URL path through soft tags (`_N_T_` prefixed tags per segment). Regeneration happens lazily on the next request. Use it when tag-based invalidation is overkill.

## Offline behavior

With the experimental `useOffline` config enabled, a Server Action interrupted by a connectivity drop stays pending and completes when the network returns. The UI remains in its loading state (Suspense fallback or pending transition). Use `useOffline` from `next/offline` for user-facing connectivity feedback. See the [offline support guide](/docs/app/guides/offline-support).

## Cookies in Server Actions

`cookies()` from `next/headers` is an **async** function — you must `await` it (or use React's `use`). It was introduced in `v13.0.0` and became async in `v15.0.0-RC`; in `v14` and earlier it was synchronous, and Next.js 15 still allows synchronous access but that behavior will be deprecated in the future.

You can get, set, and delete cookies inside a Server Action (and in Route Handlers) using `cookies()`. Setting/deleting a cookie re-renders the current page so the UI reflects the new cookie value.

### Cookie store methods

The awaited `cookieStore` exposes:

| Method | Return Type | Description |
| --- | --- | --- |
| `get('name')` | Object | Returns an object with the cookie's name and value. |
| `getAll()` | Array of objects | Returns all cookies; if `name` is given, only those matching it. |
| `has('name')` | Boolean | Whether a cookie with the given name exists. |
| `set(name, value, options)` | — | Sets the outgoing request cookie (`options` optional). |
| `delete(name)` | — | Deletes the cookie. |
| `toString()` | String | String representation of the cookies. |

### `set` options

`set` accepts either positional `set(name, value, options)` or a single options object `set({ name, value, ...options })`. Supported options:

| Option | Type | Description |
| --- | --- | --- |
| `name` | String | Name of the cookie. |
| `value` | String | Value stored in the cookie. |
| `expires` | Date | Exact date when the cookie expires. |
| `maxAge` | Number | Cookie lifespan in seconds. |
| `domain` | String | Domain where the cookie is available. |
| `path` | String (default `'/'`) | Path scope within the domain. Only option with a default value. |
| `secure` | Boolean | Sent only over HTTPS. |
| `httpOnly` | Boolean | Restricts the cookie to HTTP requests (no client-side access). |
| `sameSite` | Boolean, `'lax'`, `'strict'`, `'none'` | Cross-site request behavior. |
| `priority` | String (`"low"`, `"medium"`, `"high"`) | Cookie priority. |
| `partitioned` | Boolean | Whether the cookie is partitioned (CHIPS). |

### Read vs write location

- **Reading** cookies works in Server Components because you access the `Cookie` headers the browser sends in the request.
- **Writing** (`.set`, `.delete`) is NOT permitted during Server Component render. Invoke a Server Function from the client or use a Route Handler — that is the only place `Set-Cookie` response headers can be set.
- HTTP disallows setting cookies after streaming starts, so `.set` must run in a Server Function or Route Handler.
- `.delete` additionally requires the same domain as `.set` (exact subdomain match for wildcard domains) and the same protocol (HTTP/HTTPS).

### Caching implications

- `cookies()` is a Request-time API; using it in a layout or page opts the route into **dynamic rendering** (its value cannot be known ahead of time).
- Under Cache Components, calling `cookies()` outside a `<Suspense>` boundary prevents the route from being prerendered.

## Single-roundtrip response

When a Server Action triggers an immediate cache invalidation (`updateTag`, `revalidatePath`, `refresh`) or cookie mutation, Next.js runs the action and re-renders the current route in one HTTP request. The response contains both the action's return value and the new RSC Payload, so the UI updates without a follow-up fetch.

`redirect()` is another single-response path: it navigates the router and streams the destination's RSC Payload. It throws a control-flow exception, so code after it does not run; place revalidation calls before `redirect` when the destination needs fresh data.

`revalidateTag` with a stale-while-revalidate profile is the exception: it marks the tag for background refresh and does not include a re-render in the action response. If an action does not invalidate, refresh, mutate cookies, or redirect, its response carries only the return value and does not re-render the current route.

## Sequential dispatch on the client

Next.js dispatches Server Actions one at a time per client. If a user triggers multiple actions in quick succession, the second waits for the first to finish. This is a property of the **client dispatcher**, not of Server Functions in general. Do not rely on `Promise.all` to parallelize them from the client. If you need parallel work, do it inside a single Server Action, fetch in parallel from a Server Component, or use a Route Handler for non-mutation requests. Server-side, an action runs in its own request and can do anything an async function can do.

> **Good to know:** Sequential dispatch keeps the re-rendered server tree consistent with the action result that produced it.

## Security

A Server Action is reachable by anyone who can send the same POST, not just through your UI. Treat every action as an untrusted entry point.

Framework-level protections:
- **CSRF check** — compares `Origin` to `Host`/`X-Forwarded-Host`. Configure `serverActions.allowedOrigins` for proxy/CDN domains; `*` matches exactly one label, `**` matches one or more labels (only at the start of a pattern); ports cannot be wildcarded. Requests with no `Origin` header are allowed with a warning.
- **Body size limit** — defaults to 1MB. Configure `serverActions.bodySizeLimit` when accepting larger payloads; it applies to the raw HTTP body including `multipart/form-data` overhead.
- **Encrypted action IDs and DCE** — unused Server Functions are stripped from client bundles; action references are encrypted at build time.
- **Closure variable encryption** — captured inline-action variables are encrypted before being sent to the client. Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` to a stable key shared across instances for multi-instance/self-hosted deployments.

Application-level checks (still required):
- Authenticate and authorize inside every action.
- Validate inputs (shape is not enough; check ownership).
- Send references/IDs from the client, not full records.
- Schema validation (zod or similar) only checks the shape of the input; a well-formed object can still refer to a row the caller does not own.
- A client legitimately tells the server _which_ item to act on, but it should not supply the row's contents or ownership.
- Render-time gating (only rendering a form on an authenticated page) is not a security boundary, because requests can be sent without going through the UI.
- Constrain return values to what the UI needs.
- Use a `server-only` Data Access Layer for database access.

If `authInterrupts` is enabled, throw `unauthorized()`/`forbidden()` from `next/navigation` to render `unauthorized.tsx`/`forbidden.tsx` automatically. `forbidden()` is only available when `authInterrupts` is enabled; calling it without the flag throws an error. ([unauthorized](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/unauthorized.mdx))

## Choosing a cache update after mutation

- `updateTag(tag)` — immediate expiration; next read waits for fresh data. **Server Actions only**; calling it elsewhere throws. Use for read-your-own-writes.
- `revalidateTag(tag, profile)` — stale-while-revalidate; action response does not wait for fresh data.
- `revalidatePath(path)` — invalidate by URL path when tagging is overkill; regeneration is lazy on next request. From a Server Action, it also refreshes the current page; from a Route Handler it only marks the path. ([revalidatePath](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/revalidatePath.mdx))
- `refresh()` — refetch current route RSC Payload without invalidating cached data. Use when the view depends on non-cache state that changed.

> **Good to know:** In Route Handlers or webhooks, use `revalidateTag(tag, profile)` instead of `updateTag`. `revalidatePath` accepts an optional second argument `type?: 'page' | 'layout'`. `type` is **required when `path` contains a dynamic segment** and must be **omitted for a literal path**; `'layout'` invalidates the layout plus all nested pages. ([revalidatePath](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/revalidatePath.mdx))

## Forms and progressive enhancement

- Server Actions invoked via `<form action>` or `<button formAction>` automatically receive a `FormData` object.
- Use `Object.fromEntries(formData)` to convert multi-field forms to objects; note extra `$ACTION_`-prefixed properties.
- Pass additional arguments with `bind`, or use hidden input fields (the value is rendered as HTML and not encoded).
- `bind` works in both Server and Client Components and supports progressive enhancement.
- For validation errors / pending UI, use `useActionState` in a Client Component. When `useActionState` is used, the Server Function receives `prevState` / `initialState` as its first argument.
- For pending feedback independent of `useActionState`, use `useFormStatus` from `react-dom` inside a Client Component nested in the form. In React 19, `useFormStatus` returns additional keys (`data`, `method`, `action`); in earlier React versions only `pending` is available.
- Use `useOptimistic` to update UI before the Server Function finishes executing (optimistic updates).
- Nested `<button>`, `<input type="submit">`, and `<input type="image">` elements inside a form can call Server Actions via the `formAction` prop.
- Trigger programmatic form submission with `requestSubmit()` on the form element.
- With the experimental `useOffline` config enabled, a Server Action interrupted by a connectivity drop stays pending and completes when the network returns.

## Server Action encryption key (self-hosting / multi-instance)

When self-hosting across multiple servers, each instance may end up with a different encryption key for closed-over variables. Set `process.env.NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` to a base64-encoded value whose decoded length matches a valid AES key size (16, 24, or 32 bytes). Next.js generates 32-byte keys by default. This ensures persistent keys across builds and consistent behavior across instances.

## Configuration

The `serverActions` option is configured under `experimental` in `next.config.js` per current docs:

```ts
const nextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
      bodySizeLimit: '2mb',
    },
  },
}
```

- `allowedOrigins`: entries can use wildcards — `*` matches exactly one label, `**` matches one or more labels (only at the start of a pattern). Ports can't be wildcarded; write them out fully (`my-proxy.com:8443`). Partial replacement is not supported (`app-*.my-proxy.com` invalid). Write the host visible in the browser address bar, not the internal proxy host. Requests with no `Origin` header are allowed with a warning.
- `bodySizeLimit`: default **1MB**; applies to the **raw HTTP body** including `multipart/form-data` overhead (boundaries, headers, metadata). Leave ~10–20 KB headroom. Values like `'2mb'`, `'500kb'`, or byte numbers.
- The CSRF check compares the request's `Origin` header against the app's own host (`x-forwarded-host` or `host`) and runs in production and development.
- For reverse proxies, set `allowedDevOrigins` (dev-server assets) **and** `serverActions.allowedOrigins` for the same tunnel host.

Always verify the config shape for the installed Next.js version; stable vs experimental placement can change.

## Deployment considerations

Action IDs are part of build artifacts and can rotate between deployments (at most every 14 days). A client running an older build may invoke an action ID that no longer exists, producing "Failed to find Server Action". Mitigate with rolling deployments, a stable `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`, and retry paths in the UI.

## Source URLs

- Mutating Data: https://nextjs.org/docs/app/getting-started/mutating-data
- Server Actions guide: https://nextjs.org/docs/app/guides/server-actions
- Forms guide: https://nextjs.org/docs/app/guides/forms
- Data Security guide: https://nextjs.org/docs/app/guides/data-security
- `use server` directive: https://nextjs.org/docs/app/api-reference/directives/use-server
- `serverActions` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `revalidatePath` / `revalidateTag` / `updateTag` / `refresh`: see `caching-and-revalidation.md`
- `useActionState`: https://react.dev/reference/react/useActionState
- `useFormStatus`: https://react.dev/reference/react-dom/hooks/useFormStatus
- `useOptimistic`: https://react.dev/reference/react/useOptimistic
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- How revalidation works: https://nextjs.org/docs/app/guides/how-revalidation-works
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- Redirecting guide: https://nextjs.org/docs/app/guides/redirecting
- `redirect`: https://nextjs.org/docs/app/api-reference/functions/redirect
- `permanentRedirect`: https://nextjs.org/docs/app/api-reference/functions/permanentRedirect
- Interactive apps: https://nextjs.org/docs/app/guides/interactive-apps
- `cookies`: https://nextjs.org/docs/app/api-reference/functions/cookies
- `refresh` (canary): https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/refresh.mdx

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — mutations / BFF additions (ingest 2026-08-30)

**Forms with Server Actions (`forms`)**
- Alternative to `bind`: pass args as hidden inputs (`<input type="hidden" name="userId" value={userId} />`), but the value is part of rendered HTML and is NOT encoded — prefer `bind` for sensitive/structured data. (Source: https://nextjs.org/docs/app/guides/forms)
- `bind` works in both Server and Client Components and supports progressive enhancement. (Source: above)
- With the experimental `useOffline` config enabled, a Server Action interrupted by a connectivity drop stays pending and completes when the network returns, so the user does not lose the submission. (Source: above)

**Backend-for-frontend (`backend-for-frontend`)**
- Next.js backend capabilities (Route Handlers / Server Actions) are NOT a full backend replacement — they are a publicly reachable API layer that handles any HTTP request and can return any content type. (Source: https://nextjs.org/docs/app/guides/backend-for-frontend)
- Validate data before passing it to other systems. (Source: above)
- Use `POST` (not `GET`) for requests carrying sensitive data such as geo-location — `GET` may be cached or logged, exposing the data. (Source: above)
- Third-party libraries may still call `proxy` "middleware" — same concept, renamed in v16. (Source: above)
