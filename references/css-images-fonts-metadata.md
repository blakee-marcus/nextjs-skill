# CSS, Images, Fonts, and Metadata

## CSS

Next.js supports:

- **Global CSS** — import `.css` files. In the App Router, global styles can be imported into any layout, page, or component, but stylesheets are not removed on navigation, so keep global styles truly global (e.g. Tailwind base). Import global/Tailwind stylesheets in the root layout.
- **CSS Modules** — `*.module.css` (and `*.module.scss` / `*.module.sass`), scoped locally. Use the same class name in different files without collisions.
- **Tailwind CSS** — use the installed Tailwind skill for Tailwind-specific semantics; this skill owns the Next.js integration boundary. Next.js default templates use Tailwind CSS v4 with `@import 'tailwindcss';` in `app/globals.css` and the `@tailwindcss/postcss` plugin in `postcss.config.mjs`.
- **Sass** — built-in support for `.scss` / `.sass`. Install `sass` as a dev dependency. Configure `sassOptions` in `next.config.*` for `additionalData`, `implementation`, etc. Use `.module.scss` / `.module.sass` for component-level scoped styles. Sass variables can be exported from CSS Module files via `:export` and consumed in components.
- **CSS-in-JS** — see the CSS-in-JS guide for library-specific setup. Note: CSS-in-JS libraries that rely on runtime injection are not compatible with React Server Components or Next.js 16's streaming model unless the library specifically supports React 19 / Server Components.

### CSS-in-JS compatibility

CSS-in-JS libraries that depend on injecting styles at runtime during render are not compatible with React Server Components and streaming. Prefer libraries that support React 19, Server Components, and the App Router. When migrating, move global/reset styles to CSS Modules or Tailwind and keep component-scoped dynamic styles minimal.

### CSS ordering and merging

Next.js optimizes CSS during production builds by automatically chunking stylesheets. The final CSS order depends on the order you import styles in your code:

- Imports from earlier imported components are ordered before later imports.
- Keep imports contained to a single entry file where possible.
- Import global styles and Tailwind in the root layout.
- Avoid import-sorting linters (e.g. ESLint `sort-imports`) that would reorder CSS imports.
- Use `cssChunking` in `next.config.js` to control chunking behavior.
- CSS ordering can differ between development and production; verify with `next build`.

### Development vs production

- In development, CSS updates apply via Fast Refresh.
- In production, CSS is concatenated into minified, code-split `.css` files.
- CSS works without JavaScript in production; development requires JavaScript for Fast Refresh.

## Images

Use `next/image` for optimized images:

```tsx
import Image from 'next/image'

<Image src="/profile.png" alt="Profile" width={500} height={500} />
```

- Static imports provide automatic `width`, `height`, `blurDataURL`.
- Remote images require explicit dimensions and `next.config.js` `images.remotePatterns`.
- Use `fill` prop to make the image fill its parent container.
- Store static files in `public/`.
- If you can't use a static import, use a dynamic `import()` in a Server Component to still get automatic `width`, `height`, and `blurDataURL`. The dynamic path must include a static prefix and only files in that directory are bundled.
- Use `unoptimized` for images that should not be optimized (SVG, GIF, authenticated sources). Can be set globally in `images.unoptimized`.
- The default loader does **not** forward headers when fetching remote `src`; use `unoptimized` for authenticated remote images.
- `images.localPatterns` can restrict which local paths are allowed for optimization.
- `sizes` is required for responsive `fill` images; without it the browser assumes `100vw`. `sizes` also controls whether Next.js generates a limited `srcset` (without `sizes`) or a full responsive `srcset` (with `sizes`).
- Configure `qualities` to enforce an allowlist of quality values; values outside the list are coerced to the nearest entry, with a dev warning.
- `priority` is deprecated in Next.js 16 in favor of `preload`.
- `onLoadingComplete` is deprecated; use `onLoad`.
- `overrideSrc` lets you set a custom `src` attribute on the rendered `img` while keeping the generated `srcset`.
- `decoding` defaults to `"async"`; can be set to `"sync"` or `"auto"`.
- `preload` defaults to `false`; set to `true` for LCP images.

### Analytics / Web Vitals

