import { useEffect, useState } from 'react';
import { Sparkles, X } from 'lucide-react';

const FUN_FACTS = [
  { emoji: '🥕', text: 'Carrots were originally grown in purple, yellow, and red—not orange!' },
  { emoji: '🍌', text: 'Bananas are berries, while strawberries are not—botany is full of surprises.' },
  { emoji: '🫑', text: 'Bell peppers can contain more vitamin C than an orange.' },
  { emoji: '🍅', text: 'Cooking tomatoes makes lycopene easier for your body to absorb.' },
  { emoji: '🥬', text: 'A handful of leafy greens adds fibre and colour to almost any meal.' },
  { emoji: '🫘', text: 'Beans are a budget-friendly source of both protein and fibre.' },
  { emoji: '🌶️', text: 'Chilli heat comes from capsaicin, which is concentrated around the seeds.' },
];

export default function FunFactPopup() {
  const [visible, setVisible] = useState(true);
  const [closing, setClosing] = useState(false);
  const [factIndex, setFactIndex] = useState(() => Math.floor(Math.random() * FUN_FACTS.length));
  const fact = FUN_FACTS[factIndex];

  useEffect(() => {
    if (!visible) return undefined;
    const factTimer = window.setInterval(() => {
      setFactIndex((current) => (current + 1 + Math.floor(Math.random() * (FUN_FACTS.length - 1))) % FUN_FACTS.length);
    }, 7000);
    return () => window.clearInterval(factTimer);
  }, [visible]);

  const close = (e) => {
    e?.stopPropagation();
    setClosing(true);
    setTimeout(() => {
      setVisible(false);
    }, 200);
  };

  if (!visible) return null;

  return (
    <aside
      className={`fun-fact-popup fixed right-4 top-24 z-40 w-[min(19rem,calc(100vw-2rem))] transition-all duration-200 ${
        closing ? 'opacity-0 scale-90 translate-y-2 pointer-events-none' : 'fun-fact-enter'
      }`}
      aria-label="Fun nutrition fact"
    >
      <div className="relative overflow-hidden rounded-2xl border border-amber-300/25 bg-slate-900/95 p-4 pr-11 shadow-2xl shadow-amber-500/10 backdrop-blur-xl">
        <div className="fun-fact-orb absolute -right-6 -top-7 h-20 w-20 rounded-full bg-amber-400/15" />
        <button
          type="button"
          onClick={close}
          aria-label="Hide fun fact"
          className="absolute right-2.5 top-2.5 rounded-lg p-1.5 text-slate-400 transition-all hover:bg-rose-500/20 hover:text-rose-300 focus:outline-none focus:ring-2 focus:ring-amber-300 z-50 cursor-pointer"
        >
          <X className="h-4 w-4" />
        </button>
        <div key={factIndex} className="fun-fact-content relative flex gap-3">
          <span className="fun-fact-emoji grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-amber-400/15 text-xl">{fact.emoji}</span>
          <div>
            <p className="mb-1 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-amber-300">
              <Sparkles className="h-3.5 w-3.5" /> Fun food fact
            </p>
            <p className="text-xs leading-5 text-slate-200">{fact.text}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
