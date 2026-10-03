# Server and Client Components

Reference: https://nextjs.org/docs/app/getting-started/server-and-client-components

## Default behavior

In the App Router, **Server Components are the default**. `page.tsx`, `layout.tsx`, and most UI start as Server Components.

## When to use Client Components

Use `"use client"` only when you need:

- State (`useState`, `useReducer`) and event handlers (`onClick`, `onChange`)
- Lifecycle logic (`useEffect`, `useLayoutEffect`)
- Browser-only APIs (`localStorage`, `window`, `navigator.geolocation`, `document`)
- Custom hooks that depend on any of the above

## When to use Server Components

- Fetch data from databases or APIs close to the source
- Use API keys / tokens / secrets without exposing them to the client
- Reduce JavaScript sent to the browser
- Improve First Contentful Paint and stream content progressively

## Edge Runtime constraints

> Applies to code running in the deprecated `runtime = 'edge'` route segment or in Proxy (formerly Middleware). Server Components normally run on the Node.js runtime; prefer Node.js for rendering and Proxy for request-time edge logic.

- **Runtime choice.** Next.js has two server runtimes: Node.js (default, full Node.js APIs) and the Edge Runtime (limited Web-standard APIs). ([edge runtime](https://nextjs.org/docs/app/api-reference/edge))
- **Deprecation.** `export const runtime = 'edge'` is deprecated. Remove the `runtime` export from route files and use the Node.js runtime for rendering; use `proxy.ts` for request-time edge logic. ([runtime segment config](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime))
- **Proxy runtime.** Proxy defaults to Node.js; the `runtime` segment config cannot be used in Proxy files and throws an error. ([proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy))
- **Cache Components incompatibility.** Cache Components requires the Node.js runtime; `runtime = 'edge'` routes must be migrated to Node.js or Proxy. ([migrating-to-cache-components](https://nextjs.org/docs/app/guides/migrating-to-cache-components#runtime--edge))
- **No ISR.** The Edge Runtime does not support Incremental Static Regeneration (ISR).
- **Limited Node.js API surface.** Native Node.js APIs such as `fs`, `path`, `http`, `net`, `crypto` (Node.js module), `child_process`, `cluster`, `os`, `stream`, `zlib`, `tls`, `dgram`, `dns`, `Buffer`, and direct `require()` are **not supported**. Packages must use ES Modules and Web-standard APIs only.
- **Supported APIs.** The Edge Runtime exposes Web-standard APIs including `fetch`, `Request`, `Response`, `Headers`, `URL`, `URLSearchParams`, `URLPattern`, `Blob`, `File`, `FormData`, `WebSocket`, `AbortController`, `ReadableStream`, `WritableStream`, `TransformStream`, `ReadableStreamDefaultReader`, `ReadableStreamBYOBReader`, `WritableStreamDefaultWriter`, `TextEncoder`, `TextDecoder`, `TextEncoderStream`, `TextDecoderStream`, `crypto`, `CryptoKey`, `SubtleCrypto`, `atob`/`btoa`, `structuredClone`, `queueMicrotask`, `setTimeout`/`setInterval`, `clearTimeout`/`clearInterval`, `Intl`, `WebAssembly`, and standard ECMAScript globals.
- **Next.js polyfill.** `AsyncLocalStorage` is polyfilled in the Edge Runtime.
- **Environment variables.** `process.env` works for build-time and runtime env vars.
- **No dynamic code evaluation.** `eval`, `new Function(...)`, `WebAssembly.compile`, and `WebAssembly.instantiate` are disabled. If unreachable code cannot be tree-shaken, opt out per file with the `unstable_allowDynamic` glob in Proxy config (`/proxy.ts`); if executed at runtime these statements throw.
- **Absolute URLs enforced.** Edge Runtime requires absolute URLs for fetches/redirects. ([proxy version history](https://nextjs.org/docs/app/api-reference/file-conventions/proxy#version-history))
- **Composition rule.** Use Node.js for data-heavy Server Components, Route Handlers, and Server Actions. Reserve Edge Runtime/Proxy for lightweight, request-time logic such as auth redirects, header/cookie manipulation, rewrites, and CORS.

## Boundary / composition rules

1. **Default-to-server.** In the App Router, `page.tsx`, `layout.tsx`, and ordinary UI are Server Components unless a client boundary is introduced.
2. **`'use client'` is a module-graph boundary.** When a file is marked with the directive, its imports and the components it directly renders enter the client bundle. Keep boundaries narrow and near interactive leaves.
3. **Start server-first.** Introduce `'use client'` at the smallest interactive boundary, and never promote a page/layout to client merely because one descendant needs browser behavior.
4. **Serializable boundary.** Props passed from Server Components to Client Components must be React-serializable. Functions, class instances, and non-serializable objects cannot cross directly; pass a Server Action (`'use server'`) reference instead.
5. **Interleaving rule.** Server Components passed as `children` or other props to a Client Component remain server-rendered; only their rendered output crosses the boundary. They are not imported into the Client Component's module graph.
6. **Provider rule.** React context cannot be created or consumed in a Server Component. Context providers require a `'use client'` component and should wrap as deeply/narrowly in the tree as practical.
7. **Third-party escape hatch.** Wrap third-party components that rely on hooks or browser APIs in a thin Client Component when the library lacks its own `'use client'` entry point.
8. **Environment poisoning protection.** Use `import 'server-only'` to enforce at build time that a module is never imported by client code; use `import 'client-only'` to enforce that a module requires browser APIs.
9. **TypeScript function props.** A Client Component prop typed as a function is allowed when its name is `action` or ends in `Action`; other function props are flagged by the TypeScript plugin. Server Functions are not distinguishable by type.
10. **Compound components across the boundary break.** A Server Component that imports a Client Component receives a client reference, so static subcomponents like `Menu.Item` are undefined. Keep compound pieces within one graph or expose them as named exports. ([server-and-client-boundary](https://nextjs.org/docs/app/guides/server-and-client-boundary))
11. **Native HTML can replace Client Components.** Built-ins such as `<details>`, `<form action={serverAction}>`, and `<video controls>` provide interactivity without a client boundary.
12. **Interleaving pass-through.** Cached components can accept non-serializable `children` or Server Action references as long as the cached function does not introspect them.
13. **Data enters during render.** A Server Component can read databases, files, or internal services directly during its render; there is no separate loader step. Pass the resulting data (or a pending Promise) to Client Components via props.
14. **Client Components render on the server too.** A Client Component renders to HTML on the initial request, then hydrates in the browser. On client-side navigation it renders only in the browser from the RSC payload.
15. **State never reaches the browser from Server Components.** Server Component code is not included in the client bundle; only its rendered output travels to the browser. To update it, re-render the route server-side.
16. **Promises can stream to clients.** A Server Component can start a fetch and pass the pending Promise to a Client Component, which unwraps it with React's `use()` inside a `<Suspense>` boundary.
17. **Avoid broad `'use client'` boundaries.** A Server Component that dynamically imports a Client Component still eagerly renders the Client Component on the server during SSR. Keep `'use client'` boundaries narrow and near interactive leaves. Dynamic imports of Server Components only lazy-load their **Client children**, not the Server Component itself; for a Client-only island, use `next/dynamic` inside a Client Component or `React.lazy` + `Suspense`. ([lazy-loading](https://nextjs.org/docs/app/guides/lazy-loading))

## Rendering pipeline and RSC payload

- Next.js splits server rendering into chunks by route segment, including parallel-route slots whether or not a slot is currently displayed. Account for hidden slots when diagnosing unexpected server work.
- Server Components render into the React Server Component payload. This compact serialized payload contains their rendered result, placeholders and JavaScript references for Client Components, and props passed across the Server-to-Client boundary.
- On the initial load, prerendered HTML provides the immediate non-interactive view, the RSC payload reconciles the Server and Client trees, and JavaScript hydrates Client Components by attaching interactivity.
- On subsequent client navigations, Next.js prefetches and caches the RSC payload. Client Components render in the browser from that payload without receiving new server-rendered HTML.

Source: [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components), Next.js 16.3.8.

### Dynamic imports

- `next/dynamic` is for lazy-loading **Client Components** and libraries. Server Components are automatically code-split and streamed.
- If you dynamically import a Server Component, only its **Client Component children** are lazy-loaded; the Server Component itself is not. `ssr: false` is not supported in Server Components—move it into a Client Component.
- Magic comments such as `/* webpackIgnore: true */` / `/* turbopackIgnore: true */` skip bundling a dynamic import for runtime-only modules. `/* turbopackOptional: true */` suppresses build errors when a module may not exist (Turbopack only).

## Interleaving pattern

```tsx
// Server Component page
import Modal from './modal' // 'use client'
import Cart from './cart'    // Server Component

export default function Page() {
  return (
    <Modal>
      <Cart />
    </Modal>
  )
}
```

`Cart` runs on the server; `Modal` only receives rendered output, not `Cart`'s source code.

### Environment protection

- Only env vars prefixed with `NEXT_PUBLIC_` reach the client bundle. Variables without that prefix are replaced with an empty string in the client bundle.
- Use the `server-only` package to mark modules that must never be imported by Client Components.
- Use the `client-only` package to mark modules that require browser APIs.
- Installing `server-only` / `client-only` is optional; Next.js handles these imports internally for clearer error messages, and provides its own type declarations for TypeScript configurations using [`noUncheckedSideEffectImports`](https://www.typescriptlang.org/tsconfig/#noUncheckedSideEffectImports).
- **Server Actions dispatch sequentially per client.** Next.js dispatches Server Actions one at a time per client; do not rely on `Promise.all` to parallelize actions from the client. Parallel work belongs inside a single Server Action, a Server Component, or a Route Handler. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))

### Avoiding full-page client boundaries

- Default to Server Components for pages and layouts.
- Keep `'use client'` directives at the smallest interactive leaf.
- A Client Component can receive Server Component output as `children`/`props` (interleaving) — do not import a Server Component into a Client Component's module graph.
- Third-party libraries that lack their own `'use client'` entry point should be wrapped in a thin local Client Component, not promoted to a layout/page.
- Prefer native HTML interactivity (`<form action>`, `<details>`, `<video controls>`) to avoid extra client JS.

### Dynamic imports

- `next/dynamic` is for lazy-loading **Client Components** and libraries. Server Components are automatically code-split and streamed.
- If you dynamically import a Server Component, only its **Client Component children** are lazy-loaded; the Server Component itself is not. `ssr: false` is not supported in Server Components—move it into a Client Component.
- Magic comments such as `/* webpackIgnore: true */` / `/* turbopackIgnore: true */` skip bundling a dynamic import for runtime-only modules. `/* turbopackOptional: true */` suppresses build errors when a module may not exist (Turbopack only).

## Forms and progressive enhancement

- Use `form action={serverAction}` for submissions that work without JavaScript (Server Actions with progressive enhancement).
- For interactive forms, use `useActionState` to read returned state and show validation messages.
- Keep forms in Server Components by default; move client-only validation/presentation into small Client Components.
- Next.js 16+ provides a `next/form` `Form` component. When `action` is a string, it performs a client-side navigation with the form data encoded as search params, and prefetches the destination path (App Router only). When `action` is a function, it behaves like a React form and invokes the Server Action. The string form supports `replace`, `scroll`, and `prefetch` props; the function form ignores `replace` and `scroll`.
- `Form` caveats: `method`, `encType`, `target` (and per-button `formMethod`, `formEncType`, `formTarget`) override `Form` behavior and fall back to native browser behavior; use a plain `<form>` if you need those props. `onSubmit` with `event.preventDefault()` cancels `Form` navigation. `formAction` on a button/input can override the action but does not support prefetching. File inputs in a string-action form submit filenames, not file objects.
- **Server Actions dispatch sequentially per client.** Do not rely on `Promise.all` across multiple client-triggered actions; parallel work belongs inside a single Server Action, Server Component, or Route Handler. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))

## Preserving UI state with Cache Components

With Cache Components enabled, Next.js preserves up to 3 routes across navigations using React's `<Activity>` component. The DOM is kept in the document (hidden with `display: none`), so React state and DOM state such as form drafts, scroll positions, expanded `<details>` elements, and video progress are retained.

To reset transient state when a page is hidden (e.g. dropdowns, status messages, dialog open state), use a `useLayoutEffect` cleanup:

```tsx
useLayoutEffect(() => {
  return () => {
    setIsOpen(false)
    setStatus('idle')
  }
}, [])
```

Use `useRouter().bfcacheId` as a React `key` on a fragment to reset an entire subtree on push/replace navigations while still restoring state on browser back/forward. For new code, prefer per-pattern resets.

For state that should reset when the authenticated user changes, key the component by `userId` or reset explicitly in an effect.

Source: [Preserving UI state](https://nextjs.org/docs/app/guides/preserving-ui-state)

## Security checklist

- Authenticate and authorize inside Server Actions, Route Handlers, and the Data Access Layer — never trust UI gating.
- Keep secrets, tokens, and passwords out of client bundles; only `NEXT_PUBLIC_`-prefixed env vars reach the client.
- Filter server data into DTOs before passing to Client Components.
- Use React Taint APIs (`experimental_taintObjectReference`, `experimental_taintUniqueValue`) and/or the `server-only` package to prevent accidental exposure of sensitive data.
- If `authInterrupts` is enabled, throw `unauthorized()` / `forbidden()` from `next/navigation` to render `unauthorized.tsx` / `forbidden.tsx` automatically.
- The `forbidden.tsx` file renders a 403 UI when `forbidden()` is invoked. It accepts no props.
- The `unauthorized.tsx` file renders UI when `unauthorized()` is invoked during authentication.
- Treat every Server Action as a public POST endpoint; validate inputs, check ownership, and constrain return values.
- Use nonces for strict CSP only if dynamic rendering is acceptable; nonces disable PPR, ISR/CDN caching, and static optimization. Prefer hash-based CSP or `unsafe-inline` when dynamic rendering is not acceptable.
- **Server Actions dispatch sequentially per client.** Next.js dispatches Server Actions one at a time per client; do not rely on `Promise.all` to parallelize actions from the client. Parallel work belongs inside a single Server Action, a Server Component, or a Route Handler. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))
- **Choosing a cache update after mutation.** After a Server Action mutates data, use `updateTag` for immediate read-your-own-writes, `revalidateTag` for stale-while-revalidate, `revalidatePath` when tagging is awkward, and `refresh` when state outside the cache changed. ([server-actions](https://nextjs.org/docs/app/guides/server-actions))
- **`server-only` is optional but still recommended.** Next.js provides the import internally; explicitly `import 'server-only'` if you want TypeScript/eslint rules to catch client-side imports of server-only modules. ([data-security](https://nextjs.org/docs/app/guides/data-security))

## Common mistakes to prevent

- Marking an entire page or layout `"use client"` when only a small subtree needs it.
- Passing non-serializable props (functions, class instances) from server to client.
- Importing server-only secrets into a Client Component.
- Using `useState` / `useEffect` / `useContext` in a Server Component.

### Advice for library authors

If you publish a component library, add `"use client"` to entry points that rely on client-only features so consumers can import them into Server Components without wrappers. Some bundlers may strip the directive; configure your build tool (e.g. esbuild/tsup) to preserve it.

## Source URLs

- Server and Client Components overview: https://nextjs.org/docs/app/getting-started/server-and-client-components
- Server and Client Boundary guide: https://nextjs.org/docs/app/guides/server-and-client-boundary
- `use client` directive: https://nextjs.org/docs/app/api-reference/directives/use-client
- `use server` directive: https://nextjs.org/docs/app/api-reference/directives/use-server
- `server-only` / `client-only`: https://www.npmjs.com/package/server-only
- Interactive apps guide: https://nextjs.org/docs/app/guides/interactive-apps
- Data security guide: https://nextjs.org/docs/app/guides/data-security
- CSP guide: https://nextjs.org/docs/app/guides/content-security-policy
- Edge Runtime: https://nextjs.org/docs/app/api-reference/edge
- Runtime segment config: https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/runtime
- Proxy file convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Proxy version history: https://nextjs.org/docs/app/api-reference/file-conventions/proxy#version-history
- Migrating to Cache Components (`runtime = 'edge`): https://nextjs.org/docs/app/guides/migrating-to-cache-components#runtime--edge
- Authentication: https://nextjs.org/docs/app/guides/authentication
- `authInterrupts`: https://nextjs.org/docs/app/api-reference/config/next-config-js/authInterrupts
- Lazy loading: https://nextjs.org/docs/app/guides/lazy-loading
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- Preserving UI state (Activity): https://nextjs.org/docs/app/guides/preserving-ui-state
- Forms: https://nextjs.org/docs/app/guides/forms
- Progressive Web Apps: https://nextjs.org/docs/app/guides/progressive-web-apps
- `useActionState`: https://react.dev/reference/react/useActionState
- Single-page applications: https://nextjs.org/docs/app/guides/single-page-applications
- Third-party libraries: https://nextjs.org/docs/app/guides/third-party-libraries
- View transitions: https://nextjs.org/docs/app/guides/view-transitions
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- `forbidden` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/forbidden
- `unauthorized` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/unauthorized
- `Form` component: https://nextjs.org/docs/app/api-reference/components/form
- `use-link-status`: https://nextjs.org/docs/app/api-reference/functions/use-link-status
- MCP / `next-devtools-mcp`: https://nextjs.org/docs/app/guides/mcp
- Server Actions: https://nextjs.org/docs/app/guides/server-actions
- Preserving UI state: https://nextjs.org/docs/app/guides/preserving-ui-state
- Preventing flash before hydration: https://nextjs.org/docs/app/guides/preventing-flash-before-hydration
- Optimizing prefetching: https://nextjs.org/docs/app/guides/optimizing-prefetching
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — auth/boundary additions (ingest 2026-08-30)

**Authentication (`authentication`)**
- A Data Access Layer (DAL) protects data fetched at request time, but for static routes that share data between users the data is fetched at build time, not request time. Use Proxy to protect static routes. (Source: https://nextjs.org/docs/app/guides/authentication)
- With `cacheComponents` enabled, reading the session and caching per-user data is the documented pattern — see "Authentication with Cache Components". (Source: above)

**Authentication with Cache Components (`authentication-with-cache-components`)**
- `cacheLife` and `cacheTag` for per-user data should be derived from the **session token** (e.g. the value of the session cookie), not from `cookies()` as an object, because the object itself is not serializable as a cache input. (Source: https://nextjs.org/docs/app/guides/authentication-with-cache-components)
- `use cache: private` can be used to cache a rendered layout/template per user in the browser when it reads request-time APIs. (Source: above)
- Do not store sensitive values such as raw passwords in cache tags; tags are not encrypted and may be exposed in cache keys/headers. (Source: above)
