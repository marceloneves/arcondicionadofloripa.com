/**
 * Calculadora de consumo de ar-condicionado (kWh e R$).
 * Potência nominal em watts; inverter aplica fator médio configurável.
 */
const WHATSAPP_NUMBER = "5548988105199";
const WHATSAPP_MESSAGE =
  "Olá! Usei a calculadora de consumo de ar-condicionado no site e quero tirar uma dúvida / orçamento.";

/** BTU → potência média estimada (W), ponto médio das faixas indicadas */
const BTU_TO_WATTS_AVG = {
  "": null,
  "9000": 900,
  "12000": 1200,
  "18000": 1600,
  "24000": 2150,
  "30000": 3000
};

const form = document.getElementById("consumo-form");
const menuBtn = document.querySelector(".menu-toggle");
const nav = document.querySelector("#mainNav");
const feedback = document.getElementById("form-feedback");
const resultCard = document.getElementById("resultado-card");
const elWatts = document.getElementById("potencia-watts");
const elBtu = document.getElementById("btu-preset");
const elHours = document.getElementById("horas-dia");
const elDays = document.getElementById("dias-mes");
const elTariff = document.getElementById("tarifa-kwh");
const elTipoConv = document.getElementById("tipo-convencional");
const elTipoInv = document.getElementById("tipo-inverter");
const elInvPct = document.getElementById("inverter-pct");
const grupoInv = document.getElementById("grupo-inverter-pct");
const btnClear = document.getElementById("btn-limpar");
const btnCopy = document.getElementById("btn-copiar");
const ctaWhatsappBtn = document.getElementById("cta-whatsapp");
const footerWhatsappBtn = document.getElementById("footer-whatsapp");

const outKwhDia = document.getElementById("out-kwh-dia");
const outKwhMes = document.getElementById("out-kwh-mes");
const outCustoDia = document.getElementById("out-custo-dia");
const outCustoMes = document.getElementById("out-custo-mes");
const outResumo = document.getElementById("out-resumo-texto");
const outExplica = document.getElementById("out-explicacao");

let lastCopyText = "";

function getWhatsappUrl(message) {
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
}

function parseNumberBR(value) {
  if (value == null || String(value).trim() === "") return NaN;
  const s = String(value).trim().replace(/\s/g, "").replace(/\./g, "").replace(",", ".");
  return Number(s);
}

function formatKwh(n) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(n);
}

function formatBRL(n) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(n);
}

function toggleInverterGroup() {
  const show = elTipoInv.checked;
  grupoInv.hidden = !show;
  elInvPct.disabled = !show;
}

function applyBtuPreset() {
  const key = elBtu.value;
  const w = BTU_TO_WATTS_AVG[key];
  if (w != null) {
    elWatts.value = String(w);
  }
}

function setFeedback(msg, ok = false) {
  feedback.textContent = msg;
  feedback.classList.toggle("ok", ok);
}

function getEffectiveWatts() {
  const nominal = parseFloat(elWatts.value);
  if (!Number.isFinite(nominal) || nominal <= 0) return { error: "Informe a potência em watts (valor maior que zero)." };

  if (elTipoInv.checked) {
    const pct = parseFloat(elInvPct.value);
    if (!Number.isFinite(pct) || pct <= 0 || pct > 100) {
      return { error: "O percentual de uso médio do inverter deve estar entre 1 e 100." };
    }
    return {
      nominal,
      effective: nominal * (pct / 100),
      pct
    };
  }

  return { nominal, effective: nominal, pct: null };
}

function validate() {
  const w = getEffectiveWatts();
  if (w.error) return w;

  const horas = parseFloat(elHours.value);
  if (!Number.isFinite(horas) || horas <= 0 || horas > 24) {
    return { error: "Horas de uso por dia deve ser maior que zero e no máximo 24 (ex.: 8 ou 8,5)." };
  }

  const dias = parseInt(elDays.value, 10);
  if (!Number.isFinite(dias) || dias < 1 || dias > 31) {
    return { error: "Dias de uso no mês deve ser entre 1 e 31." };
  }

  const tarifa = parseNumberBR(elTariff.value);
  if (!Number.isFinite(tarifa) || tarifa < 0) {
    return { error: "Informe a tarifa de energia em R$/kWh (ex.: 0,85 ou 0.85)." };
  }

  return { ...w, horas, dias, tarifa };
}

