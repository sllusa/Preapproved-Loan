import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, FileText, ExternalLink, AlertCircle, Check } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

export function PrecontractualReview() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [acknowledged, setAcknowledged] = useState(true);

  const documents = [
    { name: 'Ficha de Información Precontractual (SECCI)', pages: 4 },
    { name: 'Contrato de Préstamo Personal', pages: 8 },
    { name: 'Condiciones Generales', pages: 6 },
  ];

  const conditions = [
    { label: 'Importe del préstamo', value: '15.000,00€' },
    { label: 'Plazo', value: '48 meses' },
    { label: 'Cuota mensual', value: '352,47€' },
    { label: 'TIN', value: '6,95%' },
    { label: 'TAE', value: '7,18%' },
    { label: 'Importe total adeudado', value: '16.918,56€' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col">
        <div className="flex-shrink-0 h-14 bg-white flex items-center justify-between px-4 border-b border-gray-300">
          <button onClick={() => navigate(-1)} className="w-8 h-8 flex items-center justify-center text-[#0066CC]"><ArrowLeft size={24} /></button>
          <div className="text-base font-semibold text-[#1A1A1A]">Documentación</div>
          <div className="w-8" />
        </div>

        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          <div className="bg-gray-300 h-1 rounded-full mb-6"><div className="bg-[#0066CC] h-full" style={{width: '62%'}}></div></div>

          <h1 className="text-xl font-bold text-[#1A1A1A] mb-2">Revisa la documentación</h1>
          <p className="text-sm text-[#666666] mb-6">Lee atentamente los documentos antes de continuar con la firma</p>

          {documents.map((doc, i) => (
            <div key={i} className="bg-white rounded-xl p-4 border border-gray-300 flex items-center mb-3">
              <div className="w-12 h-12 bg-[#E6F2FF] rounded-lg flex items-center justify-center mr-4"><FileText size={24} className="text-[#0066CC]" /></div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-[#1A1A1A] mb-1">{doc.name}</div>
                <div className="text-xs text-[#999999]">PDF • {doc.pages} páginas</div>
              </div>
              <div className="flex items-center text-sm font-semibold text-[#0066CC]">Ver <ExternalLink size={20} className="ml-1" /></div>
            </div>
          ))}

          <div className="bg-[#FFF4E6] border border-[#FFE0B2] rounded-xl p-4 mb-5">
            <div className="flex items-center mb-3"><AlertCircle size={24} className="text-[#FFA500] mr-3" /><div className="text-base font-semibold text-[#1A1A1A]">Información importante</div></div>
            <p className="text-[13px] text-[#666666]">Es obligatorio leer y comprender toda la documentación antes de firmar el contrato. Estos documentos contienen información esencial sobre tus derechos y obligaciones.</p>
          </div>

          <div className="bg-white rounded-xl p-5 border border-gray-300 mb-5">
            <div className="text-base font-semibold text-[#1A1A1A] mb-4">Resumen de condiciones</div>
            {conditions.map((c, i) => (
              <div key={i} className={`flex justify-between py-2.5 ${i < conditions.length - 1 ? 'border-b border-gray-200' : ''}`}>
                <span className="text-[13px] text-[#666666]">{c.label}</span>
                <span className="text-sm font-semibold text-[#1A1A1A]">{c.value}</span>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl p-4 border border-gray-300 mb-5">
            {[
              'He leído y comprendido la Ficha de Información Precontractual (SECCI) y el Contrato de Préstamo Personal',
              'Acepto las condiciones establecidas en el contrato y las condiciones generales'
            ].map((text, i) => (
              <div key={i} className={`flex items-start ${i === 0 ? 'mb-4' : ''}`}>
                <div className="w-5 h-5 border-2 border-[#0066CC] rounded bg-[#0066CC] flex items-center justify-center mr-3 flex-shrink-0 text-white">
                  <Check size={14} />
                </div>
                <div className="text-[13px] text-[#1A1A1A]"><strong>{text.split(' ')[0]} {text.split(' ')[1]} {text.split(' ')[2]}</strong> {text.split(' ').slice(3).join(' ')}</div>
              </div>
            ))}
          </div>

          <button onClick={() => navigate(`/checks?${searchParams.toString()}`)} className="w-full bg-[#0066CC] text-white rounded-lg py-4 flex items-center justify-center font-semibold">
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
