import { createContext, useContext, useState, useCallback, useRef } from 'react';

const ToastContext = createContext(null);

let toastIdCounter = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const timersRef = useRef({});

  const addToast = useCallback((message, type = 'info', title = '', duration = 5000) => {
    const id = ++toastIdCounter;
    const autoTitle = title || (type === 'success' ? 'Éxito' : type === 'error' ? 'Error' : type === 'warning' ? 'Advertencia' : 'Info');

    setToasts((prev) => [...prev, { id, message, type, title: autoTitle, duration }]);

    timersRef.current[id] = setTimeout(() => {
      setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)));
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
        delete timersRef.current[id];
      }, 300);
    }, duration);

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    if (timersRef.current[id]) {
      clearTimeout(timersRef.current[id]);
      delete timersRef.current[id];
    }
    setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)));
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 300);
  }, []);

  const success = useCallback((msg, title) => addToast(msg, 'success', title), [addToast]);
  const error = useCallback((msg, title) => addToast(msg, 'error', title), [addToast]);
  const warning = useCallback((msg, title) => addToast(msg, 'warning', title), [addToast]);
  const info = useCallback((msg, title) => addToast(msg, 'info', title), [addToast]);

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, warning, info }}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.type} ${toast.exiting ? 'exiting' : ''}`}>
            <span className="toast-icon">
              {toast.type === 'success' && '✓'}
              {toast.type === 'error' && '✕'}
              {toast.type === 'warning' && '⚠'}
              {toast.type === 'info' && 'ℹ'}
            </span>
            <div className="toast-content">
              <div className="toast-title">{toast.title}</div>
              <div className="toast-message">{toast.message}</div>
            </div>
            <button className="toast-close" onClick={() => removeToast(toast.id)}>✕</button>
            <div className="toast-progress" style={{ animationDuration: `${toast.duration}ms` }}></div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export default ToastContext;
