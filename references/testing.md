# Testing

Reference: https://nextjs.org/docs/app/guides/testing

## Overview

Next.js projects commonly use:

- **Vitest** — unit testing.
- **Jest** — unit and snapshot testing.
- **Playwright** — end-to-end testing.
- **Cypress** — end-to-end and component testing.

## Vitest

Example `vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: { environment: 'jsdom' },
})
```

Package script: `"test": "vitest"`.

- `async` Server Components are **not** supported by Vitest; use E2E tests for those.

## Jest

Use `next/jest` for a default configuration.

- Install `jest`, `jest-environment-jsdom`, `@testing-library/react`, `@testing-library/dom`, `@testing-library/jest-dom`, `ts-node`, `@types/jest` as dev dependencies.
- Create a `jest.config.ts|js` and wrap it with `nextJest({ dir: './' })` from `next/jest.js`.
- `next/jest` automatically configures: Next.js Compiler transform, auto-mocking of CSS/SCSS modules, image imports, and `next/font`, loading `.env` variants, ignoring `node_modules`/`.next`, and loading `next.config.js` for SWC transform flags.
- For module path aliases, mirror `tsconfig.json`/`jsconfig.json` `paths` in `moduleNameMapper`.
- `async` Server Components are **not** supported by Jest; use E2E tests for those.

For the full setup, see the official Jest guide.

## Playwright

Create E2E tests in `e2e/` or `tests/`:

```ts
import { test, expect } from '@playwright/test'

test('homepage has title', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/My Site/)
})
```

## Cypress

Use `cypress.config.ts` and the Cypress CLI. Component tests mount individual components; E2E tests run against the running dev server or production build.

- Cypress versions **below 13.6.3** do not support TypeScript 5 with `moduleResolution: "bundler"`. Use Cypress 13.6.3+ if your project uses TS5 + bundler resolution. ([Cypress](https://nextjs.org/docs/app/guides/testing/cypress))

## Testing with instant navigation

For Cache Components, the Instant Navigation guide recommends writing `instant()` tests to assert that specific UI is present at click time. Write the test first, make it fail, fix the route, then keep the test as a regression guard. This is the same pattern used by the official `next-cache-components-optimizer` skill.

The `@next/playwright` package provides an `instant()` helper that scopes assertions to the UI immediately available on navigation. Install it alongside `@playwright/test`:

```bash
pnpm add -D @next/playwright @playwright/test
```

Pass Playwright's `baseURL` to `instant()` when `page.goto()` is the first navigation. Inside the callback, assert on the static UI for an initial page load and the prefetched UI for a client navigation. For client navigations, wait for the destination URL before asserting on its UI to avoid matching the source page.

Run `instant()` tests against `next dev` (the testing API is enabled automatically). To run them in CI against a production build, set `experimental.exposeTestingApiInProductionBuild: true` so `next start` exposes the same API.

## Testing Server Actions and offline behavior

- E2E tests are the right layer for Server Actions, async Server Components, and offline retry behavior.
- Test offline behavior with a production build (`next build && next start`) rather than `next dev`.
- Use Playwright's network throttling or DevTools "Offline" mode to simulate connectivity drops.

## Source URLs

- Testing overview: https://nextjs.org/docs/app/guides/testing
- Vitest: https://nextjs.org/docs/app/guides/testing/vitest
- Jest: https://nextjs.org/docs/app/guides/testing/jest
- Playwright: https://nextjs.org/docs/app/guides/testing/playwright
- Cypress: https://nextjs.org/docs/app/guides/testing/cypress
- Instant navigation: https://nextjs.org/docs/app/guides/instant-navigation
- Offline support: https://nextjs.org/docs/app/guides/offline-support
- Server Actions: https://nextjs.org/docs/app/guides/server-actions
- Single-page applications: https://nextjs.org/docs/app/guides/single-page-applications
- View transitions: https://nextjs.org/docs/app/guides/view-transitions
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- `@next/playwright` package: https://www.npmjs.com/package/@next/playwright
