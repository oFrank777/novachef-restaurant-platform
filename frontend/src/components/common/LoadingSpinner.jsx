export default function LoadingSpinner({ size = 40, text = '' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem', gap: '1rem' }}>
      <div
        style={{
          width: size,
          height: size,
          border: '3px solid rgba(255,255,255,0.1)',
          borderTopColor: '#ff6b35',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      {text && <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>{text}</p>}
    </div>
  );
}
