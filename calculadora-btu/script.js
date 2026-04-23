// Link base do WhatsApp (edite facilmente se precisar trocar o número)
const WHATSAPP_NUMBER = "5548988105199";
const WHATSAPP_MESSAGE =
  "Olá! Fiz a simulação na calculadora de BTU e quero um orçamento para ar-condicionado.";

const COMMERCIAL_CAPACITIES = [9000, 12000, 18000, 22000, 24000, 30000, 36000, 48000, 60000];

const form = document.getElementById("btu-form");
const menuBtn = document.querySelector(".menu-toggle");
const nav = document.querySelector("#mainNav");
const feedback = document.getElementById("form-feedback");
const resultCard = document.getElementById("resultado-card");
const resultArea = document.getElementById("resultado-area");
const resultBtu = document.getElementById("resultado-btu");
const resultCapacity = document.getElementById("resultado-capacidade");
const resultRecommended = document.getElementById("resultado-recomendado");
const resultMessage = document.getElementById("resultado-mensagem");
const resultWhatsappBtn = document.getElementById("resultado-whatsapp");
const ctaWhatsappBtn = document.getElementById("cta-whatsapp");
const footerWhatsappBtn = document.getElementById("footer-whatsapp");

function formatNumber(value) {
  return new Intl.NumberFormat("pt-BR").format(Math.round(value));
}

function formatArea(value) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2
  }).format(value);
}

function getWhatsappUrl(message) {
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;
}

function getRecommendedCapacity(estimatedBtu) {
  for (const cap of COMMERCIAL_CAPACITIES) {
    if (estimatedBtu <= cap) return cap;
  }
  return COMMERCIAL_CAPACITIES[COMMERCIAL_CAPACITIES.length - 1];
}

function setGlobalWhatsappLinks() {
  const url = getWhatsappUrl(WHATSAPP_MESSAGE);
  ctaWhatsappBtn.href = url;
  footerWhatsappBtn.href = url;
}

function validatePositiveNumber(value, fieldLabel, min = 0) {
  if (Number.isNaN(value)) return `${fieldLabel} é obrigatório.`;
  if (value < min) return `${fieldLabel} não pode ser menor que ${min}.`;
  return "";
}

function buildResultMessage(capacity) {
  return `Para esse ambiente, a recomendação estimada é um ar-condicionado de ${formatNumber(
    capacity
  )} BTUs. Para uma indicação mais precisa, o ideal é solicitar uma avaliação técnica.`;
}

form.addEventListener("submit", function onSubmit(event) {
  event.preventDefault();
  feedback.textContent = "";

  const largura = Number(document.getElementById("largura").value);
  const comprimento = Number(document.getElementById("comprimento").value);
  const pessoas = Number(document.getElementById("pessoas").value);
  const eletronicos = Number(document.getElementById("eletronicos").value);
  const solar = document.getElementById("solar").value;
  const ambiente = document.getElementById("ambiente").value;
  const janelas = Number(document.getElementById("janelas").value);
  const cobertura = document.getElementById("cobertura").value;
  const uso = document.getElementById("uso").value;

  const errors = [
    validatePositiveNumber(largura, "Largura do ambiente", 0.1),
    validatePositiveNumber(comprimento, "Comprimento do ambiente", 0.1),
    validatePositiveNumber(pessoas, "Quantidade de pessoas", 1),
    validatePositiveNumber(eletronicos, "Quantidade de eletrônicos", 0),
    validatePositiveNumber(janelas, "Quantidade de janelas", 0)
  ].filter(Boolean);

  if (!solar || !ambiente || !cobertura || !uso) {
    errors.push("Preencha todos os campos obrigatórios da calculadora.");
  }

  if (errors.length > 0) {
    feedback.textContent = errors[0];
    resultCard.hidden = true;
    return;
  }

  const area = largura * comprimento;
  let estimatedBtu = area * 600;

  // Pessoas adicionais além da primeira
  if (pessoas > 1) {
    estimatedBtu += (pessoas - 1) * 600;
  }

  // Cada eletrônico que gera calor
  estimatedBtu += eletronicos * 600;

  // Janelas
  estimatedBtu += janelas * 300;

  // Ajustes por exposição e perfil do ambiente
  if (solar === "media") estimatedBtu *= 1.1;
  if (solar === "alta") estimatedBtu *= 1.2;
  if (cobertura === "sim") estimatedBtu *= 1.1;
  if (uso === "comercial") estimatedBtu *= 1.1;
  if (["escritorio", "loja", "comercio"].includes(ambiente)) estimatedBtu *= 1.1;

  const recommendedCapacity = getRecommendedCapacity(estimatedBtu);
  const message = buildResultMessage(recommendedCapacity);

  resultArea.textContent = `${formatArea(area)} m²`;
  resultBtu.textContent = `${formatNumber(estimatedBtu)} BTUs`;
  resultCapacity.textContent = `${formatNumber(recommendedCapacity)} BTUs`;
  resultRecommended.textContent = `Capacidade sugerida: ${formatNumber(recommendedCapacity)} BTUs`;
  resultMessage.textContent = message;

  const dynamicWhatsappMessage = `${WHATSAPP_MESSAGE} Resultado da simulação: área ${formatArea(
    area
  )} m², BTU estimado ${formatNumber(estimatedBtu)} e capacidade sugerida ${formatNumber(
    recommendedCapacity
  )} BTUs.`;
  resultWhatsappBtn.href = getWhatsappUrl(dynamicWhatsappMessage);

  resultCard.hidden = false;
  resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
});

setGlobalWhatsappLinks();

if (menuBtn && nav) {
  menuBtn.addEventListener("click", function toggleMenu() {
    const isOpen = nav.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(isOpen));
  });
}
