import React, { useState, useEffect } from 'react';

const AdminBusinesses = () => {
    const [businesses, setBusinesses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBusinesses = async () => {
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/businesses`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setBusinesses(data);
            } else {
                console.error('Failed to fetch businesses');
            }
            setLoading(false);
        };
        fetchBusinesses();
    }, []);
    
    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-neutral-800 mb-6">Manage Businesses</h2>
            <div className="card-base overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-neutral-600">
                        <thead className="text-xs text-neutral-800 uppercase bg-neutral-100">
                            <tr>
                                <th scope="col" className="px-6 py-3">ID</th>
                                <th scope="col" className="px-6 py-3">Name</th>
                                <th scope="col" className="px-6 py-3">Email</th>
                                <th scope="col" className="px-6 py-3">Created At</th>
                                <th scope="col" className="px-6 py-3">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {businesses.map(business => (
                                <tr key={business.id} className="bg-white border-b hover:bg-neutral-50">
                                    <td className="px-6 py-4 font-bold text-neutral-900">{business.id}</td>
                                    <td className="px-6 py-4">{business.name}</td>
                                    <td className="px-6 py-4">{business.email}</td>
                                    <td className="px-6 py-4">{new Date(business.created_at).toLocaleDateString()}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            business.is_active 
                                                ? 'bg-green-100 text-green-800' 
                                                : 'bg-red-100 text-red-800'
                                        }`}>
                                            {business.is_active ? 'Active' : 'Suspended'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {businesses.length === 0 && (
                    <p className="text-center p-8 text-neutral-500">No businesses found.</p>
                )}
            </div>
        </div>
    );
};

export default AdminBusinesses;
