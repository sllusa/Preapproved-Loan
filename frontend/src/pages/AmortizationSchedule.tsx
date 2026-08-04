import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Info, ArrowRight } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function AmortizationSchedule() {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState('monthly');

  const installments = [
    { cuota: 1, month: 'Octubre 2026', total: '352,47€', principal: '265,22€', interest: '87,25€', pending: '14.734,78€' },
    { cuota: 2, month: 'Noviembre 2026', total: '352,47€', principal: '266,76€', interest: '85,71€', pending: '14.468,02€' },
    { cuota: 3, month: 'Diciembre 2026', total: '352,47€', principal: '268,31€', interest: '84,16€', pending: '14.199,71€' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-between px-4 border-b border-gray-300">
          <button onClick={() => navigate(-1)} className="w-8 h-8 flex items-center justify-center text-[#0066CC]"><ArrowLeft size={24} /></button>
          <div className="text-base font-semibold text-[#1A1A1A]">Desglose de cuotas</div>
          <button className="w-8 h-8 flex items-center justify-center text-[#666666]"><Download size={20} /></button>
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gray-300 h-1 rounded-full mb-6">
            <div className="bg-[#0066CC] h-full w-1/2"></div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <div className="text-sm text-[#666666] mb-2">Cuota mensual</div>
            <div className="text-[32px] font-bold text-[#0066CC] mb-4">{formatCurrency(352.47)}</div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Importe total', value: '15.000€' },
                { label: 'Plazo', value: '48 meses' },
                { label: 'TIN', value: '6,95%' },
                { label: 'TAE', value: '7,18%' },
              ].map((item, i) => (
                <div key={i}>
                  <span className="text-xs text-[#999999] block mb-1">{item.label}</span>
                  <span className="text-base font-semibold text-[#1A1A1A]">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Evolución del préstamo</h2>
            <div className="flex items-end justify-between h-[120px] mb-3">
              {[100, 95, 88, 80, 70, 58, 45, 30, 18, 8].map((height, i) => (
                <div
                  key={i}
                  className="w-[8%] bg-gradient-to-t from-[#00A86B] to-[#FF6B35] rounded-t"
                  style={{ height: `${height}%` }}
                />
              ))}
            </div>
            <div className="flex justify-center gap-6">
              {[
                { color: 'bg-[#00A86B]', label: 'Capital' },
                { color: 'bg-[#FF6B35]', label: 'Intereses' },
              ].map((item, i) => (
                <div key={i} className="flex items-center text-[13px] text-[#666666]">
                  <div className={`w-3 h-3 ${item.color} rounded mr-2`}></div>
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-[#1A1A1A]">Cuadro de amortización</h2>
            <div className="flex bg-white rounded-lg border border-gray-300 overflow-hidden">
              {['monthly', 'annual'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-4 py-2 text-[13px] font-medium ${
                    viewMode === mode ? 'bg-[#0066CC] text-white' : 'bg-white text-[#666666]'
                  }`}
                >
                  {mode === 'monthly' ? 'Mensual' : 'Anual'}
                </button>
              ))}
            </div>
          </div>

          {installments.map((inst, i) => (
            <div key={i} className="bg-white rounded-xl p-4 border border-gray-300 mb-3">
              <div className="flex justify-between mb-3">
                <span className="text-sm font-semibold text-[#1A1A1A]">Cuota {inst.cuota} - {inst.month}</span>
                <span className="text-base font-bold text-[#0066CC]">{inst.total}</span>
              </div>
              <div className="grid grid-cols-3 gap-3 pt-3 border-t border-gray-200">
                <div>
                  <span className="text-[11px] text-[#999999] uppercase tracking-wider block mb-1">Capital</span>
                  <span className="text-sm font-semibold text-[#00A86B]">{inst.principal}</span>
                </div>
                <div>
                  <span className="text-[11px] text-[#999999] uppercase tracking-wider block mb-1">Intereses</span>
                  <span className="text-sm font-semibold text-[#FF6B35]">{inst.interest}</span>
                </div>
                <div>
                  <span className="text-[11px] text-[#999999] uppercase tracking-wider block mb-1">Pendiente</span>
                  <span className="text-sm font-semibold text-[#1A1A1A]">{inst.pending}</span>
                </div>
              </div>
            </div>
          ))}

          <div className="bg-[#E6F2FF] rounded-lg p-3 flex items-start mb-5">
            <Info size={20} className="text-[#0066CC] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#1A1A1A]">
              Puedes realizar amortizaciones anticipadas sin penalización en cualquier momento desde tu área de préstamos.
            </div>
          </div>

          <button className="w-full bg-[#0066CC] text-white rounded-lg py-4 flex items-center justify-center font-semibold">
            Continuar <ArrowRight size={20} className="ml-2" />
          </button>
        </div>

        <div className="flex-shrink-0 h-16 bg-white border-t border-gray-300 flex items-center justify-around px-4">
          <button className="flex flex-col items-center text-[#999999]"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg><span className="text-[11px] font-medium">Inicio</span></button>
          <button className="flex flex-col items-center text-[#0066CC]"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" /></svg><span className="text-[11px] font-medium">Productos</span></button>
          <button className="flex flex-col items-center text-[#999999]"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><rect x="1" y="4" width="22" height="16" rx="2" ry="2" /><line x1="1" y1="10" x2="23" y2="10" /></svg><span className="text-[11px] font-medium">Tarjetas</span></button>
          <button className="flex flex-col items-center text-[#999999]"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg><span className="text-[11px] font-medium">Perfil</span></button>
        </div>
      </div>
    </div>
  );
}
