import React, { useState, useEffect } from 'react';

const SendStkPush = () => {
    const [phone, setPhone] = useState('');
    const [amount, setAmount] = useState('');
    const [notification, setNotification] = useState({ message: '', type: '' });
    const [isSending, setIsSending] = useState(false);
    const [stkPushStatus, setStkPushStatus] = useState(''); // 'idle', 'initiated', 'pending', 'success', 'failed'
    const [checkoutRequestID, setCheckoutRequestID] = useState(null);

    // Effect to clean up the polling interval if the component unmounts or checkoutRequestID changes
    useEffect(() => {
        let intervalId;
        if (checkoutRequestID && (stkPushStatus === 'initiated' || stkPushStatus === 'pending')) {
            intervalId = setInterval(() => {
                pollTransactionStatus(checkoutRequestID);
            }, 5000); // Poll every 5 seconds
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [checkoutRequestID, stkPushStatus]);

    const showNotification = (message, type) => {
        setNotification({ message, type });
        setTimeout(() => setNotification({ message: '', type: '' }), 5000);
    };

    const pollTransactionStatus = async (id) => {
        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/transaction-status/${id}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setStkPushStatus(data.status); // 'pending', 'success', 'failed'

                if (data.status === 'success') {
                    showNotification('STK push successful!', 'success');
                    setCheckoutRequestID(null); // Stop polling
                    setIsSending(false);
                } else if (data.status === 'failed') {
                    showNotification('STK push failed. Please try again.', 'error');
                    setCheckoutRequestID(null); // Stop polling
                    setIsSending(false);
                }
            } else {
                // Handle error during polling, maybe the transaction ID became invalid
                const errorData = await response.json();
                console.error("Error polling transaction status:", errorData.message);
                showNotification(errorData.message || 'Failed to get transaction status.', 'error');
                setCheckoutRequestID(null); // Stop polling
                setIsSending(false);
            }
        } catch (error) {
            console.error("Network error while polling:", error);
            showNotification('Network error while checking status.', 'error');
            setCheckoutRequestID(null); // Stop polling
            setIsSending(false);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        setIsSending(true);
        setStkPushStatus('initiated');
        setCheckoutRequestID(null); // Reset for new transaction
        setNotification({ message: '', type: '' }); // Clear previous notification

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/stk-push`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ phone_number: phone, amount: Number(amount) }),
            });

            if (response.ok) {
                const data = await response.json();
                const newCheckoutRequestID = data.checkout_request_id;
                setCheckoutRequestID(newCheckoutRequestID);
                showNotification('STK push initiated. Waiting for confirmation...', 'success');
                // Polling will start via useEffect
            } else {
                const data = await response.json();
                showNotification(data.message || 'Failed to send STK push.', 'error');
                setIsSending(false);
                setStkPushStatus('failed');
            }
        } catch (error) {
            console.error("Network error sending STK push:", error);
            showNotification('Network error. Please check your connection.', 'error');
            setIsSending(false);
            setStkPushStatus('failed');
        }
    };

    return (
        <div className="max-w-xl mx-auto">
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">Send STK Push</h2>
            <div className="card-base">
                <form onSubmit={handleSend} className="space-y-6">
                    <div>
                        <label htmlFor="phone" className="block text-sm font-medium text-neutral-600 mb-1">Customer Phone</label>
                        <input
                            id="phone"
                            type="text"
                            className="input-base"
                            placeholder="e.g. 254712345678"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            required
                            disabled={isSending}
                        />
                    </div>
                    <div>
                        <label htmlFor="amount" className="block text-sm font-medium text-neutral-600 mb-1">Amount</label>
                        <input
                            id="amount"
                            type="number"
                            className="input-base"
                            placeholder="e.g. 100"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            required
                            disabled={isSending}
                        />
                    </div>
                    <button type="submit" className="btn-primary w-full" disabled={isSending}>
                        {isSending ? (stkPushStatus === 'initiated' ? 'Initiating...' : 'Waiting for M-Pesa...') : 'Send Payment Request'}
                    </button>
                </form>
                {stkPushStatus && stkPushStatus !== 'idle' && (stkPushStatus === 'initiated' || stkPushStatus === 'pending') && (
                    <div className="mt-4 p-3 bg-blue-100 text-blue-800 rounded-lg text-center flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {stkPushStatus === 'initiated' ? 'STK Push Initiated. Waiting for M-Pesa response.' : `Transaction Status: ${stkPushStatus}`}
                    </div>
                )}
            </div>
            
            {notification.message && (
                <div className={`fixed bottom-5 right-5 p-4 rounded-lg shadow-lg text-white ${notification.type === 'success' ? 'bg-success-500' : 'bg-error-500'}`}>
                    {notification.message}
                </div>
            )}
        </div>
    );
};

export default SendStkPush;
