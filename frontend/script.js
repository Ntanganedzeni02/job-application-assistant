
    const api = () => "https://job-application-assistant-7vnq.onrender.com";

    function switchTab(name) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(`panel-${name}`).classList.add('active');
    }

    function setLoading(id, loading) {
      const btn = document.getElementById(`btn-${id}`);
      const txt = document.getElementById(`btn-${id}-text`);
      btn.disabled = loading;
      txt.innerHTML = loading
        ? '<div class="spinner"></div> Processing...'
        : { analyze: 'Analyze CV', match: 'Check Match', improve: 'Improve CV + Generate Cover Letter' }[id];
    }

    function showError(id, msg) {
      const el = document.getElementById(`err-${id}`);
      el.textContent = `Error: ${msg}`;
      el.classList.add('show');
    }
    function hideError(id) {
      document.getElementById(`err-${id}`).classList.remove('show');
    }

    async function callAPI(path, body) {
      const res = await fetch(`${api()}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || res.statusText);
      }
      return res.json();
    }

    // Health ping 

    async function pingHealth() {
      const dot = document.getElementById('apiDot');
      try {
        const res = await fetch(`${api()}/health`);
        dot.classList.toggle('ok', res.ok);
      } catch {
        dot.classList.remove('ok');
      }
    }

    pingHealth();

    // Analyze CV

    async function analyzeCV() {
      const cv = document.getElementById('cv-analyze').value.trim();
      if (!cv) return alert('Please paste your CV first.');
      hideError('analyze');
      setLoading('analyze', true);
      try {
        const d = await callAPI('/analyze/cv', { cv_text: cv });
        const el = document.getElementById('analyze-out');
        el.innerHTML = `
          <div style="margin-bottom:1rem">
            <div style="font-size:1.6rem;font-weight:800;letter-spacing:-0.03em">${d.seniority_level}</div>
            <div style="color:var(--muted);font-size:0.85rem;margin-top:0.2rem">${d.experience_years} experience</div>
          </div>
          <p style="font-size:0.9rem;line-height:1.65;color:#c8cad8;margin-bottom:1.25rem">${d.summary}</p>
          <div class="grid2">
            <div class="mini-card">
              <div class="mini-title">Strengths</div>
              ${d.strengths.map(s => `<div style="font-size:0.83rem;padding:0.2rem 0;color:var(--accent)">✓ ${s}</div>`).join('')}
            </div>
            <div class="mini-card">
              <div class="mini-title">Weaknesses</div>
              ${d.weaknesses.map(w => `<div style="font-size:0.83rem;padding:0.2rem 0;color:#ffd166">⚠ ${w}</div>`).join('')}
            </div>
          </div>
          <div class="mini-card" style="margin-top:1rem">
            <div class="mini-title">Skills Identified</div>
            <div class="chip-list" style="margin-top:0.5rem">
              ${d.skills.map(s => `<span class="chip">${s}</span>`).join('')}
            </div>
          </div>
        `;
        document.getElementById('result-analyze').classList.add('show');
      } catch (e) {
        showError('analyze', e.message);
      } finally {
        setLoading('analyze', false);
      }
    }

    // Match Job

    async function matchJob() {
      const cv = document.getElementById('cv-match').value.trim();
      const jd = document.getElementById('jd-match').value.trim();
      if (!cv || !jd) return alert('Please fill in both fields.');
      hideError('match');
      setLoading('match', true);
      try {
        const d = await callAPI('/analyze/match', { cv_text: cv, job_description: jd });
        const scoreClass = d.match_score >= 70 ? 'high' : d.match_score >= 45 ? 'mid' : 'low';
        document.getElementById('match-out').innerHTML = `
          <div style="display:flex;align-items:flex-end;gap:1rem;margin-bottom:1.25rem">
            <div class="score-big ${scoreClass}">${d.match_score}<span style="font-size:1.5rem">%</span></div>
            <div>
              <div class="${d.qualifies ? 'qualify-badge qualify-yes' : 'qualify-badge qualify-no'}">
                ${d.qualifies ? '✓ You Qualify' : '✗ Underqualified'}
              </div>
              <div style="font-size:0.83rem;color:var(--muted);margin-top:0.4rem">${d.recommendation}</div>
            </div>
          </div>
          <p style="font-size:0.87rem;line-height:1.6;color:#c8cad8;margin-bottom:1.25rem">${d.reasoning}</p>
          <div class="grid2">
            <div class="mini-card">
              <div class="mini-title">Matching Skills</div>
              <div class="chip-list" style="margin-top:0.5rem">
                ${d.matching_skills.map(s => `<span class="chip">${s}</span>`).join('') || '<span style="color:var(--muted);font-size:0.8rem">None found</span>'}
              </div>
            </div>
            <div class="mini-card">
              <div class="mini-title">Missing Skills</div>
              <div class="chip-list" style="margin-top:0.5rem">
                ${d.missing_skills.map(s => `<span class="chip missing">${s}</span>`).join('') || '<span style="color:var(--accent);font-size:0.8rem">None — great fit!</span>'}
              </div>
            </div>
          </div>
        `;
        document.getElementById('result-match').classList.add('show');
      } catch (e) {
        showError('match', e.message);
      } finally {
        setLoading('match', false);
      }
    }

    //Improve CV

    async function improveCV() {
      const cv = document.getElementById('cv-improve').value.trim();
      const jd = document.getElementById('jd-improve').value.trim();
      const tone = document.getElementById('tone-improve').value;
      if (!cv || !jd) return alert('Please fill in both fields.');
      hideError('improve');
      setLoading('improve', true);
      try {
        const d = await callAPI('/analyze/improve', { cv_text: cv, job_description: jd, tone });
        document.getElementById('improve-out').innerHTML = `
          <div class="mini-card" style="margin-bottom:1rem">
            <div class="mini-title">Changes Made</div>
            <ul class="changes-list" style="margin-top:0.5rem">
              ${d.changes_made.map(c => `<li>${c}</li>`).join('')}
            </ul>
          </div>
          <div class="mini-card" style="margin-bottom:1rem">
            <div class="mini-title">Improved CV</div>
            <div class="text-output" style="margin-top:0.75rem">${d.improved_cv}</div>
          </div>
          <div class="mini-card">
            <div class="mini-title">Cover Letter</div>
            <div class="text-output" style="margin-top:0.75rem">${d.cover_letter}</div>
          </div>
        `;
        document.getElementById('result-improve').classList.add('show');
      } catch (e) {
        showError('improve', e.message);
      } finally {
        setLoading('improve', false);
      }
    }