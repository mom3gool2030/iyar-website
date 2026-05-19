const REGA_BASE = "https://rentalrei.rega.gov.sa/RegaIndicatorsAPIs/api/IndicatorEjar";

let cachedToken = null;
let tokenExpiry = null;

async function getToken() {
  if (cachedToken && tokenExpiry && Date.now() < tokenExpiry) {
    return cachedToken;
  }

  const res = await fetch(`${REGA_BASE}/GetToken`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Origin": "https://rentalrei.rega.gov.sa"
    },
    body: JSON.stringify({})
  });

  if (!res.ok) throw new Error("فشل في الحصول على التوكن");

  const token = await res.text();
  cachedToken = token.trim().replace(/"/g, "");
  tokenExpiry = Date.now() + 50 * 60 * 1000;

  return cachedToken;
}

exports.handler = async function (event) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Typ
