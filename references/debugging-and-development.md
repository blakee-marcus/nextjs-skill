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

Tools include:

- `get_errors` — build/runtime/type errors.
- `get_compilation_issues` — bundler issues (Turbopack only).
- `compile_route` — compile a route on demand.
- `get_routes` — scanned filesystem routes.
- `get_page_metadata` — route/component/rendering info.
- `get_server_action_by_id` — locate a Server Action source.

Use these before guessing about dev-server state.

## Browser / Node debugging

- VS Code: create `.vscode/launch.json` with Node + Chrome configs.
- Chrome DevTools: `next dev --inspect` (or `NODE_OPTIONS=--inspect-brk next dev` for break-on-start).
- Server source files appear under `webpack://_N_E/` or `webpack://{app-name}/`.

## Local performance

- Use latest Next.js and Turbopack.
- Avoid broad Tailwind `content` globs and unnecessary barrel imports.
- Disable antivirus/macOS Gatekeeper scanning of the project folder if dev is slow.
- Prefer local dev over Docker on macOS/Windows for HMR performance.
- Use `logging.fetches.fullUrl` to inspect fetch behavior.

## Dev overlay

With Cache Components, blocking errors show labeled fixes with a **Copy prompt** button. The same menu prints in the terminal and in `next build` output, linking to `/docs/messages/<error-id>`.

## Source URLs

- Debugging: https://nextjs.org/docs/app/guides/debugging
- Local development: https://nextjs.org/docs/app/guides/local-development
- Next.js MCP Server: https://nextjs.org/docs/app/guides/mcp
- AI Coding Agents: https://nextjs.org/docs/app/guides/ai-agents
- Logging config: https://nextjs.org/docs/app/api-reference/config/next-config-js/logging
- `serverComponentsHmrCache`: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverComponentsHmrCache
