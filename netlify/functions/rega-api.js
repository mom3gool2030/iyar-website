const REGA_BASE = "https://rentalrei.rega.gov.sa/RegaIndicatorsAPIs/api/IndicatorEjar";

let cachedToken = null;
let tokenExpiry = null;

async function getToken() {
  if (cachedToken && tokenExpiry && Date.now() < tokenExpiry) {
    return cachedToken;
  }
  const res = await fetch(REGA_BASE + "/GetToken", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}"
  });
  const token = await res.text();
  cachedToken = token.trim().replace(/"/g, "");
  tokenExpiry = Date.now() + 50 * 60 * 1000;
  return cachedToken;
}

exports.handler = async function(event) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Type": "application/json"
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers, body: "" };
  }

  try {
    var path = event.path.replace("/.netlify/functions/rega-api", "");
    var endpoint = path.replace(/^\//, "");
    var qs = event.rawQuery ? "?" + event.rawQuery : "";

    if (!endpoint) {
      return { statusCode: 400, headers, body: JSON.stringify({ error: "no endpoint" }) };
    }

    var token = await getToken();

    var regaRes = await fetch(REGA_BASE + "/" + endpoint + qs, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      }
    });

    var data = await regaRes.json();
    return { statusCode: 200, headers, body: JSON.stringify(data) };

  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};
