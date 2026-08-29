import { Link } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { GlassCard } from '@/components/ui/GlassCard';

export function SettingsPage() {
  return (
    <PageWrapper>
      <div className="mx-auto max-w-lg p-6">
        <h1 className="mb-6 text-2xl font-semibold">Settings</h1>
        <GlassCard>
          <p className="mb-4 text-sm opacity-80">
            Account settings are managed from your profile for now.
          </p>
          <Link to="/profile" className="text-sm font-medium text-purple-500 hover:underline">
            Go to profile
          </Link>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
