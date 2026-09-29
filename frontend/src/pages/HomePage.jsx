import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Icon, capitalize, formatAccountNo, getRecentAccounts } from '../components/ui'

export default function HomePage() {
  const navigate = useNavigate()
  const [accountId, setAccountId] = useState('')
  const recent = getRecentAccounts()

  const openAccount = (e) => {
    e.preventDefault()
    const id = accountId.replace(/\D/g, '')
    if (id) navigate(`/accounts/${Number(id)}`)
  }

  return (
    <div className="fade-in">
      <section className="hero">
        <h1>Banking, made simple.</h1>
        <p>Open an account in seconds, move money instantly, and keep track of every transaction.</p>
      </section>

      <div className="home-grid">
        <div className="card">
          <div className="icon-tile"><Icon.Plus /></div>
          <div className="card-body">
            <h2 className="card-title">Open a new account</h2>
            <p className="card-sub">Checking or savings, no minimum balance.</p>
          </div>
          <Link to="/create-account" className="btn btn-primary btn-block">Get started</Link>
        </div>

        <div className="card">
          <div className="icon-tile"><Icon.Search /></div>
          <div className="card-body">
            <h2 className="card-title">View an existing account</h2>
            <p className="card-sub">Enter your account number to see your balance and activity.</p>
          </div>
          <form className="inline-form" onSubmit={openAccount}>
            <input
              className="input"
              inputMode="numeric"
              placeholder="Account number"
              aria-label="Account number"
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
            />
            <button className="btn btn-secondary" type="submit" disabled={!accountId.trim()}>
              View
            </button>
          </form>
        </div>
      </div>

      {recent.length > 0 && (
        <>
          <div className="section-head"><h2>Recently viewed</h2></div>
          <div className="recent">
            {recent.map((a) => (
              <Link key={a.id} to={`/accounts/${a.id}`} className="recent-item">
                <strong className="num">{formatAccountNo(a.id)}</strong>
                <span className="muted">{a.name} · {capitalize(a.type)}</span>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
