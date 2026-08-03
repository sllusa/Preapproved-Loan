import { useNavigate } from 'react-router-dom';
import { ArrowLeft, MoreVertical, TrendingDown, FileText, ChevronRight } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function ActiveLoanSummary() {
  const navigate = useNavigate();

  const loanDetails = [
    { label: 'Importe inicial', value: '15.000,00€' },
    { label: 'Plazo total', value: '48 meses' },
    { label: 'TIN', value: '6,95%' },
    { label: 'TAE', value: '7,18%' },
    { label: 'Fecha de contratación', value: '03 Sep 2026' },
    { label: 'Fecha de vencimiento', value: '15 Sep 2030' },
  ];

  const recentPayments = [
    { cuota: 1, month: 'Oct 2026', status: 'Pagada', amount: '352,47€' },
    { cuota: 2, month: 'Nov 2026', status: 'Pagada', amount: '352,47€' },
    { cuota: 3, month: 'Dic 2026', status: 'Pagada', amount: '352,47€' },
    { cuota: 4, month: 'Ene 2027', status: 'Pendiente', amount: '352,47€' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-[#0066CC] flex items-center justify-between px-4">
          <button onClick={() => navigate(-1)} className="w-8 h-8 flex items-center justify-center text-white"><ArrowLeft size={24} /></button>
          <div className="text-base font-semibold text-white">Mi préstamo</div>
          <button className="w-8 h-8 flex items-center justify-center text-white"><MoreVertical size={20} /></button>
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gradient-to-br from-[#0066CC] to-[#004C99] rounded-xl p-6 mb-5 text-white">
            <div className="inline-block bg-white bg-opacity-20 px-3 py-1.5 rounded-full text-xs font-semibold mb-3">ACTIVO</div>
            <div className="text-[13px] mb-4">Préstamo PRE-2026-08-001234</div>
            <div className="text-sm opacity-90 mb-1">Saldo pendiente</div>
            <div className="text-4xl font-bold mb-4">{formatCurrency(14734.78)}</div>
            <div className="bg-white bg-opacity-20 h-2 rounded-full overflow-hidden mb-2">
              <div className="bg-white h-full w-[15%]"></div>
            </div>
            <div className="text-xs opacity-90">7 de 48 cuotas pagadas (15%)</div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-5">
            {[
              { icon: TrendingDown, label: 'Amortizar' },
              { icon: FileText, label: 'Documentos' },
            ].map((action, i) => (
              <div key={i} className="bg-white rounded-xl p-4 border border-gray-300 flex flex-col items-center text-center">
                <div className="w-10 h-10 bg-[#E6F2FF] rounded-lg flex items-center justify-center mb-3"><action.icon size={20} className="text-[#0066CC]" /></div>
                <div className="text-[13px] font-semibold text-[#1A1A1A]">{action.label}</div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <div className="flex items-center justify-between mb-4">
              <div className="text-base font-semibold text-[#1A1A1A]">Próxima cuota</div>
              <div className="bg-[#E6F2FF] px-3 py-1.5 rounded-md text-xs font-semibold text-[#0066CC]">15 Oct 2026</div>
            </div>
            <div className="text-[32px] font-bold text-[#0066CC] mb-4">{formatCurrency(352.47)}</div>
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              {[
                { label: 'Capital', value: '265,22€', color: 'text-[#00A86B]' },
                { label: 'Intereses', value: '87,25€', color: 'text-[#FF6B35]' },
                { label: 'Cuenta de cargo', value: 'ES79 •••• 3456', color: 'text-[#1A1A1A]' },
                { label: 'Pendiente tras pago', value: '14.382,31€', color: 'text-[#1A1A1A]' },
              ].map((item, i) => (
                <div key={i}>
                  <span className="text-xs text-[#999999] block mb-1">{item.label}</span>
                  <span className={`text-base font-semibold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Detalles del préstamo</h2>
            {loanDetails.map((d, i) => (
              <div key={i} className={`flex justify-between py-2.5 ${i < loanDetails.length - 1 ? 'border-b border-gray-200' : ''}`}>
                <span className="text-[13px] text-[#666666]">{d.label}</span>
                <span className="text-sm font-semibold text-[#1A1A1A]">{d.value}</span>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300">
            <div className="flex items-center justify-between mb-4">
              <div className="text-base font-semibold text-[#1A1A1A]">Cuadro de amortización</div>
              <button onClick={() => navigate('/amortization')} className="text-[13px] font-semibold text-[#0066CC] flex items-center">
                Ver todo <ChevronRight size={16} className="ml-1" />
              </button>
            </div>
            {recentPayments.map((p, i) => (
              <div key={i} className={`flex justify-between py-3 ${i < recentPayments.length - 1 ? 'border-b border-gray-200' : ''}`}>
                <div>
                  <div className="text-sm font-semibold text-[#1A1A1A] mb-0.5">Cuota {p.cuota} - {p.month}</div>
                  <div className="text-xs text-[#00A86B]">{p.status}</div>
                </div>
                <div className="text-sm font-semibold text-[#1A1A1A]">{p.amount}</div>
              </div>
            ))}
          </div>
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
