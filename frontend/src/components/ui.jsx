import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

// ── Formatting ────────────────────────────────────────────────

const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

export const formatMoney = (value) => usd.format(Number(value) || 0)

/** "#0001" style account number */
export const formatAccountNo = (id) => `#${String(id).padStart(4, '0')}`

export const capitalize = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)

// Backend timestamps are UTC without a "Z" suffix; add it so the browser converts to local time
export const parseDate = (value) =>
  new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value}Z`)

export const formatTime = (value) =>
  parseDate(value).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })

/** "Today" / "Yesterday" / "Mon, Sep 29" */
export function formatDay(value) {
  const d = parseDate(value)
  const today = new Date()
  const yesterday = new Date()
  yesterday.setDate(today.getDate() - 1)
  if (d.toDateString() === today.toDateString()) return 'Today'
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return d.toLocaleDateString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: d.getFullYear() === today.getFullYear() ? undefined : 'numeric',
  })
}

export const errorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (!err?.response) return 'Can’t reach the server. Is the backend running?'
  return fallback
}

/**
 * Transactions come newest-first. Starting from the current balance, walk
 * backwards to work out what the balance was right after each one.
 */
export function withRunningBalance(transactions, currentBalance) {
  let balance = Number(currentBalance)
  return transactions.map((t) => {
    const row = { ...t, balanceAfter: balance }
    const signed = t.txnType === 'deposit' ? Number(t.amount) : -Number(t.amount)
    balance -= signed
    return row
  })
}

// ── Recently viewed accounts (per-browser convenience) ────────

const RECENT_KEY = 'simple-bank:recent-accounts'

export function getRecentAccounts() {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY)) || []
  } catch {
    return []
  }
}

export function rememberAccount(entry) {
  try {
    const rest = getRecentAccounts().filter((a) => a.id !== entry.id)
    localStorage.setItem(RECENT_KEY, JSON.stringify([entry, ...rest].slice(0, 4)))
  } catch {
    /* storage unavailable: ignore */
  }
}

// ── Icons ─────────────────────────────────────────────────────

const Svg = ({ children, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {children}
  </svg>
)

export const Icon = {
  ArrowDown: (p) => <Svg {...p}><path d="M12 5v14M19 12l-7 7-7-7" /></Svg>,
  ArrowUp: (p) => <Svg {...p}><path d="M12 19V5M5 12l7-7 7 7" /></Svg>,
  Back: (p) => <Svg {...p}><path d="M15 18l-6-6 6-6" /></Svg>,
  Plus: (p) => <Svg {...p}><path d="M12 5v14M5 12h14" /></Svg>,
  List: (p) => <Svg {...p}><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" /></Svg>,
  Search: (p) => <Svg {...p}><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /></Svg>,
  Alert: (p) => <Svg {...p}><circle cx="12" cy="12" r="9" /><path d="M12 8v4M12 16h.01" /></Svg>,
  Check: (p) => <Svg {...p}><path d="M20 6L9 17l-5-5" /></Svg>,
  Receipt: (p) => <Svg {...p}><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3z" /><path d="M9 8h6M9 12h6" /></Svg>,
}

// ── Small building blocks ─────────────────────────────────────

export function Layout({ children }) {
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand">
            <span className="brand-mark">S</span>
            Simple Bank
          </Link>
          <Link to="/create-account" className="btn btn-ghost btn-sm" aria-label="Open account">
            <Icon.Plus size={16} /> <span className="hide-sm">Open account</span>
          </Link>
        </div>
      </header>
      <main className="page">{children}</main>
    </>
  )
}

export function BackLink({ to, children = 'Back' }) {
  const navigate = useNavigate()
  return (
    <button type="button" className="back" onClick={() => navigate(to)}>
      <Icon.Back size={16} /> {children}
    </button>
  )
}

export function Alert({ kind = 'error', children }) {
  if (!children) return null
  return (
    <div className={`alert alert-${kind}`} role={kind === 'error' ? 'alert' : 'status'}>
      {kind === 'error' ? <Icon.Alert /> : <Icon.Check />}
      <span>{children}</span>
    </div>
  )
}

export function Toast({ children }) {
  if (!children) return null
  return (
    <div className="toast" role="status">
      <Icon.Check size={16} /> {children}
    </div>
  )
}

export const Spinner = () => <span className="spinner" aria-hidden="true" />

export function TxnRow({ txn, showDay = true }) {
  const isIn = txn.txnType === 'deposit'
  return (
    <div className="txn">
      <div className={`txn-icon ${isIn ? 'in' : 'out'}`}>
        {isIn ? <Icon.ArrowDown /> : <Icon.ArrowUp />}
      </div>
      <div className="txn-main">
        <div className="txn-title">{isIn ? 'Deposit' : 'Withdrawal'}</div>
        <div className="txn-meta">
          {showDay && `${formatDay(txn.createdAt)} · `}{formatTime(txn.createdAt)}<span className="ref"> · Ref {txn.txnId}</span>
        </div>
      </div>
      <div className="txn-right">
        <div className={`txn-amount ${isIn ? 'in' : 'out'}`}>
          {isIn ? '+' : '−'}{formatMoney(txn.amount)}
        </div>
        {txn.balanceAfter !== undefined && (
          <div className="txn-balance">{formatMoney(txn.balanceAfter)}</div>
        )}
      </div>
    </div>
  )
}

export function EmptyTransactions() {
  return (
    <div className="empty">
      <div className="empty-icon"><Icon.Receipt /></div>
      <strong>No transactions yet</strong>
      Deposits and withdrawals will show up here.
    </div>
  )
}
