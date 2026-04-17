import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

const OrbVisualizer = ({ orbState, listening }) => {
  const containerRef = useRef(null)
  const sceneRef = useRef(null)
  const rendererRef = useRef(null)
  const orbRef = useRef(null)
  const particlesRef = useRef([])

  useEffect(() => {
    if (!containerRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0e27)
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.z = 3

    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Create orb geometry
    const geometry = new THREE.IcosahedronGeometry(1, 5)
    const material = new THREE.MeshPhongMaterial({
      color: 0x0099FF,
      emissive: 0x0066AA,
      wireframe: false,
      shininess: 100
    })
    const orb = new THREE.Mesh(geometry, material)
    scene.add(orb)
    orbRef.current = orb

    // Lighting
    const light1 = new THREE.PointLight(0x0099FF, 1, 100)
    light1.position.set(5, 5, 5)
    scene.add(light1)

    const light2 = new THREE.PointLight(0xFF0099, 0.5, 100)
    light2.position.set(-5, -5, 5)
    scene.add(light2)

    const ambientLight = new THREE.AmbientLight(0x404040)
    scene.add(ambientLight)

    // Particle system for neural effects
    const particleGeometry = new THREE.BufferGeometry()
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x00FF99,
      size: 0.05,
      sizeAttenuation: true
    })
    const particles = new THREE.Points(particleGeometry, particleMaterial)
    scene.add(particles)
    particlesRef.current = particles

    // Animation loop
    let animationId
    let time = 0

    const animate = () => {
      animationId = requestAnimationFrame(animate)
      time += 0.016

      if (orbRef.current) {
        // Rotate orb
        orbRef.current.rotation.x += 0.002
        orbRef.current.rotation.y += 0.003

        // Update material color
        const color = new THREE.Color(orbState.color || '#0099FF')
        orbRef.current.material.color = color
        orbRef.current.material.emissive = color.clone().multiplyScalar(0.5)

        // Pulse based on intensity
        const pulse = 1.0 + Math.sin(time * orbState.intensity) * 0.1
        orbRef.current.scale.set(
          orbState.scale * pulse,
          orbState.scale * pulse,
          orbState.scale * pulse
        )

        // If listening, animate more actively
        if (listening) {
          orbRef.current.rotation.z += 0.005
        }
      }

      // Update particles
      if (orbState.neural_firing && orbState.neural_firing.length > 0) {
        updateParticles(orbState.neural_firing, time)
      }

      renderer.render(scene, camera)
    }

    animate()

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current) return
      const width = containerRef.current.clientWidth
      const height = containerRef.current.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      cancelAnimationFrame(animationId)
      if (containerRef.current && rendererRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement)
      }
      geometry.dispose()
      material.dispose()
      renderer.dispose()
    }
  }, [])

  // Update particle positions when neural firing pattern changes
  const updateParticles = (neuralFiring, time) => {
    if (!particlesRef.current || neuralFiring.length === 0) return

    const positions = new Float32Array(neuralFiring.length * 3)
    
    neuralFiring.forEach((particle, idx) => {
      positions[idx * 3] = particle.x + Math.sin(time + idx) * 0.5
      positions[idx * 3 + 1] = particle.y + Math.cos(time + idx) * 0.5
      positions[idx * 3 + 2] = particle.z
    })

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    particlesRef.current.geometry = geometry
  }

  return (
    <div className="orb-container">
      <div ref={containerRef} className="orb-canvas"></div>
      <div className="orb-info">
        <h2>Neural Engine</h2>
        <div className="stats">
          <div>Intensity: {(orbState.intensity * 100).toFixed(0)}%</div>
          <div>Status: {orbState.intensity > 0.5 ? '🔥 Active' : '🟢 Ready'}</div>
          <div>Neurons: {orbState.neural_firing?.length || 0}</div>
        </div>
      </div>
    </div>
  )
}

export default OrbVisualizer
