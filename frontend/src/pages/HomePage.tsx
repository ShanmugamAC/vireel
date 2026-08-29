import { Navigate, useNavigate } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { MeshBackground } from '@/components/layout/MeshBackground';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { useAuth } from '@/hooks/useAuth';

export function HomePage() {
  const navigate = useNavigate();
  const { user, isLoading } = useAuth();

  if (!isLoading && user) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <PageWrapper>
      <MeshBackground />
      <div className="flex min-h-screen items-center justify-center p-6">
        <GlassCard className="max-w-md text-center">
          <h1 className="text-2xl font-semibold mb-2">Vireel</h1>
          <p className="mb-6 text-sm opacity-80">
            Turn any video into a share-ready trailer.
          </p>
          <GradientButton onClick={() => navigate('/register')}>Get Started</GradientButton>
          <p className="mt-4 text-sm opacity-80">
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="underline underline-offset-2 hover:opacity-100"
            >
              Log in
            </button>
          </p>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
