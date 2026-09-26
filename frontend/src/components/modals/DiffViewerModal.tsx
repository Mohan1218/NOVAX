import React, { useState } from 'react';
import { Code2, GitCompare, Copy, Check, X, FileDiff, CheckCircle } from 'lucide-react';

interface DiffViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DiffViewerModal: React.FC<DiffViewerModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'unified' | 'split'>('unified');

  if (!isOpen) return null;

  const diffLines = [
    { type: 'header', text: '--- a/src/services/cart_calculator.py' },
    { type: 'header', text: '+++ b/src/services/cart_calculator.py' },
    { type: 'info', text: '@@ -81,8 +81,11 @@ class CartCalculator:' },
    { type: 'context', text: '     def calculate_discount(self, item: CartItem, tier: DiscountTier) -> Decimal:' },
    { type: 'context', text: '         """Calculates item promotional discount with tier matching."""' },
    { type: 'remove', text: '-        raw_discount = item.price * (tier.discount_percent / 100.0)' },
    { type: 'remove', text: '-        return Decimal(round(raw_discount, 2))' },
    { type: 'add', text: '+        price_decimal = Decimal(str(item.price))' },
    { type: 'add', text: '+        rate_decimal = Decimal(str(tier.discount_percent)) / Decimal("100")' },
    { type: 'add', text: '+        discount_amount = (price_decimal * rate_decimal).quantize(' },
    { type: 'add', text: '+            Decimal("0.01"), rounding=ROUND_HALF_UP' },
    { type: 'add', text: '+        )' },
    { type: 'add', text: '+        return min(discount_amount, price_decimal)' },
    { type: 'context', text: ' ' },
    { type: 'context', text: '     def total(self, items: List[CartItem]) -> Decimal:' },
  ];

  const copyDiff = () => {
    const raw = diffLines.map(d => d.text).join('\n');
    navigator.clipboard.writeText(raw);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-4xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Diff Viewer</h2>
                <span className="text-xs text-rose-400 font-mono">
                  cart_calculator.py (+6 / -2 lines)
                </span>
              </div>
              <p className="text-xs text-slate-400">Compare autonomous code changes against git base branch</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyDiff}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-xs text-slate-300 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Patch'}</span>
            </button>
            <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Diff Code Container */}
        <div className="flex-1 p-5 bg-[#050813] font-mono text-xs overflow-auto select-text leading-relaxed">
          <div className="rounded-xl border border-[#17244a] overflow-hidden">
            {diffLines.map((line, idx) => {
              const isAdd = line.type === 'add';
              const isRemove = line.type === 'remove';
              const isInfo = line.type === 'info';
              const isHeader = line.type === 'header';

              return (
                <div
                  key={idx}
                  className={`flex items-start px-4 py-1 text-[11px] ${
                    isAdd
                      ? 'bg-emerald-950/30 text-emerald-300 border-l-2 border-emerald-400'
                      : isRemove
                      ? 'bg-rose-950/30 text-rose-300 border-l-2 border-rose-500'
                      : isInfo
                      ? 'bg-blue-950/20 text-blue-400 font-semibold'
                      : isHeader
                      ? 'bg-[#0d1633] text-slate-400 font-semibold'
                      : 'text-slate-300 hover:bg-white/[0.02]'
                  }`}
                >
                  <span className="w-8 select-none text-slate-600 font-mono text-[10px]">{idx + 1}</span>
                  <span className="flex-1 whitespace-pre">{line.text}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-emerald-400 font-medium">
            <CheckCircle className="w-4 h-4" />
            <span>Passed AST validation & syntax compilation without warnings</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
};
