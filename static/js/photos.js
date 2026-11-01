/**
 * Initialize photo preview modal behavior.
 */
function initPhotoPreview() {
  const modal = new bootstrap.Modal(document.getElementById('photoPreviewModal'));
  const modalImg = document.getElementById('photoPreviewImg');
  const caption = document.getElementById('photoPreviewCaption');

  document.querySelectorAll('.photo-card img').forEach(img => {
    img.addEventListener('click', () => {
      const parent = img.closest('.photo-card');
      const meta = parent.querySelector('.photo-meta') || parent.querySelector('.photo-overlay');

      // Grab metadata (e.g. caption, visibility, username).
      const text = meta ? meta.textContent.trim() : "";

      modalImg.src = img.src;
      caption.textContent = text;

      modal.show();
    });
  });
}

