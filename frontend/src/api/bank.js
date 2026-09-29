import axios from 'axios'

// All API calls go through this axios instance.
// The Vite proxy forwards /api/* to http://localhost:8000.
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── User endpoints ────────────────────────────────────────────

/** Create a new user. Returns the created user object. */
export const createUser = (name, email) =>
  api.post('/users', { name, email }).then((r) => r.data)

/** Fetch a user by ID. */
export const getUser = (userId) =>
  api.get(`/users/${userId}`).then((r) => r.data)

// ── Account endpoints ─────────────────────────────────────────

/** Open a new account for a user. accountType: 'checking' | 'savings' */
export const createAccount = (userId, accountType) =>
  api.post('/accounts', { userId, accountType }).then((r) => r.data)

/** Fetch account details (including balance) by account ID. */
export const getAccount = (accountId) =>
  api.get(`/accounts/${accountId}`).then((r) => r.data)

/** Deposit an amount into an account. Returns updated account. */
export const deposit = (accountId, amount) =>
  api.post(`/accounts/${accountId}/deposit`, { amount }).then((r) => r.data)

/** Withdraw an amount from an account. Returns updated account. */
export const withdraw = (accountId, amount) =>
  api.post(`/accounts/${accountId}/withdraw`, { amount }).then((r) => r.data)

/** Fetch all transactions for an account (newest first). */
export const getTransactions = (accountId) =>
  api.get(`/accounts/${accountId}/transactions`).then((r) => r.data)
