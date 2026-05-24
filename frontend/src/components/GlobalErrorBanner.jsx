import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { eventEmitter } from '../utils/eventEmitter';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

function getToastConfig(message) {
  if (message.startsWith('✅') || message.toLowerCase().includes('exitosamente') || message.toLowerCase().includes('correctamente') || message.toLowerCase().includes('actualizado')) {
    return { type: 'success', icon: CheckCircle, bg: 'rgba(16, 185, 129, 0.95)', title: 'Operación Exitosa', msg: message.replace('✅ ', '') };
  }
  if (message.toLowerCase().includes('error') || message.toLowerCase().includes('falló')) {
    return { type: 'error', icon: AlertCircle, bg: 'rgba(239, 68, 68, 0.95)', title: 'Error', msg: message };
  }
  if (message.toLowerCase().includes('advertencia') || message.toLowerCase().includes('atención')) {
    return { type: 'warning', icon: AlertTriangle, bg: 'rgba(245, 158, 11, 0.95)', title: 'Advertencia', msg: message };
  }
  return { type: 'info', icon: Info, bg: 'rgba(59, 130, 246, 0.95)', title: 'Información', msg: message };
}

export default function GlobalErrorBanner() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleMsg = (message) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev.slice(-4), { id, message }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4500);
    };
    eventEmitter.on('globalError', handleMsg);
    return () => eventEmitter.off('globalError', handleMsg);
  }, []);

  const dismiss = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  return (
    <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '380px', pointerEvents: 'none' }}>
      <AnimatePresence>
        {toasts.map((toast) => {
          const config = getToastConfig(toast.message);
          const Icon = config.icon;
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 60, scale: 0.92 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 60, scale: 0.92, transition: { duration: 0.2 } }}
              style={{
                background: config.bg,
                backdropFilter: 'blur(12px)',
                color: 'white',
                padding: '14px 16px',
                borderRadius: '12px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                pointerEvents: 'auto'
              }}
            >
              <Icon size={20} style={{ flexShrink: 0, marginTop: '1px' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: '0.88rem', marginBottom: '2px' }}>{config.title}</div>
                <div style={{ fontSize: '0.82rem', lineHeight: 1.4, opacity: 0.92 }}>{config.msg}</div>
              </div>
              <button onClick={() => dismiss(toast.id)}
                style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.7)', cursor: 'pointer', padding: '2px', flexShrink: 0 }}>
                <X size={16} />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
