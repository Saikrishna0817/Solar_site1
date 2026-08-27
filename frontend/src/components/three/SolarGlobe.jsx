import { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';

const isWebGLAvailable = () => {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
  } catch (e) {
    return false;
  }
};

const EnergyOrb = () => {
  const meshRef = useRef();
  const glowRef = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (meshRef.current) {
      meshRef.current.rotation.y = t * 0.15;
      meshRef.current.rotation.x = Math.sin(t * 0.1) * 0.1;
    }
    if (glowRef.current) {
      glowRef.current.scale.setScalar(1 + Math.sin(t * 2) * 0.05);
    }
  });

  const gradientMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        color1: { value: new THREE.Color('#F5A623') },
        color2: { value: new THREE.Color('#E8590C') },
        color3: { value: new THREE.Color('#06B6D4') },
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          vUv = uv;
          vNormal = normalize(normalMatrix * normal);
          vPosition = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        uniform vec3 color3;
        varying vec2 vUv;
        varying vec3 vNormal;
        varying vec3 vPosition;
        void main() {
          float fresnel = pow(1.0 - dot(vNormal, vec3(0, 0, 1)), 2.0);
          vec3 col = mix(color1, color2, vUv.y);
          col = mix(col, color3, fresnel * 0.6);
          float grid = smoothstep(0.02, 0.0, abs(fract(vUv.x * 20.0) - 0.5)) +
                       smoothstep(0.02, 0.0, abs(fract(vUv.y * 10.0) - 0.5));
          col += grid * 0.15 * color3;
          float glow = fresnel * 0.8;
          gl_FragColor = vec4(col + glow * color1, 0.95);
        }
      `,
      transparent: true,
    });
  }, []);

  return (
    <group>
      <mesh ref={meshRef} material={gradientMaterial}>
        <sphereGeometry args={[2, 64, 64]} />
      </mesh>
      <mesh ref={glowRef} scale={2.15}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color="#F5A623" transparent opacity={0.06} />
      </mesh>
      <mesh rotation={[Math.PI / 2.5, 0, 0]}>
        <torusGeometry args={[2.8, 0.01, 16, 100]} />
        <meshBasicMaterial color="#06B6D4" transparent opacity={0.3} />
      </mesh>
      <mesh rotation={[Math.PI / 3, 0.5, 0]}>
        <torusGeometry args={[3.0, 0.008, 16, 100]} />
        <meshBasicMaterial color="#F5A623" transparent opacity={0.2} />
      </mesh>
    </group>
  );
};

const FloatingParticles = () => {
  const pointsRef = useRef();
  const count = 200;

  const { geometry, positions } = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 12;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 12;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 12;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    return { geometry: geo, positions: pos };
  }, []);

  useFrame(({ clock }) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = clock.getElapsedTime() * 0.02;
      pointsRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.01) * 0.1;
    }
  });

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.03}
        color="#F5A623"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
};

const GlobeCanvas = () => {
  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[5, 5, 5]} intensity={1} color="#F5A623" />
      <pointLight position={[-5, -3, 5]} intensity={0.5} color="#06B6D4" />
      <EnergyOrb />
      <FloatingParticles />
      <Stars radius={20} depth={50} count={1500} factor={3} saturation={0.2} fade speed={0.5} />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.5}
        maxPolarAngle={Math.PI / 1.5}
        minPolarAngle={Math.PI / 3}
      />
    </>
  );
};

const SolarGlobe = ({ className = '' }) => {
  const [webglAvailable, setWebglAvailable] = useState(true);

  useEffect(() => {
    setWebglAvailable(isWebGLAvailable());
  }, []);

  if (!webglAvailable) {
    return (
      <div className={`w-full h-full flex items-center justify-center ${className}`}>
        <div className="w-32 h-32 rounded-full bg-gradient-solar opacity-20 animate-pulse" />
      </div>
    );
  }

  return (
    <div className={`w-full h-full ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 6], fov: 50 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'default' }}
        style={{ background: 'transparent' }}
        onCreated={({ gl }) => {
          gl.setClearColor(0x000000, 0);
        }}
      >
        <GlobeCanvas />
      </Canvas>
    </div>
  );
};

export default SolarGlobe;
