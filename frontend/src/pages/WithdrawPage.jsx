import React from 'react'
import { withdraw } from '../api/bank'
import AmountForm from '../components/AmountForm'

export default function WithdrawPage() {
  return <AmountForm mode="withdraw" submit={withdraw} />
}
