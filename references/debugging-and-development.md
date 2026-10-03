# Debugging and Development

Reference: https://nextjs.org/docs/app/guides/debugging

## Dev server

- `next dev` compiles routes as you open/navigate to them.
- Browser console errors and warnings are forwarded to the terminal via `logging.browserToTerminal`.
- `.next/dev/lock` contains PID, port, and URL so agents can connect to an existing server.

## Next.js MCP server

Next.js 16+ exposes an MCP endpoint at `/_next/mcp`. Install `next-devtools-mcp` in `.mcp.json`:

```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

When you start the development server, `next-devtools-mcp` automatically discovers and connects to the running Next.js instance.

Tools include:

- `get_errors` — current build errors, runtime errors, and type errors.
- `get_logs` — path to the dev log file containing browser console logs and server output.
- `get_compilation_issues` — bundler warnings/errors (Turbopack only).
- `compile_route` — compile a route on demand without an HTTP request. Accepts a `routeSpecifier` or `path`; resolved via the dev router's live route table.
- `get_routes` — scanned filesystem routes grouped by `appRouter` / `pagesRouter`, with dynamic segments as `[param]` / `[...slug]`.
- `get_page_metadata` — route/component/rendering info for specific pages.
- `get_server_action_by_id` — locate a Server Action source file and function name.
- `get_project_metadata` — project structure, config, and dev server URL.

Use these before guessing about dev-server state.

## Agent-facing dev tools

Next.js can generate and maintain an `AGENTS.md` file at the project root:

- `create-next-app` generates `AGENTS.md` and `CLAUDE.md` by default; pass `--no-agents-md` to skip.
- On Next.js 16.3+, `next dev` detects AI agents and auto-generates/upserts a managed `AGENTS.md` block, preserving user content outside the managed markers.
- Earlier versions can use `npx @next/codemod@canary agents-md` to download version-matched docs to `.next-docs/`.
- Auto-generation can be disabled with `agentRules: false` in `next.config.*`.

For error-driven debugging, Cache Components blocking errors show a **Copy prompt** button with a canonical fix; the same prompt is printed in the terminal and `next build` output, linking to `/docs/messages/<error-id>`. Append `.md` or use `Accept: text/markdown` to fetch these error pages as Markdown.

## Source maps

By default, Next.js keeps source maps private in production to protect source code. You can enable production browser source maps via the `productionBrowserSourceMaps` config, but this can increase build time and expose source code.

## Browser / Node debugging

- VS Code: create `.vscode/launch.json` with Node + Chrome configs; use `npm run dev -- --inspect` for the server-side config; for full-stack use `program` pointing at `node_modules/next/dist/bin/next` with `--inspect` and a `serverReadyAction`.
- Chrome DevTools: `next dev --inspect` (or `NODE_OPTIONS=--inspect-brk next dev` for break-on-start); use `chrome://inspect` for Remote Target inspection.
- Firefox DevTools: install the Firefox Debugger extension; set `pathMappings` from `webpack://_N_E` to the workspace folder.
- Server source files appear under `webpack://_N_E/` or `webpack://{app-name}/`.
- Use `--inspect=0.0.0.0` to allow remote debugging access outside localhost, such as when running the app in a Docker container.
- To use `--inspect-brk` or `--inspect-wait`, specify via `NODE_OPTIONS` (e.g. `NODE_OPTIONS=--inspect-brk next dev`).

## Local performance

