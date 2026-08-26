# Configuration

Reference: https://nextjs.org/docs/app/api-reference/config/next-config-js

## `next.config.*`

Supported extensions: `.js`, `.mjs`, `.ts`. TypeScript config is recommended:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // options
}

export default nextConfig
```

## Version-sensitive config (v16+)

### `cacheComponents`

Enables Cache Components, Partial Prerendering by default, `use cache`, `cacheLife`, `cacheTag`.

```ts
const nextConfig: NextConfig = {
  cacheComponents: true,
}
```

Requires Node.js runtime. Migrate any `runtime = 'edge'` exports.

### `turbopack`

Turbopack is the default bundler in v16 for `next dev` and `next build`. Configure it at top level:

```ts
const nextConfig: NextConfig = {
  turbopack: {
    // root, rules, resolveAlias, resolveExtensions, debugIds
  },
}
```

- Remove `--turbopack` / `--turbo` from scripts.
- Keep Webpack with `--webpack` if a custom webpack config is required.
- `experimental.turbopack` is deprecated; migrate to top-level `turbopack`.

### `serverActions`

```ts
const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
      bodySizeLimit: '2mb',
    },
  },
}
```

- `allowedOrigins` — extra safe origins for CSRF check.
- `bodySizeLimit` — default 1MB.

## Common options

| Option | Purpose |
|---|---|
| `output: 'standalone'` | Minimal server output for Docker/Node. |
| `output: 'export'` | Static export (limited feature support). |
| `images.remotePatterns` | Allowed remote image hostnames. |
| `headers` / `redirects` / `rewrites` | Static routing rules. |
| `pageExtensions` | Custom page/proxy extensions. |
| `logging` | Dev-server logging behavior. |
| `agentRules` | Set to `false` to opt out of auto-generated `AGENTS.md`. |

## Removed / renamed v15 → v16

- `experimental.ppr` removed; PPR is default under `cacheComponents`.
- `experimental.useCache` / `experimental.dynamicIO` removed; use `cacheComponents`.
- `unstable_rootParams` removed; use `next/root-params`.
- `runtime` config edge usage deprecated with Cache Components.
- `publicRuntimeConfig` / `serverRuntimeConfig` removed; use env vars.

## Source URLs

- `next.config.js` overview: https://nextjs.org/docs/app/api-reference/config/next-config-js
- `cacheComponents`: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents
- `turbopack`: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack
- `serverActions`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `images`: https://nextjs.org/docs/app/api-reference/config/next-config-js/images
- `logging`: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- Version 16 upgrade guide: https://nextjs.org/docs/app/guides/upgrading/version-16
