# Turbopack and Build

Reference: https://nextjs.org/docs/app/guides/building

## Turbopack in Next.js 16+

- Turbopack is the default bundler for `next dev` and `next build`.
- Remove `--turbopack` / `--turbo` from `package.json` scripts.
- To keep Webpack, use `--webpack` explicitly.
- A custom `webpack` config will fail a default `next build` in v16. Options:
  - Use `--turbopack` to ignore the webpack config.
  - Migrate to Turbopack-compatible options.
  - Use `--webpack` to opt out.

## Build output

`next build` prints a route table:

| Symbol | Name | Behavior |
|---|---|---|
| `○` | Static | Fully prerendered at build time. |
| `◐` | Partial Prerender | Static shell + dynamic streaming. |
| `●` | SSG | Prerendered static HTML. |
| `ƒ` | Dynamic | Server-rendered per request. |

With `cacheComponents`, PPR is the default model.

## Prerender errors

Cache Components catches uncached/runtime data at build time. Common fix options printed in the error:

- `[stream]` — wrap access in `Suspense`.
- `[cache]` — cache the access with `"use cache"`.
- `[block]` — set `export const instant = false` to allow a blocking route.

Use `next build --debug-prerender` for source-mapped server stack traces. **Do not deploy `--debug-prerender` builds.**

## Turbopack tracing

Generate a trace during dev:

```bash
pnpm dev --internal-trace
npx next internal trace .next-profiles/trace-turbopack.bin
```

View at https://trace.nextjs.org/.

## Bundle analysis

- Webpack: `@next/bundle-analyzer`.
- Turbopack: experimental `pnpm next experimental-analyze` (see package bundling guide).

## Common build / HMR failures

- Missing `/_next/static/chunks/...` usually points to stale `.next` artifacts, a dead dev server, or a bundler mismatch — not application components.
- HMR chunk mismatch: restart `next dev` and clear `.next` only after identifying why stale artifacts formed.
- Turbopack loader limitations: no `importModule`, `loadModule`, `emitFile`; partial `fs` support.

## Source URLs

- Building: https://nextjs.org/docs/app/guides/building
- Turbopack config: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack
- Package bundling / bundle analyzer: https://nextjs.org/docs/app/guides/package-bundling
- `next CLI`: https://nextjs.org/docs/app/api-reference/cli/next
- Version 16 upgrade guide (Turbopack section): https://nextjs.org/docs/app/guides/upgrading/version-16
