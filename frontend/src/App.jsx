import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import CreateAccountPage from './pages/CreateAccountPage'
import AccountDetailsPage from './pages/AccountDetailsPage'
import DepositPage from './pages/DepositPage'
import WithdrawPage from './pages/WithdrawPage'
import TransactionsPage from './pages/TransactionsPage'

// Shared base styles applied to every page
const globalStyle = {
  fontFamily: "'Segoe UI', Arial, sans-serif",
  background: '#f4f6fb',
  minHeight: '100vh',
  margin: 0,
  padding: 0,
}

export default function App() {
  return (
    <div style={globalStyle}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create-account" element={<CreateAccountPage />} />
          <Route path="/accounts/:accountId" element={<AccountDetailsPage />} />
          <Route path="/accounts/:accountId/deposit" element={<DepositPage />} />
          <Route path="/accounts/:accountId/withdraw" element={<WithdrawPage />} />
          <Route path="/accounts/:accountId/transactions" element={<TransactionsPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}
