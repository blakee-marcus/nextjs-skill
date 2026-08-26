# Deployment and Production

Reference: https://nextjs.org/docs/app/getting-started/deploying

## Deployment options

| Option | Feature support |
|---|---|
| Node.js server | All |
| Docker container | All |
| Static export | Limited |
| Adapters | Varies |

## Node.js server

Ensure `package.json` has:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

Run `npm run build` then `npm run start`.

## Docker

Use `output: 'standalone'` for a minimal production image. See the official `with-docker` example.

## Static export

```ts
const nextConfig: NextConfig = {
  output: 'export',
}
```

Does not support Server Actions, Route Handlers, or runtime APIs that need a server.

## Adapters

The Deployment Adapter API lets platforms customize build and deploy. Verified adapters (Vercel, Bun) run the Next.js compatibility test suite. Other platforms may offer their own integrations; verify feature support with the provider.

## Self-hosting considerations

- Configure caching/ISR with a durable store if needed.
- Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` for Server Functions across instances.
- Use `connection()` for runtime env reads when needed.

## Source URLs

- Deploying: https://nextjs.org/docs/app/getting-started/deploying
- Self-hosting: https://nextjs.org/docs/app/guides/self-hosting
- Static exports: https://nextjs.org/docs/app/guides/static-exports
- Adapters: https://nextjs.org/docs/app/api-reference/adapters
- Docker examples: https://github.com/vercel/next.js/tree/canary/examples/with-docker
