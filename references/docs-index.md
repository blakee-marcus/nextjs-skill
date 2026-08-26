# Next.js Docs Index

Navigation + source inventory for the Next.js skill. Each entry maps a URL to its topic, relevance to agent tasks, and the local reference file that owns the extracted operational knowledge.

This index was initially populated from the Next.js 16.3.3 `llms.txt` index and high-priority official pages. **Always verify the installed `next` version** before trusting any specific API detail; behavior changes across releases.

## Getting Started

| Topic | URL | Owner reference |
|---|---|---|
| Installation | https://nextjs.org/docs/app/getting-started/installation | `app-router.md` |
| Project Structure | https://nextjs.org/docs/app/getting-started/project-structure | `app-router.md` |
| Layouts and Pages | https://nextjs.org/docs/app/getting-started/layouts-and-pages | `routing-and-navigation.md` |
| Linking and Navigating | https://nextjs.org/docs/app/getting-started/linking-and-navigating | `routing-and-navigation.md` |
| Server and Client Components | https://nextjs.org/docs/app/getting-started/server-and-client-components | `server-client-components.md` |
| Fetching Data | https://nextjs.org/docs/app/getting-started/fetching-data | `data-fetching-and-streaming.md` |
| Mutating Data | https://nextjs.org/docs/app/getting-started/mutating-data | `mutations-and-server-actions.md` |
| Caching | https://nextjs.org/docs/app/getting-started/caching | `caching-and-revalidation.md` |
| Revalidating | https://nextjs.org/docs/app/getting-started/revalidating | `caching-and-revalidation.md` |
| Error Handling | https://nextjs.org/docs/app/getting-started/error-handling | `error-handling.md` |
| CSS | https://nextjs.org/docs/app/getting-started/css | `css-images-fonts-metadata.md` |
| Image Optimization | https://nextjs.org/docs/app/getting-started/images | `css-images-fonts-metadata.md` |
| Font Optimization | https://nextjs.org/docs/app/getting-started/fonts | `css-images-fonts-metadata.md` |
| Metadata and OG Images | https://nextjs.org/docs/app/getting-started/metadata-and-og-images | `css-images-fonts-metadata.md` |
| Route Handlers | https://nextjs.org/docs/app/getting-started/route-handlers | `routing-and-navigation.md` |
| Proxy | https://nextjs.org/docs/app/getting-started/proxy | `routing-and-navigation.md` |
| Deploying | https://nextjs.org/docs/app/getting-started/deploying | `deployment-and-production.md` |
| Upgrading | https://nextjs.org/docs/app/getting-started/upgrading | `migration-and-upgrades.md` |

## Guides

| Topic | URL | Owner reference |
|---|---|---|
| AI Coding Agents | https://nextjs.org/docs/app/guides/ai-agents | `source-manifest.md`, `debugging-and-development.md` |
| Building | https://nextjs.org/docs/app/guides/building | `turbopack-and-build.md` |
| Caching (Previous Model) | https://nextjs.org/docs/app/guides/caching-without-cache-components | `caching-and-revalidation.md` |
| Debugging | https://nextjs.org/docs/app/guides/debugging | `debugging-and-development.md` |
| Development Environment | https://nextjs.org/docs/app/guides/local-development | `debugging-and-development.md` |
| Forms | https://nextjs.org/docs/app/guides/forms | `mutations-and-server-actions.md` |
| How Revalidation Works | https://nextjs.org/docs/app/guides/how-revalidation-works | `caching-and-revalidation.md` |
| Instant Navigation | https://nextjs.org/docs/app/guides/instant-navigation | `routing-and-navigation.md`, `caching-and-revalidation.md` |
| ISR with Cache Components | https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components | `caching-and-revalidation.md` |
| Migrating to Cache Components | https://nextjs.org/docs/app/guides/migrating-to-cache-components | `migration-and-upgrades.md`, `caching-and-revalidation.md` |
| Next.js MCP Server | https://nextjs.org/docs/app/guides/mcp | `debugging-and-development.md` |
| Server and Client Boundary | https://nextjs.org/docs/app/guides/server-and-client-boundary | `server-client-components.md` |
| Server Actions and Mutations | https://nextjs.org/docs/app/guides/server-actions | `mutations-and-server-actions.md` |
| Streaming | https://nextjs.org/docs/app/guides/streaming | `data-fetching-and-streaming.md` |
| Testing overview | https://nextjs.org/docs/app/guides/testing | `testing.md` |
| Upgrading to Version 16 | https://nextjs.org/docs/app/guides/upgrading/version-16 | `migration-and-upgrades.md` |

