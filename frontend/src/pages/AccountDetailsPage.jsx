import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getAccount, getUser } from '../api/bank'
import { card, btn, btnSecondary, title } from './HomePage'

export default function AccountDetailsPage() {
  const { accountId } = useParams()
  const navigate = useNavigate()
  const [account, setAccount] = useState(null)
  const [user, setUser] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Fetch account info, then fetch the owner's name
    getAccount(accountId)
      .then((acc) => {
        setAccount(acc)
        return getUser(acc.userId)
      })
      .then(setUser)
      .catch((err) => setError(err.response?.data?.detail || 'Account not found'))
  }, [accountId])

  if (error) {
    return (
      <div style={card}>
        <p style={{ color: '#dc2626', fontWeight: 500 }}>{error}</p>
        <button style={btnSecondary} onClick={() => navigate('/')}>Back</button>
      </div>
    )
  }

  if (!account) {
    return <div style={card}><p style={{ color: '#64748b' }}>Loading...</p></div>
  }

  return (
    <div style={card}>
      <h1 style={title}>Account Details</h1>

      <div style={{ background: '#f8fafc', borderRadius: 8, padding: '1rem', marginBottom: '1.5rem' }}>
        <Row label="Account ID" value={account.accountId} />
        <Row label="Account Type" value={capitalize(account.accountType)} />
        <Row label="Owner" value={user?.name ?? '—'} />
        <Row label="Balance" value={`$${Number(account.balance).toFixed(2)}`} large />
      </div>

      <button style={btn} onClick={() => navigate(`/accounts/${accountId}/deposit`)}>
        Deposit
      </button>
      <button style={{ ...btn, background: '#dc2626', marginTop: '0.5rem' }}
        onClick={() => navigate(`/accounts/${accountId}/withdraw`)}>
        Withdraw
      </button>
      <button style={{ ...btn, background: '#0891b2', marginTop: '0.5rem' }}
        onClick={() => navigate(`/accounts/${accountId}/transactions`)}>
        View Transactions
      </button>
      <button style={btnSecondary} onClick={() => navigate('/')}>
        Back
      </button>
    </div>
  )
}

function Row({ label, value, large }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
      <span style={{ color: '#64748b', fontWeight: 500 }}>{label}</span>
      <span style={{ fontWeight: large ? 700 : 400, fontSize: large ? '1.25rem' : '1rem', color: '#1e293b' }}>
        {value}
      </span>
    </div>
  )
}

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s
}
