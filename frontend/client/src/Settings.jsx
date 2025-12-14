import React, { useState, useEffect } from 'react';

const Settings = () => {
    const [consumerKey, setConsumerKey] = useState('');
    const [consumerSecret, setConsumerSecret] = useState('');
    const [tillNumber, setTillNumber] = useState('');
    const [paybillNumber, setPaybillNumber] = useState('');

    useEffect(() => {
        const fetchSettings = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch('/settings', { // Assuming a GET /settings route exists
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setConsumerKey(data.consumer_key || '');
                setConsumerSecret(data.consumer_secret || '');
                setTillNumber(data.till_number || '');
                setPaybillNumber(data.paybill_number || '');
            } else {
                console.error('Failed to fetch settings');
            }
        };
        fetchSettings();
    }, []);

    const handleUpdateSettings = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const response = await fetch('/settings/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                consumer_key: consumerKey,
                consumer_secret: consumerSecret,
                till_number: tillNumber,
                paybill_number: paybillNumber
            }),
        });

        if (response.ok) {
            console.log('Settings updated successfully');
        } else {
            console.error('Failed to update settings');
        }
    };

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Settings</h2>
            <form onSubmit={handleUpdateSettings} className="p-8 bg-white rounded shadow-md">
                <div className="mb-4">
                    <label className="block text-gray-700">Daraja Consumer Key</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={consumerKey}
                        onChange={(e) => setConsumerKey(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Daraja Consumer Secret</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={consumerSecret}
                        onChange={(e) => setConsumerSecret(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Till Number</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={tillNumber}
                        onChange={(e) => setTillNumber(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Paybill Number</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={paybillNumber}
                        onChange={(e) => setPaybillNumber(e.target.value)}
                    />
                </div>
                <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
                    Update Settings
                </button>
            </form>
        </div>
    );
};

export default Settings;
