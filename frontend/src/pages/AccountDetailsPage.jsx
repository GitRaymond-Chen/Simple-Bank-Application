import React, { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { getAccount, getTransactions, getUser } from '../api/bank'
import {
  Alert, BackLink, EmptyTransactions, Icon, Toast, TxnRow, capitalize, errorMessage,
  formatAccountNo, formatMoney, rememberAccount, withRunningBalance,
} from '../components/ui'

export default function AccountDetailsPage() {
  const { accountId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [account, setAccount] = useState(null)
  const [user, setUser] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [error, setError] = useState(null)
  const flash = location.state?.flash

  useEffect(() => {
    setAccount(null)
    setError(null)
    Promise.all([getAccount(accountId), getTransactions(accountId)])
      .then(async ([acc, txns]) => {
        const owner = await getUser(acc.userId)
        setAccount(acc)
        setUser(owner)
        setTransactions(withRunningBalance(txns, acc.balance))
        rememberAccount({ id: acc.accountId, name: owner.name, type: acc.accountType })
      })
      .catch((err) => setError(errorMessage(err, 'Account not found')))
  }, [accountId])

  if (error) {
    return (
      <div className="narrow fade-in">
        <BackLink to="/">Home</BackLink>
        <div className="card">
          <Alert>{error}</Alert>
          <button className="btn btn-secondary btn-block" onClick={() => navigate('/')}>Back to home</button>
        </div>
      </div>
    )
  }

  if (!account) return <DashboardSkeleton />

  const [dollars, cents] = formatMoney(account.balance).split('.')
  const recent = transactions.slice(0, 5)

  return (
    <div className="medium fade-in">
      <BackLink to="/">Home</BackLink>

      <div className="balance-card">
        <div className="balance-top">
          <span className="pill">{capitalize(account.accountType)}</span>
          <span className="acct-no">{formatAccountNo(account.accountId)}</span>
        </div>
        <div className="balance-label">Available balance</div>
        <div className="balance-amount">
          {dollars}<span className="cents">.{cents}</span>
        </div>
        <div className="balance-owner">Account holder · <strong>{user?.name}</strong></div>
      </div>

      <div className="actions">
        <Link className="action" to={`/accounts/${accountId}/deposit`}>
          <span className="action-icon in"><Icon.ArrowDown /></span> Deposit
        </Link>
        <Link className="action" to={`/accounts/${accountId}/withdraw`}>
          <span className="action-icon out"><Icon.ArrowUp /></span> Withdraw
        </Link>
        <Link className="action" to={`/accounts/${accountId}/transactions`}>
          <span className="action-icon neutral"><Icon.List /></span> History
        </Link>
      </div>

      <div className="section-head">
        <h2>Recent activity</h2>
        {transactions.length > 0 && (
          <Link className="link" to={`/accounts/${accountId}/transactions`}>View all</Link>
        )}
      </div>

      <div className="txn-list">
        {recent.length === 0 ? <EmptyTransactions /> : recent.map((t) => <TxnRow key={t.txnId} txn={t} />)}
      </div>

      <Toast key={location.key}>{flash}</Toast>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="medium" aria-busy="true" aria-label="Loading account">
      <div className="skeleton" style={{ width: 70, height: 18, marginBottom: 20 }} />
      <div className="skeleton" style={{ height: 228, borderRadius: 22 }} />
      <div className="actions">
        {[0, 1, 2].map((i) => <div key={i} className="skeleton" style={{ height: 92, borderRadius: 14 }} />)}
      </div>
      <div className="skeleton" style={{ height: 200, marginTop: 44, borderRadius: 16 }} />
    </div>
  )
}
