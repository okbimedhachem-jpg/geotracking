import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import L from 'leaflet'

const defaultPosition = [36.8065, 10.1815]

const vehicleIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

export default function App() {
  const [position, setPosition] = useState(defaultPosition)
  const [speed, setSpeed] = useState(0)
  const [userId, setUserId] = useState(25)

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws')

    socket.onopen = () => {
      console.log('WebSocket connecté')
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setUserId(data.user_id)
      setPosition([data.latitude, data.longitude])
      setSpeed(data.speed || 0)
    }

    socket.onclose = () => {
      console.log('WebSocket fermé')
    }

    return () => socket.close()
  }, [])

  return (
    <div className="app">
      <div className="header">
        <h1>GeoTracking</h1>
        <div className="stats">
          <span>Véhicule #{userId}</span>
          <span>Vitesse: {speed} km/h</span>
        </div>
      </div>

      <MapContainer center={position} zoom={15} scrollWheelZoom={true}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Circle center={position} radius={50} color="blue" />
        <Marker position={position} icon={vehicleIcon}>
          <Popup>
            <strong>Véhicule</strong><br />
            Latitude: {position[0]}<br />
            Longitude: {position[1]}<br />
            Vitesse: {speed} km/h
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
