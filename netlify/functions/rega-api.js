const BASE = "https://rentalrei.rega.gov.sa/RegaIndicatorsAPIs/api/IndicatorEjar";

var BROWSER_HEADERS = {
  "Content-Type": "application/json",
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Referer": "https://rentalrei.rega.gov.sa/",
  "Origin": "https://rentalrei.rega.gov.sa"
};

exports.handler = async function(event) {
  var h = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Type": "application/json"
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: h, body: "" };
  }

  try {
    var tokenRes = await fetch(BASE + "/GetToken", {
      method: "POST",
      headers: BROWSER_HEADERS,
      body: "{}"
    });
    var token = (await tokenRes.text()).replace(/"/g, "").trim();

    var seg = event.path.split("/rega-api/")[1] || "";
    var qs = event.rawQuery ? "?" + event.rawQuery : "";
    var url = BASE + "/" + seg + qs;

    var res = await fetch(url, {
      method: "GET",
      headers: Object.assign({}, BROWSER_HEADERS, {
        "Authorization": "Bearer " + token
      })
    });

    var data = await res.json();
    return { statusCode: 200, headers: h, body: JSON.stringify(data) };

  } catch (e) {
    return { statusCode: 500, headers: h, body: JSON.stringify({ error: e.message }) };
  }
};
