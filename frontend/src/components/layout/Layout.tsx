import { ReactNode } from 'react';
import { Header } from './Header';
import { BottomNavigation } from './BottomNavigation';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  showBackButton?: boolean;
  showLogo?: boolean;
  onBackClick?: () => void;
  showBottomNav?: boolean;
}

export function Layout({
  children,
  title,
  showBackButton = false,
  showLogo = false,
  onBackClick,
  showBottomNav = true,
}: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-start py-10">
      <div className="w-[375px] min-h-[812px] bg-white border border-gray-300 flex flex-col relative">
        <Header
          title={title}
          showBackButton={showBackButton}
          showLogo={showLogo}
          onBackClick={onBackClick}
        />
        
        <div className="flex-1 p-5 bg-[#F8F9FA] overflow-y-auto">
          {children}
        </div>

        {showBottomNav && <BottomNavigation />}
      </div>
    </div>
  );
}
