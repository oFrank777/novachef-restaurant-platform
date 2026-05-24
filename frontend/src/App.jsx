import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/common/Toast';
import GlobalErrorBanner from './components/GlobalErrorBanner';
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/Layout/ProtectedRoute';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import MenuPage from './pages/MenuPage';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import PaymentsPage from './pages/PaymentsPage';
import InventoryPage from './pages/InventoryPage';
import DeliveryPage from './pages/DeliveryPage';
import ReportsPage from './pages/ReportsPage';

import './styles/global.css';

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <CartProvider>
            <ToastProvider>
              <GlobalErrorBanner />
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={
                    <ProtectedRoute roles={['admin', 'cajero', 'delivery', 'cliente']}>
                      <DashboardPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/menu" element={
                    <ProtectedRoute roles={['admin', 'cajero', 'cliente']}>
                      <MenuPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/cart" element={
                    <ProtectedRoute roles={['admin', 'cajero', 'cliente']}>
                      <CartPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/orders" element={
                    <ProtectedRoute roles={['admin', 'cajero', 'cliente', 'delivery']}>
                      <OrdersPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/payments" element={
                    <ProtectedRoute roles={['admin', 'cajero']}>
                      <PaymentsPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/inventory" element={
                    <ProtectedRoute roles={['admin']}>
                      <InventoryPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/delivery" element={
                    <ProtectedRoute roles={['admin', 'delivery']}>
                      <DeliveryPage />
                    </ProtectedRoute>
                  } />
                  <Route path="/reports" element={
                    <ProtectedRoute roles={['admin']}>
                      <ReportsPage />
                    </ProtectedRoute>
                  } />
                </Route>
              </Routes>
            </ToastProvider>
          </CartProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
