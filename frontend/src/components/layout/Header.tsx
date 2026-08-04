import { ArrowLeft, Bell } from 'lucide-react';

interface HeaderProps {
  title?: string;
  showBackButton?: boolean;
  showLogo?: boolean;
  onBackClick?: () => void;
  variant?: 'primary' | 'white';
}

export function Header({
  title,
  showBackButton = false,
  showLogo = false,
  onBackClick,
  variant = 'white',
}: HeaderProps) {
  const isPrimary = variant === 'primary';
  
  return (
    <div 
      className={`flex-shrink-0 h-14 flex items-center justify-between px-4 ${
        isPrimary 
          ? 'bg-[#0066CC] border-none' 
          : 'bg-white border-b border-gray-300'
      }`}
    >
      {showBackButton && (
        <button
          onClick={onBackClick}
          className={`w-8 h-8 flex items-center justify-center ${
            isPrimary ? 'text-white' : 'text-[#0066CC]'
          }`}
          aria-label="Volver"
        >
          <ArrowLeft size={24} />
        </button>
      )}

      {showLogo && (
        <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center">
          <span className="text-[#0066CC] text-sm font-bold">RV</span>
        </div>
      )}

      {!showBackButton && !showLogo && <div className="w-8" />}

      {title && (
        <div className={`text-base font-semibold ${isPrimary ? 'text-white' : 'text-[#1A1A1A]'}`}>
          {title}
        </div>
      )}

      {showLogo && isPrimary && (
        <button className="w-8 h-8 flex items-center justify-center text-white" aria-label="Notificaciones">
          <Bell size={24} />
        </button>
      )}

      {!showLogo && !title && <div className="w-8" />}
      {!showLogo && title && <div className="w-8" />}
    </div>
  );
}
