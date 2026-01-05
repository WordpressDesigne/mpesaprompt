import React, { useState, useEffect } from 'react';

const AdminCommissions = () => {
    const [commissions, setCommissions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCommissions = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/commissions`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setCommissions(data);
            } else {
                console.error('Failed to fetch commissions');
            }
            setLoading(false);
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
                    <table className="w-full text-sm text-left text-neutral-600">
                        <thead className="text-xs text-neutral-800 uppercase bg-neutral-100">
                            <tr>
                                <th scope="col" className="px-6 py-3">ID</th>
                                <th scope="col" className="px-6 py-3">Amount</th>
                                <th scope="col" className="px-6 py-3">Timestamp</th>
                                <th scope="col" className="px-6 py-3">Business ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {commissions.map(commission => (
                                <tr key={commission.id} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-bold text-neutral-900">{commission.id}</td>
                                    <td className="px-6 py-4">${commission.amount.toFixed(2)}</td>
                                    <td className="px-6 py-4">{new Date(commission.timestamp).toLocaleString()}</td>
                                    <td className="px-6 py-4">{commission.business_id}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {commissions.length === 0 && (
                    <p className="text-center p-8 text-neutral-500">No commissions found.</p>
                )}
            </div>
        </div>
    );
};

export default AdminCommissions;
