# Skills de Nomad Business Lab

Skills de Claude para la comunidad de Nomad Business Lab. Cada una se instala por separado.

## Cómo se instala

**En Claude Code**, copia la línea de la skill que quieras y pégala en tu terminal. La primera vez también da de alta este catálogo; después solo instala.

O, dentro de un chat de Claude Code, pega la frase que trae cada skill y Claude la instala por ti.

**Para recibir las mejoras solas:** en Claude Code escribe `/plugin`, entra a *Marketplaces*, elige `nbl-skills` y prende la actualización automática. Si no, de vez en cuando corre `claude plugin marketplace update nbl-skills`.

**En claude.ai (web o app):** baja el ZIP de la skill y súbelo en *Configuración → Capacidades → Skills*. Cuando salga una versión nueva, bájalo otra vez.

**¿Las quieres todas?**

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install elevenlabs-expert@nbl-skills; claude plugin install higgsfield-expert@nbl-skills; claude plugin install ugc-ad-pipeline@nbl-skills; claude plugin install gsap-skills@nbl-skills; claude plugin install impeccable@nbl-skills; claude plugin install ui-ux-pro-max@nbl-skills; claude plugin install design-taste-frontend@nbl-skills; claude plugin install web-design-guidelines@nbl-skills; claude plugin install building-components@nbl-skills; claude plugin install shadcn-ui@nbl-skills; claude plugin install seo-audit@nbl-skills; claude plugin install deep-research@nbl-skills; claude plugin install n8n-mcp-skills@nbl-skills
```

## Automatización con n8n

### `n8n-mcp-skills`

15 skills para armar workflows de n8n con n8n-mcp: expresiones, nodos, código JS/Python, validación, errores, subworkflows y agentes.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install n8n-mcp-skills@nbl-skills
```

En un chat de Claude Code: «Instala la skill `n8n-mcp-skills` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Romuald Członkowski (czlonkowski)](https://github.com/czlonkowski/n8n-skills) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

## Diseño web y frontend

### `gsap-skills`

Las 8 skills oficiales de GSAP: tweens, timelines, ScrollTrigger, plugins, React/Vue/Svelte, utilidades y rendimiento de animaciones.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install gsap-skills@nbl-skills
```

En un chat de Claude Code: «Instala la skill `gsap-skills` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [GreenSock (oficiales)](https://github.com/greensock/gsap-skills) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

### `impeccable`

Diseña, critica, audita y pule interfaces (web, dashboards, móvil): jerarquía, tipografía, color, movimiento y accesibilidad.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install impeccable@nbl-skills
```

En un chat de Claude Code: «Instala la skill `impeccable` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Paul Bakaus](https://github.com/pbakaus/impeccable) · licencia Apache-2.0 · se instala desde el repo de su autor, así te llegan sus mejoras

### `ui-ux-pro-max`

Datos buscables de UI/UX: estilos, paletas, tipografías, patrones y reglas por stack para diseñar o revisar interfaces.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install ui-ux-pro-max@nbl-skills
```

En un chat de Claude Code: «Instala la skill `ui-ux-pro-max` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Next Level Builder](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

### `design-taste-frontend`

Dirección de arte para landings y sitios públicos que no se vean hechos por IA: direcciones de diseño, reglas estrictas y revisión en navegador.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install design-taste-frontend@nbl-skills
```

En un chat de Claude Code: «Instala la skill `design-taste-frontend` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Leonxlnx (tasteskill)](https://github.com/Leonxlnx/taste-skill) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

### `web-design-guidelines`

Revisa el código de una interfaz contra las Web Interface Guidelines de Vercel: accesibilidad, UX y buenas prácticas.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install web-design-guidelines@nbl-skills
```

En un chat de Claude Code: «Instala la skill `web-design-guidelines` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Vercel](https://github.com/vercel-labs/agent-skills) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

### `building-components`

Guía para construir componentes de interfaz accesibles y componibles: APIs, design tokens, publicación y documentación.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install building-components@nbl-skills
```

En un chat de Claude Code: «Instala la skill `building-components` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Vercel (components.build)](https://github.com/vercel/components.build) · licencia Apache-2.0 · se instala desde el repo de su autor, así te llegan sus mejoras

### `shadcn-ui`

Referencia de shadcn/ui para React y Tailwind: componentes accesibles que se copian al proyecto.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install shadcn-ui@nbl-skills
```

En un chat de Claude Code: «Instala la skill `shadcn-ui` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [bobmatnyc (Claude MPM)](https://github.com/bobmatnyc/claude-mpm-skills) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

## Investigación

### `deep-research`

Investiga en la web en varias pasadas y desde varios ángulos antes de escribir, en vez de quedarse con una sola búsqueda.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install deep-research@nbl-skills
```

En un chat de Claude Code: «Instala la skill `deep-research` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [ByteDance (DeerFlow)](https://github.com/bytedance/deer-flow) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

## Marketing

### `seo-audit`

Audita el SEO técnico y on-page de un sitio: indexación, meta tags, Core Web Vitals y caídas de tráfico.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install seo-audit@nbl-skills
```

En un chat de Claude Code: «Instala la skill `seo-audit` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Creada por [Corey Haines](https://github.com/coreyhaines31/marketingskills) · licencia MIT · se instala desde el repo de su autor, así te llegan sus mejoras

## Video y anuncios con IA

### `elevenlabs-expert`

Voz con IA en ElevenLabs que suena humana: qué modelo, voz y ajustes usar en español mexicano, cómo clonar tu voz y qué plan necesitas para anuncios.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install elevenlabs-expert@nbl-skills
```

En un chat de Claude Code: «Instala la skill `elevenlabs-expert` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Versión 1.1.0 · [Bajar ZIP para claude.ai](https://github.com/DevAI-MX/nbl-skills/raw/main/descargas/elevenlabs-expert.zip)

### `higgsfield-expert`

Imagen y video con IA en Higgsfield: qué modelo elegir, cómo escribir el prompt, cómo hacer avatares que hablan con tu voz y cómo no quemar créditos.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install higgsfield-expert@nbl-skills
```

En un chat de Claude Code: «Instala la skill `higgsfield-expert` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Versión 2.0.0 · [Bajar ZIP para claude.ai](https://github.com/DevAI-MX/nbl-skills/raw/main/descargas/higgsfield-expert.zip)

### `ugc-ad-pipeline`

Un anuncio UGC vertical de principio a fin: brief, guion, voz, persona, lip-sync, edición y entrega, usando ElevenLabs y Higgsfield.

```bash
claude plugin marketplace add DevAI-MX/nbl-skills; claude plugin install ugc-ad-pipeline@nbl-skills
```

En un chat de Claude Code: «Instala la skill `ugc-ad-pipeline` del marketplace `DevAI-MX/nbl-skills` de GitHub (claude plugin marketplace add y claude plugin install).»

Versión 1.1.0 · [Bajar ZIP para claude.ai](https://github.com/DevAI-MX/nbl-skills/raw/main/descargas/ugc-ad-pipeline.zip)

---

Este repo se genera solo desde el baúl privado de Devia; los cambios aquí se pierden en la siguiente publicación.
