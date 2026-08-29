import { PageWrapper } from '@/components/layout/PageWrapper';

export function NotFoundPage() {
  return (
    <PageWrapper>
      <div className="flex min-h-screen flex-col items-center justify-center gap-2">
        <h1 className="text-2xl font-semibold">404</h1>
        <p className="text-sm opacity-80">Page not found.</p>
      </div>
    </PageWrapper>
  );
}
