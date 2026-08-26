# Installation

Reference: https://nextjs.org/docs/app/getting-started/installation

## Quick start

Create and run a new Next.js app with `create-next-app`:

```bash
npx create-next-app@latest my-app --yes
cd my-app
npm run dev
```

With `--yes`, the CLI skips prompts and uses defaults:

- TypeScript
- Tailwind CSS
- ESLint
- App Router
- Turbopack (default bundler in v16)
- Import alias `@/*`
- `AGENTS.md` (and a `CLAUDE.md` that references it)

## Create with the CLI

Run `create-next-app` without `--yes` to choose settings interactively:

```bash
npx create-next-app@latest
```

Prompted options include TypeScript, linter (ESLint / Biome / none), React Compiler, Tailwind CSS, `src/` directory, App Router, import alias, and `AGENTS.md`.

## Manual installation

Install the required packages:

```bash
npm i next@latest react@latest react-dom@latest
```

Even though the App Router bundles React canary releases, you should still declare `react` and `react-dom` in `package.json` for tooling and ecosystem compatibility. See [React version handling](../app-router.md#react-version-handling) for the router differences.

Add typical scripts to `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "lint:fix": "eslint --fix"
  }
}
```

- `next dev` starts the dev server.
- `next build` builds for production.
- `next start` starts the production server.

For bundler details, including how to opt back into Webpack, see [Turbopack and Build](../turbopack-and-build.md).

## System requirements and browsers

See [Migration and Upgrades](../migration-and-upgrades.md#requirements) for Node.js / OS / TypeScript requirements and supported browser versions.

## TypeScript

Rename a file to `.ts` / `.tsx` and run `next dev`. Next.js installs the necessary dependencies and creates a recommended `tsconfig.json`.

Next.js also ships a custom TypeScript plugin and type checker for advanced type-checking and auto-completion in VS Code and other editors. Enable it by selecting the workspace TypeScript version in the editor command palette.

## Linting

Next.js 16 supports ESLint or Biome. Run the linter through `package.json` scripts:

- **ESLint**:

```json
{
  "scripts": {
    "lint": "eslint",
    "lint:fix": "eslint --fix"
  }
}
```

- **Biome**:

```json
{
  "scripts": {
    "lint": "biome check",
    "format": "biome format --write"
  }
}
```

Starting with Next.js 16, `next build` no longer runs the linter automatically.

If a project previously used `next lint`, migrate to the ESLint CLI with the codemod:

```bash
npx @next/codemod@canary next-lint-to-eslint-cli .
```

For ESLint, create an explicit config (recommended: `eslint.config.mjs`).

## Absolute imports and module path aliases

Next.js supports `baseUrl` and `paths` from `tsconfig.json` / `jsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": "src/",
    "paths": {
      "@/components/*": ["components/*"],
      "@/styles/*": ["styles/*"]
    }
  }
}
```

Paths are relative to the `baseUrl` location.

## Keeping up to date

To upgrade an existing app, see [Migration and Upgrades](../migration-and-upgrades.md#keeping-up-to-date).

## Source URLs

- Installation: https://nextjs.org/docs/app/getting-started/installation
- `create-next-app`: https://nextjs.org/docs/app/api-reference/cli/create-next-app
- TypeScript reference: https://nextjs.org/docs/app/api-reference/config/typescript
- ESLint config: https://nextjs.org/docs/app/api-reference/config/eslint
