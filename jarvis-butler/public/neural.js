/**
 * Neural Network Visualization Engine
 * Real-time animated neural nodes with firing states and pulsing effects
 */

class NeuralNetwork {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = this.canvas.getContext('2d');
    this.dpr = window.devicePixelRatio || 1;
    
    // Network configuration
    this.nodeCount = 25;
    this.nodes = [];
    this.connections = [];
    
    // Animation state
    this.animationFrameId = null;
    this.currentState = 'idle'; // idle, firing, processing, matched, responding
    this.stateTimestamp = Date.now();
    this.pulsePhase = 0;
    
    // Colors for different states
    this.colors = {
      idle: '#333333',
      firing: '#00ccff',
      processing: '#00ffff',
      matched: '#00ff00',
      responding: '#ffd700'
    };
    
    // Setup
    this.setupCanvas();
    this.createNetwork();
    this.start();
  }

  setupCanvas() {
    // Set canvas size with DPR
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * this.dpr;
    this.canvas.height = rect.height * this.dpr;
    this.ctx.scale(this.dpr, this.dpr);
    
    this.width = rect.width;
    this.height = rect.height;
    
    // Handle window resize
    window.addEventListener('resize', () => this.handleResize());
  }

  handleResize() {
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * this.dpr;
    this.canvas.height = rect.height * this.dpr;
    this.ctx.scale(this.dpr, this.dpr);
    this.width = rect.width;
    this.height = rect.height;
    this.updateNodePositions();
  }

  createNetwork() {
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const radius = Math.min(this.width, this.height) * 0.35;
    
    // Create nodes in circular arrangement
    for (let i = 0; i < this.nodeCount; i++) {
      const angle = (i / this.nodeCount) * Math.PI * 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      this.nodes.push({
        id: i,
        x: x,
        y: y,
        baseX: x,
        baseY: y,
        radius: 8,
        state: 'idle',
        stateTime: 0,
        energy: Math.random() * 0.3,
        frequency: 0.05 + Math.random() * 0.05
      });
    }
    
    // Create connections (each node connects to nearby nodes)
    for (let i = 0; i < this.nodes.length; i++) {
      const node = this.nodes[i];
      const connectionCount = 3 + Math.floor(Math.random() * 3);
      
      for (let j = 0; j < connectionCount; j++) {
        const targetIdx = (i + 1 + Math.floor(Math.random() * 5)) % this.nodes.length;
        if (targetIdx !== i) {
          this.connections.push({
            from: i,
            to: targetIdx,
            opacity: 0.2 + Math.random() * 0.2
          });
        }
      }
    }
  }

  updateNodePositions() {
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const radius = Math.min(this.width, this.height) * 0.35;
    
    for (let i = 0; i < this.nodes.length; i++) {
      const angle = (i / this.nodeCount) * Math.PI * 2;
      this.nodes[i].baseX = centerX + Math.cos(angle) * radius;
      this.nodes[i].baseY = centerY + Math.sin(angle) * radius;
    }
  }

  setState(newState) {
    this.currentState = newState;
    this.stateTimestamp = Date.now();
    
    // Trigger neuron firing based on state
    if (newState === 'firing') {
      this.fireRandomNeurons(8);
    } else if (newState === 'processing') {
      this.fireRandomNeurons(12);
    } else if (newState === 'matched') {
      this.fireAllNeurons();
    } else if (newState === 'responding') {
      this.fireRandomNeurons(15);
    }
  }

  fireRandomNeurons(count) {
    for (let i = 0; i < count; i++) {
      const idx = Math.floor(Math.random() * this.nodes.length);
      this.nodes[idx].state = this.currentState;
      this.nodes[idx].stateTime = 0;
    }
  }

  fireAllNeurons() {
    for (const node of this.nodes) {
      node.state = this.currentState;
      node.stateTime = 0;
    }
  }

  update() {
    this.pulsePhase += 0.02;
    const elapsed = Date.now() - this.stateTimestamp;
    
    for (const node of this.nodes) {
      // Update node state timer
      if (node.state !== 'idle' && node.stateTime < 500) {
        node.stateTime += 16; // Approximate 60fps
      } else if (node.stateTime >= 500) {
        node.state = 'idle';
      }
      
      // Natural pulsing when idle
      if (node.state === 'idle') {
        node.energy += (Math.sin(this.pulsePhase + node.id) * 0.02);
        node.energy = Math.max(0, Math.min(1, node.energy));
      } else {
        // Decay energy when active
        node.energy = Math.max(0, node.energy - 0.05);
      }
      
      // Slight position jitter when firing
      if (node.state !== 'idle') {
        node.x = node.baseX + Math.sin(this.pulsePhase * node.frequency) * 2;
        node.y = node.baseY + Math.cos(this.pulsePhase * node.frequency) * 2;
      } else {
        node.x = node.baseX + Math.sin(this.pulsePhase * node.frequency) * 0.5;
        node.y = node.baseY + Math.cos(this.pulsePhase * node.frequency) * 0.5;
      }
    }
  }

  draw() {
    // Clear canvas
    this.ctx.fillStyle = '#0a0e27';
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    // Draw connections
    this.drawConnections();
    
    // Draw nodes
    this.drawNodes();
    
    // Draw center core (JARVIS brain)
    this.drawCore();
  }

  drawConnections() {
    for (const conn of this.connections) {
      const fromNode = this.nodes[conn.from];
      const toNode = this.nodes[conn.to];
      
      const fromActive = fromNode.state !== 'idle';
      const toActive = toNode.state !== 'idle';
      
      let color = '#1a3a4a';
      let opacity = conn.opacity * 0.3;
      
      if (fromActive || toActive) {
        color = '#00ccff';
        opacity = conn.opacity * 0.8;
      }
      
      this.ctx.strokeStyle = color;
      this.ctx.globalAlpha = opacity;
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(fromNode.x, fromNode.y);
      this.ctx.lineTo(toNode.x, toNode.y);
      this.ctx.stroke();
    }
    this.ctx.globalAlpha = 1;
  }

  drawNodes() {
    for (const node of this.nodes) {
      const baseColor = this.colors[node.state] || this.colors.idle;
      
      // Calculate glow intensity
      let glowIntensity = 0.2 + node.energy * 0.8;
      if (node.state !== 'idle') {
        glowIntensity = 0.6 + Math.sin(this.pulsePhase) * 0.4;
      }
      
      // Draw glow
      const gradient = this.ctx.createRadialGradient(
        node.x, node.y, 0,
        node.x, node.y, node.radius * 3
      );
      gradient.addColorStop(0, this.hexToRgba(baseColor, glowIntensity * 0.8));
      gradient.addColorStop(1, this.hexToRgba(baseColor, 0));
      
      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius * 3, 0, Math.PI * 2);
      this.ctx.fill();
      
      // Draw node core
      this.ctx.fillStyle = baseColor;
      this.ctx.shadowColor = baseColor;
      this.ctx.shadowBlur = 12;
      this.ctx.shadowOffsetX = 0;
      this.ctx.shadowOffsetY = 0;
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fill();
      
      // Draw inner highlight
      const highlight = this.ctx.createRadialGradient(
        node.x - 2, node.y - 2, 0,
        node.x, node.y, node.radius
      );
      highlight.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
      highlight.addColorStop(1, 'rgba(255, 255, 255, 0)');
      this.ctx.fillStyle = highlight;
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      this.ctx.fill();
    }
    
    this.ctx.shadowColor = 'transparent';
  }

  drawCore() {
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    
    // Core glow
    const gradient = this.ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, 40
    );
    
    const coreColor = this.currentState === 'idle' ? '#1a3a6a' : '#2a5aaa';
    gradient.addColorStop(0, this.hexToRgba(coreColor, 0.6));
    gradient.addColorStop(1, this.hexToRgba(coreColor, 0));
    
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, 40, 0, Math.PI * 2);
    this.ctx.fill();
    
    // Core pulse
    const pulseSize = 12 + Math.sin(this.pulsePhase) * 4;
    this.ctx.fillStyle = '#00ffff';
    this.ctx.shadowColor = '#00ffff';
    this.ctx.shadowBlur = 15;
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, pulseSize, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowColor = 'transparent';
  }

  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  animate() {
    this.update();
    this.draw();
    this.animationFrameId = requestAnimationFrame(() => this.animate());
  }

  start() {
    this.animate();
  }

  stop() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  reset() {
    this.currentState = 'idle';
    for (const node of this.nodes) {
      node.state = 'idle';
      node.stateTime = 0;
    }
  }
}

// Export for use in HTML
if (typeof window !== 'undefined') {
  window.NeuralNetwork = NeuralNetwork;
}
