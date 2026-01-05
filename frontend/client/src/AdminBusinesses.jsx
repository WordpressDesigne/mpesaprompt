import React, { useState, useEffect } from 'react';

const AdminBusinesses = () => {
    const [businesses, setBusinesses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBusinesses = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/businesses`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setBusinesses(data);
                } else {
                    console.error('Failed to fetch businesses:', response.status, response.statusText);
                    // Optionally, show a user-friendly error message
                }
            } catch (error) {
                console.error('Network error fetching businesses:', error);
                // Optionally, show a user-friendly error message
            } finally {
                setLoading(false);
            }
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
                    <table className="table-base"> {/* Apply the new table-base class */}
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Created At</th>
                                <th>Status</th>
                                {/* Add actions column header if suspension/reactivation is done here */}
                            </tr>
                        </thead>
                        <tbody>
                            {businesses.length > 0 ? (
                                businesses.map(business => (
                                    <tr key={business.id}>
                                        <td className="font-bold text-neutral-900">{business.id}</td>
                                        <td>{business.name}</td>
                                        <td>{business.email}</td>
                                        <td>{new Date(business.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                business.is_active 
                                                    ? 'bg-success-100 text-success-800' 
                                                    : 'bg-error-100 text-error-800'
                                            }`}>
                                                {business.is_active ? 'Active' : 'Suspended'}
                                            </span>
                                        </td>
                                        {/* Actions column can be added here */}
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center p-8 text-neutral-500">No businesses found.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminBusinesses;
