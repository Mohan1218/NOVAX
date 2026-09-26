import React, { useState } from 'react';
import { Folder, FileCode, ChevronRight, ChevronDown, Search, X, GitBranch, Copy, Check } from 'lucide-react';

interface RepositoryExplorerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RepositoryExplorerModal: React.FC<RepositoryExplorerModalProps> = ({ isOpen, onClose }) => {
  const [selectedFile, setSelectedFile] = useState<string>('cart_calculator.py');
  const [copied, setCopied] = useState(false);
  const [search, setSearch] = useState('');

  const filesMap: Record<string, { lang: string; content: string }> = {
    'cart_calculator.py': {
      lang: 'python',
      content: `from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict
from models.order import CartItem, DiscountTier

class CartCalculator:
    """Calculates cart totals, promotional discount tiers, and taxes."""
    
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self.rounding = ROUND_HALF_UP

    def calculate_discount(self, item: CartItem, tier: DiscountTier) -> Decimal:
        """
        Calculates item discount with precision decimal quantization
        avoiding IEEE-754 binary floating point precision leakage.
        """
        price = Decimal(str(item.price))
        rate = Decimal(str(tier.discount_percent)) / Decimal("100")
        
        discount_amount = (price * rate).quantize(Decimal("0.01"), rounding=self.rounding)
        return min(discount_amount, price)

    def total(self, items: List[CartItem]) -> Decimal:
        subtotal = sum(Decimal(str(i.price)) * i.quantity for i in items)
        return subtotal.quantize(Decimal("0.01"))`
    },
    'test_discounts.py': {
      lang: 'python',
      content: `import pytest
from decimal import Decimal
from services.cart_calculator import CartCalculator
from models.order import CartItem, DiscountTier

def test_tier_precision_rounding():
    calc = CartCalculator()
    item = CartItem(id="SKU-894", name="Enterprise license", price=84.99, quantity=1)
    tier = DiscountTier(name="VIP Partner", discount_percent=15.0)

    discount = calc.calculate_discount(item, tier)
    assert discount == Decimal("12.75")
    print("Assertion passed: Decimal arithmetic exact.")`
    },
    'auth.py': {
      lang: 'python',
      content: `import jwt
from datetime import datetime, timedelta

SECRET_KEY = "novax-secure-cluster-key"

def verify_session_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("Session token expired.")`
    },
    'README.md': {
      lang: 'markdown',
      content: `# ecommerce-engine
High-throughput headless e-commerce pricing and order fulfillment engine.

## Autonomous Verification
Verified by NOVAX Autonomous Software Engineer.
- Python 3.12+
- PyTest Suite: 48 passing
- Strict Typing: Enabled (mypy)`
    }
  };

  if (!isOpen) return null;

  const currentFileData = filesMap[selectedFile] || filesMap['cart_calculator.py'];

  const copyCode = () => {
    navigator.clipboard.writeText(currentFileData.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-5xl h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Folder className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Repository Explorer</h2>
                <span className="text-xs text-cyan-400 font-mono flex items-center gap-1">
                  <GitBranch className="w-3.5 h-3.5" /> ecommerce-engine (main)
                </span>
              </div>
              <p className="text-xs text-slate-400">Browse directory structure, symbol references, and verified source files</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Workspace Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: File Tree */}
          <div className="w-64 border-r border-[#17254d] bg-[#070c1e] flex flex-col">
            <div className="p-3 border-b border-[#17254d]">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter files..."
                  className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-[#0e1733] border border-[#1b2b52] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="p-2 space-y-1 overflow-y-auto flex-1 text-xs font-mono">
              <div className="text-slate-400 px-2 py-1 text-[11px] font-sans font-semibold uppercase tracking-wider">
                Source Files
              </div>
              
              {Object.keys(filesMap).map((fileName) => {
                const isActive = selectedFile === fileName;
                return (
                  <button
                    key={fileName}
                    onClick={() => setSelectedFile(fileName)}
                    className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left transition-colors ${
                      isActive 
                        ? 'bg-blue-600/30 text-cyan-300 font-semibold border border-blue-500/30' 
                        : 'text-slate-300 hover:bg-[#101b38] hover:text-white'
                    }`}
                  >
                    <FileCode className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                    <span className="truncate">{fileName}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Code Viewer */}
          <div className="flex-1 flex flex-col bg-[#050813] overflow-hidden">
            <div className="p-3 px-5 border-b border-[#17254d] bg-[#090f23] flex items-center justify-between">
              <span className="font-mono text-xs text-slate-200 flex items-center gap-2">
                <FileCode className="w-4 h-4 text-cyan-400" />
                {selectedFile}
              </span>

              <button
                onClick={copyCode}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-xs text-slate-300 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy Code'}</span>
              </button>
            </div>

            <div className="flex-1 p-5 overflow-auto font-mono text-xs text-slate-200 leading-relaxed select-text">
              <pre className="text-slate-300">{currentFileData.content}</pre>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 px-6 bg-[#0d1633] border-t border-[#17254d] flex justify-between items-center text-xs">
          <span className="text-slate-400 font-mono">Status: Synced with local repository clone</span>
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium">
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
