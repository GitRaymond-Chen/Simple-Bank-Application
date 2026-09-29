import React from 'react'
import { deposit } from '../api/bank'
import AmountForm from '../components/AmountForm'

export default function DepositPage() {
  return <AmountForm mode="deposit" submit={deposit} />
}