- Use `instrumentation-client.js|ts` at the project root to run analytics/monitoring code before the frontend app starts executing.
- `instrumentation-client` executes after the HTML document is loaded but before React hydration begins. Only synchronous top-level code is guaranteed to complete before hydration; async work (`Promise`, dynamic `import()`, top-level `await`) is fire-and-forget and may resolve after hydration.
- To guarantee a polyfill is applied before components run, statically import and apply it synchronously after feature detection. Conditional/dynamic imports here may be too late.
- Export `onRouterTransitionStart(url, navigationType)` to observe App Router navigation starts. Enable `experimental.instrumentationClientRouterTransitionEvents` to receive a third `event` argument with `id`, `timestamp`, `fromRoutes`, and `prefetchIntent`.
- Use the `useReportWebVitals` hook from `next/web-vitals` in a `'use client'` component to capture TTFB, FCP, LCP, FID, CLS, INP, etc.
- Keep the client boundary narrow: create a dedicated `WebVitals` component and import it into the root layout.

### Forms / navigation

- `<Form>` from `next/form` extends HTML `<form>` for client-side navigation when `action` is a string, and for progressive enhancement.
- With a string `action`, the form uses `GET`, encodes data as search params, and navigates via client-side transition in the App Router (prefetching shared UI when `prefetch` is true).
- With a function `action` (Server Action), it behaves like a React form.
- Supported props for string `action`: `action`, `replace` (default `false`), `scroll` (default `true`), `prefetch` (default `true`, App Router only).
- `formAction` on a submit button/input can override the form `action` but does not support prefetching; include `basePath` in the path if configured.
- `method`, `encType`, `target`, and their `form*` equivalents are not supported and fall back to native browser behavior. Use a plain `<form>` if you need them.
- `<input type="file">` with a string action submits the filename, not the file object, matching native browser behavior.

<!-- CANARY-API-REFERENCE-2026-08-31 -->
### Canary API reference additions (ingest 2026-08-31)

**`next/image` (component reference details)**
- Required props: `src` and `alt`. `width`/`height` are required unless the image is statically imported or uses `fill`. `fill` requires the parent element to assign `position: "relative"`, `"fixed"`, or `"absolute"`.
- `loader` is a custom function receiving `{ src, width, quality }` and returning a URL string. In the App Router, using function props such as `onLoad` requires a Client Component.
- `sizes` is required for responsive `fill` images; without it the browser assumes `100vw`.
- `preload` defaults to `false`; set to `true` for LCP images. `priority` is deprecated in favor of `preload`.
- `onLoadingComplete` is deprecated; use `onLoad`.
- `overrideSrc` lets you set a custom `src` attribute on the rendered `img` while keeping the generated `srcset`.
- `decoding` defaults to `"async"`; can be set to `"sync"` or `"auto"`.
- The default loader does **not** forward headers when fetching remote `src`; use `unoptimized` for authenticated remote images. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/image.mdx)

**`next/font` (component reference details)**
- For `next/font/local`, `src` is a string or array of `{ path, weight?, style? }` objects relative to the file that calls `localFont`.
- Variable fonts do not need a `weight`; non-variable Google fonts require `weight` (string, range string, or array).
- Supported options: `subsets`, `axes` (variable Google fonts only), `display` (`'auto'`, `'block'`, `'swap'`, `'fallback'`, `'optional'`, default `'swap'`), `preload` (default `true`), `fallback`, `adjustFontFallback`, `variable`, and `declarations` (local fonts only). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/font.mdx)

**`next/script` (component reference details)**
- Strategies: `beforeInteractive` (server-rendered in `\u003chead\u003e`, executes before Next.js code but does not block hydration), `afterInteractive` (default, client-side after some hydration), `lazyOnload` (idle), `worker` (experimental web worker; not supported in App Router).
- `beforeInteractive` must be placed in a root layout (App Router) or `_document` (Pages Router). It runs once per document load and is not re-executed on client-side navigations, including root-param changes.
- `onLoad`, `onReady`, and `onError` handlers only work in Client Components.
- Inline scripts need a stable `id` so Next.js can deduplicate/optimize them. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/script.mdx)

**`next/form` / `<Form>` (component reference details)**
- With a string `action`, `<Form>` uses `GET`, encodes data as search params, and navigates via client-side transition in the App Router, prefetching shared UI when `prefetch` is true.
- With a Server Action, it behaves like a React form.
- String-action props: `action` (required; empty string navigates to same route with updated search params), `replace` (default `false`), `scroll` (default `true`), `prefetch` (default `true`, App Router only).
- `formAction` on a submit button/input can override the form action but does not support prefetching; include `basePath` in the path if configured.
- `method`, `encType`, `target`, and their `form*` equivalents are not supported and fall back to native browser behavior.
- `<input type="file">` with a string action submits the filename, not the file object. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/02-components/form.mdx)

