# Data Fetching and Streaming

Reference: https://nextjs.org/docs/app/getting-started/fetching-data

## Server Components

Server Components can fetch data directly during render using any async I/O (`fetch`, ORM, database client, file system):

```tsx
export default async function Page() {
  const posts = await (await fetch('https://api.example.com/posts')).json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

- Fetch in the component that needs the data instead of prop-drilling; identical `fetch` requests are automatically deduplicated within a single render pass (see `fetch` extended options below).
- `fetch` is **not cached by default** and blocks the page until complete. Opt in with the [`use cache`](/docs/app/api-reference/directives/use-cache) directive to cache results, or wrap the fetching component in [`<Suspense>`](/docs/app/getting-started/caching#streaming-uncached-data) to stream fresh data at request time.
- During development, you can log `fetch` calls for visibility. See the [`logging`](/docs/app/api-reference/config/next-config-js/logging) API reference.
- ORM / database queries are safe because they run only on the server; still authenticate and authorize the request.

## Streaming

### `fetch` extended server options

Next.js extends the Web `fetch()` API so each server request can set its own persistent caching and revalidation semantics. The `cache` option controls how a server-side fetch interacts with the framework cache (distinct from the browser's HTTP cache).

- `options.cache`:
  - `auto no cache` (default): fetched on every request in development; during `next build` it is fetched once because the route is statically prerendered, unless Request-time APIs are detected on the route (then every request).
  - `no-store`: fetched on every request, even if Request-time APIs are not detected.
  - `force-cache`: Next.js looks for a matching request in the server-side cache (matched on URL, method, headers, and body). Only `200` responses are stored.
- `options.next.revalidate`: `false` (cache indefinitely, ~`Infinity`), `0` (never cache), or a number of seconds for the cache lifetime.
- `options.next.tags`: array of cache tags (max 256 chars each, max 128 items) for on-demand revalidation via `revalidateTag`.
- **Edge Runtime fetch caveats.** The Edge Runtime uses the Web-standard `fetch` API, so `options.cache`, `options.next.revalidate`, and `options.next.tags` do not apply in Edge Runtime contexts such as Proxy (formerly Middleware). ISR/Next.js cache semantics are Node.js-runtime features.
- Caching is opt-in — set `cache: 'force-cache'` to cache any request, including `POST` and requests sending `authorization`/`cookie` headers.
- Draft Mode bypasses the cache entirely (no read or write).
- Conflicting `fetch` options are ignored: e.g. `{ revalidate: 3600, cache: 'no-store' }` — both are dropped and (in development) a warning prints to the terminal. Don't mix `revalidate`/`cache` semantics on one call. ([fetch](https://nextjs.org/docs/app/api-reference/functions/fetch))
- Do not mix `revalidate`/`cache` semantics on one `fetch` call — conflicting options are ignored and a dev warning prints.
- Memoization is separate from persistent caching; `GET` requests with the same URL + options are memoized within a single server render pass (shared across Server Components, layouts, pages, `generateStaticParams`, `generateViewport`). Opt out with an `AbortController` signal. Memoization does not apply in Route Handlers. ([fetch](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/fetch.mdx))
- In development, `fetch` responses are cached across HMR by default (`serverComponentsHmrCache`), so uncached requests may not show fresh data between HMR refreshes (cleared on navigation / full reload). ([fetch](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/fetch.mdx))

Break slow data into smaller chunks and stream them from the server so the page isn't blocked by the slowest request.

On initial page load, two streams work together:
- **HTML stream** — React produces progressive HTML chunks. Static parts (layouts, navigation, Suspense fallbacks) render first; when a `<Suspense>` boundary's content is ready, React streams its HTML plus inline scripts that swap the fallback DOM without waiting for the JS bundle to load.
- **Component payload (RSC Payload)** — a serialized representation of the component tree used for hydration and client-side updates. On client-side navigation, only the payload is fetched (with `rsc: 1` header), no HTML.

The **static shell** is everything that renders before any async work resolves. With Cache Components, it is prerendered at build time and served instantly from the edge.

**`loading.tsx`** automatically wraps a segment's `page.tsx` and any children below in a `<Suspense>` boundary.

- Good for route-level loading UI.
- A layout that accesses uncached/runtime data (e.g. `cookies()`, `headers()`, uncached fetches) does **not** fall back to a same-segment `loading.tsx`; it blocks navigation. Move the runtime access into its own `<Suspense>` boundary, or fetch in the page so `loading.tsx` can cover it.
- `loading.js` nests inside `layout.js` in the component hierarchy.
- With Cache Components enabled, a layout that accesses uncached runtime data will produce a build-time error instead of silently blocking navigation.

**`<Suspense>`** gives granular control around a component:

```tsx
import { Suspense } from 'react'
import BlogList from '@/components/BlogList'
import BlogListSkeleton from '@/components/BlogListSkeleton'

