import { Link } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { MeshBackground } from '@/components/layout/MeshBackground';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { LoginForm } from '@/components/auth/LoginForm';

export function LoginPage() {
  return (
    <PageWrapper>
      <MeshBackground />
      <div className="flex min-h-screen items-center justify-center p-6">
        <GlassCard className="w-full max-w-md">
          <h1 className="mb-1 text-2xl font-semibold">Welcome back</h1>
          <p className="mb-6 text-sm opacity-80">Sign in to continue to Vireel.</p>
          <LoginForm />
          <p className="mt-6 text-center text-sm opacity-80">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-medium text-purple-500 hover:underline">
              Sign up
            </Link>
          </p>
          <p className="mt-2 text-center text-sm opacity-80">
            <Link to="/forgot-password" className="font-medium text-purple-500 hover:underline">
              Forgot password?
            </Link>
          </p>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
