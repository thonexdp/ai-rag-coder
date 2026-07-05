import { useEffect } from 'react';

import { useUiStore } from '../../store/ui.store';
import { Toast } from './Toast';

export function ToastContainer() {
  const toasts = useUiStore((state) => state.toasts);
  const dismissToast = useUiStore((state) => state.dismissToast);

  useEffect(() => {
    if (!toasts.length) {
      return;
    }
    const timers = toasts.map((toast) => window.setTimeout(() => dismissToast(toast.id), 3000));
    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [dismissToast, toasts]);

  return (
    <div className="toast-stack">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onDismiss={dismissToast} />
      ))}
    </div>
  );
}
