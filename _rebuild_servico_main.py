# -*- coding: utf-8 -*-
"""Regenera páginas servico/*: <main> (8 seções), <title>, meta description, canonical e JSON-LD (Service + FAQ num bloco)."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from _fix_html_root_paths import apply_relative_paths_to_file
from _brand import LOGO_URL as BUSINESS_LOGO_URL
from _social_meta import insert_social_meta_after_description

root = Path(__file__).parent
BASE_URL = "https://arcondicionadofloripa.com"
# JSON-LD: um bloco Service + FAQPage com provider, breadcrumb e mainEntity (FAQ).
BUSINESS_ID = f"{BASE_URL}/#empresa"
BUSINESS_NAME = "Ar Condicionado Floripa"
BUSINESS_IMAGE = f"{BASE_URL}/images/ar-condicionado-florianopolis.webp"
BUSINESS_STREET = "Rodovia Armando Calil Bullos, 630"
BUSINESS_NEIGHBORHOOD = "Vargem Grande"
BUSINESS_POSTAL = "88056-618"
FOUNDING_DATE = "2021-04-06"
bairros_html = (root / "regioes" / "index.html").read_text(encoding="utf-8")

# Rodapé idêntico ao de index.html. Após gravar, apply_relative_paths_to_file() ajusta /… para ../…
SITE_FOOTER_HTML = """<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h3>Ar Condicionado em Florianópolis</h3>
      <p>Atendimento técnico e rápido para instalação, manutenção, limpeza, higienização, carga de gás e reinstalação em Florianópolis desde 2021.</p>
    </div>
    <div><h4>Institucional</h4><ul><li><a href="https://arcondicionadofloripa.com/">Início</a></li><li><a href="https://arcondicionadofloripa.com/servicos/">Serviços</a></li><li><a href="/regioes/">Regiões Atendidas</a></li><li><a href="/quem-somos/">Quem Somos</a></li><li><a href="https://arcondicionadofloripa.com/blog/">Blog</a></li><li><a href="/contato/">Contato</a></li><li><a href="/politica-de-privacidade/">Política de Privacidade</a></li></ul></div>
    <div><h4>Serviços</h4><ul><li><a href="/servico/instalacao-de-ar-condicionado-em-florianopolis/">Instalação de Ar-Condicionado</a></li><li><a href="/servico/manutencao-de-ar-condicionado-em-florianopolis/">Manutenção de Ar-Condicionado</a></li><li><a href="/servico/limpeza-de-ar-condicionado-em-florianopolis/">Limpeza de Ar-Condicionado</a></li><li><a href="/servico/higienizacao-de-ar-condicionado-em-florianopolis/">Higienização de Ar-Condicionado</a></li><li><a href="/servico/carga-de-gas-de-ar-condicionado-em-florianopolis/">Carga de Gás de Ar-Condicionado</a></li><li><a href="/servico/remocao-e-reinstalacao-de-ar-condicionado-em-florianopolis/">Remoção e Reinstalação de Ar-Condicionado</a></li><li><a href="/servico/conserto-de-ar-condicionado-em-florianopolis/">Conserto de Ar-Condicionado</a></li><li><a href="/servico/pmoc-de-ar-condicionado-em-florianopolis/">PMOC de Ar-Condicionado</a></li></ul></div>
    <div><h4>Cidades</h4><ul><li><a href="/servicos/#servicos-florianopolis">Florianópolis</a></li><li><a href="/regioes/#sao-jose">São José</a></li><li><a href="/regioes/#biguacu">Biguaçu</a></li><li><a href="/regioes/#palhoca">Palhoça</a></li></ul></div>
  </div>
  <div class="container footer-bottom"><p class="footer-address">Rodovia Armando Calil Bullos, 630 — Vargem Grande, Florianópolis - SC, 88056-618</p><p>© 2026 Ar Condicionado em Florianópolis. Todos os direitos reservados.</p><p><a href="tel:+5548988105199">(48) 98810-5199</a></p><p>Fale conosco: <a href="mailto:marcelo@arcondicionadofloripa.com">marcelo@arcondicionadofloripa.com</a></p></div>
