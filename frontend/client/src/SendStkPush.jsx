import React, { useState } from 'react';

const SendStkPush = () => {
    const [phone, setPhone] = useState('');
    const [amount, setAmount] = useState('');
    const [notification, setNotification] = useState({ message: '', type: '' });

    const showNotification = (message, type) => {
        setNotification({ message, type });
        setTimeout(() => setNotification({ message: '', type: '' }), 5000);
    };

    const handleSend = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/stk-push`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ phone_number: phone, amount: Number(amount) }),
        });

        if (response.ok) {
            showNotification('STK push sent successfully!', 'success');
            setPhone('');
            setAmount('');
        } else {
            const data = await response.json();
            showNotification(data.message || 'Failed to send STK push.', 'error');
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
                        />
                    </div>
                    <button type="submit" className="btn-primary w-full">
                        Send Payment Request
                    </button>
                </form>
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
