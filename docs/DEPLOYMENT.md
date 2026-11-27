# Cloudflare Pages deployment

The Cloudflare Pages Free project is connected to `thenirajshah/Unity-Engineering-` and publishes the `main` branch to `https://unity-engineering.pages.dev`.

1. In the Cloudflare dashboard, open Workers & Pages and create a Pages application using Git integration.
2. Authorize Cloudflare to access the Unity-Engineering repository and select it. Use `main` as the production branch.
3. Select the **None** framework preset, `npm run build` for the build command and `dist` for the output directory. Use the repository root as the root directory.
4. Deploy once and record the actual HTTPS `pages.dev` origin shown by Cloudflare.
5. The Cloudflare Pages build on `main` uses the production origin automatically. To override it, set `SITE_URL` as a **Production** environment variable without a trailing slash and redeploy. Previews should omit `SITE_URL`.
6. Open the production homepage, a detail route, the PDF and an invalid route. Check HTTPS, security headers, PDF delivery, legacy redirects, 404 status, `robots.txt` and `sitemap.xml`. Verify the email and WhatsApp drafts from a normal browser.

Cloudflare Pages takes care of TLS and deploys automatically from `main` once linked. Headers live in `public/_headers` and redirects are generated during build. No API keys or paid dependencies are needed.

For a one-off manual deployment, build first and upload the contents of `dist/` to a Pages Direct Upload project. Choose Git integration for automatic deployments.

Local and preview builds omit indexing unless `SITE_URL` is explicitly provided.

## Push the preserved Git history

When using a fresh checkout, verify that `origin` points to the dedicated repository before pushing.

```sh
git remote add origin https://github.com/thenirajshah/Unity-Engineering-.git
git push -u origin main
git push origin --tags
```
