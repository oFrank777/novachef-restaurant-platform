import axios from 'axios';
import { eventEmitter } from '../utils/eventEmitter';

const client = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

const SAFE_MESSAGES = {
  400: 'La solicitud no es válida. Revisa los datos ingresados.',
  401: 'Sesión expirada o credenciales inválidas.',
  403: 'No tienes permiso para realizar esta acción.',
  404: 'El recurso solicitado no existe.',
  409: 'La operación ya fue procesada o hay un conflicto.',
  422: 'Algunos campos no cumplen las validaciones requeridas.',
  429: 'Demasiadas peticiones. Espera un momento e intenta de nuevo.',
  500: 'Error del servidor. Intenta más tarde.',
};

function mapValidationDetail(detail) {
  if (!Array.isArray(detail)) return SAFE_MESSAGES[422];
  return 'Revisa los campos del formulario e intenta de nuevo.';
}

function resolveErrorMessage(error) {
  const status = error.response?.status;
  const detail = error.response?.data?.detail;

  if (status && SAFE_MESSAGES[status] && status !== 422) {
    if (status === 400 && typeof detail === 'string' && detail.length < 120) {
      return detail;
    }
    if (status === 403 && typeof detail === 'string' && detail.length < 120) {
      return detail;
    }
    return SAFE_MESSAGES[status];
  }
  if (status === 422) {
    if (typeof detail === 'string' && detail.length < 120) return detail;
    return mapValidationDetail(detail);
  }
  if (typeof detail === 'string' && detail.length < 120) return detail;
  return SAFE_MESSAGES[500];
}

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        window.dispatchEvent(new Event('auth:logout'));
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }

      const message = resolveErrorMessage(error);
      if (!error.config?.skipGlobalError) {
        eventEmitter.emit('globalError', message);
      }
      return Promise.reject(new Error(message));
    }

    if (error.request) {
      const msg = 'Error de red. Verifica tu conexión.';
      eventEmitter.emit('globalError', msg);
      return Promise.reject(new Error(msg));
    }

    const fallbackMsg = 'No se pudo completar la operación.';
    eventEmitter.emit('globalError', fallbackMsg);
    return Promise.reject(error);
  }
);

export const api = {
  get: (url, config) => client.get(url, config),
  post: (url, data, config) => client.post(url, data, config),
  put: (url, data, config) => client.put(url, data, config),
  patch: (url, data, config) => client.patch(url, data, config),
  del: (url, config) => client.delete(url, config),
};

export default client;
