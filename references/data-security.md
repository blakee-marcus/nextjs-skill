# Data Security

Reference: https://nextjs.org/docs/app/guides/data-security

## Data fetching approaches

Choose one approach and avoid mixing them:

1. **External HTTP APIs** — call existing REST/GraphQL endpoints from Server Components with `fetch`, passing credentials explicitly. Good for large existing apps with separate backend teams.
2. **Data Access Layer (DAL)** — create a `server-only` internal library that performs authorization and returns minimal DTOs. Recommended for new projects; centralizes access and reduces accidental data leaks.
3. **Component-level data access** — place database queries directly in Server Components. Fine for prototypes, but easy to accidentally pass full records to Client Components.

## Server / Client boundary

- Server Components run only on the server and can safely access env vars, secrets, databases, and internal APIs.
- Client Components run on the server during prerendering, but must follow browser security assumptions and must not access privileged data or server-only modules.
- Functions and classes are already blocked from being passed to Client Components by default.

## Tainting

Use React Taint APIs to prevent accidental exposure of sensitive objects or values to the client:

- `experimental_taintObjectReference` for data objects.
- `experimental_taintUniqueValue` for specific values.
- Enable with `experimental.taint: true` in `next.config.js`. Also enables the React `experimental` channel for `app`.

**Caveats:**
- Copying a tainted object creates an **untainted** version (loses all guarantees). You must taint the copy.
- Data derived from a tainted value is **not** tainted — you must taint derived values explicitly.
- Values are tainted only while their lifetime reference is in scope.
- **Do not rely on tainting as the only mechanism** to prevent exposing sensitive data to the client. Model your DAL so sensitive data isn't returned where unneeded.

Tainting is an additional safety net, not a substitute for filtering data in your DAL.

## Server-only modules

Mark modules that must never run on the client with `import 'server-only'`:

```ts
import 'server-only'
```

Next.js handles `server-only` imports internally; install the package only if linting rules require the dependency.

## Server Actions security

A Server Action is reachable by anyone who can send the same POST, not just through your UI. Treat every action as an untrusted entry point.

- Always authenticate **and** authorize inside every action. Page-level checks do not extend to actions.
- Validate inputs (shape is not enough; check ownership of resources).
- Do not trust UI gating; requests can bypass the UI.
- Keep actions thin: delegate authentication, authorization, ownership checks, and database mutations to a `server-only` DAL where practical. `import 'server-only'` is also valid in the `'use server'` module itself when that action is imported into a Client Component.
- Constrain return values to what the client needs.
- Consider rate limiting for expensive or abuse-prone operations such as email sends and database writes.
- Schema validation (Zod, Valibot) only checks shape; a well-formed object can still refer to a row the caller does not own.

### Framework-level protections

