# Frontend

React + TypeScript app built with Vite, styled with Tailwind CSS and shadcn/ui components.

- `src/pages/`: page components (Home, Browse, Product, Cart, Checkout, Order success, Account, Admin)
- `src/components/`: shared components (Header, Footer, ProductCard)
- `src/components/ui/`: shadcn components (added with `npx shadcn@latest add <component>`)
- `src/context/`: the store (cart, products, orders and the signed in account)
- `src/lib/`: API, form and shadcn helpers
- `src/data/`: the `Product` type and price formatting
- `docker/`: Dockerfile and Nginx config for the production image

## Setup

Run each command block from the repo root (`Placeholder-Store/`).

```sh
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

The frontend uses the API at http://127.0.0.1:8000/api. To use another address, set `VITE_API_URL`, for example `VITE_API_URL=http://127.0.0.1:9000/api npm run dev`.

Run tests with `npm test`. They cover the cart, checkout and API helpers, using a mocked API.

## Docker

If you have Docker installed, you can run the app in containers.

```sh
docker build -f frontend/docker/Dockerfile -t placeholder-store-frontend frontend
docker run -p 8080:80 placeholder-store-frontend
```

Then open http://localhost:8080. To point the image at another API, add `--build-arg VITE_API_URL=<api address>` to `docker build`.

See the [root README](../README.md) for full setup.
