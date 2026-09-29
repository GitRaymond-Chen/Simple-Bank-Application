import React, { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { deposit } from '../api/bank'
import { card, btn, btnSecondary, title } from './HomePage'

const inputStyle = {
  display: 'block',
  width: '100%',
  padding: '0.6rem 0.75rem',
  marginTop: '0.25rem',
  marginBottom: '1rem',
  borderRadius: 8,
  border: '1px solid #cbd5e1',
  fontSize: '1rem',
  boxSizing: 'border-box',
}

export default function DepositPage() {
  const { accountId } = useParams()
  const navigate = useNavigate()
  const [amount, setAmount] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await deposit(accountId, amount)
      // Go back to account details to see the updated balance
      navigate(`/accounts/${accountId}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Deposit failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={card}>
      <h1 style={title}>Deposit</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
        Account ID: <strong>{accountId}</strong>
      </p>

      <form onSubmit={handleSubmit}>
        <label style={{ fontWeight: 500, color: '#374151' }}>Amount ($)</label>
        <input
          style={inputStyle}
          type="number"
          step="0.01"
          min="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
          placeholder="100.00"
        />

        {error && (
          <p style={{ color: '#dc2626', marginBottom: '1rem', fontWeight: 500 }}>{error}</p>
        )}

        <button style={btn} type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Deposit'}
        </button>
      </form>

      <button style={btnSecondary} onClick={() => navigate(`/accounts/${accountId}`)}>
        Cancel
      </button>
    </div>
  )
}
