"""
SPHEREx Hunter Frontend Redesign Generator.
Generates frontend/index.html with modern dark observatory theme,
responsive top bar, 4-tab inspector, 3-tab dock, and preserved data logic.
"""


def build():
    parts = []

    # 1. HTML HEAD & STYLES
    parts.append("""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SPHEREx Hunter - Deep Space Infrared Observatory</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Lucide Icons CDN -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <!-- Chart.js for 102-band Spectrum & Light Curve -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- CDS ALADIN LITE V3 (Vendored locally for 100% offline & zero cross-origin ORB blocks) -->
  <script type="module">
    import A from '/app/vendor/aladin.js';
    window.A = A;
  </script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            space: {
              950: '#070a11', // Deep space canvas background
              900: '#0d111b', // Main panel background
              850: '#131926', // Elevated card / header background
              800: '#1a2234', // Button / Card background
              750: '#222c42', // Hover card background
              700: '#2b3752', // Border default
              600: '#3c4c6f', // Hover border
              500: '#526694', // Muted text
            },
            blender: {
              950: '#070a11',
              900: '#0d111b',
              850: '#131926',
              800: '#1a2234',
              750: '#222c42',
              700: '#2b3752',
              600: '#3c4c6f',
              orange: '#ea7600',
              blue: '#1f6feb',
              lightBlue: '#388bfd'
            },
            accent: {
              orange: '#ea7600',
              amber: '#f59e0b',
              cyan: '#06b6d4',
              blue: '#2563eb',
              emerald: '#10b981',
              rose: '#f43f5e',
              purple: '#a855f7'
            }
          }
        }
      }
    }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
      --bg-deep: #070a11;
      --bg-panel: #0d111b;
      --bg-card: #131926;
      --border-subtle: #202b42;
      --border-focus: #3b82f6;
      --accent-orange: #ea7600;
      --accent-blue: #1f6feb;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-deep);
      color: #cbd5e1;
      overflow: hidden;
      user-select: none;
    }
    .font-mono { font-family: 'JetBrains Mono', monospace; }

    /* Button primitives */
    .blender-btn {
      background-color: #172033;
      border: 1px solid #283550;
      border-radius: 4px;
      color: #cbd5e1;
      transition: all 0.12s ease;
    }
    .blender-btn:hover {
      background-color: #212c44;
      border-color: #3b4d73;
      color: #ffffff;
    }
    .blender-btn-active {
      background-color: #1f6feb !important;
      border-color: #388bfd !important;
      color: #ffffff !important;
      box-shadow: 0 0 10px rgba(31, 111, 235, 0.35);
    }
    .blender-btn-orange-active {
      background-color: #ea7600 !important;
      border-color: #ff9124 !important;
      color: #ffffff !important;
      box-shadow: 0 0 10px rgba(234, 118, 0, 0.4);
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0a0e17; }
    ::-webkit-scrollbar-thumb { background: #283550; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3c4c6f; }

    input[type=range] { accent-color: #1f6feb; }

    /* Canvas colormap filters */
    .filter-grayscale { filter: none; }
    .filter-inverted { filter: invert(1) hue-rotate(180deg); }
    .filter-thermal { filter: contrast(1.3) saturate(1.8) hue-rotate(190deg); }

    /* Tooltips */
    .tooltip-hint {
      position: relative;
    }
    .tooltip-hint:hover::after {
      content: attr(data-tooltip);
      position: absolute;
      bottom: -28px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(13, 17, 27, 0.95);
      border: 1px solid #2b3752;
      color: #e2e8f0;
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
      z-index: 60;
      pointer-events: none;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    /* Subtle pulse animation */
    @keyframes pulse-subtle {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.85; transform: scale(1.02); }
    }
    .animate-pulse-subtle { animation: pulse-subtle 3s infinite ease-in-out; }
  </style>
</head>
<body class="h-screen flex flex-col bg-space-950 text-xs">
""")

    # 2. TOP WORKSPACE HEADER (48px / h-12)
    parts.append("""
  <!-- ========================================================================= -->
  <!-- 1. TOP OBSERVATORY HEADER (48px / h-12)                                    -->
  <!-- ========================================================================= -->
  <header class="h-12 bg-space-900 border-b border-space-700 px-3 flex items-center justify-between z-30 shrink-0 text-xs gap-3 shadow-md">

    <!-- Left: Branding & Workspace Mode Segmented Control -->
    <div class="flex items-center gap-3 shrink-0">
      <!-- App Brand -->
      <div class="flex items-center gap-2 pr-3 border-r border-space-700">
        <div class="w-6 h-6 rounded bg-gradient-to-br from-amber-500 via-blender-orange to-orange-600 flex items-center justify-center font-bold text-white text-xs shadow-md shadow-orange-950/50">
          <i data-lucide="crosshair" class="w-3.5 h-3.5 text-white"></i>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="font-bold text-white tracking-wide text-sm font-sans">SPHEREx</span>
          <span class="text-blender-orange font-semibold text-xs tracking-wider">HUNTER</span>
        </div>
      </div>

      <!-- Segmented View Mode Control -->
      <div class="flex items-center bg-space-950 p-0.5 rounded-lg border border-space-700 gap-0.5 shadow-inner">
        <button id="wsBlink" class="blender-btn blender-btn-active px-3 py-1 rounded text-xs font-medium whitespace-nowrap flex items-center gap-1.5 transition-all" title="Multi-Epoch Flipbook Blink Comparator (Hotkey: B)">
          <i data-lucide="split" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>Blink</span>
          <kbd class="hidden sm:inline-block px-1 py-0.2 bg-black/40 rounded text-[9px] font-mono text-gray-400 border border-white/10">B</kbd>
        </button>
        <button id="wsDiff" class="blender-btn px-3 py-1 rounded text-xs font-medium whitespace-nowrap flex items-center gap-1.5 transition-all" title="Numerical ZOGY Image Subtraction (Hotkey: D)">
          <i data-lucide="layers" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>Difference</span>
          <kbd class="hidden sm:inline-block px-1 py-0.2 bg-black/40 rounded text-[9px] font-mono text-gray-400 border border-white/10">D</kbd>
        </button>
        <button id="wsSpec" class="blender-btn px-3 py-1 rounded text-xs font-medium whitespace-nowrap flex items-center gap-1.5 transition-all" title="102-Band SPHEREx Infrared Spectroscopy (Hotkey: S)">
          <i data-lucide="activity" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>Spectra</span>
          <kbd class="hidden sm:inline-block px-1 py-0.2 bg-black/40 rounded text-[9px] font-mono text-gray-400 border border-white/10">S</kbd>
        </button>
        <button id="wsAladin" class="blender-btn px-3 py-1 rounded text-xs font-medium whitespace-nowrap flex items-center gap-1.5 transition-all" title="Interactive CDS Strasbourg Aladin Lite (Hotkey: A)">
          <i data-lucide="globe" class="w-3.5 h-3.5 text-blue-400"></i>
          <span>Aladin Sky</span>
          <kbd class="hidden sm:inline-block px-1 py-0.2 bg-black/40 rounded text-[9px] font-mono text-gray-400 border border-white/10">A</kbd>
        </button>
      </div>
    </div>

    <!-- Center: Curated Target Selector & Quick Search -->
    <div class="flex items-center gap-1.5 bg-space-950 p-1 px-2.5 rounded-lg border border-space-700 shadow-inner overflow-x-auto shrink min-w-0">

      <!-- Command Palette / Target Switcher Button -->
      <button id="btnOpenCommandPalette" class="flex items-center gap-1.5 text-xs text-gray-300 hover:text-white bg-space-850 hover:bg-space-800 px-2 py-0.5 rounded border border-space-700 transition" title="Search targets and coordinates (Ctrl+K)">
        <i data-lucide="search" class="w-3 h-3 text-cyan-400"></i>
        <span id="activeTargetBadgeName" class="font-semibold text-white truncate max-w-[120px]">WISE 0855</span>
        <kbd class="px-1 py-0.2 bg-black/50 rounded text-[9px] font-mono text-gray-400 border border-white/10">Ctrl+K</kbd>
      </button>

      <div class="w-[1px] h-4 bg-space-700/80 mx-1"></div>

      <!-- Quick Preset Buttons (Preserves .target-btn for E2E tests) -->
      <div class="flex items-center gap-1">
        <button class="target-btn blender-btn blender-btn-active px-2 py-0.5 text-[10px] font-mono whitespace-nowrap rounded" data-target="wise0855" title="WISE 0855-0714 (Cold Y-Dwarf, ~250 K)">WISE 0855</button>
        <button class="target-btn blender-btn px-2 py-0.5 text-[10px] font-mono whitespace-nowrap rounded" data-target="barnard" title="Barnard's Star (10.36 \"/yr Proper Motion)">Barnard's Star</button>
        <button class="target-btn blender-btn px-2 py-0.5 text-[10px] font-mono whitespace-nowrap rounded" data-target="epsindi" title="Epsilon Indi B (Binary Brown Dwarf)">Eps Indi B</button>
        <button class="target-btn blender-btn px-2 py-0.5 text-[10px] font-mono whitespace-nowrap rounded" data-target="rwaur" title="RW Aurigae (T-Tauri Variable)">RW Aur</button>
        <button class="target-btn blender-btn px-2 py-0.5 text-[10px] font-mono whitespace-nowrap rounded" data-target="rdraconis" title="R Draconis (Mira Variable)">R Dra</button>
      </div>
    </div>

    <!-- Right: Telemetry, Coordinates Popover, Primary Actions & Overflow -->
    <div class="flex items-center gap-2 shrink-0">

      <!-- Compact Coordinates Popover Trigger -->
      <div class="relative">
        <button id="btnToggleCoordsPopover" class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-space-850 hover:bg-space-800 border border-space-700 text-xs font-mono text-gray-300 hover:text-white transition" title="Edit celestial coordinates & field of view">
          <i data-lucide="crosshair" class="w-3.5 h-3.5 text-blender-orange"></i>
          <span id="quickCoordsLabel" class="text-[11px]">133.795°, -7.245°</span>
          <i data-lucide="chevron-down" class="w-3 h-3 text-gray-400"></i>
        </button>

        <!-- Floating Coordinates Popover Card -->
        <div id="coordsPopover" class="hidden absolute right-0 top-10 mt-1 w-72 bg-space-900 border border-space-700 rounded-lg p-3 shadow-2xl z-50 space-y-2.5 font-mono">
          <div class="flex items-center justify-between pb-1.5 border-b border-space-700">
            <span class="text-xs font-bold text-white flex items-center gap-1.5">
              <i data-lucide="navigation" class="w-3.5 h-3.5 text-cyan-400"></i>
              <span>Target Coordinates</span>
            </span>
            <button id="btnCloseCoordsPopover" class="text-gray-400 hover:text-white text-xs">✕</button>
          </div>

          <div class="space-y-1.5 text-xs">
            <div>
              <label class="block text-[10px] text-gray-400 mb-0.5">Right Ascension α (deg):</label>
              <input id="inputRA" type="text" value="133.79513" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-blender-orange font-mono">
            </div>
            <div>
              <label class="block text-[10px] text-gray-400 mb-0.5">Declination δ (deg):</label>
              <input id="inputDec" type="text" value="-7.24515" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-blender-orange font-mono">
            </div>
            <div>
              <label class="block text-[10px] text-gray-400 mb-0.5">Field of View (FOV):</label>
              <select id="selectFOV" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white text-xs focus:outline-none focus:border-blender-orange font-mono">
                <option value="1.5">1.5 Arcmin (High-Res Core)</option>
                <option value="3.0" selected>3.0 Arcmin (Standard Science)</option>
                <option value="5.0">5.0 Arcmin (Extended Context)</option>
                <option value="10.0">10.0 Arcmin (Wide Overview)</option>
              </select>
            </div>
          </div>

          <button id="btnGoCoords" class="w-full py-1.5 rounded bg-blender-orange hover:bg-orange-600 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition shadow">
            <i data-lucide="compass" class="w-3.5 h-3.5"></i>
            <span>Slew Telescope (Fetch)</span>
          </button>
        </div>
      </div>

      <!-- Primary Action: Direct Fetch Button -->
      <button id="btnTopFetch" class="px-3 py-1 rounded bg-blender-orange hover:bg-orange-600 text-white font-semibold text-xs flex items-center gap-1.5 shadow transition" title="Fetch multi-epoch FITS cutouts for current coordinates">
        <i data-lucide="download" class="w-3.5 h-3.5"></i>
        <span>Fetch</span>
      </button>

      <!-- Beginner / Scientist Mode Toggle Pill -->
      <button id="btnToggleUserMode" class="flex items-center gap-1 px-2 py-1 rounded bg-space-850 hover:bg-space-800 border border-space-700 text-[11px] font-medium text-gray-300 hover:text-white transition" title="Switch between Beginner (simple plain language) and Scientist (raw telemetry) mode">
        <i data-lucide="graduation-cap" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span id="userModeLabel">Beginner</span>
      </button>

      <!-- Mission Codex & Phase 2 Validation Button -->
      <button id="btnOpenValidation" class="p-1.5 rounded blender-btn text-cyan-300 hover:text-white flex items-center gap-1 text-xs" title="Open Official NASA/CSA Codex & Phase 2 Scientific Validation Benchmark">
        <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-cyan-400"></i>
        <span class="hidden md:inline">Validation</span>
      </button>

      <!-- Keyboard Shortcuts Trigger -->
      <button id="btnOpenShortcuts" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Keyboard Shortcuts Cheat Sheet (?)">
        <i data-lucide="help-circle" class="w-3.5 h-3.5"></i>
      </button>

      <!-- Toggle Right Inspector Panel -->
      <button id="toggleSidebarBtn" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Toggle Inspector Sidebar">
        <i data-lucide="sidebar" class="w-3.5 h-3.5"></i>
      </button>
    </div>
  </header>
""")

    # 3. WORKSPACE BODY: LEFT RAIL (56px) + CENTER VIEWPORT + RIGHT INSPECTOR (380px)
    parts.append("""
  <!-- ========================================================================= -->
  <!-- 2. MAIN WORKSPACE CONTAINER                                               -->
  <!-- ========================================================================= -->
  <div class="flex-1 flex overflow-hidden relative">

    <!-- LEFT TOOL RAIL (56px / w-14) -->
    <aside class="w-14 bg-space-900 border-r border-space-700 flex flex-col items-center py-2 gap-2 z-20 shrink-0 select-none text-[10px]">

      <!-- Select / Inspect Tool -->
      <button id="toolSelect" class="w-10 h-10 rounded blender-btn blender-btn-active flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Inspect / Reticle Target (V)">
        <i data-lucide="mouse-pointer" class="w-4 h-4 text-cyan-400"></i>
        <span class="text-[8px] font-mono">Select</span>
      </button>

      <!-- Pan Tool -->
      <button id="toolPan" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Pan / Drag Telescope (H)">
        <i data-lucide="hand" class="w-4 h-4 text-gray-300"></i>
        <span class="text-[8px] font-mono">Pan</span>
      </button>

      <!-- Measure / Ruler Tool -->
      <button id="toolMeasure" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Measure Distance in Arcseconds (M)">
        <i data-lucide="ruler" class="w-4 h-4 text-emerald-400"></i>
        <span class="text-[8px] font-mono">Dist</span>
      </button>

      <!-- Blink A/B Flip Tool -->
      <button id="toolBlinkFlip" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Flip Blink Frame A / B (Space / B)">
        <i data-lucide="flip-horizontal" class="w-4 h-4 text-amber-400"></i>
        <span class="text-[8px] font-mono">Flip</span>
      </button>

      <div class="w-7 h-[1px] bg-space-700/80 my-1"></div>

      <!-- Gaia DR3 Astrometry Overlay -->
      <button id="toggleGaia" class="w-10 h-10 rounded blender-btn blender-btn-active flex flex-col items-center justify-center gap-0.5 text-cyan-300 hover:text-white transition" title="Toggle ESA/NASA Gaia DR3 Proper Motion Vectors (G)">
        <i data-lucide="sparkles" class="w-4 h-4 text-cyan-400"></i>
        <span class="text-[8px] font-mono">Gaia</span>
      </button>

      <!-- Recenter Viewport -->
      <button id="toolRecenter" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Recenter on Target Coordinates (R)">
        <i data-lucide="crosshair" class="w-4 h-4 text-blender-orange"></i>
        <span class="text-[8px] font-mono">Center</span>
      </button>

      <!-- Reset Zoom 1:1 -->
      <button id="toolResetZoom" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Reset Zoom to 1.0x (1)">
        <i data-lucide="zoom-in" class="w-4 h-4 text-gray-300"></i>
        <span class="text-[8px] font-mono">1:1</span>
      </button>

      <!-- WASD Walk Navigation -->
      <button id="toolWalk" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="WASD Spaceflight Walk Flight Navigation (W / Shift+`)">
        <i data-lucide="gamepad-2" class="w-4 h-4 text-purple-400"></i>
        <span class="text-[8px] font-mono">Walk</span>
      </button>

      <div class="flex-1"></div>

      <!-- Fullscreen Viewport -->
      <button id="toolFullscreen" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Toggle Fullscreen Viewport (F)">
        <i data-lucide="maximize" class="w-4 h-4 text-gray-300"></i>
        <span class="text-[8px] font-mono">Full</span>
      </button>

      <!-- Audio Mute -->
      <button id="toolMute" class="w-10 h-10 rounded blender-btn flex flex-col items-center justify-center gap-0.5 text-gray-300 hover:text-white transition" title="Toggle Synthesizer Audio">
        <i id="muteIcon" data-lucide="volume-2" class="w-4 h-4 text-gray-300"></i>
        <span class="text-[8px] font-mono">Sound</span>
      </button>
    </aside>

    <!-- CENTER OBSERVATORY VIEWPORT (Edge-to-Edge Pure Astronomy Canvas) -->
    <main class="flex-1 relative bg-[#070a11] overflow-hidden flex items-center justify-center cursor-crosshair" id="viewportContainer">

      <!-- Primary Astronomical Canvas -->
      <canvas id="astroCanvas" class="w-full h-full block filter-grayscale"></canvas>

      <!-- Interactive CDS Strasbourg Aladin Lite Container -->
      <div id="aladinContainer" class="absolute inset-0 hidden z-10 w-full h-full"></div>

      <!-- LOADING OVERLAY -->
      <div id="loadingOverlay" class="absolute inset-0 bg-black/70 backdrop-blur-sm z-30 flex flex-col items-center justify-center gap-3 transition-opacity duration-300 pointer-events-none opacity-0">
        <div class="relative w-12 h-12 flex items-center justify-center">
          <div class="w-12 h-12 rounded-full border-2 border-blender-orange/20 border-t-blender-orange animate-spin"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-blender-orange animate-ping absolute"></div>
          <div class="w-2 h-2 rounded-full bg-white absolute"></div>
        </div>
        <div class="text-center font-mono space-y-1">
          <div class="text-white text-xs font-semibold tracking-wide flex items-center gap-1.5 justify-center">
            <span class="w-1.5 h-1.5 rounded-full bg-blender-orange animate-pulse"></span>
            <span id="loadingTitleText">Querying Real NASA IRSA Database...</span>
          </div>
          <div id="loadingDetailText" class="text-gray-400 text-[10px]">
            Fetching live multi-epoch FITS telescope cutouts
          </div>
        </div>
      </div>

      <!-- FIRST 10 SECONDS GUIDED DEMO TOUR BANNER -->
      <div id="guidedTourBanner" class="absolute top-3 left-1/2 -translate-x-1/2 bg-space-900/95 backdrop-blur-md border border-blender-orange/70 px-4 py-2 rounded-xl shadow-2xl flex items-center gap-3 text-xs z-20 max-w-xl transition-all">
        <div class="w-7 h-7 rounded-lg bg-blender-orange/20 border border-blender-orange flex items-center justify-center text-blender-orange shrink-0">
          <i data-lucide="sparkles" class="w-4 h-4"></i>
        </div>
        <div class="flex-1">
          <div class="font-bold text-white flex items-center gap-1.5">
            <span>What you're seeing:</span>
            <span class="text-blender-orange font-mono">WISE 0855-0714</span>
          </div>
          <p class="text-[11px] text-gray-300 leading-snug">
            The coldest known brown dwarf (~250 K), ~7.2 light-years away. Discovered by its rapid proper motion (8.15 "/yr) across infrared surveys.
          </p>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button id="btnStartTourBlink" class="px-2.5 py-1 rounded bg-blender-orange hover:bg-orange-600 text-white font-semibold text-[11px] shadow">
            ▶ Blink
          </button>
          <button id="btnDismissTour" class="p-1 text-gray-400 hover:text-white rounded hover:bg-space-800" title="Dismiss guide">
            ✕
          </button>
        </div>
      </div>

      <!-- INLINE CANDIDATE SELECTION ALERT STRIP (Dismissible, only shows on candidate selection) -->
      <div id="candidateAlertStrip" class="hidden absolute top-3 left-1/2 -translate-x-1/2 bg-space-900/95 backdrop-blur-md border border-cyan-500/70 px-4 py-2 rounded-xl shadow-2xl flex items-center gap-3 text-xs z-20 max-w-xl">
        <i data-lucide="flag" class="w-4 h-4 text-cyan-400 shrink-0"></i>
        <div id="candidateAlertText" class="text-gray-200 text-xs font-mono flex-1 truncate">
          Selected Candidate at RA 133.79513°, Dec -7.24515°
        </div>
        <button id="btnRecordFromAlert" class="px-2 py-0.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-[10px]">
          Record
        </button>
        <button id="btnDismissCandidateAlert" class="text-gray-400 hover:text-white text-xs">✕</button>
      </div>

      <!-- TOP-LEFT VIEWPORT TARGET TELEMETRY CHIP (Minimal & Unobtrusive) -->
      <div class="absolute top-3 left-3 pointer-events-none text-xs font-mono space-y-0.5 bg-space-900/85 backdrop-blur-md px-3 py-2 rounded-lg border border-space-700 text-gray-300 shadow-lg">
        <div class="flex items-center gap-2">
          <span id="vpTargetName" class="text-white font-bold text-xs tracking-wide">WISE 0855-0714</span>
          <span class="text-space-500">|</span>
          <span id="vpFrameLabel" class="text-blender-orange font-semibold text-[11px]">(Frame 1) 2MASS Baseline 1999</span>
        </div>
        <div id="gaiaCrossMatchBadge" class="hidden text-[10px] font-mono mt-1 px-2 py-0.5 rounded border flex items-center gap-1.5 transition-all">
          <span id="gaiaCrossMatchIcon"></span>
          <span id="gaiaCrossMatchText"></span>
        </div>
      </div>

      <!-- TOP-RIGHT COLORMAP & SHADING POPOVER CONTROLS -->
      <div class="absolute top-3 right-3 flex items-center gap-1 bg-space-900/85 backdrop-blur-md px-2 py-1 rounded-lg border border-space-700 shadow-lg z-10 font-mono text-[10px]">
        <span class="text-gray-400 mr-1 select-none">Stretch:</span>
        <button id="shadeGrayscale" class="blender-btn blender-btn-active px-2 py-0.5 rounded" title="Authentic Linear Grayscale">
          Gray
        </button>
        <button id="shadeInverted" class="blender-btn px-2 py-0.5 rounded" title="Inverted Grayscale (DS9 Print Style)">
          Invert
        </button>
        <button id="shadeThermal" class="blender-btn px-2 py-0.5 rounded" title="False Color Infrared Thermal">
          Thermal
        </button>
      </div>

      <!-- BOTTOM-LEFT LIVE CURSOR TELEMETRY HUD -->
      <div class="absolute bottom-3 left-3 pointer-events-none text-[10px] font-mono flex items-center gap-3 bg-space-900/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-700 text-gray-400 shadow-lg">
        <span>RA: <b id="vpRA" class="text-gray-200">133.79513°</b></span>
        <span>Dec: <b id="vpDec" class="text-gray-200">-7.24515°</b></span>
        <span>FOV: <b id="vpFOV" class="text-gray-200">3.00'</b></span>
        <span>Zoom: <b id="vpZoom" class="text-gray-200">1.0x</b></span>
        <span class="pl-2 border-l border-space-700">LOD: <b id="vpLOD" class="text-cyan-300">LOD 1 (Std)</b></span>
        <span id="vpMosaicBadge" class="hidden pl-2 border-l border-space-700 text-amber-300 font-bold">Mosaic: 3×3</span>
      </div>

      <!-- BOTTOM-RIGHT SCALE BAR & COMPASS HUD -->
      <div class="absolute bottom-3 right-3 pointer-events-none flex flex-col items-end gap-1 text-[10px] font-mono bg-space-900/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-700 text-gray-300 shadow-lg">
        <div class="flex items-center gap-2">
          <!-- Compass vectors -->
          <div class="relative w-5 h-5 flex items-center justify-center text-[9px] font-bold text-cyan-400">
            <span class="absolute top-0 text-[8px] text-cyan-300">N↑</span>
            <span class="absolute right-0 text-[8px] text-amber-300">←E</span>
          </div>
          <!-- Scale bar (1 arcmin) -->
          <div class="flex flex-col items-center">
            <div class="w-16 h-1 bg-cyan-400 rounded"></div>
            <span class="text-[9px] text-gray-400">1.0 Arcmin</span>
          </div>
        </div>
      </div>

      <!-- FLOATING GAMER WALK MODE HUD BANNER (Only active during Walk Nav) -->
      <div id="walkHudBanner" class="absolute bottom-12 left-1/2 -translate-x-1/2 bg-space-900/95 backdrop-blur-md border border-blender-orange/70 px-4 py-1.5 rounded-full shadow-2xl flex items-center gap-3 font-mono text-[11px] text-white hidden z-20 pointer-events-auto">
        <div class="flex items-center gap-1 text-blender-orange font-bold">
          <span class="w-2 h-2 rounded-full bg-blender-orange animate-ping"></span>
          <span>WALK NAV ACTIVE</span>
        </div>
        <div class="text-gray-300 flex items-center gap-2 text-[10px]">
          <span><b class="text-white">Mouse:</b> Look</span>
          <span><b class="text-white">W/S:</b> Zoom</span>
          <span><b class="text-white">A/D:</b> Slew RA</span>
          <span><b class="text-white">Space/C:</b> Slew Dec</span>
          <button id="btnExitWalkHud" class="bg-space-800 hover:bg-space-700 px-2 py-0.5 rounded border border-space-700 text-gray-300 hover:text-white text-[10px]">
            Esc Exit
          </button>
        </div>
      </div>
    </main>

    <!-- RIGHT INSPECTOR (380px, Data-Driven Tabbed Interface) -->
    <aside id="propertiesSidebar" class="w-96 bg-space-900 border-l border-space-700 flex flex-col shrink-0 min-h-0 z-20 text-xs select-none shadow-xl" role="region" aria-label="Scene Collection and Layer Manager">

      <!-- STICKY TAB HEADER -->
      <div class="px-2 pt-2 bg-space-850 border-b border-space-700 shrink-0 sticky top-0 z-30 shadow-sm">
        <div class="flex items-center justify-between pb-1.5 px-1">
          <span class="font-bold text-white text-xs flex items-center gap-1.5">
            <i data-lucide="sliders" class="w-3.5 h-3.5 text-blender-orange"></i>
            <span>Scene Collection</span>
          </span>
          <div class="flex items-center gap-1">
            <span id="sceneStatusBadge" class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60">LIVE STATE</span>
            <button id="btnRefreshScene" class="p-1 hover:bg-space-750 rounded text-gray-400 hover:text-white transition" title="Refresh Scene State">
              <i data-lucide="rotate-cw" class="w-3 h-3"></i>
            </button>
          </div>
        </div>

        <!-- 4 Inspector Tabs -->
        <div class="flex items-center gap-1 border-t border-space-700/80 pt-1 text-[11px]">
          <button id="tabLayersBtn" class="flex-1 py-1.5 px-2 rounded-t font-semibold blender-btn blender-btn-active text-center flex items-center justify-center gap-1 transition" title="Observation Epochs and Visual Layers">
            <i data-lucide="layers" class="w-3 h-3 text-blender-orange"></i>
            <span>Layers</span>
          </button>
          <button id="tabTargetBtn" class="flex-1 py-1.5 px-2 rounded-t font-semibold blender-btn text-center flex items-center justify-center gap-1 transition" title="Astronomical Target Metadata and Gaia Cross-match">
            <i data-lucide="target" class="w-3 h-3 text-cyan-400"></i>
            <span>Target</span>
          </button>
          <button id="tabCandidatesBtn" class="flex-1 py-1.5 px-2 rounded-t font-semibold blender-btn text-center flex items-center justify-center gap-1 transition" title="Discovered Candidates and Evidence Tiers">
            <i data-lucide="flag" class="w-3 h-3 text-amber-400"></i>
            <span>Candidates</span>
          </button>
          <button id="tabPhotometryBtn" class="flex-1 py-1.5 px-2 rounded-t font-semibold blender-btn text-center flex items-center justify-center gap-1 transition" title="SPHEREx 6-Detector Array Photometry">
            <i data-lucide="activity" class="w-3 h-3 text-emerald-400"></i>
            <span>Photometry</span>
          </button>
        </div>
      </div>

      <!-- TAB PANEL 1: LAYERS (Scene Collection - Preserves exact state and tests) -->
      <div id="inspectorPanelLayers" class="flex-1 overflow-y-auto min-h-0 divide-y divide-space-700/60 p-1">

        <!-- Filter Search Bar for Layers -->
        <div class="p-2">
          <div class="relative">
            <i data-lucide="search" class="w-3 h-3 text-gray-400 absolute left-2 top-2"></i>
            <input id="layerSearchInput" type="text" placeholder="Filter epochs & layers..." class="w-full bg-space-950 border border-space-700 rounded pl-7 pr-2 py-1 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blender-orange font-mono">
          </div>
        </div>

        <!-- LOADING SKELETON -->
        <div id="sceneSkeleton" class="p-3 space-y-2.5 hidden">
          <div class="h-4 bg-space-800 rounded animate-pulse w-3/4"></div>
          <div class="h-14 bg-space-800/60 rounded animate-pulse"></div>
          <div class="h-20 bg-space-800/40 rounded animate-pulse"></div>
        </div>

        <!-- ERROR BANNER WITH RETRY -->
        <div id="sceneError" class="p-3 bg-rose-950/60 border-b border-rose-800/60 hidden">
          <div class="flex items-center gap-2 text-rose-300 font-medium text-xs">
            <i data-lucide="alert-triangle" class="w-4 h-4 text-rose-400 shrink-0"></i>
            <span id="sceneErrorMessage">Failed to load scene state.</span>
          </div>
          <button id="btnRetryScene" class="mt-2 w-full py-1 bg-rose-900/60 hover:bg-rose-800 text-white rounded text-[11px] font-medium border border-rose-700 flex items-center justify-center gap-1 transition">
            <i data-lucide="refresh-cw" class="w-3 h-3"></i>
            <span>Retry Connection</span>
          </button>
        </div>

        <!-- DYNAMIC DATA-DRIVEN CONTENT (Populated by renderSceneCollection) -->
        <div id="sceneContent" class="divide-y divide-space-700/60">
          <!-- Populated purely by renderSceneCollection(window.scene) -->
        </div>
      </div>

      <!-- TAB PANEL 2: TARGET (Astronomical Target Telemetry & External Bridges) -->
      <div id="inspectorPanelTarget" class="hidden flex-1 overflow-y-auto min-h-0 p-3 space-y-3 font-mono text-xs">
        <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white text-sm" id="targetDetailName">WISE 0855-0714</span>
            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-600">VERIFIED</span>
          </div>
          <div class="text-gray-300 text-[11px] font-sans" id="targetDetailType">Cold Y-Dwarf (Sub-stellar Brown Dwarf)</div>
        </div>

        <!-- Coordinates & Astrometry Card -->
        <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5 text-[11px]">
          <div class="text-gray-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1 text-cyan-400">
            <i data-lucide="compass" class="w-3 h-3"></i>
            <span>ICRS Astrometry</span>
          </div>
          <div class="flex justify-between"><span class="text-gray-400">RA (α):</span><span id="propRA" class="text-white font-bold">133.79513°</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Dec (δ):</span><span id="propDec" class="text-white font-bold">-7.24515°</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Total PM (μ):</span><span id="propTotalPM" class="text-blender-orange font-bold">8.149 "/yr (8149 mas/yr)</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Distance:</span><span id="propDist" class="text-gray-200">2.28 pc (7.43 ly)</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Teff:</span><span id="propTeff" class="text-cyan-300 font-bold">~250 K</span></div>
        </div>

        <!-- Gaia DR3 Cross-Match Card -->
        <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5 text-[11px]">
          <div class="text-gray-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1 text-cyan-400">
            <i data-lucide="sparkles" class="w-3 h-3"></i>
            <span>Gaia DR3 Cross-Match</span>
          </div>
          <div class="flex justify-between"><span class="text-gray-400">Stars in 3' Cone:</span><span id="gaiaStarCount" class="text-white font-bold">--</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Nearest Star:</span><span id="gaiaNearestID" class="text-cyan-300 font-bold">--</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Highest PM:</span><span id="gaiaTopPM" class="text-amber-400 font-bold">--</span></div>
          <div class="flex justify-between"><span class="text-gray-400">Optical Counterpart:</span><span id="gaiaMatchStatus" class="text-rose-400 font-bold">No Match (IR-Only)</span></div>
        </div>

        <!-- External Archival Bridges -->
        <div class="space-y-2 pt-1 font-sans">
          <a id="btnWiseView" href="http://byw.tools/wiseview#ra=133.79513&dec=-7.24515&size=150&band=3&linear=True&diff=True" target="_blank" rel="noopener noreferrer"
             class="w-full py-2 px-3 rounded-lg bg-space-850 hover:bg-space-800 border border-space-700 hover:border-amber-400 text-amber-300 hover:text-amber-200 text-xs font-mono font-medium flex items-center justify-center gap-2 transition shadow-sm">
            <i data-lucide="external-link" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Verify in NASA WiseView Flipbook ↗</span>
          </a>

          <a id="btnCadcSearch" href="https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.jp/en/search/?collection=NEOSSAT" target="_blank" rel="noopener noreferrer"
             class="w-full py-2 px-3 rounded-lg bg-space-850 hover:bg-space-800 border border-space-700 hover:border-blue-400 text-blue-300 hover:text-white text-xs font-mono font-medium flex items-center justify-center gap-2 transition shadow-sm">
            <i data-lucide="satellite" class="w-3.5 h-3.5 text-blue-400"></i>
            <span>CADC NEOSSat Asteroid Archive ↗</span>
          </a>

          <button id="flagCandidateBtn" class="w-full py-2 rounded-lg bg-blender-orange hover:bg-orange-600 text-white font-semibold text-xs flex items-center justify-center gap-2 transition shadow">
            <i data-lucide="flag" class="w-3.5 h-3.5"></i>
            <span>Flag Discovery to NASA &amp; CSA</span>
          </button>
        </div>
      </div>

      <!-- TAB PANEL 3: CANDIDATES (Discovered Moving Sources & Evidence Tiers) -->
      <div id="inspectorPanelCandidates" class="hidden flex-1 overflow-y-auto min-h-0 p-3 space-y-3 font-mono text-xs">

        <div class="flex items-center justify-between pb-1">
          <span class="font-bold text-white text-xs flex items-center gap-1.5">
            <i data-lucide="flag" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Flagged Candidates</span>
          </span>
          <div class="flex items-center gap-1">
            <button id="btnExportCSV" class="px-2 py-0.5 rounded bg-space-800 hover:bg-space-750 border border-space-700 text-cyan-300 text-[10px] flex items-center gap-1" title="Download all discoveries as CSV">
              <i data-lucide="download" class="w-3 h-3"></i>
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        <!-- Filter Pills for Evidence Tiers -->
        <div class="flex items-center gap-1 overflow-x-auto pb-1 text-[10px]">
          <button class="cand-filter-btn px-2 py-0.5 rounded bg-blender-blue text-white" data-filter="all">All</button>
          <button class="cand-filter-btn px-2 py-0.5 rounded bg-space-800 text-gray-400 hover:text-white" data-filter="brown_dwarf">Brown Dwarf</button>
          <button class="cand-filter-btn px-2 py-0.5 rounded bg-space-800 text-gray-400 hover:text-white" data-filter="asteroid">Asteroid</button>
          <button class="cand-filter-btn px-2 py-0.5 rounded bg-space-800 text-gray-400 hover:text-white" data-filter="transient">Transient</button>
        </div>

        <!-- Dynamic Candidates Container -->
        <div id="candidatesListContainer" class="space-y-2">
          <!-- Populated dynamically via loadDiscoveries() -->
          <div class="text-center py-6 text-gray-500 font-mono text-xs">
            Loading candidate discoveries...
          </div>
        </div>

        <button id="btnFlagNewCandidate" class="w-full py-2 rounded-lg bg-blender-orange hover:bg-orange-600 text-white font-semibold text-xs flex items-center justify-center gap-2 transition shadow">
          <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i>
          <span>Log New Candidate Discovery</span>
        </button>
      </div>

      <!-- TAB PANEL 4: PHOTOMETRY (SPHEREx 6-Detector Array Cards & NEOSSat) -->
      <div id="inspectorPanelPhotometry" class="hidden flex-1 overflow-y-auto min-h-0 p-3 space-y-3 font-mono text-xs">

        <div class="flex items-center justify-between">
          <span class="font-bold text-white text-xs flex items-center gap-1.5">
            <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i>
            <span>SPHEREx 6-Detector Array</span>
          </span>
          <span id="coaddArrayStatus" class="text-gray-400 text-[10px]">Awaiting Flight Co-adds</span>
        </div>

        <!-- Responsive Grid with minmax(120px, 1fr) so cards never overflow -->
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 1 (0.75 - 1.11 μm)</div>
            <div id="coaddA1" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA1" class="text-[9px] text-gray-500">SNR --</div>
          </div>
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 2 (1.11 - 1.64 μm)</div>
            <div id="coaddA2" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA2" class="text-[9px] text-gray-500">SNR --</div>
          </div>
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 3 (1.64 - 2.42 μm)</div>
            <div id="coaddA3" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA3" class="text-[9px] text-gray-500">SNR --</div>
          </div>
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 4 (2.42 - 3.82 μm)</div>
            <div id="coaddA4" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA4" class="text-[9px] text-gray-500">SNR --</div>
          </div>
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 5 (3.82 - 4.42 μm)</div>
            <div id="coaddA5" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA5" class="text-[9px] text-gray-500">SNR --</div>
          </div>
          <div class="bg-space-950 p-2 rounded-lg border border-space-700 flex flex-col justify-between min-w-[100px]">
            <div class="text-[10px] text-gray-400">Array 6 (4.42 - 5.00 μm)</div>
            <div id="coaddA6" class="text-gray-400 font-bold text-sm my-1">--</div>
            <div id="snrA6" class="text-[9px] text-gray-500">SNR --</div>
          </div>
        </div>
        <div class="text-[10px] text-gray-400 font-sans">
          Detector array co-added fluxes are displayed only when authentic calibrated SPHEREx Level 2/3 data is acquired.
        </div>

        <!-- Optional Service: CSA NEOSSat Card (Shows data or clean 1-line note) -->
        <div id="neossatCard" class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5 font-sans">
          <div class="flex items-center justify-between text-xs font-bold text-white font-mono">
            <span class="flex items-center gap-1.5 text-blue-400">
              <i data-lucide="satellite" class="w-3.5 h-3.5"></i>
              <span>CSA NEOSSat Archival Coverage</span>
            </span>
            <span class="text-[10px] text-gray-400 font-mono">CADC</span>
          </div>
          <div id="neossatCardStatus" class="text-gray-400 text-xs font-mono">
            No archival observations in 3' cone (CADC collection: NEOSSAT).
          </div>
        </div>
      </div>
    </aside>
  </div>
""")

    # 4. BOTTOM DOCK (Resizable / Collapsible, Tabs: Timeline, Spectrum, Light Curve)
    parts.append("""
  <!-- ========================================================================= -->
  <!-- 3. BOTTOM OBSERVATORY DOCK (Resizable & Collapsible)                      -->
  <!-- ========================================================================= -->
  <footer id="bottomDock" class="bg-space-900 border-t border-space-700 flex flex-col shrink-0 z-30 shadow-2xl transition-all duration-200">

    <!-- Dock Header & Tab Bar -->
    <div class="h-9 px-3 bg-space-850 border-b border-space-700 flex items-center justify-between text-xs shrink-0 select-none">

      <!-- Dock Tabs -->
      <div class="flex items-center gap-1">
        <button id="dockTabTimeline" class="blender-btn blender-btn-active px-3 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition">
          <i data-lucide="film" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>Timeline (Flipbook)</span>
        </button>
        <button id="dockTabSpectrum" class="blender-btn px-3 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition">
          <i data-lucide="line-chart" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>102-Band Spectrum</span>
        </button>
        <button id="dockTabLightCurve" class="blender-btn px-3 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition">
          <i data-lucide="trending-up" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>Light Curve</span>
        </button>
      </div>

      <!-- Quick Playback Telemetry & Collapse Toggle -->
      <div class="flex items-center gap-3">
        <span id="temporalBaselineText" class="text-emerald-400 font-bold font-mono text-[11px] hidden sm:inline-block">
          Δt: Multi-Epoch Baseline
        </span>
        <button id="btnToggleDock" class="p-1 rounded blender-btn text-gray-400 hover:text-white" title="Collapse / Expand Bottom Dock">
          <i id="dockCollapseIcon" data-lucide="chevron-down" class="w-3.5 h-3.5"></i>
        </button>
      </div>
    </div>

    <!-- Dock Content Body -->
    <div id="dockContentBody" class="h-36 overflow-hidden transition-all duration-200">

      <!-- PANEL 1: TIMELINE (Multi-Epoch Flipbook Controls) -->
      <div id="dockPanelTimeline" class="h-full px-4 flex items-center justify-between gap-4 font-mono text-xs">

        <!-- Left: Playback VCR Transport Controls -->
        <div class="flex items-center gap-1 shrink-0">
          <button id="btnJumpStart" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Jump to First Frame (Shift + Left)">
            <i data-lucide="skip-back" class="w-4 h-4"></i>
          </button>
          <button id="btnStepBack" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Step Back 1 Frame (Left Arrow)">
            <i data-lucide="step-back" class="w-4 h-4"></i>
          </button>
          <button id="btnPlayPause" class="px-3 py-1.5 rounded blender-btn blender-btn-orange-active flex items-center gap-1 text-white font-bold" title="Toggle Flipbook Play/Pause (Spacebar)">
            <i id="playPauseIcon" data-lucide="pause" class="w-4 h-4"></i>
            <span class="text-xs">Blink</span>
          </button>
          <button id="btnStepFwd" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Step Forward 1 Frame (Right Arrow)">
            <i data-lucide="step-forward" class="w-4 h-4"></i>
          </button>
          <button id="btnJumpEnd" class="p-1.5 rounded blender-btn text-gray-300 hover:text-white" title="Jump to Last Frame (Shift + Right)">
            <i data-lucide="skip-forward" class="w-4 h-4"></i>
          </button>

          <!-- Active Frame Input Box -->
          <div class="flex items-center gap-1 ml-2 pl-2 border-l border-space-700">
            <span class="text-gray-400 text-xs">Frame:</span>
            <span id="frameBadge" class="px-2 py-0.5 rounded bg-blender-blue text-white font-bold text-xs">1</span>
            <span class="text-gray-500 text-xs">/ 4</span>
          </div>
        </div>

        <!-- Center: Interactive Epoch Timeline Track with Ticks -->
        <div class="flex-1 flex flex-col justify-center px-4 max-w-2xl">
          <div class="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span>1999 (2MASS)</span>
            <span>2010 (WISE W1)</span>
            <span>2014 (unWISE)</span>
            <span class="text-blender-orange font-bold">2025 (SPHEREx)</span>
          </div>
          <div class="relative w-full h-2 bg-space-800 rounded-full flex items-center">
            <div id="timelineProgress" class="absolute left-0 h-full bg-blender-orange rounded-full transition-all duration-150" style="width: 25%;"></div>
            <div class="absolute left-0 w-3 h-3 rounded-full bg-white border-2 border-blender-orange cursor-pointer -ml-1.5"></div>
            <div class="absolute left-1/3 w-2.5 h-2.5 rounded-full bg-space-600 cursor-pointer -ml-1"></div>
            <div class="absolute left-2/3 w-2.5 h-2.5 rounded-full bg-space-600 cursor-pointer -ml-1"></div>
            <div class="absolute right-0 w-3 h-3 rounded-full bg-blender-orange cursor-pointer -mr-1.5"></div>
          </div>
        </div>

        <!-- Right: Blink Speed Slider -->
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-gray-400 text-xs">Speed:</span>
          <input id="speedSlider" type="range" min="0.5" max="6.0" step="0.5" value="2.0" class="w-24 h-1.5 bg-space-700 rounded cursor-pointer">
          <span id="speedLabel" class="text-gray-200 text-xs w-14 font-mono">2.0 FPS</span>
        </div>
      </div>

      <!-- PANEL 2: SPECTRUM (102-Band Curve Canvas with Molecular Dips) -->
      <div id="dockPanelSpectrum" class="h-full hidden px-4 py-2 flex items-center gap-4">
        <div class="flex-1 h-full relative">
          <canvas id="spectrumChart"></canvas>
        </div>
        <div class="w-48 bg-space-950 p-2 rounded border border-space-700 font-mono text-[10px] space-y-1 shrink-0">
          <div class="text-gray-400 font-bold uppercase text-[9px] text-cyan-400">Molecular Absorption</div>
          <div class="flex justify-between"><span class="text-cyan-300">H₂O:</span><span>1.4 μm / 1.9 μm</span></div>
          <div class="flex justify-between"><span class="text-emerald-400">CH₄:</span><span>3.3 μm</span></div>
          <div class="flex justify-between"><span class="text-orange-400">CO₂:</span><span>4.3 μm</span></div>
          <div class="flex justify-between"><span class="text-purple-400">CO:</span><span>4.7 μm</span></div>
        </div>
      </div>

      <!-- PANEL 3: LIGHT CURVE (Multi-Epoch Historical Flux) -->
      <div id="dockPanelLightCurve" class="h-full hidden px-4 py-2 flex items-center gap-4">
        <div class="flex-1 h-full relative">
          <canvas id="lightCurveChart"></canvas>
        </div>
        <div class="w-48 bg-space-950 p-2 rounded border border-space-700 font-mono text-[10px] space-y-1 shrink-0">
          <div class="text-gray-400 font-bold uppercase text-[9px] text-amber-400">Photometric History</div>
          <div class="text-gray-300 text-[10px] font-sans">
            Evaluates secular variability vs stationary constant flux across the 26.2-year baseline.
          </div>
        </div>
      </div>

    </div>
  </footer>
""")

    # 5. MODALS: CITIZEN SCIENCE DISCOVERY, NASA/CSA CODEX, COMMAND PALETTE, SHORTCUTS, TOASTS
    parts.append("""
  <!-- ========================================================================= -->
  <!-- 4. MODALS & OVERLAYS                                                      -->
  <!-- ========================================================================= -->

  <!-- CITIZEN SCIENCE DISCOVERY MODAL -->
  <div id="flagModal" class="fixed inset-0 bg-black/75 backdrop-blur-md hidden z-50 flex items-center justify-center p-4">
    <div class="bg-space-900 border border-space-700 rounded-xl max-w-md w-full p-5 shadow-2xl space-y-3 font-mono text-xs">
      <div class="flex items-center justify-between border-b border-space-700 pb-2">
        <div class="flex items-center gap-2 text-white font-bold text-sm">
          <i data-lucide="flag" class="w-4 h-4 text-blender-orange"></i>
          <span>Log Moving Object Candidate</span>
        </div>
        <button id="closeModalBtn" class="text-gray-400 hover:text-white">✕</button>
      </div>

      <div class="space-y-2 text-gray-300">
        <div>
          <label class="block text-[10px] text-gray-400 mb-1">Target / Candidate Name:</label>
          <input id="candNameInput" type="text" class="w-full bg-space-950 border border-space-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blender-orange" value="WISE 0855 Moving Candidate">
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-[10px] text-gray-400 mb-1">RA (deg):</label>
            <input id="candRAInput" type="text" class="w-full bg-space-950 border border-space-700 rounded px-2.5 py-1.5 text-white" readonly>
          </div>
          <div>
            <label class="block text-[10px] text-gray-400 mb-1">Dec (deg):</label>
            <input id="candDecInput" type="text" class="w-full bg-space-950 border border-space-700 rounded px-2.5 py-1.5 text-white" readonly>
          </div>
        </div>
        <div>
          <label class="block text-[10px] text-gray-400 mb-1">Discovered Motion Signature:</label>
          <select id="candMotionType" class="w-full bg-space-950 border border-space-700 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-blender-orange">
            <option value="high_pm">High Proper Motion (Planet X / Brown Dwarf)</option>
            <option value="optical_dipole">Optical Dipole in Difference Map</option>
            <option value="variable_star">Variable Flux Pulsation (RW Aur / Mira)</option>
            <option value="fast_transient">Fast Transient / Asteroid</option>
          </select>
        </div>
        <div class="pt-1">
          <a id="modalWiseViewLink" href="#" target="_blank" rel="noopener noreferrer" class="text-amber-300 hover:text-amber-200 hover:underline flex items-center gap-1.5 text-[10px] bg-space-950 p-2 rounded border border-space-700/80">
            <i data-lucide="external-link" class="w-3.5 h-3.5 text-blender-orange"></i>
            <span>Cross-verify candidate coordinates on NASA WiseView flipbook ↗</span>
          </a>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-2 border-t border-space-700">
        <button id="cancelModalBtn" class="px-3 py-1.5 rounded blender-btn text-gray-300">Cancel</button>
        <button id="submitCandidateBtn" class="px-3 py-1.5 rounded bg-blender-orange hover:bg-orange-600 text-white font-bold shadow transition-all">
          Record Discovery
        </button>
      </div>
    </div>
  </div>

  <!-- NASA & CSA RESOURCES CODEX & PHASE 2 VALIDATION MODAL -->
  <div id="missionCodexModal" class="fixed inset-0 bg-black/80 backdrop-blur-md hidden z-50 flex items-center justify-center p-4">
    <div class="bg-space-900 border border-space-700 rounded-xl max-w-2xl w-full p-5 shadow-2xl space-y-4 font-mono text-xs flex flex-col max-h-[85vh]">

      <!-- Codex Header -->
      <div class="flex items-center justify-between border-b border-space-700 pb-3">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-blender-orange flex items-center justify-center text-white shadow-md">
            <i data-lucide="book-open" class="w-4 h-4"></i>
          </div>
          <div>
            <h2 class="text-white font-bold text-sm tracking-wide">Mission Codex &amp; Scientific Verification</h2>
            <p class="text-[10px] text-gray-400">NASA Space Apps Challenge 2026 · Challenge: Planet X and SPHEREx</p>
          </div>
        </div>
        <button id="closeCodexBtn" class="w-7 h-7 rounded-lg flex items-center justify-center text-gray-400 hover:text-white hover:bg-space-800 transition-colors">✕</button>
      </div>

      <!-- Codex Tab Navigation -->
      <div class="flex items-center gap-1 bg-space-950 p-1 rounded-lg border border-space-700 text-xs shrink-0">
        <button id="codexTabNASA" class="blender-btn blender-btn-active px-3 py-1.5 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all">
          <i data-lucide="rocket" class="w-3.5 h-3.5 text-cyan-300"></i>
          <span>NASA Missions</span>
        </button>
        <button id="codexTabCSA" class="blender-btn px-3 py-1.5 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all">
          <i data-lucide="radar" class="w-3.5 h-3.5 text-red-400"></i>
          <span>CSA &amp; Partners</span>
        </button>
        <button id="codexTabMath" class="blender-btn px-3 py-1.5 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all">
          <i data-lucide="binary" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>Science Math &amp; Formulas</span>
        </button>
        <button id="codexTabValidation" class="blender-btn px-3 py-1.5 rounded text-[11px] font-bold flex items-center gap-1.5 transition-all">
          <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>Phase 2 Validation</span>
        </button>
      </div>

      <!-- Codex Body Content (Scrollable) -->
      <div class="flex-1 overflow-y-auto space-y-3 pr-1 text-gray-300 font-sans text-xs">

        <!-- PANEL 1: NASA Missions -->
        <div id="codexPanelNASA" class="space-y-3">
          <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5">
            <div class="flex items-center justify-between text-white font-bold text-xs font-mono">
              <span class="flex items-center gap-1.5 text-blender-orange">
                <i data-lucide="satellite" class="w-3.5 h-3.5"></i>
                NASA SPHEREx Space Observatory (2025-2028)
              </span>
              <span class="text-cyan-300 text-[10px]">0.75 – 5.0 μm</span>
            </div>
            <p class="text-[11px] text-gray-300 leading-relaxed">
              SPHEREx performs an all-sky near-infrared spectral survey across 102 individual spectrophotometric bands. Equipped with 6 detector arrays, SPHEREx detects frozen water ice ($H_2O$), carbon dioxide ice ($CO_2$), and methane ($CH_4$) in interstellar clouds and maps Planet X / Brown Dwarf candidates.
            </p>
          </div>

          <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5">
            <div class="flex items-center justify-between text-white font-bold text-xs font-mono">
              <span class="flex items-center gap-1.5 text-amber-300">
                <i data-lucide="database" class="w-3.5 h-3.5"></i>
                NASA/IPAC Infrared Science Archive (IRSA) &amp; 2MASS
              </span>
              <span class="text-emerald-400 text-[10px]">TAP / FinderChart</span>
            </div>
            <p class="text-[11px] text-gray-300 leading-relaxed">
              Hosted at Caltech/JPL, NASA IRSA serves the historical Two Micron All-Sky Survey (2MASS, 1997–2001) in $J\\ (1.25\\,\\mu\text{m})$, $H\\ (1.65\\,\\mu\text{m})$, and $K_s\\ (2.17\\,\\mu\text{m})$ bands. By subtracting 2MASS from SPHEREx across a ~26.2-year temporal baseline, sub-pixel dipoles reveal slow-moving brown dwarfs and trans-Neptunian objects.
            </p>
          </div>
        </div>

        <!-- PANEL 2: CSA & Partners -->
        <div id="codexPanelCSA" class="space-y-3 hidden">
          <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5">
            <div class="flex items-center justify-between text-white font-bold text-xs font-mono">
              <span class="flex items-center gap-1.5 text-red-400">
                <i data-lucide="satellite" class="w-3.5 h-3.5"></i>
                Canadian Space Agency NEOSSat &amp; CADC
              </span>
              <span class="text-amber-300 text-[10px]">Asteroid Tracking</span>
            </div>
            <p class="text-[11px] text-gray-300 leading-relaxed">
              The Near-Earth Object Surveillance Satellite (NEOSSat) is the world's first space telescope dedicated to detecting and tracking asteroids and satellites. The Canadian Astronomy Data Centre (CADC) provides open access to NEOSSat public archives.
            </p>
          </div>
        </div>

        <!-- PANEL 3: Science Math & Formulas -->
        <div id="codexPanelMath" class="space-y-3 hidden">
          <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5">
            <div class="text-white font-bold text-xs font-mono text-emerald-400">
              Zackay, Ofek, &amp; Gal-Yam (ZOGY 2016) Subtraction
            </div>
            <p class="text-[11px] text-gray-300 leading-relaxed font-mono">
              $$\\widehat{D} = \frac{F_r \\widehat{P}_r \\widehat{N} - F_n \\widehat{P}_n \\widehat{R}}{\\sqrt{\\sigma_n^2 F_r^2 |\\widehat{P}_r|^2 + \\sigma_r^2 F_n^2 |\\widehat{P}_n|^2}}$$
            </p>
            <p class="text-[11px] text-gray-400">
              Mathematically optimal difference imaging for telescope exposures with mismatched point spread functions (PSF) and noise properties.
            </p>
          </div>
        </div>

        <!-- PANEL 4: Phase 2 Validation -->
        <div id="codexPanelValidation" class="space-y-3 hidden">
          <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-2">
            <div class="text-white font-bold text-xs font-mono text-cyan-400 flex items-center gap-2">
              <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400"></i>
              <span>Phase 2 Scientific Validation Benchmark</span>
            </div>
            <p class="text-[11px] text-gray-300 leading-relaxed">
              Validated on authentic NASA SPHEREx flight exposures (MJD 60789.752254, Detector 6):
            </p>
            <ul class="list-disc list-inside text-[11px] text-gray-300 space-y-1 font-mono">
              <li><b>Detection Completeness Benchmark:</b> 50% recovery at $m_{\text{AB}} \approx 17.3$ ($5.0\\sigma$ ZOGY cutoff).</li>
              <li><b>False-Positive Rate:</b> 29.02 per deg² with brightness-scaled Gaia DR3 star masking.</li>
              <li><b>Known Astronomical Bodies:</b> Official IMCCE SkyBoT cross-match retrieved 54 known Solar System bodies.</li>
              <li><b>EPSF Astrometric Accuracy:</b> $0.666''$ ($0.108\text{ pixels}$) RMS against Gaia DR3 stars.</li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </div>

  <!-- COMMAND PALETTE MODAL (Ctrl+K) -->
  <div id="commandPaletteModal" class="fixed inset-0 bg-black/75 backdrop-blur-md hidden z-50 flex items-start justify-center pt-20 p-4">
    <div class="bg-space-900 border border-space-700 rounded-xl max-w-lg w-full shadow-2xl overflow-hidden font-mono text-xs">
      <div class="p-3 border-b border-space-700 flex items-center gap-2 bg-space-950">
        <i data-lucide="search" class="w-4 h-4 text-cyan-400"></i>
        <input id="commandPaletteInput" type="text" placeholder="Search targets, presets, coordinates, or modes... (Esc to exit)" class="w-full bg-transparent text-white text-xs focus:outline-none placeholder-gray-500">
        <button id="closeCommandPaletteBtn" class="text-gray-400 hover:text-white text-xs">✕</button>
      </div>
      <div id="commandPaletteList" class="max-h-80 overflow-y-auto divide-y divide-space-800 p-1">
        <!-- Populated via renderCommandPalette() -->
      </div>
    </div>
  </div>

  <!-- KEYBOARD SHORTCUTS CHEAT SHEET MODAL (?) -->
  <div id="shortcutsModal" class="fixed inset-0 bg-black/75 backdrop-blur-md hidden z-50 flex items-center justify-center p-4">
    <div class="bg-space-900 border border-space-700 rounded-xl max-w-md w-full p-5 shadow-2xl space-y-3 font-mono text-xs">
      <div class="flex items-center justify-between border-b border-space-700 pb-2">
        <span class="font-bold text-white text-sm flex items-center gap-2">
          <i data-lucide="keyboard" class="w-4 h-4 text-blender-orange"></i>
          <span>Observatory Keyboard Shortcuts</span>
        </span>
        <button id="closeShortcutsBtn" class="text-gray-400 hover:text-white">✕</button>
      </div>
      <div class="space-y-1.5 text-gray-300 text-[11px]">
        <div class="flex justify-between py-1 border-b border-space-800"><span>Blink Mode</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">B</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Difference Mode (ZOGY)</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">D</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Play / Pause Flipbook</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">Space</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Previous / Next Epoch</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">[ / ]</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Toggle Gaia DR3 Overlay</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">G</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Recenter Coordinates</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">R</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Toggle Fullscreen</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">F</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>Command Palette</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">Ctrl + K</kbd></div>
        <div class="flex justify-between py-1 border-b border-space-800"><span>WASD Walk Nav Flight</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">Shift + `</kbd></div>
        <div class="flex justify-between py-1"><span>Dismiss Modals</span><kbd class="px-1.5 py-0.5 bg-space-800 rounded border border-space-700 text-white">Esc</kbd></div>
      </div>
    </div>
  </div>

  <!-- FLOATING TOAST NOTIFICATION CONTAINER -->
  <div id="toastContainer" class="fixed bottom-16 right-4 flex flex-col gap-2 z-50 pointer-events-none"></div>
""")

    # 6. SCRIPT SECTION (Preserves all math, functions, and handlers)
    script_content = generate_script()
    parts.append(f"""
  <!-- ========================================================================= -->
  <!-- 5. APPLICATION JAVASCRIPT LOGIC                                           -->
  <!-- ========================================================================= -->
  <script>
{script_content}
  </script>
</body>
</html>
""")

    return "".join(parts)


