# App Router

Reference: https://nextjs.org/docs/app

The **App Router** is Next.js's file-system based router. It uses React features including [Server Components](../server-client-components.md), [Suspense](../data-fetching-and-streaming.md), and [Server Functions](../mutations-and-server-actions.md).

## Project structure

- `app/` — App Router root (may live under an optional `src/` folder).
- `pages/` — Pages Router root (legacy; handled when present).
- `src/` optional wrapper: `src/app/` and `src/pages/` are valid.
- `public/` — static assets served at root path.
- `next.config.*` — Next.js configuration (JS, MJS, TS).
- Top-level convention files: `proxy.ts` (request proxy), `instrumentation.ts` (OpenTelemetry / instrumentation).
- Standard root files: `package.json`, `tsconfig.json` / `jsconfig.json`, `next-env.d.ts`, `eslint.config.mjs`, `.env*` files, `.gitignore`.

## File conventions in `app/`

| File | Purpose |
|---|---|
| `layout.tsx` | Shared UI for a segment and its children; preserves state across navigation. |
| `page.tsx` | Public page for a route segment. |
| `loading.tsx` | Loading UI; wraps the segment in `Suspense`. |
| `error.tsx` | Error boundary; must be a Client Component. |
| `global-error.tsx` | Root-level error UI; must include `<html>` and `<body>`. |
| `forbidden.tsx` | UI shown when `forbidden()` is called (requires `authInterrupts`). Introduced v15.1.0. |
| `not-found.tsx` | UI shown when `notFound()` is called. Streamed `200` + `noindex`; non-streamed `404`. Root `app/not-found` catches unmatched URLs. Experimental `global-not-found` (v15.4.0) bypasses layout, requires full `<html>`/`<body>`. |
| `unauthorized.tsx` | UI shown when `unauthorized()` is called (requires `authInterrupts`). Introduced v15.1.0. |
| `route.ts` | Route handler for API endpoints. |
| `template.tsx` | Re-rendered layout-like wrapper. |
| `default.tsx` | Parallel route fallback when a slot has no matching active state on hard navigation. For named slots, missing `default.tsx` errors; for the implicit `children` slot, missing `default.tsx` returns a 404. Can call `notFound()` to preserve old 404 behavior. Receives `params` as a promise. |
| `instrumentation.js|ts` | Server-side observability hook (register + onRequestError). |
| `instrumentation-client.js|ts` | Client-side instrumentation/prefetch observation hook. |
| `mdx-components.js|tsx` | Required for App Router MDX support via `@next/mdx`. |
| `global-not-found.js` | App-wide 404 page for unmatched routes (experimental; `globalNotFound` flag). |

### Special file extensions

- `layout`, `page`, `error`, `not-found`, `global-error`, `template`, `loading`, `default`, `forbidden`, `unauthorized`: `.js`, `.jsx`, `.tsx`.
- `route`: `.js`, `.ts`.
- `instrumentation-client`: `.js`, `.ts`.

## Component hierarchy

Within a segment, special files render in this order:

1. `layout.tsx`
2. `template.tsx`
3. `error.tsx` (React error boundary)
4. `loading.tsx` (React `Suspense` boundary)
5. `not-found.tsx` (React error boundary for 404 UI)
6. `page.tsx` or a nested `layout.tsx`

These components render recursively, so a child segment's UI is nested inside its parent's UI.

## Colocation and private folders

- Folders in `app/` define route segments, but a segment only becomes publicly accessible when it contains a `page` or `route` file.
- When a route is public, only the content returned by that `page` or `route` file is sent to the client; other project files colocated in the same folder are not routable.
- Prefix a folder with an underscore (`_folder`) to guarantee it is not routable, which is useful for separating UI logic from routing logic and avoiding future naming conflicts.
- To create a URL segment that literally starts with an underscore, URL-encode the underscore in the folder name: `%5Ffolder`.
- Folder names like `components`, `lib`, `ui`, `utils`, `hooks`, and `styles` have no special framework meaning in Next.js; they are ordinary project organization choices.
- Next.js is unopinionated about colocation strategy; preserve the project's existing organization unless there is a concrete reason to change it.

## Routing rules