function calcular() {
  const v = validate();
  if (v.error) {
    setFeedback(v.error, false);
    resultCard.hidden = true;
    return;
  }

  const kwhDia = (v.effective / 1000) * v.horas;
  const kwhMes = kwhDia * v.dias;
  const custoDia = kwhDia * v.tarifa;
  const custoMes = kwhMes * v.tarifa;

  outKwhDia.textContent = `${formatKwh(kwhDia)} kWh`;
  outKwhMes.textContent = `${formatKwh(kwhMes)} kWh`;
  outCustoDia.textContent = formatBRL(custoDia);
  outCustoMes.textContent = formatBRL(custoMes);

  const tipoTxt = elTipoInv.checked
    ? `inverter (${v.pct}% da potência nominal como média de uso)`
    : "convencional (potência nominal em uso contínuo)";

  outResumo.textContent = `Com base nos dados informados, seu ar-condicionado pode consumir aproximadamente ${formatKwh(
    kwhMes
  )} kWh por mês, com custo estimado de ${formatBRL(custoMes)}.`;

  const wEff = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(v.effective);
  const wNom = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(v.nominal);
  const tarifaTxt = formatBRL(v.tarifa).replace(/\s/g, " ");

  outExplica.textContent = `Cálculo: potência efetiva usada = ${wEff} W (${tipoTxt}; nominal ${wNom} W). Consumo diário = (${wEff} ÷ 1000) × ${v.horas} h = ${formatKwh(
    kwhDia
  )} kWh. Consumo mensal = ${formatKwh(kwhDia)} × ${v.dias} dias = ${formatKwh(kwhMes)} kWh. Custo mensal = ${formatKwh(
    kwhMes
  )} kWh × ${tarifaTxt}/kWh ≈ ${formatBRL(custoMes)}.`;

  lastCopyText = [
    outResumo.textContent,
    "",
    `Consumo diário: ${formatKwh(kwhDia)} kWh`,
    `Consumo mensal: ${formatKwh(kwhMes)} kWh`,
    `Custo diário: ${formatBRL(custoDia)}`,
    `Custo mensal: ${formatBRL(custoMes)}`
  ].join("\n");

  setFeedback("Cálculo atualizado.", true);
  resultCard.hidden = false;
}

function exemploInicial() {
  elBtu.value = "12000";
  applyBtuPreset();
  elHours.value = "8";
  elDays.value = "30";
  elTariff.value = "0,92";
  elTipoInv.checked = true;
  elTipoConv.checked = false;
  elInvPct.value = "70";
  toggleInverterGroup();
}

function limpar() {
  elBtu.value = "";
  elWatts.value = "";
  elHours.value = "";
  elDays.value = "";
  elTariff.value = "";
  elTipoConv.checked = true;
  elTipoInv.checked = false;
  elInvPct.value = "70";
  toggleInverterGroup();
  setFeedback("");
  resultCard.hidden = true;
  exemploInicial();
  calcular();
}

async function copiarResultado() {
  if (!lastCopyText) {
    setFeedback("Calcule antes de copiar o resultado.", false);
    return;
  }
  try {
    await navigator.clipboard.writeText(lastCopyText);
    setFeedback("Texto copiado para a área de transferência.", true);
  } catch {
    setFeedback("Não foi possível copiar automaticamente. Selecione o texto manualmente.", false);
  }
}

if (menuBtn && nav) {
  menuBtn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

elBtu.addEventListener("change", () => {
  applyBtuPreset();
});

elTipoConv.addEventListener("change", toggleInverterGroup);
elTipoInv.addEventListener("change", toggleInverterGroup);

form.addEventListener("submit", (e) => {
  e.preventDefault();
  calcular();
});

btnClear.addEventListener("click", (e) => {
  e.preventDefault();
  limpar();
});

btnCopy.addEventListener("click", (e) => {
  e.preventDefault();
  copiarResultado();
});

if (ctaWhatsappBtn) ctaWhatsappBtn.href = getWhatsappUrl(WHATSAPP_MESSAGE);
if (footerWhatsappBtn) footerWhatsappBtn.href = getWhatsappUrl(WHATSAPP_MESSAGE);

exemploInicial();
calcular();
