import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:avatar_glow/avatar_glow.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;

void main() {
  runApp(const SamiApp());
}

class SamiApp extends StatelessWidget {
  const SamiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SAMi Voice Assistant',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.blueAccent,
        scaffoldBackgroundColor: const Color(0xFF050505),
        useMaterial3: true,
      ),
      home: const VoiceAssistantScreen(),
    );
  }
}

class VoiceAssistantScreen extends StatefulWidget {
  const VoiceAssistantScreen({super.key});

  @override
  State<VoiceAssistantScreen> createState() => _VoiceAssistantScreenState();
}

class _VoiceAssistantScreenState extends State<VoiceAssistantScreen> with TickerProviderStateMixin {
  late stt.SpeechToText _speech;
  late FlutterTts _flutterTts;
  bool _isListening = false;
  bool _isSpeaking = false;
  String _text = "Hi! I'm SAMi 🐼";
  double _confidence = 1.0;
  final TextEditingController _textController = TextEditingController();
  
  // Animation Controllers
  late AnimationController _breathingController;
  late Animation<double> _breathingAnimation;

  // Socket IO
  IO.Socket? socket;
  String _backendUrl = "http://192.168.0.101:5000"; 
  bool _isConnected = false;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _flutterTts = FlutterTts();
    _initPermissions();
    
    // Breathing Animation for Logo
    _breathingController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
    
    _breathingAnimation = Tween<double>(begin: 0.9, end: 1.05).animate(
      CurvedAnimation(parent: _breathingController, curve: Curves.easeInOut),
    );

