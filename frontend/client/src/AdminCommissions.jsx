import React, { useState, useEffect } from 'react';

const AdminCommissions = () => {
    const [commissions, setCommissions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCommissions = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/commissions`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setCommissions(data);
                } else {
                    console.error('Failed to fetch commissions:', response.status, response.statusText);
                    // Optionally, show a user-friendly error message
                }
            } catch (error) {
                console.error('Network error fetching commissions:', error);
                // Optionally, show a user-friendly error message
            } finally {
                setLoading(false);
            }
        };
        fetchCommissions();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">All Commissions</h2>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="table-base"> {/* Apply the new table-base class */}
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Amount</th>
                                <th>Timestamp</th>
                                <th>Business ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {commissions.length > 0 ? (
                                commissions.map(commission => (
                                    <tr key={commission.id}>
                                        <td className="font-bold text-neutral-900">{commission.id}</td>
                                        <td>${commission.amount ? commission.amount.toFixed(2) : '0.00'}</td>
                                        <td>{new Date(commission.timestamp).toLocaleString()}</td>
                                        <td>{commission.business_id}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="text-center p-8 text-neutral-500">No commissions found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminCommissions;