def generate_script() -> str:
    import os
    import re

    if os.path.exists('frontend/index.html.bak'):
        with open('frontend/index.html.bak', 'r', encoding='utf-8') as f:
            bak_text = f.read()
        matches = list(re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>', bak_text, re.DOTALL))
        orig_script = matches[-1].group(1)
    else:
        with open('frontend/index.html', 'r', encoding='utf-8') as f:
            text = f.read()
        matches = list(re.finditer(r'<script(?![^>]*src)[^>]*>(.*?)</script>', text, re.DOTALL))
        script_full = matches[-1].group(1)
        if '// NEW UI STATE & TAB MANAGERS' in script_full:
            return script_full
        orig_script = script_full

    addon_script = """
    // =========================================================================
    // NEW UI STATE & TAB MANAGERS (Observatory Redesign)
    // =========================================================================
    let userMode = localStorage.getItem('spherex_user_mode') || 'beginner'; // 'beginner' | 'scientist'

    function updateUserModeUI() {
      const lbl = document.getElementById('userModeLabel');
      if (lbl) lbl.innerText = userMode === 'scientist' ? 'Scientist' : 'Beginner';
      document.body.classList.toggle('mode-scientist', userMode === 'scientist');
    }

    const btnToggleUserMode = document.getElementById('btnToggleUserMode');
    if (btnToggleUserMode) {
      btnToggleUserMode.addEventListener('click', () => {
        userMode = (userMode === 'beginner') ? 'scientist' : 'beginner';
        localStorage.setItem('spherex_user_mode', userMode);
        updateUserModeUI();
        showToast(`Switched to ${userMode === 'scientist' ? 'Scientist (Advanced)' : 'Beginner'} Mode`);
      });
    }

    // INSPECTOR 4-TAB SWITCHER
    const tabLayersBtn = document.getElementById('tabLayersBtn');
    const tabTargetBtn = document.getElementById('tabTargetBtn');
    const tabCandidatesBtn = document.getElementById('tabCandidatesBtn');
    const tabPhotometryBtn = document.getElementById('tabPhotometryBtn');

    const panelLayers = document.getElementById('inspectorPanelLayers');
    const panelTarget = document.getElementById('inspectorPanelTarget');
    const panelCandidates = document.getElementById('inspectorPanelCandidates');
    const panelPhotometry = document.getElementById('inspectorPanelPhotometry');

    function switchInspectorTab(activeBtn, activePanel) {
      const tabs = [tabLayersBtn, tabTargetBtn, tabCandidatesBtn, tabPhotometryBtn].filter(Boolean);
      const panels = [panelLayers, panelTarget, panelCandidates, panelPhotometry].filter(Boolean);

      tabs.forEach(t => t.classList.remove('blender-btn-active'));
      panels.forEach(p => p.classList.add('hidden'));

      if (activeBtn) activeBtn.classList.add('blender-btn-active');
      if (activePanel) activePanel.classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    }

    if (tabLayersBtn) tabLayersBtn.addEventListener('click', () => switchInspectorTab(tabLayersBtn, panelLayers));
    if (tabTargetBtn) tabTargetBtn.addEventListener('click', () => switchInspectorTab(tabTargetBtn, panelTarget));
    if (tabCandidatesBtn) {
      tabCandidatesBtn.addEventListener('click', () => {
        switchInspectorTab(tabCandidatesBtn, panelCandidates);
        loadDiscoveries();
      });
    }
    if (tabPhotometryBtn) tabPhotometryBtn.addEventListener('click', () => switchInspectorTab(tabPhotometryBtn, panelPhotometry));

    // BOTTOM DOCK 3-TAB SWITCHER & COLLAPSE
    const dockTabTimeline = document.getElementById('dockTabTimeline');
    const dockTabSpectrum = document.getElementById('dockTabSpectrum');
    const dockTabLightCurve = document.getElementById('dockTabLightCurve');

    const dockPanelTimeline = document.getElementById('dockPanelTimeline');
    const dockPanelSpectrum = document.getElementById('dockPanelSpectrum');
    const dockPanelLightCurve = document.getElementById('dockPanelLightCurve');
    const dockContentBody = document.getElementById('dockContentBody');
    const btnToggleDock = document.getElementById('btnToggleDock');
    const dockCollapseIcon = document.getElementById('dockCollapseIcon');

    let isDockCollapsed = false;

    function switchDockTab(activeBtn, activePanel) {
      const tabs = [dockTabTimeline, dockTabSpectrum, dockTabLightCurve].filter(Boolean);
      const panels = [dockPanelTimeline, dockPanelSpectrum, dockPanelLightCurve].filter(Boolean);

      tabs.forEach(t => t.classList.remove('blender-btn-active'));
      panels.forEach(p => p.classList.add('hidden'));

      if (activeBtn) activeBtn.classList.add('blender-btn-active');
      if (activePanel) activePanel.classList.remove('hidden');

      if (isDockCollapsed) {
        toggleDockCollapse(false);
      }
      if (window.lucide) lucide.createIcons();
    }

    function toggleDockCollapse(forceState = null) {
      isDockCollapsed = (forceState !== null) ? forceState : !isDockCollapsed;
      if (isDockCollapsed) {
        dockContentBody.style.height = '0px';
        if (dockCollapseIcon) dockCollapseIcon.setAttribute('data-lucide', 'chevron-up');
      } else {
        dockContentBody.style.height = '144px';
        if (dockCollapseIcon) dockCollapseIcon.setAttribute('data-lucide', 'chevron-down');
      }
      if (window.lucide) lucide.createIcons();
    }

    if (dockTabTimeline) dockTabTimeline.addEventListener('click', () => switchDockTab(dockTabTimeline, dockPanelTimeline));
    if (dockTabSpectrum) {
      dockTabSpectrum.addEventListener('click', () => {
        switchDockTab(dockTabSpectrum, dockPanelSpectrum);
        if (specChart) specChart.resize();
      });
    }
    if (dockTabLightCurve) {
      dockTabLightCurve.addEventListener('click', () => {
        switchDockTab(dockTabLightCurve, dockPanelLightCurve);
        initLightCurveChart();
      });
    }
    if (btnToggleDock) btnToggleDock.addEventListener('click', () => toggleDockCollapse());

    // COORDINATES POPOVER TOGGLE
    const btnToggleCoordsPopover = document.getElementById('btnToggleCoordsPopover');
    const coordsPopover = document.getElementById('coordsPopover');
    const btnCloseCoordsPopover = document.getElementById('btnCloseCoordsPopover');

    if (btnToggleCoordsPopover && coordsPopover) {
      btnToggleCoordsPopover.addEventListener('click', (e) => {
        e.stopPropagation();
        coordsPopover.classList.toggle('hidden');
      });
      if (btnCloseCoordsPopover) {
        btnCloseCoordsPopover.addEventListener('click', () => coordsPopover.classList.add('hidden'));
      }
      document.addEventListener('click', (e) => {
        if (!coordsPopover.contains(e.target) && !btnToggleCoordsPopover.contains(e.target)) {
          coordsPopover.classList.add('hidden');
        }
      });
    }

    // TOP FETCH BUTTON
    const btnTopFetch = document.getElementById('btnTopFetch');
    if (btnTopFetch) {
      btnTopFetch.addEventListener('click', () => {
        slewToTypedCoordinates();
      });
    }

    // GUIDED TOUR BANNER
    const guidedTourBanner = document.getElementById('guidedTourBanner');
    const btnDismissTour = document.getElementById('btnDismissTour');
    const btnStartTourBlink = document.getElementById('btnStartTourBlink');

    if (localStorage.getItem('spherex_tour_seen')) {
      if (guidedTourBanner) guidedTourBanner.classList.add('hidden');
    }

    if (btnDismissTour) {
      btnDismissTour.addEventListener('click', () => {
        if (guidedTourBanner) guidedTourBanner.classList.add('hidden');
        localStorage.setItem('spherex_tour_seen', 'true');
      });
    }

    if (btnStartTourBlink) {
      btnStartTourBlink.addEventListener('click', () => {
        if (guidedTourBanner) guidedTourBanner.classList.add('hidden');
        localStorage.setItem('spherex_tour_seen', 'true');
        diffMode = false;
        startFlipbook();
      });
    }

    // CANDIDATE ALERT STRIP
    const candidateAlertStrip = document.getElementById('candidateAlertStrip');
    const btnDismissCandidateAlert = document.getElementById('btnDismissCandidateAlert');
    if (btnDismissCandidateAlert && candidateAlertStrip) {
      btnDismissCandidateAlert.addEventListener('click', () => {
        candidateAlertStrip.classList.add('hidden');
      });
    }

    // COMMAND PALETTE (Ctrl+K)
    const btnOpenCommandPalette = document.getElementById('btnOpenCommandPalette');
    const commandPaletteModal = document.getElementById('commandPaletteModal');
    const commandPaletteInput = document.getElementById('commandPaletteInput');
    const commandPaletteList = document.getElementById('commandPaletteList');
    const closeCommandPaletteBtn = document.getElementById('closeCommandPaletteBtn');

    function openCommandPalette() {
      if (!commandPaletteModal) return;
      commandPaletteModal.classList.remove('hidden');
      renderCommandPalette('');
      if (commandPaletteInput) {
        commandPaletteInput.value = '';
        setTimeout(() => commandPaletteInput.focus(), 50);
      }
      if (window.lucide) lucide.createIcons();
    }

    function closeCommandPalette() {
      if (commandPaletteModal) commandPaletteModal.classList.add('hidden');
    }

    function renderCommandPalette(query) {
      if (!commandPaletteList) return;
      const q = query.toLowerCase().trim();
      let items = [
        { label: "WISE 0855-0714", desc: "Cold Y-Dwarf (~250 K), 8.15 \\\"/yr proper motion", action: () => selectTarget('wise0855'), icon: 'crosshair' },
        { label: "Barnard's Star", desc: "High Proper Motion Red Dwarf (10.36 \\\"/yr)", action: () => selectTarget('barnard'), icon: 'crosshair' },
        { label: "Epsilon Indi B", desc: "Binary Brown Dwarf (T1+T6)", action: () => selectTarget('epsindi'), icon: 'crosshair' },
        { label: "RW Aurigae", desc: "Young T-Tauri Eruptive Variable", action: () => selectTarget('rwaur'), icon: 'crosshair' },
        { label: "R Draconis", desc: "Mira Pulsating Red Giant", action: () => selectTarget('rdraconis'), icon: 'crosshair' },
        { label: "View Mode: Multi-Epoch Blink", desc: "Compare multi-epoch flipbook frames", action: () => { wsBlink.click(); }, icon: 'split' },
        { label: "View Mode: Difference Imaging", desc: "Numerical ZOGY subtraction (I₂ - I₁)", action: () => { wsDiff.click(); }, icon: 'layers' },
        { label: "View Mode: 102-Band Spectroscopy", desc: "SPHEREx 0.75-5.0 μm spectral profile", action: () => { wsSpec.click(); }, icon: 'activity' },
        { label: "View Mode: Aladin Sky Map", desc: "CDS Strasbourg interactive all-sky view", action: () => { wsAladin.click(); }, icon: 'globe' },
        { label: "Mission Codex & Verification", desc: "Phase 2 Validation benchmark report", action: () => { btnOpenValidation.click(); }, icon: 'check-circle-2' },
        { label: "Toggle Gaia DR3 Astrometry", desc: "Display proper motion vectors & cross-matches", action: () => { toggleGaia.click(); }, icon: 'sparkles' },
        { label: "Export Discoveries CSV", desc: "Download flagged candidate catalogue", action: () => { exportDiscoveriesCSV(); }, icon: 'download' },
      ];

      if (q) {
        items = items.filter(it => it.label.toLowerCase().includes(q) || it.desc.toLowerCase().includes(q));
      }

      let html = '';
      if (items.length === 0) {
        html = `<div class="p-4 text-center text-gray-500 font-mono text-xs">No matching actions or targets found.</div>`;
      } else {
        items.forEach((it, idx) => {
          html += `
            <div class="palette-item p-2.5 hover:bg-space-800 rounded cursor-pointer flex items-center justify-between text-xs transition" data-idx="${idx}">
              <div class="flex items-center gap-2">
                <i data-lucide="${it.icon}" class="w-4 h-4 text-blender-orange shrink-0"></i>
                <div>
                  <div class="text-white font-semibold">${escapeHtml(it.label)}</div>
                  <div class="text-[10px] text-gray-400 font-sans">${escapeHtml(it.desc)}</div>
                </div>
              </div>
              <span class="text-[9px] text-gray-500 font-mono">Select ↵</span>
            </div>
          `;
        });
      }
      commandPaletteList.innerHTML = html;

      commandPaletteList.querySelectorAll('.palette-item').forEach(el => {
        el.addEventListener('click', () => {
          const idx = parseInt(el.getAttribute('data-idx'));
          items[idx].action();
          closeCommandPalette();
        });
      });
      if (window.lucide) lucide.createIcons();
    }

    if (btnOpenCommandPalette) btnOpenCommandPalette.addEventListener('click', openCommandPalette);
    if (closeCommandPaletteBtn) closeCommandPaletteBtn.addEventListener('click', closeCommandPalette);
    if (commandPaletteInput) {
      commandPaletteInput.addEventListener('input', (e) => renderCommandPalette(e.target.value));
    }
    if (commandPaletteModal) {
      commandPaletteModal.addEventListener('click', (e) => {
        if (e.target === commandPaletteModal) closeCommandPalette();
      });
    }

    // SHORTCUTS MODAL (?)
    const btnOpenShortcuts = document.getElementById('btnOpenShortcuts');
    const shortcutsModal = document.getElementById('shortcutsModal');
    const closeShortcutsBtn = document.getElementById('closeShortcutsBtn');

    if (btnOpenShortcuts && shortcutsModal) {
      btnOpenShortcuts.addEventListener('click', () => shortcutsModal.classList.remove('hidden'));
      if (closeShortcutsBtn) closeShortcutsBtn.addEventListener('click', () => shortcutsModal.classList.add('hidden'));
      shortcutsModal.addEventListener('click', (e) => {
        if (e.target === shortcutsModal) shortcutsModal.classList.add('hidden');
      });
    }

    // TOAST NOTIFICATIONS
    function showToast(msg, type = 'info') {
      const c = document.getElementById('toastContainer');
      if (!c) return;
      const t = document.createElement('div');
      t.className = 'px-3 py-1.5 rounded-lg bg-space-900 border border-space-700 shadow-2xl text-xs font-mono text-white flex items-center gap-2 pointer-events-auto transition-all transform translate-y-2 opacity-0';
      t.innerHTML = `
        <span class="w-2 h-2 rounded-full ${type === 'error' ? 'bg-rose-500' : 'bg-blender-orange'}"></span>
        <span>${escapeHtml(msg)}</span>
      `;
      c.appendChild(t);
      setTimeout(() => {
        t.classList.remove('translate-y-2', 'opacity-0');
      }, 10);
      setTimeout(() => {
        t.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => t.remove(), 250);
      }, 3000);
    }

    // LIGHT CURVE CHART (Chart.js)
    let lightCurveChart = null;
    function initLightCurveChart() {
      const canvasLC = document.getElementById('lightCurveChart');
      if (!canvasLC || lightCurveChart) return;
      const ctxLC = canvasLC.getContext('2d');
      lightCurveChart = new Chart(ctxLC, {
        type: 'line',
        data: {
          labels: ['1999 (2MASS)', '2010 (WISE W1)', '2014 (unWISE)', '2025 (SPHEREx)'],
          datasets: [{
            label: 'Band Flux (μJy)',
            data: [1420, 1510, 1490, 1530],
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.15)',
            fill: true,
            tension: 0.2,
            pointRadius: 4,
            pointBackgroundColor: '#ea7600'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } } },
            y: { ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    // CANDIDATES DISCOVERY FETCHER
    async function loadDiscoveries() {
      const container = document.getElementById('candidatesListContainer');
      if (!container) return;

      try {
        const res = await fetch(`${BACKEND_URL}/discoveries`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (!data || data.length === 0) {
          container.innerHTML = `<div class="p-4 text-center text-gray-500 font-mono text-xs">No flagged discoveries yet. Use "Flag Discovery" to record one!</div>`;
          return;
        }

        let html = '';
        data.forEach(cand => {
          const cid = cand.candidate_id || 'SPX-CAND';
          const name = cand.target_name || cand.notes || 'Moving Candidate';
          const ra = cand.ra ? cand.ra.toFixed(5) : '--';
          const dec = cand.dec ? cand.dec.toFixed(5) : '--';
          const type = cand.object_type || 'Unknown Mover';

          html += `
            <div class="p-2.5 bg-space-950/80 rounded-lg border border-space-700/80 hover:border-space-600 transition space-y-1.5 cursor-pointer cand-item" data-ra="${ra}" data-dec="${dec}">
              <div class="flex items-center justify-between">
                <span class="font-bold text-white text-[11px] truncate max-w-[170px]">${escapeHtml(name)}</span>
                <span class="px-1.5 py-0.2 rounded text-[8px] font-mono bg-amber-950 text-amber-300 border border-amber-700">${escapeHtml(cid)}</span>
              </div>
              <div class="flex items-center justify-between text-[10px] text-gray-400">
                <span>α: ${ra}°, δ: ${dec}°</span>
                <span class="text-cyan-300 font-mono">${escapeHtml(type)}</span>
              </div>
            </div>
          `;
        });
        container.innerHTML = html;

        container.querySelectorAll('.cand-item').forEach(el => {
          el.addEventListener('click', () => {
            const ra = parseFloat(el.getAttribute('data-ra'));
            const dec = parseFloat(el.getAttribute('data-dec'));
            if (!isNaN(ra) && !isNaN(dec)) {
              camera.ra = ra;
              camera.dec = dec;
              camera.panX = 0;
              camera.panY = 0;
              updateCoordinateReadouts();
              drawFrame();
              showToast(`Centered on candidate at ${ra.toFixed(4)}°, ${dec.toFixed(4)}°`);
            }
          });
        });
      } catch (err) {
        container.innerHTML = `<div class="p-3 text-red-400 font-mono text-xs">Failed to load discoveries: ${escapeHtml(err.message)}</div>`;
      }
    }

    function exportDiscoveriesCSV() {
      window.open(`${BACKEND_URL}/discoveries/export/csv`, '_blank');
    }

    const btnExportCSV = document.getElementById('btnExportCSV');
    if (btnExportCSV) btnExportCSV.addEventListener('click', exportDiscoveriesCSV);

    const btnFlagNewCandidate = document.getElementById('btnFlagNewCandidate');
    if (btnFlagNewCandidate) {
      btnFlagNewCandidate.addEventListener('click', () => {
        if (flagCandidateBtn) flagCandidateBtn.click();
      });
    }

    // PERMALINK SYNC (URL Hash)
    function updatePermalinkHash() {
      const mode = diffMode ? 'diff' : 'blink';
      const target = currentTargetKey || 'custom';
      window.location.hash = `target=${target}&mode=${mode}&frame=${currentFrame}`;
    }

    // KEYBOARD SHORTCUTS DISPATCHER
    window.addEventListener('keydown', (e) => {
      // Ignore if inside text inputs
      const tag = document.activeElement ? document.activeElement.tagName : '';
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
        if (e.key === 'Escape') {
          document.activeElement.blur();
          closeCommandPalette();
          if (coordsPopover) coordsPopover.classList.add('hidden');
        }
        return;
      }

      // Ctrl+K / Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCommandPalette();
        return;
      }

      // '?' Cheat sheet
      if (e.key === '?') {
        e.preventDefault();
        if (shortcutsModal) shortcutsModal.classList.toggle('hidden');
        return;
      }

      // 'B' Blink Mode
      if (e.key.toLowerCase() === 'b') {
        e.preventDefault();
        wsBlink.click();
        return;
      }

      // 'D' Difference Mode
      if (e.key.toLowerCase() === 'd') {
        e.preventDefault();
        wsDiff.click();
        return;
      }

      // 'S' Spectra Mode
      if (e.key.toLowerCase() === 's') {
        e.preventDefault();
        wsSpec.click();
        return;
      }

      // 'A' Aladin Mode
      if (e.key.toLowerCase() === 'a') {
        e.preventDefault();
        wsAladin.click();
        return;
      }

      // 'G' Toggle Gaia Overlay
      if (e.key.toLowerCase() === 'g') {
        e.preventDefault();
        if (toggleGaia) toggleGaia.click();
        return;
      }

      // 'F' Fullscreen
      if (e.key.toLowerCase() === 'f') {
        e.preventDefault();
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
        return;
      }

      // '[' and ']' Previous / Next Frame
      if (e.key === '[') {
        e.preventDefault();
        document.getElementById('btnStepBack').click();
        return;
      }
      if (e.key === ']') {
        e.preventDefault();
        document.getElementById('btnStepFwd').click();
        return;
      }

      // 'R' Recenter
      if (e.key.toLowerCase() === 'r') {
        e.preventDefault();
        document.getElementById('toolRecenter').click();
        return;
      }

      // 'Esc' Close modals
      if (e.key === 'Escape') {
        closeCommandPalette();
        if (shortcutsModal) shortcutsModal.classList.add('hidden');
        if (coordsPopover) coordsPopover.classList.add('hidden');
        if (flagModal) flagModal.classList.add('hidden');
        if (missionCodexModal) missionCodexModal.classList.add('hidden');
      }
    });
    """

    adjusted_script = orig_script + "\n" + addon_script

    adjusted_script = adjusted_script.replace(
        "document.getElementById('vpTargetName').innerText = t.name;",
        """document.getElementById('vpTargetName').innerText = t.name;
      const abn = document.getElementById('activeTargetBadgeName');
      if (abn) abn.innerText = t.name;
      const tdn = document.getElementById('targetDetailName');
      if (tdn) tdn.innerText = t.name;
      const tdt = document.getElementById('targetDetailType');
      if (tdt) tdt.innerText = t.type;
      const qcl = document.getElementById('quickCoordsLabel');
      if (qcl) qcl.innerText = `${t.raDeg.toFixed(3)}°, ${t.decDeg.toFixed(3)}°`;
      updatePermalinkHash();"""
    )

    return adjusted_script

if __name__ == '__main__':
    html = build()
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated frontend/index.html ({len(html)} bytes)")
