# V3 animation system

CSS owns the entrance, hover, menu and dialog treatments. IntersectionObserver can trigger movement once per section without intercepting scrolling. Scroll-linked accent and hero depth use CSS when supported and have a static rendering on older engines. Native cross-document transitions are an enhancement for supporting browsers. No animation dependency is needed.

GSAP and ScrollTrigger are useful for tightly choreographed sequences, Motion for component-heavy transitions, Lenis for bespoke scroll behaviors and Three.js for broader scene authoring. This site has a compact set of editorial movements, a native document workflow and an existing lazy WebGL engine. The implementation keeps the smaller dependency-free setup and avoids full-document scroll interception.

Reduced motion uses a static layout with no decorative transitions. The content remains visible before scripts run. 3D opens by choice, caps rendering quality, retains keyboard controls and uses photo fallbacks. The glass-free nav and product controls maintain focus through state changes.
