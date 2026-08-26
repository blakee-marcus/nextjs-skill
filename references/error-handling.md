# Error Handling

Reference: https://nextjs.org/docs/app/getting-started/error-handling

## Expected errors

Model expected errors as return values, not thrown exceptions:

```ts
'use server'

export async function createPost(prevState: unknown, formData: FormData) {
  const title = formData.get('title')
  const res = await fetch('...', { method: 'POST', body: JSON.stringify({ title }) })
  if (!res.ok) return { message: 'Failed to create post' }
}
```

Use `useActionState` in Client Components to read the returned state and show feedback.

## Uncaught exceptions

Use error boundaries to catch unexpected errors during rendering and show fallback UI.

### `error.tsx`

```tsx
'use client'

export default function ErrorPage({
  error,
  retry,
}: {
  error: Error & { digest?: string }
  retry: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}
```

- Must be a Client Component.
- Errors bubble to the nearest parent error boundary.

### `catchError`

Component-level error boundaries for wrapping any subtree:

```tsx
'use client'

import { catchError, type ErrorInfo } from 'next/error'

function ErrorFallback(props: { title: string }, { error, retry }: ErrorInfo) {
  return (
    <div>
      <h2>{props.title}</h2>
      <p>{error.message}</p>
      <button onClick={() => retry()}>Try again</button>
    </div>
  )
}

export default catchError(ErrorFallback)
```

### `global-error.tsx`

Root-level error UI; must define its own `<html>` and `<body>` tags.

## `notFound`

Call `notFound()` from `next/navigation` to trigger the nearest `not-found.tsx`:

```tsx
import { notFound } from 'next/navigation'

if (!post) notFound()
```

## Error boundaries do not catch

- Errors in event handlers — catch manually with `try/catch` and state.
- Most async code unless inside `startTransition`, which bubbles to the nearest boundary.

## Source URLs

- Error Handling: https://nextjs.org/docs/app/getting-started/error-handling
- `error.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/error
- `catchError`: https://nextjs.org/docs/app/api-reference/functions/catchError
- `notFound`: https://nextjs.org/docs/app/api-reference/functions/not-found
- `not-found.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/not-found
