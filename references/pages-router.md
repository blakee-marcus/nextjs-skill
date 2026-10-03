# Pages Router

Reference: https://nextjs.org/docs/pages/building-your-application/routing/api-routes

Operational details for the Pages Router (`pages/`). The App Router is the preferred router; this reference covers legacy patterns that still appear in existing projects.

## API Routes

Pages Router API Routes live under `pages/api/` and map to `/api/*`. They are **server-side only** and do not add to the client bundle.

```ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({ message: 'Hello' })
}
```

### Request helpers (`req`)

- `req.cookies` — object containing request cookies; defaults to `{}`.
- `req.query` — object containing the query string; defaults to `{}`.
- `req.body` — body parsed by content-type, or `null` if no body sent. Parsing is automatic.

### Response helpers (`res`)

- `res.status(code)` — sets HTTP status code.
- `res.json(body)` — sends JSON response.
- `res.send(body)` — sends response (string, object, or Buffer).
- `res.redirect([status,] path)` — redirects; defaults to `307` if no status given.
- `res.revalidate(urlPath)` — on-demand ISR revalidation for `getStaticProps` pages.

### Custom config

Export a `config` object from an API Route to change defaults:

```js
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '1mb',
    },
  },
  maxDuration: 5,
}
```

- `bodyParser` is automatically enabled. Set to `false` to consume the body as a Stream (e.g., for webhook verification).
- `bodyParser.sizeLimit` — max parsed body size. Default not specified; use bytes string (`'500kb'`, `'3mb'`).
- `externalResolver: true` — explicit flag telling Next.js this route is handled by an external resolver (express/connect); disables unresolved-request warnings.
- `responseLimit` — warns when response body exceeds 4MB. Set to `false` to disable (only if not serverless). Can take byte count or string (`'8mb'`).

### Dynamic API Routes

Follow the same file naming conventions as `pages/`:

- `pages/api/post/[pid].js` — `req.query.pid`
- `pages/api/post/[...slug].js` — catch-all; `req.query.slug` is always an array (`["a", "b"]`)
- `pages/api/post/[[...slug]].js]` — optional catch-all; also matches `/api/post`

**Route precedence:** predefined > dynamic > catch-all. `pages/api/post/create.js` matches `/api/post/create` before `pages/api/post/[pid].js`.

### Constraints

- API Routes are **same-origin only** by default (no CORS headers emitted).
- Cannot be used with `output: 'export'` (static exports). App Router Route Handlers can.
- Affected by `pageExtensions` config.
- Streaming is supported via `res.writeHead` + `res.write`, but App Router Route Handlers are recommended for new streaming use cases.

## Error Boundaries (Pages Router)

For client-side error handling in the Pages Router, create a class-based `ErrorBoundary` and wrap the `Component` prop in `pages/_app.js`:

```jsx
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError(error) {
    return { hasError: true }
  }
  componentDidCatch(error, errorInfo) {
    console.log({ error, errorInfo })
  }
  render() {
    if (this.state.hasError) {
      return <div>Something went wrong.</div>
    }
    return this.props.children
  }
}

// In pages/_app.js
function MyApp({ Component, pageProps }) {
  return (
    <ErrorBoundary>
      <Component {...pageProps} />
    </ErrorBoundary>
  )
}
```

## Custom App (`pages/_app`)

- Override to control page initialization, inject shared layout/data, add global CSS.
- `App` does **not** support `getStaticProps` or `getServerSideProps`.
- Using `getInitialProps` in `App` disables Automatic Static Optimization for pages without `getStaticProps`. Not recommended; prefer App Router for page/layout data fetching.
- Restart dev server if adding `pages/_app.js` to an existing app.

## Custom Document (`pages/_document`)

- Override to update `<html>` and `<body>` tags for all pages.
- Required components: `<Html>`, `<Head />`, `<Main />`, `<NextScript />`.
- The `<Head />` in `_document` is **not** the same as `next/head`. Use it only for `<head>` code common to all pages.
- Event handlers (e.g., `onClick`) cannot be used — `_document` only renders on the server.
- `Document` does not support `getStaticProps` or `getServerSideProps`.
- Customizing `renderPage` is advanced and only needed for CSS-in-JS SSR support.

## Custom Error Pages

- `pages/404.js` — statically generated at build time. Can use `getStaticProps`.
- `pages/500.js` — statically generated at build time. Can use `getStaticProps`.
- `pages/_error.js` — overrides the `Error` component for both client and server errors. Only used in production; dev shows the error overlay. Receives `statusCode`.
- The default 404/500 pages follow OS color scheme via `prefers-color-scheme` and do not read app-level theme. Custom files let global styles/theme apply.

## Automatic Static Optimization

Next.js marks a page as static/prerenderable when it has **no blocking data requirements** — specifically, when it lacks `getServerSideProps` and `getInitialProps`.

- Static pages emit `.next/server/pages/<page>.html`; SSR pages emit `.next/server/pages/<page>.js`.
- Pure Automatic Static Optimization output is not an ISR/prerender cache entry and cannot be revalidated on demand. `res.revalidate()` applies to Pages Router pages backed by `getStaticProps`/ISR.
- A custom `App` with `getInitialProps` disables this optimization for pages without `getStaticProps`.
- After hydration, `query` is updated for dynamic routes, query values, and rewrites. Use `router.isReady` to check.

## Client-side Data Fetching

- Use when SEO indexing is not required, data is not prerendered, or content updates frequently.
- **SWR** (swr.vercel.app) is the recommended React Hook library for client-side fetching — handles caching, revalidation, focus tracking, and refetching.
- `useEffect` + `fetch` works but requires manual loading/error state management.

## Pages Router `useRouter` — additional methods and fields

