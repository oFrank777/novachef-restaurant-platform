const STATUS_CONFIG = {
  PENDIENTE: { color: 'var(--warning)', label: 'Pendiente' },
  PREPARANDO: { color: 'var(--info)', label: 'Preparando' },
  ENVIADO: { color: 'var(--accent-primary)', label: 'Shipped' },
  ENTREGADO: { color: 'var(--success)', label: 'Delivered' },
  CANCELADO: { color: 'var(--error)', label: 'Cancelado' },
  ASIGNADO: { color: 'var(--info)', label: 'Assigned' },
  RECOGIDO: { color: 'var(--accent-primary)', label: 'Picked Up' },
  EN_TRANSITO: { color: 'var(--warning)', label: 'In Transit' },
  COMPLETED: { color: 'var(--success)', label: 'Completado' },
  FAILED: { color: 'var(--error)', label: 'Failed' },
};

export default function EstadoBadge({ status }) {
  const config = STATUS_CONFIG[status] || { color: 'var(--text-muted)', label: status };
  return (
    <span
      className="status-badge"
      style={{
        backgroundColor: `${config.color}20`,
        color: config.color,
        border: `1px solid ${config.color}40`,
      }}
    >
      {config.label}
    </span>
  );
}