export default function BlogPage() {
  return (
    <div>
      <header>
        <h1>Welcome to the Blog</h1>
      </header>
      <Suspense fallback={<BlogListSkeleton />}>
        <BlogList />
      </Suspense>
    </div>
  )
}
```

- Prefer `<Suspense>` close to the runtime/uncached data access over a route-level `loading.tsx`.
- Sibling `<Suspense>` boundaries stream independently in whatever order they resolve.
- Push dynamic access (`params`, `searchParams`, `cookies()`, `headers()`, data fetches) down to the component that actually needs it so the rest can stay in the static shell.
- Session reads (e.g. `cookies()`/auth) should happen inside their own `<Suspense>` boundary, not at the top of a layout, so they don't block the rest of the tree.
- Bots/crawlers receive fully rendered HTML, not streaming.
- Static export does not support streaming.
- Design meaningful fallbacks (skeletons, spinners, or recognizable partial UI).

## Dynamic route data order

In the App Router, route parameters (`params` and `searchParams`) are always resolved before request-time APIs (`cookies()`, `headers()`, `connection()`, `io()`). Components that only use `params` can be cached while components using request-time APIs must be wrapped in `Suspense`. Cache Components makes this distinction a build-time requirement.

## The streaming HTTP contract

Once streaming starts, the HTTP response headers (including status code) have already been sent. **You cannot change the status code or headers after streaming starts.**

When a `<Suspense>` fallback renders or a component suspends, the server commits to `200 OK` to begin sending the HTML stream. If `notFound()` fires mid-stream, Next.js cannot change the status to `404`; instead it injects `<meta name="robots" content="noindex">` into the streamed HTML. If `redirect()` fires mid-stream, it becomes a client-side redirect rather than an HTTP redirect header. ([loading status codes](https://nextjs.org/docs/app/api-reference/file-conventions/loading#status-codes))

To get a real HTTP status code for errors, place `notFound()` **before** any `await` or `<Suspense>` boundary, or handle the request earlier in Proxy/`next.config.js` redirects.

## Streaming through infrastructure

Any layer that buffers the response defeats streaming: reverse proxies, CDNs, load balancers, compression, and even some clients. For nginx and similar proxies, disable buffering by setting the `X-Accel-Buffering: no` response header. Load balancers must support chunked transfer encoding or HTTP/2 streaming. Not all serverless platforms support streaming by default (e.g. AWS Lambda requires response streaming mode).

Verify with browser DevTools (long "Content Download" + early TTFB) or a small script that reads the response body as a stream. Use `Accept-Encoding: identity` to avoid compression buffering.

### Bots and crawlers

HTML-limited bots (e.g. `Twitterbot`, `Slackbot`, `Bingbot`) need metadata in `<head>`, so Next.js waits for `generateMetadata` to resolve before streaming. DOM-capable crawlers and regular visitors can receive streaming metadata. With Cache Components, HTML-limited bots skip the prerendered shell and render dynamically, so any data the shell relies on must also be available at request time.

### Streaming in Route Handlers

Outside React rendering, Route Handlers can stream raw responses with Web Streams (`ReadableStream`, `fileHandle.readableWebStream()`). Useful for Server-Sent Events, large files, or progressive JSON.

### Edge Runtime streaming notes

- The Edge Runtime supports Web-standard stream APIs (`ReadableStream`, `WritableStream`, `TransformStream`, `ReadableStreamDefaultReader`, `ReadableStreamBYOBReader`, `WritableStreamDefaultWriter`, `TextEncoderStream`, `TextDecoderStream`). Use these when streaming in Proxy or in the deprecated `runtime = 'edge'` environment. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))
- Edge Runtime does **not** support Node.js-specific streaming such as `node:stream`, `fs.createReadStream`, or `fileHandle.readableWebStream()` from `node:fs/promises`.
- Both Node.js and Edge runtimes can support streaming depending on the deployment adapter.

## Sequential vs parallel data fetching

Layouts and pages render in parallel by default, so each route segment can begin fetching as soon as possible. Within a single component, however, multiple `await` calls still run sequentially. Call all independent data functions first, then `await` with `Promise.all` (or `Promise.allSettled` if failures should not fail the whole operation):

```tsx
export default async function Page({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params
  const artistData = getArtist(username)
  const albumsData = getAlbums(username)
  const [artist, albums] = await Promise.all([artistData, albumsData])
  return <ArtistPage artist={artist} albums={albums} />
}
```

- Initiate requests as early as possible (`fetch` starts when called), then await together.
- `Promise.all` fails fast on the first rejection.
- `Promise.allSettled` returns all results and is useful when requests are independent and partial failure is acceptable.

## Sequential (dependent) data fetching

When one request depends on another, the dependent fetch must `await` the prerequisite. To avoid blocking the entire page, stream the dependent part with its own `<Suspense>` boundary:

```tsx
export default async function Page({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params
  const artist = await getArtist(username)

  return (
    <>
      <h1>{artist.name}</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <Playlists artistID={artist.id} />
      </Suspense>
    </>
  )
}

async function Playlists({ artistID }: { artistID: string }) {
  const playlists = await getArtistPlaylists(artistID)
  return (
    <ul>
      {playlists.map((playlist) => (
        <li key={playlist.id}>{playlist.name}</li>
      ))}
    </ul>
  )
}
```

- The first request still blocks the page; ensure it resolves quickly or cache it.
- Cache Components will surface a build-time error if a layout accesses uncached/runtime data, rather than silently blocking navigation.

### `connection()` vs `io()`

- `connection()` (from `next/server`) blocks rendering until a real request is available; it also blocks prefetching. Use when a component does not use Request-time APIs (`cookies()`, `headers()`, etc.) but still needs to run per-request. Replaces `unstable_noStore`. With Cache Components, prefer `io()`. ([connection](https://nextjs.org/docs/app/api-reference/functions/connection))
- `io()` (from `next/cache`, v16.3.0+) also suspends during prerendering so code after it is excluded from the static shell, but the boundary can still be cached/prefetched — unlike `connection()` which blocks prefetches. Use before synchronous IO like `new Date()`, `Math.random()`, `crypto.randomUUID()`, `node:sqlite`. In a Client Component, use `use(io())`. No-op without `cacheComponents: true`. ([io](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/io.mdx))
- **Edge Runtime compatibility.** `connection()`, `io()`, `cookies()`, `headers()`, and `draftMode()` are Node.js runtime/Server Component APIs and are not available in the Edge Runtime/Proxy. Use Web-standard `Request`/`Headers`/`Response` APIs and `NextRequest`/`NextResponse` in Proxy instead. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))

## Client Components

Fetch in Client Components using:

- React's `use` API to unwrap a **promise passed from a Server Component**. Start the fetch on the server without awaiting it, pass the promise to a Client Component, and wrap that component in `<Suspense>`:

  ```tsx
  // Server Component page
  import { Suspense } from 'react'
  import Posts from './posts'

  export default function Page() {
    const postsPromise = getPosts() // do not await
    return (
      <Suspense fallback={<div>Loading...</div>}>
        <Posts posts={postsPromise} />
      </Suspense>
    )
  }

  // 'use client'
  import { use } from 'react'

  export default function Posts({ posts }: { posts: Promise<Post[]> }) {
    const allPosts = use(posts)
    return <ul>{allPosts.map((post) => <li key={post.id}>{post.title}</li>)}</ul>
  }
  ```

  The promise must be cached/stable (same instance across re-renders); its resolved value must be serializable when crossing from server to client.
  To share one promise with many Client Components, provide it through context. See [Using React's `use` within a Context Provider](/docs/app/guides/single-page-applications#using-reacts-use-within-a-context-provider).

- SWR or TanStack Query for client-side caching, refetching, and mutation lifecycle. See the SWR and TanStack Query guide pages for patterns.
- For direct browser fetching and coordinating a library cache with Next.js server/client caches, see the [Client-side data fetching guide](/docs/app/guides/client-side-data-fetching).

### Offline-aware client fetching

With `experimental.useOffline` enabled, failed navigations, RSC fetches, prefetches, and Server Actions are automatically retried once connectivity returns. Direct `fetch()` inside Client Components or client data libraries (SWR, TanStack Query) remain under their own retry policies.

## Reusing data within a request

Identical `fetch` calls in the React component tree are memoized automatically. For non-`fetch` work such as ORM or database queries, wrap the data function with `React.cache` so matching calls within the same request share one result. `React.cache` is request-scoped; it does not share results across requests.

### Preloading without duplicate work

Preloading means starting a request without awaiting it before other blocking work, then calling the same data function where the result is consumed. The function must deduplicate matching calls or the preload and consumer will perform the work twice:

- `fetch`: identical calls are memoized automatically.
- ORM/database work: wrap the function with `React.cache`.
- Cache Components: use `'use cache'`; if the function reads `cookies()` or `headers()`, use `'use cache: private'`.

In production, matching calls to a private Cache Function can reuse one result within a request without storing it in the shared server cache across requests. Keep a preload helper next to the consuming component so its dependency and lifecycle remain visible.

### Security and data access patterns

Choose one approach and avoid mixing them:

1. **External HTTP APIs** — call existing REST/GraphQL endpoints from Server Components using `fetch` with the user's credentials. Good for existing large apps with separate backend teams.
2. **Data Access Layer (DAL)** — create a `server-only` internal library that performs authorization and returns minimal DTOs. Recommended for new projects; centralizes access and reduces accidental data leaks.
3. **Component-level data access** — place database queries directly in Server Components. Fine for prototypes, but easy to accidentally pass full records to Client Components.

### Authentication / authorization rules

- Always authenticate/authorize in Server Actions, Route Handlers, and the DAL — never trust UI gating.
- Use `cookies()` from `next/headers` for session cookies. Set them with `httpOnly`, `secure`, `sameSite`, and `path: '/'`.
- Keep secrets, tokens, and passwords out of client bundles; only `NEXT_PUBLIC_`-prefixed env vars reach the client.
- Use React Taint APIs (`experimental_taintObjectReference`, `experimental_taintUniqueValue`) and/or the `server-only` package to prevent accidental exposure of sensitive data.
- If `authInterrupts` is enabled, throw `unauthorized()` / `forbidden()` from `next/navigation` to render `unauthorized.tsx` / `forbidden.tsx` automatically.

### Session + Client Components

Pass the session promise through context and unwrap with `use()` so a single session read can feed many Client Components without prop drilling. Create the promise inside a `<Suspense>` boundary, not at the top of a layout.

### Auth libraries

Recommended libraries include Auth0, Better Auth, Clerk, Kinde, Logto, NextAuth.js/Auth.js, Ory, Stack Auth, Supabase, Stytch, WorkOS, Iron Session, Jose.

### Passing data from Server to Client Components

- Server and Client Components run in isolated module systems.
- Server Components can access env vars, secrets, and databases safely.
- Client Components must follow browser security assumptions; never pass secrets or full database records to them.
- Sanitize/filter data into DTOs before passing as props.
- Functions and classes are already blocked from crossing to the client by default.

### Tainting

Use React Taint APIs to prevent accidental exposure of sensitive objects or values to the client:

- `experimental_taintObjectReference` for data objects.
- `experimental_taintUniqueValue` for specific values.
- Enable with `experimental.taint: true` in `next.config.js`.

Tainting is an additional safety net, not a substitute for filtering data in your DAL.

### Server-only modules

Mark modules that must never run on the client with `import 'server-only'`:

```ts
import 'server-only'

// This module will cause a build error if imported into a Client Component.
```

Next.js handles `server-only` imports internally. Install the package only if your linting rules require the dependency.

## Detecting and using `next-devtools-mcp` / MCP server (v16+)

Next.js 16+ exposes a built-in MCP endpoint at `/_next/mcp` inside the dev server. The `next-devtools-mcp` package discovers it automatically.

- Add to `.mcp.json`: `npx -y next-devtools-mcp@latest` as a server command.
- Capabilities include `get_errors`, `get_logs`, `get_page_metadata`, `get_project_metadata`, `get_routes`, `get_server_action_by_id`, `get_compilation_issues` (Turbopack), and `compile_route` (Turbopack).
- Use it to let coding agents read version-accurate docs bundled in `node_modules/next/dist/docs/` and inspect the live app state.
- Requires Next.js 16 or above. ([mcp](https://nextjs.org/docs/app/guides/mcp))

## `io()` and `connection()`

`io()` (from `next/cache`) signals that a cached function still needs request-time APIs. It allows the suspended boundary to be prefetched and replaced at request time, while `connection()` (from `next/server`) blocks both prerendering and prefetching. Use `io()` inside `use cache` helper functions to keep runtime code colocated with cached code; use `connection()` only when rendering must wait for a real user request.

## connection() (legacy notes)

`connection()` (from `next/server`) signals that rendering should wait for an incoming user request before continuing. Use it when a component does not use Request-time APIs (`cookies`, `headers`) but still needs per-request output such as `Math.random()` or `new Date()`.

- Type: `function connection(): Promise<void>` — takes no parameters and returns a `void` Promise not meant to be consumed; you `await connection()`.
- It stops prerendering at the call site; code after it runs only at request time.
- Replaces `unstable_noStore`. Only necessary when dynamic rendering is required and common Request-time APIs are not used.
- Synchronous database drivers (e.g. `better-sqlite3`) complete during prerendering; call `connection()` before the query to exclude it (and the rest of the component's output) from prerendering.
- With Cache Components, prefer `io()` (works the same way but can also be cached and prefetched); reach for `connection()` only when rendering must wait for a real user request.
- `connection()` blocks prefetching; `io()` allows prefetching of the suspended boundary.
- When a route must be dynamic because `generateMetadata` or `generateViewport` reads runtime data, add a dynamic marker component that calls `connection()` inside a `<Suspense>` boundary so the static content still prerenders while metadata streams in. ([migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components))
- Reading uncached or runtime data in a `GET` Route Handler bails out of prerendering by throwing; a surrounding `try/catch` may catch that bail-out and log noise. Use `experimental.hideLogsAfterAbort: true` to suppress logs emitted after a bail-out when migrating Route Handlers to Cache Components. ([migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components))
- **Edge Runtime compatibility.** `connection()` is a Node.js runtime API for Server Components; do not call it in the Edge Runtime or Proxy. Use Web-standard request-time APIs and `NextRequest`/`NextResponse` in Proxy instead. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))

## after()

`after` (from `next/server`) schedules a callback to run after the response (or prerender) finishes — useful for non-blocking side effects like logging and analytics.

- Import: `import { after } from 'next/server'`. Usable in Server Components (including `generateMetadata`), Server Functions, Route Handlers, and Proxy.
- Not a Request-time API: calling it does not make a route dynamic. In a static page, the callback runs at build time or on revalidation.
- Timing: runs after the response is sent, and even if the response failed (error thrown, `notFound`, or `redirect`).
- Duration: runs for the platform's default or configured max duration; configure via the `maxDuration` route segment config.
- `React.cache` can deduplicate work inside `after`; `after` calls can be nested.
- Request APIs inside `after`:
  - Route Handlers and Server Functions: `cookies()` and `headers()` may be called directly inside the `after` callback.
  - Server Components (pages, layouts, `generateMetadata`): `cookies()`, `headers()`, and other Request-time APIs are NOT allowed inside `after` (throws a runtime error). Read the request data before `after` and pass the values in via closure.
- With Cache Components: wrap request-data access in `<Suspense>`; read request data in a dynamic component and pass it into `after` (since `cookies()`/`headers()` must run during render, not inside the callback).
- Platform support: Node.js server Yes, Docker container Yes, Static export No, Adapters platform-specific. Serverless relies on a `waitUntil(promise)` primitive (`globalThis[Symbol.for('@next/request-context')]`).
- When self-hosting in serverless contexts, provide a `waitUntil` implementation via `globalThis[Symbol.for('@next/request-context')]`; Next.js accesses it as `RequestContext.get().waitUntil`.
- **Edge Runtime compatibility.** `after()` is available in Proxy per the docs, but the Edge Runtime's limited API surface means code inside `after()` must only use Edge-compatible APIs. It is unavailable in the deprecated `runtime = 'edge'` route rendering context; use Node.js runtime for Server Component `after()` usage.
- Version: `after()` introduced in v15.2.0. ([after](https://nextjs.org/docs/app/api-reference/functions/after))

## draftMode()

`draftMode()` (from `next/headers`) is an **async** function to enable/disable Draft Mode and check whether it is enabled in a Server Component.

- Import: `import { draftMode } from 'next/headers'`; must `await draftMode()`.
- Exposes: `isEnabled` (boolean), `enable()` (sets the `__prerender_bypass` cookie — call in a Route Handler), `disable()` (deletes the cookie — call in a Route Handler).
- Async API: returns a promise; use `async/await` or React's `use`. Synchronous access is still allowed in Next.js 15 for backwards compatibility (deprecated; in v14 and earlier it was synchronous).
- A new bypass cookie value is generated on each `next build` (unguessable).
- Caching implications:
  - `isEnabled` is readable inside a `use cache` directive scope, but `cookies()`/`headers()` are not allowed inside caching directive scopes even when Draft Mode is active.
  - Calling `enable()`/`disable()` inside a caching directive scope throws an error.
  - When Draft Mode is enabled, all functions/components under a caching directive scope re-execute on every request and results are not saved to the cache (draft content is always fresh).
- **Edge Runtime compatibility.** `draftMode()` is a Node.js/Server Component API (`next/headers`) and is not available in the Edge Runtime/Proxy. Use `NextRequest`/`NextResponse` cookies and the `__prerender_bypass` cookie directly only in Node.js runtime contexts. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))

## Draft Mode in the Pages Router

In the Pages Router, Draft Mode is enabled from an API Route via `res.setDraftMode({ enable: true })` on the `NextApiResponse`. This sets the `__prerender_bypass` cookie. Subsequent requests with that cookie cause statically generated pages to render at request time.

- Enable in an API Route: `res.setDraftMode({ enable: true })` sets the bypass cookie. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- Disable: `res.setDraftMode({ enable: false })` clears it. If you link to the disable route with `next/link`, pass `prefetch={false}` so prefetch does not delete the cookie early. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- In `getStaticProps`, `getServerSideProps`, and API Routes, check the draft state with `context.draftMode` / `req.draftMode` (boolean). ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- Do **not** set `Cache-Control` on draft pages; Draft Mode cannot bypass `Cache-Control`. Use ISR instead. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- The bypass cookie value is regenerated on each `next build` to prevent guessing. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))
- Local HTTP testing requires the browser to allow third-party cookies and local storage access. ([draft-mode](https://nextjs.org/docs/pages/guides/draft-mode))

## headers()

`headers()` (from `next/headers`) reads incoming request headers in a Server Component.

- Import: `import { headers } from 'next/headers'`; it is **async** since `v15.0.0-RC` — `await headers()` (or React's `use`). Synchronous access still works in Next.js 15 for backwards compatibility but is deprecated; in v14 and earlier it was synchronous.
- Returns a **read-only** `Headers` object. You cannot `set` or `delete` the outgoing request headers via `headers()`.
- It is a Request-time API, so using it opts the route into **dynamic rendering**.
- With Cache Components, calling `headers()` outside a `<Suspense>` boundary prevents the route from being prerendered (`blocking-prerender-runtime`).
- **Edge Runtime compatibility.** `headers()` is a Node.js/Server Component API (`next/headers`) and is not available in the Edge Runtime/Proxy. In Proxy, read request headers from the `NextRequest` object and set response headers via `NextResponse`/`Response`. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))
([headers](https://nextjs.org/docs/app/api-reference/functions/headers))

## connection()

`connection()` (from `next/headers`) marks that rendering should wait for an incoming user request before continuing. Stabilized in `v15.0.0`; replaced `unstable_noStore`.

- No parameters; returns a `void` Promise not meant to be consumed — `await connection()`.
- Use it when a component does **not** use Request-time APIs (`cookies`, `headers`) but still needs to produce different output per request (e.g. `Math.random()`, `new Date()`, synchronous DB drivers like `better-sqlite3`).
- Calling `connection()` before a synchronous DB query excludes the component (and the rest of its output) from prerendering.
- **vs `io()`** (Cache Components): `io()` suspends so code after it can be wrapped in `"use cache"` and prefetched; `connection()` stays suspended until a real user navigation reaches the server and **blocks** prefetches. Prefer `io()` under Cache Components; reach for `connection()` only when rendering must wait for a real user request.
- **Migrating synchronous-IO build errors:** move `new Date()`, `Date.now()`, `Math.random()`, `crypto.randomUUID()` under `<Suspense>` with `connection()` or `io()` (Cache Components) or into a Client Component. `instant = false` does **not** clear these build errors.
- When `generateMetadata` or `generateViewport` reads runtime data, add a dynamic marker component that calls `connection()` inside a `<Suspense>` boundary so the static content still prerenders while metadata streams in. ([migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components))
- **Edge Runtime compatibility.** `connection()` is a Node.js runtime API for Server Components; do not call it in the Edge Runtime or Proxy. Use Web-standard request-time APIs and `NextRequest`/`NextResponse` in Proxy instead. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))
([connection](https://nextjs.org/docs/app/api-reference/functions/connection))

## io()

`io()` (from `next/cache`) marks that a synchronous IO operation follows so Next.js can keep it out of the static shell during prerendering (Cache Components). Added in `v16.3.0`.

- Import: `import { io } from 'next/cache'`.
- **Server Component:** `await io()` before reading `new Date()`, `Math.random()`, `crypto.randomUUID()`, or a synchronous DB driver such as `node:sqlite`. Wrap the reading component in `<Suspense>`.
- **Client Component:** call `io()` with React's `use` hook — `use(io())` — before reading a synchronous source like `Date.now()` (Client Components prerender on the server during SSR).
- Outside prerendering (real requests, inside `"use cache"` scopes, the browser, `generateStaticParams`, routes without Cache Components) `io()` resolves immediately.
- **When you don't need `io()`:** the component already uses a Request-time API (`cookies()`, `headers()`), or the data comes from an awaited `fetch`/async DB query wrapped in `<Suspense>`.
- `io()` suspends like any async function, so code after it can be wrapped in `"use cache"` and prefetched; `connection()` stays suspended until a real user navigation reaches the server and blocks prefetches. Prefer `io()`; use `connection()` only when you must wait for a real user request.
- **Edge Runtime compatibility.** `io()` is a Node.js/Server Component API (`next/cache`) and is not available in the Edge Runtime/Proxy. Use Web-standard request-time APIs and `NextRequest`/`NextResponse` for request-time edge logic. ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))
([io](https://nextjs.org/docs/app/api-reference/functions/io))

## Source URLs

- Fetching Data: https://nextjs.org/docs/app/getting-started/fetching-data
- Streaming guide: https://nextjs.org/docs/app/guides/streaming
- `fetch` API reference: https://nextjs.org/docs/app/api-reference/functions/fetch
- `loading.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/loading
- React `use` API: https://react.dev/reference/react/use
- React `cache` API: https://react.dev/reference/react/cache
- Client-side data fetching guide: https://nextjs.org/docs/app/guides/client-side-data-fetching
- Data security guide: https://nextjs.org/docs/app/guides/data-security
- `logging` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- `taint` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/taint
- Authentication guide: https://nextjs.org/docs/app/guides/authentication
- Authentication with Cache Components: https://nextjs.org/docs/app/guides/authentication-with-cache-components
- Backend for frontend: https://nextjs.org/docs/app/guides/backend-for-frontend
- Environment variables: https://nextjs.org/docs/app/guides/environment-variables
- How revalidation works: https://nextjs.org/docs/app/guides/how-revalidation-works
- Incremental Static Regeneration (previous model): https://nextjs.org/docs/app/guides/incremental-static-regeneration
- Incremental Static Regeneration with Cache Components: https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components
- Caching without Cache Components: https://nextjs.org/docs/app/guides/caching-without-cache-components
- CDN caching: https://nextjs.org/docs/app/guides/cdn-caching
- SWR guide: https://nextjs.org/docs/app/guides/client-side-data-fetching/swr
- TanStack Query guide: https://nextjs.org/docs/app/guides/client-side-data-fetching/tanstack-query
- Forms: https://nextjs.org/docs/app/guides/forms
- Server Actions: https://nextjs.org/docs/app/guides/server-actions
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- MCP / `next-devtools-mcp`: https://nextjs.org/docs/app/guides/mcp
- `connection`: https://nextjs.org/docs/app/api-reference/functions/connection
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- Instrumentation: https://nextjs.org/docs/app/guides/instrumentation
- `instrumentation` convention: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
- `connection` API reference: https://nextjs.org/docs/app/api-reference/functions/connection
- `after` API reference: https://nextjs.org/docs/app/api-reference/functions/after
- `draftMode` API reference: https://nextjs.org/docs/app/api-reference/functions/draft-mode
- `io` API reference: https://nextjs.org/docs/app/api-reference/functions/io
- `cacheLife` API reference: https://nextjs.org/docs/app/api-reference/functions/cacheLife
- `cacheTag` API reference: https://nextjs.org/docs/app/api-reference/functions/cacheTag
- `revalidateTag` API reference: https://nextjs.org/docs/app/api-reference/functions/revalidateTag
- `updateTag` API reference: https://nextjs.org/docs/app/api-reference/functions/updateTag
- `revalidatePath` API reference: https://nextjs.org/docs/app/api-reference/functions/revalidatePath
- `refresh` API reference: https://nextjs.org/docs/app/api-reference/functions/refresh
- Route Handlers: https://nextjs.org/docs/app/getting-started/route-handlers
- Proxy: https://nextjs.org/docs/app/getting-started/proxy
- Edge Runtime: https://nextjs.org/docs/app/api-reference/edge
- Runtime segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime
- Proxy file convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Web app manifest convention: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary Pages Router additions — Automatic Static Optimization (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/02-rendering/04-automatic-static-optimization.mdx`.

**Automatic Static Optimization rules (Pages Router)**
- Next.js marks a page as static/prerenderable when the page has **no blocking data requirements**, specifically when it lacks `getServerSideProps` and `getInitialProps`. (Source: https://nextjs.org/docs/pages/building-your-application/rendering/automatic-static-optimization)
- Statically optimized pages emit `.next/server/pages/<page>.html`; pages with `getServerSideProps` emit `.next/server/pages/<page>.js`. (Source: above)
- During prerendering, the router's `query` object is empty. After hydration, Next.js updates `query` for dynamic routes, URLs with query values, and rewrites-configured parameters. (Source: above)
- Use `router.isReady` to determine whether `query` has been fully updated after hydration. (Source: above)
- Parameters from dynamic routes are always available in `query` when `getStaticProps` is used. (Source: above)

**Caveats**
- A custom `App` with `getInitialProps` disables Automatic Static Optimization for pages that don't use `getStaticProps`. (Source: above)
- A custom `Document` with `getInitialProps` should check `ctx.req` is defined before assuming server-side rendering; `ctx.req` is `undefined` for prerendered pages. (Source: above)
- Avoid using `router.asPath` in the render tree until `router.isReady` is `true`, to avoid hydration mismatches. (Source: above)

### Canary Pages Router additions — Rendering overview (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/02-rendering/index.mdx`, `01-server-side-rendering.mdx`, `02-static-site-generation.mdx`, and `05-client-side-rendering.mdx`.

**Rendering models (Pages Router)**
- Next.js prerenders every page by default. Two forms: **Static Generation** (HTML generated at build time and reused per request) and **Server-side Rendering** (HTML generated on every request). (Source: https://nextjs.org/docs/pages/building-your-application/rendering)
- Each generated HTML is paired with the minimal JavaScript needed for that page; on load, React hydrates it. (Source: above)
- Static Generation is preferred for performance; Server-side Rendering is used when page content must be generated per request. (Source: above)

**Static Site Generation (SSG)**
- Use `getStaticProps` when page content depends on external data available at build time (e.g., headless CMS, SEO pages). (Source: https://nextjs.org/docs/pages/building-your-application/rendering/static-site-generation)
- Use `getStaticPaths` when dynamic route paths depend on external data. (Source: above)
- Static pages can be cached by a CDN. Good fit: marketing pages, blogs, portfolios, e-commerce listings, docs. (Source: above)
- If content changes frequently, either fetch client-side after Static Generation or use Server-side Rendering. (Source: above)

**Client-side Rendering (CSR) in Pages Router**
- Implement CSR with React `useEffect` (not recommended for production) or a data-fetching library such as SWR or TanStack Query. (Source: https://nextjs.org/docs/pages/building-your-application/rendering/client-side-rendering)
- CSR can impact SEO because some crawlers do not execute JavaScript, and it can degrade performance on slow devices/connections. Next.js recommends a hybrid approach. (Source: above)

### Canary Pages Router additions — Custom App / Document / Error pages (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/01-routing/05-custom-app.mdx`, `06-custom-document.mdx`, and `08-custom-error.mdx`.

**Custom App (`pages/_app`)**
- Override the default `App` to control page initialization, inject shared layout/data, and add global CSS. Create `pages/_app.{js,jsx,ts,tsx}`. (Source: https://nextjs.org/docs/pages/building-your-application/routing/custom-app)
- `Component` is the active page; `pageProps` are the initial props preloaded by data-fetching methods (or `{}`). (Source: above)
- Restart the dev server if a custom `App` is added where one didn't exist before. (Source: above)
- `App` does **not** support `getStaticProps` or `getServerSideProps`. (Source: above)
- Using `getInitialProps` in `App` disables Automatic Static Optimization for pages without `getStaticProps`. This pattern is not recommended; prefer App Router for page/layout data fetching. (Source: above)

**Custom Document (`pages/_document`)**
- Override the default document markup by creating `pages/_document.{js,jsx,ts,tsx}`. Use it to update `<html>` and `<body>` tags for all pages. (Source: https://nextjs.org/docs/pages/building-your-application/routing/custom-document)
- Required imports: `Html`, `Head`, `Main`, `NextScript` from `next/document`. (Source: above)
- `_document` is only rendered on the server; event handlers like `onClick` cannot be used. (Source: above)
- The `Head` component in `_document` is not the same as `next/head`; use it only for common `<head>` code. For per-page `<title>`/metadata, use `next/head`. (Source: above)
- Do not place application logic or custom CSS outside `<Main />`; components there will not be initialized by the browser. (Source: above)
- `Document` does not support `getStaticProps` or `getServerSideProps`. (Source: above)
- Customizing `renderPage` is advanced and mainly needed for CSS-in-JS server-side rendering. (Source: above)

**Custom error pages**
- Next.js provides static `404` and `500` pages by default. Custom versions are created as `pages/404.{js,jsx,ts,tsx}` and `pages/500.{js,jsx,ts,tsx}`, statically generated at build time. (Source: https://nextjs.org/docs/pages/building-your-application/routing/custom-error)
- You may use `getStaticProps` inside `pages/404` and `pages/500` if build-time data is needed. (Source: above)
- To override the shared `Error` component, create `pages/_error.{js,jsx,ts,tsx}`. It is used only in production (dev overlay in development). (Source: above)
- `Error.getInitialProps = ({ res, err }) => { ... }` returns `{ statusCode }`. (Source: above)
- The built-in error component can be imported from `next/error` and accepts `statusCode` and optional `title`. (Source: above)
- `_error` is a reserved pathname; accessing `/_error` directly renders a 404. (Source: above)

### Canary Pages Router additions — Linking and Navigating (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/01-routing/03-linking-and-navigating.mdx`.

**`<Link>` prefetch in Pages Router**
- Any `<Link />` in the viewport is prefetched by default, including corresponding data for statically generated pages. For server-rendered routes, data is fetched only when the link is clicked. (Source: https://nextjs.org/docs/pages/building-your-application/routing/linking-and-navigating)
- Use interpolation or a URL object (`{ pathname, query }`) for dynamic paths. Encode dynamic values with `encodeURIComponent` when interpolating. (Source: above)

**Shallow routing**
- Shallow routing changes the URL without re-running data-fetching methods (`getServerSideProps`, `getStaticProps`, `getInitialProps`). (Source: above)
- Use `router.push('/?counter=10', undefined, { shallow: true })`. (Source: above)
- Shallow routing only works for URL changes within the **current page**; navigating to a different page ignores the shallow flag. (Source: above)
- With Proxy, shallow routing does **not** verify that the new page matches the current page client-side; treat every shallow route as shallow. (Source: above)

### Canary Pages Router additions — API Routes (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/01-routing/07-api-routes.mdx`.

**API Routes (Pages Router)**
- Any file in `pages/api` maps to `/api/*` and is treated as a server-only API endpoint; it does not add to the client bundle. (Source: https://nextjs.org/docs/pages/building-your-application/routing/api-routes)
- Handler signature: `export default function handler(req: NextApiRequest, res: NextApiResponse)`. (Source: above)
- API routes do **not** set CORS headers by default (same-origin only); customize with CORS helpers if needed. (Source: above)
- API routes cannot be used with `output: 'export'`; use App Router Route Handlers instead for static export. (Source: above)
- API routes are affected by the `pageExtensions` config. (Source: above)

**Request helpers**
- `req.cookies` — cookies sent by the request (default `{}`). (Source: above)
- `req.query` — query string object (default `{}`). (Source: above)
- `req.body` — parsed body by content-type, or `null` if no body (default). (Source: above)

**Per-route config (`export const config`)**
- `api.bodyParser` — automatically enabled; set to `false` to consume body as a stream or with `raw-body`. `sizeLimit` supports `bytes` formats (default `1mb`). (Source: above)
- `api.externalResolver` — set to `true` when the route is handled by an external resolver (e.g., Express/Connect) to disable unresolved-request warnings. (Source: above)
- `api.responseLimit` — warns when response body exceeds 4 MB; set to `false` (or a custom size/bytes string) to disable/raise. (Source: above)
- `maxDuration` — maximum allowed duration for the function in seconds. (Source: above)

**Response helpers**
- `res.status(code)` — set status code. (Source: above)
- `res.json(body)` — send JSON response (body must be serializable). (Source: above)
- `res.send(body)` — send string, object, or `Buffer`. (Source: above)
- `res.redirect([status,] path)` — redirect; default status 307. (Source: above)
- `res.revalidate(urlPath)` — on-demand revalidation of a page using `getStaticProps`. (Source: above)

### Canary Pages Router additions — Pages and Layouts (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/01-routing/01-pages-and-layouts.mdx` and `02-dynamic-routes.mdx`.

**Pages Router routing basics**
- The Pages Router is file-system based: files in `pages/` become routes. (Source: https://nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts)
- A page is a React component exported from `.js`, `.jsx`, `.ts`, or `.tsx` inside `pages/`. (Source: above)
- Index routes: `pages/index.js` → `/`, `pages/blog/index.js` → `/blog`. (Source: above)
- Nested routes mirror the folder structure: `pages/blog/first-post.js` → `/blog/first-post`. (Source: above)

**Dynamic routes**
- Dynamic segment: `[segmentName]` (e.g., `pages/posts/[id].js`). (Source: https://nextjs.org/docs/pages/building-your-application/routing/dynamic-routes)
- Catch-all: `[...segmentName]` matches one or more segments (e.g., `/shop/a/b/c`). (Source: above)
- Optional catch-all: `[[...segmentName]]` also matches the path without the parameter (e.g., `/shop` with no slug). (Source: above)
- Access dynamic segments via `useRouter().query` (or `router.query`). (Source: above)

**Layout pattern in Pages Router**
- Layouts are not a built-in file convention; compose shared UI via components. (Source: https://nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts)
- For a single shared layout, wrap the app in `pages/_app.js`. (Source: above)
- For per-page layouts, attach a `getLayout` property to the page component and consume it in `_app.js`: `Component.getLayout ?? (page => page)`. (Source: above)
- This pattern preserves component state across navigation (e.g., input values, scroll position) because the React tree is maintained. (Source: above)

### Canary Pages Router additions — API reference: data-fetching functions (ingest 2026-09-02)

Sourced from `docs/02-pages/04-api-reference/03-functions/get-initial-props.mdx`, `get-static-props.mdx`, `get-static-paths.mdx`, `get-server-side-props.mdx`, `use-params.mdx`, and `use-router.mdx`.

**`getInitialProps` (legacy)**
- `getInitialProps` is a legacy Pages Router API. Prefer `getStaticProps` or `getServerSideProps` for new code. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-initial-props)
- Attach it to the page's default export: `Page.getInitialProps = async (ctx) => { ... }`. It runs server-side on the initial load and again client-side during page transitions via `next/link` or `next/router`. (Source: above)
- The returned object is serialized and forwarded as props; it must be a plain object (no `Date`, `Map`, or `Set`). (Source: above)
- If a custom `App` uses `getInitialProps` and the destination page uses `getServerSideProps`, `getInitialProps` runs **only** on the server. (Source: above)
- `ctx` provides: `pathname`, `query`, `asPath`, `req` (server only), `res` (server only), `err`. (Source: above)
- Use only in top-level `pages/` files; nested components cannot use it. Do not pass secrets in returned props because they reach the client HTML. (Source: above)

**`getStaticProps`**
- Export `getStaticProps` from a page to prerender it at build time with the returned props. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-static-props)
- Top-level imports used inside `getStaticProps` are **not bundled for the client**; server-only code (DB queries, file system) can run there. (Source: above)
- Return shape: `{ props: <serializable object> }`, optionally with `revalidate`, `notFound`, or `redirect`. (Source: above)
- `revalidate` (seconds) enables ISR. `false` means no revalidation. (Source: above)
- `x-nextjs-cache` header values: `MISS`, `STALE`, `HIT`. (Source: above)
- `redirect` accepts `{ destination, permanent, basePath?, statusCode? }`; use `statusCode` instead of `permanent`, not both. (Source: above)
- `notFound: true` returns 404; it follows the same `revalidate` behavior. (Source: above)
- Read files with `process.cwd()`, not `__dirname`, because Next.js compiles code into a different directory. (Source: above)

**`getStaticPaths`**
- Required for dynamic routes that use `getStaticProps`; determines which paths are prerendered. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-static-paths)
- Return `{ paths: [ { params: {...}, locale? }, ... ], fallback: false | true | 'blocking' }`. (Source: above)
- `params` keys must match the route segments; for catch-all routes use an array (`slug: ['a','b']`), and for optional catch-all use `null`, `[]`, `undefined`, or `false` for the root-most route. (Source: above)
- `fallback: false` → unknown paths 404. `fallback: true` → serve a fallback on first request, then generate statically in the background; client-side navigations behave like `'blocking'`. `fallback: 'blocking'` → SSR on first request, then cache. (Source: above)
- `fallback: true` and `fallback: 'blocking'` are **not supported** with `output: 'export'`. (Source: above)
- In fallback mode, `router.isFallback` is `true` while the fallback renders. (Source: above)

**`getServerSideProps`**
- Export `getServerSideProps` to render the page on each request. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-server-side-props)
- Top-level imports used inside are server-only. (Source: above)
- `context` includes: `params`, `req` (with `cookies`), `res`, `query`, `preview` (deprecated), `previewData` (deprecated), `draftMode`, `resolvedUrl`, `locale`, `locales`, `defaultLocale`. (Source: above)
- Return `{ props }`, `{ notFound: true }`, or `{ redirect: { destination, permanent?, statusCode? } }`; do not combine `permanent` and `statusCode`. (Source: above)

**`useParams` (Pages Router)**
- `useParams` from `next/navigation` works in both Pages and App Routers. In Pages Router it may return `null` during prerendering/static optimization and update after hydration; always guard with a fallback to avoid hydration mismatches. (Source: https://nextjs.org/docs/pages/api-reference/functions/use-params)
- It returns only dynamic route parameters; use `useRouter().query` to include query-string parameters too. (Source: above)

**`useSearchParams` (Pages Router)**
- `useSearchParams` from `next/navigation` works in both Pages and App Routers. It returns a read-only `URLSearchParams` interface, or `null` during prerendering/static optimization; guard with a fallback to avoid hydration mismatches. (Source: https://nextjs.org/docs/pages/api-reference/functions/use-search-params)
- With `getServerSideProps`, search params are available immediately. (Source: above)

**`userAgent` (Pages Router / shared)**
- `userAgent(request)` from `next/server` parses the user agent; it is a server helper used in Proxy/Route Handlers/API routes, not a client hook. (Source: https://nextjs.org/docs/pages/api-reference/functions/userAgent)

**`NextRequest` / `NextResponse`**
- These are shared with the App Router; Pages Router docs only source from App Router content. See the App Router reference for `nextUrl`, cookie helpers, redirects, rewrites, and middleware/proxy usage. (Source: https://nextjs.org/docs/pages/api-reference/functions/next-request, https://nextjs.org/docs/pages/api-reference/functions/next-response)

**`catchError`**
- `catchError` is documented in the App Router; no Pages Router-specific semantics in the canary source.

**`useRouter` (Pages Router)**
- Import from `next/router` (or `next/compat/router` for components shared with App Router). (Source: https://nextjs.org/docs/pages/api-reference/functions/use-router)
- Router object: `pathname`, `query`, `asPath`, `isFallback`, `basePath`, `locale`, `locales`, `defaultLocale`, `domainLocales`, `isReady`, `isPreview`. (Source: above)
- `router.push(url, as?, options?)` / `router.replace(...)` support `scroll`, `shallow`, and `locale` options. (Source: above)
- `router.prefetch(url, as?, options?)` is production-only. (Source: above)
- `router.beforePopState(cb)` runs before the router handles `popstate`; return `false` to handle it manually. (Source: above)
- `router.events`: `routeChangeStart`, `routeChangeComplete`, `routeChangeError`, `beforeHistoryChange`, `hashChangeStart`, `hashChangeComplete`. Subscribe in `useEffect`/`componentDidMount` and unsubscribe on unmount. (Source: above)
- `next/compat/router` returns `NextRouter | null`, allowing shared components. Once no longer used in `pages/`, remove compat code. (Source: above)
- `withRouter` provides the same router object as a prop for class components. (Source: above)
- `router.push`, `router.replace`, and `router.prefetch` return Promises; handle floating-promises ESLint rules with `void`, `await`, or per-line disables (not needed in `onClick` handlers). (Source: above)

### Canary Pages Router additions — Upgrading guides (ingest 2026-09-02)

Sourced from `docs/02-pages/02-guides/upgrading/index.mdx`, `version-9.mdx`, `version-10.mdx`, `version-11.mdx`, `version-12.mdx`, and `version-13.mdx`.

**Version 9 → 10**
- No breaking changes between v9 and v10. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-10)

**Version 10 → 11**
- Upgrade: `next@11 react@17 react-dom@17`. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-11)
- Webpack 5 is the default. (Source: above)
- `distDir` is now cleaned by default except for Next.js caches; disable with `cleanDistDir: false`. (Source: above)
- `PORT` env var is supported for `next dev` / `next start`. (Source: above)
- Static image imports via `next/image` rely on built-in processing; remove `next-images` / `next-optimized-images` or disable with `images.disableStaticImages`. (Source: above)
- Remove `super.componentDidCatch()` and `Container` from `_app`. (Source: above)
- Remove `props.url` from page components. (Source: above)
- Remove `unsized` prop from `next/image`; use `layout="fill"`. (Source: above)
- Remove `modules`/`render` options from `next/dynamic`. (Source: above)
- Remove `Head.rewind`. (Source: above)
- Moment.js locales excluded by default; opt out with `excludeDefaultMomentLocales: false`. (Source: above)
- `router.events` is no longer provided during prerendering; access it inside `useEffect`. (Source: above)
- React 17 brings the new JSX transform; minimum React version becomes 17.0.2. (Source: above)

**Version 11 → 12**
- Upgrade: `next@12 react@17 react-dom@17 eslint-config-next@12`. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-12)
- Minimum Node.js version bumped from `12.0.0` to `12.22.0`. (Source: above)
- SWC replaces Babel by default; custom `.babelrc` opts out of SWC. (Source: above)
- Opt in to SWC minification with `swcMinify: true` (default in v12.1). (Source: above)
- `next/image` now wraps `<img>` in a `<span>`; update CSS selectors accordingly. (Source: above)
- HMR connection switched from server-sent events to WebSocket; proxy configurations must forward `/_next/webpack-hmr` (renamed to `/_next/hmr` in Next.js 16). (Source: above)
- Webpack 4 support removed. (Source: above)
- `target` option deprecated in favor of output file tracing. (Source: above)

**Version 12 → 13**
- Upgrade: `next@13 react@latest react-dom@latest eslint-config-next@13`. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-13)
- Supported browsers drop IE; target modern browsers. (Source: above)
- Minimum Node.js bumped to `16.14.0`; minimum React to `18.2.0`. (Source: above)
- `swcMinify` defaults to `true`. (Source: above)
- `next/image` → `next/legacy/image`; `next/future/image` → `next/image`. Codemods available. (Source: above)
- `<Link>` no longer requires an `<a>` child; use `legacyBehavior` to keep old behavior. (Source: above)
- `target` config removed; replaced by Output File Tracing. (Source: above)
- The `app` directory is introduced, but migrating to it is optional. (Source: above)
- Updated `<Image/>`, `<Link>`, `<Script>`, and `next/font` work in both routers. (Source: above)