</footer>"""


def patch_footer_servico(html: str) -> str:
    new_html, c = re.subn(
        r'<footer\s+class="site-footer">.*?</footer>',
        SITE_FOOTER_HTML,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if c != 1:
        print("Aviso: rodapé não substituído em página de serviço (esperado 1 footer):", c)
    return new_html

# id -> nome, prep (do texto do card)
# `[^<]+` no fragmento evita atravessar </p> e capturar o próximo card (cidades SC vêm antes dos bairros).
pat_card = re.compile(
    r'<article class="card" id="([^"]+)"><h2>([^<]+)</h2><p>Atendimento técnico de ar-condicionado (no|na|em|nos|nas) ([^<]+), em Florianópolis, para residência e comércio\.</p>',
)
BAIRROS = {}
for bid, nome, prep, frag in pat_card.findall(bairros_html):
    BAIRROS[bid] = {"nome": nome, "prep": prep}

PERTO = {
    "centro": ["trindade", "itacorubi"],
    "trindade": ["itacorubi", "santa-monica"],
    "itacorubi": ["trindade", "corrego-grande"],
    "agronomica": ["centro", "trindade"],
    "santa-monica": ["itacorubi", "corrego-grande"],
    "corrego-grande": ["santa-monica", "pantanal"],
    "pantanal": ["carvoeira", "trindade"],
    "carvoeira": ["pantanal", "saco-dos-limoes"],
    "saco-dos-limoes": ["carvoeira", "costeira-do-pirajubae"],
    "joao-paulo": ["monte-verde", "itacorubi"],
    "monte-verde": ["joao-paulo", "saco-dos-limoes"],
    "lagoa-da-conceicao": ["barra-da-lagoa", "rio-tavares"],
    "barra-da-lagoa": ["lagoa-da-conceicao", "sao-joao-do-rio-vermelho"],
    "campeche": ["rio-tavares", "morro-das-pedras"],
    "rio-tavares": ["campeche", "lagoa-da-conceicao"],
    "morro-das-pedras": ["campeche", "armacao"],
    "armacao": ["morro-das-pedras", "pantano-do-sul"],
    "pantano-do-sul": ["armacao", "ribeirao-da-ilha"],
    "tapera": ["ribeirao-da-ilha", "costeira-do-pirajubae"],
    "ribeirao-da-ilha": ["tapera", "pantano-do-sul"],
    "costeira-do-pirajubae": ["saco-dos-limoes", "tapera"],
    "estreito": ["coqueiros", "capoeiras"],
    "coqueiros": ["estreito", "abraao"],
    "capoeiras": ["estreito", "jardim-atlantico"],
    "abraao": ["coqueiros", "capoeiras"],
    "jardim-atlantico": ["capoeiras", "estreito"],
    "ingleses": ["cachoeira-do-bom-jesus", "santinho"],
    "cachoeira-do-bom-jesus": ["canasvieiras", "ingleses"],
    "canasvieiras": ["jurere", "cachoeira-do-bom-jesus"],
    "jurere": ["jurere-internacional", "canasvieiras"],
    "jurere-internacional": ["jurere", "daniela"],
    "daniela": ["jurere-internacional", "santo-antonio-de-lisboa"],
    "santo-antonio-de-lisboa": ["sambaqui", "daniela"],
    "sambaqui": ["santo-antonio-de-lisboa", "ratones"],
    "ratones": ["vargem-grande", "sambaqui"],
    "vargem-grande": ["vargem-pequena", "ratones"],
    "vargem-pequena": ["vargem-grande", "ingleses"],
    "sao-joao-do-rio-vermelho": ["barra-da-lagoa", "ingleses"],
    "praia-brava": ["cachoeira-do-bom-jesus", "canasvieiras"],
    "santinho": ["ingleses", "sao-joao-do-rio-vermelho"],
    "balneario": ["centro", "agronomica"],
    "bom-abrigo": ["centro", "saco-dos-limoes"],
    "cacupe": ["jose-mendes", "carianos"],
    "canto": ["centro", "agronomica"],
    "carianos": ["cacupe", "coloninha"],
    "coloninha": ["carianos", "estreito"],
    "itaguacu": ["coqueiros", "estreito"],
    "jardim-capoeiras": ["capoeiras", "monte-cristo"],
    "jose-mendes": ["cacupe", "saco-grande"],
    "mocambique": ["saco-grande", "rio-vermelho"],
    "monte-cristo": ["jardim-capoeiras", "capoeiras"],
    "ponta-das-canas": ["canasvieiras", "praia-do-forte"],
    "praia-do-forte": ["ponta-das-canas", "jurere"],
    "rio-vermelho": ["mocambique", "saco-grande"],
    "saco-grande": ["jose-mendes", "mocambique"],
    "tapera-da-base": ["estreito", "coqueiros"],
    "vargem-do-bom-jesus": ["vargem-grande", "ratones"],
}

# Cidades da Grande Florianópolis (páginas servico com sufixo -sc.html)
CIDADES: dict[str, dict[str, str]] = {
    "sao-jose": {"nome": "São José", "prep": "em"},
    "palhoca": {"nome": "Palhoça", "prep": "em"},
    "biguacu": {"nome": "Biguaçu", "prep": "em"},
}

CIDADE_VIZINHAS: dict[str, list[str]] = {
    "sao-jose": ["palhoca", "biguacu"],
    "palhoca": ["sao-jose", "biguacu"],
    "biguacu": ["sao-jose", "palhoca"],
}

for cid, meta in CIDADES.items():
    if cid in BAIRROS:
        raise SystemExit(f"ID de região duplicado entre bairros e cidades: {cid}")
    BAIRROS[cid] = {"nome": meta["nome"], "prep": meta["prep"]}

# Página agregada da capital (sem hubs por bairro): servico/*-em-florianopolis.html
BAIRROS["florianopolis"] = {"nome": "Florianópolis", "prep": "em"}

SERVICE_KEYS = (
    "remocao-e-reinstalacao-de-ar-condicionado",
    "higienizacao-de-ar-condicionado",
    "carga-de-gas-de-ar-condicionado",
    "instalacao-de-ar-condicionado",
    "manutencao-de-ar-condicionado",
    "limpeza-de-ar-condicionado",
    "conserto-de-ar-condicionado",
    "pmoc-de-ar-condicionado",
)

SERV_META = {
    "instalacao-de-ar-condicionado": {
        "titulo": "Instalação de Ar-Condicionado",
        "curto": "instalação de ar-condicionado",
        "verbo": "instalar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">Em <strong>Florianópolis</strong>, capital de <strong>Santa Catarina</strong>, a <strong>climatização</strong> na <strong>Ilha de Santa Catarina</strong> combina umidade, salinidade em algumas frentes e uso intenso de <strong>ar-condicionado split</strong>, <strong>multi-split</strong> e <strong>inverter</strong>. '
            "{sent} <strong>{nome}</strong>, o serviço técnico costuma envolver <strong>linha frigorígena</strong> em <strong>tubulação de cobre</strong>, <strong>dreno de condensado</strong>, <strong>vácuo</strong>, <strong>teste de estanqueidade</strong> quando aplicável, <strong>fixação</strong> da <strong>unidade condensadora</strong> e <strong>alimentação elétrica</strong> compatível com o fabricante — sempre alinhado a boas práticas de <strong>HVAC</strong> e segurança.</p>"
        ),
        "oque": "A instalação de ar-condicionado é o serviço técnico que posiciona evaporadora e condensadora, executa tubulação, dreno e conexões elétricas seguindo normas e boas práticas de climatização.",
        "lista": (
            "primeiro equipamento no imóvel ou ampliação de pontos de climatização;",
            "troca de aparelho antigo por modelo novo;",
            "instalação de equipamento split ou multi-split;",
            "definição de rota de tubulação e dreno com melhor estética e segurança;",
            "adequação de suportes, furos e vedações;",
            "instalação em apartamento, casa ou comércio com análise de fachada e área técnica.",
        ),
        "como_passos": (
            ("Contato", "Você informa endereço {prep} {nome}, tipo de imóvel e necessidade (quartos, ambientes, BTUs desejados)."),
            ("Avaliação técnica", "Avaliamos carga térmica, posição da evaporadora e da condensadora, rota de tubulação e infraestrutura elétrica."),
            ("Orçamento", "Enviamos escopo e previsão de execução, com transparência sobre o que está incluso."),
            ("Execução", "Instalamos com testes de vazamento, vácuo quando aplicável, dreno funcionando e orientação de uso."),
        ),
        "porque": (
            "Menos ruído e melhor rendimento quando a instalação é feita corretamente.",
            "Mais segurança elétrica e estrutural, com fixações e dreno adequados.",
            "Maior vida útil do equipamento e menos retrabalho.",
            "Conforto térmico estável para residências e empresas {prep} {nome}.",
        ),
        "preco_txt": "O investimento varia conforme capacidade do equipamento (BTUs), número de ambientes, tipo de estrutura (parede, laje, fachada), extensão de tubulação, necessidade de suporte adicional e complexidade do acesso. Por isso, o valor mais correto sai após uma avaliação rápida do local.",
        "preco_lista": (
            "distância entre unidades interna e externa e percurso de tubulação;",
            "necessidade de eletroduto, registro, dreno com bomba ou extensão;",
            "horário e urgência do atendimento;",
            "tipo de condensadora e exigências do condomínio ou imóvel comercial.",
        ),
        "contratar_ofertas": (
            "planejamento técnico antes da perfuração e da fixação;",
            "orientação sobre capacidade ideal para o ambiente;",
            "execução organizada, com foco em limpeza e segurança;",
            "testes ao final do serviço e explicação do uso básico do controle.",
        ),
        "vantagens": (
            "Processo padronizado, com checklist técnico e comunicação clara.",
            "Menos improviso: tubulação, dreno e elétrica bem resolvidos desde o início.",
            "Atendimento para perfis diferentes: apartamento, casa, loja e escritório.",
            "Suporte para dúvidas após a instalação, conforme combinado no atendimento.",
        ),
        "onde_txt": "Atendemos ruas e conjuntos residenciais, comércio de bairro, condomínios e fluxos de circulação próximos {prep} {nome}, em Florianópolis, sempre respeitando regras de condomínio e orientações de área técnica quando existirem.",
        "faq_extra": (
            ("Vocês instalam split inverter {prep} {nome}?", "Sim, atendemos instalação de equipamentos convencionais e inverter, conforme projeto do ambiente."),
            ("Instalam em apartamento com restrição de fachada?", "Sim, avaliamos a melhor rota técnica e as opções permitidas pelo condomínio."),
            ("Quanto tempo leva uma instalação simples?", "Em muitos casos, a execução ocorre no mesmo dia, dependendo da complexidade e do horário agendado."),
        ),
    },
    "manutencao-de-ar-condicionado": {
        "titulo": "Manutenção de Ar-Condicionado",
        "curto": "manutenção de ar-condicionado",
        "verbo": "manter",
        "contexto_seo": (
            '<p class="servico-contexto-seo">A <strong>manutenção de ar-condicionado</strong> em <strong>Florianópolis</strong> (SC) costuma cruzar <strong>manutenção preventiva</strong> e <strong>corretiva</strong>, inspeção de <strong>pressões de trabalho</strong>, comportamento do <strong>compressor</strong>, <strong>motor-ventilador</strong>, <strong>dreno</strong> e <strong>superaquecimento</strong> relativo. '
            "{sent} <strong>{nome}</strong>, o objetivo é preservar o <strong>circuito frigorífico</strong>, reduzir retrabalho e manter o conforto térmico em <strong>residências</strong>, <strong>comércios</strong> e <strong>condomínios</strong> na <strong>Grande Florianópolis</strong>.</p>"
        ),
        "oque": "A manutenção de ar-condicionado é o serviço que revisa o funcionamento do sistema, identifica desgastes e ajusta pontos críticos para reduzir falhas e melhorar o desempenho.",
        "lista": (
            "queda de desempenho ou ar menos frio;",
            "barulhos diferentes do habitual;",
            "vazamento na bandeja ou umidade em volta da evaporadora;",
            "cheiro desagradável ao ligar o aparelho;",
            "consumo de energia alto para o padrão de uso;",
            "revisão preventiva após um período de uso intenso.",
        ),
        "como_passos": (
            ("Agendamento", "Você informa o sintoma e o modelo do equipamento {prep} {nome}."),
            ("Inspeção", "Verificamos pressões, dreno, elétrica básica, sujeira e funcionamento dos ventiladores."),
            ("Correções e limpeza técnica", "Executamos ajustes necessários e limpeza compatível com o estado do aparelho."),
            ("Teste final", "Ligamos o sistema e confirmamos temperatura, ruído e dreno."),
        ),
        "porque": (
            "Ajuda a evitar pane em horários de pico de calor.",
            "Melhora a eficiência e pode reduzir custo de energia em casos de sujeira ou desajuste.",
            "Antecipa componentes no limite, evitando danos maiores.",
            "Mais conforto e previsibilidade para quem mora ou trabalha {prep} {nome}.",
        ),
        "preco_txt": "O valor da manutenção varia conforme tipo de equipamento, altura de instalação, necessidade de reposição de pequenos itens, grau de sujeira e se há correções adicionais. Solicite avaliação para um orçamento objetivo.",
        "preco_lista": (
            "necessidade de limpeza profunda ou desobstrução de dreno;",
            "reposição de componentes simples (quando aplicável);",
            "deslocamento e tempo de permanência no local;",
            "manutenção preventiva x corretiva (complexidade diferente).",
        ),
        "contratar_ofertas": (
            "diagnóstico claro antes de qualquer intervenção;",
            "relatório simples do que foi verificado e ajustado;",
            "recomendações de periodicidade para o seu perfil de uso;",
            "atendimento para residências e empresas {prep} {nome}.",
        ),
        "vantagens": (
            "Menos improviso: procedimento técnico e organizado.",
            "Mais segurança ao lidar com elétrica, dreno e partes móveis.",
            "Melhor desempenho após correções e limpeza adequada.",
            "Redução de risco de parada em momentos críticos.",
        ),
        "onde_txt": "Atendemos condomínios, comércios e residências {prep} {nome}, com deslocamento planejado para regiões próximas em Florianópolis.",
        "faq_extra": (
            ("Manutenção evita vazamento?", "Muitas vezes sim, pois dreno obstruído ou posicionamento incorreto é causa comum de água no ambiente."),
            ("Vocês emitem nota e detalham o serviço?", "Sim, combinamos isso no contato inicial, conforme sua necessidade."),
        ),
    },
    "limpeza-de-ar-condicionado": {
        "titulo": "Limpeza de Ar-Condicionado",
        "curto": "limpeza de ar-condicionado",
        "verbo": "limpar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">A <strong>limpeza técnica</strong> atua em <strong>filtro de ar</strong>, <strong>serpentina</strong> acessível, <strong>rodá</strong> (ventilador radial) e <strong>bandeja</strong>, melhorando <strong>vazão de ar</strong> e sensação de frescor. '
            "Em <strong>Florianópolis</strong>, <strong>Santa Catarina</strong>, {sent} <strong>{nome}</strong>, o acúmulo de poeira e umidade na <strong>evaporadora</strong> é comum em períodos de calor e vento — cenário típico de <strong>climatização</strong> na <strong>Ilha de Santa Catarina</strong>.</p>"
        ),
        "oque": "A limpeza de ar-condicionado remove sujeira acumulada em filtros, serpentina acessível e bandeja, melhorando fluxo de ar e rendimento térmico.",
        "lista": (
            "filtro muito sujo ou com odor;",
            "queda de vazão de ar;",
            "sujeira visível na grade ou na evaporadora;",
            "manutenção leve entre visitas técnicas completas;",
            "melhoria rápida de conforto após períodos de poeira;",
            "preparação do aparelho antes de higienização mais profunda.",
        ),
        "como_passos": (
            ("Agendamento", "Você informa modelo e tempo desde a última limpeza."),
            ("Proteção do ambiente", "Preparamos o entorno para evitar respingos e sujeira no imóvel."),
            ("Limpeza técnica", "Atuamos em filtros e áreas críticas conforme o tipo de aparelho."),
            ("Finalização", "Testamos funcionamento e orientamos periodicidade ideal."),
        ),
        "porque": (
            "Melhora a sensação de frescor com menos esforço do equipamento.",
            "Reduz odores causados por poeira e umidade parada na bandeja.",
            "Ajuda a manter a qualidade do ar em ambientes fechados.",
            "Pode ser combinada com manutenção ou higienização, conforme necessidade.",
        ),
        "preco_txt": "O preço costuma variar com o tipo de equipamento (janela, split, cassete), altura da instalação e nível de sujeira. Em geral, quanto mais tempo sem limpeza técnica, maior pode ser o tempo de serviço.",
        "preco_lista": (
            "quantidade de evaporadoras no mesmo atendimento;",
            "acesso difícil ou necessidade de andaime/escada alta;",
            "necessidade de desmontagem parcial de grelhas ou acabamentos;",
            "combinação com outros serviços no mesmo dia.",
        ),
        "contratar_ofertas": (
            "limpeza focada em rendimento e higiene básica do ar;",
            "orientação de uso e frequência sugerida;",
            "atendimento ágil para comércios e escritórios {prep} {nome};",
            "possibilidade de agendar em horários de menor movimento.",
        ),
        "vantagens": (
            "Serviço objetivo, com menos interrupção na sua rotina.",
            "Melhora perceptível em odor e fluxo de ar em muitos casos.",
            "Evita que sujeira extrema leve a danos e consumo elevado.",
            "Bom custo-benefício quando feita na periodicidade correta.",
        ),
        "onde_txt": "Atendemos residências e empresas {prep} {nome}, incluindo pontos comerciais de bairro e escritórios em Florianópolis.",
        "faq_extra": (
            ("Limpeza resolve mau cheiro?", "Muitas vezes reduz bastante, mas odores persistentes podem exigir higienização mais profunda."),
            ("Quanto tempo dura o serviço?", "Depende do modelo e do estado do aparelho; combinamos uma faixa estimada no contato."),
        ),
    },
    "higienizacao-de-ar-condicionado": {
        "titulo": "Higienização de Ar-Condicionado",
        "curto": "higienização de ar-condicionado",
        "verbo": "higienizar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">A <strong>higienização de ar-condicionado</strong> reforça a <strong>qualidade do ar interno</strong> (IAQ), atuando em <strong>odor</strong>, <strong>biofilme</strong> e resíduos que escapam à limpeza superficial da <strong>evaporadora</strong>. '
            "{sent} <strong>{nome}</strong>, em <strong>Florianópolis</strong> (SC), o serviço costuma ser buscado em <strong>apartamentos</strong>, <strong>consultórios</strong>, <strong>escritórios</strong> e <strong>comércio</strong> — ambientes onde <strong>HVAC</strong> e conforto térmico impactam diretamente a rotina na <strong>Ilha de Santa Catarina</strong>.</p>"
        ),
        "oque": "A higienização é um serviço mais profundo, voltado a reduzir biofilme, odores e contaminantes em componentes internos, com foco em qualidade do ar e conforto.",
        "lista": (
            "cheiro forte ao ligar o aparelho;",
            "alergias ou sensibilidade a poeira em ambientes fechados;",
            "aparelho em locais úmidos ou pouco ventilados;",
            "após reformas com muita poeira;",
            "rotina de higiene para clínicas, consultórios e salas comerciais;",
            "preparação para alta temporada de uso.",
        ),
        "como_passos": (
            ("Diagnóstico rápido", "Entendemos o tipo de odor/sintoma e o modelo do equipamento."),
            ("Preparação", "Protegemos móveis e realizamos isolamento do ponto de serviço."),
            ("Higienização técnica", "Aplicamos procedimento compatível com o tipo de evaporadora e estado do sistema."),
            ("Teste e orientação", "Validamos funcionamento e indicamos periodicidade."),
        ),
        "porque": (
            "Melhora a percepção de ar mais limpo em ambientes sensíveis.",
            "Reduz odores que limpeza superficial não resolve.",
            "Ajuda a manter boa convivência em apartamentos e salas pequenas.",
            "Complementa a manutenção técnica em imóveis {prep} {nome}.",
        ),
        "preco_txt": "O valor depende do tipo de sistema, do nível de contaminação e do tempo necessário para desmontagem parcial de acessórios. Sempre combinamos escopo antes da execução.",
        "preco_lista": (
            "número de unidades internas atendidas no mesmo dia;",
            "altura e dificuldade de acesso;",
            "necessidade de tratamento mais demorado por odor persistente;",
            "combinação com limpeza ou manutenção.",
        ),
        "contratar_ofertas": (
            "procedimento técnico com foco em segurança e organização;",
            "explicação do que será feito e o que não está incluso;",
            "atendimento para residências e empresas {prep} {nome};",
            "agenda com horários combinados para reduzir transtorno.",
        ),
        "vantagens": (
            "Mais bem-estar em ambientes com crianças, idosos ou alérgicos.",
            "Reduz incômodo de odores em visitas e reuniões.",
            "Melhora a sensação geral do ar condicionado.",
            "Processo conduzido por equipe com foco técnico.",
        ),
        "onde_txt": "Atendemos imóveis e empresas {prep} {nome} em Florianópolis, com deslocamento planejado para regiões vizinhas quando necessário.",
        "faq_extra": (
            ("Higienização é a mesma coisa que limpeza?", "Não. A higienização é mais profunda e voltada a odor/contaminação; a limpeza é mais pontual em filtros e sujeira comum."),
            ("Posso usar o aparelho no mesmo dia?", "Quando aplicável, orientamos tempo de espera após o procedimento."),
        ),
    },
    "carga-de-gas-de-ar-condicionado": {
        "titulo": "Carga de Gás de Ar-Condicionado",
        "curto": "carga de gás de ar-condicionado",
        "verbo": "recarregar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">A <strong>carga de gás</strong> (ou ajuste de <strong>fluido refrigerante</strong>) deve estar ligada a <strong>diagnóstico</strong> do <strong>circuito frigorífico</strong>, checagem de <strong>vazamento</strong>, <strong>vácuo</strong> e desempenho do <strong>compressor</strong>. '
            "Em <strong>Florianópolis</strong>, <strong>Santa Catarina</strong>, {sent} <strong>{nome}</strong>, é comum associar o tema a <strong>ar menos gelado</strong>, <strong>gelo na linha</strong> e <strong>climatização</strong> em <strong>split</strong> e <strong>multi-split</strong> — sempre com foco em segurança e conformidade técnica na <strong>Ilha de Santa Catarina</strong>.</p>"
        ),
        "oque": "A carga de gás (fluido refrigerante) só deve ser feita após diagnóstico técnico. O objetivo é recuperar desempenho com quantidade correta e verificação de vazamentos quando indicado.",
        "lista": (
            "ar menos gelado do que o habitual;",
            "gelo ou formação anormal na linha;",
            "equipamento ligando e desarmando rápido (em alguns casos);",
            "queda de rendimento após anos de uso;",
            "serviço combinado com manutenção para teste completo;",
            "orientação técnica após instalação ou reparo.",
        ),
        "como_passos": (
            ("Triagem", "Coletamos sintomas, modelo e histórico do aparelho {prep} {nome}."),
            ("Testes e inspeção", "Verificamos indícios de perda e condições básicas do sistema."),
            ("Procedimento técnico", "Executamos a etapa adequada conforme diagnóstico (não é sempre só recarga)."),
            ("Validação", "Confirmamos desempenho e orientamos próximos passos se houver vazamento."),
        ),
        "porque": (
            "Evita “recarga” desnecessária, que não resolve causa raiz.",
            "Protege o compressor e melhora eficiência quando feito corretamente.",
            "Reduz risco de retrabalho e gasto duplicado.",
            "Mais segurança e conformidade com boas práticas técnicas.",
        ),
        "preco_txt": "O valor depende do tipo de gás/equipamento, da necessidade de localização de vazamento, do tempo de serviço e do deslocamento. Por isso, o orçamento correto vem após avaliação técnica.",
        "preco_lista": (
            "necessidade de solda, vácuo prolongado ou componentes;",
            "altura e dificuldade de acesso à condensadora;",
            "urgência e horário do atendimento;",
            "múltiplos aparelhos no mesmo local.",
        ),
        "contratar_ofertas": (
            "diagnóstico antes de qualquer recarga;",
            "explicação do que foi encontrado e do plano de correção;",
            "testes ao final do serviço;",
            "atendimento {prep} {nome} e regiões próximas em Florianópolis.",
        ),
        "vantagens": (
            "Transparência: você entende o motivo técnico do problema.",
            "Menos improviso e menos risco ao equipamento.",
            "Melhor desempenho quando o sistema está íntegro.",
            "Suporte para decidir reparo x troca, quando for o caso.",
        ),
        "onde_txt": "Atendemos residências, comércios e condomínios {prep} {nome}, com foco em diagnóstico correto antes de qualquer recarga.",
        "faq_extra": (
            ("Sempre precisa recarregar gás?", "Não. Se há vazamento, a correção vem antes; recarga sem diagnóstico pode mascarar o problema."),
            ("Vocês atendem finais de semana?", "Quando disponível na agenda, combinamos horário no contato."),
        ),
    },
    "remocao-e-reinstalacao-de-ar-condicionado": {
        "titulo": "Remoção e Reinstalação de Ar-Condicionado",
        "curto": "remoção e reinstalação de ar-condicionado",
        "verbo": "remover e reinstalar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">A <strong>remoção e reinstalação</strong> envolve <strong>desmontagem</strong> segura, <strong>transporte</strong> da <strong>unidade interna</strong> e <strong>condensadora</strong>, eventual <strong>recolhimento de refrigerante</strong> conforme técnica aplicável, e nova montagem com <strong>vácuo</strong>, <strong>teste</strong> e <strong>vazamento</strong> verificado. '
            "{sent} <strong>{nome}</strong>, em <strong>Florianópolis</strong> (SC), é serviço típico de <strong>mudança</strong>, <strong>reforma</strong> e <strong>readequação de fachada</strong> em <strong>condomínios</strong> na <strong>Ilha de Santa Catarina</strong>.</p>"
        ),
        "oque": "Esse serviço envolve desmontagem segura, transporte adequado do equipamento e reinstalação com novos testes, ideal para mudanças, reformas ou troca de posição das unidades.",
        "lista": (
            "mudança de imóvel mantendo o mesmo aparelho;",
            "reforma com necessidade de retirar e recolocar unidades;",
            "troca de posição da evaporadora ou da condensadora;",
            "substituição de suportes e readequação de tubulação;",
            "reinstalação após pintura de fachada em condomínio;",
            "transporte curto dentro do mesmo endereço.",
        ),
        "como_passos": (
            ("Planejamento", "Definimos melhor sequência para desmontagem e proteção do equipamento."),
            ("Desmontagem", "Recolhemos refrigerante quando necessário, conforme técnica aplicável, e desmontamos com cuidado."),
            ("Transporte e proteção", "Protegemos unidades para evitar amassados e perdas de componentes."),
            ("Reinstalação e testes", "Remontamos, fazemos vácuo/recarga conforme necessidade e testamos funcionamento."),
        ),
        "porque": (
            "Reduz risco de quebra e vazamento por manuseio incorreto.",
            "Evita perda de peças pequenas que comprometem a vedação.",
            "Garante teste final no novo ponto de instalação.",
            "Mais segurança em apartamentos e fachadas {prep} {nome}.",
        ),
        "preco_txt": "O valor varia com distância entre unidades, necessidade de novos furos/acabamentos, extensão de tubulação nova, altura e complexidade de acesso. Avaliamos o cenário e enviamos proposta fechada quando possível.",
        "preco_lista": (
            "necessidade de alongar tubulação ou refazer dreno;",
            "condomínio com regras específicas de horário e acesso;",
            "dois deslocamentos (retirada e nova instalação) no mesmo processo;",
            "equipamentos grandes ou multi-split.",
        ),
        "contratar_ofertas": (
            "execução com etapas combinadas (retirada e reinstalação);",
            "proteção do mobiliário e da área de trabalho;",
            "testes ao final e orientação pós-serviço;",
            "atendimento {prep} {nome} e regiões próximas.",
        ),
        "vantagens": (
            "Menos dor de cabeça em mudanças e reformas.",
            "Reduz chance de vazamento por conexões mal reapertadas.",
            "Melhor organização do cronograma com pedreiro/pintor.",
            "Suporte técnico para decidir o melhor novo posicionamento.",
        ),
        "onde_txt": "Atendemos imóveis {prep} {nome} e deslocamentos para bairros vizinhos em Florianópolis, conforme logística combinada.",
        "faq_extra": (
            ("Dá para reinstalar no mesmo dia?", "Em vários cenários sim, dependendo de acesso e complexidade."),
            ("Vocês desmontam para guardar o aparelho durante reforma?", "Sim, combinamos retirada e data de reinstalação."),
        ),
    },
    "conserto-de-ar-condicionado": {
        "titulo": "Conserto de Ar-Condicionado",
        "curto": "conserto de ar-condicionado",
        "verbo": "consertar",
        "contexto_seo": (
            '<p class="servico-contexto-seo">O <strong>conserto de ar-condicionado</strong> envolve <strong>diagnóstico</strong>, identificação de causa raiz e correção de falhas em componentes como <strong>placa eletrônica</strong>, <strong>compressor</strong>, <strong>ventiladores</strong>, <strong>sensores</strong> e <strong>alimentação elétrica</strong>. '
            "{sent} <strong>{nome}</strong>, em <strong>Florianópolis</strong> (SC), o foco é devolver estabilidade ao sistema com testes após a intervenção e orientação de uso.</p>"
        ),
        "oque": "O conserto de ar-condicionado é o atendimento voltado a corrigir defeitos específicos, restaurar o funcionamento do equipamento e orientar sobre a melhor forma de uso após a intervenção.",
        "lista": (
            "aparelho que não liga ou desarma logo em seguida;",
            "erros intermitentes em placa eletrônica ou sensores;",
            "ruídos anormais vindos da unidade interna ou externa;",
            "problemas recorrentes após instalação ou mudanças de local;",
            "falhas após queda de energia ou surtos elétricos;",
            "equipamento que passou por conserto anterior sem solução definitiva.",
        ),
        "como_passos": (
            ("Coleta de informações", "Você explica o sintoma, histórico recente e o tipo de equipamento {prep} {nome}."),
            ("Diagnóstico técnico", "Avaliamos comportamento do sistema, leituras básicas, histórico e indícios de defeito."),
            ("Proposta de correção", "Indicamos a linha de reparo e as possibilidades (ajuste, troca de peça, nova avaliação)."),
            ("Execução e testes", "Executamos o conserto combinado e testamos o funcionamento em diferentes condições."),
        ),
        "porque": (
            "Ajuda a resolver falhas que vão além de limpeza e manutenção leve.",
            "Permite avaliar se vale a pena reparar ou partir para troca do equipamento.",
            "Reduz o risco de paradas repetidas em horários críticos.",
            "Gera histórico técnico útil para decisões futuras {prep} {nome}.",
        ),
        "preco_txt": "O valor do conserto de ar-condicionado varia conforme o defeito encontrado, necessidade de peças, tempo de diagnóstico e acesso ao equipamento. Por isso, o orçamento correto costuma ser fechado após avaliação técnica.",
        "preco_lista": (
            "complexidade do problema identificado;",
            "necessidade de componentes de reposição e disponibilidade;",
            "acesso à unidade condensadora e evaporadora;",
            "tempo de testes e validação após o conserto.",
        ),
        "contratar_ofertas": (
            "diagnóstico estruturado antes de qualquer troca de peça;",
            "orientação clara sobre custo-benefício de reparar ou trocar;",
            "execução alinhada às recomendações do fabricante sempre que possível;",
            "atendimento {prep} {nome} e regiões próximas em Florianópolis.",
        ),
        "vantagens": (
            "Maior clareza sobre o real estado do equipamento.",
            "Redução de tentativas e erros com trocas desnecessárias.",
            "Possibilidade de prolongar a vida útil em cenários viáveis.",
            "Base técnica para decidir quando migrar para um modelo mais novo.",
        ),
        "onde_txt": "Atendemos residências, comércios e condomínios {prep} {nome} em Florianópolis, com atenção especial a acessos, regras de condomínio e segurança elétrica.",
        "faq_extra": (
            ("Vocês consertam qualquer marca?", "Atendemos principais marcas do mercado; detalhes são combinados no contato."),
            ("Sempre compensa consertar o aparelho?", "Depende da idade, estado geral e custo da peça; explicamos os prós e contras antes de decidir."),
        ),
    },
    "pmoc-de-ar-condicionado": {
        "titulo": "PMOC de Ar-Condicionado",
        "curto": "PMOC de ar-condicionado",
        "verbo": "implantar o PMOC",
        "contexto_seo": (
            '<p class="servico-contexto-seo">O <strong>PMOC</strong> (<strong>Plano de Manutenção, Operação e Controle</strong>) organiza <strong>rotinas de manutenção</strong>, <strong>registros</strong>, <strong>frequências</strong> e <strong>responsabilidades técnicas</strong> para sistemas de <strong>climatização</strong>. '
            "{sent} <strong>{nome}</strong>, em <strong>Florianópolis</strong> (SC), ele é especialmente relevante para <strong>condomínios</strong>, <strong>clínicas</strong>, <strong>escritórios</strong> e ambientes com permanência prolongada de pessoas.</p>"
        ),
        "oque": "O PMOC de ar-condicionado é o plano formal que define como serão feitas manutenção, operação e controle dos sistemas de climatização, com foco em segurança, desempenho e qualidade do ar interno.",
        "lista": (
            "empresas que precisam organizar a manutenção de vários equipamentos;",
            "condomínios com áreas comuns climatizadas;",
            "ambientes com permanência prolongada de colaboradores ou clientes;",
            "imóveis que desejam padronizar fornecedores, periodicidades e registros;",
            "adequação a exigências legais e boas práticas de climatização.",
        ),
        "como_passos": (
            ("Levantamento inicial", "Mapeamos os equipamentos, capacidades, locais de instalação e condições gerais {prep} {nome}."),
            ("Definição do plano", "Estruturamos rotinas, periodicidades e pontos de verificação alinhados ao perfil do imóvel."),
            ("Execução das rotinas", "Realizamos as manutenções previstas ou apoiamos a implementação com equipe local."),
            ("Ajustes e registros", "Ajustamos o plano conforme histórico real e mantemos registros das intervenções."),
        ),
        "porque": (
            "Ajuda a manter qualidade do ar e desempenho dos sistemas ao longo do tempo.",
            "Organiza responsabilidades técnicas e periodicidades de manutenção.",
            "Reduz improviso e paradas inesperadas em ambientes críticos.",
            "Facilita demonstração de cuidado com climatização em auditorias e vistorias.",
        ),
        "preco_txt": "O valor para elaboração e execução do PMOC depende da quantidade de equipamentos, complexidade do sistema, perfil de uso do imóvel e escopo desejado (apenas plano ou plano + execução). Por isso, o orçamento é definido após um levantamento inicial.",
        "preco_lista": (
            "número de equipamentos e capacidades envolvidas;",
            "distribuição dos aparelhos em diferentes áreas e pavimentos;",
            "nível de detalhamento e tipo de registro exigido;",
            "se o contrato inclui apenas plano ou também execução recorrente.",
        ),
        "contratar_ofertas": (
            "elaboração do plano de manutenção, operação e controle adaptado ao imóvel;",
            "apoio na execução das rotinas de PMOC conforme escopo combinado;",
            "orientação sobre uso adequado dos sistemas de climatização;",
            "atendimento {prep} {nome} e regiões próximas em Florianópolis.",
        ),
        "vantagens": (
            "Visão organizada de todos os equipamentos e necessidades.",
            "Mais previsibilidade de custos de manutenção ao longo do tempo.",
            "Melhor conforto térmico para quem usa o espaço diariamente.",
            "Apoio técnico para decisões de troca e modernização de sistemas.",
        ),
        "onde_txt": "Atendemos empresas, condomínios, comércios e espaços de serviço {prep} {nome}, em Florianópolis, que precisam estruturar ou revisar o seu PMOC de climatização.",
        "faq_extra": (
            ("PMOC é obrigatório para qualquer ambiente?", "Ele é especialmente recomendado e exigido em diversos contextos com permanência de pessoas; avaliamos seu caso no contato."),
            ("Vocês também executam as manutenções previstas no PMOC?", "Sim, quando combinado no escopo, realizamos tanto o plano quanto as rotinas de manutenção."),
        ),
    },
}

# Meta description: frases únicas por serviço (cidade × bairro) — evita texto genérico repetido e cortado no SERP.
# Tupla: (trecho para páginas em cidade/SC, trecho para páginas de bairro em Florianópolis).
SEO_META_FRAGMENTS: dict[str, tuple[str, str]] = {
    "instalacao-de-ar-condicionado": (
        "Split e multi: tubulação, dreno, vácuo e testes. Orçamento claro — chame no WhatsApp e agende visita.",
        "Tubulação e dreno conforme norma. Orçamento no bairro; resposta rápida por WhatsApp.",
    ),
    "manutencao-de-ar-condicionado": (
        "Filtros, pressões, dreno e testes. Volte a ter ar gelado com diagnóstico honesto. Peça orçamento no WhatsApp.",
        "Revisão no bairro que evita pane e alto consumo. Fale conosco e combine horário.",
    ),
    "limpeza-de-ar-condicionado": (
        "Filtros, serpentina e bandeja: mais frescor e menos odor. Serviço objetivo — solicite orçamento hoje.",
        "Mais vazão e higiene no seu split. Orçamento rápido para residência ou empresa no bairro.",
    ),
    "higienizacao-de-ar-condicionado": (
        "Elimine mau cheiro e sujeira profunda na evaporadora. Ideal para apartamento e consultório. Peça valor no WhatsApp.",
        "Tratamento profundo no bairro com escopo combinado. Entre em contato e agende.",
    ),
    "carga-de-gas-de-ar-condicionado": (
        "Recarga só após diagnóstico: vazamento, vácuo e fluido certo. Evite golpe — orçamento transparente no WhatsApp.",
        "Avaliação técnica antes de recarregar. Proteja o compressor; fale com a equipe no bairro.",
    ),
    "remocao-e-reinstalacao-de-ar-condicionado": (
        "Mudança ou obra: desmontagem segura, transporte e nova instalação com testes. Solicite orçamento sem compromisso.",
        "Protegemos equipamento e fachada. Combine retirada e reinstalação — WhatsApp.",
    ),
    "conserto-de-ar-condicionado": (
        "Placa, compressor, sensores: achamos a causa antes de trocar peça. Orçamento justo — chame no WhatsApp.",
        "Defeito no split do bairro? Diagnóstico claro e reparo com testes. Peça visita.",
    ),
    "pmoc-de-ar-condicionado": (
        "Condomínios e empresas: PMOC com rotinas e registros. Organize a climatização — peça proposta pelo WhatsApp.",
        "Periodicidade e responsáveis definidos para seu edifício. Fale com a equipe técnica.",
    ),
}

# Ajustes de seção 3/4 e títulos por tipo de serviço (evita texto de “pane” em instalação, etc.)
SEC_EXTRAS = {
    "instalacao-de-ar-condicionado": {
        "sec3_h2": "3. Por que investir em instalação técnica {pp}?",
        "sec3_intro": "Uma instalação bem planejada reduz ruído, vazamentos recorrentes e riscos elétricos associados à má execução. Também favorece melhor rendimento e conforto desde o primeiro dia de uso.",
        "sec4_fecho": "Ou seja: o orçamento mais fiel depende de <strong>onde</strong> será instalado, <strong>qual</strong> é o equipamento e qual é a <strong>complexidade</strong> (tubulação, dreno, altura e acabamentos).",
    },
    "limpeza-de-ar-condicionado": {
        "sec3_h2": "3. Por que fazer limpeza técnica {pp}?",
        "sec3_intro": "Com o tempo, sujeira e poeira reduzem a vazão de ar e podem alterar cheiro e rendimento. Uma limpeza técnica bem feita melhora a sensação de frescor e a eficiência em muitos casos.",
        "sec4_fecho": "Ou seja: o valor costuma variar com <strong>tipo de aparelho</strong>, <strong>altura e acesso</strong> e <strong>nível de sujeira</strong> acumulada.",
    },
    "higienizacao-de-ar-condicionado": {
        "sec3_h2": "3. Por que fazer higienização {pp}?",
        "sec3_intro": "Odores persistentes, sensação de ar “pesado” e ambientes sensíveis pedem um tratamento mais profundo que a limpeza comum. A higienização atua em causas comuns de mau cheiro e biofilme.",
        "sec4_fecho": "Ou seja: o orçamento depende de <strong>tipo de sistema</strong>, <strong>tempo de serviço</strong> e <strong>dificuldade de acesso</strong>, além de ser combinado por escopo.",
    },
    "carga-de-gas-de-ar-condicionado": {
        "sec3_h2": "3. Por que fazer diagnóstico antes da recarga {pp}?",
        "sec3_intro": "Perda de desempenho nem sempre significa “falta de gás”. Insistir em recarga sem diagnóstico pode mascarar vazamento e prejudicar o compressor. O caminho correto começa com teste e análise técnica.",
        "sec4_fecho": "Ou seja: o valor depende de <strong>achado técnico</strong> (recarga x vazamento x outro defeito), <strong>acesso</strong> e <strong>tempo de intervenção</strong>.",
    },
    "remocao-e-reinstalacao-de-ar-condicionado": {
        "sec3_h2": "3. Por que contratar remoção e reinstalação com técnica {pp}?",
        "sec3_intro": "Mudanças e reformas exigem desmontagem segura, proteção do equipamento e reinstalação com testes. Improviso aumenta risco de vazamento, perda de peças e retrabalho na fachada ou área técnica.",
        "sec4_fecho": "Ou seja: o orçamento considera <strong>complexidade de desmontagem</strong>, <strong>nova rota</strong> de tubulação/dreno e <strong>logística</strong> entre retirada e reinstalação.",
    },
    "conserto-de-ar-condicionado": {
        "sec3_h2": "3. Por que investir em conserto técnico {pp}?",
        "sec3_intro": "Nem todo problema se resolve com limpeza ou recarga de gás. Um conserto bem conduzido começa por diagnóstico, identifica a causa raiz e só então parte para troca de peças ou ajustes.",
        "sec4_fecho": "Ou seja: o orçamento depende de <strong>defeito encontrado</strong>, <strong>peças necessárias</strong> e <strong>tempo de testes</strong> para garantir que o problema não volte.",
    },
    "pmoc-de-ar-condicionado": {
        "sec3_h2": "3. Por que implantar o PMOC {pp}?",
        "sec3_intro": "O PMOC organiza a manutenção de forma estruturada, reduz improviso e melhora a previsibilidade do desempenho dos sistemas de climatização ao longo do ano.",
        "sec4_fecho": "Ou seja: o valor leva em conta <strong>quantidade de equipamentos</strong>, <strong>complexidade do sistema</strong> e se o contrato inclui <strong>apenas plano</strong> ou também <strong>execução recorrente</strong>.",
    },
}

PHONE = "(48) 98810-5199"
TEL = "+5548988105199"
WA = "https://wa.me/5548988105199?text=Olá!%20Quero%20orçamento%20de%20ar-condicionado%20em%20Florianópolis."


def prep_phrase(prep, nome):
    return f"{prep} {nome}"


PREP_SENT = {"no": "No", "na": "Na", "em": "Em", "nos": "Nos", "nas": "Nas"}


def prep_sentence_start(prep):
    return PREP_SENT.get(prep, prep.capitalize())


def intro_paragraphs(sk, nome, prep, variante, is_city: bool = False):
    pp = prep_phrase(prep, nome)
    curto = SERV_META[sk]["curto"]
    if is_city:
        intros = [
            (
                f"Se você precisa de {curto} {pp}, na Grande Florianópolis (SC), o ideal é resolver com técnica e sem improviso. "
                f"Quem mora ou trabalha {pp} sabe que conforto térmico faz diferença na rotina, principalmente em dias mais quentes.",
                f"Em {nome}, é comum encontrar apartamentos, casas, condomínios e pontos comerciais com necessidades diferentes de climatização. "
                f"Bem planejar o atendimento reduz retrabalho e melhora o resultado final, principalmente quando há restrições de fachada, área técnica ou agenda do condomínio.",
            ),
            (
                f"Na região metropolitana, buscar {curto} {pp} com agilidade ajuda a voltar ao normal sem perder produtividade em casa ou no trabalho. "
                f"Serviços bem executados também reduzem improviso e melhoram a sensação de conforto no ambiente.",
                f"Nossa atuação {pp} prioriza diagnóstico claro, execução organizada e comunicação direta. "
                f"Assim você entende o que será feito, o que está incluso no escopo e quais cuidados são necessários no seu tipo de imóvel.",
            ),
            (
                f"O clima de Santa Catarina e a rotina urbana fazem o ar-condicionado ser peça-chave em muitos imóveis {pp}. "
                f"Por isso, um atendimento técnico bem conduzido evita soluções paliativas e melhora a estabilidade do equipamento ao longo do tempo.",
                f"Se você precisa de {curto} {pp}, o caminho mais seguro é combinar visita, entender o cenário (modelo, instalação e objetivo do serviço) e só então executar com testes ao final.",
            ),
        ]
    else:
        intros = [
            (
                f"Se você precisa de {curto} {pp}, em Florianópolis, o ideal é resolver com técnica e sem improviso. "
                f"Quem mora ou trabalha {pp} sabe que conforto térmico faz diferença na rotina, principalmente em dias mais quentes.",
                f"Em {nome}, é comum encontrar apartamentos, casas, condomínios e pontos comerciais com necessidades diferentes de climatização. "
                f"Bem planejar o atendimento reduz retrabalho e melhora o resultado final, principalmente quando há restrições de fachada, área técnica ou agenda do condomínio.",
            ),
            (
                f"Em Florianópolis, buscar {curto} {pp} com agilidade ajuda a voltar ao normal sem perder produtividade em casa ou no trabalho. "
                f"Serviços bem executados também reduzem improviso e melhoram a sensação de conforto no ambiente.",
                f"Nossa atuação {pp} prioriza diagnóstico claro, execução organizada e comunicação direta. "
                f"Assim você entende o que será feito, o que está incluso no escopo e quais cuidados são necessários no seu tipo de imóvel.",
            ),
            (
                f"O clima da Ilha e a rotina urbana fazem o ar-condicionado ser peça-chave em muitos imóveis {pp}. "
                f"Por isso, um atendimento técnico bem conduzido evita soluções paliativas e melhora a estabilidade do equipamento ao longo do tempo.",
                f"Se você precisa de {curto} {pp}, o caminho mais seguro é combinar visita, entender o cenário (modelo, instalação e objetivo do serviço) e só então executar com testes ao final.",
            ),
        ]
    return intros[variante % len(intros)]


def _servico_fname_token(suffix: str) -> str:
    return "florianopolis" if suffix == "florianopolis" else "sc"


def servico_html_fname(osk: str, bslug: str, prep: str, suffix: str) -> str:
    """Nome do ficheiro em servico/ para o par (tipo de serviço, região)."""
    if bslug == "florianopolis":
        return f"{osk}-em-florianopolis.html"
    tok = _servico_fname_token(suffix)
    return f"{osk}-{prep}-{bslug}-{tok}.html"


def servico_public_path(fname: str) -> str:
    """Caminho público /servico/<slug>/ a partir do nome legado foo.html."""
    return f"/servico/{fname.replace('.html', '')}/"


def build_outros_servicos_cidade_html(sk: str, bslug: str, nome: str, suffix: str) -> str:
    """Sete cartões com os demais tipos de serviço na mesma cidade/região (exclui o serviço da página atual)."""
    p_here = BAIRROS[bslug]["prep"]
    cards: list[str] = []
    for osk in SERVICE_KEYS:
        if osk == sk:
            continue
        fn = servico_html_fname(osk, bslug, p_here, suffix)
        tit = SERV_META[osk]["titulo"]
        lbl = f"{tit} em {nome}"
        cards.append(
            f'<article class="card servico-outro-card"><h3><a href="{servico_public_path(fn)}">{escape(lbl)}</a></h3></article>'
        )
    body = "".join(cards)
    return (
        f'<section class="section servico-outros-servicos"><div class="container">'
        f'<h2 class="servico-outros-titulo">Outros serviços em {escape(nome)}</h2>'
        f'<p class="servico-outros-lead">Na mesma região também realizamos os serviços abaixo.</p>'
        f'<div class="grid-3 servico-outros-grid">{body}</div></div></section>'
    )


def faq_items(sk, prep, nome, is_city: bool = False):
    cur = SERV_META[sk]["curto"]
    pp = prep_phrase(prep, nome)
    lugar = nome if is_city else "Florianópolis"
    items = [
        (f"Vocês fazem {cur} {pp} em {lugar}?", f"Sim. Atendemos {prep} {nome} com serviço técnico e agenda conforme disponibilidade."),
        (f"O atendimento {pp} é rápido?", "Priorizamos triagem ágil e deslocamento organizado para reduzir o tempo de espera."),
        (f"Atendem apartamentos e comércios {pp}?", "Sim. Atendemos perfis residenciais e comerciais, respeitando regras de condomínio quando necessário."),
        ("Como solicitar orçamento?", "Você pode chamar no WhatsApp, ligar ou preencher o formulário de contato com dados do aparelho e do endereço."),
        ("Quais formas de pagamento são aceitas?", "As formas de pagamento são combinadas no orçamento, conforme tipo de serviço e empresa emissora."),
        ("Vocês atendem à noite ou feriado?", "Quando há disponibilidade na agenda, combinamos horário especial no contato."),
    ]
    for q, a in SERV_META[sk]["faq_extra"]:
        items.append((q.format(prep=prep, nome=nome), a.format(prep=prep, nome=nome)))
    return items


def faq_block(sk, prep, nome, is_city: bool = False):
    rows = []
    for q, a in faq_items(sk, prep, nome, is_city=is_city):
        rows.append(
            f'<div class="faq-item"><button class="faq-question" type="button">{escape(q)}</button>'
            f'<div class="faq-answer"><p>{escape(a)}</p></div></div>'
        )
    return "\n".join(rows)


TITLE_MAX_LEN = 70
# Snippet Google ~155–160 caracteres; evitamos corte feio e incentivamos clique.
META_DESC_MAX_LEN = 155


def build_meta_title(meta, pp, is_city: bool = False, nome_cidade: str = ""):
    """Título único, com palavra-chave + local; máximo TITLE_MAX_LEN (SERP não corta o texto exibido)."""
    tit = meta["titulo"]
    curto = (meta.get("curto") or tit).strip()
    short = (curto[0].upper() + curto[1:]) if curto else tit

    if is_city and nome_cidade:
        variants = (
            f"{tit} em {nome_cidade} | SC",
            f"{short} em {nome_cidade} | SC",
            f"{tit} em {nome_cidade}",
            f"{short} em {nome_cidade}",
        )
    else:
        variants = (
            f"{tit} {pp} | SC",
            f"{short} {pp} | SC",
            f"{tit} {pp}",
            f"{short} {pp}",
        )
    for t in variants:
        if len(t) <= TITLE_MAX_LEN:
            return t
    # Último recurso: corta no último espaço antes do limite (sem reticências).
    t = variants[0]
    if len(t) <= TITLE_MAX_LEN:
        return t
    cut = t[:TITLE_MAX_LEN]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut[:TITLE_MAX_LEN]


def _clip_meta_description(s: str, max_len: int = META_DESC_MAX_LEN) -> str:
    """Encerra o snippet em limite seguro, em limite de palavra, sem reticências artificiais no HTML."""
    s = (s or "").strip()
    if len(s) <= max_len:
        return s
    cut = s[: max_len + 1]
    if " " in cut:
        cut = cut[:max_len].rsplit(" ", 1)[0]
    else:
        cut = s[:max_len]
    return cut.rstrip(" ,;:")


def build_meta_desc(sk: str, meta, nome: str, is_city: bool = False):
    """Snippet persuasivo para o SERP; comprimento ≤ META_DESC_MAX_LEN (evita corte feio no Google)."""
    frags = SEO_META_FRAGMENTS.get(sk)
    if not frags:
        frags = (
            "Split e inverter com técnica e orçamento claro na Grande Florianópolis. Chame no WhatsApp.",
            "Atendimento no bairro com orçamento e agendamento. Fale no WhatsApp.",
        )
    city_frag, bairro_frag = frags
    curto = meta["curto"]
    if curto:
        curto = curto[0].upper() + curto[1:]
    if is_city:
        s = f"{curto} em {nome}, SC. {city_frag}"
    else:
        s = f"{curto} no bairro {nome}, Florianópolis. {bairro_frag}"
    return _clip_meta_description(s)


def paragraph_vizinhos(bslug, nome, is_city: bool = False):
    if is_city:
        ids = CIDADE_VIZINHAS.get(bslug, [])[:2]
        names = [BAIRROS[i]["nome"] for i in ids if i in BAIRROS]
        if len(names) < 2:
            return ""
        n1, n2 = names[0], names[1]
        return (
            f'<p class="servico-vizinhanca">Além de <strong>{escape(nome)}</strong>, a demanda por climatização costuma aparecer com força em '
            f"<strong>{escape(n1)}</strong> e <strong>{escape(n2)}</strong> na <strong>Grande Florianópolis</strong> (<strong>SC</strong>), "
            f"o que ajuda no planejamento de deslocamento e na organização da agenda técnica.</p>"
        )
    ids = PERTO.get(bslug, [])[:2]
    names = [BAIRROS[i]["nome"] for i in ids if i in BAIRROS]
    if len(names) < 2:
        return ""
    n1, n2 = names[0], names[1]
    return (
        f'<p class="servico-vizinhanca">O <strong>{escape(nome)}</strong> se articula com <strong>{escape(n1)}</strong> e <strong>{escape(n2)}</strong> '
        f"no tecido urbano de <strong>Florianópolis</strong> (<strong>Santa Catarina</strong>), o que ajuda na logística de atendimento na "
        f"<strong>Ilha de Santa Catarina</strong> e em buscas por técnico de ar-condicionado em bairros próximos.</p>"
    )


def build_schema_service_jsonld(sk, prep, bslug, nome, fname, title, desc, is_city: bool = False, suffix: str = "florianopolis"):
    """Um único nó JSON-LD: Service + FAQPage (herda WebPage → aceita breadcrumb) com FAQ em mainEntity."""
    page_url = f"{BASE_URL}{servico_public_path(fname)}"
    meta = SERV_META[sk]
    main_q = [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq_items(sk, prep, nome, is_city=is_city)
    ]

    hvac_provider = {
        "@type": "HVACBusiness",
        "@id": BUSINESS_ID,
        "name": BUSINESS_NAME,
        "url": f"{BASE_URL}/",
        "foundingDate": FOUNDING_DATE,
        "telephone": TEL,
        "logo": {"@type": "ImageObject", "url": BUSINESS_LOGO_URL},
        "image": BUSINESS_IMAGE,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": f"{BUSINESS_STREET} — {BUSINESS_NEIGHBORHOOD}",
            "addressLocality": "Florianópolis",
            "addressRegion": "SC",
            "postalCode": BUSINESS_POSTAL,
            "addressCountry": "BR",
        },
        "areaServed": [
            {"@type": "City", "name": "Florianópolis"},
            {"@type": "City", "name": "São José"},
            {"@type": "City", "name": "Palhoça"},
            {"@type": "City", "name": "Biguaçu"},
        ],
    }

    service_area = {"@type": "City", "name": nome if is_city else "Florianópolis"}

    return {
        "@context": "https://schema.org",
        "@type": ["Service", "FAQPage"],
        "@id": page_url + "#servico",
        "name": title,
        "description": desc,
        "url": page_url,
        "serviceType": meta["titulo"],
        "provider": hvac_provider,
        "areaServed": service_area,
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Serviços", "item": f"{BASE_URL}/servicos/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
            ],
        },
        "mainEntity": main_q,
    }


def patch_head_seo(html, sk, prep, bslug, nome, fname, is_city: bool = False, suffix: str = "florianopolis"):
    meta = SERV_META[sk]
    pp = prep_phrase(prep, nome)
    page_url = f"{BASE_URL}{servico_public_path(fname)}"
    title = build_meta_title(meta, pp, is_city=is_city, nome_cidade=nome if is_city else "")
    desc = build_meta_desc(sk, meta, nome, is_city=is_city)
    payload = build_schema_service_jsonld(sk, prep, bslug, nome, fname, title, desc, is_city=is_city, suffix=suffix)
    jstr = json.dumps(payload, ensure_ascii=False)
    new_script = f"<script type=\"application/ld+json\">\n{jstr}\n</script>"
    if 'rel="canonical"' not in html:
        html, ccan = re.subn(
            r'(<meta name="viewport"[^>]*>)',
            rf'\1\n  <link rel="canonical" href="{escape(page_url)}">',
            html,
            count=1,
        )
        if ccan != 1:
            print("Aviso: canonical não inserido em", fname)
    html, c = re.subn(r"<title>.*?</title>", f"<title>{escape(title)}</title>", html, count=1, flags=re.DOTALL)
    if c != 1:
        print("Aviso: <title> não atualizado em", fname)
    html, c = re.subn(
        r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
        f'<meta name="description" content="{escape(desc, quote=True)}">',
        html,
        count=1,
    )
    if c != 1:
        print("Aviso: meta description não atualizada em", fname)
    html, c = re.subn(
        r'<script type="application/ld\+json">.*?</script>',
        new_script,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if c != 1:
        html, ins = re.subn(r"(</head>)", f"{new_script}\n\\1", html, count=1)
        if ins != 1:
            print("Aviso: JSON-LD não inserido em", fname)
    html = insert_social_meta_after_description(
        html,
        og_type="website",
        title=title,
        description=desc,
        page_url=page_url,
    )
    return html


def build_main(sk, prep, bslug, nome, suffix: str = "florianopolis"):
    is_city = bslug in CIDADES or bslug == "florianopolis"
    meta = SERV_META[sk]
    pp = prep_phrase(prep, nome)
    extras = SEC_EXTRAS.get(sk, {})
    variante = int(hashlib.md5(f"{sk}-{bslug}".encode()).hexdigest(), 16) % 3
    p1, p2 = intro_paragraphs(sk, nome, prep, variante, is_city=is_city)

    lista_html = "".join(f"<li>{x.format(prep=prep, nome=nome)}</li>" for x in meta["lista"])
    porque_html = "".join(f"<li>{x.format(prep=prep, nome=nome)}</li>" for x in meta["porque"])
    preco_l_html = "".join(f"<li>{x.format(prep=prep, nome=nome)}</li>" for x in meta["preco_lista"])
    ofertas_html = "".join(f"<li>{x.format(prep=prep, nome=nome)}</li>" for x in meta["contratar_ofertas"])
    vant_html = "".join(f"<li>{x.format(prep=prep, nome=nome)}</li>" for x in meta["vantagens"])

    outros_servicos_html = build_outros_servicos_cidade_html(sk, bslug, nome, suffix)

    ctx_html = meta.get("contexto_seo") or ""
    if ctx_html:
        ctx_html = ctx_html.format(prep=prep, nome=nome, sent=prep_sentence_start(prep))
    viz_html = paragraph_vizinhos(bslug, nome, is_city=is_city)

    sec3_h2 = (extras.get("sec3_h2") or "3. Por que fazer {curto} {pp}?").format(curto=meta["curto"], pp=pp)
    sec3_intro = extras.get("sec3_intro") or (
        "Quando o ar-condicionado apresenta sintomas ou passa muito tempo sem revisão técnica, adiar o serviço pode aumentar desconforto e, em alguns casos, ampliar o problema."
    )
    sec4_fecho = extras.get("sec4_fecho") or (
        "Ou seja: o orçamento mais fiel depende de três eixos — <strong>onde</strong> está o equipamento, <strong>qual</strong> é o modelo/cenário e <strong>qual</strong> é o objetivo do serviço (preventivo, corretivo ou adequação)."
    )

    p_sec1_fecho = (
        f"Na Grande Florianópolis (SC), isso é relevante porque cada cidade tem perfis diferentes de imóveis e uso — e, {prep} {nome}, a demanda por climatização costuma ser constante ao longo do ano."
        if is_city
        else f"Em Florianópolis, isso é relevante porque cada bairro tem perfis diferentes de imóveis e uso — e, {prep} {nome}, a demanda por climatização costuma ser constante ao longo do ano."
    )
    p_sec3_fecho = (
        f"Em {nome} e na rotina da região metropolitana, agir com técnica e rapidez costuma fazer diferença na experiência de uso e na previsibilidade do ambiente."
        if is_city
        else f"No bairro {nome} e na rotina de Florianópolis, agir com técnica e rapidez costuma fazer diferença na experiência de uso e na previsibilidade do ambiente."
    )
    if bslug == "florianopolis":
        curto = meta["curto"]
        sj = servico_html_fname(sk, "sao-jose", "em", "sc")
        bg = servico_html_fname(sk, "biguacu", "em", "sc")
        ph = servico_html_fname(sk, "palhoca", "em", "sc")
        p_sec5_links = (
            "Confira a secção <strong>Outros serviços</strong> nesta página para navegar entre tipos de serviço na capital e na Grande Florianópolis."
        )
        sec5_extra = (
            f'<p class="servico-tambem-atende">Também atendemos <a href="{servico_public_path(sj)}">{curto} em São José</a>, '
            f'<a href="{servico_public_path(bg)}">Biguaçu</a> e <a href="{servico_public_path(ph)}">Palhoça</a> '
            f"(na ilha e na Grande Florianópolis, inclusive bairros como Trindade e Campeche).</p>"
        )
    else:
        sec5_extra = ""
        p_sec5_links = (
            "Também atendemos Florianópolis e cidades vizinhas — a secção <strong>Outros serviços</strong> nesta página reúne os demais tipos de serviço na mesma cidade."
            if is_city
            else "Também atendemos regiões próximas em Florianópolis — a secção <strong>Outros serviços</strong> nesta página reúne os demais tipos de serviço na mesma região."
        )
    p_sec7_cobertura = (
        "Nosso atendimento busca cobrir a cidade e entornos próximos na Grande Florianópolis, com foco em deslocamento planejado e comunicação clara sobre prazos."
        if is_city
        else "Nosso atendimento busca cobrir o bairro e entornos próximos em Florianópolis, com foco em deslocamento planejado e comunicação clara sobre prazos."
    )

    return f"""<main>
