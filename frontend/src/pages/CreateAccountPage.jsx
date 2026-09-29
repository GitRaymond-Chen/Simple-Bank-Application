import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createUser, createAccount } from '../api/bank'
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
      // Step 1: create the user
      const user = await createUser(form.name, form.email)
      // Step 2: open an account for that user
      const account = await createAccount(user.userId, form.accountType)
      // Navigate to the new account's detail page
      navigate(`/accounts/${account.accountId}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={card}>
      <h1 style={title}>Create Account</h1>

      <form onSubmit={handleSubmit}>
        <label style={{ fontWeight: 500, color: '#374151' }}>Full Name</label>
        <input
          style={inputStyle}
          name="name"
          value={form.name}
          onChange={handleChange}
          required
          placeholder="Alice Smith"
        />

        <label style={{ fontWeight: 500, color: '#374151' }}>Email</label>
        <input
          style={inputStyle}
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
          placeholder="alice@example.com"
        />

        <label style={{ fontWeight: 500, color: '#374151' }}>Account Type</label>
        <select
          style={inputStyle}
          name="accountType"
          value={form.accountType}
          onChange={handleChange}
        >
          <option value="checking">Checking</option>
          <option value="savings">Savings</option>
        </select>

        {error && (
          <p style={{ color: '#dc2626', marginBottom: '1rem', fontWeight: 500 }}>{error}</p>
        )}

        <button style={btn} type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Account'}
        </button>
      </form>

      <button style={btnSecondary} onClick={() => navigate('/')}>
        Back
      </button>
    </div>
  )
}
