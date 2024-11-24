
import { defineConfig } from 'vite';
import dotenv from 'dotenv';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import { resolve } from 'path';

dotenv.config();

export default defineConfig({
    root: './bakery_store/static',
    base: process.env.STATIC_URL,
    build: {
        outDir: resolve("./bakery_store/static/dist"),
        manifest: true,
        rollupOptions: {
            input: {
                main: './bakery_store/static/src/js/main.js',
                styles: './bakery_store/static/src/styles/app.css'
            },
        },
    },
    plugins: [
        viteStaticCopy({
          targets: [
            {
                src: 'img/*',
                dest: 'assets/img',
            },
          ],
        }),
    ],
});
