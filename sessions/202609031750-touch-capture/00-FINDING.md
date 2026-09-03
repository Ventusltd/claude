# MapLibre does not consume the card's touch gesture — refuted at the source

Stamp 202609031750 (UTC). Question asked: does MapLibre's touch handling swallow the
drag that should scroll `.maplibregl-popup-content`, leaving the grid distance
unreachable 650 px below the fold on a phone?

**Refuted.** MapLibre consumes nothing. It cannot: its touch listeners are bound to an
element that is not an ancestor of the popup, so a touch on the card never traverses
them. This note records the structural proof, because it closes the hypothesis by
construction rather than by one negative observation.

A parallel agent settled the same question from the other end, with real
`Input.dispatchTouchEvent` flicks on a verified 393x852 @3x device with
`pointer: coarse` true. Their result — the card scrolls 402-421 px per flick wherever
the card is the topmost element, and exactly 0 px where `.map-controls` (the tray,
GB PRICES, VERSIONS, y 698-822) is on top — is the operative finding. This note is
the corroborating half: it says *why* no event-level fix was ever going to help.

## What was measured

Live v9.89, Botley West deep link (`repd_ref=12588`), atlas generation 202609031316,
release `202608300453-atlas-v9`. Same-origin iframe declared at 393x852 inside a tab on
`ventusltd.github.io`; the inner window reported `innerWidth 393 / innerHeight 852`.
Caveat stated up front: that method gives a true narrow viewport but **not**
`pointer: coarse` (it reported false, `maxTouchPoints 0`). It is therefore valid for
DOM topology, computed style and script inspection — which is all that is claimed
below — and invalid for anything about how a finger behaves. The device-level
behaviour comes from the parallel agent, not from here.

### 1. The popup is a sibling of the canvas container, not a descendant

Ancestor chain from the answer element upward, read from the live composed page:

    DIV  .maplibregl-popup-content            touch-action auto   pointer-events auto   overflow-y auto
    DIV  .maplibregl-popup ...-anchor-right   touch-action auto   pointer-events none   overflow-y visible
    DIV  .maplibregl-map#map                  touch-action auto   pointer-events auto   overflow-y hidden
    DIV  .map-container.is-fullscreen         touch-action auto   pointer-events auto   overflow-y hidden
    DIV  .dashboard                           touch-action auto   pointer-events auto   overflow-y visible
    BODY .fs-active                           touch-action auto   pointer-events auto   overflow-y hidden
    HTML .fs-active                           touch-action auto   pointer-events auto   overflow-y hidden

Direct assertions against the same DOM:

    canvasContainer.contains(popupContent)              -> false
    canvasContainer.parentNode === popup.parentNode     -> true   (they are siblings)

The card's bubble path is popup-content -> popup -> `.maplibregl-map` -> ... . It never
passes through `.maplibregl-canvas-container`.

### 2. Every MapLibre touch listener is on the canvas container

maplibre-gl 3.6.2 (`cdn.jsdelivr.net/npm/maplibre-gl@3.6.2/dist/maplibre-gl.js`, the
build the shell loads). In the minified HandlerManager constructor:

    this._map = t, this._el = this._map.getCanvasContainer(), ...
    const s = this._el;
    this._listeners = [[s,"touchstart",{passive:!0}],[s,"touchmove",{passive:!1}],
                       [s,"touchend",void 0],[s,"touchcancel",void 0],
                       [s,"mousedown",...],[s,"mousemove",...],[s,"mouseup",...],
                       [document,"mousemove",{capture:!0}],[document,"mouseup",void 0],
                       [s,"mouseover"],[s,"mouseout"],[s,"dblclick"],[s,"click"],
                       [s,"keydown",{capture:!1}],[s,"keyup"],[s,"wheel",{passive:!1}],
                       [s,"contextmenu"],[window,"blur"]]

Two things follow. The only `document`- or `window`-level entries are `mousemove`,
`mouseup` and `blur` — **no document-level touch listener exists**, so there is no
capture-phase interception of touch anywhere above the popup. And the one non-passive
touch listener, `touchmove`, is bound to `s` = the canvas container, which by (1) is
not on the card's path.

The only other touch registrations in the whole bundle are
`addEventListener(s,"touchstart",...,{passive:!1})` and `touchcancel` inside
`DragRotateHandler` for the **compass control element**, plus `window` touchmove/touchend
added only *after* a compass drag starts; and `Marker.setDraggable`, which subscribes via
`map.on("touchstart")` and is not used here. None of these touch the popup.

