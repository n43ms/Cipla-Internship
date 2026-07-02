import { Check, ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

export type SelectOption = { value: string; label: string };

type SmoothSelectProps = {
  ariaLabel: string;
  value: string;
  options: SelectOption[];
  placeholder: string;
  onChange: (value: string) => void;
  className?: string;
};

export function SmoothSelect({ ariaLabel, value, options, placeholder, onChange, className = "" }: SmoothSelectProps) {
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);
  const listboxId = useId();
  const selected = options.find((option) => option.value === value);
  const allOptions = [{ value: "", label: placeholder }, ...options];

  useEffect(() => {
    function handleOutside(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("pointerdown", handleOutside);
    return () => document.removeEventListener("pointerdown", handleOutside);
  }, []);

  function openMenu() {
    const selectedIndex = allOptions.findIndex((option) => option.value === value);
    setActiveIndex(Math.max(0, selectedIndex));
    setOpen(true);
  }

  function selectOption(option: SelectOption) {
    onChange(option.value);
    setOpen(false);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLButtonElement>) {
    if (event.key === "Escape") {
      setOpen(false);
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (!open) return openMenu();
      const direction = event.key === "ArrowDown" ? 1 : -1;
      setActiveIndex((current) => (current + direction + allOptions.length) % allOptions.length);
      return;
    }
    if ((event.key === "Enter" || event.key === " ") && open) {
      event.preventDefault();
      selectOption(allOptions[activeIndex]);
    }
  }

  return (
    <div ref={rootRef} className={`relative ${className}`}>
      <select className="sr-only" aria-label={ariaLabel} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{placeholder}</option>
        {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select>
      <button
        type="button"
        className={`form-control flex w-full items-center justify-between gap-3 text-left ${open ? "border-accent/70 ring-2 ring-accent/10" : ""}`}
        aria-expanded={open}
        aria-label={`${ariaLabel}: ${selected?.label ?? placeholder}`}
        aria-haspopup="listbox"
        aria-controls={listboxId}
        onClick={() => (open ? setOpen(false) : openMenu())}
        onKeyDown={handleKeyDown}
      >
        <span className={selected ? "text-zinc-200" : "text-zinc-500"}>{selected?.label ?? placeholder}</span>
        <ChevronDown aria-hidden="true" className={`h-4 w-4 shrink-0 text-zinc-500 transition-transform duration-300 ${open ? "rotate-180 text-accent" : ""}`} />
      </button>
      <div
        id={listboxId}
        role="listbox"
        aria-hidden={!open}
        className={`absolute left-0 right-0 z-30 mt-2 max-h-64 origin-top overflow-y-auto rounded-md border border-[#303437] bg-[#17191b]/98 p-1.5 shadow-2xl shadow-black/45 backdrop-blur-xl transition-all duration-300 ease-out ${
          open ? "visible translate-y-0 scale-100 opacity-100" : "invisible -translate-y-1 scale-[0.985] opacity-0"
        }`}
      >
        {allOptions.map((option, index) => {
          const isSelected = option.value === value;
          const isActive = index === activeIndex;
          return (
            <button
              key={`${option.value}-${option.label}`}
              type="button"
              role="option"
              aria-selected={isSelected}
              tabIndex={open ? 0 : -1}
              className={`flex w-full items-center justify-between gap-3 rounded px-3 py-2 text-left text-sm transition-colors duration-200 ${
                isActive ? "bg-white/[0.06] text-zinc-100" : "text-zinc-400 hover:bg-white/[0.045] hover:text-zinc-200"
              }`}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => selectOption(option)}
            >
              <span>{option.label}</span>
              <Check className={`h-4 w-4 text-accent transition-opacity duration-200 ${isSelected ? "opacity-80" : "opacity-0"}`} aria-hidden="true" />
            </button>
          );
        })}
      </div>
    </div>
  );
}