<section class="section servico-hero-top"><div class="container">
  <h1>Precisa de {meta["titulo"]} {pp}?</h1>
  <p class="servico-phones"><a href="tel:{TEL}">{PHONE}</a> &nbsp;|&nbsp; <a href="tel:{TEL}">{PHONE}</a></p>
</div></section>
<section class="section servico-intro"><div class="container">
  <p>{p1}</p>
  <p>{p2} O serviço de {meta["curto"]} {pp} é pensado para quem busca resultado técnico com orientação clara, execução organizada e menos improviso no dia a dia.</p>
  {ctx_html}
</div></section>
<section class="section"><div class="container">
  <div class="servico-num-sec"><h2>1. O que é o serviço de {meta["curto"]} {pp}?</h2>
  <p>{meta["oque"]}</p>
  <p>Esse atendimento costuma ser necessário em situações como:</p>
  <ul>{lista_html}</ul>
  <p>{p_sec1_fecho}</p></div>
  <div class="servico-num-sec"><h2>2. Como funciona o serviço?</h2>
  <p>O atendimento é organizado para reduzir dúvidas e evitar retrabalho.</p>
  <ol class="servico-passos">{"".join(f"<li><strong>{t}:</strong> {d.format(prep=prep, nome=nome)}</li>" for t, d in meta["como_passos"])}</ol></div>
  <div class="servico-num-sec"><h2>{sec3_h2}</h2>
  <p>{sec3_intro}</p>
  <ul>{porque_html}</ul>
  <p>{p_sec3_fecho}</p></div>
  <div class="servico-num-sec"><h2>4. Quanto custa {meta["curto"]} {pp}?</h2>
  <p>{meta["preco_txt"]}</p>
  <p>O valor pode variar mais em cenários como:</p>
  <ul>{preco_l_html}</ul>
  <p>{sec4_fecho}</p></div>
  <div class="servico-num-sec"><h2>5. Onde contratar {meta["curto"]} {pp}?</h2>
  <p>Ao procurar atendimento técnico {pp}, o ideal é escolher uma equipe que explique o processo, combine escopo e execute com segurança.</p>
  <p>Oferecemos:</p>
  <ul>{ofertas_html}</ul>
  <p>{p_sec5_links}</p>{sec5_extra}</div>
  <div class="servico-num-sec"><h2>6. Vantagens de contratar um serviço profissional</h2>
  <p>Contratar um serviço técnico bem conduzido reduz improviso e melhora o resultado final.</p>
  <ul>{vant_html}</ul>
  <p>Nos imóveis e comércios {prep} {nome}, isso é importante porque o ambiente exige cuidado com acabamento, dreno, elétrica e acesso — pontos que influenciam diretamente na qualidade do serviço.</p></div>
  <div class="servico-num-sec"><h2>7. Onde atendemos com {meta["curto"]} {pp}?</h2>
  <p><strong>Principais perfis de atendimento:</strong> ruas residenciais, avenidas de circulação local, comércio de bairro, condomínios e conjuntos comerciais.</p>
  <p><strong>Áreas atendidas:</strong> {meta["onde_txt"].format(prep=prep, nome=nome)}</p>
  {viz_html}
  <p>{p_sec7_cobertura}</p></div>
  <div class="servico-num-sec"><h2>8. Perguntas frequentes</h2>
  <div class="faq">{faq_block(sk, prep, nome, is_city=is_city)}</div></div>
