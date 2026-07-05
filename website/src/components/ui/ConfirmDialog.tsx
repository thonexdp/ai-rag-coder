import { useState } from 'react';

import { useUiStore } from '../../store/ui.store';
import { Button } from './Button';
import { Modal } from './Modal';

export function ConfirmDialog() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const dialog = useUiStore((state) => state.confirmDialog);
  const closeConfirmDialog = useUiStore((state) => state.closeConfirmDialog);

  const handleConfirm = async () => {
    try {
      setIsSubmitting(true);
      await dialog.onConfirm?.();
      closeConfirmDialog();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      open={dialog.isOpen}
      title={dialog.title}
      onClose={closeConfirmDialog}
      footer={
        <>
          <Button type="button" variant="outline" onClick={closeConfirmDialog}>
            Cancel
          </Button>
          <Button type="button" variant="danger" onClick={handleConfirm} disabled={isSubmitting}>
            {isSubmitting ? 'Working...' : dialog.confirmLabel}
          </Button>
        </>
      }
    >
      <p className="muted-copy">{dialog.description}</p>
    </Modal>
  );
}
