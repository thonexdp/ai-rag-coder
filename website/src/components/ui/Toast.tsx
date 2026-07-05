import type { ToastItem } from '../../store/ui.store';

interface ToastProps {
  toast: ToastItem;
  onDismiss: (id: string) => void;
}

export function Toast({ onDismiss, toast }: ToastProps) {
  return (
    <button className={`toast-item ${toast.tone}`} onClick={() => onDismiss(toast.id)} type="button">
      {toast.title}
    </button>
  );
}
