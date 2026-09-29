import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/ui'
import HomePage from './pages/HomePage'
import CreateAccountPage from './pages/CreateAccountPage'
import AccountDetailsPage from './pages/AccountDetailsPage'
import DepositPage from './pages/DepositPage'
import WithdrawPage from './pages/WithdrawPage'
import TransactionsPage from './pages/TransactionsPage'
import './styles.css'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
          <Route path="/accounts/:accountId" element={<AccountDetailsPage />} />
          <Route path="/accounts/:accountId/deposit" element={<DepositPage />} />
          <Route path="/accounts/:accountId/withdraw" element={<WithdrawPage />} />
          <Route path="/accounts/:accountId/transactions" element={<TransactionsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
