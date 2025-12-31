/**
 * Sidebar - Cyberpunk command-center style navigation
 */
import { motion } from 'framer-motion';
import { 
  Database, 
  GitCompare, 
  BarChart3, 
  Bot,
  Shield,
  Columns3,
  ChevronRight,
  ChevronLeft,
  FileSpreadsheet
} from 'lucide-react';
import type { FileInfo } from '../../hooks/useApi';

export type NavTab = 'upload' | 'compare' | 'visualize' | 'quality' | 'schema' | 'ai';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  uploadedFiles: string[];
  fileInfos: Record<string, FileInfo>;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const navItems: { id: NavTab; label: string; icon: React.ReactNode; description: string }[] = [
  { id: 'upload', label: 'Data Import', icon: <Database size={20} />, description: 'Upload files' },
  { id: 'compare', label: 'Compare', icon: <GitCompare size={20} />, description: 'Run comparison' },
  { id: 'visualize', label: 'Analytics', icon: <BarChart3 size={20} />, description: 'View charts' },
  { id: 'quality', label: 'Quality', icon: <Shield size={20} />, description: 'Data quality' },
  { id: 'schema', label: 'Schema', icon: <Columns3 size={20} />, description: 'Schema analysis' },
  { id: 'ai', label: 'AI Analysis', icon: <Bot size={20} />, description: 'AI insights' },
];

export function Sidebar({ 
  activeTab, 
  onTabChange, 
  uploadedFiles, 
  fileInfos,
  isCollapsed,
  onToggleCollapse 
}: SidebarProps) {
  return (
    <motion.aside 
      className="relative flex flex-col h-full border-r border-[#2a2a3a] bg-[#0d0d14]"
      animate={{ width: isCollapsed ? 64 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {/* Collapse Toggle */}
      <button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-8 z-20 w-6 h-6 rounded-full bg-[#1a1a24] border border-[#2a2a3a] flex items-center justify-center text-[#888899] hover:text-[#00f5ff] hover:border-[#00f5ff] transition-colors"
      >
        {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>

      {/* Navigation */}
      <nav className="flex-1 py-4 space-y-1 overflow-hidden">
        {navItems.map((item, index) => (
          <motion.button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`
              w-full flex items-center gap-3 px-4 py-3 transition-all duration-300 relative overflow-hidden
              ${activeTab === item.id 
                ? 'text-[#00f5ff]' 
                : 'text-[#888899] hover:text-[#e0e0e0]'
              }
            `}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ x: isCollapsed ? 0 : 4 }}
          >
            {/* Active indicator */}
            {activeTab === item.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-gradient-to-r from-[#00f5ff]/20 to-transparent border-l-2 border-[#00f5ff]"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
              />
            )}
            
            {/* Hover glow effect */}
            <motion.div 
              className="absolute inset-0 bg-[#00f5ff]/5 opacity-0"
              whileHover={{ opacity: 1 }}
            />
            
            <span className={`relative z-10 flex-shrink-0 ${activeTab === item.id ? 'text-[#00f5ff]' : ''}`}>
              {item.icon}
            </span>
            
            {!isCollapsed && (
              <motion.div 
                className="relative z-10 flex flex-col items-start overflow-hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <span 
                  className="font-semibold uppercase tracking-wider text-sm"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  {item.label}
                </span>
                <span className="text-xs text-[#555566]">{item.description}</span>
              </motion.div>
            )}
            
            {!isCollapsed && activeTab === item.id && (
              <ChevronRight size={16} className="ml-auto relative z-10" />
            )}
          </motion.button>
        ))}
      </nav>

      {/* File Summary (when not collapsed) */}
      {!isCollapsed && uploadedFiles.length > 0 && (
        <motion.div 
          className="p-4 border-t border-[#2a2a3a]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <h3 
            className="text-xs uppercase tracking-wider text-[#555566] mb-3"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Loaded Files
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {uploadedFiles.map((file) => {
              const info = fileInfos[file];
              return (
                <div 
                  key={file}
                  className="flex items-center gap-2 p-2 rounded bg-[#12121a] border border-[#2a2a3a]"
                >
                  <FileSpreadsheet size={14} className="text-[#ff0080] flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p 
                      className="text-xs text-[#e0e0e0] truncate"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      {file}
                    </p>
                    {info && (
                      <p className="text-xs text-[#555566]">
                        {(info.rows ?? 0).toLocaleString()} rows • {info.columns ?? 0} cols
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Status Bar */}
      <div className="p-4 border-t border-[#2a2a3a]">
        {isCollapsed ? (
          <div className="flex justify-center">
            <div className="w-2 h-2 rounded-full bg-[#39ff14] animate-pulse" />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#39ff14] animate-pulse" />
            <span className="text-xs text-[#555566]">System Online</span>
          </div>
        )}
      </div>
    </motion.aside>
  );
}

export default Sidebar;

