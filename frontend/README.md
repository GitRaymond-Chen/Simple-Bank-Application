# Simple Bank · Frontend

React 18 + Vite single-page app for the [Simple Bank API](../README.md).

<img src="../docs/screenshots/history.jpg" alt="Transaction history page" width="640" />

## Run it

The backend must be running first (see the [main README](../README.md#quick-start)).

```bash
npm install
npm run dev        # http://localhost:5173
```

| Script | What it does |
|---|---|
| `npm run dev` | Dev server with hot reload |
| `npm run build` | Production build into `dist/` |
| `npm run preview` | Serve the production build locally |

### Pointing at the API

In development, Vite proxies every `/api/*` request to the backend (see [`vite.config.js`](vite.config.js)), so there are no CORS issues and no URLs to configure. The default target is `http://localhost:8000`; override it with `API_URL`:

```bash
API_URL=http://localhost:8001 npm run dev
```

## Pages

| Route | Page | What's on it |
|---|---|---|
| `/` | Home | Open a new account, look one up by number, recently viewed accounts |
| `/create-account` | Open account | Name, email, checking/savings picker |
| `/accounts/:id` | Account | Balance card, Deposit / Withdraw / History actions, last 5 transactions |
| `/accounts/:id/deposit` | Deposit | Large amount input, quick amounts, inline validation |
| `/accounts/:id/withdraw` | Withdraw | Same as deposit, plus **Max** and an over-balance warning |
| `/accounts/:id/transactions` | History | Money in / out totals, transactions grouped by day, running balance |

## Structure

```
src/
├── main.jsx                 # entry point
├── App.jsx                  # routes, wrapped in the shared Layout
├── styles.css               # the whole design system (tokens, components, dark mode)
├── api/
│   └── bank.js              # axios client, one function per endpoint
├── components/
│   ├── ui.jsx               # Layout, TxnRow, Alert, Toast, icons, formatting helpers
│   └── AmountForm.jsx       # shared deposit/withdraw form
└── pages/                   # one component per route
```

## Design notes

- **One stylesheet, no UI library.** Colors, radii and shadows are CSS custom properties on `:root` in [`styles.css`](src/styles.css). Change them there to re-theme the whole app.
- **Light and dark mode** follow the operating system (`prefers-color-scheme`).
- **Responsive** down to 320px wide; layouts collapse to a single column on phones.
- **Money** is formatted with `Intl.NumberFormat` as USD, using tabular figures so digits line up.
- **Running balance** in the history is computed on the client, starting from the current balance and walking back through the transactions ([`withRunningBalance`](src/components/ui.jsx)).
- **Errors:** the API always returns `{ "detail": "…" }`, which is shown as-is. Network failures show a "can't reach the server" message instead.
- **Recently viewed accounts** are kept in `localStorage`. They're only a convenience, so the app works fine without them.
- **Motion** is minimal (fade-ins, loading skeletons, toasts) and turned off for users who prefer reduced motion.
