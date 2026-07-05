import { create } from 'zustand';

export interface ToastItem {
  id: string;
  title: string;
  tone: 'success' | 'error' | 'info';
}

interface ConfirmDialogState {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  onConfirm?: () => void | Promise<void>;
}

interface UiState {
  toasts: ToastItem[];
  confirmDialog: ConfirmDialogState;
  pushToast: (toast: Omit<ToastItem, 'id'>) => void;
  dismissToast: (id: string) => void;
  openConfirmDialog: (dialog: Omit<ConfirmDialogState, 'isOpen'>) => void;
  closeConfirmDialog: () => void;
}

const initialConfirmDialog: ConfirmDialogState = {
  isOpen: false,
  title: '',
  description: '',
  confirmLabel: 'Confirm',
};

export const useUiStore = create<UiState>((set) => ({
  toasts: [],
  confirmDialog: initialConfirmDialog,
  pushToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id: crypto.randomUUID() }],
    })),
  dismissToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    })),
  openConfirmDialog: (dialog) =>
    set({
      confirmDialog: {
        isOpen: true,
        title: dialog.title,
        description: dialog.description,
        confirmLabel: dialog.confirmLabel,
        onConfirm: dialog.onConfirm,
      },
    }),
  closeConfirmDialog: () => set({ confirmDialog: initialConfirmDialog }),
}));