- Folders define URL segments; files define UI or handlers.
- A route becomes public only when a `page` or `route` file exists.
- `app/layout.tsx` is the root layout and **must** contain `<html>` and `<body>`.
- Nested layouts wrap children automatically via the `children` prop.
- Route groups `(group)` omit the group name from the URL.
- Private folders `_folder` are not routable; safe for co-located components/utils.

### Dynamic segments

| Pattern | URL example | `params` shape |
|---|---|---|
| `[slug]` | `/blog/post-1` | `Promise<{ slug: string }>` |
| `[...slug]` | `/shop/a/b` | `Promise<{ slug: string[] }>` |
| `[[...slug]]` | `/docs` or `/docs/a` | `Promise<{ slug?: string[] }>` |

In Next.js 15+, `params` is a **promise** — `await` it before use. `searchParams` is also a promise and opts the page into dynamic rendering.

Dynamic segments can be prerendered at build time by exporting `generateStaticParams` from a `page.tsx` file. If a dynamic segment could be prerendered but is missing `generateStaticParams`, it falls back to dynamic rendering at request time.

### Catch-all URL patterns

| Path | URL pattern |
|---|---|
| `app/blog/[slug]/page.tsx` | `/blog/my-first-post` |
| `app/shop/[...slug]/page.tsx` | `/shop/clothing`, `/shop/clothing/shirts` |
| `app/docs/[[...slug]]/page.tsx` | `/docs`, `/docs/layouts-and-pages`, `/docs/api-reference/use-router` |

### Dynamic segments and `generateStaticParams`

Ensure dynamic segments that can be prerendered export `generateStaticParams`:

```tsx
export async function generateStaticParams() {
  const posts = await fetch('https://.../posts').then((res) => res.json())
  return posts.map((post) => ({ slug: post.slug }))
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  // ...
}
```

With Cache Components enabled and **without** `generateStaticParams`, dynamic segment params are runtime data. You must wrap param access in `<Suspense>` boundaries so the static shell can be prerendered. In layouts, avoid awaiting `params` at the top level; pass the promise down and await it in the component that needs it.

With `generateStaticParams`, the build validates sample params, generates static HTML for them, and saves runtime-param renders to disk after the first successful request. Build-time validation only covers code paths executed with the sample params; branches guarded by runtime values are not validated.

