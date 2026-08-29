import { GlassCard } from '@/components/ui/GlassCard';
import { GradientButton } from '@/components/ui/GradientButton';
import { MeshBackground } from '@/components/layout/MeshBackground';
import { PageWrapper } from '@/components/layout/PageWrapper';

export function HomePage() {
  return (
    <PageWrapper>
      <MeshBackground />
      <div className="flex min-h-screen items-center justify-center p-6">
        <GlassCard className="max-w-md text-center">
          <h1 className="text-2xl font-semibold mb-2">Vireel</h1>
          <p className="mb-6 text-sm opacity-80">
            Turn any video into a share-ready trailer.
          </p>
          <GradientButton>Get Started</GradientButton>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
