import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getTransactions } from '../api/bank'
import { card, btnSecondary, title } from './HomePage'

export default function TransactionsPage() {
  const { accountId } = useParams()
  const navigate = useNavigate()
  const [transactions, setTransactions] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getTransactions(accountId)
      .then(setTransactions)
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load transactions'))
  }, [accountId])

  return (
    <div style={{ ...card, maxWidth: 620 }}>
      <h1 style={title}>Transactions</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
        Account ID: <strong>{accountId}</strong>
      </p>

      {error && <p style={{ color: '#dc2626', fontWeight: 500 }}>{error}</p>}

      {transactions.length === 0 && !error ? (
        <p style={{ color: '#94a3b8' }}>No transactions yet.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
          <thead>
            <tr style={{ background: '#f1f5f9' }}>
              <Th>Txn ID</Th>
              <Th>Type</Th>
              <Th>Amount</Th>
              <Th>Date</Th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.txnId} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <Td>{txn.txnId}</Td>
                <Td>
                  <span style={{
                    padding: '2px 10px',
                    borderRadius: 12,
                    fontWeight: 600,
                    fontSize: '0.85rem',
                    background: txn.txnType === 'deposit' ? '#dcfce7' : '#fee2e2',
                    color: txn.txnType === 'deposit' ? '#166534' : '#991b1b',
                  }}>
                    {txn.txnType}
                  </span>
                </Td>
                <Td>${Number(txn.amount).toFixed(2)}</Td>
                <Td style={{ color: '#64748b' }}>{new Date(txn.createdAt).toLocaleString()}</Td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button style={btnSecondary} onClick={() => navigate(`/accounts/${accountId}`)}>
        Back
      </button>
    </div>
  )
}

function Th({ children }) {
  return (
    <th style={{ padding: '0.6rem 0.75rem', textAlign: 'left', fontWeight: 600, color: '#374151' }}>
      {children}
    </th>
  )
}

function Td({ children, style }) {
  return (
    <td style={{ padding: '0.6rem 0.75rem', ...style }}>
      {children}
    </td>
  )
}
