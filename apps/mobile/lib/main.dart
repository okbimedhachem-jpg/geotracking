import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const GeoTrackingApp());
}

class GeoTrackingApp extends StatelessWidget {
  const GeoTrackingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: TrackingPage(),
    );
  }
}

class TrackingPage extends StatefulWidget {
  const TrackingPage({super.key});

  @override
  State<TrackingPage> createState() => _TrackingPageState();
}

class _TrackingPageState extends State<TrackingPage> {
  Position? _position;
  String _status = 'Démarrage...';
  late final StreamSubscription<Position> _positionStream;
  late final WebSocketChannel _socket;

  @override
  void initState() {
    super.initState();
    _startTracking();
  }

  Future<void> _startTracking() async {
    final permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      setState(() => _status = 'Permission GPS refusée');
      return;
    }

    _socket = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/ws'),
    );

    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.best,
        distanceFilter: 5,
      ),
    ).listen((position) async {
      setState(() {
        _position = position;
        _status = 'GPS actif';
      });

      final payload = {
        'user_id': 25,
        'latitude': position.latitude,
        'longitude': position.longitude,
        'accuracy': position.accuracy,
        'speed': position.speed * 3.6,
        'heading': position.heading,
        'timestamp': DateTime.now().toIso8601String(),
      };

      try {
        final response = await http.post(
          Uri.parse('http://localhost:8000/api/v1/location'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(payload),
        );

        if (response.statusCode == 200) {
          print('Position envoyée au backend');
        }
      } catch (e) {
        print('Erreur backend: $e');
      }

      _socket.sink.add(jsonEncode(payload));
    });
  }

  @override
  void dispose() {
    _positionStream.cancel();
    _socket.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('GeoTracking'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _status,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            if (_position != null) ...[
              Text('Latitude: ${_position!.latitude}'),
              Text('Longitude: ${_position!.longitude}'),
              Text('Précision: ${_position!.accuracy} m'),
              Text('Vitesse: ${(_position!.speed * 3.6).toStringAsFixed(1)} km/h'),
              Text('Direction: ${_position!.heading.toStringAsFixed(1)}°'),
            ] else ...[
              const Text('En attente de la position GPS...'),
            ],
          ],
        ),
      ),
    );
  }
}
