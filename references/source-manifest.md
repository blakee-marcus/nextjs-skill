# Source Manifest

Provenance and authority notes for this skill.

## What this skill is

An independent, open Agent Skill for Next.js. It is **not** an official Vercel project. Next.js is a Vercel trademark and open-source project; see https://github.com/vercel/next.js for the source code and official license.

## Source material

- The initial navigation index came from the official Next.js `llms.txt` at https://nextjs.org/docs/llms.txt (version 16.3.3).
- Operational knowledge was extracted directly from official Next.js documentation pages at https://nextjs.org/docs/app/* and https://nextjs.org/docs/app/api-reference/*.
- Every implementation-sensitive claim in the references should be paired with a source URL. Where a URL is missing, treat it as a TODO for future ingestion.

## Authority order for agents

1. Installed `next` package version in the target project
2. Observed runtime / build behavior
3. Current official Next.js documentation for that version
4. Current Next.js source / release information
5. Bundled skill references
6. Existing project code as evidence of current assumptions
7. Remembered framework behavior

## Reading the official docs

Next.js documentation is available:

1. **Bundled with the installed package** (preferred for version match): `node_modules/next/dist/docs/`
2. **Over the network as Markdown**: append `.md` to any `https://nextjs.org/docs/...` URL, or send `Accept: text/markdown`.
3. **Per-error pages**: `https://nextjs.org/docs/messages/<error-id>`.

## Anti-hallucination guard

- URLs are URLs. Package identifiers like `@next/bundle-analyzer` and `next/third-parties` are NPM packages, not local `@file:` references.
- If extraction fails, retry via another supported path. Do not interpret missing content as absence of a feature.
- Never claim the skill is exhaustive or permanently current. Record the source URL for version-sensitive facts.

## License

Original skill content is MIT. Derived references are summaries of official Next.js documentation, which remains under its own license (https://github.com/vercel/next.js/blob/canary/license.md). Use this skill as a navigation aid and operational guide, not as a substitute for the official docs when exact semantics matter.
