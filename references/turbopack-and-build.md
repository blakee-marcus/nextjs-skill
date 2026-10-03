# Turbopack and Build

Reference: https://nextjs.org/docs/app/guides/building

## Turbopack in Next.js 16+

- Turbopack is the default bundler for `next dev` and `next build`.
- Remove `--turbopack` / `--turbo` from `package.json` scripts.
- To keep Webpack, use `--webpack` explicitly.
- A custom `webpack()` config in `next.config.js` is not recognized by Turbopack. Options:
  - Migrate to the `turbopack` config (`resolveAlias`, `resolveExtensions`, `rules`, etc.).
  - Use `--webpack` to opt out.

## Build output

`next build` creates an optimized production build and prints a route table. As of Next.js 16.0.0, the command no longer reports JavaScript bundle-size metrics; use `next experimental-analyze` when bundle composition is the question.

| Symbol | Name | Behavior |
|---|---|---|
| `○` | Static | Fully prerendered at build time. |
| `◐` | Partial Prerender | Static shell + dynamic streaming. |
| `●` | SSG | Prerendered static HTML. |
| `ƒ` | Dynamic | Server-rendered per request. |

With `cacheComponents`, PPR is the default model. `◐` rows appear only for real uncached I/O; a synchronous in-memory value prerenders as `○`.

## Prerender errors

Cache Components catches uncached/runtime data at build time. Common fix options printed in the error:

- `[stream]` — wrap access in `Suspense`.
- `[cache]` — cache the access with `"use cache"`.
- `[block]` — set `export const instant = false` to allow a blocking route.

Use `next build --debug-prerender` for source-mapped server stack traces. This disables server minification (`experimental.serverMinification`, `experimental.turbopackMinify`), enables server source maps (`experimental.serverSourceMaps`), and continues past the first prerender error (`experimental.prerenderEarlyExit = false`). **Do not deploy `--debug-prerender` builds.**

Build only specific routes with `--debug-build-paths=<patterns>`; supports comma-separated file paths, glob patterns, and `!`-prefixed excludes. In `src/` projects paths resolve with or without the `src/` prefix.

## Instrumentation

`instrumentation.ts|js` at project root (or `src/` root) exports a `register()` function that runs once when a new server instance starts. Use it to initialize OpenTelemetry, monitoring, or imports with side effects. It must complete before the server handles requests. Pair with `instrumentation-client.ts|js` for client-side startup code.

## Next.js CLI (`next`)

Source: https://nextjs.org/docs/app/api-reference/cli/next (v16.3.8, updated 2026-08-25)

```bash
pnpm next [command] [options]
# or: npx next / yarn next / bunx next
```

> With `npm run`, use `--` before CLI flags so npm forwards them to `next`. Not required for `pnpm`, `yarn`, or `bun`.

### Commands

| Command | Description |
|---|---|
| `dev` | Starts dev server with HMR, error reporting |
| `build` | Creates optimized production build, prints route table |
| `start` | Starts production server (requires `next build` first) |
| `info` | Prints system details for bug reports |
| `telemetry` | Enable/disable anonymous telemetry |
| `typegen` | Generate TypeScript definitions for routes without full build |
| `upgrade` | Upgrade Next.js application to latest version |
| `experimental-analyze` | Analyze bundle output via Turbopack (no build artifacts) |

> Running `next` without a command is an alias for `next dev`.

### Common flags

| Flag | Command | Description |
|---|---|---|
| `--turbopack` / `--turbo` | `dev`, `build` | Force enable Turbopack (default) |
| `--webpack` | `dev`, `build` | Force enable Webpack |
| `-p, --port <port>` | `dev`, `start` | Port number (default 3000, env: `PORT`) |
| `-H, --hostname <host>` | `dev`, `start` | Hostname (default `0.0.0.0`) |
| `-d, --debug` | `build` | Verbose build output (rewrites, redirects, headers) |
| `--profile` | `build` | Enable production React profiling |
| `--no-mangling` | `build`, `experimental-analyze` | Disable name mangling (debug only) |
| `--experimental-app-only` | `build` | Build only App Router routes |
| `--debug-prerender` | `build` | Debug prerender errors |
| `--debug-build-paths=<patterns>` | `build` | Build only specific routes |
| `--experimental-cpu-prof` | `dev`, `build`, `start` | CPU profiling via V8 |
| `--experimental-https` | `dev` | HTTPS with self-signed cert |
| `--experimental-https-key/cert/ca <path>` | `dev` | Custom HTTPS cert/key/CA |
| `--experimental-upload-trace <url>` | `dev` | Upload a subset of the debugging trace to a remote URL; external transmission |
| `--experimental-build-mode [mode]` | `build` | Experimental `compile`, `generate`, or `default` build mode |
| `--keepAliveTimeout <ms>` | `start` | Keep-alive timeout for downstream proxies |
| `--output` (`-o`) | `experimental-analyze` | Write analysis files to `.next/diagnostics/analyze` |
| `--revision <revision>` | `upgrade` | Version/tag to upgrade to |

