const PROXY_BASE = "/.netlify/functions/rega-api";

const RegaService = {

  async getDistricts(cityId = 21) {
    try {
      const res = await fetch(`${PROXY_BASE}/GetDistrictsByCityId?cityId=${cityId}`);
      if (!res.ok) throw new Error("فشل جلب الأحياء");
      return await res.json();
    } catch (err) {
      console.error("getDistricts error:", err);
      return null;
    }
  },

  async getDetails(districtId, propertyType = 1) {
    try {
      const res = await fetch(`${PROXY_BASE}/GetDetailsV2?districtId=${districtId}&propertyType=${propertyType}`);
      if (!res.ok) throw new Error("فشل جلب التفاصيل");
      return await res.json();
    } catch (err) {
      console.error("getDetails error:", err);
      return null;
    }
  },

  async getChartData(districtId, propertyType = 1) {
    try {
      const res = await fetch(`${PROXY_BASE}/GetChartClassicIndicatorEjar?districtId=${districtId}&propertyType=${propertyType}`);
      if (!res.ok) throw new Error("فشل جلب الرسم البياني");
      return await res.json();
    } catch (err) {
      console.error("getChartData error:", err);
      return null;
    }
  },

  formatPrice(value) {
    if (!value && value !== 0) return "غير متوفر";
    return new Intl.NumberFormat("ar-SA", {
      style: "currency",
      currency: "SAR",
      maximumFractionDigits: 0
    }).format(value);
  }
};

window.RegaService = RegaService;
