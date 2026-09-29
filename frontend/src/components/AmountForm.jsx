import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getAccount } from '../api/bank'
import {
  Alert, BackLink, Spinner, errorMessage, formatAccountNo, formatMoney,
} from './ui'

const QUICK_AMOUNTS = [20, 50, 100, 500]

/**
 * Shared deposit / withdraw screen.
 * mode: 'deposit' | 'withdraw'
 * submit: (accountId, amount) => Promise
 */
export default function AmountForm({ mode, submit }) {
  const { accountId } = useParams()
  const navigate = useNavigate()
  const [account, setAccount] = useState(null)
  const [amount, setAmount] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const isDeposit = mode === 'deposit'
  const verb = isDeposit ? 'Deposit' : 'Withdraw'

  useEffect(() => {
    getAccount(accountId)
      .then(setAccount)
      .catch((err) => setError(errorMessage(err, 'Account not found')))
  }, [accountId])

  const value = Number(amount)
  const balance = account ? Number(account.balance) : null
  const tooManyDecimals = /\.\d{3,}$/.test(amount)
  const overBalance = !isDeposit && balance !== null && value > balance
  const valid = amount !== '' && value > 0 && !tooManyDecimals && !overBalance

  const handleChange = (e) => {
    // Digits and one decimal point only
    const next = e.target.value.replace(/[^\d.]/g, '').replace(/(\..*)\./g, '$1')
    setAmount(next)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!valid) return
    setError(null)
    setLoading(true)
    try {
      await submit(accountId, amount)
      const done = isDeposit ? 'Deposited' : 'Withdrew'
      navigate(`/accounts/${accountId}`, { state: { flash: `${done} ${formatMoney(value)}` } })
    } catch (err) {
      setError(errorMessage(err, `${verb} failed`))
      setLoading(false)
    }
  }

  let hint = null
  if (tooManyDecimals) hint = { warn: true, text: 'Use at most 2 decimal places' }
  else if (overBalance) hint = { warn: true, text: `Exceeds available balance of ${formatMoney(balance)}` }
  else if (balance !== null) hint = { warn: false, text: `Available balance ${formatMoney(balance)}` }

  return (
    <div className="narrow fade-in">
      <BackLink to={`/accounts/${accountId}`}>Account {formatAccountNo(accountId)}</BackLink>

      <div className="card">
        <div className="page-head" style={{ marginBottom: 20 }}>
          <h1>{verb}</h1>
          <p>
            {isDeposit ? 'Add money to' : 'Take money out of'} account {formatAccountNo(accountId)}
          </p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          <label className="amount-wrap" htmlFor="amount">
            <span className="amount-currency">$</span>
            <input
              id="amount"
              className="amount-input"
              inputMode="decimal"
              autoComplete="off"
              placeholder="0.00"
              value={amount}
              onChange={handleChange}
              autoFocus
              aria-label="Amount in dollars"
              style={{ width: `${Math.max(amount.length, 4)}ch` }}
            />
          </label>

          {hint && <p className={`hint ${hint.warn ? 'warn' : ''}`}>{hint.text}</p>}

          <div className="chips">
            {QUICK_AMOUNTS.map((n) => (
              <button type="button" key={n} className="chip" onClick={() => { setAmount(String(n)); setError(null) }}>
                ${n}
              </button>
            ))}
            {!isDeposit && balance > 0 && (
              <button type="button" className="chip" onClick={() => { setAmount(balance.toFixed(2)); setError(null) }}>
                Max
              </button>
            )}
          </div>

          <Alert>{error}</Alert>

          <button className="btn btn-primary btn-block" type="submit" disabled={!valid || loading}>
            {loading ? <><Spinner /> Processing…</> : valid ? `${verb} ${formatMoney(value)}` : verb}
          </button>
        </form>
      </div>
    </div>
  )
}
