import { useUiStore } from '../store/ui.store';

export function useToast() {
  const pushToast = useUiStore((state) => state.pushToast);

  return {
    toast: (title: string, tone: 'success' | 'error' | 'info' = 'info') => pushToast({ title, tone }),
  };
}