**File-based metadata (convention reference details)**
- `favicon.ico` is only valid at the root `/app` segment; `icon` and `apple-icon` files can live in any segment. Static types: `favicon.ico`, `icon.(ico|jpg|jpeg|png|svg)`, `apple-icon.(jpg|jpeg|png)`. Generated icon files can use `ImageResponse` and may receive a `params` promise. Multiple icons can be created with numbered suffixes and are sorted lexically. You cannot generate a `favicon`; use `icon` or a `favicon.ico` file. `sizes="any"` is added to `.svg` icons or when image size cannot be determined. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/app-icons.mdx)
- `opengraph-image` / `twitter-image`: static files support `.jpg`, `.jpeg`, `.png`, `.gif`; `twitter-image` must be ≤ 5 MB and `opengraph-image` ≤ 8 MB or the build fails. Generated files export `alt`, `size`, and `contentType`; they are special Route Handlers cached by default unless dynamic. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/opengraph-image.mdx)
- `sitemap.(xml|js|ts)` is a special Route Handler cached by default unless dynamic. Supports `images`, `videos`, and `alternates.languages`. Split via `generateSitemaps` (array of `{ id }`); generated sitemaps served at `/.../sitemap/[id].xml`. As of v16.0.0, `id` in the default `sitemap` function is a `Promise\u003cstring\u003e`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/sitemap.mdx)
- `robots.(txt|ts|js)`: `rules` supports `userAgent`, `allow`, `disallow`, `crawlDelay`, and an `other` field for non-standard per-agent directives. Rules can be a single object or an array. Generated robots files are special Route Handlers cached by default unless dynamic. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/robots.mdx)
- `manifest.(json|webmanifest|ts|js)` at the root of `app/` provides the PWA web app manifest. Generated manifest files are special Route Handlers cached by default unless dynamic. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/01-metadata/manifest.mdx)

**Route Segment Config (reference details)**
- Supported exports: `dynamicParams` (boolean, default `true`; not available when Cache Components enabled), `runtime` (`'nodejs'` default, `'edge'` deprecated), `preferredRegion` (deprecated), `maxDuration` (seconds).
- As of v16.0.0, `dynamic`, `dynamicParams`, `revalidate`, and `fetchCache` are removed when Cache Components is enabled. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/index.mdx)
- `instant` only works when `cacheComponents` enabled; cannot be used in Client Components. Accepts `true`, `false`, or `{ level: 'warning' }`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/instant.mdx)
- `prefetch` only works when `cacheComponents` enabled; cannot be used in Client Components. Values: `'auto'` (default/omit), `'partial'`, `'force-disabled'`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/prefetch.mdx)
- `maxDuration` sets maximum execution time (seconds) for server-side logic in a route segment; also changes default timeout of all Server Actions on the page. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/maxDuration.mdx)
- `runtime`: `'nodejs'` default; `'edge'` deprecated. Cannot be used in Proxy. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/runtime.mdx)
- `preferredRegion` is deprecated; remove the export. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/02-route-segment-config/preferredRegion.mdx)

**Other file conventions**
- `instrumentation-client.js|ts`: runs before app becomes interactive, after HTML document load but before React hydration. Only synchronous top-level code is guaranteed before hydration. Export `onRouterTransitionStart(url, navigationType)` to observe App Router navigation starts; enable `experimental.instrumentationClientRouterTransitionEvents` for a third `event` argument (`id`, `timestamp`, `fromRoutes`, `prefetchIntent`). Dev warns if initialization exceeds 16ms. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/instrumentation-client.mdx)
- `default.js`: parallel-route fallback when a slot has no matching active state on hard navigation. For named slots, missing `default.js` errors; for implicit `children` it returns 404. Receives `params` as a promise. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/default.mdx)
- `dynamic-routes`: `params` and `searchParams` are promises in v15+ and must be awaited. With Cache Components and without `generateStaticParams`, param access must be wrapped in `\u003cSuspense\u003e`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/dynamic-routes.mdx)
- `error.js` / `error.tsx`: see `references/error-handling.md`; `retry` stable since v16.3.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/error.mdx)
- `forbidden.js` / `forbidden.tsx`: renders UI when `forbidden()` invoked; returns 403. No props. Introduced v15.1.0. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/forbidden.mdx)

## Fonts

`next/font` automatically optimizes and self-hosts fonts:

```tsx
import { Geist } from 'next/font/google'

const geist = Geist({ subsets: ['latin'] })

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={geist.className}>
      <body>{children}</body>
    </html>
  )
}
```

