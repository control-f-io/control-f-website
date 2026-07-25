# Website of control-f

## Development

To run a local webserver to develop the site run `uv run -m http.server` in the repo root.

## Deployment

Every merge to `main` publishes the repo root to GitHub Pages via
`.github/workflows/deploy.yml`. No build step — the files are served as they are.

- Website: https://control-f-io.github.io/control-f-website/
- Design system: https://control-f-io.github.io/control-f-website/design-system/

Because the site is served from a subpath, links and asset references must stay
**relative** (`assets/css/main.css`, `../index.html`) — a leading `/` would
resolve against `control-f-io.github.io` and 404.

## Fragen

- contact email: info@control-f.io?
- host control-f.io or controlf.io or both?
- Use a hamburger manu at the header?
- Do we want "Home" Link at the top?
- Should we remove the map, mail and linkdin elegments at the start of the homepage?

## TODOs

- Add Favicon and control-f svg logo
- Add text animations, like in the old page?
- SEO optimizations
- optimize for Google Lighthouse
- Add english variants (do this at the very end)