# Cloudflare Pages deployment

Use Cloudflare Pages Free and the dedicated Unity-Engineering GitHub repository.

1. In the Cloudflare dashboard, open Workers & Pages and create a Pages application using Git integration.
2. Authorize Cloudflare to access the Unity-Engineering repository and select it. Use `main` as the production branch.
3. Select the **None** framework preset, `npm run build` for the build command and `dist` for the output directory. Use the repository root as the root directory.
4. Deploy once and record the actual HTTPS `pages.dev` origin shown by Cloudflare.
5. To enable production indexing, add `SITE_URL` as a **Production** environment variable using that origin, without a trailing slash. Redeploy. Previews should omit `SITE_URL`.
6. Open the production homepage, a detail route, the PDF and an invalid route. Check HTTPS, security headers, PDF delivery, legacy redirects, 404 status, `robots.txt` and `sitemap.xml`. Verify the email and WhatsApp drafts from a normal browser.

Cloudflare Pages takes care of TLS and deploys automatically from `main` once linked. Headers live in `public/_headers` and redirects are generated during build. No API keys or paid dependencies are needed.

For a one-off manual deployment, build first and upload the contents of `dist/` to a Pages Direct Upload project. Choose Git integration for automatic deployments.

Production indexing is disabled in local and preview builds. Set the actual confirmed production origin before creating sitemap and canonical URLs.

## Push the preserved Git history

The connected `thenirajshah` GitHub account could be identified, but its integration credential could not create repositories. An account owner can create an empty repository using the GitHub CLI authenticated as that owner:

```sh
gh auth login
gh repo create thenirajshah/Unity-Engineering --private
git remote add origin https://github.com/thenirajshah/Unity-Engineering.git
git push -u origin main
git push origin --tags
```

Run the Git commands from the original project checkout or clone the included Git bundle first. When a remote already exists, check that it points to this dedicated repository before pushing. Grant Cloudflare access only to this repository for the automatic deployment.
