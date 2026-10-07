# -*- coding: utf-8 -*-
# design_prompt.html のテンプレ本文を機械的に抽出し、新UI（カードブック）に移植する
import re, json

import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'design_prompt.html')
DST = os.path.join(HERE, '..', 'index.html')
src = open(SRC, encoding='utf-8').read()

def between(a, b, text=src):
    i = text.index(a); j = text.index(b, i)
    return text[i:j]

def fn_src(name):
    i = src.index(f"  function {name}(")
    j = re.search(r"\n  function \w+\(|\n  const RC_WORDS|\n  let rcCat", src[i+10:]).start() + i + 10
    return src[i:j]

# ---------- 共通定数（PRINT〜askBlock）をそのまま ----------
consts = between("  const PRINT =", "  function tmplBrief(")
# ---------- RC_WORDS ----------
rc = between("  const RC_WORDS={", "  let rcCat=")

def body_from(name, marker):
    s = fn_src(name)
    k = s.index(marker)
    return s[k:].rstrip()

def strip_close(s):
    # 末尾の "  }" を落とす
    s = s.rstrip()
    assert s.endswith('}'), name
    return s[:-1].rstrip()

T = {}
T['brief']  = "const sl=sizeLine(st), step=st.step;\n" + strip_close(body_from('tmplBrief', "    if(step==='1') return `"))
T['svg']    = "const sl=sizeLine(st), step=st.step;\n" + strip_close(body_from('tmplSvg', "    if(step==='1') return `"))
T['ocrsvg'] = ("const sl=sizeLine(st), step=st.step; const font=st.font, dir=st.dir, al=st.align;\n"
               + strip_close(body_from('tmplOcrSvg', "    const fontLine = ")))
T['denpyo'] = ("const sl=sizeLine(st), step=st.step; const lw=st.lw, ami=st.ami, rc=st.rc;\n"
               + strip_close(body_from('tmplDenpyo', "    const lwLine = ")))
T['meishi'] = ("const ori=st.ori, side=st.side, bleed=(st.bleed!=='off'), step=st.step;\n"
               + strip_close(body_from('tmplMeishi', "    const fin = ")))
T['chart']  = ("if(st.src==='image') return chartFromImage(st);\n    const type=st.ctype; const label={bar:'縦棒グラフ',barh:'横棒グラフ',line:'折れ線グラフ',pie:'円グラフ',table:'表'}[type];\n"
               "    const data=(st.data||'').trim(); const emph=(st.emph||'').trim();\n"
               + strip_close(body_from('tmplChart', "    return `")))
T['parts']  = strip_close(body_from('tmplParts', "    return `"))
T['psup']   = strip_close(body_from('tmplPsUp', "    return `"))
T['ocr']    = strip_close(body_from('tmplOcr', "    return `"))
T['psfill'] = ("const t=PS_TARGETS[st.target]||PS_TARGETS[0]; const m=PS_MATS[st.mat]||PS_MATS[0];\n"
               "    const tja=t.ja, ten=t.en; let mja=m.ja, men=m.en;\n"
               "    const cja=(st.matJa||'').trim(), cen=(st.matEn||'').trim(); if(cja) mja=cja; if(cen) men=cen;\n"
               "    const colja=(st.colJa||'').trim(), colen=(st.colEn||'').trim(); if(colja) mja=colja+mja; if(colen) men=colen+' '+men;\n"
               + strip_close(body_from('tmplPsFill', "    return `")))
T['recolor']= ("const kw=(st.kw||'').trim();\n"
               + strip_close(body_from('tmplRecolor', "    return `")).replace(
                 "■ 上のカテゴリから候補をクリックしてコピーするか、自由に情景・雰囲気を入力してください。",
                 "${kw ? `■ 今回のキーワード\\n  「${kw}」\\n\\n` : ''}■ カードの候補をクリックするか、自由に情景・雰囲気を入力してください。"))
T['proof']  = ("const pm=st.pmode; const staged=pm==='staged'; const selected=st.stages||[]; const book=selected.includes('book');\n"
               + strip_close(body_from('tmplProof', "    const ALL = [")))

# proof 内の「差異だけ見たいときは〜」等はそのまま。
tmpl_js = "\n".join(f"  T.{k} = function(st){{\n    {v}\n  }};" for k,v in T.items())

html = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PROMPT BOOK</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f5f5f3; --card:#ffffff; --ink:#1a1a1a; --sub:#6b6b6b; --line:#e3e3df; --line2:#cfcfc9;
  --acc:#1a1a1a; --accText:#ffffff;
  --gen:#2f6fed; --chk:#1f9d55; --app:#e07a1f; --once:#7a7a7a;
  --radius:14px; --shadow:0 1px 2px rgba(0,0,0,.04),0 8px 24px rgba(0,0,0,.06);
  --shadowHover:0 2px 4px rgba(0,0,0,.06),0 16px 40px rgba(0,0,0,.12);
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Sans JP","Hiragino Sans","Yu Gothic",Meiryo,sans-serif;font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit}
button{font-family:inherit}

header{padding:40px 24px 4px;max-width:1180px;margin:0 auto}
header h1{margin:0;font-family:"Bebas Neue","DIN Condensed","Oswald",Impact,sans-serif;font-size:44px;font-weight:400;letter-spacing:.06em;line-height:1}
header p{margin:6px 0 0;color:var(--sub);font-size:14px}

main{max-width:1180px;margin:0 auto;padding:12px 24px 80px}
.group{margin-top:28px}
.group h2{margin:0 0 12px;font-size:13px;font-weight:700;letter-spacing:.12em;color:var(--sub)}
.group .desc{margin:0 0 14px;font-size:13px;color:var(--sub)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}

.card{position:relative;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 18px 16px 18px;cursor:pointer;display:flex;flex-direction:column;
  box-shadow:var(--shadow);transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease;text-align:left;width:100%;display:block}
