import { Link } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { MeshBackground } from '@/components/layout/MeshBackground';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { RegisterForm } from '@/components/auth/RegisterForm';

export function RegisterPage() {
  return (
    <PageWrapper>
      <MeshBackground />
      <div className="flex min-h-screen items-center justify-center p-6">
        <GlassCard className="w-full max-w-md">
          <h1 className="mb-1 text-2xl font-semibold">Create your account</h1>
          <p className="mb-6 text-sm opacity-80">
            Turn any video into a share-ready trailer.
          </p>
          <RegisterForm />
          <p className="mt-6 text-center text-sm opacity-80">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-purple-500 hover:underline">
              Sign in
            </Link>
          </p>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
