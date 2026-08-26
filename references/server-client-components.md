# Server and Client Components

Reference: https://nextjs.org/docs/app/getting-started/server-and-client-components

## Default behavior

In the App Router, **Server Components are the default**. `page.tsx`, `layout.tsx`, and most UI start as Server Components.

## When to use Client Components

Use `"use client"` only when you need:

- State (`useState`, `useReducer`) and event handlers (`onClick`, `onChange`)
- Lifecycle logic (`useEffect`, `useLayoutEffect`)
- Browser-only APIs (`localStorage`, `window`, `navigator.geolocation`, `document`)
- Custom hooks that depend on any of the above

## When to use Server Components

- Fetch data from databases or APIs close to the source
- Use API keys / tokens / secrets without exposing them to the client
- Reduce JavaScript sent to the browser
- Improve First Contentful Paint and stream content progressively

## Boundary rules

- `"use client"` marks a file and its imported module graph as client-side code.
- A Client Component can receive a Server Component as `children` or a prop; the Server Component renders on the server and only its output crosses the boundary.
- Props passed from Server Components to Client Components must be **serializable**.
- Functions (including event handlers) cannot be passed as props from a Server Component to a Client Component. Pass a Server Action (`'use server'`) reference instead.
- Compound components with static subcomponents (e.g. `Menu.Item`) break across the boundary; use named exports or keep them inside one graph.

## Interleaving pattern

```tsx
// Server Component page
import Modal from './modal' // 'use client'
import Cart from './cart'    // Server Component

export default function Page() {
  return (
    <Modal>
      <Cart />
    </Modal>
  )
}
```

`Cart` runs on the server; `Modal` only receives rendered output, not `Cart`'s source code.

## Environment protection

- Only env vars prefixed with `NEXT_PUBLIC_` reach the client bundle.
- Use the `server-only` package to mark modules that must never be imported by Client Components.
- Use the `client-only` package to mark modules that require browser APIs.

## Common mistakes to prevent

- Marking an entire page or layout `"use client"` when only a small subtree needs it.
- Passing non-serializable props (functions, class instances) from server to client.
- Importing server-only secrets into a Client Component.
- Using `useState` / `useEffect` in a Server Component.

## Source URLs

- Server and Client Components overview: https://nextjs.org/docs/app/getting-started/server-and-client-components
- Server and Client Boundary guide: https://nextjs.org/docs/app/guides/server-and-client-boundary
- `use client` directive: https://nextjs.org/docs/app/api-reference/directives/use-client
- `server-only` / `client-only`: https://www.npmjs.com/package/server-only
