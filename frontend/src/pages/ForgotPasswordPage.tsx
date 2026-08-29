import { Link } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { MeshBackground } from '@/components/layout/MeshBackground';
import { PageWrapper } from '@/components/layout/PageWrapper';

export function ForgotPasswordPage() {
  return (
    <PageWrapper>
      <MeshBackground />
      <div className="flex min-h-screen items-center justify-center p-6">
        <GlassCard className="w-full max-w-md text-center">
          <h1 className="mb-2 text-2xl font-semibold">Password reset</h1>
          <p className="mb-6 text-sm opacity-80">
            Self-service password reset isn&apos;t available yet. Please contact support and
            we&apos;ll help you regain access to your account.
          </p>
          <Link to="/login" className="text-sm font-medium text-purple-500 hover:underline">
            Back to sign in
          </Link>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
