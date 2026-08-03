import { Home, Wallet, CreditCard, User } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export function BottomNavigation() {
  const location = useLocation();
  
  // Determine active tab based on current path
  const isProductsActive = [
    '/offers',
    '/simulation',
    '/accounts',
    '/documents',
    '/checks',
    '/signing',
    '/confirmation',
    '/active-loan',
    '/amortization',
  ].some(path => location.pathname.startsWith(path));

  return (
    <div className="flex-shrink-0 h-16 bg-white border-t border-gray-300 flex items-center justify-around px-4">
      <button className="flex flex-col items-center text-[#999999]">
        <Home size={24} className="mb-1" />
        <span className="text-[11px] font-medium">Inicio</span>
      </button>

      <button className={`flex flex-col items-center ${isProductsActive ? 'text-[#0066CC]' : 'text-[#999999]'}`}>
        <Wallet size={24} className="mb-1" />
        <span className="text-[11px] font-medium">Productos</span>
      </button>

      <button className="flex flex-col items-center text-[#999999]">
        <CreditCard size={24} className="mb-1" />
        <span className="text-[11px] font-medium">Tarjetas</span>
      </button>

      <button className="flex flex-col items-center text-[#999999]">
        <User size={24} className="mb-1" />
        <span className="text-[11px] font-medium">Perfil</span>
      </button>
    </div>
  );
}