> **Good to know:** `PORT` cannot be set in `.env` because the HTTP server boots before any other code runs.

> **Development builds** output to `.next/dev`, allowing `next dev` and `next build` to run concurrently.

### Diagnostics, telemetry, and upgrades

- `next info` reports OS, CPU/memory, package-manager binaries, relevant package versions, and Next.js config for bug reports; `next info --verbose` collects additional detail.
- `next telemetry --enable` and `next telemetry --disable` control anonymous telemetry participation.
- `next upgrade [directory] --revision <latest|canary|version> --verbose` upgrades a project; without `--revision`, it follows the currently installed release channel.

### `next experimental-analyze`

Turbopack-powered bundle analysis (v16.1.0+). Does not produce a build.

```bash
npx next experimental-analyze              # starts interactive server
npx next experimental-analyze --output     # writes static report to .next/diagnostics/analyze
```

Supports `--no-mangling`, `--profile`, and `--port` (default 4000).

### `next typegen`

Generates TypeScript definitions for routes independently of a build. Useful for CI:

```bash
next typegen && tsc --noEmit
```

Output to `<distDir>/types` (`.next/dev/types` in dev, `.next/types` in prod). Also regenerates `next-env.d.ts`. Loads `next.config.*` using the production build phase — ensure required env vars are available.

> Add `next-env.d.ts` to `.gitignore`.

### `next upgrade`

```bash
npx next upgrade --revision latest   # or canary, 15.0.0, etc.
```

### CPU profiling

```bash
next build --experimental-cpu-prof
next dev --experimental-cpu-prof
next start --experimental-cpu-prof
```

Profile files go to `.next-profiles/`. Naming convention:
- `next dev`: `dev-main-*` (parent), `dev-server-*` (child — usually what to analyze)
- `next build` (Turbopack): `build-main-*`, `build-turbopack-*`
- `next build` (Webpack): `build-main-*`, `build-webpack-client-*`, `build-webpack-server-*`, `build-webpack-edge-server-*`
- `next start`: `start-main-*`

### HTTPS in development

```bash
next dev --experimental-https
next dev --experimental-https --experimental-https-key ./key.pem --experimental-https-cert ./cert.pem
```

Uses `mkcert` for a locally trusted cert. For production, use certificates from a trusted authority.

### `--debug-prerender`

```bash
next build --debug-prerender
```

Enables several experimental options: `experimental.serverMinification = false`, `experimental.turbopackMinify = false`, `experimental.serverSourceMaps = true`, `experimental.prerenderEarlyExit = false`. **Do not deploy `--debug-prerender` builds.**

### `--debug-build-paths`

```bash
next build --debug-build-paths="app/page.tsx"
next build --debug-build-paths="app/**/page.tsx,!app/admin/**"
```

Supports comma-separated paths, glob patterns, and `!`-prefixed excludes. In `src/` projects paths resolve with or without the `src/` prefix.

### `--keepAliveTimeout`

Use behind a downstream proxy that reuses keep-alive connections. Set Next.js' timeout higher than the downstream proxy's timeout so the proxy does not reuse a connection that Node.js has already closed:

```bash
next start --keepAliveTimeout 70000
```

### Pass Node.js arguments

```bash
NODE_OPTIONS='--inspect' next build
NODE_OPTIONS='--throw-deprecation' next dev
```

## Turbopack tracing

Generate a trace during dev:

```bash
pnpm dev --internal-trace
npx next internal trace .next-profiles/trace-turbopack.bin
```

View at https://trace.nextjs.org/. CPU profiling via `--experimental-cpu-prof` saves `.cpuprofile` files to `.next-profiles/` for `next dev`, `next build`, and `next start`. For `next build` with Turbopack it produces `build-main-*` and `build-turbopack-*` profiles; with Webpack it also produces `build-webpack-client-*`, `build-webpack-server-*`, and `build-webpack-edge-server-*` profiles.

## Bundle analysis

