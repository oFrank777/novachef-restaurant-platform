import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Zap, Shield, BarChart3, Layers, Globe, ChevronRight, CheckCircle2, PlayCircle, Star, LogIn } from 'lucide-react';

const IMAGES = [
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1414235077428-338988a9228e?auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1920&q=80'
];

const fadeIn = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, type: 'spring', bounce: 0.2 } }
};

const stagger = {
  visible: { transition: { staggerChildren: 0.15 } }
};

export default function LandingPage() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % IMAGES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', position: 'relative', overflowX: 'hidden' }}>

      { }
      <header className="glass" style={{
        position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 100,
        width: 'calc(100% - 48px)', maxWidth: '1200px', padding: '16px 32px', borderRadius: 'var(--radius-full)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '18px', boxShadow: 'var(--shadow-glow)' }}>N</div>
          <span className="text-h4 text-gradient" style={{ fontWeight: 800 }}>NovaChef</span>
        </div>
        <div style={{ display: 'flex', gap: '16px' }}>
          <Link to="/login" className="btn btn-outline hide-mobile" style={{ border: 'none' }}>Iniciar Sesión</Link>
          <Link to="/register" className="btn btn-gradient">Comenzar</Link>
        </div>
      </header>

      { }
      <section style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden', background: '#000', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>

        { }
        <AnimatePresence mode="popLayout">
          <motion.img
            key={currentIndex}
            src={IMAGES[currentIndex]}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 0.6, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: 'easeInOut' }}
            style={{
              position: 'absolute',
              top: 0, left: 0, width: '100%', height: '100%',
              objectFit: 'cover',
              zIndex: 0
            }}
          />
        </AnimatePresence>

        { }
        <div style={{
          position: 'absolute',
          top: 0, left: 0, width: '100%', height: '100%',
          background: 'radial-gradient(circle at center, rgba(0,0,0,0.4) 0%, var(--bg-primary) 100%)',
          zIndex: 1
        }} />

        { }
        <main style={{ position: 'relative', zIndex: 10, textAlign: 'center', padding: '0 24px', width: '100%', maxWidth: '1000px', margin: '0 auto', marginTop: '60px' }}>
          <motion.div variants={stagger} initial="hidden" animate="visible">
            <motion.div variants={fadeIn} className="badge" style={{ background: 'rgba(139, 92, 246, 0.1)', color: 'var(--accent-purple)', border: '1px solid rgba(139, 92, 246, 0.2)', marginBottom: '32px', padding: '8px 16px', fontSize: '0.85rem', backdropFilter: 'blur(10px)' }}>
              🚀 Presentando NovaChef Empresarial
            </motion.div>

            <motion.h1 variants={fadeIn} style={{ fontSize: 'clamp(3.5rem, 8vw, 6rem)', margin: '0 auto 32px', lineHeight: 1.05, paddingBottom: '10px', color: 'white', fontWeight: 800, letterSpacing: '-0.03em', textShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              Eleva tu experiencia culinaria.
            </motion.h1>

            <motion.p variants={fadeIn} style={{ fontSize: 'clamp(1.2rem, 3vw, 1.5rem)', color: 'rgba(255,255,255,0.8)', maxWidth: '700px', margin: '0 auto 48px', fontWeight: 400, lineHeight: 1.6, textShadow: '0 4px 10px rgba(0,0,0,0.5)' }}>
              El sistema exclusivamente para restaurantes, entregas fluidas e inventario inteligente.
            </motion.p>

            <motion.div variants={fadeIn} style={{ display: 'flex', gap: '24px', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }}>
              <Link to="/register" style={{
                display: 'inline-flex', alignItems: 'center', gap: '12px',
                background: 'white', color: 'black', textDecoration: 'none',
                padding: '20px 48px', borderRadius: '50px', fontWeight: 700, fontSize: '1.25rem',
                boxShadow: '0 20px 40px rgba(0,0,0,0.4)', transition: 'transform 0.3s'
              }} onMouseOver={e => e.currentTarget.style.transform = 'scale(1.05)'} onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}>
                Comenzar <ArrowRight size={24} />
              </Link>
            </motion.div>

            <motion.div variants={fadeIn} style={{ marginTop: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', color: 'rgba(255,255,255,0.8)', fontSize: '0.95rem', textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
              <div style={{ display: 'flex' }}>
                {[1, 2, 3, 4, 5].map(i => <Star key={i} size={16} fill="var(--accent-purple)" color="var(--accent-purple)" />)}
              </div>
              <span>Confiado por más de 5,000 restaurantes top en el mundo</span>
            </motion.div>
          </motion.div>

          { }
          <div style={{ position: 'absolute', bottom: 40, left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: '12px', zIndex: 10 }}>
            {IMAGES.map((_, i) => (
              <div key={i} onClick={() => setCurrentIndex(i)} style={{ width: currentIndex === i ? 32 : 8, height: 8, borderRadius: 4, background: 'white', opacity: currentIndex === i ? 1 : 0.3, cursor: 'pointer', transition: 'all 0.3s ease' }} />
            ))}
          </div>
        </main>
      </section>

      { }
      <main style={{ paddingBottom: '120px', paddingInline: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', zIndex: 10, background: 'var(--bg-primary)' }}>

        { }
        <div className="bg-glow-effect" style={{ filter: 'blur(120px)', opacity: 0.6 }} />
        <div className="bg-glow-effect-right" style={{ filter: 'blur(120px)', opacity: 0.6 }} />

        { }
        <motion.div
          initial={{ opacity: 0, y: 150 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 1.2, type: 'spring', bounce: 0.1 }}
          className="glass-panel"
          style={{
            width: '100%', maxWidth: '1200px', height: '600px', margin: '80px auto 0',
            borderRadius: 'var(--radius-xl)', position: 'relative', overflow: 'hidden',
            boxShadow: 'var(--shadow-lg), 0 0 100px rgba(59, 130, 246, 0.15)',
            borderTop: '1px solid rgba(255,255,255,0.2)', padding: '2px'
          }}
        >
          <div style={{ width: '100%', height: '100%', borderRadius: 'calc(var(--radius-xl) - 2px)', background: 'var(--bg-primary)', display: 'flex', overflow: 'hidden' }}>
            { }
            <div style={{ width: '240px', background: 'var(--bg-secondary)', borderRight: '1px solid var(--border-light)', padding: '24px', display: 'none', '@media (minWidth: 768px)': { display: 'block' } }}>
              <div style={{ display: 'flex', gap: '12px', marginBottom: '40px' }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--accent-blue)' }} />
                <div style={{ width: 120, height: 32, borderRadius: 8, background: 'var(--bg-tertiary)' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {[1, 2, 3, 4, 5, 6].map(i => <div key={i} style={{ width: '100%', height: 32, borderRadius: 8, background: i === 1 ? 'var(--bg-glow)' : 'var(--bg-tertiary)', opacity: i === 1 ? 1 : 0.6 }} />)}
              </div>
            </div>
            { }
            <div style={{ flex: 1, padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ width: 200, height: 40, borderRadius: 8, background: 'var(--bg-tertiary)' }} />
                <div style={{ width: 120, height: 40, borderRadius: 20, background: 'var(--bg-glow)' }} />
              </div>
              <div style={{ display: 'flex', gap: '24px' }}>
                {[1, 2, 3].map(i => <div key={i} style={{ flex: 1, height: 120, borderRadius: 16, background: 'var(--bg-secondary)', border: '1px solid var(--border-light)' }} />)}
              </div>
              <div style={{ flex: 1, display: 'flex', gap: '24px' }}>
                <div style={{ flex: 2, borderRadius: 16, background: 'var(--bg-secondary)', border: '1px solid var(--border-light)' }} />
                <div style={{ flex: 1, borderRadius: 16, background: 'var(--bg-secondary)', border: '1px solid var(--border-light)' }} />
              </div>
            </div>
          </div>
        </motion.div>

        { }
        <div style={{ width: '100%', maxWidth: '1200px', margin: '160px auto 0' }}>
          <div style={{ textAlign: 'center', marginBottom: '64px' }}>
            <h2 className="text-h2" style={{ marginBottom: '16px' }}>Todo lo que necesitas para escalar</h2>
            <p className="text-muted" style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>NovaChef provee un conjunto completo de herramientas para gestionar tu imperio de restaurantes.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '32px', textAlign: 'left' }}>
            {[
              { icon: Zap, title: 'Motor de Sincronización', desc: 'Los pedidos fluyen instantáneamente desde el POS hacia las pantallas de cocina.' },
              { icon: Layers, title: 'Arquitectura Modular', desc: 'Añade módulos de inventario, envíos o lealtad fácilmente a medida que creces.' },
              { icon: BarChart3, title: 'Analítica Predictiva', desc: 'Predicciones basadas en IA para prever demanda y optimizar suministros.' },
              { icon: Globe, title: 'Omnicanal Listo', desc: 'Gestiona la tienda, las apps de envío y los pedidos web desde una sola pantalla.' },
              { icon: Shield, title: 'Seguridad Bancaria', desc: 'Encriptación de extremo a extremo y cumplimiento de normativas de fábrica.' },
              { icon: CheckCircle2, title: 'SLA de 99.99%', desc: 'Infraestructura sólida como una roca que nunca se cae en hora punta.' }
            ].map((feature, i) => (
              <motion.div key={i} className="card" whileHover={{ y: -8, borderColor: 'var(--accent-blue)' }} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: i * 0.1 }}>
                <div style={{ width: 64, height: 64, borderRadius: 20, background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1))', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px', color: 'var(--accent-blue)' }}>
                  <feature.icon size={32} />
                </div>
                <h3 className="text-h3" style={{ marginBottom: '12px', fontSize: '1.4rem' }}>{feature.title}</h3>
                <p className="text-muted" style={{ fontSize: '1.05rem', lineHeight: 1.6 }}>{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>

        { }
        <motion.div initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ duration: 0.8 }}
          style={{ width: '100%', maxWidth: '1200px', margin: '160px auto 0', padding: '80px 40px', borderRadius: 'var(--radius-xl)', background: 'linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%)', border: '1px solid var(--border-light)', position: 'relative', overflow: 'hidden' }}
        >
          <div style={{ position: 'absolute', top: '-50%', left: '-10%', width: '120%', height: '200%', background: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.08) 0%, transparent 60%)', pointerEvents: 'none' }} />
          <div style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
            <h2 className="text-h1 text-gradient" style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)', marginBottom: '24px' }}>¿Listo para transformar tu negocio?</h2>
            <p className="text-muted" style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto 40px' }}>Únete a miles de restaurantes que han mejorado sus operaciones con NovaChef.</p>
            <Link to="/register" className="btn btn-gradient" style={{ padding: '20px 40px', fontSize: '1.25rem', borderRadius: 'var(--radius-full)' }}>
              Inicia tu prueba gratis de 14 días
            </Link>
          </div>
        </motion.div>

      </main>

      { }
      <footer style={{ borderTop: '1px solid var(--border-light)', padding: '64px 24px', background: 'var(--bg-secondary)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexWrap: 'wrap', gap: '64px', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--text-primary)', color: 'var(--bg-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>N</div>
              <span className="text-h4" style={{ fontWeight: 800 }}>NovaChef</span>
            </div>
            <p className="text-muted" style={{ maxWidth: '300px' }}>El sistema operativo definitivo para operaciones de restaurantes de alto rendimiento.</p>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            <div>
              <p className="text-muted" style={{ maxWidth: '300px' }}>NovaChef Inc.<br />Av. Las Flores, CC, Arequipa<br />olopeza@unsa.edu.pe</p>
            </div>
          </div>
        </div>
        <div style={{ maxWidth: '1200px', margin: '64px auto 0', paddingTop: '32px', borderTop: '1px solid var(--border-light)', color: 'var(--text-muted)', fontSize: '0.9rem', textAlign: 'center' }}>
          © 2026 NovaChef Inc. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  );
}
