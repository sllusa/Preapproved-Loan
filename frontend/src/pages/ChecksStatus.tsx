import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ShieldCheck, CheckCircle, Loader, Clock, Info } from 'lucide-react';

export function ChecksStatus() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [checksComplete, setChecksComplete] = useState(false);

  const checks = [
    { name: 'Verificación de identidad', status: 'success', statusText: 'Completada' },
    { name: 'Análisis de solvencia', status: 'loading', statusText: 'En proceso...' },
    { name: 'Verificación antifraude', status: 'pending', statusText: 'Pendiente' },
    { name: 'Cumplimiento normativo (AML/PBC)', status: 'pending', statusText: 'Pendiente' },
  ];

  const timeline = [
    { step: 'Simulación completada', time: 'Hace 5 minutos', status: 'complete' },
    { step: 'Documentación revisada', time: 'Hace 2 minutos', status: 'complete' },
    { step: 'Verificaciones en curso', time: 'Ahora', status: 'current' },
    { step: 'Firma digital', time: 'Siguiente paso', status: 'pending' },
    { step: 'Abono del préstamo', time: 'Último paso', status: 'pending' },
  ];

  useEffect(() => {
    const timer = setTimeout(() => {
      setChecksComplete(true);
      navigate(`/signing?${searchParams.toString()}`);
    }, 5000);
    return () => clearTimeout(timer);
  }, [navigate, searchParams]);

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-center px-4 border-b border-gray-300">
          <div className="text-base font-semibold text-[#1A1A1A]">Verificación en curso</div>
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gray-300 h-1 rounded-full mb-6"><div className="bg-[#0066CC] h-full" style={{width: '87%'}}></div></div>

          <div className="bg-white rounded-xl p-8 border border-gray-300 mb-6 text-center">
            <div className="w-20 h-20 bg-[#E6F2FF] rounded-full flex items-center justify-center mx-auto mb-5 relative">
              <div className="absolute inset-0 border-[3px] border-gray-300 border-t-[#0066CC] rounded-full animate-spin"></div>
              <ShieldCheck size={40} className="text-[#0066CC]" />
            </div>
            <h1 className="text-xl font-bold text-[#1A1A1A] mb-2">Verificando tu solicitud</h1>
            <p className="text-sm text-[#666666]">Estamos realizando las comprobaciones necesarias. Este proceso suele tardar menos de un minuto.</p>
          </div>

          {checks.map((check, i) => (
            <div key={i} className="bg-white rounded-xl p-4 border border-gray-300 flex items-center mb-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-4 ${
                check.status === 'success' ? 'bg-[#E8F5E9] text-[#00A86B]' :
                check.status === 'loading' ? 'bg-[#FFF4E6] text-[#FFA500]' :
                'bg-[#E6F2FF] text-[#0066CC]'
              }`}>
                {check.status === 'success' && <CheckCircle size={20} />}
                {check.status === 'loading' && <Loader size={20} className="animate-spin" />}
                {check.status === 'pending' && <Clock size={20} />}
              </div>
              <div>
                <div className="text-sm font-semibold text-[#1A1A1A] mb-1">{check.name}</div>
                <div className={`text-xs ${
                  check.status === 'success' ? 'text-[#00A86B]' :
                  check.status === 'loading' ? 'text-[#FFA500]' :
                  'text-[#0066CC]'
                }`}>{check.statusText}</div>
              </div>
            </div>
          ))}

          <div className="bg-[#E6F2FF] rounded-xl p-4 mb-5">
            <div className="flex items-center mb-3"><Info size={20} className="text-[#0066CC] mr-3" /><div className="text-sm font-semibold text-[#1A1A1A]">¿Por qué verificamos?</div></div>
            <p className="text-[13px] text-[#1A1A1A]">Estas verificaciones son obligatorias por normativa y nos ayudan a protegerte contra el fraude y garantizar que el préstamo se ajusta a tu situación financiera.</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <div className="text-base font-semibold text-[#1A1A1A] mb-4">Progreso de tu solicitud</div>
            {timeline.map((item, i) => (
              <div key={i} className={`flex items-start ${i < timeline.length - 1 ? 'mb-4' : ''}`}>
                <div className={`w-3 h-3 rounded-full mr-3 flex-shrink-0 mt-1 ${
                  item.status === 'complete' ? 'bg-[#00A86B]' :
                  item.status === 'current' ? 'bg-[#0066CC] shadow-[0_0_0_4px_rgba(0,102,204,0.2)]' :
                  'bg-gray-300'
                }`}></div>
                <div>
                  <div className="text-sm font-semibold text-[#1A1A1A]">{item.step}</div>
                  <div className="text-xs text-[#999999]">{item.time}</div>
                </div>
              </div>
            ))}
          </div>

          <button disabled className="w-full bg-gray-300 text-[#999999] rounded-lg py-4 font-semibold">
            Esperando verificaciones...
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