- **Webpack**: `ANALYZE=true npm run build` with `@next/bundle-analyzer` generates visual bundle reports.
- **Turbopack (v16.1+)**: `npx next experimental-analyze` opens an interactive bundle analyzer integrated with Turbopack's module graph. Use `--output` to write a static report to `.next/diagnostics/analyze` for sharing or diffing. Supports `--no-mangling`, `--profile`, and `--port` (default 4000).

## Turbopack `import.meta.env`

Turbopack supports built-in environment metadata through `import.meta.env`. Not available with webpack.

| Property   | Type      | Value                                                              |
| ---------- | --------- | ------------------------------------------------------------------ |
| `DEV`      | `boolean` | Whether `MODE` is not `"production"`                               |
| `PROD`     | `boolean` | Whether `MODE` is `"production"`                                   |
| `MODE`     | `string`  | The compile-time `NODE_ENV`, defaulting to `"development"`         |
| `BASE_URL` | `string`  | The Next.js `basePath`, with a trailing slash (`"/"` by default)   |
| `SSR`      | `boolean` | `true` in server bundles and `false` in browser and client bundles |

These values are statically analyzed so Turbopack can remove unreachable branches. `BASE_URL` reflects the Next.js `basePath` configuration. Custom `VITE_*` variables, Vite custom modes, `envPrefix`, and `envDir` are not supported.

## Turbopack `import.meta.glob`

Turbopack supports `import.meta.glob()`, a Vite-compatible API for importing multiple modules at once using glob patterns. Not available with webpack.

```js
const modules = import.meta.glob('./dir/*.js')
// { './dir/foo.js': () => import('./dir/foo.js'), ... }
```

Options: `eager: true` (import synchronously), `import: 'default'` (named export), `query: '?raw'` (needs matching `turbopack.rules`), `base`, `caseSensitive`. TypeScript types included automatically with `"moduleResolution": "bundler"`. The `as` option is not supported; use `query` + matching rule instead.

### Multiple patterns and negation

Pass an array of glob patterns. Prefix with `!` to exclude:

```js
const modules = import.meta.glob(['./dir/*.js', './other/*.js'])
const withoutTests = import.meta.glob(['./src/**/*.js', '!**/*.test.js'])
```

### Query strings

The `query` option accepts a string or an object (URL-encoded). Unlike Vite, Turbopack has no built-in `?raw` or `?url` handling — match the query with a `turbopack.rules` entry:

```ts
// next.config.ts
turbopack: {
  rules: {
    '*.txt': { condition: { query: '?raw' }, type: 'text' },
  },
}
```

## Optimizing large bundles

- Icon and utility libraries with many exports can bloat bundles. Use `optimizePackageImports` in `next.config.js` for Webpack; Turbopack analyzes and optimizes imports automatically without this config.
- Move heavy client-only rendering (syntax highlighting, charting, markdown parsing, etc.) into Server Components when the work does not require browser APIs or user interaction.
- App Router Server Components and Route Handlers bundle imported packages by default; opt specific packages out with `serverExternalPackages` when needed.

## Common build / HMR failures

- Missing `/_next/static/chunks/...` usually points to stale `.next` artifacts, a dead dev server, or a bundler mismatch — not application components.
- HMR chunk mismatch: restart `next dev` and clear `.next` only after identifying why stale artifacts formed.
- Development builds output to `.next/dev`, allowing `next dev` and `next build` to run concurrently without conflicts.
- Turbopack loader limitations: no `importModule`, `loadModule`, `emitFile`; partial `fs` support.
- Magic comments: `webpackIgnore` / `turbopackIgnore` skip bundling a dynamic import for runtime-only modules. `turbopackOptional` suppresses build errors when a module might not exist (runtime throws if executed). `webpackOptional` is not supported.
- `next/dynamic` is for Client Components only in App Router; Server Components are automatically code-split. Use `ssr: false` only inside Client Components.
- Tailwind CSS v3 is supported by Turbopack since Next.js 13.1. Use `tailwindcss@^3 postcss autoprefixer` and the `@tailwind` directives for v3 projects.
- On platforms without native bindings (FreeBSD, OpenBSD, etc.), Next.js falls back to WASM bindings, but WASM does not support Turbopack. Use `--webpack` on those platforms.
- Turbopack resolves modules from the project root only; files outside the root (e.g. linked packages via `npm link`) need `turbopack.root` configured to the shared parent directory.

## Source URLs

