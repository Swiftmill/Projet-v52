window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toast').forEach((toast) => {
    setTimeout(() => {
      toast.classList.add('hide');
    }, 4000);
  });
});
