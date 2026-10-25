// Change these values to customize the defaults for every visitor.
// Only theme and grid can be changed in the on-page panel.
window.PHISHGUARD_CONFIG = {
  theme: 'paper',             // paper | noir | acid
  accent: '#466457',         // Any CSS hex color
  headline: 'DON\'T TRUST<br><span class="hero-italic">the</span> <span class="outlined">link.</span>',
  motion: 65,                // 0..100
  grid: true,
  grain: true,
  cursor: true,
  smoothScroll: true,
  apiEndpoint: '/analyze',   // Use same-origin FastAPI endpoint
  scanPhrases: ['READING THE SIGNAL', 'EXAMINING THE PATTERN', 'CONNECTING THE DOTS'],
  scanMinDurationMs: 1400,   // Animation time, not artificial model inference
};
