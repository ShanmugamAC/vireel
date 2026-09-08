import { ArrowLeft, Home, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface AppHeaderProps {
  /** Hide the back button on top-level pages (e.g. the dashboard itself). */
  showBack?: boolean;
}

export function AppHeader({ showBack = true }: AppHeaderProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-10 border-b border-white/10 bg-white/5 backdrop-blur-lg">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-1">
          {showBack && (
            <button
              type="button"
              onClick={() => navigate(-1)}
              aria-label="Go back"
              className="rounded-full p-2 opacity-70 transition hover:bg-white/10 hover:opacity-100"
            >
              <ArrowLeft size={18} />
            </button>
          )}
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            aria-label="Go to dashboard"
            className="flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium opacity-70 transition hover:bg-white/10 hover:opacity-100"
          >
            <Home size={18} />
            Home
          </button>
        </div>

        <div className="flex items-center gap-3">
          {user && <span className="hidden text-sm opacity-70 sm:inline">{user.full_name || user.email}</span>}
          <button
            type="button"
            onClick={() => void handleLogout()}
            aria-label="Log out"
            className="flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-medium opacity-70 transition hover:bg-white/10 hover:opacity-100"
          >
            <LogOut size={18} />
            <span className="hidden sm:inline">Log out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
