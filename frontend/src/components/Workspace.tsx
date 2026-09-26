import React, { useState, useRef } from 'react';
import { 
  Sparkles, 
  Paperclip, 
  Folder, 
  Play, 
  ChevronDown, 
  Code, 
  Plus, 
  CheckCircle2, 
  X, 
  FileCode,
  Loader2,
  Check
} from 'lucide-react';
import { Language, AttachedFile, Repository } from '../types';
import { QUICK_EXAMPLES } from '../data/mockData';
import { RobotHero } from './RobotHero';

interface WorkspaceProps {
  prompt: string;
  setPrompt: (value: string) => void;
  attachedFiles: AttachedFile[];
  onAddFiles: (files: FileList | null) => void;
  onRemoveFile: (fileId: string) => void;
  selectedRepo: Repository | null;
  onOpenRepoPicker: () => void;
  onRemoveRepo: () => void;
  selectedLanguage: Language;
  onSelectLanguage: (lang: Language) => void;
  onStartWorking: () => void;
  isConnecting: boolean;
}

export const Workspace: React.FC<WorkspaceProps> = ({
  prompt,
  setPrompt,
  attachedFiles,
  onAddFiles,
  onRemoveFile,
  selectedRepo,
  onOpenRepoPicker,
  onRemoveRepo,
  selectedLanguage,
  onSelectLanguage,
  onStartWorking,
  isConnecting
}) => {
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const languages: Language[] = ['Python', 'TypeScript', 'JavaScript', 'Go', 'Rust', 'Java', 'C++'];

  const handleExampleClick = (examplePrompt: string, lang: Language) => {
    setPrompt(examplePrompt);
    onSelectLanguage(lang);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onAddFiles(e.target.files);
    if (e.target) e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onAddFiles(e.dataTransfer.files);
    }
  };

  return (
    <main className="flex-1 flex flex-col items-center justify-between p-6 lg:p-8 max-w-5xl mx-auto w-full overflow-y-auto">
      <div className="w-full">
        {/* Welcome Heading matching screenshot */}
        <div className="mb-6">
          <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400">NOVAX</span>
          </h1>
          <p className="mt-2 text-sm lg:text-base text-slate-400 font-normal">
            Describe your issue or upload your repository. I'll handle the rest — analyze, debug, fix and verify.
          </p>
        </div>

        {/* Main Task Input Card with Glowing Border */}
        <div 
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`w-full rounded-2xl bg-[#0c142b]/95 border transition-all duration-300 shadow-xl ${
            isDragOver 
              ? 'border-blue-400 ring-2 ring-blue-500/30 bg-[#0f1a3a]' 
              : 'border-[#1b2b54] focus-within:border-blue-500 focus-within:shadow-[0_0_30px_rgba(59,130,246,0.22)]'
          }`}
        >
          {/* Top text input area */}
          <div className="p-4 lg:p-5 flex items-start gap-3">
            {/* Sparkle Icon */}
            <div className="mt-1 text-blue-400 flex-shrink-0">
              <Sparkles className="w-5 h-5 drop-shadow-[0_0_8px_#38bdf8]" />
            </div>

            <div className="flex-1 w-full">
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Type your bug report, issue or task here..."
                rows={3}
                className="w-full bg-transparent border-0 resize-none text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-0 text-sm lg:text-base leading-relaxed"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    onStartWorking();
                  }
                }}
              />

              {/* Attached Files & Selected Repository Preview Chips */}
              {(attachedFiles.length > 0 || selectedRepo) && (
                <div className="flex flex-wrap gap-2 mt-2 pt-2 border-t border-[#172344]">
                  {selectedRepo && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-950/60 border border-blue-500/40 text-xs text-blue-200">
                      <Folder className="w-3.5 h-3.5 text-blue-400" />
                      <span className="font-mono">{selectedRepo.name}</span>
                      <span className="text-slate-400">({selectedRepo.branch})</span>
                      <button 
                        onClick={onRemoveRepo} 
                        className="p-0.5 hover:text-white text-slate-400 rounded transition-colors"
                        title="Remove repository"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  )}

                  {attachedFiles.map(file => (
                    <div key={file.id} className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#142042] border border-[#233566] text-xs text-slate-300">
                      <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="truncate max-w-[140px] font-mono">{file.name}</span>
                      <span className="text-[10px] text-slate-400">({(file.size / 1024).toFixed(0)}KB)</span>
                      <button 
                        onClick={() => onRemoveFile(file.id)}
                        className="p-0.5 hover:text-white text-slate-400 rounded transition-colors"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Bottom Toolbar inside the box */}
          <div className="px-4 lg:px-5 py-3 border-t border-[#162348] bg-[#091024]/70 rounded-b-2xl flex flex-wrap items-center justify-between gap-3">
            {/* Left Controls: Attach Files & Select Repository */}
            <div className="flex items-center gap-2.5 flex-wrap">
              {/* Hidden file input */}
              <input 
                ref={fileInputRef} 
                type="file" 
                multiple 
                className="hidden" 
                onChange={handleFileChange} 
              />

              {/* Attach Files Button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#111a36] hover:bg-[#162349] border border-[#1e2f5d] text-xs font-medium text-slate-300 hover:text-white transition-all shadow-sm"
              >
                <Paperclip className="w-3.5 h-3.5 text-slate-400" />
                <span>Attach Files</span>
              </button>

              {/* Select Repository Button */}
              <button
                type="button"
                onClick={onOpenRepoPicker}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#111a36] hover:bg-[#162349] border border-[#1e2f5d] text-xs font-medium text-slate-300 hover:text-white transition-all shadow-sm"
              >
                <Folder className="w-3.5 h-3.5 text-slate-400" />
                <span>Select Repository</span>
              </button>
            </div>

            {/* Right Controls: Language Dropdown + Start Working Button */}
            <div className="flex items-center gap-3">
              {/* Language Dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowLangDropdown(!showLangDropdown)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#111a36] hover:bg-[#162349] border border-[#1e2f5d] text-xs font-medium text-slate-300 hover:text-white transition-all"
                >
                  {/* Language icon */}
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block shadow-[0_0_6px_#f59e0b]" />
                  <span>{selectedLanguage}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {showLangDropdown && (
                  <div className="absolute right-0 bottom-full mb-2 w-36 rounded-xl bg-[#0f1938] border border-[#233566] shadow-2xl p-1 z-40 animate-in fade-in duration-100">
                    {languages.map((lang) => (
                      <button
                        key={lang}
                        onClick={() => {
                          onSelectLanguage(lang);
                          setShowLangDropdown(false);
                        }}
                        className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                          selectedLanguage === lang 
                            ? 'bg-blue-600/30 text-blue-300 font-semibold' 
                            : 'text-slate-300 hover:bg-[#16244d] hover:text-white'
                        }`}
                      >
                        <span>{lang}</span>
                        {selectedLanguage === lang && <Check className="w-3 h-3 text-blue-400" />}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Start Working Button matching screenshot */}
              <button
                type="button"
                onClick={onStartWorking}
                disabled={isConnecting}
                className="flex items-center gap-2.5 px-5 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-500 hover:to-indigo-500 shadow-[0_0_20px_rgba(59,130,246,0.35)] transition-all transform active:scale-95 disabled:opacity-75 disabled:pointer-events-none"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Connecting...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-white text-white" />
                    <span>Start Working</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* "Or try a quick example:" section */}
        <div className="mt-5">
          <p className="text-xs text-slate-400 mb-2.5 font-normal">
            Or try a quick example:
          </p>

          <div className="flex flex-wrap items-center gap-2">
            {QUICK_EXAMPLES.map((example) => (
              <button
                key={example.id}
                onClick={() => handleExampleClick(example.prompt, example.language)}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#0c142b] hover:bg-[#131f42] border border-[#1b2a52] hover:border-blue-500/40 text-xs text-slate-300 hover:text-white transition-all shadow-sm"
              >
                {/* Specific Icons matching the screenshot */}
                {example.id === 'ex-1' && <Code className="w-3.5 h-3.5 text-blue-400" />}
                {example.id === 'ex-2' && <Folder className="w-3.5 h-3.5 text-blue-400" />}
                {example.id === 'ex-3' && <Plus className="w-3.5 h-3.5 text-blue-400" />}
                {example.id === 'ex-4' && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />}
                <span>{example.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Robot Hero Avatar at the Center bottom */}
      <RobotHero />
    </main>
  );
};