- Google Fonts are downloaded at build time; no runtime request to Google.
- Local fonts use `localFont` from `next/font/local`; the `src` path is resolved relative to the file that calls `localFont`.
- Variable fonts are preferred for performance and flexibility. For non-variable Google fonts, specify `weight`.
- For multiple files in the same family, pass an array of `{ path, weight?, style? }` objects to `localFont`.
- `localFont` accepts `src` as a string or an array of objects (`Array<{ path: string, weight?: string, style?: string }>`); paths are resolved relative to the file that calls `localFont`.
- Google Fonts support `subsets`, `axes` (for variable fonts), `display`, `preload`, `fallback`, `adjustFontFallback`, `variable`, and `declarations` (local only).
- `display` defaults to `'swap'`; other values include `'auto'`, `'block'`, `'fallback'`, `'optional'`.
- `preload` defaults to `true`.
- Local fonts support `declarations` to add custom `@font-face` descriptor properties.
- The `sizeAdjust` option has been removed.

## Metadata

Define static metadata by exporting a `metadata` object, or dynamic metadata with `generateMetadata`:

```tsx
export const metadata = {
  title: 'My Site',
  description: '...',
}
```

- `metadata` and `generateMetadata` exports are only supported in Server Components.
- Default `meta charset="utf-8"` and `meta viewport` tags are always added.
- `generateMetadata` receives `{ params, searchParams }` and an optional `parent: ResolvingMetadata` argument; it can fetch data and return a `Metadata` object.
- Use `React.cache` to memoize shared data fetches between `generateMetadata` and the page.

### Streaming metadata

For dynamically rendered pages, metadata streams separately and is injected once `generateMetadata` resolves, without blocking UI rendering. Streaming metadata was introduced in **v15.2.0**. Resolved tags are appended to `<body>` for JS-capable crawlers (e.g. `Googlebot`), but rendering **blocks** for HTML-limited bots that expect metadata in `<head>` (e.g. `Twitterbot`, `Slackbot`, `Bingbot`, `facebookexternalhit`). Customize with `htmlLimitedBots` in `next.config.js`; disable streaming entirely with `htmlLimitedBots: /.*/`.

### Metadata export rules (canary)
- `generateMetadata` / the static `metadata` object and `generateViewport` / the static `viewport` object are **only** supported in Server Components.
- You **cannot** export both the static `metadata` object and `generateMetadata` (or both `viewport` and `generateViewport`) from the same route segment.
- If metadata/viewport does not depend on request data, prefer the static object over the function.
- `searchParams` is only available in `page.js` segments (not layouts).
- `metadataBase` lets URL-based metadata fields use relative paths; a relative path **without** a configured `metadataBase` causes a build error.
- Metadata from multiple segments is **shallowly merged**, not deep-merged: a nested field (`openGraph`, `robots`) defined in a parent is **overwritten entirely** by the last segment that defines it. Re-declare the keys you still want.
- `title.template` applies **only to child segments**, never the segment that defines it, and **requires `title.default`**. It is a no-op in `page.js` (a terminating segment). `title.absolute` **ignores** any parent `title.template`. `title.template` has no effect if a route hasn't defined a `title` or `title.default`. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx)
- If `generateMetadata` uses `'use cache'`, its return value must be **serializable** — Cache Functions do not support `URL` instances, so return `metadataBase` and similar fields as strings (`url.toString()`).
- Under Cache Components, `generateMetadata`/`generateViewport` that touch runtime data (`cookies()`, `headers()`, `params`, `searchParams`, uncached `fetch`) **raise an error** unless you either mark the scope `'use cache'` or signal intentional dynamic rendering with a dynamic marker (`connection()` inside `<Suspense>`).
- For `generateViewport` deferring to request time under Cache Components, either wrap `<body>` in `<Suspense>` **or** set `export const instant = false` to opt the segment out of instant-navigation validation; otherwise the build errors.
- Unlike metadata, `viewport` **cannot be streamed** (it affects initial page load). If `generateViewport` defers to request time, wrap the document `<body>` in `<Suspense>` so the route is dynamic; otherwise the page blocks until it resolves.
- To isolate fully dynamic `viewport` to specific routes while keeping a static shell elsewhere, use multiple root layouts. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/generate-viewport.mdx)
([generate-metadata](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)) ([generate-viewport](https://nextjs.org/docs/app/api-reference/functions/generate-viewport))

### generateMetadata: data fetching, redirects, and `metadataBase` composition

- `fetch` requests inside `generateMetadata` (and across `generateStaticParams`, Layouts, Pages, and Server Components) are automatically **memoized** for the same data; use React `cache()` only when `fetch` is unavailable. ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))
- `redirect()` and `notFound()` can be called inside `generateMetadata`. ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))

