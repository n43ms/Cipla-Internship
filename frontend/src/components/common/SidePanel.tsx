import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

type SidePanelProps = {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  widthClass?: string;
};

const EXIT_DURATION_MS = 380;

export function SidePanel({ open, onClose, children, widthClass = "max-w-xl" }: SidePanelProps) {
  const [mounted, setMounted] = useState(open);
  const [visible, setVisible] = useState(false);
  const retainedChildren = useRef(children);

  if (open && children) retainedChildren.current = children;

  useEffect(() => {
    if (open) {
      setMounted(true);
      const frame = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(frame);
    }
    setVisible(false);
    const timer = window.setTimeout(() => setMounted(false), EXIT_DURATION_MS);
    return () => window.clearTimeout(timer);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose, open]);

  if (!mounted) return null;

  return createPortal(
    <div
      className={`fixed inset-0 z-50 flex items-stretch justify-end overflow-hidden bg-black/55 backdrop-blur-[2px] transition-all duration-[380ms] ease-out ${visible ? "opacity-100" : "pointer-events-none opacity-0"}`}
      role="dialog"
      aria-modal="true"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <aside
        className={`h-dvh w-full min-w-0 max-w-[calc(100vw-1rem)] ${widthClass} overflow-y-auto overflow-x-hidden border-l border-[#292d2f] bg-[#111315] p-4 shadow-2xl shadow-black/50 outline-none transition-transform duration-[380ms] ease-out will-change-transform sm:p-5 ${visible ? "translate-x-0" : "translate-x-full"}`}
      >
        {retainedChildren.current}
      </aside>
    </div>,
    document.body,
  );
}
