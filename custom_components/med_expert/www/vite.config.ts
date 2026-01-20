import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'MedExpertPanel',
      fileName: () => 'med-expert-panel',
      formats: ['es'],
    },
    rollupOptions: {
      // Don't externalize lit - bundle it for HA compatibility
      output: {
        entryFileNames: '[name].js',
      },
    },
    // Build to .build/ then copy to parent
    outDir: '.build',
    emptyOutDir: true,
    sourcemap: false,
    minify: 'esbuild',
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
});