## API Reference

| Topic | URL | Owner reference |
|---|---|---|
| `cacheComponents` | https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents | `configuration.md`, `caching-and-revalidation.md` |
| `cacheLife` | https://nextjs.org/docs/app/api-reference/functions/cacheLife | `caching-and-revalidation.md` |
| `cacheTag` | https://nextjs.org/docs/app/api-reference/functions/cacheTag | `caching-and-revalidation.md` |
| `cookies` / `headers` | https://nextjs.org/docs/app/api-reference/functions/cookies | `data-fetching-and-streaming.md`, `caching-and-revalidation.md` |
| `redirect` / `permanentRedirect` | https://nextjs.org/docs/app/api-reference/functions/redirect | `routing-and-navigation.md` |
| `revalidatePath` | https://nextjs.org/docs/app/api-reference/functions/revalidatePath | `caching-and-revalidation.md` |
| `revalidateTag` | https://nextjs.org/docs/app/api-reference/functions/revalidateTag | `caching-and-revalidation.md` |
| `updateTag` | https://nextjs.org/docs/app/api-reference/functions/updateTag | `caching-and-revalidation.md` |
| `refresh` | https://nextjs.org/docs/app/api-reference/functions/refresh | `caching-and-revalidation.md` |
| `route` file convention | https://nextjs.org/docs/app/api-reference/file-conventions/route | `routing-and-navigation.md` |
| `proxy` file convention | https://nextjs.org/docs/app/api-reference/file-conventions/proxy | `routing-and-navigation.md` |
| `serverActions` config | https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions | `configuration.md`, `mutations-and-server-actions.md` |
| `turbopack` config | https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack | `configuration.md`, `turbopack-and-build.md` |
| `use cache` directive | https://nextjs.org/docs/app/api-reference/directives/use-cache | `caching-and-revalidation.md` |
| `use cache: private` | https://nextjs.org/docs/app/api-reference/directives/use-cache-private | `caching-and-revalidation.md` |
| `use cache: remote` | https://nextjs.org/docs/app/api-reference/directives/use-cache-remote | `caching-and-revalidation.md` |
| `use client` directive | https://nextjs.org/docs/app/api-reference/directives/use-client | `server-client-components.md` |
| `use server` directive | https://nextjs.org/docs/app/api-reference/directives/use-server | `mutations-and-server-actions.md` |
| `Image` component | https://nextjs.org/docs/app/api-reference/components/image | `css-images-fonts-metadata.md` |
| `Font` / `next/font` | https://nextjs.org/docs/app/api-reference/components/font | `css-images-fonts-metadata.md` |
| `Link` component | https://nextjs.org/docs/app/api-reference/components/link | `routing-and-navigation.md` |

## Version notes

- Snapshot version: **16.3.3**.
- Verify installed version with the package manager before applying any API-specific detail.
- For older projects, consult the previous-model caching guide and version-specific upgrade docs.

## Ownership model

As references grow, each concept has exactly one **canonical local owner**. Other files summarize or cross-link but do not duplicate the full explanation. The table above is the source-of-truth map.

When ingesting a new page, update this index and route extracted knowledge to the owner reference. If no owner exists, create a new reference file rather than duplicating into an unrelated one.
