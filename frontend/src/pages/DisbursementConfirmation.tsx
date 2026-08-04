import { useNavigate } from 'react-router-dom';
import { CheckCircle, Clock, ArrowRight, FileText, Calendar, X } from 'lucide-react';

export function DisbursementConfirmation() {
  const navigate = useNavigate();

  const details = [
    { label: 'Número de préstamo', value: 'PRE-2026-08-001234' },
    { label: 'Importe', value: '15.000,00€', highlight: true },
    { label: 'Cuota mensual', value: '352,47€' },
    { label: 'Primera cuota', value: '15 octubre 2026' },
    { label: 'Cuenta de abono', value: 'ES79 •••• 3456' },
    { label: 'Fecha de firma', value: '03 septiembre 2026' },
  ];

  const steps = [
    { number: 1, title: 'Recibirás el dinero', text: 'En un máximo de 24 horas en tu cuenta seleccionada' },
    { number: 2, title: 'Documentación firmada', text: 'Recibirás por email una copia del contrato firmado' },
    { number: 3, title: 'Primera cuota', text: 'Se cargará automáticamente el 15 de octubre 2026' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-end px-4 border-b border-gray-300">
          <button className="w-8 h-8 flex items-center justify-center text-[#666666]"><X size={24} /></button>
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gradient-to-br from-[#00A86B] to-[#008556] rounded-xl p-10 mb-6 text-center text-white">
            <div className="w-[100px] h-[100px] bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle size={50} />
            </div>
            <h1 className="text-2xl font-bold mb-3">¡Préstamo confirmado!</h1>
            <p className="text-[15px] opacity-95">Tu contrato ha sido firmado correctamente. El dinero estará disponible en tu cuenta muy pronto.</p>
          </div>

          <div className="bg-[#E6F2FF] rounded-xl p-4 mb-5">
            <div className="flex items-center mb-3"><Clock size={24} className="text-[#0066CC] mr-3" /><div className="text-base font-semibold text-[#1A1A1A]">Tiempo estimado de abono</div></div>
            <p className="text-sm text-[#1A1A1A]">El importe de <strong className="font-semibold text-[#0066CC]">15.000,00€</strong> se abonará en tu cuenta en un plazo máximo de <strong className="font-semibold text-[#0066CC]">24 horas</strong>. Te notificaremos cuando el dinero esté disponible.</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Detalles de tu préstamo</h2>
            {details.map((d, i) => (
              <div key={i} className={`flex justify-between py-2.5 ${i < details.length - 1 ? 'border-b border-gray-200' : ''}`}>
                <span className="text-[13px] text-[#666666]">{d.label}</span>
                <span className={d.highlight ? 'text-lg font-semibold text-[#00A86B]' : 'text-sm font-semibold text-[#1A1A1A]'}>{d.value}</span>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Próximos pasos</h2>
            {steps.map((s, i) => (
              <div key={i} className={`flex items-start ${i < steps.length - 1 ? 'mb-4' : ''}`}>
                <div className="w-7 h-7 bg-[#E6F2FF] rounded-full flex items-center justify-center mr-3 flex-shrink-0 text-[13px] font-bold text-[#0066CC]">{s.number}</div>
                <div>
                  <div className="text-sm font-semibold text-[#1A1A1A] mb-1">{s.title}</div>
                  <div className="text-[13px] text-[#666666]">{s.text}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3 mb-3">
            {[
              { icon: FileText, label: 'Ver contrato' },
              { icon: Calendar, label: 'Ver cuotas' },
            ].map((action, i) => (
              <button key={i} className="bg-white border border-gray-300 rounded-lg p-4 flex flex-col items-center text-center">
                <action.icon size={32} className="text-[#0066CC] mb-2" />
                <div className="text-[13px] font-semibold text-[#1A1A1A]">{action.label}</div>
              </button>
            ))}
          </div>

          <button onClick={() => navigate('/active-loan')} className="w-full bg-[#0066CC] text-white rounded-lg py-4 flex items-center justify-center font-semibold">
            Ir a mis préstamos <ArrowRight size={20} className="ml-2" />
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
