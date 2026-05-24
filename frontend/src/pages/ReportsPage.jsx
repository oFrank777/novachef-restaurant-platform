import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, PackageSearch, AlertTriangle, Download, FileText } from 'lucide-react';
import { api } from '../api/client';
import { eventEmitter } from '../utils/eventEmitter';

function exportReportCSV(salesReport, inventoryReport, popularReport) {
  let csv = 'REPORTE DE VENTAS\n';
  csv += `Total Pedidos,${salesReport?.total_orders || 0}\n`;
  csv += `Ingresos Totales,$${(salesReport?.total_revenue || 0).toFixed(2)}\n\n`;
  csv += 'DESGLOSE POR ESTADO\n';
  csv += 'Estado,Cantidad,Ingresos\n';
  (salesReport?.by_status || []).forEach(s => {
    csv += `${s.status},${s.count},$${(s.revenue || 0).toFixed(2)}\n`;
  });
  csv += `\nINVENTARIO\n`;
  csv += `Items Rastreados,${inventoryReport?.total_items_tracked || 0}\n`;
  csv += `Stock Total,${inventoryReport?.total_stock || 0}\n`;
  csv += `Alertas Bajo Stock,${inventoryReport?.low_stock_count || 0}\n\n`;
  csv += 'PRODUCTOS POPULARES\n';
  csv += 'ID Producto,Total Ordenado,Pedidos,Ingresos\n';
  (popularReport?.popular_items || []).forEach(p => {
    csv += `#${p.menu_item_id},${p.total_ordered},${p.order_count},$${(p.total_revenue || 0).toFixed(2)}\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `reporte_novachef_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const [salesReport, setSalesReport] = useState(null);
  const [inventoryReport, setInventoryReport] = useState(null);
  const [popularReport, setPopularReport] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const [salesRes, invRes, popRes] = await Promise.all([
        api.get('/reports/sales'),
        api.get('/reports/inventory'),
        api.get('/reports/popular')
      ]);
      setSalesReport(salesRes.data);
      setInventoryReport(invRes.data);
      setPopularReport(popRes.data);
    } catch (err) {
      console.error('Error cargando reportes', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const handleExport = () => {
    exportReportCSV(salesReport, inventoryReport, popularReport);
    eventEmitter.emit('globalError', 'Reporte exportado correctamente');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 className="text-h2" style={{ marginBottom: '4px' }}>Reportes y Analíticas</h1>
          <p className="text-muted" style={{ fontSize: '0.95rem' }}>Métricas en tiempo real desde tu base de datos.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={fetchReports} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={16} /> Actualizar
          </button>
          <button className="btn btn-gradient" onClick={handleExport} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Download size={16} /> Exportar CSV
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando reportes...</div>
      ) : (
        <>
          {}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="card glass-panel" style={{ padding: '24px' }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: '#3b82f615', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3b82f6', marginBottom: '16px' }}>
                <TrendingUp size={24} />
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Ingresos Totales</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '4px' }}>${(salesReport?.total_revenue || 0).toFixed(2)}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Total de pedidos: {salesReport?.total_orders || 0}</div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card glass-panel" style={{ padding: '24px' }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: '#8b5cf615', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8b5cf6', marginBottom: '16px' }}>
                <PackageSearch size={24} />
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Inventario</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '4px' }}>{inventoryReport?.total_items_tracked || 0} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>productos</span></div>
              <div style={{ fontSize: '0.85rem', color: inventoryReport?.low_stock_count > 0 ? '#ef4444' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                {inventoryReport?.low_stock_count > 0 && <AlertTriangle size={14} />}
                Alertas: {inventoryReport?.low_stock_count || 0}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card glass-panel" style={{ padding: '24px' }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: '#10b98115', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981', marginBottom: '16px' }}>
                <BarChart3 size={24} />
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>Productos Populares</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '4px' }}>{popularReport?.popular_items?.length || 0}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Basado en volumen de órdenes</div>
            </motion.div>
          </div>

          {}
          {salesReport?.by_status && salesReport.by_status.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px' }}>Desglose por Estado</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estado</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Cantidad</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {salesReport.by_status.map(s => (
                      <tr key={s.status} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td style={{ padding: '10px 12px', fontWeight: 600, fontSize: '0.9rem' }}>{s.status}</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right', fontSize: '0.9rem' }}>{s.count}</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 700, fontSize: '0.9rem' }}>${(s.revenue || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {}
          {popularReport?.popular_items && popularReport.popular_items.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px' }}>Productos Más Vendidos</h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-light)' }}>
                      <th style={{ padding: '8px 12px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Producto</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Vendido</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pedidos</th>
                      <th style={{ padding: '8px 12px', textAlign: 'right', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Ingresos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {popularReport.popular_items.map((item, i) => (
                      <tr key={item.menu_item_id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                        <td style={{ padding: '10px 12px', fontWeight: 600, fontSize: '0.9rem' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 24, height: 24, borderRadius: '50%', background: i < 3 ? '#f59e0b20' : 'var(--bg-tertiary)', color: i < 3 ? '#f59e0b' : 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700, marginRight: '10px' }}>
                            {i + 1}
                          </span>
                          Producto #{item.menu_item_id}
                        </td>
                        <td style={{ padding: '10px 12px', textAlign: 'right', fontSize: '0.9rem' }}>{item.total_ordered}</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right', fontSize: '0.9rem' }}>{item.order_count}</td>
                        <td style={{ padding: '10px 12px', textAlign: 'right', fontWeight: 700, fontSize: '0.9rem' }}>${(item.total_revenue || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}
