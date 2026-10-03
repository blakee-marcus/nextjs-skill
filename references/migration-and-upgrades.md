# Migration and Upgrades

Reference: https://nextjs.org/docs/app/guides/upgrading/version-16

## Upgrade to Next.js 16

1. Run the official upgrade command (Next.js 16.1.0+):

```bash
npx next upgrade
```

For versions before 16.1.0, use:

```bash
npx @next/codemod@canary upgrade latest
```

2. If the project used synchronous `params`, `searchParams`, `cookies()`, `headers()`, or `draftMode()`, also run:

```bash
npx @next/codemod@latest next-async-request-api .
```

3. Migrate `middleware.ts` → `proxy.ts`:

```bash
npx @next/codemod@canary middleware-to-proxy .
```

### Canary version

To update to the latest canary:

```bash
pnpm add next@canary
```

| Canary currently includes authentication-related features: `forbidden`, `unauthorized`, `forbidden.js`, `unauthorized.js`, and the `authInterrupts` config option.
| Canary currently includes an `upgrade` command for the package manager that auto-runs codemods (`npx next upgrade`).

## Manual package update

```bash
npm install next@latest react@latest react-dom@latest
# also update @types/react and @types/react-dom for TypeScript
```

## Requirements

- Node.js 20.9+ (Node 18 no longer supported).
- TypeScript 5.1+.
- Browsers: Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+.

## Removed / renamed v15 → v16

- `experimental.turbopack` → top-level `turbopack`.
- `experimental.ppr` removed; PPR default with `cacheComponents`.
- `experimental.useCache` / `experimental.dynamicIO` removed → `cacheComponents`.
- `unstable_rootParams` removed → `next/root-params`.
- `publicRuntimeConfig` / `serverRuntimeConfig` removed → env vars; read server-only env directly in Server Components, client-prefixed `NEXT_PUBLIC_*` for the browser, or use `connection()` to read runtime env.
- `devIndicators.appIsrStatus`, `buildActivity`, `buildActivityPosition` removed.
- AMP support and the `amp` config / `next/amp` removed.
- `next lint` command and `eslint` config option removed; use ESLint/Biome directly.
- `next/legacy/image` deprecated.
- `images.domains` deprecated; use `images.remotePatterns`.

## Turbopack by default

- Remove `--turbopack` / `--turbo` from scripts.
- `next build` now uses Turbopack by default.
- Custom webpack config causes `next build` to fail unless you use `--webpack`, `--turbopack`, or migrate.
- `experimental.turbopack` is promoted to top-level `turbopack`.
- Turbopack filesystem caching is enabled by default for both dev and build (configurable via `turbopackFileSystemCache`).
- Sass `~` imports are not supported under Turbopack; remove the tilde or add `turbopack.resolveAlias: { '~*': '*' }`.
- To resolve Node.js native module imports in client code, prefer refactoring; `turbopack.resolveAlias` with a browser-only empty module is a fallback.

## Cache Components migration

If adopting Cache Components:

1. Set `cacheComponents: true`.
2. Remove `experimental.useCache` / `experimental.dynamicIO`.
3. Wrap runtime data in `Suspense` or cache with `"use cache"`.
4. Migrate `unstable_cache` and route-segment revalidation to `use cache` + `cacheTag` where appropriate.

See the dedicated migration guide for the full path.

## Migrating from Pages to App Router

- Minimum Node.js v18.17; target Next.js 13.4+.
- The `app` directory co-exists with `pages` for incremental migration.
- Root layout (`app/layout.tsx`) must include `<html>` and `<body>`; it replaces `pages/_app.tsx` and `pages/_document.tsx`.
- Replace `getServerSideProps` / `getStaticProps` with data fetching inside Server Components; replace `getStaticPaths` with `generateStaticParams`.
- Replace `pages/api/*` with Route Handlers (`route.ts`).
- Keep existing `_app` / `_document` while migrating so `pages/*` routes keep working; remove them once fully migrated.

## Migrating from Create React App

1. Install `next` and create `next.config.ts`:
   ```ts
   const nextConfig = { output: 'export', distDir: 'build' }
   ```
2. Create `app/layout.tsx` from `public/index.html`, replacing `body div#root` with `<div id="root">{children}</div>`.
3. Migrate head tags to the Metadata API; move global CSS into the root layout.
4. Keep old `_app` / `_document` only if a `pages` directory still exists.

## Migrating from Vite

1. Install `next` and create `next.config.mjs`:
   ```js
   const nextConfig = { output: 'export', distDir: './dist' }
   ```
2. Update `tsconfig.json`:
   - Remove `tsconfig.node.json` project reference.
   - Add `./dist/types/**/*.ts` and `./next-env.d.ts` to `include`; add `./node_modules` to `exclude`.
   - Add `"plugins": [{ "name": "next" }]` to `compilerOptions`.
   - Set `esModuleInterop: true`, `jsx: "react-jsx"`, `allowJs: true`, `forceConsistentCasingInFileNames: true`, `incremental: true`.
3. Create `app/layout.tsx` from `index.html` and migrate to the Metadata API.

## Keeping up to date

Run the upgrade command to move to the latest Next.js version:

```bash
npx next upgrade
```

Upgrading also refreshes the documentation bundled inside `node_modules/next/dist/docs/`, so agents and tooling work from the installed version.

## AGENTS.md hygiene

After upgrading, ensure `AGENTS.md` points at `node_modules/next/dist/docs/` for version-matched guidance. `create-next-app` and `next dev` can auto-generate or update the managed block.

## Codemods

Codemods automate common upgrade/migration steps:

