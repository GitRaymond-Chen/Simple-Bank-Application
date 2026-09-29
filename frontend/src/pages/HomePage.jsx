import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

// Shared card style used across pages
export const card = {
  background: '#fff',
  borderRadius: 12,
  boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  padding: '2rem',
  maxWidth: 420,
  margin: '4rem auto',
}

export const btn = {
  display: 'block',
  width: '100%',
  padding: '0.75rem',
  marginTop: '0.75rem',
  borderRadius: 8,
  border: 'none',
  cursor: 'pointer',
  fontSize: '1rem',
  fontWeight: 600,
  background: '#2563eb',
  color: '#fff',
}

export const btnSecondary = { ...btn, background: '#6b7280' }

export const title = { margin: '0 0 1.5rem', fontSize: '1.5rem', color: '#1e293b' }

export default function HomePage() {
  const navigate = useNavigate()
  const [accountId, setAccountId] = useState('')

  return (
    <div style={card}>
      <h1 style={title}>Simple Bank</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
        Welcome! Create a new account or view an existing one.
      </p>

      <button style={btn} onClick={() => navigate('/create-account')}>
        Create Account
      </button>

      <hr style={{ margin: '1.5rem 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

      <label style={{ fontWeight: 500, color: '#374151' }}>View Account by ID</label>
      <input
        type="number"
        placeholder="Enter account ID"
        value={accountId}
        onChange={(e) => setAccountId(e.target.value)}
        style={{
          display: 'block',
          width: '100%',
          padding: '0.6rem 0.75rem',
          marginTop: '0.5rem',
          borderRadius: 8,
          border: '1px solid #cbd5e1',
          fontSize: '1rem',
          boxSizing: 'border-box',
        }}
      />
      <button
        style={btnSecondary}
        onClick={() => accountId && navigate(`/accounts/${accountId}`)}
      >
        View Account
      </button>
    </div>
  )
}
