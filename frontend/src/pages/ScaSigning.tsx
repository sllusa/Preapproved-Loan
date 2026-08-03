import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PenTool, ShieldCheck, Smartphone, Key, Info } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function ScaSigning() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedMethod, setSelectedMethod] = useState('sms');

  const handleSign = () => {
    navigate(`/confirmation?${searchParams.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-center px-4 border-b border-gray-300">
          <div className="text-base font-semibold text-[#1A1A1A]">Firma digital</div>
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gray-300 h-1 rounded-full mb-6"><div className="bg-[#0066CC] h-full" style={{width: '95%'}}></div></div>

          <div className="bg-gradient-to-br from-[#0066CC] to-[#004C99] rounded-xl p-8 mb-6 text-center text-white">
            <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-5"><PenTool size={40} /></div>
            <h1 className="text-[22px] font-bold mb-2">Último paso: Firma tu contrato</h1>
            <p className="text-sm opacity-90">Tu solicitud ha sido aprobada. Solo falta tu firma digital para completar el proceso.</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Resumen del préstamo</h2>
            {[
              { label: 'Importe del préstamo', value: '15.000,00€' },
              { label: 'Plazo', value: '48 meses' },
              { label: 'Cuota mensual', value: '352,47€', highlight: true },
              { label: 'TIN', value: '6,95%' },
              { label: 'TAE', value: '7,18%' },
              { label: 'Cuenta de abono', value: 'ES79 •••• 3456' },
            ].map((item, i) => (
              <div key={i} className={`flex justify-between py-2.5 ${i < 5 ? 'border-b border-gray-200' : ''}`}>
                <span className="text-[13px] text-[#666666]">{item.label}</span>
                <span className={item.highlight ? 'text-lg font-semibold text-[#0066CC]' : 'text-sm font-semibold text-[#1A1A1A]'}>{item.value}</span>
              </div>
            ))}
          </div>

          <div className="bg-[#E8F5E9] border border-[#C8E6C9] rounded-xl p-4 mb-5">
            <div className="flex items-center mb-3"><ShieldCheck size={24} className="text-[#00A86B] mr-3" /><div className="text-base font-semibold text-[#1A1A1A]">Firma segura PSD2</div></div>
            <p className="text-[13px] text-[#666666]">Tu firma está protegida por autenticación reforzada de cliente (SCA) según la normativa europea PSD2, garantizando la máxima seguridad.</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-3">Método de autenticación</h2>
            <p className="text-sm text-[#666666] mb-4">Selecciona cómo quieres autenticar tu firma:</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'sms', icon: Smartphone, label: 'SMS' },
                { id: 'digital', icon: Key, label: 'Clave digital' },
              ].map((method) => (
                <button
                  key={method.id}
                  onClick={() => setSelectedMethod(method.id)}
                  className={`p-4 rounded-lg border-2 text-center ${
                    selectedMethod === method.id ? 'border-[#0066CC] bg-[#E6F2FF]' : 'border-gray-300 bg-[#F8F9FA]'
                  }`}
                >
                  <method.icon size={32} className="text-[#0066CC] mx-auto mb-2" />
                  <div className="text-[13px] font-semibold text-[#1A1A1A]">{method.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-[#E6F2FF] rounded-lg p-3 flex items-start mb-5">
            <Info size={20} className="text-[#0066CC] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#1A1A1A]">Recibirás un código de verificación en tu móvil terminado en •••45. Introdúcelo en la siguiente pantalla para completar la firma.</div>
          </div>

          <button onClick={handleSign} className="w-full bg-[#0066CC] text-white rounded-lg py-4 flex items-center justify-center font-semibold mb-3">
            Firmar contrato <PenTool size={20} className="ml-2" />
          </button>

          <button className="w-full bg-transparent text-[#666666] py-3 text-sm font-medium text-center">Revisar documentación de nuevo</button>
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
