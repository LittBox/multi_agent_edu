import "./GlassToast.css";

export type GlassToastType = "info" | "success" | "warning" | "error";

interface GlassToastProps {
  open: boolean;
  title?: string;
  message: string;
  type?: GlassToastType;
  confirmText?: string;
  onClose: () => void;
}

export default function GlassToast({
  open,
  title = "提示",
  message,
  type = "info",
  confirmText = "知道了",
  onClose,
}: GlassToastProps) {
  if (!open) return null;

  return (
    <div className="glass-toast-mask" role="presentation" onClick={onClose}>
      <div
        className={`glass-toast glass-toast-${type}`}
        role="dialog"
        aria-modal="true"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="glass-toast-glow" />

        <div className="glass-toast-header">
          <span className="glass-toast-dot" />
          <h3>{title}</h3>
        </div>

        <p>{message}</p>

        <button type="button" onClick={onClose}>
          {confirmText}
        </button>
      </div>
    </div>
  );
}