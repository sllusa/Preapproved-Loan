import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Wallet, PiggyBank, CreditCard, AlertCircle, Check, Info } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function AccountSelection() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedAccountId, setSelectedAccountId] = useState('ES79 2085 1234 5678 9012 3456');

  // Mock accounts data (would come from API)
  const accounts = [
    { id: 'ES79 2085 1234 5678 9012 3456', name: 'Cuenta Nómina', icon: Wallet, balance: 3245.67, operable: true },
    { id: 'ES79 2085 9876 5432 1098 7654', name: 'Cuenta Ahorro', icon: PiggyBank, balance: 12890.45, operable: true },
    { id: 'ES79 2085 1111 2222 3333 4444', name: 'Cuenta Joven', icon: CreditCard, balance: 156.23, operable: false },
  ];

  const handleContinue = () => {
    navigate(`/documents?${searchParams.toString()}&accountId=${selectedAccountId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-between px-4 border-b border-gray-300">
          <button onClick={() => navigate(-1)} className="w-8 h-8 flex items-center justify-center text-[#0066CC]">
            <ArrowLeft size={24} />
          </button>
          <div className="text-base font-semibold text-[#1A1A1A]">Cuenta de abono</div>
          <div className="w-8" />
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gray-300 h-1 rounded-full mb-6">
            <div className="bg-[#0066CC] h-full w-1/2"></div>
          </div>

          <h1 className="text-xl font-bold text-[#1A1A1A] mb-2">Selecciona tu cuenta</h1>
          <p className="text-sm text-[#666666] mb-6">Elige la cuenta donde quieres recibir el importe del préstamo</p>

          {accounts.map((account) => {
            const Icon = account.icon;
            const isSelected = selectedAccountId === account.id;
            
            return (
              <div
                key={account.id}
                onClick={() => account.operable && setSelectedAccountId(account.id)}
                className={`bg-white rounded-xl p-4 flex items-center mb-3 relative cursor-pointer ${
                  isSelected ? 'border-2 border-[#0066CC] bg-[#E6F2FF]' : 'border-2 border-gray-300'
                } ${!account.operable ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-4 flex-shrink-0 ${
                  isSelected ? 'bg-[#0066CC] text-white' : account.operable ? 'bg-[#E6F2FF] text-[#0066CC]' : 'bg-gray-300 text-[#999999]'
                }`}>
                  <Icon size={24} />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-[#1A1A1A] mb-1">{account.name}</div>
                  <div className="text-[13px] text-[#666666] mb-1">{account.id}</div>
                  <div className="text-sm font-semibold text-[#00A86B]">Saldo: {formatCurrency(account.balance)}</div>
                </div>
                {isSelected && <Check size={24} className="text-[#0066CC] absolute right-4 top-1/2 -translate-y-1/2" />}
                {!account.operable && (
                  <div className="absolute top-3 right-3 bg-[#FFF4E6] border border-[#FFE0B2] rounded px-2 py-1 text-[11px] font-semibold text-[#FFA500]">
                    No disponible
                  </div>
                )}
              </div>
            );
          })}

          <div className="bg-[#FFF4E6] border border-[#FFE0B2] rounded-lg p-3 flex items-start mb-5">
            <AlertCircle size={20} className="text-[#FFA500] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#1A1A1A]">
              La cuenta seleccionada debe estar operativa y sin restricciones para recibir el abono del préstamo.
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 border border-gray-300 mb-5">
            <div className="text-sm font-semibold text-[#1A1A1A] mb-3">Requisitos de la cuenta</div>
            {['Debe ser una cuenta a tu nombre', 'Debe estar activa y operativa', 'No puede tener embargos o restricciones', 'Debe permitir operaciones de abono'].map((req, i) => (
              <div key={i} className="flex items-start mb-2">
                <Check size={16} className="text-[#00A86B] mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-[13px] text-[#666666]">{req}</span>
              </div>
            ))}
          </div>

          <div className="bg-[#E6F2FF] rounded-lg p-3 flex items-start mb-5">
            <Info size={20} className="text-[#0066CC] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#1A1A1A]">
              El dinero estará disponible en tu cuenta en un plazo máximo de 24 horas tras la firma del contrato.
            </div>
          </div>

          <button onClick={handleContinue} className="w-full bg-[#0066CC] text-white rounded-lg py-4 flex items-center justify-center font-semibold">
            Continuar <ArrowRight size={20} className="ml-2" />
          </button>
        </div>

        <div className="flex-shrink-0 h-16 bg-white border-t border-gray-300 flex items-center justify-around px-4">
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>
            <span className="text-[11px] font-medium">Inicio</span>
          </button>
          <button className="flex flex-col items-center text-[#0066CC]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><polyline points="3.27 6.96 12 12.01 20.73 6.96" /><line x1="12" y1="22.08" x2="12" y2="12" /></svg>
            <span className="text-[11px] font-medium">Productos</span>
          </button>
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><rect x="1" y="4" width="22" height="16" rx="2" ry="2" /><line x1="1" y1="10" x2="23" y2="10" /></svg>
            <span className="text-[11px] font-medium">Tarjetas</span>
          </button>
          <button className="flex flex-col items-center text-[#999999]">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mb-1"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
            <span className="text-[11px] font-medium">Perfil</span>
          </button>
        </div>
      </div>
    </div>
  );
}
