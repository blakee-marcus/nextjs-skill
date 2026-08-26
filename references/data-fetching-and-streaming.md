# Data Fetching and Streaming

Reference: https://nextjs.org/docs/app/getting-started/fetching-data

## Server Components

Server Components can fetch data directly during render using any async I/O:

```tsx
export default async function Page() {
  const posts = await (await fetch('https://api.example.com/posts')).json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

- Identical `fetch` requests in a React tree are **memoized** by default during a server render.
- `fetch` is **not cached by default** and blocks the page until complete. Opt in with `"use cache"` or stream with `Suspense`.
- Database / ORM queries are safe because they run only on the server.

## Streaming

Break slow data into smaller chunks and stream them from the server:

1. **`loading.tsx`** — wraps the segment in `Suspense` automatically.
2. **`<Suspense>`** — more granular control around a component.

```tsx
import { Suspense } from 'react'
import BlogList from '@/components/BlogList'
import BlogListSkeleton from '@/components/BlogListSkeleton'

export default function BlogPage() {
  return (
    <div>
      <header>
        <h1>Welcome to the Blog</h1>
      </header>
      <Suspense fallback={<BlogListSkeleton />}>
        <BlogList />
      </Suspense>
    </div>
  )
}
```

- Layouts that access uncached/runtime data do **not** fall back to a same-segment `loading.tsx`; they block navigation. Wrap the access in its own `Suspense` boundary.
- Bots/crawlers receive fully rendered HTML, not streaming.

## Client Components

Fetch in Client Components using:

- React `use` API to unwrap a promise passed from a Server Component.
- SWR or TanStack Query for client-side caching / refetching.

## Reusing data within a request

Wrap a data function with `React.cache` so multiple components in the same request share one result:

```ts
import { cache } from 'react'

export const getUser = cache(async () => {
  const res = await fetch('https://api.example.com/user')
  return res.json()
})
```

`React.cache` is scoped to the current request only.

## Source URLs

- Fetching Data: https://nextjs.org/docs/app/getting-started/fetching-data
- Streaming guide: https://nextjs.org/docs/app/guides/streaming
- `fetch` API reference: https://nextjs.org/docs/app/api-reference/functions/fetch
- `loading.js` convention: https://nextjs.org/docs/app/api-reference/file-conventions/loading
- React `use` API: https://react.dev/reference/react/use