- Building: https://nextjs.org/docs/app/guides/building
- Turbopack config: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack
- Package bundling / bundle analyzer: https://nextjs.org/docs/app/guides/package-bundling
- `next CLI`: https://nextjs.org/docs/app/api-reference/cli/next
- `create-next-app`: https://nextjs.org/docs/app/api-reference/cli/create-next-app
- Turbopack reference: https://nextjs.org/docs/app/api-reference/turbopack
- Version 16 upgrade guide (Turbopack section): https://nextjs.org/docs/app/guides/upgrading/version-16
- Instrumentation: https://nextjs.org/docs/app/guides/instrumentation
- `instrumentation` convention: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
- `instrumentation-client` convention: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation-client
- CI build caching: https://nextjs.org/docs/app/guides/ci-build-caching
- Lazy loading: https://nextjs.org/docs/app/guides/lazy-loading
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Local development: https://nextjs.org/docs/app/guides/local-development
- Sass: https://nextjs.org/docs/app/guides/sass
- Tailwind v3: https://nextjs.org/docs/app/guides/tailwind-v3-css
- Scripts: https://nextjs.org/docs/app/guides/scripts
- Third-party libraries: https://nextjs.org/docs/app/guides/third-party-libraries
- View transitions: https://nextjs.org/docs/app/guides/view-transitions
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- Single-page applications: https://nextjs.org/docs/app/guides/single-page-applications
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- Multi-tenant: https://nextjs.org/docs/app/guides/multi-tenant
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary architecture additions — Next.js Compiler (SWC) (ingest 2026-09-02)

Sourced from `docs/03-architecture/nextjs-compiler.mdx`. Merged into the build reference because compiler/transform behavior is part of the build pipeline.

**Next.js Compiler (SWC)**
- The Next.js Compiler, written in Rust using SWC, replaces Babel for individual files and Terser for minification. It is enabled by default since Next.js 12 and is ~17x faster than Babel. (Source: https://nextjs.org/docs/architecture/nextjs-compiler)
- If an existing `.babelrc` or Babel configuration is present, Next.js automatically falls back to Babel for transforming individual files. (Source: above)
- **Styled Components**: enable via `compiler.styledComponents: true` in `next.config.js`. `ssr` and `displayName` transforms are the main requirements. Advanced options: `displayName`, `ssr`, `fileName`, `topLevelImportPaths`, `meaninglessFileNames`, `minify`, `transpileTemplateLiterals`, `namespace`, `pure`, `cssProp`. (Source: above)
- **Jest**: the compiler transpiles tests and `next/jest` auto-mocks CSS/image imports, sets up SWC `transform`, loads `.env` files, and ignores `node_modules`/`.next`. (Source: above)
- **Relay**: configure `compiler.relay` with `src`, `artifactDirectory`, `language`, `eagerEsModules`. Place `artifactDirectory` **outside the `pages` directory**; otherwise generated files are treated as routes and break production builds. (Source: above)
- **Remove React properties**: `compiler.reactRemoveProperties: true` (default removes `^data-test`) or custom `{ properties: ['^data-custom$'] }`. Regex syntax is Rust's `regex` crate syntax, not JavaScript `RegExp`. (Source: above)
- **Remove console**: `compiler.removeConsole: true` removes all `console.*` calls; `{ exclude: ['error'] }` keeps `console.error`. (Source: above)
- **Legacy decorators**: auto-detected from `experimentalDecorators` in `jsconfig.json`/`tsconfig.json`. Only for compatibility — not recommended in new apps. (Source: above)
- **importSource**: auto-detected from `jsxImportSource` in `jsconfig.json`/`tsconfig.json`. (Source: above)
- **Emotion**: configure `compiler.emotion` with `sourceMap`, `autoLabel`, `labelFormat`, `importMap`. (Source: above)
- **Minification**: SWC minifier is used by default since v13; `swcMinify` was removed in v15 — minification can no longer be customized via `next.config.js`. (Source: above)
- **Module transpilation**: built-in `transpilePackages` replaces `next-transpile-modules`. (Source: above)
- **Modularize imports**: superseded by `optimizePackageImports` in Next.js 13.5. (Source: above)
- **Define**: `compiler.define` replaces variables at build time across all environments; `compiler.defineServer` replaces only in server+edge code. (Source: above)
- **Build lifecycle hooks**: `compiler.runAfterProductionCompile: async ({ distDir, projectDir }) => ...` runs after production compilation but before type checking and static generation. (Source: above)
- **Experimental SWC trace profiling**: `experimental.swcTraceProfiling: true` writes `swc-trace-profile-<timestamp>.json` to `.next/`. (Source: above)
- **Experimental SWC plugins**: `experimental.swcPlugins: [['plugin', { ...options }]]` where the plugin path is an npm module or absolute path to a `.wasm` binary.
