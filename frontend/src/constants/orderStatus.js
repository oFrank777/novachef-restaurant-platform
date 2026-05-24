export const STATUS_FLOW = ['PENDIENTE', 'PREPARANDO', 'LISTO', 'RECOGIDO', 'ENVIADO', 'ENTREGADO'];

export const STATUS_LABELS = {
  PENDIENTE: 'Pendiente',
  PREPARANDO: 'En Preparación',
  LISTO: 'Listo',
  RECOGIDO: 'Recogido',
  ENVIADO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

export const STATUS_COLORS = {
  PENDIENTE: '#f59e0b',
  PREPARANDO: '#8b5cf6',
  LISTO: '#06b6d4',
  RECOGIDO: '#3b82f6',
  ENVIADO: '#6366f1',
  ENTREGADO: '#10b981',
  CANCELADO: '#ef4444',
};

export function isPickupOrder(order) {
  const addr = order?.delivery_address?.trim().toLowerCase();
  return !addr || addr === 'recojo en local' || addr === 'recogida en local';
}

export function getNextStatuses(order, role) {
  const isPickup = isPickupOrder(order);

  if (order.status === 'PENDIENTE') {
    return role === 'admin' || role === 'cajero' ? ['PREPARANDO', 'CANCELADO'] : [];
  }
  if (order.status === 'PREPARANDO') {
    return role === 'admin' || role === 'cajero' ? ['LISTO', 'CANCELADO'] : [];
  }
  if (order.status === 'LISTO') {
    if (isPickup) {
      return role === 'admin' || role === 'cajero' ? ['ENTREGADO', 'CANCELADO'] : [];
    }
    return role === 'admin' || role === 'delivery' ? ['RECOGIDO'] : [];
  }
  if (order.status === 'RECOGIDO') {
    return role === 'admin' || role === 'delivery' ? ['ENVIADO'] : [];
  }
  if (order.status === 'ENVIADO') {
    return role === 'admin' || role === 'delivery' ? ['ENTREGADO'] : [];
  }
  return [];
}
