# Installation

References:

- https://nextjs.org/docs/app/getting-started/installation
- https://nextjs.org/docs/app/api-reference/cli/create-next-app (v16.3.8, updated 2026-08-25)

## Quick start

Create and run a new Next.js app with `create-next-app`:

```bash
npx create-next-app@latest my-app --yes
cd my-app
npm run dev
```

With `--yes`, the CLI skips prompts and uses previous saved preferences when available, otherwise defaults. The documented recommended defaults are:

- TypeScript
- Tailwind CSS
- ESLint
- App Router
- Turbopack (default bundler in v16)
- Import alias `@/*`
- `AGENTS.md` (and a `CLAUDE.md` that references it)

Because saved preferences can vary by machine, use explicit flags when the generated shape must be reproducible.

## System requirements and browsers

Source: https://nextjs.org/docs/app/getting-started/installation#system-requirements

- Node.js 20.9 or later.
- macOS, Windows (including WSL), and Linux.
- Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+.

## Create with the CLI

Run `create-next-app` without `--yes` to choose settings interactively:

```bash
npx create-next-app@latest
```

Equivalent entry points are:

```bash
pnpm create next-app [project-name] [options]
yarn create next-app [project-name] [options]
bun create next-app [project-name] [options]
```

Prompted options include TypeScript, linter (ESLint / Biome / none), React Compiler, Tailwind CSS, `src/` directory, App Router, import alias, and `AGENTS.md`. To skip generating `AGENTS.md` and `CLAUDE.md`, pass `--no-agents-md`.

### `create-next-app` CLI flags (v16+)

| Flag | Description |
|------|-------------|
| `--ts` / `--typescript` | Initialize as TypeScript project (default) |
| `--js` / `--javascript` | Initialize as JavaScript project |
| `--tailwind` | Initialize with Tailwind CSS config (default) |
| `--react-compiler` | Initialize with React Compiler enabled |
| `--eslint` | Initialize with ESLint config |
| `--biome` | Initialize with Biome config |
| `--no-linter` | Skip linter configuration |
| `--app` | Initialize as App Router project |
| `--api` | Initialize with only route handlers |
| `--src-dir` | Initialize inside `src/` directory |
| `--turbopack` | Force enable Turbopack in package.json (default) |
| `--webpack` | Force enable Webpack in package.json |
| `--import-alias <alias>` | Import alias to use (default `@/*`) |
| `--empty` | Initialize an empty project |
| `--use-npm` / `--use-pnpm` / `--use-yarn` / `--use-bun` | Force a specific package manager |
| `-e` / `--example [name] [github-url]` | Bootstrap from an official example name or public GitHub URL |
| `--example-path <path-to-example>` | Specify the path within an example separately |
| `--reset-preferences` | Reset stored preferences |
| `--skip-install` | Skip installing packages |
| `--disable-git` | Disable git initialization |
| `--agents-md` | Include `AGENTS.md` and `CLAUDE.md` (default) |
| `--yes` | Use previous preferences or defaults |

([create-next-app](https://nextjs.org/docs/app/api-reference/cli/create-next-app))

### Reproducible and safe scaffolding

- For automation, prefer explicit flags and a `--use-*` package-manager selector. `--yes` can reuse machine-local preferences.
- `--reset-preferences` deliberately clears those saved choices before the next scaffold.
- The CLI initializes Git by default. Use `--disable-git` when repository initialization is not desired or authorized.
- Use `--skip-install` when you need to inspect or modify the generated manifest before dependency installation.
- `--example` accepts either an official example name or a public GitHub URL. Treat arbitrary GitHub examples as third-party source code and inspect them before trusting install/build scripts.
- `--example-path` disambiguates the path when the example resides below the repository root.

Official example:

```bash
pnpm create next-app --example [example-name] [your-project-name]
```

Public GitHub example:

```bash
pnpm create next-app --example "https://github.com/.../" [your-project-name]
```

### Recommended defaults prompt

When running `create-next-app` interactively, you can choose:

- **Yes, use recommended defaults** — TypeScript, ESLint, Tailwind CSS, App Router, AGENTS.md.
- **No, reuse previous settings**
- **No, customize settings** — choose each option individually.

### Linter choices

- **ESLint** includes Next.js-specific rules from `@next/eslint-plugin-next`.
- **Biome** combines linting and formatting and includes built-in React and Next.js domain support.
- **None** skips linter setup; add and verify one later if the project requires it.

## Manual installation

Install the required packages:

```bash
npm i next@latest react@latest react-dom@latest
```

Even though the App Router bundles React canary releases, you should still declare `react` and `react-dom` in `package.json` for tooling and ecosystem compatibility. See [React version handling](app-router.md#react-version-handling) for the router differences.

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

For bundler details, including how to opt back into Webpack, see [Turbopack and Build](turbopack-and-build.md).

## System requirements and browsers

See [Migration and Upgrades](migration-and-upgrades.md#requirements) for Node.js / OS / TypeScript requirements and supported browser versions.

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

## Editor setup

### VS Code / Cursor custom editor labels

Because the App Router uses repeated filenames (`page.tsx`, `layout.tsx`, `route.ts`, etc.), VS Code 1.88+ and Cursor can label tabs by enclosing folders. Add this to `.vscode/settings.json`:

```json
{
  "workbench.editor.customLabels.patterns": {
    "**/app/**/page.tsx": "${dirname(1)}/${dirname} - page.tsx",
    "**/app/**/layout.tsx": "${dirname(1)}/${dirname} - layout.tsx",
    "**/app/**/loading.tsx": "${dirname(1)}/${dirname} - loading.tsx",
    "**/app/**/error.tsx": "${dirname(1)}/${dirname} - error.tsx",
    "**/app/**/not-found.tsx": "${dirname(1)}/${dirname} - not-found.tsx",
    "**/app/**/template.tsx": "${dirname(1)}/${dirname} - template.tsx",
    "**/app/**/default.tsx": "${dirname(1)}/${dirname} - default.tsx",
    "**/app/**/route.ts": "${dirname(1)}/${dirname} - route.ts"
  }
}
```

Labeling two folders deep keeps dynamic routes like `blog/[id]/page.tsx` from collapsing to the same `[id]` label. JetBrains IDEs show the folder automatically.

To upgrade an existing app, see [Migration and Upgrades](migration-and-upgrades.md#keeping-up-to-date).

## Source URLs

- Installation: https://nextjs.org/docs/app/getting-started/installation
- `create-next-app`: https://nextjs.org/docs/app/api-reference/cli/create-next-app
- TypeScript reference: https://nextjs.org/docs/app/api-reference/config/typescript
- ESLint config: https://nextjs.org/docs/app/api-reference/config/eslint
- Project structure: https://nextjs.org/docs/app/getting-started/project-structure
