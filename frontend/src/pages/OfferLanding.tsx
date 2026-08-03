import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, CheckCircle, Info, Clock, ArrowRight } from 'lucide-react';
import { Layout } from '../components/layout/Layout';
import { apiClient } from '../lib/api-client';
import { formatCurrency, formatDateTime } from '../lib/utils';
import type { PreapprovedOffer } from '../types/api';

export function OfferLanding() {
  const navigate = useNavigate();
  const [offer, setOffer] = useState<PreapprovedOffer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOffer() {
      try {
        const data = await apiClient.getOffers();
        if (data.offers && data.offers.length > 0) {
          setOffer(data.offers[0]);
        } else {
          setError('No hay ofertas disponibles');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar la oferta');
      } finally {
        setLoading(false);
      }
    }
    loadOffer();
  }, []);

  if (loading) {
    return (
      <Layout title="Préstamos" showLogo showBottomNav>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#0066CC] mx-auto mb-4"></div>
            <p className="text-[#666666]">Cargando oferta...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !offer) {
    return (
      <Layout title="Préstamos" showLogo showBottomNav>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error || 'No se encontró la oferta'}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-[#0066CC] text-white rounded-lg font-semibold"
            >
              Reintentar
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col relative">
        {/* Top Bar */}
        <div className="flex-shrink-0 h-14 bg-[#0066CC] flex items-center justify-between px-4">
          <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center">
            <span className="text-[#0066CC] text-sm font-bold">RV</span>
          </div>
          <div className="text-white text-base font-semibold">Préstamos</div>
          <button className="w-8 h-8 flex items-center justify-center text-white" aria-label="Notificaciones">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          {/* Hero Section */}
          <div className="bg-gradient-to-br from-[#0066CC] to-[#004C99] rounded-xl p-6 mb-5 text-white">
            <div className="inline-block bg-white bg-opacity-20 px-3 py-1.5 rounded-full text-xs font-semibold mb-3">
              OFERTA PRECONCEDIDA
            </div>
            <h1 className="text-2xl font-bold mb-2 leading-tight">Tu préstamo está listo</h1>
            <p className="text-sm opacity-90 mb-5">
              Hemos analizado tu perfil y tienes una oferta personalizada disponible
            </p>
            
            <div className="flex items-baseline mb-4">
              <span className="text-[40px] font-bold mr-2">{formatCurrency(offer.max_amount)}</span>
              <span className="text-sm opacity-90">disponibles</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white bg-opacity-15 p-3 rounded-lg">
                <div className="text-[11px] opacity-80 mb-1 uppercase tracking-wider">Plazo máximo</div>
                <div className="text-base font-semibold">{offer.max_term_months} meses</div>
              </div>
              <div className="bg-white bg-opacity-15 p-3 rounded-lg">
                <div className="text-[11px] opacity-80 mb-1 uppercase tracking-wider">TIN desde</div>
                <div className="text-base font-semibold">{offer.indicative_tin.toFixed(2)}%</div>
              </div>
            </div>
          </div>

          {/* Expiry Notice */}
          <div className="bg-[#FFF4E6] border border-[#FFE0B2] rounded-lg p-3 flex items-start mb-4">
            <Clock size={20} className="text-[#FFA500] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#666666] leading-relaxed">
              Esta oferta es válida hasta el{' '}
              <span className="font-semibold text-[#1A1A1A]">
                {formatDateTime(offer.validity_ends_at)}
              </span>
            </div>
          </div>

          {/* Features Card */}
          <div className="bg-white rounded-xl p-5 mb-4 border border-gray-300">
            <div className="flex items-center mb-3">
              <div className="w-10 h-10 bg-[#E6F2FF] rounded-lg flex items-center justify-center mr-3">
                <Sparkles size={20} className="text-[#0066CC]" />
              </div>
              <h2 className="text-base font-semibold text-[#1A1A1A]">Ventajas de tu préstamo</h2>
            </div>
            <ul className="space-y-3 mt-3">
              <li className="flex items-start">
                <CheckCircle size={20} className="text-[#00A86B] mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-[#1A1A1A] leading-relaxed">
                  Sin comisiones de apertura ni estudio
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle size={20} className="text-[#00A86B] mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-[#1A1A1A] leading-relaxed">
                  Amortización anticipada sin penalización
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle size={20} className="text-[#00A86B] mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-[#1A1A1A] leading-relaxed">
                  Dinero disponible en tu cuenta en 24 horas
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle size={20} className="text-[#00A86B] mr-3 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-[#1A1A1A] leading-relaxed">
                  Gestión 100% digital desde la app
                </span>
              </li>
            </ul>
          </div>

          {/* How it Works Card */}
          <div className="bg-white rounded-xl p-5 mb-4 border border-gray-300">
            <div className="flex items-center mb-3">
              <div className="w-10 h-10 bg-[#E6F2FF] rounded-lg flex items-center justify-center mr-3">
                <Info size={20} className="text-[#0066CC]" />
              </div>
              <h2 className="text-base font-semibold text-[#1A1A1A]">Cómo funciona</h2>
            </div>
            <p className="text-sm text-[#666666] leading-relaxed">
              Elige el importe y plazo que mejor se adapte a ti, revisa las condiciones, firma digitalmente y recibe el dinero en tu cuenta. Todo el proceso es rápido, seguro y sin papeleos.
            </p>
          </div>

          {/* Primary Button */}
          <button
            onClick={() => navigate(`/simulation?offerId=${offer.offer_id}`)}
            className="w-full bg-[#0066CC] text-white border-none rounded-lg py-4 text-base font-semibold flex items-center justify-center mb-3"
          >
            Simular mi préstamo
            <ArrowRight size={20} className="ml-2" />
          </button>

          {/* Secondary Button */}
          <button className="w-full bg-transparent text-[#0066CC] border-2 border-[#0066CC] rounded-lg py-3.5 text-base font-semibold text-center">
            Ver más detalles
          </button>
        </div>

        {/* Bottom Navigation */}
        <div className="flex-shrink-0 h-16 bg-white border-t border-gray-300 flex items-center justify-around px-4">
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            <span className="text-[11px] font-medium">Inicio</span>
          </button>
          <button className="flex flex-col items-center text-[#0066CC]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
              <line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
            <span className="text-[11px] font-medium">Productos</span>
          </button>
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
              <line x1="1" y1="10" x2="23" y2="10" />
            </svg>
            <span className="text-[11px] font-medium">Tarjetas</span>
          </button>
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            <span className="text-[11px] font-medium">Perfil</span>
          </button>
        </div>
      </div>
    </div>
  );
}
