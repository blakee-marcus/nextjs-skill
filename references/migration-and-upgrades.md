# Migration and Upgrades

Reference: https://nextjs.org/docs/app/guides/upgrading/version-16

## Upgrade to Next.js 16

1. Run the official upgrade codemod:

```bash
npx @next/codemod@latest upgrade latest
```

2. If the project used synchronous `params`, `searchParams`, `cookies()`, `headers()`, or `draftMode()`, also run:

```bash
npx @next/codemod@latest next-async-request-api .
```

3. Migrate `middleware.ts` → `proxy.ts`:

```bash
npx @next/codemod@canary middleware-to-proxy .
```

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
- `publicRuntimeConfig` / `serverRuntimeConfig` removed → env vars.
- `devIndicators.appIsrStatus`, `buildActivity`, `buildActivityPosition` removed.

## Turbopack by default

- Remove `--turbopack` / `--turbo` from scripts.
- `next build` now uses Turbopack by default.
- Custom webpack config causes `next build` to fail unless you use `--webpack`, `--turbopack`, or migrate.

## Cache Components migration

If adopting Cache Components:

1. Set `cacheComponents: true`.
2. Remove `experimental.useCache` / `experimental.dynamicIO`.
3. Wrap runtime data in `Suspense` or cache with `"use cache"`.
4. Migrate `unstable_cache` and route-segment revalidation to `use cache` + `cacheTag` where appropriate.

See the dedicated migration guide for the full path.

## AGENTS.md hygiene

After upgrading, ensure `AGENTS.md` points at `node_modules/next/dist/docs/` for version-matched guidance. `create-next-app` and `next dev` can auto-generate or update the managed block.

## Source URLs

- Version 16 upgrade: https://nextjs.org/docs/app/guides/upgrading/version-16
- Migrating to Cache Components: https://nextjs.org/docs/app/guides/migrating-to-cache-components
- App Router migration (Pages → App): https://nextjs.org/docs/app/guides/migrating/app-router-migration
- Codemods: https://nextjs.org/docs/app/guides/upgrading/codemods
- AI Coding Agents: https://nextjs.org/docs/app/guides/ai-agents
