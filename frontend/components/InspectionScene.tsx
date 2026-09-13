import { ScanLine, Layers3, ShieldCheck, Cpu } from 'lucide-react';

export default function InspectionScene({ compact = false }: { compact?: boolean }) {
  return (
    <section className={compact ? 'inspection-story inspection-story-compact' : 'inspection-story'} aria-label="VisionInspect platform introduction">
      <div className="scene-eyebrow"><ScanLine size={16} /> VISIONINSPECT <span>AI</span></div>
      <div className="scene-copy">
        <p className="scene-kicker">PRECISION AT EVERY LAYER</p>
        <h2>See the detail.<br /><span>Elevate the quality.</span></h2>
        <p>Turn product images into clear inspection insights. Detect defects, assess severity, and keep your production moving.</p>
      </div>
      <div className="inspection-stage" aria-hidden="true">
        <div className="stage-orbit orbit-one" /><div className="stage-orbit orbit-two" />
        <div className="assembly">
          <div className="assembly-layer layer-bottom" />
          <div className="assembly-layer layer-middle" />
          <div className="assembly-layer layer-top">
            <div className="circuit-line circuit-one" /><div className="circuit-line circuit-two" />
            <div className="chip"><Cpu size={58} strokeWidth={1} /></div>
            <i className="board-node node-one" /><i className="board-node node-two" /><i className="board-node node-three" />
            <div className="scan-beam" />
          </div>
        </div>
        <div className="scene-tag tag-top"><span className="scene-dot" /> Surface analysis <ScanLine size={14} /></div>
        <div className="scene-tag tag-bottom"><Layers3 size={15} /> Layer-by-layer precision</div>
        <span className="scene-caption">ILLUSTRATIVE INSPECTION PREVIEW</span>
      </div>
      <div className="scene-features"><span><ScanLine size={16} /> Visual detection</span><span><ShieldCheck size={16} /> Quality assessment</span><span><Layers3 size={16} /> Inspection reports</span></div>
    </section>
  );
}
