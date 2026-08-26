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

## Jest

Use `next/jest` for a default configuration. See the official Jest guide for `jest.config.js` setup and handling CSS/image imports.

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

## Testing with instant navigation

For Cache Components, the Instant Navigation guide recommends writing `instant()` tests to assert that specific UI is present at click time. Write the test first, make it fail, fix the route, then keep the test as a regression guard.

## Source URLs

- Testing overview: https://nextjs.org/docs/app/guides/testing
- Vitest: https://nextjs.org/docs/app/guides/testing/vitest
- Jest: https://nextjs.org/docs/app/guides/testing/jest
- Playwright: https://nextjs.org/docs/app/guides/testing/playwright
- Cypress: https://nextjs.org/docs/app/guides/testing/cypress
- Instant navigation: https://nextjs.org/docs/app/guides/instant-navigation