### 3. The application binds no touch handlers at all

Full grep of every script the shell composes — `ventus-corev8engine.js` (91 KB),
`202608291818-place-postcode-search.js`, `202608292126-pre-snapped-config-adapter.js`,
`202608292311-maplibre-worker-bridge.js`, and the four cartridges named in
`current.json` — for `touchstart|touchmove|touchend|pointerdown|touch-action|overscroll`:

    zero matches

Every `preventDefault` in the app source is on a `keydown` (Enter in the radius input),
on `map.on("dblclick")` for measure/zone-draw, or in `_zoneDrawOnMouseDown`. All
mouse/keyboard. Nothing that could cancel a touchmove.

### 4. No touch-action anywhere on the chain

Every ancestor from popup-content to `html` computes `touch-action: auto` (table in 1).
The `touch-action: none` that maplibre-gl.css does apply lands on
`.maplibregl-canvas-container.maplibregl-touch-drag-pan.maplibregl-touch-zoom-rotate` —
again the sibling, not an ancestor. Effective touch-action at the card is `auto`, so
vertical panning of the scroller is permitted by the browser. Nothing to fix here
either.

## Conclusion

The three ways a gesture could have been swallowed are each independently excluded:
no listener on the path (1 + 2), no app handler at all (3), no touch-action restriction
(4). The card's scroller was never the problem, and no amount of `stopPropagation` on
`.maplibregl-popup-content`, `touch-action` tuning, or excluding MapLibre's handlers
over the popup would have moved it. Those were the three candidate fixes in the brief;
all three are dead.

What is left is the parallel agent's measurement: the card scrolls fine, and stops dead
only where `.map-controls` sits on top of it, y 698-822 — the bottom 154 px, which is
the thumb zone. The overlap and the unreachable answer are one defect. **De-overlap is
the fix.** No event-level change is warranted.

Incidental, recorded because it is cheap and may matter to whoever does the de-overlap:
at 393 px the popup content's bounding rect was
`left -87, width 330, top 116, height 809` — the card hangs 87 px off the left edge of
the viewport, and its 809 px height against an 852 px viewport leaves the scroller's
`scrollHeight 1810 / clientHeight 808` almost exactly the 1003 px of unused range
reported earlier.

## Reproduction

Structural half, runnable from any shell, no browser needed:

    curl -s https://ventusltd.github.io/gridatlas/atlas/current.json
    curl -s https://cdn.jsdelivr.net/npm/maplibre-gl@3.6.2/dist/maplibre-gl.js \
      | grep -oE '.{320}this\._changes=\[\],this\._inertia'
    # -> shows  this._el = this._map.getCanvasContainer()
    curl -s https://cdn.jsdelivr.net/npm/maplibre-gl@3.6.2/dist/maplibre-gl.js \
      | grep -oE '.{200}"touchstart".{200}'
    # -> the four registrations described in section 2, and no document-level touch

DOM half, in a tab already on `ventusltd.github.io` (same-origin iframe, so
`contentDocument` is readable). Confirm `document.hidden === false` first; a
backgrounded tab misreports on this product:

    const f = document.createElement('iframe');
    f.style.cssText = 'position:fixed;left:0;top:0;width:393px;height:852px;z-index:9e5';
    f.src = '/gridatlas/atlas/?repd_ref=12588&latitude=51.8132088&longitude=-1.3489728&zoom=12';
    document.body.appendChild(f);
    // wait for load, then ~9 s for the popup
    const d = f.contentDocument;
    const pc = d.querySelector('.maplibregl-popup-content');
    const cc = d.querySelector('.maplibregl-canvas-container');
    cc.contains(pc);                      // false
    cc.parentNode === pc.parentNode.parentNode;   // true
    // walk pc upward logging getComputedStyle(n).touchAction -> auto at every level

Then remove the iframe. Nothing else is left running.

## Not tested here

Anything requiring a real coarse pointer. The iframe-at-declared-width method cannot
produce `pointer: coarse`, generates no trusted touch, and synthetic `TouchEvent`s are
untrusted so they can never move `scrollTop` natively — which is why "dispatch touch and
watch scrollTop" is not a valid discriminator and was not used as one. The device-level
numbers belong to the parallel agent's `Input.dispatchTouchEvent` run.

No Chrome was launched on a debug port by this investigation. The iframe harness was
removed in the same session; the tab was closed.
