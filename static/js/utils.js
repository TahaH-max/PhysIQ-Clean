/**
 * Read a named cookie value for CSRF or auth.
 * @param {string} name
 * @returns {string|null}
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Fetch HTML content and return response text.
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<string>}
 */
function fetchHtml(url, options = {}) {
  return fetch(url, options).then(r => {
    if (!r.ok) throw new Error('Failed to load content');
    return r.text();
  });
}

/**
 * POST JSON data and return parsed JSON.
 * @param {string} url
 * @param {object} data
 * @returns {Promise<any>}
 */
function postJson(url, data) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(data),
  }).then(r => r.json());
}

/**
 * POST form data and return response text.
 * @param {string} url
 * @param {object} data
 * @returns {Promise<string>}
 */
function postHtml(url, data) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(data),
  }).then(r => {
    if (!r.ok) throw new Error('Failed to load content');
    return r.text();
  });
}