- `npx next upgrade` (Next.js 16.1.0+) — interactive upgrade that runs the matching codemods for you.
- `npx @next/codemod@latest upgrade latest` — upgrade to the latest stable and run all relevant transformations.
- `npx @next/codemod@canary upgrade latest` — upgrade to the latest canary.
- `npx @next/codemod@latest next-async-request-api .` — migrate synchronous `params`/`searchParams`/`cookies()`/`headers()`/`draftMode()` to async APIs.
- `npx @next/codemod@canary middleware-to-proxy .` — migrate `middleware.ts` to `proxy.ts`.
- `npx @next/codemod@canary remove-partial-prefetch .` — remove per-route `prefetch = 'partial'` once global `partialPrefetching` is enabled.
- `npx @next/codemod@canary agents-md` — download version-matched docs into `.next-docs/` for projects that do not auto-generate `AGENTS.md`.
- `npx @next/codemod@canary next-image-to-legacy-image` / `next-image-experimental` — migrate Image usage.
- `npx @next/codemod@canary next-lint-to-eslint-cli .` — migrate `next lint` scripts to ESLint CLI.
- `npx @next/codemod@canary upgrade latest` — upgrade to the latest stable and run all relevant transformations.
- `npx @next/codemod@canary upgrade version-15` — upgrade to Next.js 15.
- `npx @next/codemod@canary upgrade version-14` — upgrade to Next.js 14.
- `npx @next/codemod@canary upgrade version-13` — upgrade to Next.js 13.
- `npx @next/codemod@canary upgrade version-12` — upgrade to Next.js 12.
- `npx @next/codemod@canary upgrade version-11` — upgrade to Next.js 11.
- `npx @next/codemod@canary upgrade version-10` — upgrade to Next.js 10.
- `npx @next/codemod@canary upgrade version-9` — upgrade to Next.js 9.

**Version-specific Pages Router upgrade notes**

| Version | Highlights |
|---|---|
| 9 → 10 | No breaking changes; `npm i next@10`. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-10) |
| 10 → 11 | Webpack 5 default, `cleanDistDir` default, `PORT` env support, static image imports, remove `Container`/`Head.rewind`, React 17. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-11) |
| 11 → 12 | SWC default, `swcMinify` opt-in, `next/image` wraps `<img>` in `<span>`, HMR WebSocket, Webpack 4 removed, `target` deprecated. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-12) |
| 12 → 13 | Minimum Node `16.14.0`, React `18.2.0`, `next/image`→`next/legacy/image`, `<Link>` no longer needs `<a>`, `target` removed, `app` directory optional. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-13) |
| 13 → 14 | Sourced from `docs/02-pages/02-guides/upgrading/version-14.mdx`; it is a redirect to the App Router version-14 guide. Treat as App Router guidance. (Source: https://nextjs.org/docs/pages/guides/upgrading/version-14) |

## Source URLs

- Version 16 upgrade: https://nextjs.org/docs/app/guides/upgrading/version-16
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
- App Router migration (Pages → App): https://nextjs.org/docs/app/guides/migrating/app-router-migration
- Migrating from Create React App: https://nextjs.org/docs/app/guides/migrating/from-create-react-app
- Migrating from Vite: https://nextjs.org/docs/app/guides/migrating/from-vite
- Codemods: https://nextjs.org/docs/app/guides/upgrading/codemods
- AI Coding Agents: https://nextjs.org/docs/app/guides/ai-agents
- Installation / upgrade command: https://nextjs.org/docs/app/getting-started/installation#upgrade-your-nextjs-app
- Version 14 upgrade: https://nextjs.org/docs/app/guides/upgrading/version-14
- Version 15 upgrade: https://nextjs.org/docs/app/guides/upgrading/version-15
- Version 16 upgrade codemod details: https://nextjs.org/docs/app/guides/upgrading/version-16
- AGENTS.md setup: https://nextjs.org/docs/app/guides/upgrading/version-16#set-up-ai-agent-docs
- Pages Router version 9 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-9
- Pages Router version 10 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-10
- Pages Router version 11 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-11
- Pages Router version 12 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-12
- Pages Router version 13 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-13
- Pages Router version 14 upgrade: https://nextjs.org/docs/pages/guides/upgrading/version-14
- Pages Router upgrading index: https://nextjs.org/docs/pages/guides/upgrading
- Redirecting guide: https://nextjs.org/docs/app/guides/redirecting
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- Production checklist: https://nextjs.org/docs/app/guides/production-checklist
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Local development: https://nextjs.org/docs/app/guides/local-development
- MCP server: https://nextjs.org/docs/app/guides/mcp
- Sass: https://nextjs.org/docs/app/guides/sass
- Scripts: https://nextjs.org/docs/app/guides/scripts
- Server and Client Boundary: https://nextjs.org/docs/app/guides/server-and-client-boundary
- Single-page applications: https://nextjs.org/docs/app/guides/single-page-applications
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- Tailwind v3: https://nextjs.org/docs/app/guides/tailwind-v3-css
- Third-party libraries: https://nextjs.org/docs/app/guides/third-party-libraries
- View transitions: https://nextjs.org/docs/app/guides/view-transitions
- Videos: https://nextjs.org/docs/app/guides/videos
- Version 15 upgrade: https://nextjs.org/docs/app/guides/upgrading/version-15
- Version 16 upgrade codemod details: https://nextjs.org/docs/app/guides/upgrading/version-16
- AGENTS.md setup: https://nextjs.org/docs/app/guides/upgrading/version-16#set-up-ai-agent-docs
- Redirecting guide: https://nextjs.org/docs/app/guides/redirecting
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- Production checklist: https://nextjs.org/docs/app/guides/production-checklist
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Local development: https://nextjs.org/docs/app/guides/local-development
- MCP server: https://nextjs.org/docs/app/guides/mcp
