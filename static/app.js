/* ================================================================
   PayloadForge — app.js
   Frontend logic for the Encoder & Obfuscation Framework UI
   ================================================================ */

const API = "http://localhost:5000/api";

/* ─── Utility helpers ─── */
function $(id) { return document.getElementById(id); }

function showLoading(msg = "Processing...") {
  $("loader-text").textContent = msg;
  $("loading-overlay").style.display = "flex";
}
function hideLoading() { $("loading-overlay").style.display = "none"; }

function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  $("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

async function apiFetch(endpoint, body) {
  const res = await fetch(API + endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function apiGet(endpoint) {
  const res = await fetch(API + endpoint);
  return res.json();
}

function copyText(text, label = "Copied") {
  navigator.clipboard.writeText(text).then(() => toast(`✓ ${label} to clipboard`, "success"));
}

function severityBadge(sev) {
  const cls = { CRITICAL: "badge-critical", HIGH: "badge-high", MEDIUM: "badge-medium", LOW: "badge-low" };
  return `<span class="badge ${cls[sev] || 'badge-low'}">${sev}</span>`;
}

function verdictBadge(v) {
  return v === "BYPASSED"
    ? `<span class="badge badge-bypassed">✓ Bypassed</span>`
    : `<span class="badge badge-detected">✗ Detected</span>`;
}

function entropyClass(label) {
  return { LOW: "entropy-low", MEDIUM: "entropy-medium", HIGH: "entropy-high", "VERY HIGH": "entropy-very-high" }[label] || "entropy-low";
}

function progressBar(pct, cls = "fill-red") {
  return `<div class="progress-bar-wrap">
    <div class="progress-bar-fill ${cls}" style="width:${pct}%"></div>
  </div>`;
}

/* ─── Tab switching ─── */
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    $("panel-" + btn.dataset.tab).classList.add("active");

    // Auto-load reports when switching to that tab
    if (btn.dataset.tab === "reports") loadReports();
  });
});

/* ─── Disclaimer ─── */
$("disclaimerToggle").addEventListener("click", () => {
  $("disclaimerBanner").classList.toggle("hidden");
});
$("disclaimerClose").addEventListener("click", () => {
  $("disclaimerBanner").classList.add("hidden");
});

/* ================================================================
   ENCODER TAB
   ================================================================ */

// Method card selection
let selectedMethod = "base64";
document.querySelectorAll(".method-card").forEach(card => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".method-card").forEach(c => c.classList.remove("selected"));
    card.classList.add("selected");
    selectedMethod = card.dataset.method;
    $("xor-options").style.display = selectedMethod === "xor" ? "block" : "none";
  });
});

// Layer chip toggle (encoder tab)
let encLayers = [];
document.querySelectorAll("#layer-chain .layer-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("selected");
    const layer = chip.dataset.layer;
    if (chip.classList.contains("selected")) {
      if (!encLayers.includes(layer)) encLayers.push(layer);
    } else {
      encLayers = encLayers.filter(l => l !== layer);
    }
  });
  if (chip.classList.contains("selected")) encLayers.push(chip.dataset.layer);
});

// Pipeline layer chips
let pipeLayers = ["base64", "xor"];
document.querySelectorAll("#pipe-layer-chain .layer-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("selected");
    const layer = chip.dataset.layer;
    if (chip.classList.contains("selected")) {
      if (!pipeLayers.includes(layer)) pipeLayers.push(layer);
    } else {
      pipeLayers = pipeLayers.filter(l => l !== layer);
    }
  });
});

// Copy button
let lastEncoded = "";
$("enc-copy-btn").addEventListener("click", () => copyText(lastEncoded, "Encoded output"));

/* Single encode */
$("enc-single-btn").addEventListener("click", async () => {
  const payload = $("enc-payload").value.trim();
  if (!payload) { toast("Please enter a payload first", "error"); return; }

  showLoading(`Encoding with ${selectedMethod.toUpperCase()}...`);
  try {
    const data = await apiFetch("/encode", {
      payload,
      method: selectedMethod,
      xor_key: $("xor-key").value || "K3Y",
    });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderEncoderResult(data.result);
    toast("✓ Encoded successfully", "success");
  } catch (e) {
    hideLoading();
    toast("Connection error — is the server running?", "error");
  }
});

