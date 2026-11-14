// --- min portfölj (privat per inloggad person; sparas i data/users/<id>/portfolj) ---
const PF = {db: null, uid: null, data: null, laddad: false, fel: null, unsub: null, forhand: null, sparar: false, kanSkriva: true};
const PF_TOM = () => ({transaktioner: [], kurser: {}, anteckningar: {}, importer: [], dolda: {}});
const tal = v => { if (v == null) return null; const t = String(v).replace(/[\s ]/g, "").replace(/−/g, "-").replace(/^-$/, ""); if (!t) return null; const n = Number(t.includes(",") ? t.replace(/\./g, "").replace(",", ".") : t); return isFinite(n) ? n : null; };
function datumNorm(v){
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  const t = String(v||"").trim(); let m;
  if ((m = t.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/))) return `${m[1]}-${m[2].padStart(2,"0")}-${m[3].padStart(2,"0")}`;
  if ((m = t.match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})/))) return `${m[3]}-${m[2].padStart(2,"0")}-${m[1].padStart(2,"0")}`;
  if (/^\d{5}$/.test(t)) return new Date(Date.UTC(1899, 11, 30) + Number(t) * 864e5).toISOString().slice(0, 10);
  return "";
}
const PF_FALT = [
  ["datum", "Datum", /^(affärsdag|affärsdatum|transaktionsdag|transaktionsdatum|datum|bokföringsdag|bokföringsdatum|likviddag|date)/],
  ["typ", "Typ (köp/sälj)", /(typ av transaktion|transaktionstyp|^typ|händelse|^transaktion$|^text$|^rubrik)/],
  ["namn", "Värdepapper", /(värdepapper|instrument|^namn|beskrivning|^aktie|security)/],
  ["isin", "ISIN", /isin/],
  ["antal", "Antal", /^(antal|kvantitet|quantity|innehavsförändring)/],
  ["kurs", "Kurs", /^(kurs|pris|price)/],
  ["belopp", "Belopp (kr)", /^(belopp|likvidbelopp|likvid$|summa|total|amount)/],
  ["avgift", "Courtage/avgift", /(courtage|avgift|fee)/],
  ["valuta", "Valuta", /valuta|currency/],
  ["konto", "Konto/depå", /^(konto|depå|account)/]
];
function typNorm(t, antal, belopp){
  const s = String(t||"").toLowerCase();
  if (/sälj|sål|sell|avyttr/.test(s)) return "sälj";
  if (/köp|buy|förvärv/.test(s)) return "köp";
  if (/utdeln|dividend/.test(s)) return "utdelning";
  if (s.trim()) return null; // insättning, uttag, ränta, skatt m.m. används inte
  if (antal != null && antal < 0) return "sälj";
  if (belopp != null && belopp < 0) return "köp";
  if (antal != null && antal > 0) return "köp";
  return null;
}
function hashStr(s){ let h = 2166136261; for (let i = 0; i < s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36); }
function lasCsv(text){
  text = text.replace(/^﻿/, "");
  const forsta = text.split(/\r?\n/).find(r => r.trim()) || "";
  const delim = [";", "\t", ","].sort((a, b) => forsta.split(b).length - forsta.split(a).length)[0];
  const rader = []; let rad = [], f = "", q = false;
  for (let i = 0; i < text.length; i++){
    const c = text[i];
    if (q){ if (c === '"' && text[i+1] === '"'){ f += '"'; i++; } else if (c === '"') q = false; else f += c; }
    else if (c === '"') q = true;
    else if (c === delim){ rad.push(f); f = ""; }
    else if (c === "\n" || c === "\r"){ if (c === "\r" && text[i+1] === "\n") i++; rad.push(f); f = ""; if (rad.some(x => x.trim())) rader.push(rad); rad = []; }
    else f += c;
  }
  rad.push(f); if (rad.some(x => x.trim())) rader.push(rad);
  return rader;
}
// Egen xlsx-läsare: zip via centralkatalogen (klarar filer med "data descriptor", som Handelsbankens) + webbläsarens inflate
async function zipFiler(buf){
  const dv = new DataView(buf), u8 = new Uint8Array(buf); let eocd = -1;
  for (let i = u8.length - 22; i >= Math.max(0, u8.length - 65557); i--) if (dv.getUint32(i, true) === 0x06054b50){ eocd = i; break; }
  if (eocd < 0) throw new Error("Inte en zip-fil");
  const n = dv.getUint16(eocd + 10, true); let p = dv.getUint32(eocd + 16, true); const ut = {};
  for (let k = 0; k < n; k++){
    const metod = dv.getUint16(p + 10, true), komp = dv.getUint32(p + 20, true), nl = dv.getUint16(p + 28, true), el = dv.getUint16(p + 30, true), cl = dv.getUint16(p + 32, true), lok = dv.getUint32(p + 42, true);
    const namn = new TextDecoder().decode(u8.subarray(p + 46, p + 46 + nl));
    const start = lok + 30 + dv.getUint16(lok + 26, true) + dv.getUint16(lok + 28, true);
    ut[namn] = {metod, data: u8.subarray(start, start + komp)};
    p += 46 + nl + el + cl;
  }
  return async namn => { const f = ut[namn]; if (!f) return null; if (f.metod === 0) return new TextDecoder().decode(f.data);
    const ds = new Blob([f.data]).stream().pipeThrough(new DecompressionStream("deflate-raw")); return await new Response(ds).text(); };
}
async function lasXlsx(buf){
  const las = await zipFiler(buf); const xml = t => new DOMParser().parseFromString(t, "application/xml");
  const ss = []; const sst = await las("xl/sharedStrings.xml");
  if (sst) xml(sst).querySelectorAll("si").forEach(si => ss.push([...si.getElementsByTagName("t")].map(t => t.textContent).join("")));
  let blad = "xl/worksheets/sheet1.xml";
  const wb = await las("xl/workbook.xml"), rel = await las("xl/_rels/workbook.xml.rels");
  if (wb && rel){ const forsta = xml(wb).getElementsByTagName("sheet")[0]; const rid = forsta && (forsta.getAttribute("r:id") || forsta.getAttributeNS("http://schemas.openxmlformats.org/officeDocument/2006/relationships", "id"));
    const r = rid && [...xml(rel).getElementsByTagName("Relationship")].find(x => x.getAttribute("Id") === rid); if (r){ const m = r.getAttribute("Target").replace(/^\/?(xl\/)?/, ""); blad = "xl/" + m; } }
  const sh = await las(blad); if (!sh) throw new Error("Hittar inget kalkylblad");
  const kol = ref => { let n = 0; for (const c of ref.replace(/\d+/g, "")) n = n * 26 + c.charCodeAt(0) - 64; return n - 1; };
  const rader = [];
  for (const row of xml(sh).getElementsByTagName("row")){
    const rad = [];
    for (const c of row.getElementsByTagName("c")){
      const t = c.getAttribute("t"), v = c.getElementsByTagName("v")[0]; let val = "";
      if (t === "s" && v) val = ss[Number(v.textContent)] ?? ""; else if (t === "inlineStr") val = [...c.getElementsByTagName("t")].map(x => x.textContent).join(""); else if (v) val = v.textContent;
      rad[kol(c.getAttribute("r") || "A")] = val;
    }
    for (let i = 0; i < rad.length; i++) if (rad[i] == null) rad[i] = "";
    if (rad.some(x => String(x).trim())) rader.push(rad);
  }
  return rader;
}
async function lasFil(fil){
  const namn = fil.name.toLowerCase();
  if (/\.xlsx$/.test(namn)){ try { return await lasXlsx(await fil.arrayBuffer()); } catch(e){ console.warn("Egen xlsx-läsare:", e); } }
  if (/\.xlsx?$/.test(namn)){
    if (!window.XLSX) await new Promise((ok, fel) => { const s = document.createElement("script"); s.src = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"; s.onload = ok; s.onerror = () => fel(new Error("Kunde inte ladda Excel-läsaren")); document.head.appendChild(s); });
    const wb = XLSX.read(await fil.arrayBuffer(), {type: "array", cellDates: true});
    return XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], {header: 1, raw: false, defval: ""}).filter(r => r.some(x => String(x).trim()));
  }
  const buf = await fil.arrayBuffer(); const b = new Uint8Array(buf);
  const enc = b[0] === 0xff && b[1] === 0xfe ? "utf-16le" : b[0] === 0xfe && b[1] === 0xff ? "utf-16be" : "utf-8";
  let text = new TextDecoder(enc).decode(buf);
  if (enc === "utf-8" && text.includes(String.fromCharCode(0xFFFD))) text = new TextDecoder("windows-1252").decode(buf);
  return lasCsv(text);
}
function hittaRubrikrad(rader){
  let bast = 0, bastP = -1;
  const alla = [...PF_FALT, ...INNEHAV_FALT, [0, 0, /^(text|saldo|reskontradatum)$/]];
  rader.slice(0, 30).forEach((r, i) => { const p = alla.filter(([, , re]) => r.some(c => re.test(String(c).trim().toLowerCase()))).length; if (p > bastP){ bastP = p; bast = i; } });
  return bast;
}
function gissaKarta(rubriker){
  const karta = {}; const tagna = new Set();
  for (const [k, , re] of PF_FALT){ const i = rubriker.findIndex((h, j) => !tagna.has(j) && re.test(String(h).trim().toLowerCase())); if (i >= 0){ karta[k] = i; tagna.add(i); } }
  return karta;
}
function gissaKalla(filnamn, rubriker){
  const r = rubriker.join(" ").toLowerCase();
  if (/typ av transaktion|värdepapper\/beskrivning/.test(r) || /avanza|transaktioner_/.test(filnamn.toLowerCase())) return "Avanza";
  if (/handelsbanken|shb/.test(filnamn.toLowerCase()) || /verifikationsnummer|likvidbelopp \(betalvaluta\)|innehavsförändring|kortnamn/.test(r)) return "Handelsbanken";
  return "Annan bank";
}
function normalisera(rader, karta, kalla){
  const ut = [], hoppade = {};
  for (const r of rader){
    const g = k => karta[k] != null ? r[karta[k]] : null;
    const antal = tal(g("antal")), kurs = tal(g("kurs")), belopp = tal(g("belopp")), avgift = tal(g("avgift"));
    const rawTyp = String(g("typ") || "").trim(); const datum = datumNorm(g("datum")); const namn = String(g("namn") || "").trim();
    const isin = String(g("isin") || "").trim().toUpperCase().replace(/^-$/, "");
    let typ = typNorm(rawTyp, antal, belopp);
    // Bolagshändelser som ändrar antalet (split, byte, teckning, inlösen, flytt mellan egna konton …)
    if (!typ && isin && antal) typ = "händelse";
    if (!typ && isin && /teckning likvid|likvid/i.test(rawTyp) && belopp) typ = "likvid";
    if (!typ || !datum || (!namn && !isin)){ const k = rawTyp || "okänd rad"; hoppade[k] = (hoppade[k]||0) + 1; continue; }
    if ((typ === "köp" || typ === "sälj") && !antal){ hoppade["saknar antal"] = (hoppade["saknar antal"]||0) + 1; continue; }
    const konto = String(g("konto") || "").trim().replace(/\d(?=\d{4})/g, "•");
    const t = {datum, typ, namn, isin, antal: antal == null ? null : (typ === "händelse" ? antal : Math.abs(antal)), kurs, belopp, avgift: avgift == null ? null : Math.abs(avgift), valuta: String(g("valuta") || "").trim(), konto, kalla};
    if (typ === "händelse") t.handelse = rawTyp;
    t.id = hashStr([t.datum, rawTyp || t.typ, t.namn, t.isin, antal, t.kurs, t.belopp, t.konto].join("|"));
    ut.push(t);
  }
  return {rader: ut, hoppade};
}
const GENERISKT = /^(överföring|otillåtet|isk|af|internt)/i;
const rensaNamn = n => String(n||"").replace(/\b(BTU|BTA|TR|UR|TO\s*\d*|IR|SDB)\b.*$/i, "").replace(/\b(AB|publ|ser\.?|series|ltd|holding|group)\b|[().]/gi, " ").replace(/\s+/g, " ").trim();
const tokenFor = n => (rensaNamn(n).toLowerCase().match(/[a-zåäö0-9]{3,}/) || [""])[0];
const nyckelFor = t => t.isin || "namn:" + rensaNamn(t.namn).toLowerCase();
function bevakatFor(namn, isin){
  const n = String(namn||"").toLowerCase();
  return DATA.bolag.find(b => (isin && b.status.isin === isin) || (n && n.includes(b.status.namn.toLowerCase().split(" ")[0])) || (b.status.ticker && n.split(/\s+/).includes(b.status.ticker.toLowerCase())));
}
const BANKER = ["Avanza", "Handelsbanken", "Nordnet", "Annan bank"];
const bankFor = t => t.bank || (t.kalla === "Manuell" || t.kalla === "Fil" ? "Annan bank" : t.kalla);
function bankerI(d){ const n = {}; (d.transaktioner||[]).forEach(t => { const b = bankFor(t); n[b] = (n[b]||0) + 1; }); return n; }
// Antal per bank och konto (bara antal, för att visa var aktierna ligger)
function platser(d){
  const ut = {};
  for (const t of d.transaktioner || []){
    if (!t.isin && !t.namn) continue; if (t.typ === "utdelning" || t.typ === "likvid") continue;
    const a = t.typ === "sälj" ? -(t.antal||0) : (t.antal||0);
    const b = bankFor(t), k = String(t.konto || "").trim();
    (ut[t.isin || "namn:" + rensaNamn(t.namn).toLowerCase()] ||= {})[b + (k ? " · " + k : "")] = ((ut[t.isin || "namn:" + rensaNamn(t.namn).toLowerCase()] || {})[b + (k ? " · " + k : "")] || 0) + a;
  }
  return ut;
}
function beraknaPortfolj(d, bank){
  const txs = [...(d.transaktioner||[])].filter(t => !bank || bankFor(t) === bank).sort((a, b) => a.datum.localeCompare(b.datum));
  // Bästa namnet per ISIN: helst från köp/sälj, aldrig "Överföring mellan egna konton"
  const namnFor = {};
  for (const t of txs){ if (!t.isin || !t.namn || GENERISKT.test(t.namn)) continue; if (!namnFor[t.isin] || t.typ === "köp" || t.typ === "sälj") namnFor[t.isin] = t.namn; }
  // Handinmatade rader utan ISIN kopplas till samma värdepapper via namnet
  const namnTillIsin = {}; Object.entries(namnFor).forEach(([i, n]) => { const k = rensaNamn(n).toLowerCase(); if (!namnTillIsin[k]) namnTillIsin[k] = i; const bo = bevakatFor(n, i); if (bo) namnTillIsin["bolag:" + bo.slug] = i; });
  const nyckel = t => { if (t.isin) return t.isin; const bo = bevakatFor(t.namn); return (bo && namnTillIsin["bolag:" + bo.slug]) || namnTillIsin[rensaNamn(t.namn).toLowerCase()] || nyckelFor(t); };
  const pos = {}; const P = (k, t) => pos[k] || (pos[k] = {nyckel: k, isin: t.isin || "", namn: namnFor[t.isin] || t.namn, antal: 0, kostnad: 0, realiserat: 0, utdelning: 0, forsta: t.datum, senast: t.datum, antalTx: 0});
  let pool = []; let bortbokat = 0; const bortbokade = {};
  const dagar = {}; txs.forEach(t => (dagar[t.datum] = dagar[t.datum] || []).push(t));
  for (const dag of Object.keys(dagar).sort()){
    const lista = dagar[dag]; const ordning = {likvid: 0, köp: 1, händelse: 2, sälj: 3, utdelning: 4};
    lista.sort((a, b) => (ordning[a.typ] - ordning[b.typ]) || ((a.antal||0) - (b.antal||0)));
    const okningar = [];
    for (const t of lista){
      const h = P(nyckel(t), t); h.senast = t.datum; h.antalTx++;
      if (t.typ === "köp" || t.typ === "sälj") h.senastHandel = t.datum;
      if (t.kurs != null && t.kurs > 0 && t.typ !== "utdelning" && t.typ !== "likvid") h.senastKurs = t.kurs;
      if (/konkurs/i.test(t.namn) || /avskiljning|konkurs|likvidation/i.test(t.handelse || "")) h.konkurs = t.datum;
      if (/otillåtet innehav/i.test(t.namn)) h.otillatet = t.datum;
      if (t.typ === "likvid"){ h.kostnad += Math.abs(t.belopp || 0); }
      else if (t.typ === "köp"){ if (h.antal <= 1e-9 && h.kostnad <= 1e-9) h.forsta = t.datum; h.antal += t.antal; h.kostnad += t.belopp != null ? Math.abs(t.belopp) : t.antal * (t.kurs||0) + (t.avgift||0); }
      else if (t.typ === "sälj"){
        const intakt = t.belopp != null ? Math.abs(t.belopp) : t.antal * (t.kurs||0) - (t.avgift||0);
        const andel = h.antal > 0 ? Math.min(1, t.antal / h.antal) : 1; const sald = h.kostnad * andel;
        h.realiserat += intakt - sald; h.kostnad -= sald; h.antal = Math.max(0, h.antal - t.antal);
        h.saltAntal = (h.saltAntal||0) + t.antal; h.saltBelopp = (h.saltBelopp||0) + intakt; h.saltDatum = t.datum;
      }
      else if (t.typ === "utdelning"){ h.utdelning += Math.abs(t.belopp || 0); }
      else if (t.typ === "händelse"){
        if (t.antal < 0){
          const ut = Math.min(-t.antal, h.antal); const andel = h.antal > 0 ? ut / h.antal : 0;
          let flytt = h.kostnad * andel; h.antal = Math.max(0, h.antal + t.antal);
          if (h.antal <= 1e-9){ flytt = h.kostnad; h.antal = 0; }
          h.kostnad -= flytt;
          pool.push({nyckel: h.nyckel, token: tokenFor(h.namn), kostnad: flytt, dag});
        } else { if (h.antal <= 1e-9 && h.kostnad <= 1e-9) h.forsta = t.datum; h.antal += t.antal; okningar.push({h, antal: t.antal}); }
      }
    }
    // Kostnaden följer med aktierna: först till samma värdepapper (flytt mellan konton), sedan till samma bolag (split, byte, teckning)
    for (const o of okningar){
      for (const p of pool) if (p.kostnad > 0 && p.nyckel === o.h.nyckel){ o.h.kostnad += p.kostnad; p.kostnad = 0; o.klar = true; }
    }
    const grupper = {}; okningar.filter(o => !o.klar).forEach(o => { const tk = tokenFor(o.h.namn); (grupper[tk] = grupper[tk] || []).push(o); });
    for (const p of pool){
      if (p.kostnad <= 0) continue; const g = grupper[p.token]; if (!g || !p.token) continue;
      const sum = g.reduce((a, o) => a + o.antal, 0);
      g.forEach(o => { o.h.kostnad += p.kostnad * o.antal / sum; }); p.kostnad = 0;
    }
    // Det som inte hittat nytt hem inom 60 dagar räknas som bortbokat (t.ex. konkurs eller flytt till konto utanför filen)
    pool = pool.filter(p => { if (p.kostnad <= 0.005) return false; const gammal = (new Date(dag) - new Date(p.dag)) / 864e5 > 60; if (gammal){ bortbokat += p.kostnad; bortbokade[p.token] = (bortbokade[p.token]||0) + p.kostnad; } return !gammal; });
  }
  pool.forEach(p => { if (p.kostnad > 0.005){ bortbokat += p.kostnad; bortbokade[p.token] = (bortbokade[p.token]||0) + p.kostnad; } });
  const alla = Object.values(pos);
  for (const h of alla){
    h.gav = h.antal > 0 ? h.kostnad / h.antal : null;
    h.bolag = bevakatFor(h.namn, h.isin);
    const manuell = (d.kurser||{})[h.nyckel];
    if (manuell && manuell.ingen_kurs) h.ingenKurs = manuell.datum;
    if (manuell && manuell.kurs != null) { h.kurs = manuell.kurs; h.kursKalla = "manuell"; h.kursDatum = manuell.datum; h.kursFranYahoo = /yahoo/i.test(manuell.kalla || ""); h.kursKallaNamn = manuell.kalla; }
    if (h.bolag && h.bolag.kurs && !(manuell && manuell.datum > String(h.bolag.kurs.tid||""))) { h.kurs = h.bolag.kurs.kurs; h.kursKalla = "auto"; h.kursDatum = String(h.bolag.kurs.tid||"").slice(0,10); }
    h.varde = h.kurs != null && h.antal > 0 ? h.kurs * h.antal : null;
    h.orealiserat = h.varde != null ? h.varde - h.kostnad : null;
    h.orealiseratPct = h.varde != null && h.kostnad > 0 ? (h.varde / h.kostnad - 1) * 100 : null;
  }
  // Konkurs och avnotering känns igen automatiskt: aktierna saknar värde och skrivs av som förlust
  const tillbaka = d.aktiva_igen || {};
  for (const h of alla){
    if (h.antal <= 1e-6 || tillbaka[h.nyckel]) continue;
    const ingenHandel = !h.senastHandel || (Date.now() - new Date(h.senastHandel)) / 864e5 > 365;
    if (h.konkurs) h.avslut = {typ: "Konkurs", datum: h.konkurs, varfor: "Bolaget har gått i konkurs enligt banken. Aktierna saknar värde."};
    else if (h.ingenKurs && (h.otillatet || ingenHandel)) h.avslut = {typ: "Avnoterad", datum: h.otillatet || h.ingenKurs, varfor: `Ingen handel hittas längre${h.otillatet ? ", och banken flyttade aktierna som otillåtet innehav på ISK, vilket brukar betyda avnotering" : ""}.`};
    if (h.avslut){
      // Avnoterade aktier har ofta kvar ett litet restvärde till senast kända kurs (så räknar banken). Konkurs = 0.
      h.restvarde = h.avslut.typ === "Avnoterad" && h.senastKurs ? h.antal * h.senastKurs : 0;
      if (h.restvarde) h.avslut.varfor += ` Banken räknar fortfarande med senast kända kurs (${fmt(h.senastKurs, 3)} kr), alltså ett restvärde på ${fmt(h.restvarde, 0)} kr.`;
      h.avskrivet = h.kostnad - h.restvarde; h.realiserat -= h.avskrivet; h.kostnad = 0; h.varde = 0; h.orealiserat = null;
    }
  }
  const dolda = d.dolda || {};
  const aktiva = alla.filter(h => h.antal > 1e-6 && !dolda[h.nyckel] && !h.avslut).sort((a, b) => (b.varde ?? b.kostnad) - (a.varde ?? a.kostnad));
  // Sålt allt: bevakas i ett år (eller tills du arkiverar), sedan arkiv. Du kan ändra själv.
  const ar = Date.now() - 365 * 864e5;
  alla.forEach(h => { if (h.antal <= 1e-6 && h.saltDatum && !h.avslut){ const val = (d.salt_lage || {})[h.nyckel]; h.saltLage = val || (new Date(h.saltDatum) >= ar ? "bevakas" : "arkiv");
    if (h.kurs != null && h.saltAntal) { h.vardeOmKvar = h.saltAntal * h.kurs; h.snittSalj = h.saltBelopp / h.saltAntal; } } });
  const stangda = alla.filter(h => h.avslut || ((h.antal <= 1e-6 || dolda[h.nyckel]) && (Math.abs(h.realiserat) > 0.5 || h.utdelning > 0.5))).sort((a, b) => b.senast.localeCompare(a.senast));
  const restvarde = alla.reduce((a, h) => a + (h.restvarde || 0), 0);
  const totVarde = aktiva.reduce((a, h) => a + (h.varde ?? 0), 0) + restvarde, basAndel = aktiva.reduce((a, h) => a + (h.varde ?? h.kostnad), 0);
  aktiva.forEach(h => h.andel = basAndel ? (h.varde ?? h.kostnad) / basAndel * 100 : 0);
  const sum = (arr, f) => arr.reduce((a, h) => a + (h[f] || 0), 0);
  const medKurs = aktiva.filter(h => h.varde != null);
  return {aktiva, stangda, saltBevakas: alla.filter(h => h.saltLage === "bevakas"), dolda: alla.filter(h => dolda[h.nyckel] && h.antal > 1e-6), bortbokade, tot: {kostnad: sum(aktiva, "kostnad"), varde: totVarde, kostnadMedKurs: sum(medKurs, "kostnad"), orealiserat: sum(medKurs, "orealiserat"), utanKurs: aktiva.length - medKurs.length, restvarde, realiserat: sum(alla, "realiserat") - bortbokat, bortbokat, avskrivet: sum(alla, "avskrivet"), utdelning: sum(alla, "utdelning")}};
}
function strategiKoll(h){
  const ut = []; const b = h.bolag;
  if (!b){ ut.push(["gra", "Ingen tes i verktyget. Be Claude analysera bolaget om du vill följa det här."]); return ut; }
  const s = b.status, p = s.redo && arVandning(s) ? s.redo.punkter.reduce((a, x) => a + x.poang, 0) : null;
  const fas = p == null ? null : p >= 15 ? 2 : p >= 10 ? 1 : 0;
  if (s.trafikljus === "rod") ut.push(["rod", "Tesen är skadad (rött). Enligt din strategi är det läge att ompröva innehavet."]);
  else if (s.trafikljus === "gul") ut.push(["gul", "Gult: något att bevaka noga. Läs senaste nytt."]);
  if (s.beslut === "Kasta") ut.push(["rod", "Bolaget är kastat i verktyget. Läs skälen under Kastade."]);
  if (fas === 0) ut.push(["gul", `Redo-poäng ${p}/20: för tidigt enligt din strategi.`]);
  if (fas === 1) ut.push([h.andel > 10 ? "gul" : "gron", `Fas 1 (redo-poäng ${p}/20): din strategi säger en liten startposition.${h.andel > 10 ? ` Innehavet är ${fmt(h.andel,0)} % av portföljen, alltså mer än en startposition.` : ""}`]);
  if (fas === 2) ut.push(["gron", `Fas 2 (redo-poäng ${p}/20): läge att ta ställning till en större position enligt din strategi.`]);
  if (!arVandning(s)) ut.push(["gra", `Mäts som Kärna${s.lynch ? ` (${LYNCH[s.lynch] || s.lynch})` : ""}: följ lönsamheten och priset, inte en vändning.`]);
  if (s.nasta_handelse) ut.push(["gra", `Nästa händelse: ${s.nasta_handelse}`]);
  return ut;
}
const kr = (v, d = 0) => v == null ? "–" : `${fmt(v, d)} kr`;
const plus = (v, d = 0, enh = " kr") => v == null ? "–" : `<span style="color:${v < 0 ? "var(--bad)" : "var(--ok)"}">${v >= 0 ? "+" : ""}${fmt(v, d)}${enh}</span>`;
async function pfSpara(){
  if (!PF.db || !PF.uid) throw new Error("Inte inloggad");
  PF.sparar = true;
  try { await PF.db.doc(`data/users/${PF.uid}/portfolj`).set(JSON.parse(JSON.stringify(PF.data))); }
  catch(e){ if (e && e.code === "invalid_argument") PF.kanSkriva = false; throw e; }
  finally { PF.sparar = false; }
}
async function pfStart(){
  try {
    if (!window.claude || !window.claude.use) { PF.laddad = true; return; }
    const [db, user] = await Promise.all([window.claude.use("db"), window.claude.use("user")]);
    if (!db || !user){ PF.laddad = true; if (location.hash === "#portfolj") vyPortfolj(); return; }
    PF.db = db; PF.uid = await user.id();
    if (!PF.uid){ PF.laddad = true; if (location.hash === "#portfolj") vyPortfolj(); return; }
    const timer = setTimeout(() => { if (!PF.laddad){ PF.fel = "Portföljen går inte att nå just nu. Prova att ladda om sidan om en stund."; if (location.hash === "#portfolj") vyPortfolj(); } }, 10000);
    PF.unsub = db.doc(`data/users/${PF.uid}/portfolj`).onSnapshot(snap => {
      if (!snap.metadata.fromCache) clearTimeout(timer);
      PF.data = snap.exists ? {...PF_TOM(), ...JSON.parse(JSON.stringify(snap.data()))} : PF_TOM();
      PF.laddad = true; PF.fel = null;
      const hh = location.hash || "#lage"; if (/^#(lage|bevakning|nyheter|fonder)$/.test(hh) || hh.startsWith("#bolag-")) route();
      if (location.hash === "#portfolj" && !PF.forhand && !document.activeElement?.closest?.("#vy form")) vyPortfolj();
    }, e => { clearTimeout(timer); PF.laddad = true; PF.fel = "Portföljen kunde inte läsas (" + (e && e.code) + ")."; if (location.hash === "#portfolj") vyPortfolj(); });
  } catch(e){ PF.laddad = true; }
}
// --- fondkoll: överlapp och genomlysning av det användaren äger (bara i webbläsaren, privat) ---
function rensaFondnamn(n){ return String(n||"").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/\b(sek|eur|nok|usd|acc|dis|klass|class|a|b|c|d)\d*\b/g, " ").replace(/[^a-z0-9]+/g, " ").trim(); }
function fondFor(h){
  const reg = DATA.fondregister || [];
  const r = reg.find(x => x[0] === h.isin) || reg.find(x => { const a = rensaFondnamn(x[1]); return a.length > 6 && a === rensaFondnamn(h.namn); });
  if (r) return {isin: r[0], namn: r[1], avgift: r[2], foljd: (DATA.fonder||[]).find(f => f.isin === r[0])};
  if (!h.bolag && /fond|fund|ucits|etf|index/i.test(h.namn)) return {namn: h.namn, utanfor: true};
  return null;
}
function fondkoll(aktiva){
  const fonder = aktiva.map(h => ({h, f: fondFor(h)})).filter(x => x.f);
  if (!fonder.length) return null;
  const varde = h => h.varde ?? h.kostnad ?? 0;
  const tot = aktiva.reduce((a, h) => a + varde(h), 0) || 1;
  const varningar = [];
  const foljda = fonder.filter(x => x.f.foljd);
  for (let i = 0; i < foljda.length; i++) for (let j = i + 1; j < foljda.length; j++){
    const a = foljda[i].f, b = foljda[j].f, o = (a.foljd.overlapp || {})[b.isin];
    if (o != null && o >= 50) varningar.push(["gul", `<b>${esc(a.namn)}</b> och <b>${esc(b.namn)}</b> äger till ${fmt(o, 0)} % samma sak. Du sprider alltså inte risken så mycket som det ser ut, men betalar två avgifter (${fmt(a.avgift, 2)} % och ${fmt(b.avgift, 2)} %).`]);
  }
  const exp = {};
  for (const {h, f} of foljda){
    for (const i of f.foljd.innehav){ if (i.typ === "Övrigt") continue; const k = i.isin || i.namn; const e = exp[k] || (exp[k] = {namn: snyggt(i.namn), v: 0, via: [], direkt: false}); e.v += varde(h) * i.andel / 100; e.via.push(f.namn); }
  }
  for (const h of aktiva){ if (fonder.some(x => x.h === h)) continue; const k = h.isin || h.nyckel; const e = exp[k] || (exp[k] = {namn: h.namn, v: 0, via: [], direkt: false}); e.v += varde(h); e.direkt = true; }
  const topp = Object.values(exp).map(e => ({...e, pct: e.v / tot * 100})).sort((a, b) => b.v - a.v);
  for (const e of topp){
    const kallor = e.via.length + (e.direkt ? 1 : 0);
    if (e.pct >= 10 && kallor >= 2) varningar.push(["gul", `Du äger <b>${esc(e.namn)}</b> ${e.direkt ? "både direkt och " : ""}via ${e.via.length} ${e.via.length === 1 ? "fond" : "fonder"}. Tillsammans är det ca ${fmt(e.pct, 0)} % av portföljen, mer än det kan se ut som.`]);
    else if (e.direkt && e.via.length && e.pct >= 3) varningar.push(["gra", `Du äger <b>${esc(e.namn)}</b> både direkt och via ${esc(e.via.join(", "))}. Tillsammans ca ${fmt(e.pct, 1)} % av portföljen.`]);
  }
  const ejFoljda = fonder.filter(x => !x.f.foljd && !x.f.utanfor), utanfor = fonder.filter(x => x.f.utanfor);
  if (ejFoljda.length) varningar.push(["gra", `${ejFoljda.map(x => `<b>${esc(x.f.namn)}</b>`).join(", ")} ${ejFoljda.length === 1 ? "följs" : "följs"} inte i verktyget än, så ${ejFoljda.length === 1 ? "den" : "de"} kan inte kontrolleras. Skriv <i>följ fonden ${esc(ejFoljda[0].f.namn)}</i> i Claude-appen.`]);
  if (utanfor.length) varningar.push(["gra", `${utanfor.map(x => `<b>${esc(x.f.namn)}</b>`).join(", ")} finns inte i Finansinspektionens data. Den är troligen registrerad utomlands, så innehaven kan inte kontrolleras automatiskt.`]);
  return {fonder, varningar, topp: topp.slice(0, 10), fondandel: fonder.reduce((a, x) => a + varde(x.h), 0) / tot * 100, saknarKurs: fonder.some(x => x.h.varde == null)};
}
function fondkollHtml(aktiva, rubrik = true){
  const k = fondkoll(aktiva); if (!k) return "";
  const ikon = {gul: "⚠️", gra: "ℹ️"};
  return `<section class="nt fondkoll">${rubrik ? `<h2>Fondkoll: vad du äger via dina fonder</h2>` : ""}<p class="hint" style="margin-top:0">Verktyget lyser igenom dina fonder och lägger ihop det med aktierna du äger direkt. Det här ser bara du. ${k.saknarKurs ? "Fonder utan aktuell kurs räknas på vad du betalade. " : ""}Fonderna är ca ${fmt(k.fondandel, 0)} % av portföljen.</p>
    ${k.varningar.length ? k.varningar.map(([n, txt]) => `<div class="callout${n === "gul" ? " flag" : ""}"><p style="margin:0">${ikon[n]} ${txt}</p></div>`).join("") : `<div class="callout"><p style="margin:0">✅ Inga stora överlapp hittades mellan dina fonder och aktier.</p></div>`}
    ${k.topp.length ? `<div class="label" style="margin-top:12px">Dina största bolag efter genomlysningen</div><div class="tw2"><table class="matris"><tr><th style="text-align:left">Bolag</th><th style="text-align:left">Hur du äger det</th><th>Andel av portföljen</th></tr>${k.topp.map(e => `<tr><td style="text-align:left">${esc(e.namn)}</td><td style="text-align:left;font-size:12.5px">${[e.direkt ? "direkt" : "", ...e.via.map(esc)].filter(Boolean).join(", ")}</td><td>${fmt(e.pct, 1)} %</td></tr>`).join("")}</table></div>` : ""}
  </section>`;
}
function fordelningHtml(aktiva){
  const tot = aktiva.reduce((a, h) => a + (h.andel || 0), 0); if (!tot) return "";
  const grupp = (nyckel, namn) => { const g = {}; aktiva.forEach(h => { const k = h.bolag ? nyckel(h.bolag.status) : "ej"; g[k] = (g[k] || 0) + (h.andel || 0); }); return Object.entries(g).sort((a, b) => b[1] - a[1]).map(([k, v]) => [namn(k), v / tot * 100]); };
  const spar = grupp(s => s.spar === "karna" ? "karna" : s.spar ? "vandning" : "ingen", k => k === "ej" ? "Följs inte" : k === "ingen" ? "Spår ej satt" : SPAR[k][0]);
  const lynch = grupp(s => s.lynch || "ingen", k => k === "ej" ? "Följs inte" : LYNCH[k] || "Ej satt");
  const rad = (rubrik, del) => `<div style="margin:8px 0"><div class="label">${rubrik}</div><div class="bar" style="display:flex;height:10px;margin:6px 0 4px">${del.map(([n, v], i) => `<b title="${esc(n)} ${fmt(v,0)} %" style="width:${v}%;opacity:${1 - i * 0.14};border-right:2px solid var(--surface)"></b>`).join("")}</div><div class="lek-m">${del.map(([n, v]) => `${esc(n)} ${fmt(v,0)} %`).join(" · ")}</div></div>`;
  return `<details class="fold"><summary><span class="ft">Fördelning</span><span class="fs">${spar.map(([n, v]) => `${esc(n)} ${fmt(v,0)} %`).join(" · ")}</span></summary>${rad("Spår (andel av värdet)", spar)}${rad("Peter Lynchs kategorier", lynch)}<p class="hint">Vändning är bolag som ska bevisa en vändning, Kärna är lönsamma bolag. Om du vill ha en målfördelning kan du skriva den i Min strategi. Fördelningen är bara en bild av läget och inget råd.</p></details>`;
}
function vyPortfolj(){
  const v = $("#vy");
  const head = `<h1>Min portfölj</h1><p class="lede">Dina innehav, vad de kostade och hur de går, kopplat till din strategi och verktygets bedömning. <b>Privat:</b> bara du ser din portfölj, även om sidan är delad. Inget här är köp- eller säljråd.</p>`;
  if (!PF.laddad){ v.innerHTML = head + `<div class="empty">Laddar portföljen…</div>`; return; }
  if (!PF.db || !PF.uid){ v.innerHTML = head + `<div class="empty">Portföljen fungerar bara när sidan är öppnad inloggad på claude.ai. Där sparas den privat i ditt konto.</div>`; return; }
  if (PF.fel && !PF.data){ v.innerHTML = head + `<div class="empty">${esc(PF.fel)}</div>`; return; }
  const d = PF.data || PF_TOM();
  const finns = bankerI(d); const bankLista = Object.keys(finns).sort();
  if (!PF.bank){ try { PF.bank = localStorage.getItem("ih-pf-bank") || "alla"; } catch(e){ PF.bank = "alla"; } }
  if (PF.bank !== "alla" && !finns[PF.bank]) PF.bank = "alla";
  const valdBank = PF.bank === "alla" ? null : PF.bank;
  const r = beraknaPortfolj(d, valdBank);
  PF.platser = platser(d);
  const bankval = bankLista.length ? `<div class="filters pf-bankval" role="tablist" aria-label="Välj bank"><button type="button" data-bank="alla" class="${!valdBank ? "on" : ""}">Alla banker</button>${bankLista.map(b => `<button type="button" data-bank="${esc(b)}" class="${valdBank === b ? "on" : ""}">${esc(b)}</button>`).join("")}</div>
    <p class="hint" style="margin:6px 0 12px">${valdBank ? `Visar bara det som ligger hos <b>${esc(valdBank)}</b>.` : `Visar allt kombinerat${bankLista.length > 1 ? ` från ${bankLista.length} banker` : ""}. Välj en bank för att se bara den.`}</p>` : "";
  const kort = [
    ["Värde nu", kr(r.tot.varde), (r.tot.utanKurs ? `${r.tot.utanKurs} innehav saknar kurs och räknas inte med. ` : "Med senaste kurserna. ") + (r.tot.restvarde >= 0.5 ? `Inklusive ${kr(r.tot.restvarde)} restvärde i avnoterade aktier.` : "")],
    ["Investerat", kr(r.tot.kostnad), "Vad det du äger nu kostade (snittpris × antal)"],
    ["Upp/ner", plus(r.tot.orealiserat), r.tot.kostnadMedKurs ? `${plus(r.tot.orealiserat / r.tot.kostnadMedKurs * 100, 1, " %")} på innehaven med kurs` : ""],
    ["Realiserat + utdelning", plus(r.tot.realiserat + r.tot.utdelning), `Utdelning ${kr(r.tot.utdelning)}${r.tot.avskrivet > 0.5 ? ` · konkurs/avnoterat ${kr(-r.tot.avskrivet)}` : ""}${r.tot.bortbokat > 0.5 ? ` · bortbokat ${kr(r.tot.bortbokat)}` : ""}`],
  ];
  const fasN = [1, 2].map(f => r.aktiva.filter(h => { const p = h.bolag?.status.redo?.punkter.reduce((a, x) => a + x.poang, 0); return p != null && (f === 2 ? p >= 15 : p >= 10 && p < 15); }).length);
  v.innerHTML = head + bankval + (PF.fel ? `<div class="callout flag"><p style="margin:0">${esc(PF.fel)}</p></div>` : "") + (r.aktiva.length || r.stangda.length ? `
    <div class="snabb">${kort.map(([l, val, sub]) => `<div class="sf"><div class="label">${l}</div><div class="v num">${val}</div><div class="s">${sub}</div></div>`).join("")}</div>
    <p class="hint" style="margin:0 0 14px">${r.aktiva.length} innehav · ${r.aktiva.filter(h => h.bolag).length} följs i verktyget · ${fasN[0]} i fas 1 och ${fasN[1]} i fas 2 · största innehavet är ${fmt(r.aktiva[0]?.andel || 0, 0)} % av portföljen. Din strategi: 2–3 vinnare ska bära portföljen, så många små tidiga positioner och färre stora.</p>
    ${fondkollHtml(r.aktiva)}
    ${fordelningHtml(r.aktiva)}
    <div class="pf-lista">${r.aktiva.map(h => pfKort(h, d)).join("")}</div>
    ${r.dolda.length ? `<p class="lek-m">Dolda innehav: ${r.dolda.map(h => `${esc(h.namn)} <button type="button" class="lank-knapp" data-visa="${esc(h.nyckel)}">visa igen</button>`).join(" · ")}</p>` : ""}
    ${r.saltBevakas.length ? `<h2>Sålt, bevakas</h2><p class="hint" style="margin-top:0">Bolag du har sålt helt men fortsätter följa, ifall läget vänder. Flytta till arkivet när du inte vill följa dem längre.</p><div class="pf-lista">${r.saltBevakas.map(h => { const not = (d.anteckningar||{})[h.nyckel] || {}; return `<article class="pf-kort"><div class="lk-top"><h2>${h.bolag ? `<a href="#bolag-${esc(h.bolag.slug)}">${esc(h.namn)}</a>` : esc(h.namn)}</h2>${h.bolag ? ljus(h.bolag.status) : `<span class="pill" style="background:var(--sunk);color:var(--muted)">Följs inte i verktyget</span>`}<span class="lek-m">Sålt ${esc(h.saltDatum)}</span></div>
      <div class="pf-tal"><div><span class="label">Resultat</span><b class="num">${plus(h.realiserat)}</b></div><div><span class="label">Snitt säljkurs</span><b class="num">${h.snittSalj ? kr(h.snittSalj, 2) : "–"}</b></div><div><span class="label">Kurs nu</span><b class="num">${h.kurs != null ? kr(h.kurs, 2) : "–"}</b></div><div><span class="label">Värt i dag om du behållit</span><b class="num">${h.vardeOmKvar != null ? kr(h.vardeOmKvar) : "–"}</b><small>${h.vardeOmKvar != null && h.saltBelopp ? plus(h.vardeOmKvar - h.saltBelopp) + " mot vad du fick" : ""}</small></div></div>
      ${not.salj_varfor ? `<p class="lek-m" style="margin:0">Varför du sålde: ${esc(not.salj_varfor)}</p>` : ""}
      <form class="pf-not-form" data-k="${esc(h.nyckel)}" data-falt="salj_varfor"><label>Varför sålde jag? Vad skulle få mig att köpa igen?<textarea name="salj_varfor" rows="2">${esc(not.salj_varfor||"")}</textarea></label><span><button type="submit" class="knapp">Spara</button> <button type="button" class="lank-knapp" data-arkiv="${esc(h.nyckel)}">Flytta till arkivet</button> <span class="lek-m pf-status"></span></span></form></article>`; }).join("")}</div>` : ""}
    ${r.stangda.length ? `<h2>Sålda och avslutade innehav</h2><p class="hint" style="margin-top:0">Bolag som gått i konkurs eller avnoterats flyttas hit automatiskt och räknas som förlust. Har det blivit fel kan du flytta tillbaka innehavet.</p><div class="tw2"><table class="matris"><tr><th style="text-align:left">Värdepapper</th><th>Resultat</th><th>Utdelning</th><th>Period</th></tr>${r.stangda.map(h => `<tr><td style="text-align:left">${esc(h.namn)}${h.avslut ? `<br><span class="pill p-kasta">${esc(h.avslut.typ)}</span> <span class="lek-m">${esc(h.avslut.varfor)}</span> <button type="button" class="lank-knapp" data-igen="${esc(h.nyckel)}">räkna som aktivt igen</button>` : ""}${h.saltLage === "arkiv" ? ` <button type="button" class="lank-knapp" data-bevaka="${esc(h.nyckel)}">bevaka igen</button>` : h.saltLage === "bevakas" ? ` <span class="lek-m">(bevakas)</span>` : ""}</td><td>${plus(h.realiserat)}</td><td>${kr(h.utdelning)}</td><td>${esc(h.forsta)} – ${esc(h.senast)}</td></tr>`).join("")}</table></div>` : ""}`
    : `<div class="empty">Ingen portfölj än. Läs in en fil från banken nedan, eller lägg till ett köp för hand.</div>`) + pfImportHtml(d);
  pfKoppla(r);
}
function platsHtml(h){
  const p = (PF.platser || {})[h.isin || h.nyckel]; if (!p) return "";
  const delar = Object.entries(p).filter(([, a]) => a > 1e-6).sort((a, b) => b[1] - a[1]);
  if (!delar.length) return "";
  return `<p class="pf-plats"><span class="label">Finns hos</span> ${delar.map(([k, a]) => `<span class="pf-bank">${esc(k)}: <b class="num">${fmt(a, a % 1 ? 2 : 0)} st</b></span>`).join("")}</p>`;
}
function pfKort(h, d){
  const not = (d.anteckningar||{})[h.nyckel] || {};
  const koll = strategiKoll(h);
  return `<article class="pf-kort" data-k="${esc(h.nyckel)}">
    <div class="lk-top"><h2>${h.bolag ? `<a href="#bolag-${esc(h.bolag.slug)}">${esc(h.namn)}</a>` : esc(h.namn)}</h2>${h.bolag ? ljus(h.bolag.status) : `<span class="pill" style="background:var(--sunk);color:var(--muted)">Följs inte</span>`}<span class="lek-m">${fmt(h.andel,0)} % av portföljen</span></div>
    ${platsHtml(h)}
    <div class="pf-tal">
      <div><span class="label">Antal</span><b class="num">${fmt(h.antal, h.antal % 1 ? 2 : 0)}</b></div>
      <div><span class="label">Snittpris (GAV)</span><b class="num">${kr(h.gav, 2)}</b></div>
      <div><span class="label">Kurs nu</span><b class="num">${h.kurs != null ? kr(h.kurs, 2) : "–"}</b><small>${h.kursKalla === "auto" ? `hämtad ${esc(h.kursDatum)}` : h.kursKalla === "manuell" ? `${h.kursFranYahoo ? "hämtad" : h.kursKallaNamn && h.kursKallaNamn !== "Manuell" ? "från " + esc(h.kursKallaNamn) : "inskriven"} ${esc(h.kursDatum||"")}` : ""} <button type="button" class="lank-knapp" data-kurs="${esc(h.nyckel)}">${h.kursKalla === "auto" ? "" : h.kurs != null ? "ändra" : "ange kurs"}</button></small></div>
      <div><span class="label">Investerat</span><b class="num">${kr(h.kostnad)}</b></div>
      <div><span class="label">Värde</span><b class="num">${kr(h.varde)}</b></div>
      <div><span class="label">Upp/ner</span><b class="num">${plus(h.orealiserat)} ${h.orealiseratPct != null ? `(${plus(h.orealiseratPct, 0, " %")})` : ""}</b></div>
    </div>
    <ul class="pf-koll">${koll.map(([f, t]) => `<li class="k-${f}">${esc(t)}</li>`).join("")}</ul>
    <details class="pf-not"${not.varfor || not.salj ? "" : ""}><summary>Mina anteckningar${not.varfor || not.salj ? " ✓" : ""}: varför jag köpte och när jag säljer</summary>
      <form class="pf-not-form" data-k="${esc(h.nyckel)}">
        <label>Varför köpte jag? Vad väntar jag mig?<textarea name="varfor" rows="2">${esc(not.varfor||"")}</textarea></label>
        <label>Jag säljer om… (bestäm i förväg)<textarea name="salj" rows="2">${esc(not.salj||"")}</textarea></label>
        <button type="submit" class="knapp">Spara anteckningar</button> <span class="lek-m pf-status"></span>
      </form>
    </details>
    <p class="hint" style="margin:0"><button type="button" class="lank-knapp" data-dolj="${esc(h.nyckel)}">Dölj innehavet</button> (till exempel om bolaget gått i konkurs eller avnoterats) · Köpt första gången ${esc(h.forsta)} · ${h.antalTx} transaktioner${h.utdelning ? ` · utdelning ${kr(h.utdelning)}` : ""}${h.realiserat ? ` · realiserat ${plus(h.realiserat)}` : ""}</p>
  </article>`;
}
function pfImportHtml(d){
  return `<h2 id="pf-import">Läs in eller lägg till</h2>
  <div class="pf-import">
    <div class="pf-ruta">
      <h3>Läs in från banken</h3>
      <p class="lek-m" style="margin-top:0"><b>Avanza:</b> Min ekonomi → Transaktioner → välj period → Exportera (CSV).<br><b>Handelsbanken:</b> gå till din depå och exportera <b>innehavet</b> (eller depåtransaktionerna) till Excel. Kontoutdrag från ISK-kontot räcker inte, eftersom de bara visar pengar.<br>Filen läses i din webbläsare. Bara köp, sälj och utdelningar sparas, privat i ditt konto. Kontonummer kortas.</p>
      <input type="file" id="pf-fil" accept=".csv,.txt,.xlsx,.xls">
      <div id="pf-forhand"></div>
    </div>
    <div class="pf-ruta">
      <h3>Lägg till för hand</h3>
      <form id="pf-manuell" class="pf-form">
        <label>Datum<input type="date" name="datum" required></label>
        <label>Bank<select name="bank">${BANKER.map(b => `<option${(PF.bank === b) ? " selected" : ""}>${b}</option>`).join("")}</select></label>
        <label>Typ<select name="typ"><option value="köp">Köp</option><option value="sälj">Sälj</option><option value="utdelning">Utdelning</option></select></label>
        <label class="bred">Värdepapper<input name="namn" list="pf-namn" required placeholder="t.ex. Unibap Space Solutions"></label>
        <label>Antal<input name="antal" inputmode="decimal"></label>
        <label>Kurs (kr)<input name="kurs" inputmode="decimal"></label>
        <label>Courtage (kr)<input name="avgift" inputmode="decimal" value="0"></label>
        <label>Belopp (vid utdelning)<input name="belopp" inputmode="decimal"></label>
        <button type="submit" class="knapp">Lägg till</button>
        <datalist id="pf-namn">${DATA.bolag.map(b => `<option value="${esc(b.status.namn)}">`).join("")}</datalist>
      </form>
    </div>
  </div>
  <details class="mer"><summary>Alla transaktioner (${(d.transaktioner||[]).length}) och inställningar</summary>
    <div class="tw2"><table class="matris pf-tx"><tr><th style="text-align:left">Datum</th><th style="text-align:left">Typ</th><th style="text-align:left">Värdepapper</th><th>Antal</th><th>Kurs</th><th>Belopp</th><th>Källa</th><th></th></tr>
    ${[...(d.transaktioner||[])].sort((a, b) => b.datum.localeCompare(a.datum)).map(t => `<tr><td style="text-align:left">${esc(t.datum)}</td><td style="text-align:left">${esc(t.typ)}</td><td style="text-align:left">${esc(t.namn)}</td><td>${fmt(t.antal, t.antal % 1 ? 2 : 0)}</td><td>${t.kurs != null ? fmt(t.kurs, 2) : "–"}</td><td>${t.belopp != null ? fmt(t.belopp, 0) : "–"}</td><td>${esc(t.kalla)}</td><td><button type="button" class="lank-knapp" data-tabort="${esc(t.id)}">ta bort</button></td></tr>`).join("")}</table></div>
    <p class="lek-m">Importer: ${(d.importer||[]).map(i => `${esc(i.datum)} ${esc(i.kalla)} (${i.antal} nya)`).join(" · ") || "inga än"}.</p>
    <p class="lek-m">Ditt portfölj-id, om du vill att Claude Code ska läsa portföljen: <code>${esc(PF.uid||"")}</code></p>
    <button type="button" class="knapp knapp-fara" id="pf-rensa">Radera hela portföljen</button>
  </details>`;
}
async function pfAndra(fn, statusEl, okText){
  const fore = JSON.stringify(PF.data);
  try { fn(PF.data); await pfSpara(); if (statusEl) statusEl.textContent = okText || "Sparat."; }
  catch(e){ PF.data = JSON.parse(fore); const t = e && e.code === "quota_exceeded" ? "Portföljen är full. Ta bort gamla transaktioner." : PF.kanSkriva ? "Kunde inte spara. Försök igen." : "Du har inte behörighet att spara här."; if (statusEl) statusEl.textContent = t; else alert(t); }
}
function pfKoppla(r){
  const v = $("#vy");
  v.querySelectorAll(".pf-not-form").forEach(f => f.onsubmit = e => { e.preventDefault(); const k = f.dataset.k;
    if (f.dataset.falt === "salj_varfor"){ const t = f.salj_varfor.value.trim(); return pfAndra(d => { d.anteckningar[k] = {...(d.anteckningar[k]||{}), salj_varfor: t, datum: new Date().toISOString().slice(0,10)}; }, f.querySelector(".pf-status")); }
    const varfor = f.varfor.value.trim(), salj = f.salj.value.trim(); pfAndra(d => { d.anteckningar[k] = {...(d.anteckningar[k]||{}), varfor, salj, datum: new Date().toISOString().slice(0,10)}; }, f.querySelector(".pf-status")); });
  v.querySelectorAll("[data-arkiv]").forEach(btn => btn.onclick = () => { const k = btn.dataset.arkiv; pfAndra(d => { d.salt_lage = d.salt_lage || {}; d.salt_lage[k] = "arkiv"; }); });
  v.querySelectorAll("[data-bevaka]").forEach(btn => btn.onclick = () => { const k = btn.dataset.bevaka; pfAndra(d => { d.salt_lage = d.salt_lage || {}; d.salt_lage[k] = "bevakas"; }); });
  v.querySelectorAll("[data-kurs]").forEach(btn => { if (!btn.textContent) return; btn.onclick = () => { const k = btn.dataset.kurs; const s = prompt("Senaste kurs i kronor (finns på bankens sida):"); const n = tal(s); if (n == null || n < 0) return; pfAndra(d => { d.kurser[k] = {kurs: n, datum: new Date().toISOString().slice(0,10)}; }); }; });
  v.querySelectorAll("[data-tabort]").forEach(btn => btn.onclick = () => { if (!confirm("Ta bort transaktionen?")) return; const id = btn.dataset.tabort; pfAndra(d => { d.transaktioner = d.transaktioner.filter(t => t.id !== id); }); });
  v.querySelectorAll("[data-dolj]").forEach(btn => btn.onclick = () => { const k = btn.dataset.dolj; pfAndra(d => { d.dolda = d.dolda || {}; d.dolda[k] = true; }); });
  v.querySelectorAll("[data-bank]").forEach(btn => btn.onclick = () => { PF.bank = btn.dataset.bank; try { localStorage.setItem("ih-pf-bank", PF.bank); } catch(e){} vyPortfolj(); });
  v.querySelectorAll("[data-igen]").forEach(btn => btn.onclick = () => { const k = btn.dataset.igen; pfAndra(d => { d.aktiva_igen = d.aktiva_igen || {}; d.aktiva_igen[k] = true; }); });
  v.querySelectorAll("[data-visa]").forEach(btn => btn.onclick = () => { const k = btn.dataset.visa; pfAndra(d => { d.dolda = d.dolda || {}; delete d.dolda[k]; }); });
  const rensa = $("#pf-rensa"); if (rensa) rensa.onclick = () => { if (!confirm("Radera alla transaktioner, kurser och anteckningar? Det går inte att ångra.")) return; pfAndra(d => { Object.assign(d, PF_TOM()); }); };
  const man = $("#pf-manuell"); if (man) man.onsubmit = e => { e.preventDefault(); const f = man;
    const t = {datum: f.datum.value, typ: f.typ.value, namn: f.namn.value.trim(), isin: "", antal: tal(f.antal.value), kurs: tal(f.kurs.value), avgift: tal(f.avgift.value) || 0, belopp: null, valuta: "SEK", konto: "", kalla: "Manuell", bank: f.bank.value};
    if (t.typ === "utdelning"){ t.belopp = tal(f.belopp.value); if (!t.belopp) return alert("Ange beloppet för utdelningen."); }
    else { if (!t.antal || !t.kurs) return alert("Ange antal och kurs."); t.belopp = t.typ === "köp" ? -(t.antal * t.kurs + t.avgift) : t.antal * t.kurs - t.avgift; }
    t.id = hashStr([t.datum, t.typ, t.namn, t.antal, t.kurs, t.belopp, Date.now()].join("|"));
    pfAndra(d => { d.transaktioner.push(t); }); };
  const fil = $("#pf-fil"); if (fil) fil.onchange = async () => {
    const box = $("#pf-forhand"); const f = fil.files[0]; if (!f) return;
    box.innerHTML = `<p class="lek-m">Läser ${esc(f.name)}…</p>`;
    try {
      const rader = await lasFil(f); const ri = hittaRubrikrad(rader); const rubriker = rader[ri].map(x => String(x).trim());
      PF.forhand = {filnamn: f.name, rubriker, data: rader.slice(ri + 1), karta: gissaKarta(rubriker), kalla: gissaKalla(f.name, rubriker)};
      pfRitaForhand();
    } catch(e){ box.innerHTML = `<p class="lek-m">Kunde inte läsa filen: ${esc(e.message || e)}</p>`; }
  };
}
// Filtyp: transaktioner (Avanza m.fl.), innehavslista (t.ex. Handelsbankens depå) eller kontoutdrag (bara pengar)
function filtyp(rubriker){
  const h = rubriker.map(x => String(x).trim().toLowerCase());
  const har = re => h.some(x => re.test(x));
  if (har(/^antal|kvantitet|innehav$/) && !har(/innehavsförändring|affärsdag|transaktion/) && har(/anskaffn|gav|inköpskurs|inköpsvärde|marknadsvärde|genomsnitt/) && !har(/^(typ|transaktionstyp|typ av transaktion)/)) return "innehav";
  if (!har(/^antal|kvantitet|innehavsförändring/) && har(/^text$|beskrivning|meddelande/) && har(/saldo/)) return "konto";
  return "transaktioner";
}
const INNEHAV_FALT = [
  ["namn", "Värdepapper", /(värdepapper|instrument|^namn|^aktie|benämning|security)/],
  ["isin", "ISIN", /isin/],
  ["antal", "Antal", /^(antal|kvantitet|innehav$)/],
  ["gav", "Snittpris (GAV)", /(gav|genomsnittlig|inköpskurs|anskaffningskurs|snittkurs)/],
  ["anskaffning", "Anskaffningsvärde", /(anskaffningsvärde|inköpsvärde|anskaffat)/],
  ["kurs", "Senaste kurs", /^(senast|kurs|marknadskurs)/],
  ["varde", "Marknadsvärde", /(marknadsvärde|värde)/],
  ["kursdatum", "Kursdatum", /kursdatum/],
  ["konto", "Konto/depå", /^(konto|depå|account)/]
];
function innehavRader(F){
  const k = F.karta, ut = [], idag = new Date().toISOString().slice(0, 10);
  for (const r of F.data){
    const g = f => k[f] != null ? r[k[f]] : null;
    const namn = String(g("namn") || "").trim(), antal = tal(g("antal"));
    if (!namn || !antal || /^(summa|totalt|total)\s*:?\s*$/i.test(namn)) continue;
    let ansk = tal(g("anskaffning")); const gav = tal(g("gav"));
    if (ansk == null && gav != null) ansk = gav * antal;
    const t = {datum: idag, typ: "köp", namn, isin: String(g("isin") || "").trim().toUpperCase(), antal: Math.abs(antal), kurs: gav ?? (ansk != null ? ansk / Math.abs(antal) : null), belopp: ansk != null ? -Math.abs(ansk) : null, avgift: 0, valuta: "SEK", konto: String(g("konto") || "").trim().replace(/\d(?=\d{4})/g, "•"), kalla: F.kalla, ogonblicksbild: true};
    const varde = tal(g("varde")), kurs = tal(g("kurs"));
    // Kurs i kronor: marknadsvärde/antal ger bankens egen omräkning för utländska aktier
    if (varde != null && antal) t.senaste_kurs = varde / Math.abs(antal); else if (kurs != null) t.senaste_kurs = kurs;
    t.kursdatum = datumNorm(g("kursdatum")) || idag;
    t.id = hashStr(["innehav", t.namn, t.isin, t.antal, t.belopp, t.kalla].join("|"));
    ut.push(t);
  }
  return ut;
}
function pfRitaInnehav(F, box){
  const rader = innehavRader(F); const tidigare = (PF.data.transaktioner||[]).filter(t => t.kalla === F.kalla).length;
  const harHistorik = (PF.data.transaktioner||[]).some(t => t.kalla === F.kalla && !t.ogonblicksbild);
  if (F.baraKurser == null) F.baraKurser = harHistorik;
  if (F.baraKurser){
    const r = beraknaPortfolj(PF.data, F.kalla); const avvik = [];
    rader.forEach(t => { const h = r.aktiva.find(x => x.isin === t.isin); const a = h ? h.antal : 0; if (Math.abs(a - t.antal) > 1e-6) avvik.push(`${t.namn}: listan ${fmt(t.antal,0)} st, transaktionerna ${fmt(a,0)} st`); });
    box.innerHTML = `<p class="lek-m" style="margin:10px 0 6px"><b>${esc(F.filnamn)}</b> är en innehavslista från ${esc(F.kalla)}. Du har redan läst in transaktionerna därifrån, så listan används för att sätta <b>bankens egna kurser</b> (${rader.filter(t => t.senaste_kurs != null).length} st). Transaktionerna rörs inte.</p>
      ${avvik.length ? `<div class="callout flag"><p style="margin:0"><b>Antalet skiljer sig</b> för: ${avvik.map(esc).join("; ")}. Kanske saknas äldre transaktioner i filen.</p></div>` : `<p class="lek-m">Antalet stämmer för alla innehav. ✓</p>`}
      <p><button type="button" class="knapp" id="pf-importera">Uppdatera kurserna</button> <button type="button" class="lank-knapp" id="pf-som-innehav">Ersätt transaktionerna med listan i stället</button> <button type="button" class="lank-knapp" id="pf-avbryt">Avbryt</button> <span class="lek-m pf-status"></span></p>`;
    $("#pf-avbryt").onclick = () => { PF.forhand = null; vyPortfolj(); };
    $("#pf-som-innehav").onclick = () => { F.baraKurser = false; pfRitaForhand(); };
    $("#pf-importera").onclick = async () => { const st = box.querySelector(".pf-status"); st.textContent = "Sparar…";
      await pfAndra(d => { rader.forEach(t => { if (t.senaste_kurs != null && t.isin) d.kurser[t.isin] = {kurs: t.senaste_kurs, datum: t.kursdatum, kalla: F.kalla}; }); }, st, "Sparat.");
      if (st.textContent === "Sparat."){ PF.forhand = null; vyPortfolj(); } };
    return;
  }
  box.innerHTML = `<p class="lek-m" style="margin:10px 0 6px"><b>${esc(F.filnamn)}</b> är en <b>innehavslista</b> (det du äger just nu). Bank: <select id="pf-kalla">${BANKER.map(b => `<option${F.kalla === b ? " selected" : ""}>${b}</option>`).join("")}</select> Kontrollera kolumnerna:</p>
    <div class="pf-karta">${INNEHAV_FALT.map(([f, n]) => `<label>${n}<select data-f="${f}"><option value="">–</option>${F.rubriker.map((h, i) => `<option value="${i}"${F.karta[f] === i ? " selected" : ""}>${esc(h || "(kolumn " + (i+1) + ")")}</option>`).join("")}</select></label>`).join("")}</div>
    <p class="lek-m">${rader.length} innehav. Varje innehav sparas med dagens antal och anskaffningsvärde. Vill du uppdatera senare läser du in en ny lista, så ersätts den gamla.${rader.some(t => t.belopp == null) ? " <b>Obs:</b> anskaffningsvärde eller snittpris saknas för vissa innehav, så de får inget inköpspris." : ""}</p>
    ${rader.length ? `<div class="tw2"><table class="matris"><tr><th style="text-align:left">Värdepapper</th><th>Antal</th><th>Snittpris</th><th>Anskaffat</th></tr>${rader.slice(0, 12).map(t => `<tr><td style="text-align:left">${esc(t.namn)}</td><td>${fmt(t.antal, t.antal % 1 ? 2 : 0)}</td><td>${t.kurs != null ? fmt(t.kurs, 2) : "–"}</td><td>${t.belopp != null ? fmt(-t.belopp, 0) : "–"}</td></tr>`).join("")}</table></div>` : ""}
    ${tidigare ? `<p class="lek-m">Ersätter de ${tidigare} rader som tidigare lästs in från ${esc(F.kalla)}.</p>` : ""}
    <p><button type="button" class="knapp" id="pf-importera"${rader.length ? "" : " disabled"}>Spara ${rader.length} innehav</button> <button type="button" class="lank-knapp" id="pf-avbryt">Avbryt</button> <span class="lek-m pf-status"></span></p>`;
  box.querySelectorAll("select[data-f]").forEach(sel => sel.onchange = () => { const f = sel.dataset.f; if (sel.value === "") delete F.karta[f]; else F.karta[f] = Number(sel.value); pfRitaForhand(); });
  $("#pf-kalla").onchange = e => { F.kalla = e.target.value; pfRitaForhand(); };
  $("#pf-avbryt").onclick = () => { PF.forhand = null; vyPortfolj(); };
  $("#pf-importera").onclick = async () => {
    const st = box.querySelector(".pf-status"); st.textContent = "Sparar…";
    await pfAndra(d => { d.transaktioner = d.transaktioner.filter(t => t.kalla !== F.kalla); d.transaktioner.push(...rader); rader.forEach(t => { if (t.senaste_kurs != null && t.isin) d.kurser[t.isin] = {kurs: t.senaste_kurs, datum: t.kursdatum, kalla: F.kalla}; }); d.importer.push({datum: new Date().toISOString().slice(0,10), kalla: F.kalla + " (innehav)", antal: rader.length}); }, st, "Sparat.");
    if (st.textContent === "Sparat."){ PF.forhand = null; vyPortfolj(); }
  };
}
function pfRitaForhand(){
  const F = PF.forhand, box = $("#pf-forhand"); if (!F || !box) return;
  F.typ = F.typ || filtyp(F.rubriker);
  if (F.typ === "konto"){
    box.innerHTML = `<div class="callout flag"><p style="margin:0"><b>Den här filen är ett kontoutdrag</b>, alltså bara pengar in och ut (till exempel "KÖPT 89550661" och ett belopp). Den säger inte vilka aktier eller hur många, så innehaven går inte att räkna fram ur den.</p>
      <p style="margin:8px 0 0"><b>Gör så här i stället hos Handelsbanken:</b> gå till din <b>depå</b> (Spara & placera → Depå eller Mina innehav) och exportera <b>innehavet</b> till Excel. Då får du en lista med värdepapper, antal och anskaffningsvärde, som sidan kan läsa. Finns det en export av <b>depåtransaktioner</b> (köp och sälj med antal) fungerar den också.</p></div>
      <p><button type="button" class="lank-knapp" id="pf-avbryt">Stäng</button></p>`;
    $("#pf-avbryt").onclick = () => { PF.forhand = null; vyPortfolj(); };
    return;
  }
  if (F.typ === "innehav"){ if (!F.innehavKarta){ F.innehavKarta = true; F.karta = {}; const tagna = new Set(); for (const [f, , re] of INNEHAV_FALT){ const i = F.rubriker.findIndex((h, j) => !tagna.has(j) && re.test(String(h).trim().toLowerCase())); if (i >= 0){ F.karta[f] = i; tagna.add(i); } } } return pfRitaInnehav(F, box); }
  const {rader, hoppade} = normalisera(F.data, F.karta, F.kalla);
  const tidigare = (PF.data.transaktioner||[]).filter(t => t.kalla === F.kalla).length;
  if (F.ersatt == null) F.ersatt = tidigare > 0;
  const kanda = new Set((PF.data.transaktioner||[]).filter(t => !(F.ersatt && t.kalla === F.kalla)).map(t => t.id)); const nya = rader.filter(t => !kanda.has(t.id));
  const per = rader.reduce((a, t) => (a[t.typ] = (a[t.typ]||0) + 1, a), {}); if (per["händelse"]) { per["bolagshändelser (split, byte, teckning, flytt)"] = per["händelse"]; delete per["händelse"]; } if (per.likvid) { per["teckningslikvider"] = per.likvid; delete per.likvid; }
  box.innerHTML = `<p class="lek-m" style="margin:10px 0 6px"><b>${esc(F.filnamn)}</b>. Bank: <select id="pf-kalla">${BANKER.map(b => `<option${F.kalla === b ? " selected" : ""}>${b}</option>`).join("")}</select> Kontrollera att kolumnerna stämmer:</p>
    <div class="pf-karta">${PF_FALT.map(([k, n]) => `<label>${n}<select data-f="${k}"><option value="">–</option>${F.rubriker.map((h, i) => `<option value="${i}"${F.karta[k] === i ? " selected" : ""}>${esc(h || "(kolumn " + (i+1) + ")")}</option>`).join("")}</select></label>`).join("")}</div>
    <p class="lek-m">${rader.length} rader känns igen (${Object.entries(per).map(([k, n]) => `${n} ${k}`).join(", ") || "inga"}), varav <b>${nya.length} nya</b>. ${Object.keys(hoppade).length ? `Hoppar över: ${Object.entries(hoppade).slice(0, 6).map(([k, n]) => `${esc(k)} (${n})`).join(", ")}.` : ""}</p>
    ${rader.length ? `<div class="tw2"><table class="matris"><tr><th style="text-align:left">Datum</th><th style="text-align:left">Typ</th><th style="text-align:left">Värdepapper</th><th>Antal</th><th>Kurs</th><th>Belopp</th></tr>${rader.slice(0, 6).map(t => `<tr><td style="text-align:left">${esc(t.datum)}</td><td style="text-align:left">${esc(t.typ)}</td><td style="text-align:left">${esc(t.namn)}</td><td>${fmt(t.antal ?? 0, (t.antal||0) % 1 ? 2 : 0)}</td><td>${t.kurs != null ? fmt(t.kurs, 2) : "–"}</td><td>${t.belopp != null ? fmt(t.belopp, 0) : "–"}</td></tr>`).join("")}</table></div>` : ""}
    ${tidigare ? `<label class="lek-m" style="display:flex;gap:6px;align-items:center;margin:8px 0"><input type="checkbox" id="pf-ersatt"${F.ersatt ? " checked" : ""}> Ersätt de ${tidigare} transaktioner som tidigare lästs in från ${esc(F.kalla)} (rekommenderas när filen täcker hela perioden)</label>` : ""}
    <p><button type="button" class="knapp" id="pf-importera"${nya.length ? "" : " disabled"}>Spara ${nya.length} nya transaktioner</button> <button type="button" class="lank-knapp" id="pf-avbryt">Avbryt</button> <span class="lek-m pf-status"></span></p>`;
  box.querySelectorAll("select[data-f]").forEach(s => s.onchange = () => { const k = s.dataset.f; if (s.value === "") delete F.karta[k]; else F.karta[k] = Number(s.value); pfRitaForhand(); });
  const kl = $("#pf-kalla"); if (kl) kl.onchange = () => { F.kalla = kl.value; F.ersatt = null; pfRitaForhand(); };
  const ers = $("#pf-ersatt"); if (ers) ers.onchange = () => { F.ersatt = ers.checked; pfRitaForhand(); };
  $("#pf-avbryt").onclick = () => { PF.forhand = null; vyPortfolj(); };
  $("#pf-importera").onclick = async () => {
    const st = box.querySelector(".pf-status"); st.textContent = "Sparar…";
    await pfAndra(d => { if (F.ersatt) d.transaktioner = d.transaktioner.filter(t => t.kalla !== F.kalla); d.transaktioner.push(...nya); d.importer.push({datum: new Date().toISOString().slice(0,10), kalla: F.kalla, antal: nya.length}); }, st, "Sparat.");
    if (st.textContent === "Sparat."){ PF.forhand = null; vyPortfolj(); }
  };
}
// --- vilka bevakade bolag är mina? (räknas bara i webbläsaren, sparas aldrig i sidan) ---
function minaBolag(){
  if (!PF.data) return null;
  const r = beraknaPortfolj(PF.data); const agda = new Map(), salda = new Map();
  r.aktiva.forEach(h => { if (h.bolag) agda.set(h.bolag.slug, h); });
  r.saltBevakas.forEach(h => { if (h.bolag && !agda.has(h.bolag.slug)) salda.set(h.bolag.slug, h); });
  return {agda, salda};
}
let URVAL = (() => { try { return localStorage.getItem("ih-urval") || "alla"; } catch(e){ return "alla"; } })();
function filtreraBolag(lista){
  const m = minaBolag(); if (!m || URVAL === "alla") return lista;
  if (URVAL === "mina") return lista.filter(b => m.agda.has(b.slug) || m.salda.has(b.slug));
  if (URVAL === "ovriga") return lista.filter(b => !m.agda.has(b.slug) && !m.salda.has(b.slug));
  return lista;
}
function urvalHtml(){
  const m = minaBolag(); if (!m) return "";
  const n = m.agda.size + m.salda.size;
  return `<div class="filters urval" role="tablist" aria-label="Välj bolag">${[["alla","Alla bolag"],["mina",`Mina innehav (${n})`],["ovriga","Bevakade jag inte äger"]].map(([k, t]) => `<button type="button" data-urval="${k}" class="${URVAL === k ? "on" : ""}">${t}</button>`).join("")}</div><p class="hint" style="margin:6px 0 14px">Filtret syns bara för dig och räknas fram ur din privata portfölj.</p>`;
}
document.addEventListener("click", e => { const b = e.target.closest("[data-urval]"); if (!b) return; URVAL = b.dataset.urval; try { localStorage.setItem("ih-urval", URVAL); } catch(err){} route(); });
function mittInnehavHtml(slug){
  const m = minaBolag(); if (!m) return "";
  const h = m.agda.get(slug), s = m.salda.get(slug); if (!h && !s) return "";
  if (h) return `<div class="mitt-innehav"><div class="label">Ditt innehav (syns bara för dig)</div><div class="pf-tal"><div><span class="label">Antal</span><b class="num">${fmt(h.antal, h.antal % 1 ? 2 : 0)}</b></div><div><span class="label">Snittpris</span><b class="num">${kr(h.gav, 2)}</b></div><div><span class="label">Värde</span><b class="num">${kr(h.varde)}</b></div><div><span class="label">Upp/ner</span><b class="num">${plus(h.orealiserat)} ${h.orealiseratPct != null ? `(${plus(h.orealiseratPct, 0, " %")})` : ""}</b></div><div><span class="label">Andel</span><b class="num">${fmt(h.andel, 0)} %</b></div></div>${platsHtml(h)}<ul class="pf-koll">${strategiKoll(h).filter(x => x[0] !== "gra").map(([f, t]) => `<li class="k-${f}">${esc(t)}</li>`).join("")}</ul><a href="#portfolj" class="lek-m">Till Min portfölj →</a></div>`;
  return `<div class="mitt-innehav"><div class="label">Du sålde allt ${esc(s.saltDatum)} (syns bara för dig)</div><p style="margin:4px 0 0">Resultat ${plus(s.realiserat)}${s.vardeOmKvar != null ? ` · värt i dag om du behållit: ${kr(s.vardeOmKvar)} (${plus(s.vardeOmKvar - s.saltBelopp)} mot vad du fick)` : ""}.</p></div>`;
}
function portfoljForClaude(){
  if (!PF.data) throw new Error("Portföljen är inte laddad, eller så är användaren inte inloggad.");
  const r = beraknaPortfolj(PF.data); const pl = platser(PF.data);
  return {totalt_kr: r.tot, innehav: r.aktiva.map(h => ({namn: h.namn, antal: h.antal, gav_kr: h.gav && +h.gav.toFixed(2), kurs_kr: h.kurs, investerat_kr: Math.round(h.kostnad), varde_kr: h.varde && Math.round(h.varde), upp_ner_pct: h.orealiseratPct && Math.round(h.orealiseratPct), andel_pct: Math.round(h.andel), finns_hos: Object.fromEntries(Object.entries(pl[h.isin || h.nyckel] || {}).filter(([, a]) => a > 1e-6)), foljs_i_verktyget: h.bolag ? h.bolag.status.namn : null, spar: h.bolag ? h.bolag.status.spar || null : null, lynch: h.bolag ? h.bolag.status.lynch || null : null, strategikoll: strategiKoll(h).map(x => x[1]), anteckning: (PF.data.anteckningar||{})[h.nyckel] || null})),
    salda: r.stangda.map(h => ({namn: h.namn, realiserat_kr: Math.round(h.realiserat), utdelning_kr: Math.round(h.utdelning)}))};
}
pfStart();