- Use latest Next.js and Turbopack.
- Avoid broad Tailwind `content` globs that include `node_modules` or large directories; keep the array scoped to source files.
- Avoid unnecessary barrel imports; icon libraries like `react-icons`, `@material-ui/icons`, or `@phosphor-icons/react` can import tens of thousands of modules even if you only use a few. Import directly from the specific icon subset or use `optimizePackageImports`.
- `optimizePackageImports` is only needed for Webpack; Turbopack analyzes and optimizes imports automatically.
- Disable antivirus/macOS Gatekeeper scanning of the project folder if dev is slow.
- Prefer local dev over Docker on macOS/Windows for HMR performance.
- Reserve Docker for production builds and testing. If Docker is required for dev, use a Linux machine or VM.
- Use `logging.fetches.fullUrl` to inspect fetch behavior.
- Use `next dev --trace` for Turbopack tracing; `next dev --internal-trace` on newer versions produces a `.next-profiles/trace-turbopack.bin` file that can be interpreted with `npx next internal trace [path]` and viewed at https://trace.nextjs.org/.
- For build memory issues, try `experimental.webpackMemoryOptimizations` or `next build --experimental-debug-memory-usage`.
- Record heap profiles with `node --heap-prof node_modules/next/dist/bin/next build` and load the `.heapprofile` in Chrome DevTools.
- Use `NODE_OPTIONS=--inspect` (or `--inspect-brk`) with `next build`/`next dev` to capture heap snapshots via Chrome DevTools; send `SIGUSR2` in `--experimental-debug-memory-usage` mode to trigger snapshots.
- The Webpack build worker is enabled by default for apps without custom webpack config starting in v14.1.0; set `experimental.webpackBuildWorker: true` to opt in on older versions.
- Disable Webpack cache in production via custom webpack config (`config.cache = { type: 'memory' }`) if cache-related memory is a problem.
- Disable preloaded entries at server startup with `experimental.preloadEntriesOnStart: false` to reduce initial memory footprint (pages are still loaded as requested).

## Package bundling / `optimizePackageImports`

- Avoid broad barrel files; import directly from specific files for icon/utility libraries.
- Icon libraries (`react-icons`, `@material-ui/icons`, `@phosphor-icons/react`) can import tens of thousands of modules even if only a few are used. Import directly from the specific subset (e.g. `@phosphor-icons/react/dist/csr/Triangle`).
- `optimizePackageImports` in `next.config.js` helps Webpack tree-shake barrel packages automatically. It is only needed for Webpack; Turbopack analyzes and optimizes imports automatically.
- Magic comments for dynamic imports: `/* webpackIgnore: true */`, `/* turbopackIgnore: true */`, `/* turbopackOptional: true */` work with dynamic `import()`, `require()`, `require.resolve()`, and `new Worker()`. `webpackOptional` is not supported; use `turbopackOptional`.

## Antivirus / Gatekeeper

On Windows, add the project folder to Microsoft Defender exclusions. On macOS, enable Developer Tools access for your terminal in System Settings > Privacy & Security. Both reduce filesystem-scanning overhead that can slow dev builds.

## Tailwind and imports

- Keep Tailwind `content` scoped to source files; avoid globs that match `node_modules` or large monorepo directories.
- Avoid broad barrel files; import directly from specific files for icon/utility libraries.
- `optimizePackageImports` is only needed for Webpack; Turbopack analyzes and optimizes imports automatically.

## Server Components HMR cache

`serverComponentsHmrCache` (experimental) caches `fetch` responses in Server Components across Hot Module Replacement (HMR) refreshes in local development. This reduces repeated API calls and billed API usage while preserving fast iteration.

## Dev overlay / error-driven fixes

With Cache Components enabled, blocking prerender errors present labeled fixes:
- `[stream]` — wrap in `<Suspense fallback={...}>`.
- `[cache]` — cache the data access with `"use cache"`.
- `[block]` — set `export const instant = false` to allow a blocking route.

Each error links to `/docs/messages/<error-id>` with canonical patterns and trade-offs. The dev overlay has a **Copy prompt** button; the same menu appears in `next build` output and CI logs. Append `.md` or use `Accept: text/markdown` to fetch these pages as Markdown.

## Runtime visibility

- `next dev` forwards browser console errors/warnings to the terminal via `logging.browserToTerminal`.
- `.next/dev/lock` contains PID, port, and URL so agents can connect to an existing server.
- The Next.js MCP server (`next-devtools-mcp`) at `/_next/mcp` exposes routes, compilation issues, server logs, and server actions.
- The `agent-browser` tool exposes DOM, console, network, and Web Vitals as structured text, with React DevTools component tree visibility.
- The `next-dev-loop` skill combines MCP + browser verification into an edit-and-verify loop.

## Skills

Next.js Skills package multi-step workflows (not lookups) such as adopting Cache Components or Partial Prefetching. Available skills include:
- `next-dev-loop`
- `next-cache-components-adoption`
- `next-cache-components-optimizer`
- `next-partial-prefetching-adoption`

Install with `npx skills add vercel/next.js --skill <name>`.

## AGENTS.md

