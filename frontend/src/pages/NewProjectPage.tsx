import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '@/components/layout/PageWrapper';
import { GlassCard } from '@/components/ui/GlassCard';
import { AnimatedInput } from '@/components/ui/AnimatedInput';
import { GradientButton } from '@/components/ui/GradientButton';
import { useCreateProject } from '@/hooks/useProjects';
import { getErrorMessage } from '@/lib/errors';

interface FormErrors {
  sourceUrl?: string;
}

function isValidUrl(value: string): boolean {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

export function NewProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const [sourceUrl, setSourceUrl] = useState('');
  const [title, setTitle] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);

    const nextErrors: FormErrors = {};
    if (!sourceUrl.trim()) {
      nextErrors.sourceUrl = 'A video URL is required';
    } else if (!isValidUrl(sourceUrl.trim())) {
      nextErrors.sourceUrl = 'Enter a valid URL';
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    try {
      const project = await createProject.mutateAsync({
        source_url: sourceUrl.trim(),
        title: title.trim() || undefined,
      });
      navigate(`/projects/${project.id}`);
    } catch (error) {
      setFormError(getErrorMessage(error, 'Unable to create project. Please try again.'));
    }
  };

  return (
    <PageWrapper>
      <div className="mx-auto max-w-lg p-6">
        <h1 className="mb-6 text-2xl font-semibold">New Project</h1>
        <GlassCard>
          <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-4" noValidate>
            <AnimatedInput
              type="url"
              label="Video URL"
              placeholder="https://example.com/video"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              error={errors.sourceUrl}
              disabled={createProject.isPending}
            />
            <AnimatedInput
              type="text"
              label="Title (optional)"
              placeholder="My video"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={createProject.isPending}
            />
            {formError && <p className="text-sm text-red-500">{formError}</p>}
            <GradientButton
              type="submit"
              disabled={createProject.isPending}
              className="disabled:opacity-60"
            >
              {createProject.isPending ? 'Submitting...' : 'Create Project'}
            </GradientButton>
          </form>
        </GlassCard>
      </div>
    </PageWrapper>
  );
}
