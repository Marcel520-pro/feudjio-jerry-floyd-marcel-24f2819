document.querySelectorAll('input[type="range"]').forEach(slider => {
  const display = document.getElementById(slider.id + '_val');
  if (display) {
    display.textContent = slider.value;
    slider.addEventListener('input', () => { display.textContent = slider.value; });
  }
});

const form = document.getElementById('enquete-form');
if (form) {
  form.addEventListener('submit', e => {
    const required = form.querySelectorAll('[required]');
    let ok = true;
    required.forEach(field => {
      if (!field.value.trim()) {
        field.style.borderColor = '#e84393';
        ok = false;
      } else {
        field.style.borderColor = '';
      }
    });
    if (!ok) {
      e.preventDefault();
      document.querySelector('[style*="e84393"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
}
