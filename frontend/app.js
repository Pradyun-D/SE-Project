const API_BASE = 'http://127.0.0.1:8000';

const $ = (selector) => document.querySelector(selector);
const form = $('#generationForm');
const generateButton = $('#generateButton');
const ingestButton = $('#ingestButton');
const latestButton = $('#latestButton');
const formStatus = $('#formStatus');
const resultsSection = $('#resultsSection');

function setBusy(button, busy, idleLabel, busyLabel) {
  button.disabled = busy;
  const label = button.querySelector('span:first-child');
  if (label) label.textContent = busy ? busyLabel : idleLabel;
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  let payload = {};
  try { payload = await response.json(); } catch (_) { /* Empty error bodies are handled below. */ }
  if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status})`);
  return payload;
}

async function checkHealth() {
  try {
    await api('/health');
    $('#indexState').textContent = 'Ready to analyse';
    $('#indexDetail').textContent = 'Enter a scenario and start the analysis.';
  } catch (error) {
    $('#indexState').textContent = 'Start the API';
    $('#indexDetail').textContent = 'Run uvicorn api.main:app --reload from the backend directory.';
  }
}

const analysisSteps = ['requirements', 'quality', 'sdlc', 'approval', 'document'];
let stepTimer;

function setAnalysisStep(step, state) {
  const element = document.querySelector(`[data-step="${step}"]`);
  if (!element) return;
  element.classList.remove('active', 'complete');
  if (state !== 'waiting') element.classList.add(state);
  element.querySelector('.step-state').textContent = state === 'active' ? 'Working' : state === 'complete' ? 'Done' : 'Waiting';
}

function startAnalysisSteps() {
  clearInterval(stepTimer);
  analysisSteps.forEach((step) => setAnalysisStep(step, 'waiting'));
  formStatus.textContent = 'Analysis queued...';
}

function finishAnalysisSteps(success) {
  clearInterval(stepTimer);
  analysisSteps.forEach((step) => setAnalysisStep(step, success ? 'complete' : 'waiting'));
  $('#indexState').textContent = success ? 'Analysis complete' : 'Analysis stopped';
  $('#indexDetail').textContent = success ? 'Review the findings below.' : 'Check the message below and try again.';
}

function updateAnalysisProgress(job) {
  const currentIndex = analysisSteps.indexOf(job.step);
  analysisSteps.forEach((step, index) => {
    setAnalysisStep(step, index < currentIndex ? 'complete' : index === currentIndex ? 'active' : 'waiting');
  });
  $('#indexState').textContent = job.message || 'Analysis running';
  $('#indexDetail').textContent = 'The workflow is progressing through the selected steps.';
  formStatus.textContent = job.message || 'Analysis is running...';
}

async function waitForGeneration(jobId) {
  while (true) {
    const job = await api(`/generate/status/${jobId}`);
    if (job.status === 'failed') throw new Error(job.message || 'Generation failed');
    if (job.status === 'completed') return job.result;
    updateAnalysisProgress(job);
    await new Promise((resolve) => setTimeout(resolve, 800));
  }
}

function renderResult(result) {
  const output = $('#srsOutput');
  const meta = $('#resultMeta');
  if (!output || !meta) throw new Error('The page is using an outdated frontend. Refresh with Ctrl+F5.');
  output.innerHTML = renderMarkdown(result.response || 'No final document returned.');
  meta.textContent = `${result.sources?.length || 0} sources / ${result.extracted_requirements?.length || 0} requirements`;
  resultsSection.hidden = false;
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderSavedResponse(response, filename, shouldScroll = true) {
  const output = $('#srsOutput');
  const meta = $('#resultMeta');
  if (!output || !meta) throw new Error('The page is using an outdated frontend. Refresh with Ctrl+F5.');
  output.innerHTML = renderMarkdown(response);
  meta.textContent = `Saved document: ${filename}`;
  resultsSection.hidden = false;
  if (shouldScroll) resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const output = [];
  let listType = null;
  let codeOpen = false;
  let paragraph = [];
  const closeList = () => { if (listType) { output.push(`</${listType}>`); listType = null; } };
  const closeParagraph = () => {
    if (paragraph.length) {
      output.push(`<p>${inlineMarkdown(escapeHtml(paragraph.join(' ')))}</p>`);
      paragraph = [];
    }
  };
  const closeBlocks = () => { closeList(); closeParagraph(); };

  for (let index = 0; index < lines.length; index += 1) {
    const rawLine = lines[index];
    const line = rawLine.trimEnd();
    if (line.trim().startsWith('```')) {
      closeBlocks();
      closeList();
      if (codeOpen) { output.push('</code></pre>'); codeOpen = false; } else { output.push('<pre class="code-block"><code>'); codeOpen = true; }
      continue;
    }
    if (codeOpen) { output.push(`${escapeHtml(line)}\n`); continue; }
    if (!line.trim()) { closeBlocks(); continue; }

    if (isTableRow(line) && isTableSeparator(lines[index + 1] || '')) {
      closeBlocks();
      const headers = splitTableRow(line);
      const rows = [];
      index += 2;
      while (index < lines.length && isTableRow(lines[index])) {
        rows.push(splitTableRow(lines[index]));
        index += 1;
      }
      index -= 1;
      output.push(`<div class="table-wrap"><table><thead><tr>${headers.map((cell) => `<th>${inlineMarkdown(escapeHtml(cell))}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${headers.map((_, cellIndex) => `<td>${inlineMarkdown(escapeHtml(row[cellIndex] || ''))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
      continue;
    }

    const heading = line.match(/^\s*(#{1,6})\s+(.+)$/);
    if (heading) { closeBlocks(); const level = Math.min(Number(heading[1].length) + 1, 6); output.push(`<h${level}>${inlineMarkdown(escapeHtml(heading[2]))}</h${level}>`); continue; }
    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      closeParagraph();
      const nextType = unordered ? 'ul' : 'ol';
      if (listType !== nextType) { closeList(); output.push(`<${nextType}>`); listType = nextType; }
      output.push(`<li>${inlineMarkdown(escapeHtml((unordered || ordered)[1]))}</li>`);
      continue;
    }

    const quote = line.match(/^\s*>\s?(.*)$/);
    if (quote) { closeBlocks(); output.push(`<blockquote>${inlineMarkdown(escapeHtml(quote[1]))}</blockquote>`); continue; }
    closeList();
    if (/^\s*---+\s*$/.test(line)) { closeParagraph(); output.push('<hr>'); continue; }
    paragraph.push(line.trim());
  }
  closeBlocks();
  if (codeOpen) output.push('</code></pre>');
  return output.join('');
}

function isTableRow(line) {
  return line.trim().startsWith('|') && line.trim().endsWith('|');
}

function isTableSeparator(line) {
  return isTableRow(line) && splitTableRow(line).every((cell) => /^:?-{3,}:?$/.test(cell.trim()));
}

function splitTableRow(line) {
  return line.trim().slice(1, -1).split('|').map((cell) => cell.trim());
}

function inlineMarkdown(value) {
  return value.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`(.*?)`/g, '<code>$1</code>');
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[character]));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const scenario = $('#scenario').value.trim();
  if (!scenario) return;
  setBusy(generateButton, true, 'Generate requirements', 'Running agents...');
  startAnalysisSteps();
  formStatus.textContent = 'Extracting requirements, reviewing quality, and selecting an SDLC...';
  try {
    const job = await api('/generate/async', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        minimal_requirement: scenario,
        scale: $('#scale').value,
        use_rag: $('#useRag').checked,
        human_approved: $('#approved').checked,
        max_new_tokens: 4096,
        temperature: Number($('#temperature').value),
        top_p: 0.95,
      }),
    });
    const result = await waitForGeneration(job.job_id);
    renderResult(result);
    finishAnalysisSteps(true);
    formStatus.textContent = 'Analysis complete. The generated files were saved by the backend.';
  } catch (error) {
    finishAnalysisSteps(false);
    formStatus.textContent = error.message;
  } finally {
    setBusy(generateButton, false, 'Generate requirements', 'Running agents...');
  }
});

ingestButton.addEventListener('click', async () => {
  setBusy(ingestButton, true, 'Refresh document index', 'Refreshing...');
  try {
    const result = await api('/ingest');
    $('#indexState').textContent = `${result.documents} documents indexed`;
    $('#indexDetail').textContent = `${result.chunks} cached chunks are ready for regulatory retrieval.`;
    formStatus.textContent = 'Document index is ready.';
  } catch (error) {
    formStatus.textContent = error.message;
  } finally {
    setBusy(ingestButton, false, 'Refresh document index', 'Refreshing...');
  }
});

$('#copyButton').addEventListener('click', async () => {
  await navigator.clipboard.writeText($('#srsOutput').textContent);
  $('#copyButton').textContent = 'Copied';
  setTimeout(() => { $('#copyButton').textContent = 'Copy document'; }, 1400);
});

latestButton?.addEventListener('click', async () => {
  setBusy(latestButton, true, 'Load latest document', 'Loading...');
  try {
    const saved = await api('/responses/latest');
    renderSavedResponse(saved.response, saved.filename, false);
    formStatus.textContent = `${saved.filename} loaded.`;
  } catch (error) {
    formStatus.textContent = error.message;
  } finally {
    setBusy(latestButton, false, 'Load latest document', 'Loading...');
  }
});

async function loadLatestIfAvailable() {
  try {
    const saved = await api('/responses/latest');
    renderSavedResponse(saved.response, saved.filename);
    formStatus.textContent = `${saved.filename} loaded.`;
  } catch (_) {
    // No saved document exists on a first run.
  }
}

checkHealth();
loadLatestIfAvailable();
