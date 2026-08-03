import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Info } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function Simulation() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const offerId = searchParams.get('offerId');

  // State
  const [amount, setAmount] = useState(15000);
  const [termMonths, setTermMonths] = useState(48);
  
  // Simulation constants (would come from API in real implementation)
  const minAmount = 1000;
  const maxAmount = 20000;
  const minTerm = 12;
  const maxTerm = 72;
  const tin = 6.95;
  const tae = 7.18;

  // Calculate installment and totals based on French amortization
  const monthlyRate = tin / 100 / 12;
  const installment = amount * (monthlyRate * Math.pow(1 + monthlyRate, termMonths)) / (Math.pow(1 + monthlyRate, termMonths) - 1);
  const totalCost = installment * termMonths;
  const totalInterest = totalCost - amount;

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAmount(Number(e.target.value));
  };

  const handleTermChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTermMonths(Number(e.target.value));
  };

  const handleContinue = () => {
    // Navigate to account selection
    navigate(`/accounts?offerId=${offerId}&amount=${amount}&term=${termMonths}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col relative">
        {/* Top Bar */}
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-between px-4 border-b border-gray-300">
          <button
            onClick={() => navigate(-1)}
            className="w-8 h-8 flex items-center justify-center text-[#0066CC]"
            aria-label="Volver"
          >
            <ArrowLeft size={24} />
          </button>
          <div className="text-[#1A1A1A] text-base font-semibold">Simular préstamo</div>
          <button className="text-[#0066CC] text-sm font-semibold">Guardar</button>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          {/* Progress Bar */}
          <div className="bg-gray-300 h-1 rounded-full mb-6 overflow-hidden">
            <div className="bg-[#0066CC] h-full w-1/4"></div>
          </div>

          <h1 className="text-xl font-bold text-[#1A1A1A] mb-2">Personaliza tu préstamo</h1>
          <p className="text-sm text-[#666666] mb-6 leading-relaxed">
            Ajusta el importe y el plazo para ver tu cuota mensual y el coste total
          </p>

          {/* Amount Slider */}
          <div className="mb-6">
            <label className="text-sm font-semibold text-[#1A1A1A] mb-2 block">
              Importe del préstamo
            </label>
            <span className="text-xs text-[#666666] mb-2 block">
              Máximo disponible: {formatCurrency(maxAmount)}
            </span>
            <div className="py-4">
              <div className="bg-[#E6F2FF] border-2 border-[#0066CC] rounded-lg p-4 text-center mb-4">
                <div className="text-[32px] font-bold text-[#0066CC]">{formatCurrency(amount)}</div>
                <div className="text-sm text-[#666666] mt-1">Importe solicitado</div>
              </div>
              <input
                type="range"
                min={minAmount}
                max={maxAmount}
                step={100}
                value={amount}
                onChange={handleAmountChange}
                className="w-full h-2 bg-gray-300 rounded appearance-none cursor-pointer slider-thumb"
                style={{
                  background: `linear-gradient(to right, #0066CC 0%, #0066CC ${((amount - minAmount) / (maxAmount - minAmount)) * 100}%, #E0E0E0 ${((amount - minAmount) / (maxAmount - minAmount)) * 100}%, #E0E0E0 100%)`
                }}
              />
              <div className="flex justify-between text-xs text-[#999999] mt-2">
                <span>{formatCurrency(minAmount)}</span>
                <span>{formatCurrency(maxAmount)}</span>
              </div>
            </div>
          </div>

          {/* Term Slider */}
          <div className="mb-6">
            <label className="text-sm font-semibold text-[#1A1A1A] mb-2 block">
              Plazo de devolución
            </label>
            <span className="text-xs text-[#666666] mb-2 block">
              Máximo disponible: {maxTerm} meses
            </span>
            <div className="py-4">
              <div className="bg-[#E6F2FF] border-2 border-[#0066CC] rounded-lg p-4 text-center mb-4">
                <div className="text-[32px] font-bold text-[#0066CC]">{termMonths} meses</div>
                <div className="text-sm text-[#666666] mt-1">Plazo seleccionado</div>
              </div>
              <input
                type="range"
                min={minTerm}
                max={maxTerm}
                step={1}
                value={termMonths}
                onChange={handleTermChange}
                className="w-full h-2 bg-gray-300 rounded appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #0066CC 0%, #0066CC ${((termMonths - minTerm) / (maxTerm - minTerm)) * 100}%, #E0E0E0 ${((termMonths - minTerm) / (maxTerm - minTerm)) * 100}%, #E0E0E0 100%)`
                }}
              />
              <div className="flex justify-between text-xs text-[#999999] mt-2">
                <span>{minTerm} meses</span>
                <span>{maxTerm} meses</span>
              </div>
            </div>
          </div>

          {/* Summary Card */}
          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-4">
            <h2 className="text-base font-semibold text-[#1A1A1A] mb-4">Resumen de tu préstamo</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-sm text-[#666666]">Cuota mensual</span>
                <span className="text-xl font-semibold text-[#0066CC]">{formatCurrency(installment)}</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-sm text-[#666666]">TIN (Tipo de Interés Nominal)</span>
                <span className="text-base font-semibold text-[#1A1A1A]">{tin.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-sm text-[#666666]">TAE (Tasa Anual Equivalente)</span>
                <span className="text-base font-semibold text-[#1A1A1A]">{tae.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200">
                <span className="text-sm text-[#666666]">Importe total adeudado</span>
                <span className="text-base font-semibold text-[#1A1A1A]">{formatCurrency(totalCost)}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-sm text-[#666666]">Intereses totales</span>
                <span className="text-base font-semibold text-[#1A1A1A]">{formatCurrency(totalInterest)}</span>
              </div>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-[#E6F2FF] rounded-lg p-3 flex items-start mb-6">
            <Info size={20} className="text-[#0066CC] mr-3 flex-shrink-0" />
            <div className="text-[13px] text-[#1A1A1A] leading-relaxed">
              Los valores mostrados son orientativos. El cálculo definitivo se realizará tras la validación de tu solicitud.
            </div>
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full bg-[#0066CC] text-white border-none rounded-lg py-4 text-base font-semibold flex items-center justify-center"
          >
            Continuar
            <ArrowRight size={20} className="ml-2" />
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