/* Multi-layer encode */
$("enc-multi-btn").addEventListener("click", async () => {
  const payload = $("enc-payload").value.trim();
  if (!payload) { toast("Please enter a payload first", "error"); return; }
  if (encLayers.length === 0) { toast("Select at least one layer", "error"); return; }

  showLoading("Applying multi-layer encoding...");
  try {
    const data = await apiFetch("/encode/multi", {
      payload,
      layers: encLayers,
      xor_key: $("xor-key").value || "K3Y",
    });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderMultiLayerResult(data.result);
    toast(`✓ ${encLayers.length} layers applied`, "success");
  } catch (e) {
    hideLoading();
    toast("Connection error — is the server running?", "error");
  }
});

/* Decode */
$("enc-decode-btn").addEventListener("click", async () => {
  const encoded = $("enc-payload").value.trim();
  if (!encoded) { toast("Enter encoded text to decode", "error"); return; }

  showLoading("Decoding...");
  try {
    const data = await apiFetch("/decode", {
      encoded,
      method: selectedMethod,
      xor_key: $("xor-key").value || "K3Y",
    });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    lastEncoded = data.decoded;
    $("enc-output-area").innerHTML = `
      <div style="margin-bottom:10px">
        <span class="badge badge-bypassed" style="margin-bottom:8px; display:inline-block">↩ Decoded</span>
        <span style="font-size:0.78rem; color:var(--text-muted); margin-left:8px">${data.method.toUpperCase()} → Plain Text</span>
      </div>
      <div class="result-box">${escHtml(data.decoded)}</div>`;
    toast("✓ Decoded successfully", "success");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

function renderEncoderResult(r) {
  lastEncoded = r.encoded;
  const sizeColor = r.size_increase > 0 ? "orange" : "green";
  $("enc-output-area").innerHTML = `
    <div style="margin-bottom:14px">
      <span class="badge badge-bypassed" style="display:inline-block; margin-bottom:6px">✓ ${r.method} Encoded</span>
    </div>
    <label class="field-label">Encoded Output</label>
    <div class="result-box">${escHtml(r.encoded)}</div>
    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-label">Original Length</div>
        <div class="meta-value cyan">${r.original_length} B</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Encoded Length</div>
        <div class="meta-value">${r.encoded_length} B</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Size Increase</div>
        <div class="meta-value ${sizeColor}">${r.size_increase > 0 ? "+" : ""}${r.size_increase}%</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Reversible</div>
        <div class="meta-value green">${r.reversible ? "Yes ✓" : "No"}</div>
      </div>
      ${r.key ? `<div class="meta-item"><div class="meta-label">XOR Key</div><div class="meta-value pink">${escHtml(r.key)}</div></div>` : ""}
    </div>
    ${r.decode_cmd ? `<div style="margin-top:14px"><label class="field-label">Decode Command</label>
      <div class="result-box" style="color:var(--accent-cyan)">${escHtml(r.decode_cmd)}</div></div>` : ""}`;
}

function renderMultiLayerResult(r) {
  lastEncoded = r.encoded;
  const stepsHtml = r.steps.map((s, i) => `
    <div class="step-item">
      <div class="step-num">${i + 1}</div>
      <div class="step-content">
        <div class="step-label">${s.layer.toUpperCase()} Encoding</div>
        <div class="step-value">${escHtml(s.output)}</div>
      </div>
    </div>`).join("");

  $("enc-output-area").innerHTML = `
    <div style="margin-bottom:14px">
      <span class="badge badge-bypassed" style="display:inline-block; margin-bottom:6px">✓ Multi-Layer: ${r.layers.join(" → ")}</span>
    </div>
    <label class="field-label">Final Encoded Output</label>
    <div class="result-box">${escHtml(r.encoded)}</div>
    <div class="meta-grid">
      <div class="meta-item"><div class="meta-label">Original</div><div class="meta-value cyan">${r.original_length} B</div></div>
      <div class="meta-item"><div class="meta-label">Final</div><div class="meta-value">${r.encoded_length} B</div></div>
      <div class="meta-item"><div class="meta-label">Layers</div><div class="meta-value pink">${r.layers.length}</div></div>
      <div class="meta-item"><div class="meta-label">Size Change</div><div class="meta-value orange">${r.size_increase > 0 ? "+" : ""}${r.size_increase}%</div></div>
    </div>
    <div class="steps-timeline" style="margin-top:20px">
      <div class="section-divider"><span>Encoding Steps</span></div>
      ${stepsHtml}
    </div>`;
}

/* ================================================================
   OBFUSCATOR TAB
   ================================================================ */
let lastObfuscated = "";
$("obf-copy-btn").addEventListener("click", () => copyText(lastObfuscated, "Obfuscated output"));

$("obf-single-btn").addEventListener("click", async () => {
  const payload = $("obf-payload").value.trim();
  if (!payload) { toast("Please enter a payload", "error"); return; }

  const technique = $("obf-technique").value;
  showLoading("Applying obfuscation...");
  try {
    const data = await apiFetch("/obfuscate", { payload, technique });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderObfuscationResult(data.result);
    $("obf-all-card").style.display = "none";
    toast(`✓ ${data.result.technique} applied`, "success");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

$("obf-all-btn").addEventListener("click", async () => {
  const payload = $("obf-payload").value.trim();
  if (!payload) { toast("Please enter a payload", "error"); return; }

  showLoading("Applying all obfuscation techniques...");
  try {
    const data = await apiFetch("/obfuscate/all", { payload });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderAllObfuscations(data.results);
    toast(`✓ ${data.count} techniques applied`, "success");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

function renderObfuscationResult(r) {
  lastObfuscated = r.obfuscated || "";
  const ratio = r.original_length > 0
    ? Math.round((r.obfuscated_length / r.original_length) * 100)
    : 100;

  $("obf-output-area").innerHTML = `
    <div style="margin-bottom:12px">
      <span class="badge badge-bypassed" style="display:inline-block">${escHtml(r.technique)}</span>
      ${r.reversible ? '<span style="font-size:0.75rem; color:var(--accent-green); margin-left:10px">↩ Reversible</span>' : '<span style="font-size:0.75rem; color:var(--text-muted); margin-left:10px">⚠ Not reversible</span>'}
    </div>

    <label class="field-label">Original</label>
    <div class="result-box" style="color:var(--text-secondary); max-height:80px">${escHtml(r.original)}</div>

    <label class="field-label" style="margin-top:14px">Obfuscated Output</label>
    <div class="result-box">${escHtml(r.obfuscated)}</div>

    <div class="meta-grid" style="margin-top:14px">
      <div class="meta-item"><div class="meta-label">Original</div><div class="meta-value cyan">${r.original_length} B</div></div>
      <div class="meta-item"><div class="meta-label">Obfuscated</div><div class="meta-value orange">${r.obfuscated_length} B</div></div>
      <div class="meta-item"><div class="meta-label">Size Ratio</div><div class="meta-value">${ratio}%</div></div>
    </div>

    ${r.reverse_note ? `<div style="margin-top:14px; padding:12px; background:rgba(0,204,255,0.05); border:1px solid rgba(0,204,255,0.15); border-radius:6px; font-size:0.8rem; color:var(--accent-cyan)">
      <strong>↩ Reversal:</strong> ${escHtml(r.reverse_note)}</div>` : ""}

    ${r.mapping && Object.keys(r.mapping).length > 0 ? `
    <div style="margin-top:14px">
      <label class="field-label">Substitution Map</label>
      <div class="result-box" style="font-size:0.78rem">${
        Object.entries(r.mapping).map(([k,v]) => `${escHtml(k)} → "${escHtml(v)}"`).join("\n")
      }</div>
    </div>` : ""}`;
}

function renderAllObfuscations(results) {
  $("obf-output-area").innerHTML = `<div class="empty-state" style="padding:20px">
    <p>All techniques applied — see table below ↓</p></div>`;

  const rows = results.map(r => {
    const obf = r.obfuscated || r.error || "";
    return `<div class="obf-row">
      <div class="obf-row-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
        <span class="obf-row-title">${escHtml(r.technique || "Unknown")}</span>
        <span class="obf-row-meta">${r.obfuscated_length || "?"} B ${r.reversible ? "· Reversible ✓" : "· Not reversible"}</span>
      </div>
      <div class="obf-row-body" style="display:none">${escHtml(obf)}</div>
    </div>`;
  }).join("");

  $("obf-all-table").innerHTML = rows;
  $("obf-all-card").style.display = "block";
  toast(`✓ ${results.length} techniques shown — click each to expand`, "info");
}

/* ================================================================
   EVASION TESTING TAB
   ================================================================ */
$("ev-scan-btn").addEventListener("click", async () => {
  const payload = $("ev-payload").value.trim();
  if (!payload) { toast("Enter a payload to scan", "error"); return; }

  showLoading("Running signature scan...");
  try {
    const data = await apiFetch("/scan", { payload });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderScanResult(data.result);
    $("ev-scan-card").style.display = "block";
    toast(`Scan complete — ${data.result.verdict}`, data.result.detected ? "error" : "success");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

$("ev-full-btn").addEventListener("click", async () => {
  const payload = $("ev-payload").value.trim();
  if (!payload) { toast("Enter a payload to test", "error"); return; }

  showLoading("Running full evasion test suite...");
  try {
    const data = await apiFetch("/evasion-test", {
      payload,
      xor_key: $("ev-xor-key").value || "K3Y",
    });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderEvasionTest(data.evasion);
    $("ev-full-card").style.display = "block";
    toast(`✓ Evasion test complete — ${data.evasion.summary.bypass_rate}% bypass rate`, "info");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

function renderScanResult(r) {
  const verdictClass = r.detected ? "verdict-detected" : "verdict-bypassed";
  const verdictIcon = r.detected ? "🚨" : "✅";
  const detRate = r.detection_rate;
  const fillCls = detRate > 60 ? "fill-red" : detRate > 30 ? "fill-orange" : detRate > 10 ? "fill-yellow" : "fill-green";

  const matchedRows = r.signatures_matched.map(s => `
    <tr>
      <td>${escHtml(s.signature_id)}</td>
      <td>${severityBadge(s.severity)}</td>
      <td style="color:var(--accent-red)">${escHtml(s.match)}</td>
      <td style="color:var(--text-muted)">${s.position}</td>
    </tr>`).join("");

  $("ev-scan-result").innerHTML = `
    <div class="verdict-banner ${verdictClass}">
      <span style="font-size:1.8rem">${verdictIcon}</span>
      <div>
        <div style="font-size:1.1rem">${r.verdict}</div>
        <div style="font-size:0.8rem; font-weight:400; opacity:0.8">${r.match_count} of ${r.total_signatures} signatures matched</div>
      </div>
    </div>

    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-label">Detection Rate</div>
        <div class="meta-value ${r.detected ? 'red' : 'green'}">${detRate}%</div>
        ${progressBar(detRate, fillCls)}
      </div>
      <div class="meta-item">
        <div class="meta-label">Signatures Hit</div>
        <div class="meta-value orange">${r.match_count}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Payload Length</div>
        <div class="meta-value cyan">${r.payload_length} B</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Entropy</div>
        <div class="meta-value">${r.entropy.value}</div>
      </div>
    </div>

    <div class="entropy-display ${entropyClass(r.entropy.label)}" style="margin:16px 0">
      Entropy: ${r.entropy.value} — <strong>${r.entropy.label}</strong> — ${r.entropy.note}
    </div>

    ${r.signatures_matched.length > 0 ? `
    <div style="margin-top:20px">
      <div class="section-divider"><span>Matched Signatures (${r.signatures_matched.length})</span></div>
      <div style="overflow-x:auto">
        <table class="sig-table">
          <thead><tr><th>Signature ID</th><th>Severity</th><th>Match</th><th>Position</th></tr></thead>
          <tbody>${matchedRows}</tbody>
        </table>
      </div>
    </div>` : `<div style="margin-top:16px; padding:12px 16px; background:rgba(0,255,136,0.06); border:1px solid rgba(0,255,136,0.2); border-radius:6px; color:var(--accent-green); font-size:0.85rem">
      ✓ No signatures matched — payload successfully bypassed static detection</div>`}`;
}

function renderEvasionTest(ev) {
  const orig = ev.original;
  const summ = ev.summary;
  const bypassFill = summ.bypass_rate > 60 ? "fill-green" : summ.bypass_rate > 30 ? "fill-yellow" : "fill-orange";

  const rowsHtml = ev.transformations.map(t => {
    const impColor = t.evasion_improvement > 0 ? "var(--accent-green)" : t.evasion_improvement < 0 ? "var(--accent-red)" : "var(--text-muted)";
    return `<div class="evasion-row ${t.detected ? 'row-detected' : 'row-bypassed'}">
      <div style="font-weight:600; font-size:0.83rem">${escHtml(t.label)}</div>
      <div>${verdictBadge(t.verdict)}</div>
      <div style="font-family:var(--font-mono)">${t.detection_rate}%</div>
      <div style="color:${impColor}; font-family:var(--font-mono)">${t.evasion_improvement > 0 ? "+" : ""}${t.evasion_improvement}%</div>
      <div><span class="badge ${entropyClass(t.entropy.label).replace('entropy-','badge-') || ''}" style="font-size:0.65rem">${t.entropy.label}</span></div>
    </div>`;
  }).join("");

  $("ev-full-result").innerHTML = `
    <!-- Summary cards -->
    <div class="meta-grid" style="margin-bottom:20px">
      <div class="meta-item">
        <div class="meta-label">Overall Bypass Rate</div>
        <div class="meta-value green" style="font-size:1.6rem">${summ.bypass_rate}%</div>
        ${progressBar(summ.bypass_rate, bypassFill)}
      </div>
      <div class="meta-item">
        <div class="meta-label">Variants Tested</div>
        <div class="meta-value cyan">${summ.total_tested}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Bypassed Detection</div>
        <div class="meta-value green">${summ.bypassed}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Still Detected</div>
        <div class="meta-value red">${summ.detected}</div>
      </div>
      <div class="meta-item" style="grid-column: span 2">
        <div class="meta-label">Most Effective Technique</div>
        <div class="meta-value pink" style="font-size:0.88rem">${escHtml(summ.most_effective)}</div>
      </div>
    </div>

    <!-- Original vs results -->
    <div class="section-divider"><span>Original Payload Baseline</span></div>
    <div style="padding:12px; background:rgba(255,51,85,0.06); border:1px solid rgba(255,51,85,0.2); border-radius:8px; margin-bottom:16px">
      <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap">
        ${verdictBadge(orig.verdict)}
        <span style="font-family:var(--font-mono); font-size:0.82rem; color:var(--text-muted)">Detection Rate: <strong style="color:var(--accent-red)">${orig.detection_rate}%</strong></span>
        <span style="font-family:var(--font-mono); font-size:0.82rem; color:var(--text-muted)">Entropy: <strong>${orig.entropy.value}</strong> (${orig.entropy.label})</span>
      </div>
    </div>

    <div class="section-divider"><span>Transformation Results</span></div>
    <div class="evasion-row evasion-row-header" style="font-weight:700; cursor:default">
      <div>Technique</div><div>Verdict</div><div>Det. Rate</div><div>Improvement</div><div>Entropy</div>
    </div>
    ${rowsHtml}`;
}

/* ================================================================
   FULL PIPELINE TAB
   ================================================================ */
$("pipe-run-btn").addEventListener("click", async () => {
  const payload = $("pipe-payload").value.trim();
  if (!payload) { toast("Enter a payload to run through the pipeline", "error"); return; }

  showLoading("Running full analysis pipeline...");
  try {
    const data = await apiFetch("/full-pipeline", {
      payload,
      xor_key: $("pipe-xor-key").value || "K3Y",
      layers: pipeLayers,
    });
    hideLoading();
    if (!data.success) { toast(data.error, "error"); return; }
    renderPipelineResults(data.session, data.report);
    toast("✓ Full pipeline complete — report generated", "success");
  } catch (e) {
    hideLoading();
    toast("Connection error", "error");
  }
});

function renderPipelineResults(session, report) {
  const orig = session.original_scan;
  const evasion = session.evasion;
  const summ = evasion.summary;

  const encRows = (session.encodings || []).map(e => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:9px 12px; border:1px solid var(--border); border-radius:6px; margin-bottom:8px">
      <span style="font-weight:600; font-size:0.85rem">${e.method}</span>
      <span style="font-family:var(--font-mono); font-size:0.78rem; color:var(--text-muted); flex:1; margin:0 16px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis">${escHtml(e.encoded)}</span>
      <span style="font-size:0.75rem; color:var(--accent-cyan)">${e.encoded_length}B</span>
    </div>`).join("");

  const obfRows = (session.obfuscations || []).map(o => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:9px 12px; border:1px solid var(--border); border-radius:6px; margin-bottom:8px">
      <span style="font-weight:600; font-size:0.82rem; flex:0 0 220px">${escHtml(o.technique)}</span>
      <span style="font-family:var(--font-mono); font-size:0.78rem; color:var(--text-muted); flex:1; margin:0 12px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis">${escHtml(o.obfuscated || "")}</span>
      <span style="font-size:0.75rem; color:${o.reversible ? 'var(--accent-green)' : 'var(--text-muted)'}">${o.reversible ? '↩' : '—'}</span>
    </div>`).join("");

  $("pipe-results").style.display = "block";
  $("pipe-results").innerHTML = `
    <!-- Step 1: Original scan -->
    <div class="card pipeline-section" style="margin-top:24px">
      <div class="card-header">📋 Step 1 — Original Payload Analysis</div>
      <div class="card-body">
        <div class="verdict-banner ${orig.detected ? 'verdict-detected' : 'verdict-bypassed'}">
          <span style="font-size:1.5rem">${orig.detected ? '🚨' : '✅'}</span>
          <div>
            <div>${orig.verdict}</div>
            <div style="font-size:0.78rem; font-weight:400">${orig.match_count} signatures matched · Entropy ${orig.entropy.value} (${orig.entropy.label})</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Encodings -->
    <div class="card pipeline-section" style="margin-top:16px">
      <div class="card-header">🔐 Step 2 — Encoding Results</div>
      <div class="card-body">${encRows}</div>
    </div>

    <!-- Step 3: Obfuscations -->
    <div class="card pipeline-section" style="margin-top:16px">
      <div class="card-header">🌀 Step 3 — Obfuscation Results</div>
      <div class="card-body">${obfRows}</div>
    </div>

    <!-- Step 4: Evasion -->
    <div class="card pipeline-section" style="margin-top:16px">
      <div class="card-header">🎯 Step 4 — Evasion Test Summary</div>
      <div class="card-body">
        <div class="meta-grid">
          <div class="meta-item"><div class="meta-label">Bypass Rate</div><div class="meta-value green" style="font-size:1.5rem">${summ.bypass_rate}%</div>${progressBar(summ.bypass_rate, "fill-green")}</div>
          <div class="meta-item"><div class="meta-label">Tested</div><div class="meta-value cyan">${summ.total_tested}</div></div>
          <div class="meta-item"><div class="meta-label">Bypassed</div><div class="meta-value green">${summ.bypassed}</div></div>
          <div class="meta-item"><div class="meta-label">Detected</div><div class="meta-value red">${summ.detected}</div></div>
          <div class="meta-item" style="grid-column:span 2"><div class="meta-label">Most Effective</div><div class="meta-value pink">${escHtml(summ.most_effective)}</div></div>
        </div>
      </div>
    </div>

    <!-- Step 5: Report -->
    <div class="card pipeline-section" style="margin-top:16px">
      <div class="card-header">📊 Step 5 — Report Generated</div>
      <div class="card-body">
        <div style="display:flex; gap:20px; align-items:center; flex-wrap:wrap">
          <div>
            <div class="meta-label">Report ID</div>
            <div class="meta-value" style="font-family:var(--font-mono)">${report.report_id}</div>
          </div>
          <div>
            <div class="meta-label">Generated At</div>
            <div style="font-family:var(--font-mono); font-size:0.82rem; color:var(--text-secondary)">${report.generated_at}</div>
          </div>
          <div>
            <div class="meta-label">File Size</div>
            <div style="font-family:var(--font-mono); font-size:0.82rem; color:var(--text-secondary)">${(report.size_bytes / 1024).toFixed(1)} KB</div>
          </div>
          <button class="btn btn-ghost btn-sm" onclick="switchToReports()">📊 View in Reports Tab →</button>
        </div>
      </div>
    </div>`;
}

function switchToReports() {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  $("tab-reports").classList.add("active");
  $("panel-reports").classList.add("active");
  loadReports();
}

/* ================================================================
   REPORTS TAB
   ================================================================ */
async function loadReports() {
  try {
    const data = await apiGet("/reports");
    if (!data.success || data.reports.length === 0) {
      $("reports-list").innerHTML = `<div class="empty-state"><div class="empty-icon">📊</div><p>No reports yet. Run the Full Pipeline to generate one.</p></div>`;
      return;
    }

    $("reports-list").innerHTML = data.reports.map(r => {
      const id = r.filename.split("_")[1];
      const date = r.modified ? new Date(r.modified).toLocaleString() : "Unknown";
      return `<div class="report-item" onclick="viewReport('${id}')">
        <div class="report-icon">📄</div>
        <div class="report-info">
          <div class="report-name">${r.filename}</div>
          <div class="report-meta">${date} · ${(r.size_bytes / 1024).toFixed(1)} KB</div>
        </div>
        <button class="btn btn-ghost btn-sm report-view-btn">View →</button>
      </div>`;
    }).join("");
  } catch (e) {
    $("reports-list").innerHTML = `<div class="empty-state"><p style="color:var(--accent-red)">Could not load reports — is the server running?</p></div>`;
  }
}

async function viewReport(id) {
  showLoading("Loading report...");
  try {
    const data = await apiGet(`/reports/${id}`);
    hideLoading();
    if (!data.success) { toast("Report not found", "error"); return; }
    renderReportViewer(data.report);
    $("report-viewer-card").style.display = "block";
    $("report-viewer-card").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    hideLoading();
    toast("Could not load report", "error");
  }
}

function renderReportViewer(r) {
  const summ = r.analysis_summary || {};
  const recs = summ.recommendations || [];

  const recHtml = recs.map(rec => {
    const cls = `rec-${(rec.priority || "low").toLowerCase()}`;
    const pCls = `badge-${(rec.priority || "low").toLowerCase()}`;
    return `<div class="rec-item ${cls}">
      <span class="badge ${pCls} rec-priority">${rec.priority}</span>
      <span>${escHtml(rec.recommendation)}</span>
    </div>`;
  }).join("");

  $("report-viewer-body").innerHTML = `
    <div class="report-section">
      <div class="report-section-title">Report Metadata</div>
      <div class="meta-grid">
        <div class="meta-item"><div class="meta-label">Report ID</div><div class="meta-value" style="font-family:var(--font-mono)">${r.report_id}</div></div>
        <div class="meta-item"><div class="meta-label">Generated</div><div style="font-size:0.82rem; color:var(--text-secondary)">${r.generated_at}</div></div>
        <div class="meta-item"><div class="meta-label">Framework</div><div style="font-size:0.8rem; color:var(--text-secondary)">${r.framework}</div></div>
      </div>
    </div>

    <div class="report-section">
      <div class="report-section-title">Analysis Summary</div>
      <div class="meta-grid">
        ${summ.original_detection_rate !== undefined ? `<div class="meta-item"><div class="meta-label">Original Detection</div><div class="meta-value red">${summ.original_detection_rate}%</div></div>` : ""}
        ${summ.bypass_rate !== undefined ? `<div class="meta-item"><div class="meta-label">Bypass Rate</div><div class="meta-value green">${summ.bypass_rate}%</div></div>` : ""}
        ${summ.transformations_tested !== undefined ? `<div class="meta-item"><div class="meta-label">Tested</div><div class="meta-value cyan">${summ.transformations_tested}</div></div>` : ""}
        ${summ.most_effective_technique ? `<div class="meta-item"><div class="meta-label">Best Technique</div><div class="meta-value pink" style="font-size:0.8rem">${escHtml(summ.most_effective_technique)}</div></div>` : ""}
      </div>
    </div>

    ${recHtml ? `<div class="report-section"><div class="report-section-title">Defensive Recommendations</div>${recHtml}</div>` : ""}

    <div class="report-section">
      <div class="report-section-title">Full JSON Report</div>
      <div class="report-json">${escHtml(JSON.stringify(r, null, 2))}</div>
    </div>

    <div style="margin-top:16px">
      <button class="btn btn-secondary btn-sm" onclick="downloadReportJson('${r.report_id}')">⬇ Download JSON</button>
    </div>`;
}

function downloadReportJson(id) {
  apiGet(`/reports/${id}`).then(data => {
    if (!data.success) return;
    const blob = new Blob([JSON.stringify(data.report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `report_${id}.json`; a.click();
    URL.revokeObjectURL(url);
    toast("✓ Report downloaded", "success");
  });
}

$("close-report-btn").addEventListener("click", () => {
  $("report-viewer-card").style.display = "none";
});

$("refresh-reports-btn").addEventListener("click", () => {
  loadReports();
  toast("Reports refreshed", "info");
});

/* ================================================================
   Helpers
   ================================================================ */
function escHtml(str) {
  if (typeof str !== "string") str = String(str ?? "");
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* Init */
loadReports();
