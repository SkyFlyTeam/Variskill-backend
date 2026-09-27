"use strict";

const swaggerSettings = {{ settings|safe }};

function getCookie(name) {
  const prefix = name + "=";
  for (const cookie of document.cookie.split(";")) {
    const value = cookie.trim();
    if (value.startsWith(prefix)) {
      return decodeURIComponent(value.slice(prefix.length));
    }
  }
  return "";
}

const requestInterceptor = (request) => {
  if (!["GET", undefined].includes(request.method)) {
    const csrfToken = getCookie("csrftoken");
    request.headers["X-Csrftoken"] = csrfToken;
    // Swagger's generated curl only includes explicit headers. The browser
    // itself ignores manually setting Cookie, but curl receives it here.
    request.headers["Cookie"] = "csrftoken=" + csrfToken;
  }
  return request;
};

const ui = SwaggerUIBundle({
  url: "{{ schema_url|escapejs }}",
  dom_id: "#swagger-ui",
  presets: [SwaggerUIBundle.presets.apis],
  layout: "BaseLayout",
  requestInterceptor,
  ...swaggerSettings,
});
