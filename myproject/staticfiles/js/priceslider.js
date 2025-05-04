
function initializePriceSlider() {
    const priceSlider = document.getElementById('priceSlider');
    
    // Only initialize if slider exists on page
    if (!priceSlider) return;
  
    noUiSlider.create(priceSlider, {
      start: [
        parseInt(priceSlider.dataset.min || 0),
        parseInt(priceSlider.dataset.max || 20000)
      ],
      connect: true,
      range: {
        'min': 0,
        'max': 20000
      },
      tooltips: false,
    });
  
    const minInput = document.getElementById('min_price');
    const maxInput = document.getElementById('max_price');
    const minDisplay = document.getElementById('minPriceValue');
    const maxDisplay = document.getElementById('maxPriceValue');
  
    priceSlider.noUiSlider.on('update', function (values) {
      const min = Math.round(values[0]);
      const max = Math.round(values[1]);
  
      if (minInput) minInput.value = min;
      if (maxInput) maxInput.value = max;
      if (minDisplay) minDisplay.textContent = min;
      if (maxDisplay) maxDisplay.textContent = max;
    });
  }
  
  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', initializePriceSlider);