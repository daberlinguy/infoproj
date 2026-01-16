---
title: Deploying to GitHub Pages
description: How to deploy your Starlight documentation to GitHub Pages
---

This guide explains how to deploy your documentation to GitHub Pages using GitHub Actions.

## Prerequisites

- A GitHub repository with your project
- The documentation in the `docs/` folder (Starlight/Astro)
- A GitHub account with permissions to create workflows

## Method 1: GitHub Actions (Recommended)

### Step 1: Create the Workflow File

Create a file at `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Docs to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: docs/package-lock.json

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Install dependencies
        run: npm ci
        working-directory: docs

      - name: Build with Astro
        run: npm run build
        working-directory: docs

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Step 2: Configure Astro for GitHub Pages

Update `docs/astro.config.mjs` to set the correct base URL:

```js
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  // Replace with your repository name
  site: 'https://YOUR_USERNAME.github.io',
  base: '/YOUR_REPO_NAME',
  
  integrations: [
    starlight({
      title: 'Parkour Game Docs',
      // ... rest of your config
    }),
  ],
});
```

For example, if your GitHub username is `johndoe` and repo is `parkour-game`:

```js
site: 'https://johndoe.github.io',
base: '/parkour-game',
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the sidebar)
3. Under **Build and deployment**:
   - Source: **GitHub Actions**
4. Save the settings

### Step 4: Push and Deploy

```bash
git add .
git commit -m "Add GitHub Pages deployment"
git push origin main
```

The workflow will automatically run when you push changes to the `docs/` folder.

## Method 2: Manual Deployment

If you prefer manual deployments:

### Build Locally

```bash
cd docs
npm install
npm run build
```

### Deploy with gh-pages

Install the `gh-pages` package:

```bash
npm install --save-dev gh-pages
```

Add a deploy script to `docs/package.json`:

```json
{
  "scripts": {
    "deploy": "astro build && gh-pages -d dist"
  }
}
```

Deploy:

```bash
npm run deploy
```

## Viewing Your Documentation

After deployment, your docs will be available at:

```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/
```

## Troubleshooting

### 404 Errors

- Make sure the `base` path in `astro.config.mjs` matches your repo name
- Check that GitHub Pages is enabled in repository settings
- Wait a few minutes for the deployment to complete

### Build Failures

Check the **Actions** tab in your repository for error logs:

1. Go to your repository on GitHub
2. Click **Actions**
3. Click on the failed workflow run
4. Expand the failed step to see the error

### Assets Not Loading

Make sure all asset paths use the base URL prefix:

```astro
<!-- Use relative paths -->
<img src="./image.png" />

<!-- Or use Astro's built-in handling -->
import { Image } from 'astro:assets';
<Image src={import('./image.png')} alt="..." />
```

## Custom Domain (Optional)

To use a custom domain:

1. Go to **Settings** → **Pages**
2. Enter your custom domain
3. Add a CNAME record in your DNS settings pointing to `YOUR_USERNAME.github.io`
4. Update `site` in `astro.config.mjs`:

```js
site: 'https://docs.yourdomain.com',
base: '/', // Can be '/' with custom domain
```

## Next Steps

- [Adding Content](/guides/creating-levels) - Learn to add new documentation pages
- [Starlight Docs](https://starlight.astro.build/) - Full Starlight documentation
