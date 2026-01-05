import React, { useState, useEffect } from 'react';

const Settings = () => {
    const [consumerKey, setConsumerKey] = useState('');
    const [consumerSecret, setConsumerSecret] = useState('');
    const [tillNumber, setTillNumber] = useState('');
    const [paybillNumber, setPaybillNumber] = useState('');
    const [notification, setNotification] = useState({ message: '', type: '' });
    const [loading, setLoading] = useState(true);

    const showNotification = (message, type) => {
        setNotification({ message, type });
        setTimeout(() => setNotification({ message: '', type: '' }), 5000);
    };

    useEffect(() => {
        const fetchSettings = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/settings`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setConsumerKey(data.consumer_key || '');
                    setConsumerSecret(data.consumer_secret || '');
                    setTillNumber(data.till_number || '');
                    setPaybillNumber(data.paybill_number || '');
                } else {
                    console.error('Failed to fetch settings:', response.status, response.statusText);
                    showNotification('Failed to fetch settings.', 'error');
                }
            } catch (error) {
                console.error('Network error fetching settings:', error);
                showNotification('Network error fetching settings.', 'error');
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, []);

    const handleUpdateSettings = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/settings/update`, {
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

            const data = await response.json();
            if (response.ok) {
                showNotification(data.message || 'Settings updated successfully!', 'success');
            } else {
                showNotification(data.message || 'Failed to update settings.', 'error');
            }
        } catch (error) {
            console.error('Network error updating settings:', error);
            showNotification('Network error updating settings.', 'error');
        }
    };

    if (loading) {
        return <div>Loading settings...</div>;
    }

    return (
        <div className="max-w-xl mx-auto">
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">M-Pesa Settings</h2>
             <div className="card-base">
                <form onSubmit={handleUpdateSettings} className="space-y-6">
                    <div>
                        <label htmlFor="consumerKey" className="block text-sm font-medium text-neutral-600 mb-1">Daraja Consumer Key</label>
                        <input
                            id="consumerKey"
                            type="text"
                            className="input-base"
                            value={consumerKey}
                            onChange={(e) => setConsumerKey(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="consumerSecret" className="block text-sm font-medium text-neutral-600 mb-1">Daraja Consumer Secret</label>
                        <input
                            id="consumerSecret"
                            type="password"
                            className="input-base"
                            value={consumerSecret}
                            onChange={(e) => setConsumerSecret(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="tillNumber" className="block text-sm font-medium text-neutral-600 mb-1">Till Number (Optional)</label>
                        <input
                            id="tillNumber"
                            type="text"
                            className="input-base"
                            value={tillNumber}
                            onChange={(e) => setTillNumber(e.target.value)}
                        />
                    </div>
                     <div>
                        <label htmlFor="paybillNumber" className="block text-sm font-medium text-neutral-600 mb-1">Paybill Number (Optional)</label>
                        <input
                            id="paybillNumber"
                            type="text"
                            className="input-base"
                            value={paybillNumber}
                            onChange={(e) => setPaybillNumber(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="btn-primary w-full">
                        Save and Test Settings
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

export default Settings;
