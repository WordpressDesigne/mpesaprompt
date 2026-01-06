import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AdminLoginPage from './AdminLoginPage';
import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import Dashboard from './Dashboard';
import SendStkPush from './SendStkPush';
import Customers from './Customers';
import Settings from './Settings';
import AdminBusinesses from './AdminBusinesses';
import AdminTransactions from './AdminTransactions';

const PrivateRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    return token ? children : <Navigate to="/login" />;
};

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/admin/login" element={<AdminLoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route
                    path="/dashboard"
                    element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    }
                >
                    {/* Business Routes */}
                    <Route path="stk-push" element={<SendStkPush />} />
                    <Route path="customers" element={<Customers />} />
                    <Route path="settings" element={<Settings />} />

                    {/* Admin Routes */}
                    <Route path="businesses" element={<AdminBusinesses />} />
                    <Route path="transactions" element={<AdminTransactions />} />
                </Route>
                <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
        </Router>
    );
}

export default App;