#### `metadataBase` URL composition

`metadataBase` lets URL-based `metadata` fields in the **current segment and below** use a **relative path** instead of an absolute URL. Resolution favors developer intent over directory traversal:

| Field value                      | Resolved URL                     |
| -------------------------------- | -------------------------------- |
| `/`                              | `https://acme.com`               |
| `./`                             | `https://acme.com`               |
| `payments`                       | `https://acme.com/payments`      |
| `/payments`                      | `https://acme.com/payments`      |
| `./payments`                     | `https://acme.com/payments`      |
| `../payments`                    | `https://acme.com/payments`      |
| `https://beta.acme.com/payments` | `https://beta.acme.com/payments` |

- Trailing slashes between `metadataBase` and a field are normalized; duplicate slashes collapse to one.
- `metadataBase` may include a subdomain (e.g. `https://app.acme.com`) or a base path (e.g. `https://acme.com/start/from/here`).
- An absolute URL in a field overrides `metadataBase` entirely. A relative path in a URL-based field without a configured `metadataBase` is a **build error**. ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))

#### Deprecations and custom/unsupported tags

- `themeColor`, `colorScheme`, and `viewport` inside the `metadata` object are **deprecated as of Next.js 14** — define them via the `viewport` object / `generateViewport` instead. ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))
- Use the `other` field to render arbitrary custom `<meta name content>` tags (an array value emits multiple tags with the same name). ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))
- The Metadata API does **not** support `<meta http-equiv>`, `<base>`, `<noscript>`, `<style>`, `<script>`, or `<link rel="stylesheet|preload|preconnect|dns-prefetch">`; render those directly in the layout/page, or for resource hints use `ReactDOM.preload` / `ReactDOM.preconnect` / `ReactDOM.prefetchDNS` (these run only in Client Components). ([generate-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-metadata.mdx))

### File-based metadata

- `favicon.ico`, `icon.*`, `apple-icon.*`
- `opengraph-image.*`, `twitter-image.*`
- Generated versions are `.js`, `.ts`, `.tsx`.
- `sitemap.xml` / `sitemap.ts`, `robots.txt` / `robots.ts`.
- `manifest.ts` / `manifest.json` for PWA web app manifest.

The most specific file in the folder structure takes precedence over parent ones.

### Generated Open Graph images

Use `ImageResponse` from `next/og` in an `opengraph-image.tsx` or `twitter-image.tsx` file to generate dynamic OG/Twitter images with JSX/CSS. Export `alt`, `size`, and `contentType`. Supported CSS is limited (flexbox, absolute positioning, text wrapping, nested images); grid and many advanced layouts are not supported. Constraints: total bundle size is capped at **500 KB** (JSX + CSS + fonts + images); only `ttf`, `otf`, and `woff` font formats are supported (prefer `ttf`/`otf` for parse speed). Reduce asset sizes or fetch at runtime if you exceed the limit.

- Generated OG/Twitter image files are special Route Handlers that are **cached by default** unless they use request-time APIs or dynamic config.
- You can generate multiple images in the same file using `generateImageMetadata`.
- Static file versions (`opengraph-image.jpg`, `twitter-image.png`, etc.) are supported; `twitter-image` must be ≤ 5 MB and `opengraph-image` ≤ 8 MB or the build fails.
- For static image files, place an accompanying `opengraph-image.alt.txt` / `twitter-image.alt.txt` file in the same segment to set alt text.

#### `ImageResponse` (`next/og`) constructor

