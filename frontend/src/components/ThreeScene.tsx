/**
 * 3D scene rendering the furniture layout using React Three Fiber.
 * Each furniture piece is represented as a box with its real dimensions.
 */

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Box, Text, Environment, Grid } from "@react-three/drei";
import type { FurniturePiece } from "../types";

interface Props {
    furniture: FurniturePiece[];
    roomWidth: number;
    roomDepth: number;
    colorPalette: string[];
}

export function ThreeScene({ furniture, roomWidth, roomDepth, colorPalette }: Props) {
    return (
        <div style={{ width: "100%", height: 420, borderRadius: 12, overflow: "hidden", background: "#111118" }}>
            <Canvas
                camera={{ position: [0, 4, 8], fov: 50 }}
                shadows
                gl={{ antialias: true }}
            >
                <ambientLight intensity={0.4} />
                <directionalLight
                    position={[5, 8, 5]}
                    intensity={1.2}
                    castShadow
                    shadow-mapSize={[1024, 1024]}
                />

                {/* Room floor */}
                <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
                    <planeGeometry args={[roomWidth, roomDepth]} />
                    <meshStandardMaterial color="#1e1e2e" roughness={0.8} />
                </mesh>

                {/* Room walls (wireframe) */}
                <mesh position={[0, 1.5, -roomDepth / 2]}>
                    <planeGeometry args={[roomWidth, 3]} />
                    <meshStandardMaterial color="#252535" roughness={1} />
                </mesh>
                <mesh position={[-roomWidth / 2, 1.5, 0]} rotation={[0, Math.PI / 2, 0]}>
                    <planeGeometry args={[roomDepth, 3]} />
                    <meshStandardMaterial color="#222232" roughness={1} />
                </mesh>

                {/* Floor grid */}
                <Grid
                    args={[roomWidth * 2, roomDepth * 2]}
                    cellSize={0.5}
                    cellThickness={0.3}
                    cellColor="#2a2a3a"
                    sectionSize={2}
                    sectionThickness={0.5}
                    sectionColor="#3a3a5a"
                    fadeDistance={20}
                    position={[0, 0, 0]}
                />

                {/* Furniture boxes */}
                {furniture.map((piece, idx) => {
                    const color = piece.color || colorPalette[idx % colorPalette.length] || "#7c6ef0";
                    const { w, h, d } = piece.dimensions;
                    const { x, y, z } = piece.position;
                    const rotY = (piece.rotation * Math.PI) / 180;

                    return (
                        <group key={piece.id} position={[x, y + h / 2, z]} rotation={[0, rotY, 0]}>
                            <Box args={[w, h, d]} castShadow receiveShadow>
                                <meshStandardMaterial color={color} roughness={0.6} metalness={0.1} />
                            </Box>
                            <Text
                                position={[0, h / 2 + 0.15, 0]}
                                fontSize={0.18}
                                color="#e8e8ec"
                                anchorX="center"
                                anchorY="bottom"
                                maxWidth={1.5}
                            >
                                {piece.name}
                            </Text>
                        </group>
                    );
                })}

                <OrbitControls
                    makeDefault
                    minPolarAngle={0}
                    maxPolarAngle={Math.PI / 2.1}
                    dampingFactor={0.1}
                    enableDamping
                />
                <Environment preset="city" />
            </Canvas>
        </div>
    );
}
