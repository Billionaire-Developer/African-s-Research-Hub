// Payment.jsx
import React from 'react';
import './Payment.css';

const Payment = () => {
  // Static data (simulate fetch from backend)
  const invoice = {
    submissionId: 'AB12345',
    amountUSD: '1.99',
    amountMWK: '2500',
    dueDate: '2025-07-15',
  };

  const handlePayment = (method) => {
    alert(`Redirecting to ${method} payment gateway...`);
    // Simulate redirect to confirmation
    window.location.href = '/payment-success';
  };

  return (
    <div className="payment-container">
      <h2>Invoice Details</h2>
      <div className="invoice-box">
        <p><strong>Submission ID:</strong> {invoice.submissionId}</p>
        <p><strong>Amount:</strong> ${invoice.amountUSD} / MWK {invoice.amountMWK}</p>
        <p><strong>Due Date:</strong> {invoice.dueDate}</p>
      </div>

      <h3>Select Payment Method</h3>
      <div className="payment-options">
        <button onClick={() => handlePayment('PayPal')}>PayPal</button>
        <button onClick={() => handlePayment('Card/Stripe')}>Card (Stripe)</button>
        <button onClick={() => handlePayment('Airtel')}>Airtel</button>
        <button onClick={() => handlePayment('MTN')}>MTN</button>
        <button onClick={() => handlePayment('Bank')}>Bank Transfer</button>
        <button onClick={() => handlePayment('Flutterwave/Paystack')}>Flutterwave / Paystack</button>
      </div>
    </div>
  );
};

export default Payment;