# CSS, Images, Fonts, and Metadata

## CSS

Next.js supports:

- **Global CSS** — import `.css` files.
- **CSS Modules** — `*.module.css`, scoped locally.
- **Tailwind CSS** — use the installed Tailwind skill for Tailwind-specific semantics; this skill owns the Next.js integration boundary.
- **Sass** — built-in support for `.scss` / `.sass`.
- **CSS-in-JS** — see the CSS-in-JS guide for library-specific setup.

## Images

Use `next/image` for optimized images:

```tsx
import Image from 'next/image'

<Image src="/profile.png" alt="Profile" width={500} height={500} />
```

- Static imports provide automatic `width`, `height`, `blurDataURL`.
- Remote images require explicit dimensions and `next.config.js` `images.remotePatterns`.
- Use `fill` prop to make the image fill its parent container.
- Store static files in `public/`.

## Fonts

`next/font` automatically optimizes and self-hosts fonts:

```tsx
import { Geist } from 'next/font/google'

const geist = Geist({ subsets: ['latin'] })

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={geist.className}>
      <body>{children}</body>
    </html>
  )
}
```

- Google Fonts are downloaded at build time; no runtime request to Google.
- Local fonts use `localFont` from `next/font/local`.
- Variable fonts are preferred for performance and flexibility.

## Metadata

Define static metadata by exporting a `metadata` object, or dynamic metadata with `generateMetadata`:

```tsx
export const metadata = {
  title: 'My Site',
  description: '...',
}
```

File conventions for icons / Open Graph / Twitter images:

- `favicon.ico`, `icon.*`, `apple-icon.*`
- `opengraph-image.*`, `twitter-image.*`
- Generated versions are `.js`, `.ts`, `.tsx`.
- `sitemap.xml` / `sitemap.ts`, `robots.txt` / `robots.ts`.

## Source URLs

- CSS: https://nextjs.org/docs/app/getting-started/css
- Images: https://nextjs.org/docs/app/getting-started/images
- Fonts: https://nextjs.org/docs/app/getting-started/fonts
- Metadata and OG Images: https://nextjs.org/docs/app/getting-started/metadata-and-og-images
- `Image` component: https://nextjs.org/docs/app/api-reference/components/image
- `Font` component: https://nextjs.org/docs/app/api-reference/components/font
- `metadata` API: https://nextjs.org/docs/app/api-reference/functions/generate-metadata