</div></section>
<section class="section"><div class="container cta-box"><div><h2>Precisa de {meta["curto"]} {pp}?</h2><p>Fale agora com a equipe e receba orientação técnica.</p></div><div><a class="btn btn-whats" href="{WA}" target="_blank" rel="noopener">WhatsApp</a> <a class="btn btn-primary" href="/contato/">Solicitar orçamento</a> <a class="btn btn-outline" href="tel:{TEL}">Ligar</a></div></div></section>
{outros_servicos_html}
</main>"""


def parse_filename(fname: str):
    base = fname.replace(".html", "")
    if base.endswith("-florianopolis"):
        suffix = "florianopolis"
        inner = base[: -len("-florianopolis")]
    elif base.endswith("-sc"):
        suffix = "sc"
        inner = base[: -len("-sc")]
    else:
        return None
    for sk in sorted(SERVICE_KEYS, key=len, reverse=True):
        if inner.startswith(sk + "-"):
            rest = inner[len(sk) + 1 :]
            m = re.match(r"^(no|na|em|nos|nas)-(.+)$", rest)
            if not m:
                # Capital agregada: *-em-florianopolis.html (sem slug de bairro)
                if suffix == "florianopolis" and rest == "em":
                    return sk, "em", "florianopolis", suffix
                continue
            prep, loc = m.group(1), m.group(2)
            if suffix == "florianopolis":
                return sk, prep, loc, suffix
            if loc in CIDADES:
                return sk, prep, loc, suffix
    return None


def rebuild(path: Path):
    if path.name != "index.html" or path.parent.parent != root / "servico":
        return False
    fname = path.parent.name + ".html"
    parsed = parse_filename(fname)
    if not parsed:
        return False
    sk, _prep_ignore, bslug, suffix = parsed
    if bslug not in BAIRROS:
        print("Região não mapeada:", bslug, fname)
        return False
    nome = BAIRROS[bslug]["nome"]
    prep = BAIRROS[bslug]["prep"]
    is_city = bslug in CIDADES or bslug == "florianopolis"

    html = path.read_text(encoding="utf-8")
    m = re.search(r"<main>.*?</main>", html, re.DOTALL)
    if not m:
        return False
    new_main = build_main(sk, prep, bslug, nome, suffix=suffix)
    html = html[: m.start()] + new_main + html[m.end() :]
    html = patch_head_seo(html, sk, prep, bslug, nome, fname, is_city=is_city, suffix=suffix)
    html = patch_footer_servico(html)
    path.write_text(html, encoding="utf-8")
    apply_relative_paths_to_file(path, root)
    return True


def ensure_city_servico_stubs() -> None:
    """Cria arquivos servico/*-em-{cidade}-sc.html a partir de um template existente (conteúdo é sobrescrito pelo rebuild)."""
    src = root / "servico" / "instalacao-de-ar-condicionado-em-florianopolis" / "index.html"
    if not src.is_file():
        print("Aviso: template para stubs de cidade não encontrado:", src)
        return
    tpl = src.read_text(encoding="utf-8")
    for cid in CIDADES:
        prep = CIDADES[cid]["prep"]
        for sk in SERVICE_KEYS:
            fn = f"{sk}-{prep}-{cid}-sc.html"
            stem = fn.replace(".html", "")
            dst = root / "servico" / stem / "index.html"
            if dst.is_file():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(tpl, encoding="utf-8")
            apply_relative_paths_to_file(dst, root)
            print("Criado stub:", dst.relative_to(root))


def main():
    ensure_city_servico_stubs()
    n = 0
    for p in sorted((root / "servico").glob("*/index.html")):
        if rebuild(p):
            n += 1
    print("Páginas atualizadas:", n)


if __name__ == "__main__":
    main()