    // Auto-connect on startup
    _initSocket();
  }

  @override
  void dispose() {
    _textController.dispose();
    _speech.stop();
    _flutterTts.stop();
    _breathingController.dispose();
    socket?.dispose();
    super.dispose();
  }

  void _showConnectionDialog() {
    TextEditingController controller = TextEditingController(text: _backendUrl);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E1E1E),
        title: Text("Connect Brain", style: GoogleFonts.poppins(color: Colors.white)),
        content: TextField(
          controller: controller,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            labelText: "Backend URL",
            labelStyle: const TextStyle(color: Colors.white70),
            hintText: "http://192.168.0.xxx:5000",
            hintStyle: TextStyle(color: Colors.white38),
            enabledBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.white30), borderRadius: BorderRadius.circular(12)),
            focusedBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.pinkAccent), borderRadius: BorderRadius.circular(12)),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
               setState(() {
                 _backendUrl = controller.text;
               });
               Navigator.pop(ctx);
               _initSocket();
            },
            child: const Text("Connect", style: TextStyle(color: Colors.pinkAccent)),
          )
        ],
      ),
    );
  }

  Future<void> _speak(String text) async {
    if (!mounted) return;
    setState(() => _isSpeaking = true);
    
    await _flutterTts.setLanguage("en-US");
    
    _flutterTts.setCompletionHandler(() {
      if (mounted) setState(() => _isSpeaking = false);
    });

    await _flutterTts.speak(text);
  }

  // Duplicate initState removed

  // ... (dispose and other methods) ... Note: I need to be careful with replace context. 
  // Let's target _initSocket and listeners specifically.

  void _initSocket() {
    print("Connecting to $_backendUrl...");
    
    // Cleanup existing socket if any
    socket?.disconnect();
    socket?.dispose();

    socket = IO.io(_backendUrl, <String, dynamic>{
      'transports': ['websocket', 'polling'], // Allow polling for better stability
      'autoConnect': false,
    });
    
    socket!.connect();
    socket!.onConnect((_) {
      print("Socket Connected!"); // Debug log
      setState(() => _isConnected = true);
      _speak("Connected to SAMi.");
    });
    
    socket!.onDisconnect((_) {
      print("Socket Disconnected"); // Debug log
      setState(() => _isConnected = false);
    });
    
    socket!.on('conversation_update', (data) {
       // Check for both 'model' (old) and 'sami' (new audio engine)
       if (data != null && (data['role'] == 'model' || data['role'] == 'sami')) {
          String reply = data['text'];
          setState(() { _text = reply; });
          _speak(reply); 
       }
    });

    socket!.on('phone_control', (data) async {
       if (data != null && data['action'] == 'open_url') {
          _speak("Opening ${data['label'] ?? 'page'}");
          await _launchUrl(data['url']);
       }
    });
  }

  Future<void> _launchUrl(String urlString) async {
    final Uri url = Uri.parse(urlString);
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      _speak("Could not open that link.");
    }
  }

  Future<void> _initPermissions() async {
    await Permission.microphone.request();
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) => setState(() {
            _text = val.recognizedWords;
            if (val.finalResult) {
              _processCommand(_text);
            }
          }),
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  void _processCommand(String command) {
    command = command.toLowerCase();
    if (_isConnected) {
       socket?.emit('text_command', {'text': command});
    } else {
       _speak("Please connect to the brain first.");
    }
  }

  // Duplicate _speak removed


  // View State
  String _currentView = 'avatar'; // 'avatar' or 'screen'

  // Polling Timer for Live Screen
  int _frameTimestamp = 0;
  
  void _toggleView(String view) {
    setState(() {
      _currentView = view;
      if (view == 'screen') {
        _updateFrameTimestamp();
      }
    });
  }

  void _updateFrameTimestamp() async {
    while (_currentView == 'screen' && mounted) {
      await Future.delayed(const Duration(milliseconds: 200)); // 5 FPS polling
      setState(() {
        _frameTimestamp = DateTime.now().millisecondsSinceEpoch;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false, 
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF2E0225), // Deep Purple/Pink
              Color(0xFF050505), // Black
              Color(0xFF0F0F2E), // Deep Blue
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Top Status Bar & Mode Switch
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                      // Status Pill
                     Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: _isConnected ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: _isConnected ? Colors.green : Colors.red, width: 1),
                      ),
                      child: Row(
                        children: [
                          Icon(_isConnected ? Icons.cloud_done : Icons.cloud_off, 
                               color: _isConnected ? Colors.greenAccent : Colors.redAccent, size: 14),
                          const SizedBox(width: 8),
                          Text(_isConnected ? "ONLINE" : "OFFLINE", 
                               style: GoogleFonts.poppins(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.settings, color: Colors.white54),
                      onPressed: _showConnectionDialog,
                    )
                  ],
                ),
              ),

              // Mode Switcher Buttons
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 40),
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: Colors.white12),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () => _toggleView('avatar'),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: _currentView == 'avatar' ? Colors.pinkAccent : Colors.transparent,
                            borderRadius: BorderRadius.circular(25),
                          ),
                          child: Center(
                            child: Text(
                              "AI AVATAR",
                              style: GoogleFonts.orbitron(
                                color: Colors.white, 
                                fontSize: 12, 
                                fontWeight: FontWeight.bold
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: GestureDetector(
                        onTap: () => _toggleView('screen'),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: _currentView == 'screen' ? Colors.blueAccent : Colors.transparent,
                            borderRadius: BorderRadius.circular(25),
                          ),
                          child: Center(
                            child: Text(
                              "LIVE SCREEN",
                              style: GoogleFonts.orbitron(
                                color: Colors.white, 
                                fontSize: 12, 
                                fontWeight: FontWeight.bold
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),

              // MAIN CONTENT AREA (Avatar or Screen)
              Expanded(
                flex: 4,
                child: _currentView == 'avatar' 
                  ? _buildAvatarView() 
                  : _buildLiveScreenView(),
              ),

              // WAVEFORM (Only on Avatar Mode or reduced)
              if (_currentView == 'avatar')
                 Padding(
                   padding: const EdgeInsets.symmetric(vertical: 20),
                   child: AnimatedWaveform(active: _isListening || _isSpeaking),
                 ),

              // TEXT OUTPUT (Reduced Height)
              Expanded(
                flex: 2,
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.white10),
                  ),
                  child: SingleChildScrollView(
                    child: Text(
                      _text,
                      textAlign: TextAlign.center,
                      style: GoogleFonts.poppins(
                        fontSize: 16,
                        fontWeight: FontWeight.w400,
                        height: 1.4,
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ),
                ),
              ),

              // BOTTOM INPUT
              Padding(
                padding: const EdgeInsets.only(bottom: 20, left: 24, right: 24, top: 10),
                child: Row(
                  children: [
                    // Mic
                    AvatarGlow(
                      animate: _isListening,
                      glowColor: Colors.blueAccent,
                      endRadius: 30.0,
                      duration: const Duration(milliseconds: 2000),
                      child: GestureDetector(
                        onTap: _listen, 
                        child: Container(
                          width: 55,
                          height: 55,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [Colors.pinkAccent, Colors.purpleAccent]),
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(color: Colors.pinkAccent.withOpacity(0.5), blurRadius: 15, offset: const Offset(0, 5))
                            ],
                          ),
                          child: Icon(_isListening ? Icons.graphic_eq : Icons.mic, color: Colors.white, size: 28),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Container(
                        height: 50,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(25),
                          border: Border.all(color: Colors.white12),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _textController,
                                style: const TextStyle(color: Colors.white),
                                decoration: const InputDecoration(
                                  border: InputBorder.none,
                                  hintText: "Type command...",
                                  hintStyle: TextStyle(color: Colors.white38),
                                  contentPadding: EdgeInsets.symmetric(horizontal: 20),
                                ),
                                onSubmitted: (val) {
                                  if (val.trim().isNotEmpty) {
                                    _processCommand(val.trim());
                                    _textController.clear();
                                  }
                                },
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.send_rounded, color: Colors.white70),
                              onPressed: () {
                                if (_textController.text.trim().isNotEmpty) {
                                  _processCommand(_textController.text.trim());
                                  _textController.clear();
                                }
                              },
                            )
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatarView() {
    return Center(
      child: ScaleTransition(
        scale: _breathingAnimation,
        child: Container(
          height: 200,
          width: 200,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.pinkAccent.withOpacity(0.4),
                blurRadius: 50,
                spreadRadius: 10,
              ),
            ],
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              AvatarGlow(
                animate: _isListening,
                glowColor: Colors.pinkAccent,
                duration: const Duration(milliseconds: 1500),
                repeat: true,
                endRadius: 120.0,
                child: const SizedBox(),
              ),
              ClipOval(
                child: Image.asset('assets/sami_logo.png', fit: BoxFit.cover, height: 180, width: 180),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLiveScreenView() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: Colors.black,
        border: Border.all(color: Colors.blueAccent, width: 2),
        borderRadius: BorderRadius.circular(10),
        boxShadow: [BoxShadow(color: Colors.blueAccent.withOpacity(0.3), blurRadius: 20)],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: _isConnected 
          ? Image.network(
              "$_backendUrl/current_frame?t=$_frameTimestamp",
              fit: BoxFit.contain,
              gaplessPlayback: true,
              errorBuilder: (ctx, _, __) => const Center(child: Text("Connecting to Feed...", style: TextStyle(color: Colors.white54))),
            )
          : const Center(child: Text("OFFLINE", style: TextStyle(color: Colors.red))),
      ),
    );
  }
}

class AnimatedWaveform extends StatefulWidget {
  final bool active;
  const AnimatedWaveform({super.key, required this.active});

  @override
  State<AnimatedWaveform> createState() => _AnimatedWaveformState();
}

class _AnimatedWaveformState extends State<AnimatedWaveform> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1000))..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.active) return const SizedBox(height: 30);

    return SizedBox(
      height: 30,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(5, (index) {
          return AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final double height = 10 + 20 * (0.5 + 0.5 *  
                  (index % 2 == 0 ? 
                    _controller.value 
                    : (1 - _controller.value))); 
              return Container(
                width: 6,
                height: height,
                margin: const EdgeInsets.symmetric(horizontal: 3),
                decoration: BoxDecoration(
                  color: Colors.pinkAccent,
                  borderRadius: BorderRadius.circular(3),
                  boxShadow: [
                    BoxShadow(color: Colors.pinkAccent.withOpacity(0.6), blurRadius: 5)
                  ]
                ),
              );
            },
          );
        }),
      ),
    );
  }
}
