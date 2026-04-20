function withCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function validatePayload(payload) {
  const nome = (payload.nome || "").trim();
  const email = (payload.email || "").trim();
  const telefone = (payload.telefone || "").trim();
  const cidade = (payload.cidade || "").trim();
  const servico = (payload.servico || "").trim();
  const mensagem = (payload.mensagem || "").trim();

  if (!nome) return "Informe seu nome.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Informe um e-mail valido.";
  if (!/^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$/.test(telefone.replace(/\s+/g, ""))) {
    return "Informe um telefone valido com DDD.";
  }
  if (!cidade) return "Selecione uma cidade.";
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

function firstNonEmptyEnv(names) {
  for (const name of names) {
    const value = process.env[name];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return "";
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

  const apiKey = firstNonEmptyEnv(["RESEND_API_KEY", "RESEND_KEY"]);
  const from = firstNonEmptyEnv(["RESEND_FROM_EMAIL", "FROM_EMAIL", "CONTACT_FROM_EMAIL"]);
  const to = firstNonEmptyEnv(["CONTACT_TO_EMAIL", "RESEND_TO_EMAIL"]) || "marcelo@arcondicionadofloripa.com";

  if (!apiKey || !from) {
    return res.status(500).json({
      error: "Configuracao de e-mail incompleta no servidor.",
      missing: {
        resendApiKey: !apiKey,
        resendFromEmail: !from,
      },
    });
  }

  const { nome, email, telefone, cidade, servico, mensagem } = req.body;

  const html = `
    <h2>Novo contato pelo site</h2>
    <p><strong>Nome:</strong> ${escapeHtml(nome)}</p>
    <p><strong>E-mail:</strong> ${escapeHtml(email)}</p>
    <p><strong>Telefone:</strong> ${escapeHtml(telefone)}</p>
    <p><strong>Cidade:</strong> ${escapeHtml(cidade)}</p>
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
      subject: `Novo lead: ${servico} - ${cidade}`,
      reply_to: email,
      html,
      text: `Novo contato pelo site\n\nNome: ${nome}\nE-mail: ${email}\nTelefone: ${telefone}\nCidade: ${cidade}\nServico: ${servico}\nMensagem:\n${mensagem}`,
    }),
  });

  if (!resendResponse.ok) {
    const resendError = await resendResponse.text();
    return res.status(502).json({ error: "Falha no envio de e-mail.", details: resendError });
  }

  return res.status(200).json({ ok: true });
};
