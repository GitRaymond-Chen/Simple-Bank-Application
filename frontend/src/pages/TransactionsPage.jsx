import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getAccount, getTransactions } from '../api/bank'
import {
  Alert, BackLink, EmptyTransactions, TxnRow, errorMessage, formatAccountNo, formatDay,
  formatMoney, withRunningBalance,
} from '../components/ui'

export default function TransactionsPage() {
  const { accountId } = useParams()
  const [transactions, setTransactions] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getAccount(accountId), getTransactions(accountId)])
      .then(([acc, txns]) => setTransactions(withRunningBalance(txns, acc.balance)))
      .catch((err) => setError(errorMessage(err, 'Failed to load transactions')))
  }, [accountId])

  const totalIn = sum(transactions, 'deposit')
  const totalOut = sum(transactions, 'withdrawal')

  // Group consecutive transactions by day label ("Today", "Yesterday", ...)
  const groups = []
  for (const t of transactions ?? []) {
    const day = formatDay(t.createdAt)
    if (groups.at(-1)?.day !== day) groups.push({ day, items: [] })
    groups.at(-1).items.push(t)
  }

  return (
    <div className="medium fade-in">
      <BackLink to={`/accounts/${accountId}`}>Account {formatAccountNo(accountId)}</BackLink>

      <div className="page-head">
        <h1>Transaction history</h1>
        <p>All activity for account {formatAccountNo(accountId)}</p>
      </div>

      <Alert>{error}</Alert>

      {!error && (
        <>
          <div className="stats">
            <Stat label="Money in" value={transactions && formatMoney(totalIn)} className="in" />
            <Stat label="Money out" value={transactions && formatMoney(totalOut)} />
            <Stat label="Transactions" value={transactions?.length} />
          </div>

          <div className="txn-list">
            {transactions === null ? (
              [0, 1, 2].map((i) => (
                <div className="txn" key={i}>
                  <div className="skeleton" style={{ width: 38, height: 38, borderRadius: '50%' }} />
                  <div style={{ flex: 1 }}>
                    <div className="skeleton" style={{ width: '40%', height: 14, marginBottom: 6 }} />
                    <div className="skeleton" style={{ width: '60%', height: 12 }} />
                  </div>
                </div>
              ))
            ) : transactions.length === 0 ? (
              <EmptyTransactions />
            ) : (
              groups.map((g) => (
                <React.Fragment key={g.day}>
                  <div className="txn-group-label">{g.day}</div>
                  {g.items.map((t) => <TxnRow key={t.txnId} txn={t} showDay={false} />)}
                </React.Fragment>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}

function Stat({ label, value, className = '' }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      {value === undefined || value === null
        ? <div className="skeleton" style={{ height: 24, width: '70%', marginTop: 6 }} />
        : <div className={`stat-value ${className}`}>{value}</div>}
    </div>
  )
}

const sum = (txns, type) =>
  (txns ?? []).filter((t) => t.txnType === type).reduce((acc, t) => acc + Number(t.amount), 0)