- `router.back()` — navigates back in history (`window.history.back()`). Equivalent to the browser back button.
- `router.reload()` — reloads the current URL (`window.location.reload()`). Equivalent to the browser refresh button.
- `router.domainLocales` — array of configured domain locales (`{ domain, defaultLocale, locales }`).
- `routeChangeError` event: the error object includes `err.cancelled` (`true` when navigation was cancelled, e.g., two rapid link clicks).
- **State is not reset on same-page navigation** — React does not unmount unless the parent changes. To reset: `useEffect(() => setCount(0), [router.query.slug])` or wrap with `<Component key={router.asPath} />` in `_app`.
- **URL object usage**: `router.push({ pathname: '/post/[pid]', query: { pid: post.id } })`. Omitting `pathname` applies the query to `asPath` instead of `router.pathname`, preserving rewrites. (Source: https://nextjs.org/docs/pages/api-reference/functions/use-router)

## `getStaticProps` — additional context and return details

- `context.revalidateReason` — one of `"build"` (initial build), `"stale"` (revalidate period expired / dev mode), `"on-demand"` (triggered via `revalidatePath`).
- `redirect` accepts `{ destination, permanent?, basePath?, statusCode? }`. Use `statusCode` **instead of** `permanent`, not both. Set `basePath: false` to opt out of basePath prefixing. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-static-props)

## `getStaticPaths` — additional details

- `params` strings are **case-sensitive** — normalize to avoid missed matches.
- For catch-all routes use an array (`slug: ['a','b']`); for optional catch-all use `null`, `[]`, `undefined`, or `false`.
- `fallback: true` and `fallback: 'blocking'` are **not supported** with `output: 'export'`.
- Web crawlers (e.g. Google) are **not** served fallback pages — they see `fallback: 'blocking'` behavior.
- Client-side navigations behave like `fallback: 'blocking'` (no fallback page). (Source: https://nextjs.org/docs/pages/api-reference/functions/get-static-paths)

## `getServerSideProps` — full context fields

- `context` includes: `params`, `req` (with `cookies`), `res`, `query`, `preview` (deprecated), `previewData` (deprecated), `draftMode`, `resolvedUrl`, `locale`, `locales`, `defaultLocale`.
- Return `{ props }`, `{ notFound: true }`, or `{ redirect: { destination, permanent?, statusCode? } }`. Do **not** combine `permanent` and `statusCode`. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-server-side-props)

## `getInitialProps` (legacy) — additional details

- `ctx` fields: `pathname`, `query`, `asPath`, `req` (server only), `res` (server only), `err`.
- Returned object must be a plain serializable `Object` — no `Date`, `Map`, or `Set`.
- If a custom `App` uses `getInitialProps` and the destination page uses `getServerSideProps`, `getInitialProps` runs **only** on the server.
- Only usable in top-level `pages/` files — nested components cannot use it. Returned props reach client HTML; never pass secrets. (Source: https://nextjs.org/docs/pages/api-reference/functions/get-initial-props)

## `useParams` (Pages Router) — additional details

- Returns `null` during prerendering/static optimization; updates after hydration. Always guard with a fallback to avoid hydration mismatches.
- Returns **only** dynamic route parameters. Use `useRouter().query` to include query-string parameters too. (Source: https://nextjs.org/docs/pages/api-reference/functions/use-params)

## `useSearchParams` (Pages Router) — additional details

- Returns a **read-only** `URLSearchParams` interface, or `null` during prerendering/static optimization. Guard with a fallback to avoid hydration mismatches.
- With `getServerSideProps`, search params are available immediately (no null phase). (Source: https://nextjs.org/docs/pages/api-reference/functions/use-search-params)

## `userAgent` (Pages Router / shared)

- `userAgent(request)` from `next/server` parses the user agent. It is a **server helper** used in Proxy/Route Handlers/API routes, not a client hook. (Source: https://nextjs.org/docs/pages/api-reference/functions/userAgent)

## `NextRequest` / `NextResponse`

- Shared with the App Router; Pages Router docs derive from App Router content. See the App Router reference for `nextUrl`, cookie helpers, redirects, rewrites, and Proxy usage. (Source: https://nextjs.org/docs/pages/api-reference/functions/next-request, https://nextjs.org/docs/pages/api-reference/functions/next-response)

## Source URLs

- API Routes: https://nextjs.org/docs/pages/building-your-application/routing/api-routes
- Custom App: https://nextjs.org/docs/pages/building-your-application/routing/custom-app
- Custom Document: https://nextjs.org/docs/pages/building-your-application/routing/custom-document
- Custom Error: https://nextjs.org/docs/pages/building-your-application/routing/custom-error
- Dynamic Routes: https://nextjs.org/docs/pages/building-your-application/routing/dynamic-routes
- Pages and Layouts: https://nextjs.org/docs/pages/building-your-application/routing/pages-and-layouts
- Automatic Static Optimization: https://nextjs.org/docs/pages/building-your-application/rendering/automatic-static-optimization
- Static Site Generation: https://nextjs.org/docs/pages/building-your-application/rendering/static-site-generation
- Server-side Rendering: https://nextjs.org/docs/pages/building-your-application/rendering/server-side-rendering
- Client-side Rendering: https://nextjs.org/docs/pages/building-your-application/rendering/client-side-rendering
- Error Handling: https://nextjs.org/docs/pages/building-your-application/configuring/error-handling
- getStaticProps: https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-props
- getStaticPaths: https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-paths
- getServerSideProps: https://nextjs.org/docs/pages/building-your-application/data-fetching/get-server-side-props
- Client-side Fetching: https://nextjs.org/docs/pages/building-your-application/data-fetching/client-side
