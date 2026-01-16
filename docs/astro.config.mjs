// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
  base: '/infoproj/',
  integrations: [
    starlight({
      title: 'Parkour Game Docs',
      description: 'Documentation for the Parkour Game platformer',
      social: {
        github: 'https://github.com/your-username/parkour-game',
      },
      sidebar: [
        {
          label: 'Getting Started',
          items: [
            { label: 'Introduction', slug: 'getting-started/introduction' },
            { label: 'Installation', slug: 'getting-started/installation' },
            { label: 'Quick Start', slug: 'getting-started/quick-start' },
          ],
        },
        {
          label: 'Guides',
          items: [
            { label: 'Adding Characters', slug: 'guides/adding-characters' },
            { label: 'Creating Levels', slug: 'guides/creating-levels' },
            { label: 'Creating Screens', slug: 'guides/creating-screens' },
            { label: 'Using Textures', slug: 'guides/using-textures' },
            { label: 'Deploying to GitHub Pages', slug: 'guides/deploying-to-github-pages' },
            { label: 'AI Contribution Guide', slug: 'guides/ai-contribution-guide' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { label: 'Level Format', slug: 'reference/level-format' },
            { label: 'Platform Types', slug: 'reference/platform-types' },
            { label: 'Character Class', slug: 'reference/character-class' },
            { label: 'Screen Base Class', slug: 'reference/screen-base-class' },
          ],
        },
        {
          label: 'API',
          autogenerate: { directory: 'api' },
        },
      ],
      customCss: [
        './src/styles/custom.css',
      ],
    }),
  ],
});
