import { useState, type FormEvent } from 'react';
import { GlassCard } from '@/components/ui/GlassCard';
import { AnimatedInput } from '@/components/ui/AnimatedInput';
import { GradientButton } from '@/components/ui/GradientButton';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { useAuth } from '@/hooks/useAuth';
import { authService } from '@/services/authService';
import { getErrorMessage } from '@/lib/errors';

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(false);
    setIsSubmitting(true);
    try {
      await authService.updateMe({ full_name: fullName.trim() || undefined });
      await refreshUser();
      setSuccess(true);
    } catch (err) {
      setError(getErrorMessage(err, 'Unable to update your profile. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) return null;

  return (
    <PageWrapper>
      <div className="mx-auto max-w-lg p-6">
        <h1 className="mb-6 text-2xl font-semibold">Profile</h1>
        <GlassCard>
          <dl className="mb-6 space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="opacity-70">Email</dt>
              <dd>{user.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="opacity-70">Verified</dt>
              <dd>{user.is_verified ? 'Yes' : 'No'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="opacity-70">Member since</dt>
              <dd>{new Date(user.created_at).toLocaleDateString()}</dd>
            </div>
          </dl>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <AnimatedInput
              type="text"
              label="Full name"
              placeholder="Jane Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={isSubmitting}
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
            {success && <p className="text-sm text-green-500">Profile updated.</p>}
            <GradientButton type="submit" disabled={isSubmitting} className="disabled:opacity-60">
              {isSubmitting ? 'Saving...' : 'Save changes'}
            </GradientButton>
          </form>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
