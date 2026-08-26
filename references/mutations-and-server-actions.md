# Mutations and Server Actions

Reference: https://nextjs.org/docs/app/getting-started/mutating-data

## Server Functions and Server Actions

A **Server Function** is an async function that runs on the server. In a mutation/action context it is called a **Server Action**.

Mark a function or an entire file with `'use server'`:

```ts
'use server'

export async function createPost(formData: FormData) {
  // runs on the server
}
```

- Inline Server Functions inside Server Components are allowed.
- Client Components cannot define Server Functions; they import them from a `'use server'` file.

## Invoking Server Actions

- Pass to a `<form action={createPost}>`.
- Pass to `<button formAction={createPost}>`.
- Call from an event handler or `useEffect` inside a Client Component.
- Server Actions use the `POST` method and are reachable via direct POST requests — always authenticate/authorize inside the action.

## Pending state

Use `useActionState` to get a `pending` boolean:

```tsx
'use client'

import { useActionState } from 'react'

export function Button({ action }) {
  const [state, formAction, pending] = useActionState(action, null)
  return (
    <button formAction={formAction} disabled={pending}>
      {pending ? 'Saving...' : 'Save'}
    </button>
  )
}
```

## Refresh / revalidate after mutation

- `refresh()` from `next/cache` refetches the current route's RSC Payload.
- `revalidatePath('/path')` invalidates a route.
- `revalidateTag('tag')` invalidates tagged cache stale-while-revalidate.
- `updateTag('tag')` immediately expires tagged cache (Server Actions only, read-your-own-writes).
- `redirect()` throws a control-flow exception; any code after it does not run.

## Cookies in Server Actions

You can get, set, and delete cookies inside a Server Action using `cookies()` from `next/headers`. Setting/deleting a cookie re-renders the current page so the UI reflects the new cookie value.

## Security

- Authenticate and authorize inside every Server Action.
- Validate inputs (shape is not enough; check ownership).
- Send references/IDs from the client, not full records.
- Constrain return values to what the UI needs.
- Configure `serverActions.allowedOrigins` for proxy/CDN domains.
- `serverActions.bodySizeLimit` defaults to 1MB.
- Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` for multi-instance/self-hosted deployments.

## Sequential dispatch

Next.js dispatches Server Actions one at a time per client. Do not rely on `Promise.all` to parallelize them from the client. Do parallel work inside a single Server Action or use a Route Handler for non-mutation requests.

## Source URLs

- Mutating Data: https://nextjs.org/docs/app/getting-started/mutating-data
- Server Actions guide: https://nextjs.org/docs/app/guides/server-actions
- Forms guide: https://nextjs.org/docs/app/guides/forms
- Data Security guide: https://nextjs.org/docs/app/guides/data-security
- `use server` directive: https://nextjs.org/docs/app/api-reference/directives/use-server
- `serverActions` config: https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions
- `revalidatePath` / `revalidateTag` / `updateTag` / `refresh`: see `caching-and-revalidation.md`
