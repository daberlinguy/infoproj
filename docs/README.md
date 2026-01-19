# Parkour Game Documentation

This folder contains Starlight documentation for the Parkour Game project.

## Setup

1. Install dependencies:
   ```bash
   cd docs
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Structure

```
docs/
├── astro.config.mjs     # Starlight configuration
├── package.json         # NPM dependencies
├── src/
│   ├── content/
│   │   └── docs/        # Documentation pages
│   │       ├── getting-started/
│   │       ├── guides/
│   │       ├── reference/
│   │       └── api/
│   └── styles/
│       └── custom.css   # Custom styling
└── README.md            # This file
```

## Adding Documentation

1. Create a `.md` file in the appropriate folder
2. Add frontmatter:
   ```md
   ---
   title: Page Title
   description: Brief description
   ---
   ```
3. Write content in Markdown
4. Update `astro.config.mjs` sidebar if needed

## Deploying

The documentation can be deployed to any static host:

- GitHub Pages
- Netlify
- Vercel
- CloudFlare Pages

Build output is in `dist/` folder.
