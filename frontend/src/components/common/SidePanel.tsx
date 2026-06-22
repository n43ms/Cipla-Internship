import { useEffect, useRef, useState, type ReactNode } from "react";

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

  return (
    <div
      className={`fixed inset-0 z-50 flex justify-end bg-black/55 backdrop-blur-[2px] transition-all duration-[380ms] ease-out ${visible ? "opacity-100" : "pointer-events-none opacity-0"}`}
      role="dialog"
      aria-modal="true"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <aside
        className={`h-full w-full ${widthClass} overflow-y-auto border-l border-[#292d2f] bg-[#111315] p-5 shadow-2xl shadow-black/50 transition-transform duration-[380ms] ease-out ${visible ? "translate-x-0" : "translate-x-full"}`}
      >
        {retainedChildren.current}
      </aside>
    </div>
  );
}
