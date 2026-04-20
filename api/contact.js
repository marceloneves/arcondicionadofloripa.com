function withCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function validatePayload(payload) {
  const nome = (payload.nome || "").trim();
  const telefone = (payload.telefone || "").trim();
  const bairro = (payload.bairro || "").trim();
  const servico = (payload.servico || "").trim();
  const mensagem = (payload.mensagem || "").trim();

  if (!nome) return "Informe seu nome.";
  if (!/^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$/.test(telefone.replace(/\s+/g, ""))) {
    return "Informe um telefone valido com DDD.";
  }
  if (!bairro) return "Selecione um bairro.";
  if (!servico) return "Selecione um servico.";
  if (mensagem.length < 10) return "Descreva sua necessidade com pelo menos 10 caracteres.";
  return "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

module.exports = async function handler(req, res) {
  withCors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Metodo nao permitido." });
  }

  const errorMessage = validatePayload(req.body || {});
  if (errorMessage) {
    return res.status(400).json({ error: errorMessage });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.RESEND_FROM_EMAIL;
  const to = process.env.CONTACT_TO_EMAIL || "marcelo@arcondicionadofloripa.com";

  if (!apiKey || !from) {
    return res.status(500).json({ error: "Configuracao de e-mail incompleta no servidor." });
  }

  const { nome, telefone, bairro, servico, mensagem } = req.body;

  const html = `
    <h2>Novo contato pelo site</h2>
    <p><strong>Nome:</strong> ${escapeHtml(nome)}</p>
    <p><strong>Telefone:</strong> ${escapeHtml(telefone)}</p>
    <p><strong>Bairro:</strong> ${escapeHtml(bairro)}</p>
    <p><strong>Servico:</strong> ${escapeHtml(servico)}</p>
    <p><strong>Mensagem:</strong></p>
    <p>${escapeHtml(mensagem).replaceAll("\n", "<br>")}</p>
  `;

  const resendResponse = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [to],
      subject: `Novo lead: ${servico} - ${bairro}`,
      reply_to: from,
      html,
      text: `Novo contato pelo site\n\nNome: ${nome}\nTelefone: ${telefone}\nBairro: ${bairro}\nServico: ${servico}\nMensagem:\n${mensagem}`,
    }),
  });

  if (!resendResponse.ok) {
    const resendError = await resendResponse.text();
    return res.status(502).json({ error: "Falha no envio de e-mail.", details: resendError });
  }

  return res.status(200).json({ ok: true });
};
