import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const SignupPage = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        if (location.state && location.state.email) {
            setEmail(location.state.email);
        }
    }, [location.state]);

    const handleSignup = async (e) => {
        e.preventDefault();
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });

        if (response.ok) {
            navigate('/login');
        } else {
            // Handle signup error
            console.error('Signup failed');
            alert('Signup failed. This email may already be in use.');
        }
    };

    return (
        <div className="flex items-center justify-center h-screen">
            <form onSubmit={handleSignup} className="p-8 bg-white rounded shadow-md">
                <h2 className="text-2xl font-bold mb-4">Create Your Business Account</h2>
                {location.state?.email && (
                    <p className="mb-4 text-center text-gray-600">
                        Welcome! Please complete your registration.
                    </p>
                )}
                <div className="mb-4">
                    <label className="block text-gray-700">Business Name</label>
                    <input
                        type="text"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Email</label>
                    <input
                        type="email"
                        className="w-full p-2 border border-gray-300 rounded bg-gray-100"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        readOnly={!!location.state?.email}
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700">Password</label>
                    <input
                        type="password"
                        className="w-full p-2 border border-gray-300 rounded"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
                    Signup
                </button>
            </form>
        </div>
    );
};

export default SignupPage;
