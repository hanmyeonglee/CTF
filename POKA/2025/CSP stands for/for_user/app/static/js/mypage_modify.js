(function () {
  const dialog   = document.getElementById('dialog');
  if (!dialog) return;

  const postForm = document.getElementById('postForm');
  const cancelBtn = document.getElementById('cancelBtn');
  const confirmBtn = document.getElementById('confirmBtn');

  const showPopup = dialog.dataset.showPopup === 'true';

  if (showPopup) {
    dialog.classList.add('show');
  }

  cancelBtn && cancelBtn.addEventListener('click', () => {
    dialog.classList.remove('show');
  });

  confirmBtn && confirmBtn.addEventListener('click', () => {
    postForm && postForm.submit();
  });
})();

document.addEventListener('DOMContentLoaded', function () {
  const query = QueryParser.parseQuery(window.location.search || "");
  const { username, email } = query;

  const renderText = txt => `${sanitizeHtml(txt)}`;
  const setHTML = (id, val) => {
    const el = document.getElementById(id);
    if (el && typeof val !== 'undefined') {
      el.innerHTML = renderText(String(val));
    }
  };

  const actions = [
    () => setHTML('r_username', username),
    () => setHTML('r_email', email)
  ];

  actions.forEach(fn => fn());
});
