// UX-MIRROR Auto-Generated JavaScript Fixes
// Generated: 2025-06-02T12:41:06.255926
// Accessibility and UX improvements

(function() {
  'use strict';

  // Automatically adds alt text to images

// Auto-add descriptive alt text for images missing it
function addMissingAltText() {
    const images = document.querySelectorAll('img:not([alt])');
    images.forEach((img, index) => {
        // Try to infer alt text from nearby content
        const parent = img.closest('article, section, div');
        const heading = parent?.querySelector('h1, h2, h3, h4, h5, h6');
        const figcaption = img.closest('figure')?.querySelector('figcaption');
        
        let altText = 'Decorative image';
        if (figcaption) {
            altText = figcaption.textContent.trim();
        } else if (heading) {
            altText = `Image related to: ${heading.textContent.trim()}`;
        } else if (img.src.includes('logo')) {
            altText = 'Company logo';
        }
        
        img.setAttribute('alt', altText);
        console.log(`Added alt text to image ${index + 1}: "${altText}"`);
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', addMissingAltText);


  // Initialize all fixes
  console.log('UX-MIRROR fixes applied');
})();