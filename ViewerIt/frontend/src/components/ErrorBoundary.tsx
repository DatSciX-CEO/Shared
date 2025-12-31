/**
 * ErrorBoundary - Catches React rendering errors and displays a fallback UI
 * Prevents blank screens when components crash
 */
import { Component, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: string | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error: Error): State {

    return { 
      hasError: true, 
      error,
      errorInfo: error.stack || null
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {

    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      errorInfo: errorInfo.componentStack || error.stack || null
    });
  }

  handleReset = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default cyberpunk-themed error UI
      return (
        <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-6">
          <div className="max-w-lg w-full">
            {/* Error Card */}
            <div className="bg-[#12121a] border border-[#ff0080] rounded-lg p-6 shadow-[0_0_30px_rgba(255,0,128,0.2)]">
              {/* Header */}
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-lg bg-[#ff0080]/20 flex items-center justify-center">
                  <AlertTriangle size={24} className="text-[#ff0080]" />
                </div>
                <div>
                  <h2 
                    className="text-xl font-bold text-[#ff0080]"
                    style={{ fontFamily: 'Orbitron, monospace' }}
                  >
                    SYSTEM ERROR
                  </h2>
                  <p className="text-sm text-[#888899]">
                    Something went wrong
                  </p>
                </div>
              </div>

              {/* Error Message */}
              <div className="mb-4 p-3 bg-[#0a0a0f] rounded border border-[#2a2a3a]">
                <p 
                  className="text-sm text-[#ff6b6b] break-words"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
              </div>

              {/* Stack Trace (collapsible) */}
              {this.state.errorInfo && (
                <details className="mb-4">
                  <summary 
                    className="text-xs text-[#888899] cursor-pointer hover:text-[#00f5ff] transition-colors flex items-center gap-2"
                    style={{ fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    <Bug size={12} />
                    View technical details
                  </summary>
                  <pre 
                    className="mt-2 p-3 bg-[#0a0a0f] rounded border border-[#2a2a3a] text-xs text-[#888899] overflow-x-auto max-h-40 overflow-y-auto"
                    style={{ fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    {this.state.errorInfo}
                  </pre>
                </details>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={this.handleReset}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[#00f5ff]/20 border border-[#00f5ff]/50 text-[#00f5ff] hover:bg-[#00f5ff]/30 transition-colors"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  <RefreshCw size={16} />
                  Try Again
                </button>
                <button
                  onClick={this.handleReload}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[#ff0080]/20 border border-[#ff0080]/50 text-[#ff0080] hover:bg-[#ff0080]/30 transition-colors"
                  style={{ fontFamily: 'Rajdhani, sans-serif' }}
                >
                  <RefreshCw size={16} />
                  Reload Page
                </button>
              </div>

              {/* Help Text */}
              <p 
                className="mt-4 text-xs text-[#555566] text-center"
                style={{ fontFamily: 'Rajdhani, sans-serif' }}
              >
                If this error persists, please check the console for more details.
              </p>
            </div>

            {/* Decorative elements */}
            <div className="mt-4 flex justify-center gap-2">
              {[...Array(3)].map((_, i) => (
                <div 
                  key={i}
                  className="w-2 h-2 rounded-full bg-[#ff0080] animate-pulse"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

