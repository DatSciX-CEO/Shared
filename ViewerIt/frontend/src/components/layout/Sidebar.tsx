/**
 * Sidebar - Cyberpunk command-center style navigation
 * Enhanced with professional hover effects and RGB-split styling
 */
import { useState } from 'react';
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
  FileSpreadsheet,
  Activity
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

const navItems: { id: NavTab; label: string; icon: React.ReactNode; description: string; accentColor: string }[] = [
  { id: 'upload', label: 'Data Import', icon: <Database size={18} />, description: 'Upload files', accentColor: '#00f5ff' },
  { id: 'compare', label: 'Compare', icon: <GitCompare size={18} />, description: 'Run comparison', accentColor: '#ff00ff' },
  { id: 'visualize', label: 'Analytics', icon: <BarChart3 size={18} />, description: 'View charts', accentColor: '#f0ff00' },
  { id: 'quality', label: 'Quality', icon: <Shield size={18} />, description: 'Data quality', accentColor: '#39ff14' },
  { id: 'schema', label: 'Schema', icon: <Columns3 size={18} />, description: 'Schema analysis', accentColor: '#ff6600' },
  { id: 'ai', label: 'AI Analysis', icon: <Bot size={18} />, description: 'AI insights', accentColor: '#ff0080' },
];

export function Sidebar({ 
  activeTab, 
  onTabChange, 
  uploadedFiles, 
  fileInfos,
  isCollapsed,
  onToggleCollapse 
}: SidebarProps) {
  const [hoveredItem, setHoveredItem] = useState<NavTab | null>(null);

  return (
    <motion.aside 
      className="relative flex flex-col h-full border-r border-[#2a2a3a] bg-[#0d0d14]"
      animate={{ width: isCollapsed ? 64 : 260 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
    >
      {/* Collapse Toggle with glow */}
      <motion.button
        onClick={onToggleCollapse}
        className="absolute -right-3 top-8 z-20 w-6 h-6 rounded-full bg-[#1a1a24] border border-[#2a2a3a] flex items-center justify-center text-[#9999aa] hover:text-[#00f5ff] hover:border-[#00f5ff] transition-colors"
        whileHover={{ boxShadow: '0 0 10px rgba(0, 245, 255, 0.4)' }}
      >
        {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </motion.button>

      {/* Navigation */}
      <nav className="flex-1 py-4 space-y-1 overflow-hidden">
        {navItems.map((item, index) => {
          const isActive = activeTab === item.id;
          const isHovered = hoveredItem === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              onHoverStart={() => setHoveredItem(item.id)}
              onHoverEnd={() => setHoveredItem(null)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 transition-all duration-300 relative overflow-hidden
                ${isActive ? 'text-[#00f5ff]' : 'text-[#9999aa]'}
              `}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ x: isCollapsed ? 0 : 4 }}
            >
              {/* Active indicator with accent color */}
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 border-l-2"
                  style={{ 
                    background: `linear-gradient(90deg, ${item.accentColor}20, transparent)`,
                    borderColor: item.accentColor,
                  }}
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                />
              )}
              
              {/* Hover glow effect with RGB split */}
              {isHovered && !isActive && (
                <motion.div 
                  className="absolute inset-0"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{ background: `linear-gradient(90deg, ${item.accentColor}10, transparent)` }}
                />
              )}
              
              {/* Icon with glow on active/hover */}
              <motion.span 
                className="relative z-10 flex-shrink-0"
                style={{ 
                  color: isActive ? item.accentColor : isHovered ? '#e8e8e8' : '#9999aa',
                  filter: isActive ? `drop-shadow(0 0 6px ${item.accentColor})` : 'none'
                }}
                animate={isHovered && !isActive ? {
                  textShadow: [
                    'none',
                    `-1px 0 #00f5ff, 1px 0 #ff0080`,
                    'none'
                  ]
                } : {}}
                transition={{ duration: 0.2 }}
              >
                {item.icon}
              </motion.span>
              
              {!isCollapsed && (
                <motion.div 
                  className="relative z-10 flex flex-col items-start overflow-hidden"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <span 
                    className="font-semibold uppercase tracking-wider text-sm"
                    style={{ 
                      fontFamily: 'Rajdhani, sans-serif',
                      color: isActive ? item.accentColor : isHovered ? '#e8e8e8' : 'inherit'
                    }}
                  >
                    {item.label}
                  </span>
                  <span 
                    className="text-xs"
                    style={{ color: '#6a6a7a' }}
                  >
                    {item.description}
                  </span>
                </motion.div>
              )}
              
              {!isCollapsed && isActive && (
                <motion.div
                  className="ml-auto relative z-10"
                  animate={{ x: [0, 3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ChevronRight size={16} style={{ color: item.accentColor }} />
                </motion.div>
              )}
            </motion.button>
          );
        })}
      </nav>

      {/* File Summary (when not collapsed) */}
      {!isCollapsed && uploadedFiles.length > 0 && (
        <motion.div 
          className="p-4 border-t border-[#2a2a3a]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <h3 
            className="text-xs uppercase tracking-wider text-[#6a6a7a] mb-3 flex items-center gap-2"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            <Activity size={10} className="text-[#39ff14]" />
            Loaded Files
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {uploadedFiles.map((file, index) => {
              const info = fileInfos[file];
              return (
                <motion.div 
                  key={file}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-2 p-2 rounded bg-[#12121a] border border-[#2a2a3a] hover:border-[#ff0080]/40 transition-colors"
                >
                  <FileSpreadsheet size={14} className="text-[#ff0080] flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p 
                      className="text-xs text-[#e8e8e8] truncate"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      {file}
                    </p>
                    {info && (
                      <p className="text-xs text-[#6a6a7a]">
                        {(info.rows ?? 0).toLocaleString()} rows • {info.columns ?? 0} cols
                      </p>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Status Bar */}
      <div className="p-4 border-t border-[#2a2a3a]">
        {isCollapsed ? (
          <div className="flex justify-center">
            <motion.div 
              className="w-2 h-2 rounded-full bg-[#39ff14]"
              animate={{ 
                opacity: [1, 0.5, 1],
                boxShadow: ['0 0 5px #39ff14', '0 0 10px #39ff14', '0 0 5px #39ff14']
              }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <motion.div 
              className="w-2 h-2 rounded-full bg-[#39ff14]"
              animate={{ 
                opacity: [1, 0.5, 1],
                boxShadow: ['0 0 5px #39ff14', '0 0 10px #39ff14', '0 0 5px #39ff14']
              }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="text-xs text-[#6a6a7a]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              System Online
            </span>
          </div>
        )}
      </div>
    </motion.aside>
  );
}

export default Sidebar;