- **CSRF check** — compares `Origin` to `Host`/`X-Forwarded-Host`. Configure `serverActions.allowedOrigins` for proxy/CDN domains; `*` matches exactly one label, `**` matches one or more labels (only at the start of a pattern); ports cannot be wildcarded. Requests with no `Origin` header are allowed with a warning.
- **Body size limit** — defaults to 1MB. Configure `serverActions.bodySizeLimit` when accepting larger payloads; it applies to the raw HTTP body including `multipart/form-data` overhead.
- **Encrypted action IDs and DCE** — unused Server Functions are stripped from client bundles; action references are encrypted at build time.
- **Closure variable encryption** — inline actions capture a render-time snapshot whose variables travel to the client and back when invoked. Next.js encrypts them, but encryption is not a substitute for minimizing sensitive captures. Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` to a stable base64-encoded AES key (16/24/32 bytes decoded) shared across instances for multi-instance/self-hosted deployments.

### Allowed origins

For reverse proxies or multi-layered backends, set `serverActions.allowedOrigins` in `next.config.js`:

```js
module.exports = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
    },
  },
}
```

### Proxy matchers do not cover Server Functions

A common mistake is to assume a `proxy.ts` (or legacy `middleware.ts`) `matcher` that protects a route also protects the Server Actions on that route. **It does not**, and excluding a path from the matcher silently *removes* Proxy coverage for that path's Server Functions.

- Server Functions (Server Actions) are **not separate routes** in the Proxy chain. They are handled as `POST` requests to the route where they are used, so a Proxy `matcher` that excludes a path also skips Server Function calls on that path.
- A `matcher` change or a refactor that moves a Server Function to a different route can silently drop Proxy authentication/authorization for those actions.
- **Always verify authentication and authorization inside each Server Function** (see above) and never rely on Proxy as the sole gate. In canary / Next.js 16, `middleware` is deprecated and renamed to `proxy` (migrate with `npx @next/codemod@canary middleware-to-proxy .`).
- The `middleware` file convention is deprecated in v16; it has been renamed to `proxy` and functionality is unchanged. A codemod is available: `npx @next/codemod@canary middleware-to-proxy .`.
- Proxy runs on the Node.js runtime by default in v16; the `runtime` segment config is not available in Proxy and throws if set.
- Proxy runs on **every** request when no `matcher` is set (including `_next/static`, `_next/image`, and `public/`); use a negative-match pattern. Note that Proxy still runs for `_next/data` routes even when a negative matcher excludes them.
- `NextResponse.next({ request: { headers } })` makes headers available upstream (to the app); `NextResponse.next({ headers })` would expose them to the client — do not use the latter for request headers.
- During RSC requests, Next.js strips internal Flight headers (`rsc`, `next-router-state-tree`, `next-router-prefetch`) from the `request` instance in Proxy. Use `NextResponse.rewrite()` so RSC headers propagate automatically; for custom `fetch()`-based rewrites, forward them manually or enable `skipProxyUrlNormalize`.

Source: https://nextjs.org/docs/app/api-reference/file-conventions/proxy (canary / Next.js 16)

## Environment variables

- Secret keys should be stored in environment variables and only accessed by the DAL.
- By default, environment variables are only available on the Server.
- Next.js exposes any environment variable prefixed with `NEXT_PUBLIC_` to the client.

## Input validation

Always validate input from the client: form data, URL parameters, headers, and `searchParams`. Do not use `searchParams` values as authorization gates without re-verifying on the server.

- When forwarding incoming request headers (e.g. in Proxy or a Route Handler via `NextResponse.next()` / `NextResponse.rewrite()`), do **not** copy all headers. Copying everything can leak sensitive data (cookies, auth tokens, `x-*` internals) to clients or upstream services. Build an allow-list of known-safe headers instead of spreading `request.headers`.
([NextResponse](https://nextjs.org/docs/app/api-reference/functions/next-response))

## Side effects during rendering

Mutations (logging out users, updating databases, invalidating caches) should never be a side effect during Server or Client Component rendering. Use Server Actions instead.

## Authorization with `forbidden()`

Use `forbidden` from `next/navigation` to render a 403 page for authenticated-but-unauthorized users (role checks, etc.). It is the authorization counterpart to `unauthorized()` (401, see `references/error-handling.md`).

- Requires `experimental.authInterrupts: true` in `next.config.js` / `next.config.ts` before it can be used.
- Invoking `forbidden()` throws a `NEXT_HTTP_ERROR_FALLBACK;403` error and terminates rendering of the current route segment; Next.js also injects `<meta name="robots" content="noindex" />` so the page is not indexed.
- Call it in the render path — a component, or a function a component `await`s. A call left in an un-awaited promise throws where nothing catches it and no 403 UI renders; in dev the server logs `⨯ unhandledRejection: NEXT_HTTP_ERROR_FALLBACK;403`. Always `await` the function that may call it.
- No `return forbidden()` needed — it throws (TypeScript `never` return type) so execution stops. A `try/catch` around the call suppresses the interrupt and no forbidden UI renders; use `unstable_rethrow` to let it through.
- Cannot be called in the root layout.
- Can be invoked in Server Components, Server Functions (Server Actions), and Route Handlers.
- After streaming starts, the response is already `200` and the status can't change; to return a real `403`, run the check before streaming (e.g. in `proxy` with Cache Components).
- Version: `forbidden` introduced in `v15.1.0`.

## Audit checklist

- Is there an established Data Access Layer?
- Are database packages and env vars imported only inside the DAL?
- Do `"use client"` component props expect private data or overly broad types?
- Do `"use server"` files re-authenticate and re-authorize inside each action?
- Do actions check ownership (authorization, not just authentication)?
- Are action return values filtered to only what the client needs?
- Are `params` validated (bracket folders are user input)?
- Are `proxy.ts` and `route.ts` audited with traditional techniques?

## Source URLs

- Data Security guide: https://nextjs.org/docs/app/guides/data-security
- Server Actions guide: https://nextjs.org/docs/app/guides/server-actions
- Forms guide: https://nextjs.org/docs/app/guides/forms
- Authentication guide: https://nextjs.org/docs/app/guides/authentication
- `serverActions` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `taint` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/taint
- Environment variables guide: https://nextjs.org/docs/app/guides/environment-variables
- `forbidden` function: https://nextjs.org/docs/app/api-reference/functions/forbidden
- `authInterrupts` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/authInterrupts
- `unauthorized` function: https://nextjs.org/docs/app/api-reference/functions/unauthorized

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — data-security additions (ingest 2026-08-30)

**Data Security guide (`data-security`)**
- The server/client isolation IDs are created during compilation and cached for a maximum of 14 days; they are regenerated on a new build or when the build cache is invalidated. This reduces risk when an auth layer is missing — but is not a substitute for auth. (Source: https://nextjs.org/docs/app/guides/data-security)

**Authentication with Cache Components (`authentication-with-cache-components`)**
- Cache keys and tags are stored in plain text: a cached function's arguments and captured variables are serialized into its cache key, and `cacheTag` values are stored as written. Avoid putting secrets into cache arguments/tags. (Source: https://nextjs.org/docs/app/guides/authentication-with-cache-components)
- Expose only what the client needs — return a narrow object (e.g. `{ id, name }`) from session helpers rather than the raw session. (Source: above)

**Content Security Policy (`content-security-policy`)**
- In development `'unsafe-eval'` is required (React uses `eval` for enhanced debugging, e.g. reconstructing server error stacks in the browser); it is NOT required in production, and neither React nor Next.js use `eval` in production by default. (Source: https://nextjs.org/docs/app/guides/content-security-policy)
- The nonce-based CSP feature is experimental and available in App Router apps. (Source: above)
- For dynamic rendering you can still generate nonces with Proxy, combining SRI integrity attributes and nonce-based CSP. (Source: above)