.card:hover,.card:focus-visible{transform:translateY(-2px);box-shadow:var(--shadowHover);border-color:var(--line2);outline:none}
.grid{align-items:stretch}
.card:active{transform:translateY(0)}
.card::before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:4px;border-radius:0 4px 4px 0;background:var(--appColor,#999)}
.card .top{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.num{font-family:"DIN Alternate","D-DIN","DIN","Barlow","Roboto Condensed",sans-serif;font-variant-numeric:tabular-nums;line-height:1;padding-top:1px}
.card .num{width:30px;height:30px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex:none}
.card .name{font-size:16px;font-weight:700;line-height:1.35}
.card .arrow{margin-left:auto;color:var(--sub);flex:none;transition:transform .15s}
.card:hover .arrow{transform:translateX(3px);color:var(--ink)}
.card .purpose{color:var(--sub);font-size:13.5px;margin:0 0 12px;flex:1}
.card .meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
/* app badges */
:root{--claude:#D97757; --gpt:#111111; --ai:#FF9A00; --ps:#31A8FF}
.apps{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:12px}
.app{font-size:11.5px;font-weight:700;letter-spacing:.02em;padding:4px 10px;border-radius:999px;color:#fff;line-height:1.2}
.app.claude{background:var(--claude)} .app.gpt{background:var(--gpt)} .app.ps{background:var(--ps)} .app.ai{background:var(--ai);color:#2b1a00}
.app.sub{opacity:.55}
.drawer .dhead .app{background:color-mix(in srgb,var(--flowColor,#999) 12%,#fff);color:var(--flowColor,#666)}
.drawer .dhead .app.sub{opacity:1;background:#f0f0ee;color:#777}
.drawer[data-app="ai"] .dhead .app{color:#9a5b00}
.drawer[data-app="gpt"] .dhead .app{color:#333;background:#eeeeeb}

/* scene (symbolic motion) */
.scene{margin-top:12px;background:#fafaf8;border:1px solid var(--line);border-radius:10px;height:84px;display:flex;align-items:center;justify-content:center;gap:8px;padding:0 10px;overflow:hidden}
.sc{display:flex;flex-direction:column;align-items:center;gap:3px;opacity:0;will-change:opacity,transform}
.sc svg{width:40px;height:40px;display:block;overflow:visible}
.sc .lb{font-size:10px;color:var(--sub);line-height:1;white-space:nowrap;font-weight:500}
.sc.plus svg{width:26px;height:26px}
.ar{opacity:0;flex:none}
.ar svg{width:16px;height:16px;display:block;color:#b5b5b0}
.scene .grp{display:flex;align-items:center;gap:4px}
.scene.dense{gap:5px;padding:0 8px}
.scene.rows{flex-wrap:wrap;height:auto;min-height:84px;padding:10px 10px;row-gap:10px}
.scene .br{flex-basis:100%;height:0}
.scene.dense .sc svg{width:32px;height:32px}
.scene.dense .sc.plus svg{width:22px;height:22px}
.scene.dense .ar svg{width:13px;height:13px}
.scene.dense .lb{font-size:9.5px}
@media (prefers-reduced-motion: reduce){ .sc,.ar{opacity:1!important;animation:none!important} .sc *{animation:none!important} }


/* drawer */
.backdrop{position:fixed;inset:0;background:rgba(20,20,20,.35);opacity:0;pointer-events:none;transition:opacity .2s;z-index:40}
.backdrop.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100%;width:min(600px,100%);background:var(--card);z-index:50;transform:translateX(102%);transition:transform .22s cubic-bezier(.2,.8,.2,1);display:flex;flex-direction:column;box-shadow:-8px 0 40px rgba(0,0,0,.15)}
.drawer.on{transform:translateX(0)}
.dhead{padding:20px 22px 12px;border-bottom:1px solid var(--line);display:flex;gap:12px;align-items:flex-start}
.dhead .num{width:34px;height:34px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;flex:none;margin-top:2px}
.dhead h3{margin:0;font-size:18px;font-weight:700;line-height:1.35}
.dhead p{margin:4px 0 0;color:var(--sub);font-size:13.5px}
.close{margin-left:auto;background:none;border:1px solid var(--line);border-radius:8px;padding:6px 10px;cursor:pointer;color:var(--sub);font-size:13px;flex:none}
.close:hover{border-color:var(--ink);color:var(--ink)}
.dbody{flex:1;overflow:auto;padding:16px 22px 24px}
.sec{margin-bottom:22px}
.sec h4{margin:0 0 8px;font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--sub)}
.paste li{margin:4px 0}
.io{display:flex;flex-direction:column;gap:8px;font-size:14px}
.io .row{display:flex;gap:10px;align-items:flex-start}
.io .k{flex:none;width:72px;font-size:11.5px;font-weight:700;color:var(--flowColor,#666);background:color-mix(in srgb,var(--flowColor,#999) 12%,#fff);border-radius:6px;padding:3px 0;text-align:center;margin-top:1px}
.drawer[data-app="ai"] .io .k{color:#9a5b00}
.drawer[data-app="gpt"] .io .k{color:#333;background:#eeeeeb}
.paste{margin:0;padding-left:18px;font-size:14px}
.flowlist{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px}
.flowlist li{display:flex;gap:10px;align-items:flex-start;font-size:14px}
.flowlist .n{width:22px;height:22px;border-radius:50%;background:color-mix(in srgb,var(--flowColor,#999) 12%,#fff);color:var(--flowColor,#666);font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex:none;margin-top:2px;font-family:"DIN Alternate","D-DIN","DIN","Barlow","Roboto Condensed",sans-serif;line-height:1;padding-top:1px}
.drawer[data-app="ai"] .flowlist .n{color:#9a5b00}
.drawer[data-app="gpt"] .flowlist .n{color:#333;background:#eeeeeb}
.flowlist .you{color:var(--sub);font-size:12.5px}

.opt{margin-bottom:16px}
.opt label.l{display:block;font-size:13px;font-weight:500;margin-bottom:6px}
.opt .hint{font-size:12px;color:var(--sub);margin-top:4px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line2);background:#fff;border-radius:999px;padding:7px 13px;font-size:13px;cursor:pointer;color:var(--ink);transition:all .12s;line-height:1.3;box-shadow:0 1px 2px rgba(0,0,0,.08),0 1px 0 rgba(0,0,0,.04)}
.chip:hover{border-color:var(--ink);transform:translateY(-1px);box-shadow:0 2px 6px rgba(0,0,0,.12)}
.chip:active{transform:translateY(0);box-shadow:0 1px 1px rgba(0,0,0,.08)}
.chip.on{background:var(--ink);border-color:var(--ink);color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.15),0 1px 2px rgba(0,0,0,.15)}
/* ドロワー内は貼り先アプリの色 */
.drawer .chip.on{background:var(--flowColor);border-color:var(--flowColor);color:#fff}
.slider{display:grid;grid-template-columns:1fr 150px;align-items:center;gap:6px 14px}
.slider input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:6px;border-radius:999px;background:linear-gradient(to right,var(--flowColor,#111) var(--p,50%),var(--line2,#ddd) var(--p,50%));outline:none;margin:0}
.slider input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:22px;height:22px;border-radius:50%;background:#fff;border:2px solid var(--flowColor,#111);box-shadow:0 1px 3px rgba(0,0,0,.25);cursor:grab}
.slider input[type=range]::-moz-range-thumb{width:20px;height:20px;border-radius:50%;background:#fff;border:2px solid var(--flowColor,#111);box-shadow:0 1px 3px rgba(0,0,0,.25);cursor:grab}
.slider .sv{display:flex;align-items:center;gap:8px;color:var(--ink,#111);font-size:13px}
.slider .sv svg{width:72px;height:24px;flex:none}
.slider .ends{grid-column:1;display:flex;justify-content:space-between;font-size:11px;color:#888}
.drawer .chip:hover{border-color:var(--flowColor);background:color-mix(in srgb,var(--flowColor) 8%,#fff)}
.drawer .chip.on:hover{background:var(--flowColor);filter:brightness(.95)}
.drawer[data-app="ai"] .chip.on{color:#2b1a00}
.drawer .opt input:focus,.drawer .opt textarea:focus{outline-color:var(--flowColor);border-color:var(--flowColor)}
.drawer .sizerow .apply{border-color:var(--flowColor);color:var(--flowColor)}
.drawer .sizerow .apply:hover{background:var(--flowColor);color:#fff}
.drawer[data-app="ai"] .sizerow .apply:hover{color:#2b1a00}
.drawer .btn.primary{background:var(--flowColor)}
.drawer .btn.primary:hover{filter:brightness(.92);background:var(--flowColor)}
.drawer[data-app="ai"] .btn.primary{color:#2b1a00}
.drawer .btn.primary.done{background:var(--chk);color:#fff}
.drawer .warn .box{border-color:var(--flowColor)}
.chip.multi.on::before{content:"✓ "}
.opt input[type=text],.opt input[type=number],.opt textarea{width:100%;border:1px solid var(--line2);border-radius:10px;padding:9px 11px;font:inherit;font-size:13.5px;background:#fff;color:var(--ink)}
.opt textarea{min-height:110px;resize:vertical;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}
.opt input:focus,.opt textarea:focus{outline:2px solid var(--ink);outline-offset:1px;border-color:var(--ink)}
.row2{display:flex;gap:8px;flex-wrap:wrap}
.row2>*{flex:1;min-width:140px}
.sizerow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-top:8px}
.sizerow input{width:80px!important}
.sizerow select{border:1px solid var(--line2);border-radius:10px;padding:8px;font:inherit;background:#fff}
.sizerow .apply{border:1px solid var(--ink);background:#fff;border-radius:10px;padding:8px 12px;cursor:pointer;font-size:13px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.sizerow .apply:hover{background:var(--ink);color:#fff}
.echo{font-size:13px;color:var(--sub);margin-top:6px}
.echo b{color:var(--ink)}

.out{margin-top:6px}
.out textarea{width:100%;min-height:200px;max-height:38vh;border:1px solid var(--line);border-radius:10px;padding:12px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;line-height:1.55;background:#fafaf8;color:#333;resize:vertical}
.dfoot{padding:14px 22px calc(14px + env(safe-area-inset-bottom));border-top:1px solid var(--line);background:#fff;display:flex;gap:10px}
.btn{border:none;border-radius:12px;padding:14px 18px;font-size:15px;font-weight:700;cursor:pointer;transition:transform .08s,background .12s,box-shadow .12s;box-shadow:0 2px 6px rgba(0,0,0,.14)}
.btn:hover{box-shadow:0 4px 12px rgba(0,0,0,.18)}
.btn:active{transform:scale(.99)}
.btn.primary{flex:1;background:var(--ink);color:#fff}
.btn.primary:hover{background:#000}
.btn.primary:disabled{background:#bdbdb8;cursor:not-allowed}
.btn.primary.done{background:var(--chk)}
.btn.ghost{background:#fff;border:1px solid var(--line2);color:var(--ink)}
.btn.ghost:hover{border-color:var(--ink)}

/* 注意アラート（消すまで先に進めない） */
.warn{position:absolute;inset:0;background:rgba(250,250,248,.96);z-index:5;display:flex;align-items:center;justify-content:center;padding:24px}
.warn .box{max-width:340px;width:100%;background:#fff;border:2px solid var(--ink);border-radius:12px;padding:16px 18px 14px;box-shadow:0 16px 40px rgba(0,0,0,.12)}
.warn .wt{display:flex;justify-content:center;margin-bottom:6px}
.warn .wt svg{width:22px;height:22px;color:var(--flowColor)}
.warn .wl{font-size:15.5px;font-weight:700;line-height:1.5;text-align:center;margin:0 0 14px;letter-spacing:.01em}
.warn .wl div+div{margin-top:4px}
.warn .btn{width:100%;padding:11px 14px;font-size:14px}
.drawer{position:fixed}
.toast{position:fixed;left:50%;bottom:28px;transform:translateX(-50%) translateY(20px);background:var(--ink);color:#fff;padding:10px 16px;border-radius:10px;font-size:13.5px;opacity:0;transition:all .2s;z-index:60;pointer-events:none}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}

@media (max-width:640px){
  header{padding:24px 16px 4px} main{padding:8px 16px 60px}
  .grid{grid-template-columns:1fr}
  .dhead,.dbody,.dfoot{padding-left:16px;padding-right:16px}
}
</style>
</head>
<body>
<header>
  <h1>PROMPT BOOK</h1>
</header>
<main id="main"></main>

<div class="backdrop" id="backdrop"></div>
<aside class="drawer" id="drawer" aria-hidden="true">
  <div class="dhead">
    <div class="num" id="dNum"></div>
    <div><h3 id="dName"></h3><p id="dPurpose"></p><div class="apps" id="dApps" style="margin-top:8px"></div></div>
    <button class="close" id="dClose">閉じる</button>
  </div>
  <div class="dbody" id="dBody"></div>
  <div class="warn" id="dWarn" style="display:none"></div>
  <div class="dfoot">
    <button class="btn ghost" id="dClose2">閉じる</button>
    <button class="btn primary" id="dCopy">プロンプトをコピー</button>
  </div>
</aside>
<div class="toast" id="toast">コピーしました</div>

<script>
(function(){
'use strict';
// ======================= 共通定数・テンプレ（design_prompt.html から移植） =======================
__CONSTS__

__RC__

  const PS_TARGETS=[
    {v:'table',label:'テーブル面',ja:'テーブル面',en:'table surface'},
    {v:'floor',label:'床',ja:'床',en:'floor'},
    {v:'bg',label:'背景',ja:'背景',en:'background'},
    {v:'wall',label:'壁',ja:'壁',en:'wall'},
    {v:'all',label:'背景全面',ja:'背景全面（床・壁・奥をまとめて）',en:'entire background including floor, wall and surroundings'}
  ];
  const PS_MATS=[
    {label:'和紙',ja:'白い和紙',en:'textured white washi paper'},
    {label:'木目',ja:'木目（ナチュラル）',en:'natural light wood grain'},
    {label:'大理石',ja:'白い大理石',en:'white marble'},
    {label:'麻布',ja:'麻布（生成り）',en:'natural linen fabric'},
    {label:'畳',ja:'畳',en:'tatami mat'},
    {label:'コンクリート',ja:'コンクリート',en:'polished concrete'},
    {label:'タイル',ja:'タイル',en:'ceramic tile'},
    {label:'無地の紙',ja:'無地の紙（マット）',en:'plain matte paper'},
    {label:'グラデ壁紙（青緑→桃）',ja:'上から青緑・中央は青みがかったグレー・下は淡いピンクベージュへなめらかに変化する縦グラデーション。全体に繊細なノイズ質感。無地・ミニマル・霧のようにやわらかいマット',en:'a smooth vertical gradient from muted teal-blue at top, through soft blue-grey, to pale pink-beige at the bottom, with subtle fine grain, plain minimal foggy matte finish'},
    {label:'無地グラデ',ja:'無地のなめらかなグラデーション。全体に繊細なノイズ質感。ミニマルでやわらかいマット',en:'a smooth plain gradient with subtle fine grain, minimal soft matte finish'}
  ];

  const SIZES=[
    {v:'A4',w:210,h:297,label:'A4'},{v:'A3',w:297,h:420,label:'A3'},{v:'B5',w:182,h:257,label:'B5'},{v:'B6',w:128,h:182,label:'B6'},
    {v:'HAGAKI',w:100,h:148,label:'ハガキ'},{v:'SNS',w:1080,h:1080,label:'SNS正方形',unit:'px',fixed:true}
  ];
  function sizeLine(st){
    const s = st.size;
    if(!s) return '〈サイズ未選択：判型・向き・綴じを選ぶ〉';
    let w=+s.w,h=+s.h;
    if(!s.fixed){
      if(st.orient==='landscape'){[w,h]=[Math.max(w,h),Math.min(w,h)];}
      else{[w,h]=[Math.min(w,h),Math.max(w,h)];}
      if(st.binding==='spread') w=w*2;
    }
    const ori=s.fixed?'':(st.orient==='landscape'?'横':'縦');
    const bind=s.fixed?'':(st.binding==='spread'?'・見開き':'');
    return `${s.label}${ori}${bind} ${w}×${h}${s.unit||'mm'}`;
  }

  const T={};
__TMPL__

  function chartFromImage(st){
    const type=st.ctype; const label={bar:'縦棒グラフ',barh:'横棒グラフ',line:'折れ線グラフ',pie:'円グラフ',table:'表'}[type];
    const emph=(st.emph||'').trim();
    return `添付したグラフ・表のスクリーンショットから、データを書き起こし、そのうえで印刷向けルールの${label}SVGに作り直してください。
作業は「転記」と「作図」の2つです。転記で止まり、確認後に作図します。

${askBlock([
  'グラフ・表の画像が添付されているか',
  'ラベル・数値・凡例・単位が読み取れる解像度か（潰れていれば再送を求める）',
  '複数のグラフが写っている場合、どれを対象にするか'
])}

■ 転記の規則（厳守）
  ・画像に印字されている文字・数値をそのまま書く。桁区切り・小数点・単位・全角半角・約物を変えない。丸めない。
  ・値ラベルが印字されていない棒・点・扇は、目盛りから読んだ推定値を書き、必ず「推定」と印を付ける。推定値は確定値と同じ欄に混ぜない。
  ・凡例・軸ラベル・単位・注記・出典も転記する。
  ・読めない文字は「■」で置き、推測しない。
  ・グラフの種類が指定（${label}）と違って見えても、転記は画像のまま行う（作図の段階で${label}に変換する）。

■ この手順の出力（転記だけ。SVGは書かない）
  1. データ表：行番号付きで「ラベル ／ 値（字種メモ）／ 確定・推定」の3列。系列が複数なら系列名も。
  2. 凡例・軸・単位・注記・出典の転記
  3. 判読不能箇所
  4. 【アラート：推定値あり】推定した値を全部列挙する（無ければ「推定値：0件」と明記）
  5. 【アラート：解像度不足】判読できなかった領域（無ければ「0箇所」）

${STOP_BLOCK}

■ 確定データ
  ・確定データ＝直前のデータ表に、受け取った修正指示を反映したもの。作業の最初に行番号付きで再掲する（修正した行には「修正」と付ける）。
  ・画像から数値を読み直さない。確定データだけを使う。
  ・推定と印の付いた値は、SVG内のラベルに「（推定）」を付けるか、指示があれば省く。

■ 作図方針
  ・${label}として作図する。数値は確定データのまま表示（丸めない・書式を変えない）。
  ・軸・目盛り・凡例・単位は確定データの転記から付ける（無いものは付けない）。
  ・数値ラベルは背後にマスク（白背景）を敷かない。重なるなら位置で回避
  ・${type==='pie'?'各扇の割合を正確に。中心角=値/合計×360':'棒の高さ/点の位置は値に比例。座標をPythonで計算して正確に'}
  ・配色はシンプルに。元画像の配色は参考にしてよいが、有彩色は指定があればそれ、なければ抑えたトーン${emph?`\n  ・強調（赤字）：${emph}`:''}

${PRINT}

■ この手順の出力（この順序で、省略なし）
  1. SVGコード全文（.svgファイル）＋プレビュー。データ由来の<text>には data-line="行番号"、生成した目盛り等には data-line="gen"
  2. 照合表（data-line順にSVGの<text>と確定データを並べる。不一致があれば冒頭に「不一致あり」）
  3. 【アラート：データに照合値なし】data-line="gen" の<text>を全部列挙（無ければ「0件」）
  4. 【アラート：推定値の使用】推定値を使った箇所（無ければ「0件」）

確定データにない文字・数値を1つでも足したり変えたりしたら失敗です。`;
  }

  const MEISHI_TRACE_ROLE =
`■ 役割（トレース）
  ・原稿＝配置・文字の大きさ・字間・色・書体の雰囲気まで、原稿そのものを再現する対象。参考デザインは使わない
  ・確定テキスト＝載せる文字のすべて。これ以外の項目を足さない

■ トレースの規則
  ・原稿画像の実寸比から、各行の位置（x・ベースライン）・文字サイズ・字間（letter-spacing）を実測して置く。デザイン上の判断で整えない・揃え直さない
  ・色は原稿の見た目に近い色で塗る（黒い文字は #000000）。行の中で色や書体が変わる箇所は <tspan> で分ける（1行1<text>は守る）
  ・書体は原稿に近い系統を選ぶ（明朝／ゴシック／丸ゴシック／セリフ体等）。Helvetica/Arial固定にしない。最後に使った書体の一覧を出す
  ・罫線・区切り線は原稿にある物だけ、位置・太さ・色を合わせて置く
  ・ロゴ・写真・印影は描き起こさず、実寸の配置枠（点線の矩形）を置く
  ・手書きの書き込み（丸囲み・チェック等）は印刷物ではないので入れない。入れなかった物は末尾に列挙する
  ・文字の大きさ・行の優先順位は原稿どおり。6pt目安などのデザイン上の注意は適用しない`;
  const _meishi = T.meishi;
  T.meishi = function(st){
    let t = _meishi(st);
    if(st.layout!=='trace') return t;
    t = t.replace(/  ・参考デザインも一緒に添付されている場合、どれが原稿か判別できるか（判別できなければ聞く）\n/, '');
    t = t.replace(/  ・参考デザイン画像が添付されているか\n/, '');
    t = t.replace(/  ・ロゴ画像がある場合、それを使うか（無ければロゴ枠はプレースホルダでよいか）\n/, '  ・ロゴは配置枠（プレースホルダ）で進める。確認は不要\n');
    t = t.replace(/■ 役割\n  ・参考デザイン＝[^\n]*\n  ・確定テキスト＝[^\n]*/, MEISHI_TRACE_ROLE);
    t = t.replace(/■ 名刺特有の注意\n(  ・[^\n]*\n)+/, '');
    t = t.replace(/  ・フォントはインライン指定（日本語Hiragino系先頭、英字Helvetica\/Arial先頭）/, '  ・フォントはインライン指定（原稿に近い系統を先頭に。Webフォント名は使わない）');
    t = t.replace('レイアウトの意図（どこを主役にしたか）も一言添えてください。', '最後に、使った書体の一覧、入れなかった物（手書き等）、原稿で確認が必要な箇所を列挙してください。');
    t = t.replace('添付した名刺の原稿（記載内容）の文字を書き起こしてください。', '添付した名刺の原稿を、そのままトレースしてSVGにします。まず文字を書き起こしてください。');
    return t;
  };

  T.mockup = function(st){
    const bg = {light:'薄いグレー（#E9E9E6 前後の単色）',white:'白（#FFFFFF）',dark:'濃いグレー（#3A3A3A 前後の単色）'}[st.bg||'light'];
    const lay = {each:'1点ずつ別々の画像にする',all:'全点を1枚の画像に並べる（実寸比を保ったまま、重ならないように配置）',both:'1点ずつの画像と、全点を並べた1枚の両方を作る'}[st.lay||'both'];
    const tex = (st.tex||'on')==='on' ? '紙の質感として、ごく弱いノイズを乗せる（印刷面の情報が読みにくくならない強さ）' : '紙の質感は乗せない（フラット）';
    const pdf = (st.proof||'on')==='on' ? '\n  4. 確認用PDF：A4縦に、モックアップ画像と各ファイル名・仕上がり寸法（mm）を載せた確認用PDFを1本作る' : '';
    return `添付したPDF（数は任意）から、確認用のモックアップ画像を作ってください。コード実行（Python）を使ってください。

${askBlock([
  'PDFが1つ以上添付されているか',
  '各PDFが何か（名刺・封筒・チラシ等）判別できるか（できなければファイル名のまま扱ってよいか聞く）',
  '表裏・複数ページがある場合、どのページを使うか（全ページか、1ページ目だけか）'
])}

■ 手順
  1. 寸法の確認：各PDFの MediaBox・TrimBox・BleedBox をmmで読む（PyMuPDF：pt÷72×25.4）。TrimBox があれば仕上がりはTrimBox、無ければMediaBox。塗り足しは切り落とした状態でモックアップにする。
  2. 画像化：各ページを300dpiでラスタライズし、仕上がり線で切り抜く。
  3. 合成：
     ・背景：${bg}
     ・${tex}
     ・影は2層：大きくぼかした柔らかい影＋近くの薄い影。影は右下にわずかに落とす。影で紙の縁が消えないこと
     ・大きさは実寸比を守る（名刺と封筒を並べたとき、大きさの関係が実物どおりになる）
     ・並べ方：${lay}
     ・画像はPNG、長辺3000px程度${pdf}

■ 守ること
  ・印刷面の中身（文字・色・配置）は一切描き直さない。PDFを画像化したものをそのまま使う
  ・トリミング・回転・傾きは付けない（真上から見た平置き）。立体化・遠近・背景写真の合成はしない
  ・色は画面表示用の近似。色校正の代わりにはならないことを最後に一行添える

■ 出力
  1. 各PDFの寸法一覧（ファイル名／仕上がり W×H mm／塗り足しの有無）
  2. モックアップ画像（プレビューも表示）${pdf? '\n  3. 確認用PDF':''}
  最後に、使ったページと、判断に迷った点を列挙する。`;
  };

  T.hand = function(st){
    const who  = {f:'女性的（やわらかく丸みのある線、字幅はやや小さめ、止め・はねは控えめ）',m:'男性的（直線的で力強い線、字幅は大きめ、止め・はねがはっきり）',n:'中性的（癖の少ない読みやすい字）'}[st.who||'f'];
    const MOOD = {stylish:'スタイリッシュ（シャープな字形、やや右上がり、字間は詰めすぎず整う）',cute:'かわいい（丸みが強く、字形は小さめで少し丸っこい、はねは短い）',elegant:'上品（流れるような運筆、字の大きさが揃い、余白が多い）',casual:'ラフ（勢いのある速書き、傾きや大きさの揺らぎがやや大きい）',genki:'元気（字形を大きくのびのびと、はっきりした止め・はね）',soboku:'素朴（ゆっくり丁寧に書いた、癖の少ないやさしい字）'};
    const moods = (Array.isArray(st.mood)?st.mood:[]).filter(k=>MOOD[k]);
    const mood = moods.length===0 ? '' : moods.length===1 ? MOOD[moods[0]] : moods.map(k=>MOOD[k]).join(' ＋ ')+'（すべての要素を1つの書きぶりに混ぜる。どれかに偏らせない）';
    const kasure = ['なし（線の中はベタで均一）','ごく少し（数か所の払いの先だけ、線の内側にごく細い抜け（背景が見える）が出る程度）','少し（書き終わりや速い払いの一部で、線の内側に細い抜けが出る）','強め（インク切れ気味。払い・はね・長い線の後半で線が割れて抜けが目立つ）','かなり強め（多くの画でかすれ、線の半分近くが割れる。ただし字形が読めなくなるほどは欠けさせない）'][(typeof st.kasure==='number'?st.kasure:1)-1];
    const wt = [['極細','文字の高さの約2%、0.3mmペン程度'],['細','文字の高さの約4%'],['やや細','文字の高さの約6%'],['普通','文字の高さの約8%'],['やや太','文字の高さの約11%'],['太','文字の高さの約14%'],['極太','文字の高さの約18%、太マーカー程度。つぶれて読めなくならない範囲']][(st.weight||4)-1];
    const tamari = ['なし（線の太さは書き始めから終わりまでペンなりに一定）','ごく少し（いくつかの書き始めだけ、インクがわずかに丸く溜まる）','少し（書き始め・止め・折り返しの一部に、線幅より少し大きい丸い溜まり）','多め（書き始め・止め・折れの多くに、はっきりした溜まり。線が重なる交点も濃く膨らむ）','かなり多め（ほとんどの止め・交点に大きめの溜まり。ただし溜まりで字がつぶれたり、隣の画とくっついたりしない）'][(typeof st.tamari==='number'?st.tamari:1)-1];
    const kind = {ja:'日本語（漢字・ひらがな・カタカナ）',en:'英字（アルファベット）',mix:'日本語と英字の混在'}[st.kind||'ja'];
    const pen  = {ball:'ボールペン（細く均一な線）',fude:'筆ペン（太細の抑揚が大きい）',mannen:'万年筆（線にわずかな抑揚）',pencil:'鉛筆（粒子感のある線、筆圧で濃淡）',marker:'マーカー（太く均一、角の丸い線）'}[st.pen||'ball'];
    const dir  = (st.dir||'h')==='v' ? '縦書き（上から下へ、列は右から左へ進む）' : '横書き（左から右へ、行は上から下へ進む）';
    const cols = st.cols||'1';
    const colLine = (st.dir||'h')==='v' ? `縦の列を${cols}列にする（改行位置は下の文章どおり）` : (cols==='1' ? '1段組み（改行位置は下の文章どおり）' : `${cols}段組み（左右に${cols}つのまとまりを並べる。どの文をどの段に入れるかは下の文章の区切り「---」どおり）`);
    const bg   = (st.bg||'trans')==='trans' ? '透過PNG（背景なし、文字の線だけ。透過できない場合は真っ白 #FFFFFF の無地にする）' : '真っ白 #FFFFFF の無地（紙の質感・罫線・汚れなし）';
    const text = (st.text||'').trim();
    return `手書き文字の画像を生成してください。書く文章は下の【書く文章】だけです。

${askBlock([
  '【書く文章】が空でないか（空なら聞く）',
  '文章が長すぎて1枚に収まらない場合、どうするか（文字を小さくするか、分けるか）',
  '読めない・判断できない文字が文章に含まれていないか'
])}

■ 書く文章（この文字だけを書く。1字も足さない・変えない・省かない）
【書く文章】
${text || '（ここに書かせたい文章を入れる）'}
【書く文章ここまで】
  ・改行は上の文章の改行どおり。勝手に改行しない、まとめない
  ・漢字をひらがなにしない、ひらがなを漢字にしない。句読点・記号もそのまま
  ・誤字に見えても直さない。文章にない飾り文字・サイン・日付・絵を足さない

■ 手書きの指定
  ・書き手の印象：${who}
${mood ? `  ・雰囲気：${mood}\n` : ''}  ・文字種：${kind}
  ・ペン：${pen}
  ・線の太さ：${wt[0]}（線幅は${wt[1]}。全体でこの太さを基準に、ペンなりの抑揚だけつける）
  ・インクのかすれ：${kasure}
  ・インクだまり：${tamari}
    （溜まりは線の一部として描く。線の外に広がるにじみ・飛び散りは描かない）
  ・組み：${dir}
  ・列：${colLine}
  ・背景：${bg}
  ・実際に人が書いたように：字の大きさ・傾き・間隔にわずかな揺らぎ。ただしフォントのような均一さは避け、崩しすぎて読めなくしない
  ・文字色：黒 #000000 の1色（鉛筆も黒鉛の濃いグレーまで。色インクは使わない）

■ 切り抜き用の条件（この画像は文字だけを切り抜いて使う）
  ・文字以外を描かない：紙の質感・影・光の反射・にじみの広がり・手・ペン・机・装飾・枠線は入れない
  ・背景はムラのない1色。グラデーション・ビネットなし
  ・文字の線は背景とはっきり分かれる濃さにする。かすれは線の内側だけで、背景に粒を散らさない
  ・文字が画像の端に触れないよう周囲に余白を取る。列（段）の間も、文字同士が重ならない間隔を空ける

■ 出力
  1. 画像
  2. 画像に書いた文字を、画像から読み直して書き起こしたもの（行ごと）
  3. 【書く文章】と2を1行ずつ比べ、違う字があれば全部挙げる（無ければ「差異：0件」）`;
  };

  T.pserase = function(st){
    const M = {none:null,floor:['床・地面','floor'],wall:['壁','wall'],sky:['空','sky'],grass:['芝生・草','grass'],water:['水面','water surface'],cloth:['布・紙','fabric / paper'],road:['道路・アスファルト','asphalt road']};
    let ja = M[st.around||'none'] ? M[st.around][0] : '';
    const free=(st.aroundFree||'').trim(); if(free) ja=free;
    const line = ja ? `${ja}の続き、周囲と同じ質感と光` : '（空欄のまま生成）';
    return `【Photoshop 選択範囲だけ削除・周囲で補完】

■ 生成塗りつぶしに入れる言葉（この1行だけ。空欄のままでも可）
${line}

■ 手順（上から順に試す）
  0. 選択範囲は消す物よりひと回り大きく取る（影・輪郭の色まで含める）。必要なら「選択範囲を変更 → 拡張」で 4〜8px
  1. コンテンツに応じた塗りつぶし（編集 → コンテンツに応じた塗りつぶし）
     画像の選択範囲外の画素だけで埋める。サンプリング範囲を塗って調整し、出力先は「新規レイヤー」
  2. 1で模様がずれる・繰り返しが目立つ場合：生成塗りつぶしを、プロンプト空欄で生成
  3. 2で余計な物が描かれる場合：上の1行を入れて生成。3案を切り替えて選ぶ

■ 書かない言葉
  「削除」「消す」「〜なし」「〜を取る」は書かない。否定が伝わらず、消したい物が描かれることがある
  書くのは「消した後にそこに見えるもの」だけ

■ 仕上げの確認
  ・拡大して、埋めた部分に文字・模様・物が新しく入っていないか
  ・周囲と明るさ・ノイズ・ぼけ具合がそろっているか（浮いて見えたら、範囲を広げて再生成）
  ・広い範囲は一度にやらず、数回に分ける（生成部分は粗くなりやすい）`;
  };

  function composeOneShot(fn, st){
    const a = fn(Object.assign({}, st, {step:'1'}));
    let b = fn(Object.assign({}, st, {step:'2'}));
    let aa = a.replace(STEP1_TAIL, STOP_BLOCK);
    b = b.replace(STEP2_INPUT, STEP0_CONFIRM);
    b = b.replace(/^.*\n/, '');
    b = b.replace(/  ・確定テキストが【確定テキスト】の枠に貼られているか（空なら聞く）\n/, '');
    b = b.replace('■ 開始前の確認（不足があれば生成せず、質問して止まる）', '■ 確認後の作業に入る前の確認（不足があれば質問して止まる）');
    return aa + '\n\n' + b;
  }

// ======================= 貼り先アプリ =======================
  const APPS={
    claude:{label:'Claude',cls:'claude',color:'var(--claude)'},
    gpt:{label:'ChatGPT',cls:'gpt',color:'var(--gpt)'},
    ps:{label:'Photoshop',cls:'ps',color:'var(--ps)'},
    ai:{label:'Illustrator',cls:'ai',color:'var(--ai)'}
  };
  function appBadges(list){ return list.map((k,i)=>`<span class="app ${APPS[k].cls}${i?' sub':''}">${APPS[k].label}</span>`).join(''); }

// ======================= 象徴モーション（scene） =======================
  // アイコン（24x24）。クラス名は内側アニメ用
  const K='stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  const ICON={
    img:  `<svg viewBox="0 0 24 24" ${K}><rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="8.5" cy="9" r="1.6"/><path d="M3.5 17l5-5 4 4 3-3 5 5"/></svg>`,
    imgblur:`<svg viewBox="0 0 24 24" ${K} style="filter:blur(1.6px);color:#888"><rect x="3" y="4" width="18" height="16" rx="2.5"/><circle cx="8.5" cy="9" r="1.6"/><path d="M3.5 17l5-5 4 4 3-3 5 5"/></svg>`,
    doc:  `<svg viewBox="0 0 24 24" ${K}><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/><path class="l l0" d="M9 12h7"/><path class="l l1" d="M9 15h7"/><path class="l l2" d="M9 18h5"/></svg>`,
    txt:  `<svg viewBox="0 0 24 24" ${K}><path class="l l0" d="M4 7h16"/><path class="l l1" d="M4 12h16"/><path class="l l2" d="M4 17h10"/></svg>`,
    svg:  `<svg viewBox="0 0 24 24" ${K}><rect x="2.5" y="5" width="19" height="14" rx="3"/><text x="12" y="15.6" text-anchor="middle" font-size="7.5" font-weight="700" fill="currentColor" stroke="none" font-family="Helvetica,Arial,sans-serif">SVG</text></svg>`,
    stop: `<svg viewBox="0 0 24 24" ${K}><g class="bars"><path d="M9 6v12"/><path d="M15 6v12"/></g><g class="ok"><rect x="3" y="7" width="18" height="10" rx="5"/><text x="12" y="14.6" text-anchor="middle" font-size="6.5" font-weight="700" fill="currentColor" stroke="none" font-family="Helvetica,Arial,sans-serif">OK</text></g></svg>`,
    braces:`<svg viewBox="0 0 24 24" ${K}><path d="M9 4c-2 0-3 1-3 3v3c0 1-1 2-2 2 1 0 2 1 2 2v3c0 2 1 3 3 3"/><path d="M15 4c2 0 3 1 3 3v3c0 1 1 2 2 2-1 0-2 1-2 2v3c0 2-1 3-3 3"/><path class="l l0" d="M10 10h4"/><path class="l l1" d="M10 14h4"/></svg>`,
    chart:`<svg viewBox="0 0 24 24" ${K}><path d="M3 20h18"/><rect class="b b0" x="5" y="11" width="3.5" height="9"/><rect class="b b1" x="10.2" y="6" width="3.5" height="14"/><rect class="b b2" x="15.5" y="14" width="3.5" height="6"/></svg>`,
    rows: `<svg viewBox="0 0 24 24" ${K}><path d="M4 7h7M15 7h5"/><path d="M4 12h7M15 12h5"/><path d="M4 17h7M15 17h5"/></svg>`,
    shapes:`<svg viewBox="0 0 24 24" ${K}><circle class="s s0" cx="7" cy="8" r="3.5"/><rect class="s s1" x="13" y="4.5" width="7" height="7" rx="1"/><path class="s s2" d="M12 20l-4.5-7h9z"/></svg>`,
    shapesColor:`<svg viewBox="0 0 24 24" stroke="none"><circle class="s s0" cx="7" cy="8" r="3.5" fill="#e0713d"/><rect class="s s1" x="13" y="4.5" width="7" height="7" rx="1" fill="#2f6fed"/><path class="s s2" d="M12 20l-4.5-7h9z" fill="#1f9d55"/></svg>`,
    card: `<svg viewBox="0 0 24 24" ${K}><rect x="2" y="6" width="20" height="12" rx="2"/><path class="l l0" d="M6 11h7"/><path class="l l1" d="M6 14h5"/></svg>`,
    grid: `<svg viewBox="0 0 24 24" ${K}><rect class="g" x="3" y="4" width="18" height="16" rx="1"/><path class="g" d="M3 9.5h18M3 15h18M9 4v16M15 4v16"/></svg>`,
    gridPhoto:`<svg viewBox="0 0 24 24" ${K} style="color:#888"><path d="M4.5 5l15-1.5L20 19.5 4 20.5z"/><path d="M4.4 10.2l15.3-1.1M4.2 15.4l15.5-.6M9.5 4.5l-.3 15.6M14.8 4l.3 16"/></svg>`,
    erase:`<svg viewBox="0 0 24 24" ${K}><rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3.5 17l5-5 4 4 3-3 5 5"/><rect x="12" y="6.5" width="6.5" height="6" rx=".5" stroke-dasharray="1.6 1.4"/><circle class="obj" cx="15.25" cy="9.5" r="1.8" fill="currentColor"/></svg>`,
    check:`<svg viewBox="0 0 24 24" ${K}><circle cx="12" cy="12" r="9"/><path class="ck" d="M7.5 12.5l3 3 6-6.5"/></svg>`,
    surface:`<svg viewBox="0 0 24 24" ${K}><rect class="fillrect" x="3" y="12" width="18" height="8" rx="1.5" fill="#ddd" stroke="none"/><rect x="3" y="12" width="18" height="8" rx="1.5"/><circle cx="12" cy="9" r="4" fill="#fff"/></svg>`,
    next: `<svg viewBox="0 0 24 24" ${K}><text x="12" y="17" text-anchor="middle" font-size="14" font-weight="700" fill="currentColor" stroke="none">次</text></svg>`,
    typo: `<svg viewBox="0 0 24 24" ${K}><text x="12" y="15" text-anchor="middle" font-size="14" font-weight="700" fill="currentColor" stroke="none" font-family="'Noto Sans JP','Hiragino Sans',sans-serif">あ</text><path class="wv" d="M5 20l2-1.5 2 1.5 2-1.5 2 1.5 2-1.5 2 1.5 2-1.5"/></svg>`,
    content:`<svg viewBox="0 0 24 24" ${K}><path d="M4 6h16M4 10.5h16M4 15h9"/><path class="ck" d="M14.5 18.5l2.2 2.2 4.3-4.7"/></svg>`,
    proper:`<svg viewBox="0 0 24 24" ${K}><path d="M3 12.5V4h8.5L21 13.5 12.5 22z"/><circle cx="7.5" cy="8.5" r="1.6"/></svg>`,
    official:`<svg viewBox="0 0 24 24" ${K}><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/><path d="M4.5 9.5h12M4.5 11.5h12M10.5 4c-2.5 2.5-2.5 10.5 0 13M10.5 4c2.5 2.5 2.5 10.5 0 13"/></svg>`,
    qr:   `<svg viewBox="0 0 24 24" ${K}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M6.5 6.5h.01M17.5 6.5h.01M6.5 17.5h.01" stroke-width="2.2"/><path d="M14 14h2v2h-2zM18 14h3M14 18h2M18 18h3v3M16 21h2"/></svg>`,
    diff: `<svg viewBox="0 0 24 24" ${K}><path d="M3 4h7v16H3zM14 4h7v16h-7z"/><path d="M5.5 8h2M5.5 11h2M5.5 14h2M16.5 8h2M16.5 11h2M16.5 14h2"/><path class="ck" d="M10.5 9.5l3-.01M13.5 9.5l-1.2-1.2M13.5 9.5l-1.2 1.2M13.5 14.5h-3M10.5 14.5l1.2-1.2M10.5 14.5l1.2 1.2"/></svg>`,
    summary:`<svg viewBox="0 0 24 24" ${K}><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/><path class="ck" d="M8.5 15l2.5 2.5 5-5.5"/></svg>`
  };
  const ARROW=`<span class="ar"><svg viewBox="0 0 24 24" ${K}><path d="M5 12h13M13 7l5 5-5 5"/></svg></span>`;
  const PLUS=`<span class="ar"><svg viewBox="0 0 24 24" ${K}><path d="M12 6v12M6 12h12"/></svg></span>`;

  // scene: [{i:'img'}, '>', {i:'txt',lb:'転記'}, '+', ...]  '>'=矢印 '+'=プラス（同スロット扱い）
  function renderScene(spec){
    let k=0, html='';
    spec.forEach((it,idx)=>{
      if(it==='>'){ html+=ARROW.replace('class="ar"',`class="ar k${k+1}"`); k++; return; }
      if(it==='/'){ html+='<span class="br"></span>'; k++; return; }
      if(it==='+'){ html+=PLUS.replace('class="ar"',`class="ar k${k}"`); return; }
      const an=it.an?` an-${it.an}`:'';
      html+=`<span class="sc k${k}${an}${it.small?' plus':''}">${ICON[it.i]}${it.lb?`<span class="lb">${it.lb}</span>`:''}</span>`;
    });
    return html;
  }
  // 各スロット k=0..7 の出現タイミングを keyframes として生成（1ループ 7秒）
  function sceneCSS(){
    let css='';
    for(let k=0;k<8;k++){
      const a=Math.min(2+k*11, 80), b=a+4;
      css+=`@keyframes in${k}{0%,${a}%{opacity:0;transform:translateY(5px) scale(.92)}${b}%,93%{opacity:1;transform:none}97%,100%{opacity:0;transform:none}}
.sc.k${k},.ar.k${k}{animation:in${k} 7s cubic-bezier(.2,.8,.2,1) infinite}
@keyframes line${k}{0%,${b}%{transform:scaleX(0)}${b+3}%,93%{transform:scaleX(1)}100%{transform:scaleX(1)}}
.sc.k${k}.an-type .l{transform-origin:left;transform:scaleX(0);animation:line${k} 7s linear infinite}
.sc.k${k}.an-type .l1{animation-delay:.25s}.sc.k${k}.an-type .l2{animation-delay:.5s}
@keyframes bar${k}{0%,${b}%{transform:scaleY(0)}${b+5}%,93%{transform:scaleY(1)}100%{transform:scaleY(1)}}
.sc.k${k}.an-grow .b{transform-origin:center bottom;transform:scaleY(0);animation:bar${k} 7s cubic-bezier(.2,.8,.2,1) infinite}
.sc.k${k}.an-grow .b1{animation-delay:.2s}.sc.k${k}.an-grow .b2{animation-delay:.4s}
@keyframes bars${k}{0%,${b}%{opacity:1}${b+2}%{opacity:.25}${b+4}%{opacity:1}${b+6}%{opacity:.25}${b+8}%{opacity:1}${b+9}%,100%{opacity:0}}
@keyframes okin${k}{0%,${b+9}%{opacity:0;transform:scale(.7)}${b+12}%,93%{opacity:1;transform:scale(1)}100%{opacity:1}}
.sc.k${k}.an-stop .bars{animation:bars${k} 7s linear infinite}
.sc.k${k}.an-stop .ok{opacity:0;transform-origin:center;animation:okin${k} 7s cubic-bezier(.2,.8,.2,1) infinite}
@keyframes draw${k}{0%,${b}%{stroke-dashoffset:60}${b+6}%,100%{stroke-dashoffset:0}}
.sc.k${k}.an-draw .ck,.sc.k${k}.an-draw .g{stroke-dasharray:60;stroke-dashoffset:60;animation:draw${k} 7s ease-out infinite}
@keyframes sharp${k}{0%,${b}%{filter:blur(1.6px)}${b+6}%,100%{filter:blur(0)}}
.sc.k${k}.an-sharp svg{animation:sharp${k} 7s ease-out infinite}
@keyframes hue${k}{0%,${b}%{filter:hue-rotate(0deg)}93%,100%{filter:hue-rotate(360deg)}}
.sc.k${k}.an-hue svg{animation:hue${k} 7s linear infinite}
@keyframes fillc${k}{0%,${b}%{fill:#ddd}${b+4}%{fill:#e8d9b8}${b+9}%{fill:#cfd8dc}${b+14}%,93%{fill:#b8d8c8}100%{fill:#b8d8c8}}
.sc.k${k}.an-fill .fillrect{animation:fillc${k} 7s linear infinite}
@keyframes erase${k}{0%,${b}%{opacity:1;transform:scale(1)}${b+8}%,100%{opacity:0;transform:scale(.4)}}
.sc.k${k}.an-erase .obj{transform-box:fill-box;transform-origin:center;animation:erase${k} 7s ease-out infinite}
@keyframes sc0${k}{0%,${b}%{transform:translate(0,0)}${b+6}%,100%{transform:translate(-2px,-2px)}}
@keyframes sc1${k}{0%,${b}%{transform:translate(0,0)}${b+6}%,100%{transform:translate(2px,-2px)}}
@keyframes sc2${k}{0%,${b}%{transform:translate(0,0)}${b+6}%,100%{transform:translate(0,2.5px)}}
.sc.k${k}.an-scatter .s0{animation:sc0${k} 7s ease-out infinite}.sc.k${k}.an-scatter .s1{animation:sc1${k} 7s ease-out infinite}.sc.k${k}.an-scatter .s2{animation:sc2${k} 7s ease-out infinite}
`;
    }
    return css;
  }
  const styleEl=document.createElement('style'); styleEl.textContent=sceneCSS(); document.head.appendChild(styleEl);

// ======================= カード定義 =======================
  const FLOWS={
    once:  {label:'1回で完了', color:'var(--once)', steps:['プロンプトと画像を貼る','結果が返る']},
    stop:  {label:'転記で停止 → OK → 配置', color:'var(--gen)', steps:['プロンプトと画像を貼る','転記が返って止まる。確認して「OK」か修正指示を返す','SVGと照合表が返る']},
    staged:{label:'段階式・「次」で進む', color:'var(--chk)', steps:['プロンプトと校正対象を貼る','段階1が返って止まる。「次」と返す','段階ごとに繰り返し、最後に総評']},
    app:   {label:'Photoshop / Illustrator に貼る', color:'var(--app)', steps:['コピーする','アプリの入力欄に貼る']}
  };
  const STEP_OPT={id:'step',type:'chips',label:'進め方',items:[{v:'0',label:'一本（転記で停止 → OK/修正 → 配置）'},{v:'1',label:'手順1のみ：転記'},{v:'2',label:'手順2のみ：配置（確定テキストを貼る）'}],def:'0',
    hint:'基本は「一本」。止まらない・貼り直したいときは手順1／2を個別に。'};
  const SIZE_OPT={id:'size',type:'size',label:'仕上がりサイズ'};

  const CARDS=[
    {id:'brief',num:'1',group:'link',name:'参考×原稿 → 包括プロンプト（YAML）',purpose:'参考の型と原稿の中身から、YAML／JSON／指示文を出す。それをGPTに貼ってデザイン画像を起こす（SVGにするなら 2 へ）',
      paste:['参考画像（1枚目）','原稿（2枚目以降、またはPDF）'],apps:['claude','gpt'],scene:[{i:'img',lb:'参考'},'+',{i:'doc',lb:'原稿'},'>',{i:'braces',lb:'YAML',an:'type'},'>',{i:'img',lb:'GPTで画像'}],alert:['生成後、必ず原稿と確認'],io:{inp:'参考画像 ＋ 原稿（画像かPDF）', out:'GPT画像生成用の包括プロンプト（YAML／JSON／指示文）'},steps:['プロンプトと、参考画像・原稿を ChatGPT か Claude に貼る','原稿の転記が返って止まる。原稿と確認して「OK」か修正を返す','包括プロンプト（YAML／JSON／指示文）が返る','ChatGPT の新しいチャットで、返ってきた包括プロンプトをそのまま貼り、原稿（と参考画像）を添付して画像を生成させる','気に入るまで再生成。画像上の文字は崩れて当然なので読まない（文字は 2 で転記から入る）','画像で完結ならここまで。SVGにするなら保存して 2 へ'],note:{title:'GPTで画像を出すとき',lines:['貼るのは返ってきた包括プロンプト全文。YAML／JSONは設計の記録、指示文が生成の本体','参考画像を一緒に添付すると型が寄る。絵柄を複製しない指示は入っている','判型の縦横比で出ているか確認。違えば「W×H の比率で」と追加指示','原稿のレイアウトに引っ張られすぎるときは、原稿を画像でなくテキストで渡す']},flow:'stop',opts:[SIZE_OPT,STEP_OPT],tmpl:'brief',stepFlow:true},
    {id:'svg',num:'2',group:'link',name:'画像 → SVG化',purpose:'1 でGPTが出したデザイン画像を、印刷向けルールでSVGにトレースする。仕上げはIllustrator',
      paste:['変換元の画像','原稿テキスト（あれば）'],apps:['claude'],scene:[{i:'img'},'>',{i:'svg'}],alert:['生成後、必ず原稿と確認'],io:{inp:'1 で GPT が出したデザイン画像（原稿テキストがあれば一緒に）', out:'SVG ＋ 照合表（印刷向けルールで出力。仕上げは Illustrator）'},steps:['プロンプトと画像を Claude に貼る','転記が返って止まる。原稿と確認して「OK」か修正を返す','SVG と照合表が返る。アラートが 0 件か見る'],flow:'stop',opts:[SIZE_OPT,STEP_OPT],tmpl:'svg',stepFlow:true},
    {id:'chart',num:'3',group:'gen',name:'グラフ・表 → SVG',purpose:'貼ったデータ、または既成グラフのスクショから、グラフ・表のSVGを作る',
      paste:['データ（下の欄に貼る。画像は不要）'],apps:['claude'],scene:[{i:'rows',lb:'データ'},'>',{i:'chart',lb:'SVG',an:'grow'}],io:{inp:'データ（下の欄に貼る）、または既成グラフのスクショ', out:'グラフ・表の SVG ＋ 照合表（印刷向けルールで出力。仕上げは Illustrator）'},steps:['データを下の欄に貼る。既成グラフのスクショなら「画像」を選ぶ','プロンプトを Claude に貼る（画像のときはスクショも）','画像のときは数値の転記が返って止まる。元と確認して「OK」か修正を返す','グラフ SVG と照合表が返る。数値がデータどおりか、推定値の印を見る'],alert:['生成後、必ず元データと確認'],flow:'once',opts:[
        {id:'src',type:'chips',label:'データ元',items:[{v:'text',label:'テキスト（下に貼る）'},{v:'image',label:'画像（既成グラフのスクショ）'}],def:'text',
          hint:'画像のときは、まず数値を転記して止まる。値ラベルの無い棒・点は「推定」と印が付く。確認してOKか修正を返すと作図する。'},
        {id:'ctype',type:'chips',label:'種別',items:[{v:'bar',label:'棒（縦）'},{v:'barh',label:'棒（横）'},{v:'line',label:'折れ線'},{v:'pie',label:'円'},{v:'table',label:'表'}],def:'bar'},
        {id:'data',type:'textarea',label:'データ（1行1項目。ラベル,数値。表は列名を1行目に）※画像のときは不要',ph:'米国,2762\n香港,2228\n台湾,1812'},
        {id:'emph',type:'text',label:'強調する項目（任意・カンマ区切り）',ph:'例）台湾'}
      ],tmpl:'chart'},
    {id:'parts',num:'4',group:'gen',name:'画像 → パーツ分解素材シート',purpose:'デザイン画像から、文字を除いたイラスト・装飾だけを素材シートにする',
      paste:['元のデザイン画像'],
      alert:['文字・顔が崩れる。拡大して原本と確認'],apps:['gpt'],scene:[{i:'img'},'>',{i:'shapes',lb:'素材',an:'scatter'}],io:{inp:'元のデザイン画像', out:'文字なしのイラスト・装飾だけの素材シート画像'},steps:['プロンプトと元画像を ChatGPT に貼る','素材シート画像が返る','拡大して文字・顔・崩れを確認してから、Illustrator でベクター化'],flow:'once',opts:[],tmpl:'parts'},
    {id:'meishi',num:'10',group:'gen',name:'名刺SVG（91×55）',purpose:'原稿をそのままトレース、または参考デザインに沿って、名刺のSVGを作る。仕上げはIllustrator',
      paste:['原稿（記載内容）','参考デザイン','ロゴ（あれば）'],apps:['claude'],scene:[{i:'doc',lb:'原稿'},'+',{i:'img',lb:'参考'},'>',{i:'card',lb:'名刺',an:'type'}],alert:['生成後、必ず原稿と確認'],io:{inp:'原稿（名刺の写真・記載内容）。参考に沿って作るときは参考デザイン（＋ロゴ）も', out:'名刺の SVG ＋ 照合表（印刷向けルールで出力。仕上げは Illustrator）'},steps:['プロンプトと原稿・参考（・ロゴ）を Claude に貼る','原稿の転記が返って止まる。原稿と確認して「OK」か修正を返す','名刺 SVG と照合表が返る。アラートが 0 件か見る'],flow:'stop',opts:[
        {id:'layout',type:'chips',label:'レイアウト',items:[{v:'trace',label:'原稿をそのままトレース'},{v:'design',label:'参考デザインに沿って作る'}],def:'trace',
          hint:'トレースは参考デザイン不要。原稿の配置・大きさ・色を実測して再現する。'},
        {id:'ori',type:'chips',label:'向き',items:[{v:'h',label:'横（91×55）'},{v:'v',label:'縦（55×91）'}],def:'h'},
        {id:'side',type:'chips',label:'面',items:[{v:'front',label:'表のみ'},{v:'both',label:'表＋裏'}],def:'front'},
        {id:'bleed',type:'chips',label:'塗り足し',items:[{v:'on',label:'3mm付き'},{v:'off',label:'仕上がりのみ'}],def:'on'},
        STEP_OPT],tmpl:'meishi',stepFlow:true},
    {id:'ocrsvg',num:'11',group:'gen',name:'文字原稿 → SVG',purpose:'案内状・はがきなど文字主体の原稿を、原文のままSVGに配置する。文字は必ず原稿と確認',
      paste:['原稿の画像'],apps:['claude'],scene:[{i:'img'},'>',{i:'txt',lb:'OCR',an:'type'},'>',{i:'svg'}],alert:['生成後、必ず原稿と確認'],io:{inp:'文字主体の原稿画像（案内状・はがき等）', out:'原文のまま配置した SVG ＋ 照合表（人の確認が前提）'},steps:['サイズ・書体・組みを選んで、プロンプトと原稿画像を Claude に貼る','転記が返って止まる。原稿と確認して「OK」か修正を返す','SVG と照合表が返る。アラートが 0 件か見る'],flow:'stop',opts:[SIZE_OPT,
        {id:'font',type:'chips',label:'書体',items:[{v:'mincho',label:'明朝'},{v:'gothic',label:'ゴシック'}],def:'mincho'},
        {id:'dir',type:'chips',label:'組み',items:[{v:'h',label:'横組み'},{v:'v',label:'縦組み'}],def:'h'},
        {id:'align',type:'chips',label:'揃え',items:[{v:'left',label:'左'},{v:'center',label:'中央'}],def:'left'},
        STEP_OPT],tmpl:'ocrsvg',stepFlow:true},
    {id:'denpyo',num:'12',group:'gen',name:'伝票トレース → SVG',purpose:'伝票のスキャンを、実寸・罫線・アミ・文字まで編集可能なSVGに',
      paste:['伝票のスキャン／写真','仕上がり実寸（必須）'],apps:['claude'],scene:[{i:'gridPhoto',lb:'伝票'},'>',{i:'grid',lb:'SVG',an:'draw'}],alert:['生成後、必ず原稿と確認'],io:{inp:'伝票のスキャン／写真 ＋ 仕上がり実寸', out:'罫線・文字・アミを分けた編集可能な SVG ＋ 検品一覧'},steps:['実寸を指定して、プロンプトと伝票画像を Claude に貼る','セル単位の転記が返って止まる。原稿と確認して「OK」か修正を返す','SVG と検品一覧が返る。補完（data-added）とアラートを見る'],flow:'stop',opts:[SIZE_OPT,
        {id:'lw',type:'chips',label:'線幅',items:[{v:'measure',label:'実測して再現'},{v:'uniform',label:'0.3mmに統一'}],def:'measure'},
        {id:'ami',type:'chips',label:'アミ・色面',items:[{v:'on',label:'再現する（濃度を塗り矩形に）'},{v:'off',label:'落とす'}],def:'on'},
        {id:'rc',type:'chips',label:'角丸',items:[{v:'keep',label:'原稿どおり'},{v:'square',label:'直角に'}],def:'keep'},
        STEP_OPT],tmpl:'denpyo',stepFlow:true},

    {id:'mockup',num:'0',group:'gen',name:'PDF → モックアップ',purpose:'入稿PDF（数は任意）から、平置きの確認用モックアップ画像を作る。色は画面用の近似',
      paste:['PDF（何点でも）'],apps:['claude'],scene:[{i:'doc',lb:'PDF'},'>',{i:'img',lb:'モックアップ'}],alert:['色は近似。原本と確認'],
      io:{inp:'PDF（名刺・封筒・チラシ等。何点でも）', out:'平置きモックアップ画像（PNG）＋ 寸法一覧（＋ 確認用PDF）'},
      steps:['選んでコピーし、プロンプトとPDFを Claude に貼る','寸法一覧とモックアップ画像が返る','中身がPDFと同じか、並べたときの大きさが実物どおりかを見る'],
      flow:'once',opts:[
        {id:'lay',type:'chips',label:'並べ方',items:[{v:'both',label:'1点ずつ＋全点を1枚'},{v:'each',label:'1点ずつ'},{v:'all',label:'全点を1枚'}],def:'both'},
        {id:'bg',type:'chips',label:'背景',items:[{v:'light',label:'薄いグレー'},{v:'white',label:'白'},{v:'dark',label:'濃いグレー'}],def:'light'},
        {id:'tex',type:'chips',label:'紙の質感',items:[{v:'on',label:'あり'},{v:'off',label:'なし'}],def:'on'},
        {id:'proof',type:'chips',label:'確認用PDF（A4）',items:[{v:'on',label:'作る'},{v:'off',label:'作らない'}],def:'on'}
      ],tmpl:'mockup'},
    {id:'hand',num:'0',group:'gen',name:'手書き文字生成',purpose:'入力した文章を、指定した書き手・ペン・縦横・列数の手書き風画像にする。文字は崩れることがある',
      paste:['画像は不要（文章は下の欄に入力）'],apps:['gpt'],scene:[{i:'txt',lb:'文章'},'>',{i:'img',lb:'手書き'}],alert:['生成後、必ず原稿と確認'],
      io:{inp:'書かせたい文章（下の欄に入力）', out:'切り抜き用の手書き画像（透過PNG／白地黒） ＋ 差異の一覧'},
      steps:['文章を入力し、印象・ペン・縦横・列数を選んでコピー','ChatGPT に貼る','画像と差異一覧が返る。1字ずつ原稿と見比べる。違えば作り直し'],
      flow:'once',opts:[
        {id:'text',type:'textarea',label:'書く文章（改行はそのまま反映。段組みの区切りは「---」）',ph:'ありがとうございました\nまたお会いしましょう'},
        {id:'who',type:'chips',label:'書き手の印象',items:[{v:'f',label:'女性的'},{v:'m',label:'男性的'},{v:'n',label:'中性的'}],def:'f'},
        {id:'mood',type:'multi',label:'雰囲気（複数可・選ばなければ指定なし）',items:[{v:'stylish',label:'スタイリッシュ'},{v:'cute',label:'かわいい'},{v:'elegant',label:'上品'},{v:'casual',label:'ラフ'},{v:'genki',label:'元気'},{v:'soboku',label:'素朴'}],def:[]},
        {id:'kind',type:'chips',label:'文字種',items:[{v:'ja',label:'日本語（漢字・かな）'},{v:'en',label:'英字'},{v:'mix',label:'混在'}],def:'ja'},
        {id:'pen',type:'chips',label:'ペン',items:[{v:'ball',label:'ボールペン'},{v:'fude',label:'筆ペン'},{v:'mannen',label:'万年筆'},{v:'pencil',label:'鉛筆'},{v:'marker',label:'マーカー'}],def:'ball'},
        {id:'weight',type:'slider',label:'線の太さ',min:1,max:7,def:4,marks:['極細','細','やや細','普通','やや太','太','極太'],px:[1,1.8,2.6,3.6,4.8,6.2,8]},
        {id:'kasure',type:'slider',label:'インクのかすれ',min:1,max:5,def:1,marks:['なし','ごく少し','少し','強め','かなり強め'],px:[5,5,5,5,5],dash:['','60 1.5','22 2.5 34 2','9 3 14 2.5 6 3','4 3 6 4 3 3']},
        {id:'tamari',type:'slider',label:'インクだまり',min:1,max:5,def:1,marks:['なし','ごく少し','少し','多め','かなり多め'],px:[3,3,3,3,3],blobs:[[],[[9,16,2.2]],[[9,16,2.8],[84,10,2.4]],[[9,16,3.4],[46,13,2.6],[84,10,3],[111,12,2.8]],[[9,16,4.2],[31,11.7,3],[46,13,3.4],[68.6,14.1,2.8],[84,10,3.8],[111,12,3.6]]]},
        {id:'dir',type:'chips',label:'組み',items:[{v:'h',label:'横書き'},{v:'v',label:'縦書き'}],def:'h'},
        {id:'cols',type:'chips',label:'列数（縦書きは列、横書きは段）',items:[{v:'1',label:'1'},{v:'2',label:'2'},{v:'3',label:'3'},{v:'4',label:'4'}],def:'1'},
        {id:'bg',type:'chips',label:'背景',items:[{v:'trans',label:'透過PNG'},{v:'white',label:'白地黒'}],def:'trans'}
      ],tmpl:'hand'},
    {id:'proof',num:'8',group:'chk',name:'校正チェック',purpose:'誤字脱字・固有名詞を本命に、段階ごとに止まりながら校正する',
      paste:['校正対象（デザイン後のPDF／画像）','比較資料（元原稿・赤字。あれば）'],apps:['gpt'],scene:[{i:'typo',lb:'文字'},'>',{i:'content',lb:'内容',an:'draw'},'>',{i:'proper',lb:'固有名詞'},'>',{i:'official',lb:'公式'},'/',{i:'qr',lb:'QR'},'>',{i:'diff',lb:'原稿'},'>',{i:'summary',lb:'総評',an:'draw'}],alert:['最後は必ず人の目で確認'],io:{inp:'校正対象（デザイン後の PDF／画像）＋ 比較資料（あれば）', out:'段階ごとの指摘一覧と総評（見落としはありうる。最終判断は人）'},steps:['段階を選んで、プロンプトと校正対象を ChatGPT に貼る','段階 1 が返って止まる。読んで「次」','最後の段階で総評。「要・原本照合」を原本で確認し、最後は人の目で通しで読む'],flow:'staged',opts:[
        {id:'pmode',type:'chips',label:'進め方',items:[{v:'staged',label:'段階式（1段階ずつ止まる）'},{v:'batch',label:'一括（1回で。折れやすい）'}],def:'staged'},
        {id:'stages',type:'multi',label:'段階（押したものだけ入る）',items:[
          {v:'typo',label:'誤字脱字'},{v:'content',label:'内容校正（文法・表記・数値・整合）'},{v:'proper',label:'固有名詞'},
          {v:'official',label:'公式情報照合（Web検索）'},{v:'qr',label:'QR（デコード＋リンク）'},{v:'diff',label:'原稿突き合わせ'},
          {v:'book',label:'通し整合（ページもの）'},{v:'summary',label:'総評'}],
          def:['typo','content','proper','official','qr','diff','summary'],
          hint:'ページものは「通し整合」を押す。差異だけ見たいときは「原稿突き合わせ」だけ。検索・コード実行ONのモデルで。'}
      ],tmpl:'proof'},
    {id:'ocr',num:'9',group:'chk',name:'OCR（原文まま）',purpose:'画像の文字を、直さず整えず、書いてある通りに書き起こす',
      paste:['文字を起こしたい画像'],apps:['claude','gpt'],scene:[{i:'img'},'>',{i:'txt',lb:'原文まま',an:'type'}],alert:['生成後、必ず原稿と確認'],io:{inp:'文字を起こしたい画像', out:'原文ままの文字起こし（不確実な箇所は別掲。要確認）'},steps:['プロンプトと画像を ChatGPT か Claude に貼る','原文ままの文字起こしが返る','数字・固有名詞を原稿と突き合わせてから使う'],flow:'once',opts:[],tmpl:'ocr'},

    {id:'psfill',num:'5',group:'app',name:'Photoshop 床／面 差し替え',purpose:'被写体を残して、テーブル面や背景だけを別素材にする生成塗りつぶし用。縁と細部は要確認',
      paste:['Photoshopの生成塗りつぶし欄に貼る（画像は不要）'],
      alert:['文字・顔が崩れる。拡大して原本と確認'],apps:['ps'],scene:[{i:'surface',lb:'面'},'>',{i:'surface',lb:'面だけ変わる',an:'fill'}],io:{inp:'変える対象と新しい素材（下で選ぶ）', out:'Photoshop 生成塗りつぶしに貼るプロンプト（日本語／英語）と手順'},steps:['対象と素材を選んでコピー','Photoshop で被写体を選択 → 選択範囲を反転 → 2〜3px 拡張','生成塗りつぶしにプロンプトを貼って生成','文字・顔・被写体の縁を拡大して確認'],flow:'app',opts:[
        {id:'target',type:'chips',label:'変える対象',items:PS_TARGETS.map((t,i)=>({v:i,label:t.label})),def:0},
        {id:'mat',type:'chips',label:'新しい素材',items:PS_MATS.map((m,i)=>({v:i,label:m.label})),def:0},
        {id:'col',type:'pair',label:'色（任意・素材の前に付く）',a:{id:'colJa',ph:'例）紺色の'},b:{id:'colEn',ph:'e.g. navy blue'}},
        {id:'matfree',type:'pair',label:'自由入力（素材を上書き）',a:{id:'matJa',ph:'例）黒い石板'},b:{id:'matEn',ph:'e.g. black slate'}}
      ],tmpl:'psfill'},
    {id:'pserase',num:'0',group:'app',name:'Photoshop 選択範囲だけ削除',purpose:'選択した物を消し、周りの画像で埋める。コンテンツに応じた塗りつぶし → 生成塗りつぶしの順で使う',
      paste:['生成塗りつぶし欄に入れるのは先頭の1行だけ（空欄でも可）'],
      alert:['生成部分に別の物が入ることがある。拡大して確認'],apps:['ps'],scene:[{i:'erase',lb:'選択'},'>',{i:'erase',lb:'周りで埋まる',an:'erase'}],io:{inp:'消した後に見えるはずの素材（下で選ぶ。任意）', out:'生成塗りつぶしに入れる1行と、削除の手順'},steps:['消した後に見える素材を選んでコピー（分からなければ「指定しない」）','Photoshop で消す物をひと回り大きく選択','まずコンテンツに応じた塗りつぶし。だめなら生成塗りつぶし（空欄 → 1行）','拡大して、余計な物が入っていないか確認'],flow:'app',opts:[
        {id:'around',type:'chips',label:'消した後に見える素材',items:[{v:'none',label:'指定しない（空欄で生成）'},{v:'floor',label:'床・地面'},{v:'wall',label:'壁'},{v:'sky',label:'空'},{v:'grass',label:'芝生・草'},{v:'water',label:'水面'},{v:'cloth',label:'布・紙'},{v:'road',label:'道路'}],def:'none'},
        {id:'aroundFree',type:'text',label:'自由入力（素材を上書き）',ph:'例）木目のテーブル'}
      ],tmpl:'pserase'},
    {id:'psup',num:'6',group:'app',name:'Photoshop 画質だけ補完',purpose:'内容を変えずに解像感を上げる手順と補助プロンプト。文字・顔は要確認',
      paste:['解像度は手動で上げる（画像解像度／Camera Raw 強化／スーパーズーム）','プロンプトは、残った粗い部分を狭く選択して使う'],
      alert:['解像度は手動で上げる（⌘⌥I）','文字・顔が崩れる。拡大して原本と確認'],apps:['ps'],scene:[{i:'imgblur',lb:'粗い'},'>',{i:'img',lb:'精細',an:'sharp'}],io:{inp:'（画像は貼らない。Photoshop 上の手順）', out:'解像度を上げる手順と、仕上げ用の補助プロンプト'},steps:['Photoshop で 画像解像度（⌘⌥I）→ 再サンプル「ディテールを保持 2.0」で画素数を上げる','残った粗い部分だけ狭く選択し、プロンプトを生成塗りつぶしに貼る（任意）','文字・顔を拡大して確認。文字・ロゴがある画像は生成を使わない'],flow:'app',opts:[],tmpl:'psup'},
    {id:'recolor',num:'7',group:'app',name:'Illustrator 生成再配色 キーワード',purpose:'生成再配色に入れる情景・雰囲気のキーワード',
      paste:['Illustratorの生成再配色欄に貼る'],apps:['ai'],scene:[{i:'shapesColor'},'>',{i:'shapesColor',lb:'配色',an:'hue'}],io:{inp:'情景・雰囲気のキーワード（下で選ぶか入力）', out:'Illustrator 生成再配色に貼るキーワードと使い方'},steps:['キーワードを選ぶか入力してコピー','Illustrator でアートを選択 → 編集 → カラーを編集 → 生成再配色','貼って生成し、4 案から選ぶ','採用後はスウォッチを CMYK 化し、黒・グレーが K 版のみか確認'],flow:'app',opts:[
        {id:'rcCat',type:'chips',label:'候補カテゴリ',items:[{v:'season',label:'季節・時間帯'},{v:'wa',label:'和のテーマ'},{v:'biz',label:'業種・媒体'},{v:'tone',label:'トーン・質感'}],def:'season'},
        {id:'kwpick',type:'words',label:'候補（クリックで下に入る）'},
        {id:'kw',type:'text',label:'キーワード（自由入力可）',ph:'例）秋の紅葉'}
      ],tmpl:'recolor'}
  ];
  const GROUPS=[
    {id:'link',title:'連動　1 → 2',desc:''},
    {id:'gen',title:'生成',desc:'SVGや素材を作る。'},
    {id:'chk',title:'確認',desc:'できたものを検査する。'},
    {id:'app',title:'Photoshop・Illustrator',desc:'アプリの入力欄に直接貼るもの。'}
  ];

// ======================= 状態 =======================
  const S={};
  function load(){ try{ const j=localStorage.getItem('cardbook.v1'); if(j) Object.assign(S, JSON.parse(j)); }catch(e){} }
  function save(){ try{ localStorage.setItem('cardbook.v1', JSON.stringify(S)); }catch(e){} }
  function stateOf(card){
    if(!S[card.id]) S[card.id]={};
    const st=S[card.id];
    card.opts.forEach(o=>{
      // 保存済みの値が今の選択肢と合わない（型が変わった・選択肢が消えた）ときは初期値に戻す
      const vals=(o.items||[]).map(it=>String(it.v));
      if(o.type==='chips' && (st[o.id]===undefined || !vals.includes(String(st[o.id])))) st[o.id]=o.def;
      if(o.type==='multi'){ if(!Array.isArray(st[o.id])) st[o.id]=o.def.slice(); else st[o.id]=st[o.id].filter(v=>vals.includes(String(v))); }
      if(o.type==='slider' && (typeof st[o.id]!=='number' || st[o.id]<o.min || st[o.id]>o.max)) st[o.id]=o.def;
      if(o.type==='size'){ if(st.orient===undefined) st.orient='portrait'; if(st.binding===undefined) st.binding='single'; }
    });
    return st;
  }
  function render(card){
    const st=stateOf(card);
    const fn=T[card.tmpl];
    if(card.stepFlow && st.step==='0') return composeOneShot(fn, st);
    return fn(st);
  }

// ======================= 一覧描画 =======================
  const main=document.getElementById('main');
  // 表示順に通し番号を振る（群の順 → 群内の順）
  let __n=0; GROUPS.forEach(g=>CARDS.filter(c=>c.group===g.id).forEach(c=>{ c.num=String(++__n); }));
  GROUPS.forEach(g=>{
    const sec=document.createElement('section'); sec.className='group';
    sec.innerHTML=`<h2>${g.title}</h2><div class="grid"></div>`;
    const grid=sec.querySelector('.grid');
    CARDS.filter(c=>c.group===g.id).forEach(c=>{
      const f=FLOWS[c.flow];
      const el=document.createElement('button'); el.className='card'; el.style.setProperty('--appColor', APPS[c.apps[0]].color);
      el.setAttribute('aria-label', c.name);
      el.innerHTML=`<div class="top"><span class="num">${c.num}</span><span class="name">${c.name}</span>
        <span class="arrow"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span></div>
        <p class="purpose">${c.purpose}</p>
        <div class="scene${c.scene.includes('/')?' rows':(c.scene.filter(x=>typeof x!=='string').length>=5?' dense':'')}">${renderScene(c.scene)}</div>
        <div class="apps">${appBadges(c.apps)}</div>`;
      el.onclick=()=>open(c);
      grid.appendChild(el);
    });
    main.appendChild(sec);
  });

// ======================= ドロワー =======================
  const drawer=document.getElementById('drawer'), backdrop=document.getElementById('backdrop');
  const dBody=document.getElementById('dBody'), dCopy=document.getElementById('dCopy');
  let cur=null, outEl=null;

  function open(card){
    cur=card;
    if(card.stepFlow){ stateOf(card).step='0'; }   // 手順は案件ごとに選ぶので、開くたびに「一本」へ戻す
    const f=FLOWS[card.flow];
    drawer.style.setProperty('--flowColor', APPS[card.apps[0]].color);   // 手順の丸数字は貼り先アプリの色
    document.getElementById('dNum').textContent=card.num;
    document.getElementById('dName').textContent=card.name;
    document.getElementById('dPurpose').textContent=card.purpose;
    document.getElementById('dApps').innerHTML=appBadges(card.apps);
    drawer.dataset.app=card.apps[0];
    dBody.innerHTML='';
    // 入れる → 返ってくる
    dBody.appendChild(sec('このプロンプトがすること', `<div class="io"><div class="row"><span class="k">入れる</span><span>${card.io.inp}</span></div><div class="row"><span class="k">返ってくる</span><span>${card.io.out}</span></div></div>`));
    // 手順（カード固有）
    const steps = card.steps || f.steps;
    dBody.appendChild(sec('手順', `<ol class="flowlist">${steps.map((s,i)=>`<li><span class="n">${i+1}</span><span>${s}</span></li>`).join('')}</ol>`));
    if(card.note){ dBody.appendChild(sec(card.note.title, `<ul class="paste">${card.note.lines.map(l=>`<li>${l}</li>`).join('')}</ul>`)); }
    // 選択肢
    if(card.opts.length){
      const box=document.createElement('div');
      card.opts.forEach(o=>box.appendChild(optEl(card,o)));
      dBody.appendChild(sec('選ぶ', box));
    }
    // 出力
    const outWrap=document.createElement('div'); outWrap.className='out';
    outEl=document.createElement('textarea'); outEl.readOnly=true; outWrap.appendChild(outEl);
    dBody.appendChild(sec('出力されるプロンプト（確認用）', outWrap));
    refresh();
    showWarn(card);
    drawer.classList.add('on'); backdrop.classList.add('on'); drawer.setAttribute('aria-hidden','false');
    document.body.style.overflow='hidden';
    if(!card.alert) setTimeout(()=>dCopy.focus(), 250);
  }
  const dWarn=document.getElementById('dWarn');
  function showWarn(card){
    if(!card.alert){ dWarn.style.display='none'; dWarn.innerHTML=''; dCopy.disabled=false; return; }
    dCopy.disabled=true;
    dWarn.style.display='flex';
    dWarn.innerHTML=`<div class="box" role="alertdialog" aria-label="注意">
      <div class="wt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/></svg></div>
      <div class="wl">${card.alert.map(l=>`<div>${l}</div>`).join('')}</div>
      <button class="btn primary" id="dWarnOk">確認した</button></div>`;
    const ok=dWarn.querySelector('#dWarnOk');
    ok.onclick=()=>{ dWarn.style.display='none'; dWarn.innerHTML=''; dCopy.disabled=false; dCopy.focus(); };
    setTimeout(()=>ok.focus(), 260);
  }
  function close(){
    drawer.classList.remove('on'); backdrop.classList.remove('on'); drawer.setAttribute('aria-hidden','true');
    document.body.style.overflow=''; cur=null;
  }
  function sec(title, content){
    const d=document.createElement('div'); d.className='sec';
    const h=document.createElement('h4'); h.textContent=title; d.appendChild(h);
    if(typeof content==='string'){ const w=document.createElement('div'); w.innerHTML=content; d.appendChild(w); } else d.appendChild(content);
    return d;
  }
  function refresh(){
    if(!cur) return;
    outEl.value=render(cur);
    save();
  }
  function chipsEl(items, isOn, onPick, multi){
    const w=document.createElement('div'); w.className='chips';
    items.forEach(it=>{
      const c=document.createElement('button'); c.type='button'; c.className='chip'+(multi?' multi':''); c.textContent=it.label;
      if(isOn(it.v)) c.classList.add('on');
      c.onclick=()=>{ onPick(it.v); if(!multi){ w.querySelectorAll('.chip').forEach(x=>x.classList.remove('on')); c.classList.add('on'); } else { c.classList.toggle('on'); } refresh(); };
      w.appendChild(c);
    });
    return w;
  }
  function optEl(card,o){
    const st=stateOf(card);
    const d=document.createElement('div'); d.className='opt';
    if(o.type!=='words' || true){ const l=document.createElement('label'); l.className='l'; l.textContent=o.label; d.appendChild(l); }
    if(o.type==='chips'){
      d.appendChild(chipsEl(o.items, v=>String(st[o.id])===String(v), v=>{ st[o.id]=v; }, false));
    } else if(o.type==='multi'){
      d.appendChild(chipsEl(o.items, v=>st[o.id].includes(v), v=>{ const a=st[o.id]; const i=a.indexOf(v); if(i>=0) a.splice(i,1); else a.push(v); }, true));
    } else if(o.type==='text'){
      const i=document.createElement('input'); i.type='text'; i.placeholder=o.ph||''; i.value=st[o.id]||''; i.oninput=()=>{ st[o.id]=i.value; refresh(); }; d.appendChild(i);
      d.dataset.opt=o.id;
    } else if(o.type==='textarea'){
      const t=document.createElement('textarea'); t.placeholder=o.ph||''; t.value=st[o.id]||''; t.oninput=()=>{ st[o.id]=t.value; refresh(); }; d.appendChild(t);
    } else if(o.type==='pair'){
      const r=document.createElement('div'); r.className='row2';
      [o.a,o.b].forEach(p=>{ const i=document.createElement('input'); i.type='text'; i.placeholder=p.ph; i.value=st[p.id]||''; i.oninput=()=>{ st[p.id]=i.value; refresh(); }; r.appendChild(i); });
      d.appendChild(r);
    } else if(o.type==='words'){
      const w=document.createElement('div'); w.className='chips';
      const draw=()=>{ w.innerHTML=''; (RC_WORDS[st.rcCat||'season']||[]).forEach(word=>{ const c=document.createElement('button'); c.type='button'; c.className='chip'; c.textContent=word;
        c.onclick=()=>{ st.kw=word; const inp=dBody.querySelector('[data-opt="kw"] input'); if(inp) inp.value=word; refresh(); }; w.appendChild(c); }); };
      draw(); d.appendChild(w); d._redraw=draw;
    } else if(o.type==='slider'){
      const w=document.createElement('div'); w.className='slider';
      const r=document.createElement('input'); r.type='range'; r.min=o.min; r.max=o.max; r.step=1; r.value=st[o.id];
      const v=document.createElement('div'); v.className='sv';
      const draw=()=>{ const n=+r.value; v.innerHTML=`<svg viewBox="0 0 120 24" aria-hidden="true"><path d="M8 16 C 34 4, 58 22, 84 10 S 108 8, 112 12" fill="none" stroke="currentColor" stroke-linecap="${o.dash&&o.dash[n-1]?'butt':'round'}" stroke-width="${o.px[n-1]}"${o.dash&&o.dash[n-1]?` stroke-dasharray="${o.dash[n-1]}"`:''}/>${o.blobs?o.blobs[n-1].map(b=>`<ellipse cx="${b[0]}" cy="${b[1]}" rx="${b[2]*1.25}" ry="${b[2]}" fill="currentColor"/>`).join(''):''}</svg><b>${o.marks[n-1]}</b>`;
        r.style.setProperty('--p', ((n-o.min)/(o.max-o.min)*100)+'%'); };
      r.oninput=()=>{ st[o.id]=+r.value; draw(); refresh(); };
      draw(); w.appendChild(r); w.appendChild(v);
      const ends=document.createElement('div'); ends.className='ends'; ends.innerHTML=`<span>${o.marks[0]}</span><span>${o.marks[o.marks.length-1]}</span>`; w.appendChild(ends);
      d.appendChild(w);
    } else if(o.type==='size'){
      const w=document.createElement('div');
      const sizeChips=chipsEl(SIZES.map(s=>({v:s.v,label:`${s.label} ${s.w}×${s.h}${s.unit||''}`})), v=>st.size&&st.size.v===v, v=>{ const s=SIZES.find(x=>x.v===v); st.size={v:s.v,w:s.w,h:s.h,label:s.label,unit:s.unit||'mm',fixed:!!s.fixed}; }, false);
      w.appendChild(sizeChips);
      const cr=document.createElement('div'); cr.className='sizerow';
      cr.innerHTML=`<input type="number" placeholder="W"><span>×</span><input type="number" placeholder="H"><select><option value="mm">mm</option><option value="px">px</option></select><button type="button" class="apply">カスタムで指定</button>`;
      const [cw,ch]=cr.querySelectorAll('input'); const un=cr.querySelector('select');
      cr.querySelector('.apply').onclick=()=>{ const W=+cw.value,H=+ch.value; if(!W||!H) return; st.size={v:'custom',w:W,h:H,label:'カスタム',unit:un.value,fixed:true}; sizeChips.querySelectorAll('.chip').forEach(x=>x.classList.remove('on')); refresh(); echo.innerHTML=echoText(); };
      w.appendChild(cr);
      const l2=document.createElement('label'); l2.className='l'; l2.style.marginTop='10px'; l2.textContent='向き・綴じ'; w.appendChild(l2);
      const r=document.createElement('div'); r.className='chips';
      r.appendChild(chipsEl([{v:'portrait',label:'縦'},{v:'landscape',label:'横'}], v=>st.orient===v, v=>{ st.orient=v; }, false));
      r.appendChild(chipsEl([{v:'single',label:'単ページ'},{v:'spread',label:'見開き（横2倍）'}], v=>st.binding===v, v=>{ st.binding=v; }, false));
      w.appendChild(r);
      const echo=document.createElement('div'); echo.className='echo';
      const echoText=()=> st.size ? `選択：<b>${sizeLine(st)}</b>` : 'サイズ未選択（伝票・はがき等は必ず指定）';
      echo.innerHTML=echoText(); w.appendChild(echo);
      w.addEventListener('click',()=>{ echo.innerHTML=echoText(); });
      d.appendChild(w);
    }
    if(o.hint){ const h=document.createElement('div'); h.className='hint'; h.textContent=o.hint; d.appendChild(h); }
    // recolor: カテゴリ変更で候補を描き直す
    if(o.id==='rcCat'){ d.addEventListener('click',()=>{ const wd=dBody.querySelector('.opt ._w'); const all=dBody.querySelectorAll('.opt'); all.forEach(x=>{ if(x._redraw) x._redraw(); }); }); }
    return d;
  }

  async function copy(){
    if(dCopy.disabled) return;
    const text=outEl?outEl.value:'';
    if(!text) return;
    try{ await navigator.clipboard.writeText(text); }
    catch(e){ outEl.select(); document.execCommand('copy'); }
    dCopy.classList.add('done'); dCopy.textContent='コピーしました';
    toast('コピーしました。画像と一緒に貼ってください');
    setTimeout(()=>{ dCopy.classList.remove('done'); dCopy.textContent='プロンプトをコピー'; }, 1600);
  }
  const toastEl=document.getElementById('toast');
  function toast(msg){ toastEl.textContent=msg; toastEl.classList.add('on'); clearTimeout(toast._t); toast._t=setTimeout(()=>toastEl.classList.remove('on'), 1800); }

  dCopy.onclick=copy;
  document.getElementById('dClose').onclick=close;
  document.getElementById('dClose2').onclick=close;
  backdrop.onclick=close;
  document.addEventListener('keydown',e=>{ if(e.key==='Escape' && cur) close(); if((e.metaKey||e.ctrlKey) && e.key==='Enter' && cur) copy(); });

  load();
})();
</script>
</body>
</html>
'''

html = html.replace('__CONSTS__', consts.rstrip()).replace('__RC__', rc.rstrip()).replace('__TMPL__', tmpl_js)
open(DST,'w',encoding='utf-8').write(html)
print("written", len(html))
