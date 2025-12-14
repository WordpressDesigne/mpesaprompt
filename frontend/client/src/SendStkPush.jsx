import React, { useState } from 'react';

const SendStkPush = () => {
    const [phone, setPhone] = useState('');
    const [amount, setAmount] = useState('');

    const handleSend = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/stk-push`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ phone_number: phone, amount }),
        });

        if (response.ok) {
            // Handle successful STK push
            console.log('STK push sent successfully');
        } else {
            // Handle error
            console.error('Failed to send STK push');
        }
    };

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Send STK Push</h2>
            <form onSubmit={handleSend} className="p-8 bg-white rounded shadow-md">
                <div className="mb-4">
                    <label className="block text-gray-700">Phone Number</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Amount</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                    />
                </div>
                <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
                    Send
                </button>
            </form>
        </div>
    );
};

export default SendStkPush;