- `create-next-app` generates `AGENTS.md` and `CLAUDE.md` by default; pass `--no-agents-md` to skip.
- On Next.js 16.3+, `next dev` auto-generates/upserts a managed `AGENTS.md` block when an AI agent is detected; content outside the managed markers is preserved.
- Earlier versions can use `npx @next/codemod@canary agents-md` to download version-matched docs to `.next-docs/`.
- Docs are also available via `https://nextjs.org/docs/...` with `.md` suffix or `Accept: text/markdown`; see `/docs/llms.txt` and `/docs/llms-full.txt` for discovery.
- Opt out of auto-generation with `agentRules: false` in `next.config.*`.

## Instrumentation (`instrumentation.ts`)

File at app root or `src/` root (next to `app`/`pages`, not inside them). Used for observability/tracing in production.

- `register()` (optional): called **once** when a new server instance is initiated; must complete before the server handles requests; may be async.
- `onRequestError` (optional): track **server** errors to a custom observability provider.
  - Signature: `(error: unknown, request: { path, method, headers }, context: { routerKind: 'Pages Router'|'App Router', routePath, routeType: 'render'|'route'|'action'|'proxy', renderSource, revalidateReason, renderType }) => void | Promise<void>`.
  - Await any async work; the function fires when Next.js captures the error.
  - `error` may not be the original instance (React may process it); use `digest` to identify the type.
  - `routeType: 'proxy'` means Proxy errors are observable here.
- Runtime targeting: works in both Node.js and Edge; use `process.env.NEXT_RUNTIME` (`'edge'` vs `'nodejs'`) to split `register`/`onRequestError` into runtime-specific files.
- Version history: v15.0.0 `onRequestError` introduced & instrumentation stable · v14.0.4 Turbopack support · v13.2.0 introduced experimental.
- OTel setup lives in deployment-and-production.md (OpenTelemetry section).

### Proxy unit testing (experimental, v15.1+)

`next/experimental/testing/server` provides `unstable_doesProxyMatch`, `isRewrite`, `getRewrittenUrl` to assert matcher behavior and rewrite/redirect output before production.

## Source URLs

- Debugging: https://nextjs.org/docs/app/guides/debugging
- Local development: https://nextjs.org/docs/app/guides/local-development
- Memory usage: https://nextjs.org/docs/app/guides/memory-usage
- Next.js MCP Server: https://nextjs.org/docs/app/guides/mcp
- AI Coding Agents: https://nextjs.org/docs/app/guides/ai-agents
- Logging config: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- `serverComponentsHmrCache`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverComponentsHmrCache
- `agentRules`: https://nextjs.org/docs/app/api-reference/config/next-config-js/agentRules
- `preloadEntriesOnStart`: https://nextjs.org/docs/app/api-reference/config/next-config-js/onDemandEntries
- `webpackMemoryOptimizations`: https://nextjs.org/docs/app/api-reference/config/next-config-js/webpackMemoryOptimizations
- Instant navigation: https://nextjs.org/docs/app/guides/instant-navigation
- Partial Prefetching: https://nextjs.org/docs/app/guides/adopting-partial-prefetching
- Cache Components: https://nextjs.org/docs/app/getting-started/caching
- `next-dev-loop`: https://www.skills.sh/vercel/next.js/next-dev-loop
- `next-cache-components-adoption`: https://www.skills.sh/vercel/next.js/next-cache-components-adoption
- `next-cache-components-optimizer`: https://www.skills.sh/vercel/next.js/next-cache-components-optimizer
- `next-partial-prefetching-adoption`: https://www.skills.sh/vercel/next.js/next-partial-prefetching-adoption
- Production browser source maps: https://nextjs.org/docs/app/api-reference/config/next-config-js/productionBrowserSourceMaps
- Node.js debugging: https://nodejs.org/learn/getting-started/debugging/
- VS Code Node.js debugging: https://code.visualstudio.com/docs/nodejs/nodejs-debugging
- Chrome DevTools: https://developers.google.com/web/tools/chrome-devtools/javascript
- Firefox DevTools: https://firefox-source-docs.mozilla.org/devtools-user/debugger/
- Trace viewer: https://trace.nextjs.org/
- OpenTelemetry: https://nextjs.org/docs/app/guides/open-telemetry
- MCP server: https://nextjs.org/docs/app/guides/mcp
- Preventing flash before hydration: https://nextjs.org/docs/app/guides/preventing-flash-before-hydration
- JSON-LD: https://nextjs.org/docs/app/guides/json-ld
- Package bundling: https://nextjs.org/docs/app/guides/package-bundling
- Public/static pages: https://nextjs.org/docs/app/guides/public-static-pages
- PPR platform guide: https://nextjs.org/docs/app/guides/ppr-platform-guide
- Rendering philosophy: https://nextjs.org/docs/app/guides/rendering-philosophy
- Multi-zones: https://nextjs.org/docs/app/guides/multi-zones
- Multi-tenant: https://nextjs.org/docs/app/guides/multi-tenant
- `useOffline`: https://nextjs.org/docs/app/api-reference/functions/use-offline
- `useOffline` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/useOffline
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- Preserving UI state: https://nextjs.org/docs/app/guides/preserving-ui-state
- Progressive Web Apps: https://nextjs.org/docs/app/guides/progressive-web-apps
- Web app manifest convention: https://nextjs.org/docs/app/api-reference/file-conventions/metadata/manifest
- Instrumentation: https://nextjs.org/docs/app/api-reference/file-conventions/instrumentation
- Proxy file convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy

