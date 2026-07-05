import type { PropsWithChildren } from 'react';

type BadgeTone = 'admin' | 'faculty' | 'student' | 'success' | 'danger' | 'warning' | 'neutral';

interface BadgeProps {
  tone?: BadgeTone;
}

export function Badge({ children, tone = 'neutral' }: PropsWithChildren<BadgeProps>) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
