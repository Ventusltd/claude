/* GridAtlas skin architecture — THE ENGINE.
   =====================================================================
   This file is the "code" half of the Winamp split. It computes. It never
   renders. It contains no CSS, no HTML, no layout decision, no reference to
   any skin id, and no branch on technology.

   The one thing it does own that looks like presentation is the HONESTY
   CONTRACT (§5). That is deliberate and it is the central claim of this
   prototype: the rules that make a superlative honest are enforced HERE, at
   the seam, so that a skin author physically cannot drop them. A skin that
   omits a mandatory qualifier is not a compact skin — it is a skin the
   engine refuses to run.

   Everything below is either:
     - ported byte-faithfully from the live Atlas (marked PORTED, with the
       file and line it came from), or
     - measured live from the Atlas engine in Chrome on 2026-09-03 (marked
       MEASURED), or
     - new architecture for this prototype (marked NEW).

   Live composition read: 202609031316, ledger v9.89 (9593f0a).
*/
(() => {
  'use strict';

  /* ==================================================================
     1. GEODESY  — PORTED verbatim from
        gridatlas/atlas/modules/202609011950-geodesy.js
        One Earth radius for the whole estate. Haversine, atan2 form,
        because parity with the incumbent is the claim being made.
     ================================================================== */
  const EARTH_RADIUS_KM = 6378.137;
  const DEG = Math.PI / 180;

  function distanceKm(lon1, lat1, lon2, lat2) {
    const dLat = (lat2 - lat1) * DEG;
    const dLon = (lon2 - lon1) * DEG;
    const a = Math.sin(dLat / 2) ** 2
      + Math.cos(lat1 * DEG) * Math.cos(lat2 * DEG) * Math.sin(dLon / 2) ** 2;
    return EARTH_RADIUS_KM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  /* ==================================================================
     2. CONSTANTS — MEASURED live from window.__GRIDATLAS_NEON_LINKS__
        .measure on 2026-09-03 against composition 202609031316.
     ================================================================== */
  const MIN_KV = 33;          // link.measure.MIN_KV
  const MAX_LINK_KM = 40;     // link.measure.MAX_LINK_KM  "beyond this, silence is more honest"
  const LINK_COUNT = 5;       // link.measure.LINK_COUNT

  /* MEASURED: window.__GRIDATLAS_NETWORK__.coverage(kv) on the same session.
     These are the denominators every superlative in this product must name.
     They are NOT literals in the real engine — they are computed at render
     time from the payload that session fetched, precisely so they cannot go
     quietly false. They are snapshotted here only because this prototype does
     not re-fetch the 2.76 MiB connection-points product. The shape is what
     matters; a real integration calls coverage() and gets today's numbers. */
  const COVERAGE = {
    33:  { minimum_kv: 33,  published: 886, located: 502, unlocated: 384 },
    132: { minimum_kv: 132, published: 886, located: 502, unlocated: 384 },
    275: { minimum_kv: 275, published: 523, located: 334, unlocated: 189 },
    400: { minimum_kv: 400, published: 355, located: 214, unlocated: 141 }
  };
  const COVERAGE_BASIS = 'counted from the connection-points payload this session fetched';

  /* MEASURED: window.__GRIDATLAS_MODULES__.corridorEstimate.basis */
  const CORRIDOR = {
    factor: 1.245,
    median_absolute_error_pct: 8.45,
    within_15_pct: 73,
    circuits: 95,
    distinct_site_pairs: 59,
    source: 'published built lengths of GB transmission cable circuits',
    caveat: 'Indicative highway-corridor screening only. Not a connection offer, '
          + 'not a constructability assessment and not a consenting design.',
    not_for_overhead: 'Calibrated on cable circuits, which follow the highway '
          + 'network. Overhead line crosses open country and measures 1.13; this '
          + 'factor is not applied to an overhead-line question.',
    withhold_below_km: 1.0
  };

  function coverage(minimumKv) {
    const band = [400, 275, 132, 33].find(k => minimumKv >= k) || 33;
    return Object.assign({ basis: COVERAGE_BASIS }, COVERAGE[band]);
  }

  /* PORTED shape from sld-sandbox corridorBeside()/corridorEstimate.forCable().
     Returns DATA. The live version returns an HTML string; that is the seam
     defect this prototype exists to demonstrate (see 00-SKINS.md §4). */
  function corridorForCable(km) {
    if (!Number.isFinite(km)) return null;
    if (km < CORRIDOR.withhold_below_km) {
      return {
        withheld: 'at this separation the straight line between two site '
                + 'centroids is not measuring route factor at all'
      };
    }
    return {
      km: km * CORRIDOR.factor,
      factor: CORRIDOR.factor,
      basis: CORRIDOR,
      withheld: null
    };
  }

  /* ==================================================================
     3. THE MEASUREMENT — PORTED from nearestSubstations()
        Takes a longitude, a latitude and a candidate set.
        Reads NO technology. That separation IS the invariant.
     ================================================================== */
  function nearestSubstations(lon, lat, subs, opts) {
    const cap = (opts && Number.isFinite(opts.maxKm)) ? opts.maxKm : MAX_LINK_KM;
    const minKv = (opts && Number.isFinite(opts.minKv)) ? opts.minKv : MIN_KV;
    const considered = [];
    const scored = [];
    for (const sub of subs) {
      if (!sub || !sub.at) continue;
      const kv = Array.isArray(sub.kv) ? Math.max(...sub.kv) : Number(sub.kv);
      if (!Number.isFinite(kv) || kv < minKv) continue;
      considered.push(sub);
      const km = distanceKm(lon, lat, sub.at[0], sub.at[1]);
      scored.push({ name: sub.name, kv, at: sub.at, km });
    }
    scored.sort((a, b) => a.km - b.km);
    return {
      considered: considered.length,
      within_range: scored.filter(s => s.km <= cap).slice(0, LINK_COUNT),
      nearest: scored[0] || null,
      out_of_range: !!(scored[0] && scored[0].km > cap),
      max_link_km: cap,
      minimum_kv: minKv
    };
  }

  /* ==================================================================
     4. THE READING — NEW. The seam's data type.
        ---------------------------------------------------------------
        This is the ONLY thing that crosses from engine to skin. It is
        flat, typed, string-free where it can be, and carries its own
        provenance. Every skin renders the same object; no skin can ask
        the engine for anything else.
     ================================================================== */

  function read(subject, subs, options) {
    const o = options || {};
    const minKv = Number.isFinite(o.minKv) ? o.minKv : 400;
    const at = subject.at;
    const search = nearestSubstations(at[0], at[1], subs, { minKv, maxKm: MAX_LINK_KM });
    const cov = coverage(minKv);
    const n = search.nearest;
    const corridor = n ? corridorForCable(n.km) : null;

    /* The scenario marker. A reading is either the public record or a
       reader's modification of it, and that fact travels at the same
       priority as the word "straight". */
    const scenario = subject.scenario || { kind: 'record' };

    return Object.freeze({
      schema: 'gridatlas.reading/1',
      generation: '202609031316',
      engine_version: 'v9.89 (9593f0a) measurement path',

      /* --- state: a reading is allowed to be in flight --- */
      state: o.state || 'settled',        // 'settled' | 'recomputing' | 'unavailable'

      subject: Object.freeze({
        name: subject.name,
        repd_ref: subject.repd_ref || null,
        capacity_mw: Number.isFinite(subject.capacity_mw) ? subject.capacity_mw : null,
        technology: subject.technology || null,   // CARRIED, NEVER BRANCHED ON
        address: subject.address || null,
        status: subject.status || null,
        at
      }),

      scenario: Object.freeze({
        kind: scenario.kind,                       // 'record' | 'modified'
        moved_km: scenario.moved_km || null,
        capacity_delta_mw: scenario.capacity_delta_mw || null,
        of_record: scenario.of_record || null
      }),

      measurement: n ? Object.freeze({
        superlative_kind: 'nearest',
        target_name: n.name,
        target_kv: n.kv,
        target_at: n.at,
        straight_km: n.km,
        minimum_kv: minKv,
        corridor_km: corridor && !corridor.withheld ? corridor.km : null,
        corridor_factor: corridor && !corridor.withheld ? corridor.factor : null,
        corridor_withheld: corridor ? corridor.withheld : null,
        out_of_range: search.out_of_range,
        max_link_km: search.max_link_km,
        links_drawable: search.within_range.length,
        others: search.within_range
      }) : null,

      sample: Object.freeze({
        considered: search.considered,
        published: cov.published,
        located: cov.located,
        unlocated: cov.unlocated,
        located_pct: Math.round((cov.located / cov.published) * 1000) / 10,
        basis: cov.basis
      })
    });
  }

  /* ==================================================================
     5. THE HONESTY CONTRACT — NEW, and the load-bearing idea.
        ---------------------------------------------------------------
        FIELDS is the whole vocabulary a skin may reference. A skin is a
        list of field ids and boxes to put them in. It cannot compute, it
        cannot reach into the reading, and it cannot invent a sentence.

        Each field declares `mandatory_with`: if a view renders field X, it
        must also render every id in X.mandatory_with, IN THE SAME VIEW.
        validate() is run by the engine before a skin is allowed to render.
        This is what makes "a glanceable skin that drops the qualifier is a
        failed skin, not a compact one" mechanical rather than cultural.
     ================================================================== */

  const nf = (x, d) => Number(x).toLocaleString('en-GB',
    { minimumFractionDigits: d, maximumFractionDigits: d });

  const FIELDS = {
    /* ---- identity ---- */
    'subject.name':      { label: 'Project',  get: r => r.subject.name },
    'subject.capacity':  { label: 'Capacity', get: r => r.subject.capacity_mw == null
                              ? null : nf(r.subject.capacity_mw, 0) + ' MW' },
    'subject.reference': { label: 'Reference', get: r => r.subject.repd_ref
                              ? 'REPD ' + r.subject.repd_ref
                                + (r.subject.status ? ' · ' + r.subject.status : '')
                              : null },
    'subject.address':   { label: 'Address',  get: r => r.subject.address },
    /* Technology is a LABEL. It is never a branch, never a layout input,
       and every skin renders it identically or not at all. 32.7% of the
       spine has no layer for its bucket; a layout that reserves one is
       broken by construction. */
    'subject.technology': { label: 'Technology', get: r => r.subject.technology || null },

    /* ---- the measurement ---- */
    'measurement.headline': {
      label: 'Nearest substation',
      /* The superlative. Naming it obliges the sample and the word
         "straight" to appear in the same view. This is the gate. */
      mandatory_with: ['qualifier.straight', 'qualifier.sample', 'qualifier.scenario'],
      get: r => r.measurement
        ? r.measurement.target_name + ' · ' + nf(r.measurement.straight_km, 2) + ' km'
        : null
    },
    'measurement.label': {
      label: 'Measurement label',
      get: r => r.measurement
        ? 'Nearest ' + r.measurement.minimum_kv + ' kV substation' : null
    },
    'measurement.km': {
      label: 'Straight-line distance',
      mandatory_with: ['qualifier.straight', 'qualifier.sample', 'qualifier.scenario'],
      get: r => r.measurement ? nf(r.measurement.straight_km, 2) + ' km' : null
    },
    'measurement.target': { label: 'Substation', get: r => r.measurement ? r.measurement.target_name : null },
    'measurement.kv':     { label: 'Voltage',    get: r => r.measurement ? r.measurement.target_kv + ' kV' : null },
    'measurement.corridor': {
      label: 'Corridor estimate',
      mandatory_with: ['qualifier.corridor'],
      get: r => r.measurement && r.measurement.corridor_km != null
        ? '~' + nf(r.measurement.corridor_km, 1) + ' km corridor estimate (×'
          + r.measurement.corridor_factor + ')'
        : (r.measurement && r.measurement.corridor_withheld
            ? 'No corridor estimate at this separation: ' + r.measurement.corridor_withheld + '.'
            : null)
    },
    'measurement.range_note': {
      label: 'Drawing range',
      get: r => r.measurement && r.measurement.out_of_range
        ? 'Further than this map draws links (' + r.measurement.max_link_km + ' km). '
          + 'The distance is measured; only the line is withheld.'
        : null
    },

    /* ---- the non-negotiable qualifiers ---- */
    'qualifier.straight': {
      label: 'Straight',
      get: () => 'straight line, not a route'
    },
    'qualifier.sample': {
      label: 'Sample',
      get: r => 'nearest of the ' + nf(r.sample.considered, 0) + ' mapped substations at '
        + (r.measurement ? r.measurement.minimum_kv : 400) + ' kV or above that this search could see'
    },
    'qualifier.sample_full': {
      label: 'Sample, in full',
      get: r => 'Scope: nearest of the ' + nf(r.sample.considered, 0) + ' mapped substations at '
        + (r.measurement ? r.measurement.minimum_kv : 400) + ' kV or above that this search could see; '
        + 'the operator publishes ' + nf(r.sample.published, 0) + ' connection points at that class and '
        + nf(r.sample.located, 0) + ' of them carry coordinates (' + r.sample.located_pct + '%), so '
        + nf(r.sample.unlocated, 0) + ' cannot be measured to at all. '
        + 'A nearer one may exist that nothing here can see.'
    },
    'qualifier.corridor': {
      label: 'Corridor basis',
      get: () => CORRIDOR.caveat + ' ' + CORRIDOR.not_for_overhead
    },
    /* The scenario marker is mandatory wherever a measurement appears,
       at every size, including the watch. A moved 840 MW project must
       never read as a consented scheme. */
    'qualifier.scenario': {
      label: 'Record or scenario',
      get: r => r.scenario.kind === 'modified'
        ? 'SCENARIO — reader-modified, not the public record'
        : 'Public record'
    },
    'state.notice': {
      label: 'State',
      get: r => r.state === 'recomputing' ? 'Recalculating…'
             : (r.state === 'unavailable' ? 'Not yet measured' : null)
    }
  };

  /* A view is valid iff, for every field it renders, every id in that
     field's mandatory_with is ALSO rendered in the same view.
     Returns [] when valid; otherwise the list of what is missing. */
  function validateView(view) {
    const present = new Set((view.blocks || []).map(b => b.field));
    const missing = [];
    for (const id of present) {
      const f = FIELDS[id];
      if (!f) { missing.push({ field: id, needs: '(unknown field id)' }); continue; }
      for (const need of (f.mandatory_with || [])) {
        if (!present.has(need)) missing.push({ field: id, needs: need });
      }
    }
    return missing;
  }

  function validateSkin(skin) {
    const problems = [];
    for (const view of (skin.views || [])) {
      for (const m of validateView(view)) {
        problems.push(skin.id + '/' + view.id + ': "' + m.field
          + '" may not be rendered without "' + m.needs + '" in the same view');
      }
    }
    return problems;
  }

  /* ==================================================================
     6. LAYER REGISTRY — NEW. Designed for 1000, proved at 1000.
        ---------------------------------------------------------------
        A layer's EXISTENCE is a manifest row (~140 bytes). A layer's
        PAYLOAD is fetched only when the reader asks for it.

        Four states, and the distinction the architect's word "minimising"
        demands:

          declared   manifest only. No payload, no map layer.   ~140 B
          loading    payload in flight.
          loaded     payload held, map layers attached, visible.
          minimised  payload HELD, map layers detached-or-hidden.
                     Reopening is instant. THIS IS A PRESENTATION ACT.
          (unload)   payload released, back to `declared`.
                     THIS IS AN ENGINE ACT. Only the engine does it, only
                     under memory pressure, and it is always reported.

        Two budgets, because they are different resources:
          paintBudget   how many layers may be attached to the map at once
          memoryBudget  how many may hold a payload at once

        At the paint ceiling the engine REFUSES and names what to turn off.
        It never silently drops a layer — a silent drop is exactly the
        false-green that let three technology buckets ship dark.

        HEALTH IS OBSERVED, NOT SELF-REPORTED. attached() reads back from
        the map adapter. link.technology_layer.enabled reported true while
        the layer was off; nothing here may repeat that.
     ================================================================== */

  function LayerRegistry(opts) {
    const cfg = Object.assign({
      paintBudget: 24,
      memoryBudget: 120,
      adapter: null          // { attach(id), detach(id), isAttached(id) } — the map
    }, opts || {});

    const rows = new Map();        // id -> manifest row
    const order = [];              // insertion order, for stable paging
    const touched = new Map();     // id -> monotonic tick, for LRU
    let tick = 0;
    const listeners = [];
    const events = [];             // observable health log

    function emit(type, detail) {
      const e = { t: Date.now(), type, ...detail };
      events.push(e);
      if (events.length > 500) events.shift();
      listeners.forEach(fn => { try { fn(e); } catch (_) {} });
    }

    function declare(row) {
      if (rows.has(row.id)) return rows.get(row.id);
      const r = {
        id: row.id,
        label: row.label,
        group: row.group || 'other',
        kv: row.kv == null ? null : Number(row.kv),
        kind: row.kind || 'other',
        source: row.source || 'unknown',
        region: row.region || null,
        bytes: row.bytes || 0,
        state: 'declared',
        error: null
      };
      rows.set(r.id, r); order.push(r.id);
      return r;
    }

    const countIn = s => { let n = 0; for (const r of rows.values()) if (r.state === s) n++; return n; };
    const painted = () => countIn('loaded');
    const resident = () => countIn('loaded') + countIn('minimised') + countIn('loading');

    /* Load = make visible. Refuses at the ceiling and says why. */
    async function load(id) {
      const r = rows.get(id);
      if (!r) return { ok: false, reason: 'no such layer: ' + id };
      if (r.state === 'loaded') return { ok: true, already: true };

      if (r.state === 'minimised') {         // instant: payload was never released
        r.state = 'loaded';
        if (cfg.adapter) cfg.adapter.attach(id);
        touched.set(id, ++tick);
        emit('restore', { id, cost_ms: 0 });
        return { ok: true, restored: true };
      }

      if (painted() >= cfg.paintBudget) {
        const suggest = [...touched.entries()]
          .filter(([k]) => rows.get(k) && rows.get(k).state === 'loaded')
          .sort((a, b) => a[1] - b[1]).slice(0, 3).map(([k]) => rows.get(k).label);
        emit('refused', { id, reason: 'paint budget', budget: cfg.paintBudget, suggest });
        return {
          ok: false,
          reason: 'At the paint ceiling (' + cfg.paintBudget + ' layers on the map). '
                + 'Turn one off first — least recently used: ' + suggest.join(', ') + '.',
          suggest
        };
      }

      if (resident() >= cfg.memoryBudget) evictLru();

      r.state = 'loading';
      const t0 = (performance && performance.now) ? performance.now() : Date.now();
      try {
        if (cfg.fetchPayload) await cfg.fetchPayload(r);
        r.state = 'loaded'; r.error = null;
        if (cfg.adapter) cfg.adapter.attach(id);
        touched.set(id, ++tick);
        const t1 = (performance && performance.now) ? performance.now() : Date.now();
        emit('load', { id, cost_ms: Math.round(t1 - t0), bytes: r.bytes });
        return { ok: true };
      } catch (err) {
        r.state = 'declared'; r.error = String(err && err.message || err);
        emit('load_failed', { id, error: r.error });
        return { ok: false, reason: r.error };
      }
    }

    /* Minimise: PRESENTATION. Payload retained. Reopening is free. */
    function minimise(id) {
      const r = rows.get(id);
      if (!r || r.state !== 'loaded') return false;
      r.state = 'minimised';
      if (cfg.adapter) cfg.adapter.detach(id);
      emit('minimise', { id });
      return true;
    }

    /* Unload: ENGINE. Payload released. Always reported. */
    function unload(id, why) {
      const r = rows.get(id);
      if (!r || r.state === 'declared') return false;
      if (cfg.adapter) cfg.adapter.detach(id);
      r.state = 'declared';
      emit('unload', { id, why: why || 'requested' });
      return true;
    }

    function evictLru() {
      const cands = [...rows.values()].filter(r => r.state === 'minimised');
      cands.sort((a, b) => (touched.get(a.id) || 0) - (touched.get(b.id) || 0));
      if (cands[0]) unload(cands[0].id, 'memory budget');
    }

    /* HEALTH: read back from the map, never from our own flag. */
    function health() {
      const out = { checked: 0, disagreements: [] };
      if (!cfg.adapter || !cfg.adapter.isAttached) return { checked: 0, disagreements: [], note: 'no adapter' };
      for (const r of rows.values()) {
        if (r.state !== 'loaded' && r.state !== 'minimised') continue;
        out.checked++;
        const actually = !!cfg.adapter.isAttached(r.id);
        const expected = r.state === 'loaded';
        if (actually !== expected) out.disagreements.push({ id: r.id, says: r.state, map_says: actually });
      }
      return out;
    }

    /* Discovery at 1000 is search + facet + page, never a list.
       Returns a PAGE of manifest rows. A skin renders the page; it never
       sees a payload and never holds 1000 DOM nodes. */
    function query(q) {
      const { text = '', group = null, kv = null, kind = null, state = null,
              offset = 0, limit = 40 } = (q || {});
      const needle = text.trim().toLowerCase();
      const hits = [];
      for (const id of order) {
        const r = rows.get(id);
        if (group && r.group !== group) continue;
        if (kind && r.kind !== kind) continue;
        if (kv != null && r.kv !== Number(kv)) continue;
        if (state && r.state !== state) continue;
        if (needle && !(r.label.toLowerCase().includes(needle) || r.id.includes(needle))) continue;
        hits.push(r);
      }
      return { total: hits.length, offset, limit, rows: hits.slice(offset, offset + limit) };
    }

    function facets() {
      const g = new Map(), k = new Map(), v = new Map();
      const bump = (m, key) => m.set(key, (m.get(key) || 0) + 1);
      for (const r of rows.values()) { bump(g, r.group); bump(k, r.kind); if (r.kv != null) bump(v, r.kv); }
      const sortNum = m => [...m.entries()].sort((a, b) => Number(b[0]) - Number(a[0]));
      const sortCnt = m => [...m.entries()].sort((a, b) => b[1] - a[1]);
      return { group: sortCnt(g), kind: sortCnt(k), kv: sortNum(v) };
    }

    function stats() {
      return {
        declared: rows.size,
        painted: painted(),
        resident: resident(),
        paintBudget: cfg.paintBudget,
        memoryBudget: cfg.memoryBudget,
        manifest_bytes: rows.size * 140,
        payload_bytes_if_all_loaded: [...rows.values()].reduce((a, r) => a + r.bytes, 0)
      };
    }

    return { declare, load, minimise, unload, query, facets, stats, health,
             get: id => rows.get(id), size: () => rows.size,
             onEvent: fn => listeners.push(fn), events: () => events.slice(-50) };
  }

  /* ==================================================================
     7. SELF-MINIMISE POLICY — NEW.
        The architect: fields "should self-minimise so the user focuses on
        the product card, drifting on the map."

        The trigger is specified here, in the engine, because "self-
        minimise" is a behaviour with safety consequences, not an
        adjective. A skin may set the delay or opt a panel out; it may not
        invent the exceptions.
     ================================================================== */
  const AUTOCOLLAPSE = Object.freeze({
    idle_ms: 6000,               // no pointer/key/scroll inside the panel
    after_commit_ms: 1200,       // a choice was made: collapse shortly after
    animation_ms: 180,           // and never longer; motion is chrome, not content
    reduced_motion_ms: 0,        // prefers-reduced-motion: snap, do not animate
    /* NEVER auto-collapses, in any skin: */
    never: Object.freeze([
      'mid-edit',                 // a field with focus or a non-empty uncommitted value
      'unread-result',            // a result the reader has not yet seen
      'error',                    // anything reporting a failure
      'in-flight',                // a fetch or a recompute still running
      'pinned'                    // the reader explicitly pinned it open
    ])
  });

  function autoCollapse(panel, opts) {
    /* panel: { el, isExempt(), onCollapse() } */
    const cfg = Object.assign({}, AUTOCOLLAPSE, opts || {});
    let timer = null;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const arm = (ms) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        if (panel.isExempt && panel.isExempt()) { arm(cfg.idle_ms); return; }
        panel.onCollapse(reduced ? cfg.reduced_motion_ms : cfg.animation_ms);
      }, ms);
    };
    const bump = () => arm(cfg.idle_ms);
    ['pointermove', 'pointerdown', 'keydown', 'scroll', 'focusin']
      .forEach(t => panel.el.addEventListener(t, bump, { passive: true }));
    panel.el.addEventListener('pointerleave', () => arm(cfg.after_commit_ms), { passive: true });
    arm(cfg.idle_ms);
    return { bump, cancel: () => clearTimeout(timer), commit: () => arm(cfg.after_commit_ms) };
  }

  /* ==================================================================
     8. ENVIRONMENT DETECTION — NEW.
        Detection chooses a DEFAULT. The reader chooses the TRUTH.
        Order of precedence, highest first:
          1. ?skin=  URL override        (a link can pin a skin; kiosks, testing)
          2. localStorage choice         (the reader's own last decision)
          3. detect()                    (a guess, always labelled as one)
        No call to requestFullscreen() anywhere in this file.
     ================================================================== */
  function probe() {
    const mq = q => { try { const m = matchMedia(q); return m.media === 'not all' ? null : m.matches; }
                      catch (_) { return null; } };
    const uad = navigator.userAgentData || null;
    const c = navigator.connection || null;
    return {
      hidden: document.hidden,
      pointer_coarse: mq('(pointer: coarse)'),
      pointer_fine: mq('(pointer: fine)'),
      pointer_none: mq('(pointer: none)'),
      any_pointer_coarse: mq('(any-pointer: coarse)'),
      hover_hover: mq('(hover: hover)'),
      any_hover_hover: mq('(any-hover: hover)'),
      maxTouchPoints: navigator.maxTouchPoints,
      innerWidth: innerWidth, innerHeight: innerHeight,
      screenWidth: screen.width, screenHeight: screen.height,
      dpr: devicePixelRatio,
      uad_mobile: uad ? uad.mobile : null,
      uad_platform: uad ? uad.platform : null,
      uad_brands: uad ? uad.brands.map(b => b.brand).join(', ') : null,
      deviceMemory: 'deviceMemory' in navigator ? navigator.deviceMemory : null,
      hardwareConcurrency: navigator.hardwareConcurrency,
      effectiveType: c ? c.effectiveType : null,
      saveData: c ? c.saveData : null,
      reduced_motion: mq('(prefers-reduced-motion: reduce)'),
      dark: mq('(prefers-color-scheme: dark)'),
      orientation: screen.orientation ? screen.orientation.type : null,
      nav_tv: /\b(SmartTV|SMART-TV|GoogleTV|AndroidTV|HbbTV|Tizen|Web0S|BRAVIA|AFT[MB])\b/i.test(navigator.userAgent),
      nav_watch: /\b(Watch|WearOS|watchOS)\b/i.test(navigator.userAgent),
      nav_car: /\b(AndroidAuto|CarPlay|Automotive|QNX)\b/i.test(navigator.userAgent),
      standalone: mq('(display-mode: standalone)')
    };
  }

  /* Each skin declares its own `detect` predicate DECLARATIVELY (see the
     JSON). This evaluates those declarations; it does not name any skin. */
  function scoreSkin(skin, p) {
    const d = skin.detect || {};
    let score = 0;
    const why = [];
    const test = (cond, pts, note) => { if (cond) { score += pts; why.push(note); } };
    if (d.uaMatch) test(new RegExp(d.uaMatch, 'i').test(navigator.userAgent), 100, 'UA matches ' + d.uaMatch);
    if (d.maxWidth != null) test(p.innerWidth <= d.maxWidth, 20, 'width <= ' + d.maxWidth);
    if (d.minWidth != null) test(p.innerWidth >= d.minWidth, 20, 'width >= ' + d.minWidth);
    if (d.minScreenWidth != null) test(p.screenWidth >= d.minScreenWidth, 15, 'screen >= ' + d.minScreenWidth);
    if (d.pointer) test(p['pointer_' + d.pointer] === true, 25, 'pointer: ' + d.pointer);
    if (d.hover === false) test(p.hover_hover === false, 25, 'no hover');
    if (d.hover === true) test(p.hover_hover === true, 10, 'hover available');
    if (d.mobile === true) test(p.uad_mobile === true, 25, 'UA-CH mobile');
    if (d.mobile === false) test(p.uad_mobile === false, 10, 'UA-CH not mobile');
    if (d.saveData === true) test(p.saveData === true, 30, 'Save-Data on');
    if (d.maxDeviceMemory != null) test(p.deviceMemory != null && p.deviceMemory <= d.maxDeviceMemory, 20,
      'deviceMemory <= ' + d.maxDeviceMemory);
    score += (d.baseline || 0);
    if (d.baseline) why.push('baseline ' + d.baseline);
    return { score, why };
  }

  function chooseSkin(skins, p) {
    const url = new URLSearchParams(location.search).get('skin');
    if (url && skins.some(s => s.id === url)) {
      return { id: url, how: 'url', why: ['?skin=' + url + ' pinned this skin'] };
    }
    let stored = null;
    try { stored = localStorage.getItem('gridatlas.skin'); } catch (_) {}
    if (stored && skins.some(s => s.id === stored)) {
      return { id: stored, how: 'chosen', why: ['you chose this skin; it survives reload and deep links'] };
    }
    const ranked = skins.map(s => ({ id: s.id, ...scoreSkin(s, p) }))
                        .sort((a, b) => b.score - a.score);
    return { id: ranked[0].id, how: 'auto', why: ranked[0].why, ranked };
  }

  function rememberSkin(id) { try { localStorage.setItem('gridatlas.skin', id); } catch (_) {} }
  function forgetSkin() { try { localStorage.removeItem('gridatlas.skin'); } catch (_) {} }

  /* ==================================================================
     9. EXPORT — the entire seam. Nothing else crosses.
     ================================================================== */
  window.GRIDATLAS_ENGINE = Object.freeze({
    EARTH_RADIUS_KM, MIN_KV, MAX_LINK_KM, LINK_COUNT, CORRIDOR, AUTOCOLLAPSE,
    distanceKm, coverage, corridorForCable, nearestSubstations,
    read, FIELDS, validateView, validateSkin,
    LayerRegistry, autoCollapse,
    probe, scoreSkin, chooseSkin, rememberSkin, forgetSkin
  });
})();