<!-- CANARY-GUIDES-2026-08-30 -->
### Canary guides — debugging additions (ingest 2026-08-30)

**Debugging (`debugging`)**
- Use `next dev --inspect=0.0.0.0` to allow remote debugging access outside localhost (e.g. app running in a Docker container). (Source: https://nextjs.org/docs/app/guides/debugging)

<!-- CANARY-ARCH-PAGES-2026-09-04 -->
### Canary architecture additions — Accessibility (ingest 2026-09-04)

Sourced from `docs/03-architecture/accessibility.mdx`. Accessibility is a dev/runtime concern; merged into the debugging-and-development reference.

**Accessibility features**
- Next.js includes a **route announcer** for client-side transitions (next/link). It announces page changes to screen readers by inspecting `document.title`, then `<h1>`, then the URL pathname. Ensure each page has a unique, descriptive title. (Source: https://nextjs.org/docs/architecture/accessibility)
- Next.js bundles `eslint-plugin-jsx-a11y` in its integrated ESLint experience. It warns on: `aria-props`, `aria-proptypes`, `aria-unsupported-elements`, `role-has-required-aria-props`, `role-supports-aria-props`. This catches missing alt text, incorrect aria-* attributes, and incorrect role attributes. (Source: above)
- Accessibility resources: WebAIM WCAG checklist, WCAG 2.2 Guidelines, The A11y Project, color contrast ratios, and `prefers-reduced-motion` for animations. (Source: above)

<!-- CANARY-ARCH-PAGES-2026-09-02 -->
### Canary architecture additions — Fast Refresh (ingest 2026-09-02)

Sourced from `docs/03-architecture/fast-refresh.mdx`.

**Fast Refresh behavior**
- Enabled by default in Next.js 9.4+. Most edits become visible within a second. (Source: https://nextjs.org/docs/architecture/fast-refresh)
- If a file only exports React component(s), Fast Refresh updates only that file and re-renders the component, preserving local state. (Source: above)
- If a file exports non-component values imported by other files, Fast Refresh re-runs the edited file and all files importing it. (Source: above)
- If a file is imported by files **outside the React tree**, Fast Refresh falls back to a full reload. Keep shared constants in separate files to avoid this. (Source: above)
- Syntax errors are auto-dismissed after fixing and saving; component state is not lost. (Source: above)
- Runtime errors inside a component show a contextual overlay; fixing dismisses it without reload. State is retained unless the error occurred during rendering (then React remounts the app). (Source: above)
- Error boundaries retry rendering on the next edit after a rendering error, helping preserve state. (Source: above)
- State is **not preserved** for class components or anonymous default arrow functions like `export default () => <div />`. Use the `name-default-component` codemod for the latter. (Source: above)
- Force a remount on every edit by adding `// @refresh reset` anywhere in the file. (Source: above)
- Hooks with dependencies (`useEffect`, `useMemo`, `useCallback`) always re-run during Fast Refresh; dependency lists are ignored so edits are visible. Even `useEffect` with an empty dependency array re-runs once during Fast Refresh. (Source: above)