Under **Cache Components**, `generateStaticParams` must return **at least one** param — an empty array is a **build error** (it blocks validation that the route doesn't touch `cookies()`/`headers()`/`searchParams` at runtime). If real values aren't known at build time, return a placeholder (e.g. `[{ slug: '__placeholder__' }]`) and call `notFound()` in the page, though this weakens build-time validation. ([generate-static-params](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-static-params.mdx))

**Multiple dynamic segments.** A segment's `generateStaticParams` can generate params for segments **at or above** it, never below — `app/[category]/layout.js` can only generate `[category]`. A child segment's `generateStaticParams` runs **once per parent param set** and receives the parent's populated `params`, so you can build sub-segments bottom-up (generate all combinations in the leaf) or top-down (each level generates its own).

**Route Handlers.** `generateStaticParams` also works in `route.ts`/`route.js` to statically generate API responses at build time — not just pages and layouts.

**Lifecycle.** In `next dev` it runs when you navigate to the route; in `next build` it runs **before** the corresponding Layouts/Pages are generated; during ISR revalidation it is **not** called again. It replaces the Pages Router's `getStaticPaths`. See `references/caching-and-revalidation.md` for the Cache Components requirement that it return at least one param.

Always return an **array** from `generateStaticParams` (even if empty) — a non-array return makes the route render dynamically. To serve all paths at runtime, return an empty array **or** `export const dynamic = 'force-static'`; combine with `export const dynamicParams = false` so unspecified paths 404 (catch-all routes may instead match). ([generate-static-params](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-static-params.mdx))
([generate-static-params](https://nextjs.org/docs/app/api-reference/functions/generate-static-params))

## Root parameters (`next/root-params`)

Dynamic segments that appear **before the root layout** are *root parameters*, readable from **any** Server Component (or server-side utility) via the `next/root-params` module — no prop drilling. The export name matches the segment folder name (e.g. `app/[locale]` → `import { locale } from 'next/root-params'`). Introduced in **v16.3.0**. ([next-root-params](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/next-root-params.mdx))

- Root parameter names must be valid JS identifiers; kebab-cased segments like `[post-slug]` are unsupported and error at dev/build time.
- `next/root-params` works only in **Server Components** — not Client Components, Server Actions, or Route Handlers (Route Handler support is planned). Importing it in a Client Component fails at build time; no `import 'server-only'` needed.
- Types are generated during `next dev`, `next build`, or `next typegen`. With **multiple root layouts**, a getter for a param absent from some roots has return type `string | undefined`.
- Getter return types: dynamic `[id]` → `string`; catch-all `[...path]` → `string[]`; optional catch-all `[[...path]]` → `string[] | undefined`.
- Inside a `use cache` function, only the root params you actually call become part of the **cache key** (not every dynamic segment), so cache entries aren't split across unrelated params.
- Calling a root getter inside `unstable_cache` **throws** — use `use cache` instead.
- In a nested `generateStaticParams`, read a root param directly via its getter (no need to destructure from `params`). Under Cache Components, root params require a `generateStaticParams` returning at least one value per root param or the build fails. ([next-root-params](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/next-root-params.mdx))

## Parallel routes and intercepting routes

Advanced `app/` routing patterns built on file conventions. (`default.js` and `LayoutProps` slot handling are summarized in the file-conventions table and Type helpers section above.)

### Parallel routes (named slots)
- Define slots with the `@folder` convention (e.g. `@analytics`, `@team`). The shared parent layout receives each slot as a prop alongside `children` and renders them in parallel.
- Slots are NOT route segments and do NOT affect the URL: `/@analytics/views` resolves to `/views`. A slot plus the regular `page` component form the final page for the segment.
- A route segment with one dynamic slot must make all slots at that level dynamic — you cannot mix prerendered and dynamically rendered slots at the same level.
- `children` is an implicit slot equivalent to `app/@children`; it does not require a folder mapping.
- `default.js` is the fallback for unmatched slots on **hard navigation** (full-page reload / initial load): Next.js renders it for slots that don't match the current URL, or 404 if absent. You also need `default.js` as the `children` fallback when Next.js can't recover the parent page's active state.
- **Soft navigation** (client-side) keeps each slot's active subpage even when it doesn't match the current URL (partial render). **Hard navigation** (refresh) falls back to `default.js`/404 for unmatched slots — this 404 guards against accidentally rendering a parallel route on an unintended page.
- `useSelectedLayoutSegment(s)` accept a `parallelRouteKey` to read the active segment within a slot (e.g. `useSelectedLayoutSegment('auth')` returns `"login"` for `app/@auth/login`).
- Add a `layout` inside a slot for independent, tab-like navigation within that slot; each slot gets its own `loading`/`error` boundaries (streamed independently).
- Conditional routes: both slots' pages execute on the server regardless of which the layout returns — the conditional decides what the user sees, not what runs. Authorize inside each slot's page or Data Access Layer.
- Modals: combine with intercepting routes — render `@auth/default.js` returning `null`, add `@auth/(.)login/page.tsx` importing the `<Modal>` content, and use a catch-all `@auth/[...catchAll]/page.tsx` returning `null` to close the modal when navigating to any other route. On refresh/initial load, `/login` renders the full login page instead of the modal.
- A route segment with one dynamic slot must make all slots at that level dynamic — you cannot mix prerendered and dynamically rendered slots at the same level.

### Intercepting routes
- `(..)` works like relative `../` but for route segments. Matchers: `(.)` same level, `(..)` one level above, `(..)(..)` two levels above, `(...)` from the `app` root.
- The matcher is based on **route segments, not the file system** — it does NOT count `@slot` folders. So a route that is two file-system levels up but only one segment level up (because a slot sits between) uses `(..)`, not `(..)(..)`.
- **Soft navigation** (client-side) overlays the intercepted route on the current layout while masking the URL; **hard navigation** (shareable URL / refresh) renders the full page for that route instead, with no interception.
- Commonly composed with parallel routes to build modals that are shareable, preserve context on refresh, close on back-navigation, and reopen on forward-navigation.
- Intercepting routes are not supported with `output: 'export'`.

## Type helpers

- `PageProps`, `LayoutProps`, and `RouteContext` are globally available helpers generated by `next dev`, `next build`, or `next typegen`. No imports are required.

```ts
export default async function Page(props: PageProps<'/blog/[slug]'>) {
  const { slug } = await props.params
}
```

- Static routes resolve `params` to `{}`.
- `LayoutProps` includes `children` and any named slots from parallel routes (e.g. `@analytics`).
- For typed routes beyond the helpers, enable `experimental.typedRoutes` and run `next typegen`.
- The `PageProps` / `LayoutProps` / `RouteContext` helpers type `params` values as `string`, `string[]`, or `undefined` because users can enter any URL.

## Page props

Pages and layouts receive typed props:

- `params` — a `Promise` containing the route segment values. In Next.js 15+, always `await` it.
- `searchParams` — a `Promise` of the URL query string values. Using it opts the page into **dynamic rendering** because the values come from the incoming request.

## Layout (`layout.tsx`)

- A layout wraps `template.js`, `error.js`, `loading.js`, `not-found.js`, and `page.js` in its segment. `children` is required; `params` is an optional `Promise` of the route params from the root down to that layout (await it, or read it with React `use`).
- **Multiple root layouts:** any layout without a `layout.js` above it is a root layout — e.g. via route groups like `app/(shop)/layout.js`, or by omitting `app/layout.js` so `app/dashboard/layout.js` and `app/blog/layout.js` each become roots. Navigating **across** multiple root layouts triggers a **full page load** (not client-side navigation).
- **Root layout under a dynamic segment:** e.g. `app/[lang]/layout.js` for i18n. Dynamic segments before the root layout are *root parameters*, readable from any Server Component via `next/root-params`.
- Do **not** manually add `<head>` tags (`<title>`, `<meta>`) to root layouts. Use the Metadata API instead: `export const metadata` (object) or `export async function generateMetadata`. It handles streaming and de-duplication of `<head>` elements.
- Layouts are cached on the client during navigation and **do not re-render**. They therefore cannot read the raw request object (use `headers()` / `cookies()`), cannot read `searchParams` (use the Page `searchParams` prop or `useSearchParams` in a Client Component), and cannot read `pathname` (use `usePathname` in a Client Component).
- `loading.js` sits *below* `layout.js`, so it cannot show a fallback for uncached/runtime data access in the layout (`cookies()`, `headers()`, uncached fetches). Without Cache Components, navigation blocks until the layout finishes; with Cache Components, such access must be wrapped in its own `<Suspense>` boundary or you get a build-time error.
- Layouts **cannot pass data to their `children`**. Fetch the same data in multiple files and dedupe with React `cache()`, or rely on `fetch` auto-deduping in Next.js.
- Layouts have no access to route segments below themselves; use `useSelectedLayoutSegment` / `useSelectedLayoutSegments` in a Client Component.
- `params` was a synchronous prop in v14 and earlier; Next.js 15 still permits synchronous access but it is deprecated — migrate with the codemod `docs/app/guides/upgrading/codemods#150`. (`layout` introduced in `v13.0.0`; `params` became a promise in `v15.0.0-RC`.)

## Page (`page.tsx`)

- A `page` is always the **leaf** of the route subtree. A `page` file is required to make a segment publicly accessible.
- `searchParams` type signature: `Promise<{ [key: string]: string | string[] | undefined }>`. It is a plain JavaScript object, **not** a `URLSearchParams` instance.
- `searchParams` is a Request-time API: using it opts the page into dynamic rendering at request time. With Cache Components, *where* you read `searchParams` in the tree determines how much of the page can be prerendered (the static shell).
- **PageProps helper (v15.0.0-RC+):** globally available after type generation; `PageProps<'/blog/[slug]'>` gives strongly typed `params` and `searchParams`. Literal routes autocomplete params keys; static routes resolve `params` to `{}`. The `PageProps` helper does not need to be imported.
- Client Component pages (which can't be `async`) can read the `params` / `searchParams` promises via React's `use()` hook.
- In v14 and earlier `params` / `searchParams` were synchronous props; in Next.js 15 you may still access them synchronously, but that behavior is deprecated. A codemod is available (`docs/app/guides/upgrading/codemods#150`).
- Versions: `page` introduced in `v13.0.0`; `params` and `searchParams` became promises in `v15.0.0-RC`.

## Template (`template.tsx`)

- Like a layout, but given a unique key on each navigation, so child Client Components **reset their state** (and `useEffect` re-synchronizes, DOM is recreated).
- Use a template when you need to: resync `useEffect` on navigation; reset child Client Component state (e.g. an input field); or change Suspense behavior — Suspense boundaries inside layouts show a fallback only on first load, but templates show it on **every** navigation.
- In the component hierarchy `template.js` renders between `layout.js` and `error.js`. It wraps `error.js`, `loading.js`, `not-found.js`, and `page.js`, but does **not** wrap the `layout.js` in the same segment.
- Behavior: a template is a Server Component by default. It receives a unique key for its segment level and remounts when that segment (including its dynamic params) changes; navigations within deeper segments do **not** remount higher-level templates; **search params do not trigger remounts**.
- Rendered as `<Layout><Template key={routeParam}>{children}</Template></Layout>` — the unique `key` is what forces the remount/state reset. Introduced in `v13.0.0`.

## Loading (`loading.tsx`)

- `loading.js` creates loading UI with React Suspense; the fallback is prefetched, making navigation immediate (unless prefetch hasn't completed). Navigation is interruptible, and shared layouts stay interactive while new segments load.
- By default a Server Component, but it can be a Client Component with the `"use client"` directive.
- Loading UI components accept **no parameters**.
- `loading.js` is not supported with `output: 'export'`.
- Some browsers buffer streamed responses until they exceed 1024 bytes (mainly affects trivial apps).
- In the component hierarchy `loading.js` wraps `not-found.js`, `page.js`, and nested `layout.js` in a `<Suspense>` boundary; it does **not** wrap the `layout.js`, `template.js`, or `error.js` in the same segment.
- When streaming, a `200` status is returned and cannot be changed afterward. A streamed 404 includes a `<meta name="robots" content="noindex">` tag so it isn't indexed despite the 200.
- For bots that cannot run JS (e.g. Twitterbot), Next.js resolves `generateMetadata` before streaming and places it in the initial HTML `<head>`; streaming is server-rendered and does not hurt SEO.
- To return a real non-200 status, call `notFound()` (or verify the resource) **before** any `<Suspense>` boundary renders or before any `await` that may suspend — once the body streams, the status is fixed at `200`.

## Static export

Set `output: 'export'` in `next.config.*` to produce a static site or SPA. `next build` emits an `out/` folder with HTML/CSS/JS assets per route.

Unsupported with static export (App Router):
- Dynamic routes without `generateStaticParams()` or with `dynamicParams: true`
- Route Handlers that rely on the Request object (only static `GET` handlers with `export const dynamic = 'force-static'` work)
- `cookies()`, `headers()`, `draftMode()` toggling, Server Actions
- Rewrites, redirects, headers, Proxy
- ISR, intercepting routes, default `next/image` loader
- `loading.js` (not supported with `output: 'export'`)
- In dev, using unsupported features throws like setting `export const dynamic = 'error'` in the root layout

Use a custom image loader (e.g. Cloudinary) if you need image optimization with `output: 'export'`.

## Single-page applications

Next.js can power strict SPAs with client-side navigation while allowing progressive adoption of server features.
- Use `next/link` for prefetching and URL-backed routing state.
- Stream server-initiated data into Client Components by passing a Promise from a Server Component/layout to a Client Component provider; unwrap with React `use()`.
- Use `next/dynamic` with `ssr: false` for components that must only render in the browser.
- `window.history.pushState` / `replaceState` integrate with the Next.js Router and sync `usePathname` / `useSearchParams`.
- Combine Server Actions with `useTransition`, `useOptimistic`, and `useActionState` for instant-feeling mutations.

## View transitions

React's `<ViewTransition>` works in the App Router with no extra configuration.
- Animations are triggered by transitions, `<Suspense>`, and `useDeferredValue`; ordinary `setState` does not trigger them.
- Wrap shared elements in `<ViewTransition name="...">` to morph them across routes.
- Use `default="none"` on named pairs to avoid animating on unrelated transitions.
- Add directional semantics with `<Link transitionTypes={['nav-forward']}>` or `useRouter().push(..., { transitionTypes: [...] })`.
- Respect `prefers-reduced-motion` by disabling view-transition animations for affected users.
- Browser support requires Chromium 125+ / recent Safari / recent Firefox; without support the app still works, just without animations.

## Instrumentation

Create `instrumentation.ts|js` at the **project root** (or `src/` root if using `src`). Export a `register` function that runs **once** when a new Next.js server instance starts, before the server is ready to handle requests. Use it for OpenTelemetry, monitoring, logging, or side-effect imports.

- The file must not be inside `app/` or `pages/`.
- If you use `pageExtensions`, update the filename to match.
- Import side-effect packages inside `register()` rather than at the top level to keep side effects colocated.
- Conditionally import runtime-specific code with `process.env.NEXT_RUNTIME` (`nodejs` / `edge`).

See `references/deployment-and-production.md` for OpenTelemetry examples.

## Instrumentation client

- `instrumentation-client.js|ts` at the project root (or `src/` root) runs client-side code before the app becomes interactive.
- It executes after the HTML document is loaded but before React hydration begins.
- Only synchronous top-level code is guaranteed to complete before hydration; async work is fire-and-forget.
- To guarantee a polyfill is applied before components run, statically import and apply it synchronously after feature detection.
- Export `onRouterTransitionStart(url, navigationType)` to observe App Router navigation starts. Enable `experimental.instrumentationClientRouterTransitionEvents` to receive a third `event` argument with `id`, `timestamp`, `fromRoutes`, and `prefetchIntent`.
- DevTools warn if initialization takes longer than 16ms.

## Source URLs

- App Router landing page: https://nextjs.org/docs/app
- Project structure: https://nextjs.org/docs/app/getting-started/project-structure
- Layouts and Pages: https://nextjs.org/docs/app/getting-started/layouts-and-pages
- Linking and Navigating: https://nextjs.org/docs/app/getting-started/linking-and-navigating
- Docs landing page: https://nextjs.org/docs
- Dynamic Routes: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes
- Route groups: https://nextjs.org/docs/app/api-reference/file-conventions/route-groups
- Parallel routes: https://nextjs.org/docs/app/api-reference/file-conventions/parallel-routes
- Intercepting routes: https://nextjs.org/docs/app/api-reference/file-conventions/intercepting-routes
- Route Handlers: https://nextjs.org/docs/app/api-reference/file-conventions/route
- Proxy: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Type helpers (`PageProps` / `LayoutProps`): https://nextjs.org/docs/app/getting-started/layouts-and-pages#route-props-helpers
- Lazy loading: https://nextjs.org/docs/app/guides/lazy-loading
- MDX: https://nextjs.org/docs/app/guides/mdx
- `mdx-components.tsx` convention: https://nextjs.org/docs/app/api-reference/file-conventions/mdx-components
- Production checklist: https://nextjs.org/docs/app/guides/production-checklist
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- Deploying to platforms: https://nextjs.org/docs/app/guides/deploying-to-platforms
- PWA / manifest: https://nextjs.org/docs/app/guides/progressive-web-apps
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- MCP server: https://nextjs.org/docs/app/guides/mcp
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- Single-page applications: https://nextjs.org/docs/app/guides/single-page-applications
- View transitions: https://nextjs.org/docs/app/guides/view-transitions
- `forbidden` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/forbidden
- `unauthorized` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/unauthorized
- `instrumentation-client` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client
- `error` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/error
- `not-found` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/not-found
- `default` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/default
- `dynamic-routes` convention: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes
- `instrumentation` guide: https://nextjs.org/docs/app/guides/instrumentation
- `instrumentation` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
- `layout` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/layout
- `page` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/page
- `template` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/template
- `loading` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/loading
- `route` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/route
- `proxy` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- `mdx-components` convention: https://nextjs.org/docs/app/api-reference/file-conventions/mdx-components
- `generateStaticParams`: https://nextjs.org/docs/app/api-reference/functions/generate-static-params
- `cacheComponents` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `partialPrefetching` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/partialPrefetching
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline

<!-- CANARY-API-REFERENCE-2026-08-31 -->
### Canary API reference additions (ingest 2026-08-31)

**Components (`03-api-reference/02-components`)**
- `<Form>` from `next/form`: with a string `action`, it uses `GET`, encodes form data as search params, and navigates via client-side transition in the App Router (prefetching shared UI when `prefetch` is true); with a Server Action it behaves like a React form. Supported string-action props: `action`, `replace` (default `false`), `scroll` (default `true`), `prefetch` (default `true`, App Router only). `formAction` overrides the form action but does not support prefetching; include `basePath` if configured. `method`, `encType`, `target`, and their `form*` equivalents are not supported and fall back to native browser behavior. `<input type="file">` with a string action submits only the filename. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/form.mdx)
- `<Link>` App Router props: `href` (required, string or URL object), `replace` (default `false`), `scroll` (default `true`), `prefetch` (`boolean`, `"auto"`, or `null`; default is `"auto"`/null), `onNavigate` (called during client-side navigation, can `preventDefault()`), `transitionTypes` (`string[]` for React `<ViewTransition>`). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/link.mdx)
- `<Script>` from `next/script`: strategies are `beforeInteractive` (server-rendered in `<head>`, executes before Next.js code but does not block hydration), `afterInteractive` (default, client-side after some hydration), `lazyOnload` (idle), `worker` (experimental web worker via Partytown; not supported in App Router). `beforeInteractive` must be placed in a root layout (App Router) or `_document` (Pages Router) and runs once per document load; it is not re-executed on client-side navigations including root-param changes. `onLoad`, `onReady`, `onError` only work in Client Components. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/script.mdx)
- `next/font`: `src` for `next/font/local` is a string or array of `{ path, weight?, style? }` relative to the file that calls `localFont`; variable fonts don't need `weight`; non-variable Google fonts require `weight`; `weight` may be a single value, range string, or array. `subsets`, `axes`, `display` (`'auto'|'block'|'swap'|'fallback'|'optional'`, default `'swap'`), `preload` (default `true`), `fallback`, `adjustFontFallback`, `variable`, and `declarations` (local only) are supported. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/font.mdx)
- `next/image`: required props are `src` and `alt`; `width`/`height` are required unless the image is statically imported or uses `fill`. `fill` requires a positioned parent (`relative`/`fixed`/`absolute`). `loader` is a custom function receiving `{ src, width, quality }`; in App Router, using function props like `onLoad` requires a Client Component. `sizes` is required for responsive `fill` images. `preload` defaults to `false`; set to `true` for LCP images. `onLoadingComplete` is deprecated; use `onLoad`. `overrideSrc` sets a custom `src` attribute on the rendered `img` while keeping the generated `srcset`. `decoding` defaults to `"async"`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/image.mdx)

**File conventions (`03-api-reference/03-file-conventions`)**
- `favicon.ico` is only valid at the root `/app` segment; `icon` and `apple-icon` files can live in any segment. Static image types: `favicon.ico`, `icon.(ico|jpg|jpeg|png|svg)`, `apple-icon.(jpg|jpeg|png)`. Generated icons (`icon.tsx`, `apple-icon.tsx`) can use `ImageResponse`; they are statically optimized by default unless they use request-time APIs or dynamic config. Multiple icons can be created with numbered suffixes and are sorted lexically. You cannot generate a `favicon`; use `icon` or a `favicon.ico` file. `sizes="any"` is added to `.svg` icons or when image size cannot be determined. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/app-icons.mdx)
- `opengraph-image` / `twitter-image`: static files support `.jpg`, `.jpeg`, `.png`, `.gif`; `twitter-image` must be ≤ 5 MB and `opengraph-image` ≤ 8 MB or the build fails. Generated versions export `alt`, `size`, and `contentType`. Generated OG/Twitter image files are special Route Handlers cached by default unless they use request-time APIs or dynamic config; multiple images per file are supported via `generateImageMetadata`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/opengraph-image.mdx)
- `sitemap.(xml|js|ts)` is a special Route Handler cached by default unless it uses request-time APIs or dynamic config. It supports `images` and `videos` entries and `alternates.languages` for localization. Split large sitemaps via `generateSitemaps` (returns array of `{ id }` objects); generated sitemaps are served at `/.../sitemap/[id].xml`. As of v16.0.0, the `id` passed to the default `sitemap` function is a `Promise<string>`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/sitemap.mdx)
- `robots.(txt|ts|js)`: `rules` supports `userAgent`, `allow`, `disallow`, `crawlDelay`, and an `other` field for non-standard per-agent directives (e.g. `Request-Rate`). Rules can be a single object or an array for per-bot configuration. Generated robots files are special Route Handlers cached by default unless dynamic. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/robots.mdx)
- `manifest.(json|webmanifest|ts|js)` at the root of `app/` provides the PWA web app manifest. Generated manifest files are special Route Handlers cached by default unless they use request-time APIs or dynamic config. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/manifest.mdx)
- Route Segment Config exports: `dynamicParams` (boolean, default `true`; not available when Cache Components is enabled), `runtime` (`'nodejs'` default; `'edge'` deprecated), `preferredRegion` (deprecated), `maxDuration` (seconds). As of v16.0.0, `dynamic`, `dynamicParams`, `revalidate`, and `fetchCache` are removed when Cache Components is enabled. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/index.mdx)
- `instant` route segment config: only works when `cacheComponents` is enabled; cannot be used in Client Components. Accepts `true`, `false`, or `{ level: 'warning' }`. Set `validationLevel` in `experimental.instantInsights` to tune implicit validation. A `false` value higher in the route tree takes precedence over deeper `true` values for the static-shell check. The Navigation Inspector is available in Next.js DevTools when Cache Components is enabled. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/instant.mdx)
- `prefetch` route segment config: only works when `cacheComponents` is enabled; cannot be used in Client Components. Values: `'auto'` (default, omit explicitly), `'partial'`, `'force-disabled'`. Set on the destination segment, not the link. With `'partial'`, a `<Link prefetch={true}>` additionally resolves URL data (`params`, `searchParams`, full URL) and cached content behind it. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/prefetch.mdx)
- `dynamic-routes`: `params` and `searchParams` are promises in Next.js 15+ and must be awaited. With Cache Components and **without** `generateStaticParams`, param access must be wrapped in `<Suspense>`; in layouts, avoid awaiting `params` at the top level. `generateStaticParams` works in pages, layouts, and Route Handlers to statically generate responses. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/dynamic-routes.mdx)
- `error.js` / `error.tsx`: must be Client Components; wraps `loading.js`, `not-found.js`, `page.js`, and nested `layout.js` in a React error boundary; does not wrap the `layout.js` or `template.js` in the same segment. Receives `error` (`Error & { digest?: string }`), `retry()` (re-fetches and re-renders), and `reset()` (re-renders without re-fetching). `global-error` handles errors in the root layout/template and must define its own `<html>` and `<body>`; it does not inherit app-level theme classes/attributes. `retry` became stable in v16.3.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/error.mdx)
- `forbidden.js` / `forbidden.tsx`: renders UI when `forbidden()` is invoked; returns a `403` status code. Components do not accept any props. Introduced in v15.1.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/forbidden.mdx)
- `default.js`: parallel-route fallback when a slot has no matching active state on hard navigation. For named slots, missing `default.js` errors; for the implicit `children` slot, missing `default.js` returns a 404. Can call `notFound()` to preserve old behavior. Receives `params` as a promise. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/default.mdx)

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary Pages Router additions — Error Handling (ingest 2026-09-02)

Sourced from `docs/02-pages/03-building-your-application/06-configuring/12-error-handling.mdx`.

**Pages Router error handling**
- Development runtime errors show a dev overlay visible only during `next dev`; fixing the error dismisses it. (Source: https://nextjs.org/docs/pages/building-your-application/configuring/error-handling)
- Next.js provides a static 500 page by default; create `pages/500.js` to customize it. (Source: above)
- Use a custom 404 page for specific runtime errors like file-not-found. (Source: above)
- For client-side errors, create a class-component `ErrorBoundary` and wrap the `Component` prop in `pages/_app.js`. (Source: above)
- Error Boundary responsibilities: render fallback UI after an error, provide a way to reset application state, log error information. (Source: above)
- For monitoring client errors, use a service like Sentry, Bugsnag, or Datadog. (Source: above)
- `pages/_error.{js,jsx,ts,tsx}` overrides the shared `Error` component and is used only in production (dev overlay in development); `Error.getInitialProps = ({ res, err }) => { ... }` returns `{ statusCode }`. Accessing `/_error` directly renders a 404. (Source: https://nextjs.org/docs/pages/building-your-application/routing/custom-error)
- `pages/404` and `pages/500` are statically generated at build time and may use `getStaticProps` for build-time data. (Source: above)