`ImageResponse` from `next/og` generates dynamic images with JSX/CSS. Constructor: `new ImageResponse(element, options)`. Defaults: `width` 1200, `height` 630. Options include `emoji` (default `'twemoji'`), `fonts` (`{ name, data, weight, style }[]`), `debug`, `status`, `statusText`, and `headers`. Examples are available in the [Vercel OG Playground](https://og-playground.vercel.app/). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/image-response.mdx)

### generateImageMetadata

|- Used in `opengraph-image.tsx` / `twitter-image.tsx` (or `icon.tsx`) to generate multiple images (e.g. icons, different sizes/variants) for one route segment; pairs with file-based image conventions. (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/generate-image-metadata.mdx)
|- `generateImageMetadata` accepts an optional `params` (the dynamic route params from the root down to the segment). It **must** return an **array** of objects, each with a unique `id`. As of **v16.0.0** that `id` (`Promise<string | number>`) and the image generation function's `params` (`Promise<object>`) are **promises** and must be awaited. ([generate-image-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-image-metadata.mdx))
|- Default-exported image generation function receives `id` (promise resolving to the returned `id` value, `string` or `number`) and `params` (promise resolving to the segment's dynamic route params). ([generate-image-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-image-metadata.mdx))

Image metadata object fields returned by `generateImageMetadata`:

| Field         | Type                                | Notes                                   |
| ------------- | ----------------------------------- | --------------------------------------- |
| `id`          | `string` (required)                 | Passed to the image function's `id` prop. |
| `alt`         | `string`                            |                                         |
| `size`        | `{ width: number; height: number }` |                                         |
| `contentType` | `string`                            | e.g. `image/png`.                       |

The default-exported image generation function receives `id` (a promise resolving to the `id` value, `string` or `number`) and `params` (a promise resolving to the segment's dynamic route params). ([generate-image-metadata](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-image-metadata.mdx))

### generateSitemaps

- Used in `sitemap.ts(x)` to programmatically split one route's sitemap into multiple sitemaps. `generateSitemaps` returns an **array of objects with an `id` property** (e.g. `[{ id: 0 }, { id: 1 }]`); the default `sitemap.ts` becomes the sitemap **index** that lists each split file. It is the default-exported `sitemap` function that returns the URL objects (`MetadataRoute.Sitemap`). (Source: https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/04-functions/generate-sitemaps.mdx)
- Generated sitemaps are served at **`/.../sitemap/[id].xml`** (e.g. `/product/sitemap/1.xml`). As of **v16.0.0** the `id` reaches the `sitemap` function as a **`Promise<string>`** and must be awaited (v15.0.0 made dev/prod URLs consistent).
- Search-engine limit: **50,000 URLs per sitemap** (e.g. Google). Split into multiple sitemaps for larger sites.
- **URL format gotcha (version-sensitive):** in development on **v13.3.2**, sitemaps are served at `/.../sitemap.xml/[id]` (e.g. `/product/sitemap.xml/1`); as of **v15.0.0** dev and prod URLs were unified to `/.../sitemap/[id].xml` (e.g. `/product/sitemap/1.xml`). ([generate-sitemaps](https://github.com/vercel/next.js/blob/canary/docs/01-app/03-api-reference/04-functions/generate-sitemaps.mdx))
([generate-sitemaps](https://nextjs.org/docs/app/api-reference/functions/generate-sitemaps))

### JSON-LD

Render JSON-LD structured data as a native `<script type="application/ld+json">` in a Server Component (`page.js` or `layout.js`). Since JSON-LD is structured data rather than executable JavaScript, the `next/script` component is not the right tool.

Sanitize the payload to avoid XSS injection from user-controlled strings. A minimal defense replaces `<` with its Unicode escape before injecting into the DOM:

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
  }}
/>
```

For production, review your organization's sanitization policy or use a community alternative such as `serialize-javascript`.

### Preventing flash before hydration

User preferences (locale, time zone, theme, persisted UI state) are unavailable during server rendering. To avoid a visible flash, run an inline `<script>` synchronously before the browser's first paint. Mark the corrected element with `suppressHydrationWarning` so React accepts the DOM value during hydration rather than client-rendering the boundary.

```tsx
<p id="event-date" suppressHydrationWarning>
  {new Date(event.date).toLocaleDateString()}
</p>
<script
  dangerouslySetInnerHTML={{
    __html: `document.getElementById("event-date").textContent=new Date("${event.date}").toLocaleDateString()`,
  }}
/>
```

For client-side navigations via `<Link>`, wrap the inline script in a Client Component and switch the script `type` to `text/plain` on the client (React warns about server-rendered `<script>`). Use `useId` to generate stable element IDs.

Strict Content Security Policies that disallow `'unsafe-inline'` require a nonce for inline scripts.

### File-based app icons

- `favicon.ico` is only valid at the root `/app` segment; `icon` and `apple-icon` files can live in any segment.
- Static image types: `favicon.ico`, `icon.(ico|jpg|jpeg|png|svg)`, `apple-icon.(jpg|jpeg|png)`.
- Generated icon files (`icon.tsx`, `apple-icon.tsx`) can also use `ImageResponse` and may receive a `params` promise.
- Generated icons are statically optimized by default unless they use request-time APIs or dynamic config.
- Multiple icons can be created with numbered suffixes (e.g., `icon1.png`, `icon2.png`) and are sorted lexically.
- You cannot generate a `favicon` icon; use `icon` or a `favicon.ico` file instead.
- `sizes="any"` is added to `.svg` icons or when image size cannot be determined.

### File-based manifest and robots

- `manifest.json` / `manifest.webmanifest` or `manifest.ts` / `manifest.js` at the root of `app/` provide the PWA web app manifest. Generated manifest files are special Route Handlers cached by default unless they use request-time APIs or dynamic config.
- `robots.txt` or `robots.ts` / `robots.js` configures crawler access. The `rules` object supports `userAgent`, `allow`, `disallow`, `crawlDelay`, and an `other` field for non-standard directives. Rules can be a single object or an array for per-bot configuration.
- `sitemap.xml` or `sitemap.ts` / `sitemap.js` produces a sitemap. It supports `images` and `videos` entries. Generated sitemaps are special Route Handlers cached by default unless they use request-time APIs or dynamic config.
- Static image files for Open Graph and Twitter are supported; `twitter-image` must be ≤ 5 MB and `opengraph-image` ≤ 8 MB or the build fails.

## Third-party scripts

Use `next/script` to load and optimize third-party scripts.
- Scripts in a layout load once for that layout's subtree; scripts in the root layout load once for the whole app.
- `next/script` strategies: `beforeInteractive` (server-rendered in `<head>`, executes before Next.js code but does not block hydration), `afterInteractive` (default, client-side after some hydration), `lazyOnload` (idle), `worker` (experimental web worker via Partytown; not supported in App Router).
- `beforeInteractive` scripts must be placed in a root layout (App Router) or `_document` (Pages Router). They run once per document load and are not re-executed on client-side navigations, including root-param changes.
- `onLoad`, `onReady`, `onError` handlers only work in Client Components (`'use client'`).
- Inline scripts need a stable `id` so Next.js can deduplicate/optimize them.
- Extra attributes (`nonce`, `data-*`) are forwarded to the final `<script>` element.

## Third-party libraries

The `@next/third-parties` package provides optimized components for common third-party integrations. It is currently experimental; install with latest or canary tags.
- Google Tag Manager: `<GoogleTagManager gtmId="GTM-XYZ" />` + `sendGTMEvent`.
- Google Analytics 4: `<GoogleAnalytics gaId="G-XYZ" />` + `sendGAEvent`.
- Google Maps Embed: `<GoogleMapsEmbed ... />`.
- YouTube Embed: `<YouTubeEmbed videoid="..." />` (uses `lite-youtube-embed`).

## Videos

Use the native HTML `<video>` tag for self-hosted/direct video files and `<iframe>` for externally hosted videos.
- Include accessible controls, fallback text, and `<track>` captions/subtitles.
- For autoplay, pair `autoPlay` with `muted` and `playsInline` for iOS compatibility.
- Stream external video embeds through a Server Component wrapped in `<Suspense>` to avoid blocking the page.
- Consider Vercel Blob, Cloudinary, Mux, or `next-video` for scalable hosting and adaptive streaming.

## Source URLs

- `Image` component: https://nextjs.org/docs/app/api-reference/components/image
- `Font` component: https://nextjs.org/docs/app/api-reference/components/font
- `Form` component: https://nextjs.org/docs/app/api-reference/components/form
- `Script` component: https://nextjs.org/docs/app/api-reference/components/script
- `metadata` API: https://nextjs.org/docs/app/api-reference/functions/generate-metadata
- `generateViewport`: https://nextjs.org/docs/app/api-reference/functions/generate-viewport
- `ImageResponse`: https://nextjs.org/docs/app/api-reference/functions/image-response
- `htmlLimitedBots`: https://nextjs.org/docs/app/api-reference/config/next-config-js/htmlLimitedBots
- `cssChunking`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cssChunking
- CSS-in-JS: https://nextjs.org/docs/app/guides/css-in-js
- Sass: https://nextjs.org/docs/app/guides/sass
- Analytics: https://nextjs.org/docs/app/guides/analytics
- Web app manifest: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
- Progressive Web Apps: https://nextjs.org/docs/app/guides/progressive-web-apps
- JSON-LD: https://nextjs.org/docs/app/guides/json-ld
- Preventing flash before hydration: https://nextjs.org/docs/app/guides/preventing-flash-before-hydration
- Third-party libraries: https://nextjs.org/docs/app/guides/third-party-libraries
- Videos: https://nextjs.org/docs/app/guides/videos
- App icons: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/app-icons
- Open Graph image convention: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/opengraph-image
- Robots: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots
- Sitemap: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap
- `instrumentation-client`: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client
- `instrumentationClientInject` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/instrumentationClientInject
- `route-segment-config/instant`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant
- `route-segment-config/prefetch`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/prefetch
- `route-segment-config/dynamicParams`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/dynamicParams
- `route-segment-config/maxDuration`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/maxDuration
- `route-segment-config/runtime`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime
- `route-segment-config/preferredRegion`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/preferredRegion
- `route-segment-config/index`: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config
- `error` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/error
- `default` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/default
- `dynamic-routes` convention: https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — CSS-in-JS additions (ingest 2026-08-30)

**CSS-in-JS (`css-in-js`)**
- During server rendering, styles are extracted to a global registry and flushed to the `<head>` so rules precede any content that uses them. (Source: https://nextjs.org/docs/app/guides/css-in-js)
- `styled-components@6` or newer is supported via a registry/`useServerInsertedHTML` setup. (Source: above)

### Canary Pages Router additions — API reference: components (ingest 2026-09-02)

Sourced from `docs/02-pages/04-api-reference/01-components/image-legacy.mdx`, `head.mdx`, and `link.mdx`.

**`next/legacy/image`**
- `next/legacy/image` is deprecated and will be removed in a future version. Prefer `next/image`. (Source: https://nextjs.org/docs/pages/api-reference/components/image-legacy)
- Required props: `src`, `alt`, `width`, `height` (except for static imports or `layout="fill"`). (Source: above)
- Layout modes: `intrinsic` (default), `fixed`, `responsive`, `fill`. `responsive`/`fill` parents need `display: block` / `position: relative`. (Source: above)
- `loader` prop overrides the loader configured in `next.config.js`. (Source: above)
- `sizes` is required for `responsive`/`fill` layouts and affects the generated `srcset`. (Source: above)
- `quality` defaults to `75`. (Source: above)
- `priority` disables lazy loading and preloads; use for LCP images. (Source: above)
- `placeholder` supports `blur` or `empty`; `blurDataURL` is auto-populated for static `.jpg/.png/.webp/.avif` imports. (Source: above)
- External URLs require `remotePatterns`; SVGs are blocked unless `unoptimized` or `dangerouslyAllowSVG` is enabled; unknown/animated formats are served as-is. (Source: above)

**`next/head` (Pages Router)**
- Import `Head` from `next/head` to add per-page `<head>` content in the Pages Router. It does not replace `next/document`'s `Head` in `_document`.
- Use `key` on tags (other than `<title>` and `<base>`, which Next.js deduplicates automatically) to avoid duplicate head entries; only the last matching `key` is rendered.
- Tags must be direct children of `<Head>` or wrapped in at most one `<React.Fragment>`/array level, or they won't be picked up on client-side navigations.
- The contents of `head` are cleared when the component unmounts, so each page must fully define its own head content.
- Do not use `next/head` to set attributes on `<html>` or `<body>` — that causes a `next-head-count is missing` error. For document-level changes, use a custom `_document`.
- Prefer `next/script` over manual `<script>` tags inside `next/head`. (Source: https://nextjs.org/docs/pages/api-reference/components/head)

**`<Link>` (Pages Router)**
- Pages Router `<Link>` supports `as`, `shallow`, and `locale` props in addition to the App Router props. (Source: https://nextjs.org/docs/pages/api-reference/components/link)

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary architecture / Pages Router additions — PostCSS (ingest 2026-09-02)

Sourced from `docs/02-pages/02-guides/post-css.mdx` (generated from shared App Router source). Merged into this reference because the CSS/PostCSS topic belongs here.

**PostCSS configuration**
- A custom PostCSS configuration file **completely disables** Next.js's built-in default PostCSS behavior. You must then configure every feature you need, including Autoprefixer, and install the required plugins manually. (Source: https://nextjs.org/docs/pages/guides/post-css)
- Next.js reads the PostCSS config from `postcss.config.json`, `.postcssrc.json`, or the `postcss` key in `package.json`. (Source: above)
- A `postcss.config.js` / `.postcssrc.js` is also supported; do **not use `require()`** to import PostCSS plugins — plugins must be provided as strings. (Source: above)
- If the same config file must support non-Next.js tools, use the interoperable object-based format: `module.exports = { plugins: { 'postcss-flexbugs-fixes': {}, 'postcss-preset-env': { autoprefixer: { flexbox: 'no-2009' }, stage: 3, features: { 'custom-properties': false } } } }`. (Source: above)
