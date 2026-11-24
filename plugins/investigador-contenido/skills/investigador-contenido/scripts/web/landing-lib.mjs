// Funciones puras para leer una landing de la competencia desde su HTML: siguiente paso del embudo,
// redirecciones configuradas, huella tecnológica y qué páginas de gracias o de pago conviene abrir (sin enviar nada).

export const slugDe = (u) => u.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').slice(0, 90);

const SIGUIENTE = /(chat\.whatsapp\.com\/[A-Za-z0-9]+|wa\.me\/\d+[^"'\s<]*|api\.whatsapp\.com\/send[^"'\s<]*|t\.me\/[A-Za-z0-9_+]+|calendly\.com\/[^"'\s<]+|zoom\.us\/[^"'\s<]+|pay\.hotmart\.com\/[^"'\s<]+|hotmart\.com\/[^"'\s<]+|kiwify\.app\/[^"'\s<]+|pay\.kiwify[^"'\s<]+|checkout\.[^"'\s<]+|buy\.stripe\.com\/[^"'\s<]+|skool\.com\/[^"'\s<]+|typeform\.com\/[^"'\s<]+|youtube\.com\/(?:live|watch)[^"'\s<]+|https?:\/\/[^"'\s<]*(?:gracias|obrigado|thank-?you|thanks|confirmacion|confirmado|grupo|bienvenid|registro-exitoso|parabens)[^"'\s<]*)/gi;
const REDIRECCION = /(redirect(?:_?url|_to|Url|To)?|thank_?you_?(?:url|page)|success_?url|on_?success|nextStep|next_step_url)["']?\s*[:=]\s*["']([^"']{4,300})["']/gi;
const GRACIAS = /gracias|obrigado|thank|confirm|bienvenid|registro-exitoso|parabens/i;
const PAGO = /pay\.hotmart|hotmart\.com\/[a-z]{2}\/checkout|kiwify|buy\.stripe|checkout\./i;

export const TECNOLOGIAS = {
  'Meta Pixel': /connect\.facebook\.net|fbq\(/, 'Google Tag Manager': /googletagmanager\.com/, 'GoHighLevel/LeadConnector': /leadconnector|msgsndr|gohighlevel|highlevel/i,
  'ClickFunnels': /clickfunnels|cfimg|myclickfunnels/i, 'Systeme.io': /systeme\.io/i, 'WordPress': /wp-content|wp-includes/i, 'Elementor': /elementor/i,
  'Kajabi': /kajabi/i, 'Hotmart': /hotmart/i, 'Kiwify': /kiwify/i, 'Greatpages': /greatpages/i, 'Webflow': /webflow/i, 'Framer': /framer/i,
  'Wix': /wix\.com|wixstatic/i, 'Shopify': /shopify/i, 'Skool': /skool\.com/i, 'ActiveCampaign': /activecampaign|actcdn/i, 'RD Station': /rdstation/i,
  'HubSpot': /hubspot|hs-scripts/i, 'Mailchimp': /mailchimp|list-manage/i, 'ConvertKit/Kit': /convertkit|kit\.com/i, 'ManyChat': /manychat/i,
  'VTurb (player VSL)': /vturb|converteai/i, 'Panda Video': /pandavideo/i, 'Vimeo': /vimeo/i, 'YouTube': /youtube\.com\/embed|youtu\.be/i, 'Wistia': /wistia/i,
  'Calendly': /calendly/i, 'Typeform': /typeform/i, 'Hotjar': /hotjar/i, 'Microsoft Clarity': /clarity\.ms/i, 'TikTok Pixel': /analytics\.tiktok/i,
  'Stripe': /stripe/i, 'Thrivecart': /thrivecart/i, 'Leadpages': /leadpages/i, 'Unbounce': /unbounce/i, 'Carrd': /carrd/i,
};

/** Enlaces de siguiente paso (WhatsApp, Telegram, gracias, pago, calendario...) tal como aparecen en el HTML. */
export function siguientePaso(html) {
  return [...new Set([...html.matchAll(SIGUIENTE)].map((m) => m[1].replace(/&amp;/g, '&').slice(0, 300)))].slice(0, 60);
}

/** Redirecciones configuradas en el código de la página (a dónde manda el formulario al enviarse). */
export function redirecciones(html) {
  return [...new Set([...html.matchAll(REDIRECCION)].map((m) => `${m[1]} = ${m[2]}`))].slice(0, 30);
}

export function tecnologia(huella) {
  return Object.entries(TECNOLOGIAS).filter(([, re]) => re.test(huella)).map(([nombre]) => nombre);
}

const absoluta = (u) => (/^https?:\/\//.test(u) ? u : 'https://' + u);

/** Hasta 2 páginas de gracias del mismo dominio y 1 de pago, para abrirlas UNA vez (no se compra ni se envía nada). */
export function paginasParaSeguir(siguientes, dominio) {
  const gracias = siguientes.filter((u) => /^https?:\/\//.test(u) && new URL(u).hostname === dominio && GRACIAS.test(u)).slice(0, 2);
  const pago = siguientes.map(absoluta).find((u) => PAGO.test(u));
  return pago ? [...gracias, pago] : gracias;
}
