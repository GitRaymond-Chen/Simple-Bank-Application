import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createUser, createAccount } from '../api/bank'
import { Alert, BackLink, Spinner, errorMessage } from '../components/ui'

const TYPES = [
  { value: 'checking', title: 'Checking', sub: 'For everyday spending' },
  { value: 'savings', title: 'Savings', sub: 'For setting money aside' },
]

export default function CreateAccountPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', accountType: 'checking' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      // Step 1: create the user (or get the existing one for this email)
      const user = await createUser(form.name.trim(), form.email.trim())
      // Step 2: open an account for that user
      const account = await createAccount(user.userId, form.accountType)
      navigate(`/accounts/${account.accountId}`, { state: { flash: 'Account opened' } })
    } catch (err) {
      setError(errorMessage(err, 'Something went wrong'))
      setLoading(false)
    }
  }

  return (
    <div className="narrow fade-in">
      <BackLink to="/">Home</BackLink>

      <div className="card">
        <div className="page-head">
          <h1>Open an account</h1>
          <p>It only takes a moment.</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label className="label" htmlFor="name">Full name</label>
            <input id="name" className="input" name="name" value={form.name}
              onChange={handleChange} required maxLength={100} autoComplete="name"
              placeholder="Alice Smith" autoFocus />
          </div>

          <div className="field">
            <label className="label" htmlFor="email">Email</label>
            <input id="email" className="input" name="email" type="email" value={form.email}
              onChange={handleChange} required maxLength={100} autoComplete="email"
              placeholder="alice@example.com" />
          </div>

          <div className="field">
            <span className="label" id="type-label">Account type</span>
            <div className="choice-group" role="radiogroup" aria-labelledby="type-label">
              {TYPES.map((t) => (
                <label key={t.value} className={`choice ${form.accountType === t.value ? 'selected' : ''}`}>
                  <input type="radio" name="accountType" value={t.value}
                    checked={form.accountType === t.value} onChange={handleChange} />
                  <div className="choice-title">{t.title}</div>
                  <div className="choice-sub">{t.sub}</div>
                </label>
              ))}
            </div>
          </div>

          <Alert>{error}</Alert>

          <button className="btn btn-primary btn-block" type="submit" disabled={loading} style={{ marginTop: 8 }}>
            {loading ? <><Spinner /> Opening account…</> : 'Open account'}
          </button>
        </form>
      </div>
    </div>
  )
}
