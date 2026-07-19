import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import '../../services/api_service.dart';
import '../../services/tts_service.dart';

const Color kEmerald = Color(0xFF10B981);

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final stt.SpeechToText _speech = stt.SpeechToText();
  final TextEditingController _textController = TextEditingController();

  bool _isListening = false;
  bool _isProcessing = false;
  String _recognizedText = "";
  String _responseText = "";
  bool _isSpeaking = false;

  final List<String> _quickQueries = [
    "खाद (Fertilizer) कब देनी चाहिए?",
    "क्या आज सिंचाई (Irrigation) करनी चाहिए?",
    "ऑर्गेनिक स्प्रे कौन सा सही है?",
    "पास की फसल में बीमारी का कितना खतरा है?",
  ];

  Future<void> _startListening() async {
    bool available = await _speech.initialize(
      onStatus: (status) {
        if (status == "done" || status == "notListening") {
          setState(() => _isListening = false);
        }
      },
      onError: (error) {
        setState(() => _isListening = false);
      },
    );

    if (available) {
      setState(() {
        _isListening = true;
        _recognizedText = "";
      });

      _speech.listen(
        onResult: (result) {
          setState(() {
            _recognizedText = result.recognizedWords;
            _textController.text = _recognizedText;
          });

          if (result.finalResult && _recognizedText.isNotEmpty) {
            _sendQueryToBackend(_recognizedText);
          }
        },
      );
    }
  }

  void _stopListening() {
    _speech.stop();
    setState(() => _isListening = false);
  }

  Future<void> _sendQueryToBackend(String query) async {
    if (query.trim().isEmpty) return;

    setState(() {
      _isProcessing = true;
      _recognizedText = query;
      _responseText = "";
    });

    final res = await ApiService.sendChatMessage(question: query);

    final String reply = res["reply_hindi"] ?? "उत्तर प्राप्त नहीं हो सका।";

    setState(() {
      _responseText = reply;
      _isProcessing = false;
    });

    // Speak reply in Hindi
    _speakReply(reply);
  }

  void _speakReply(String text) async {
    setState(() => _isSpeaking = true);
    await TTSService.speak(text);
    setState(() => _isSpeaking = false);
  }

  void _stopSpeech() async {
    await TTSService.stop();
    setState(() => _isSpeaking = false);
  }

  @override
  void dispose() {
    _textController.dispose();
    _speech.stop();
    TTSService.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("AI Crop Doctor Chatbot", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Suggestion Chips
          Container(
            height: 50,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _quickQueries.length,
              itemBuilder: (context, idx) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ActionChip(
                    backgroundColor: const Color(0xFF1E293B),
                    side: BorderSide(color: kEmerald.withValues(alpha: 0.4)),
                    label: Text(
                      _quickQueries[idx],
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    onPressed: () {
                      _textController.text = _quickQueries[idx];
                      _sendQueryToBackend(_quickQueries[idx]);
                    },
                  ),
                );
              },
            ),
          ),

          // Main Chat Area
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Mic Indicator Circle
                  GestureDetector(
                    onTap: _isListening ? _stopListening : _startListening,
                    child: Container(
                      width: 90,
                      height: 90,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isListening ? Colors.redAccent : kEmerald,
                        boxShadow: [
                          BoxShadow(
                            color: (_isListening ? Colors.redAccent : kEmerald).withValues(alpha: 0.4),
                            blurRadius: 20,
                            spreadRadius: 4,
                          ),
                        ],
                      ),
                      child: Icon(
                        _isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                        size: 42,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _isListening ? "Listening... बोलिये" : "Tap mic or type question below",
                    style: const TextStyle(color: Colors.white70, fontSize: 13),
                  ),
                  const SizedBox(height: 20),

                  // User Question Bubble
                  if (_recognizedText.isNotEmpty)
                    Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        margin: const EdgeInsets.only(left: 40, bottom: 16),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: kEmerald.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: kEmerald.withValues(alpha: 0.5)),
                        ),
                        child: Text(
                          _recognizedText,
                          style: const TextStyle(color: Colors.white, fontSize: 14),
                        ),
                      ),
                    ),

                  // Thinking Indicator
                  if (_isProcessing)
                    const Padding(
                      padding: EdgeInsets.all(20),
                      child: Column(
                        children: [
                          CircularProgressIndicator(color: kEmerald),
                          SizedBox(height: 10),
                          Text("AI Crop Doctor सोच रहा है...", style: TextStyle(color: Colors.white70)),
                        ],
                      ),
                    ),

                  // AI Response Bubble
                  if (_responseText.isNotEmpty && !_isProcessing)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: kEmerald.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Row(
                                children: [
                                  Icon(Icons.health_and_safety_rounded, color: kEmerald, size: 20),
                                  SizedBox(width: 8),
                                  Text(
                                    "AI Crop Doctor (हिंदी)",
                                    style: TextStyle(color: kEmerald, fontWeight: FontWeight.bold, fontSize: 15),
                                  ),
                                ],
                              ),
                              IconButton(
                                icon: Icon(
                                  _isSpeaking ? Icons.stop_circle : Icons.volume_up_rounded,
                                  color: kEmerald,
                                ),
                                onPressed: _isSpeaking ? _stopSpeech : () => _speakReply(_responseText),
                              ),
                            ],
                          ),
                          const Divider(color: Colors.white12),
                          Text(
                            _responseText,
                            style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Text Input Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            color: const Color(0xFF1E293B),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      hintText: "सवाल पूछें (e.g. खाद कब डालें?)...",
                      hintStyle: TextStyle(color: Colors.white38),
                      border: InputBorder.none,
                    ),
                    onSubmitted: _sendQueryToBackend,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send_rounded, color: kEmerald),
                  onPressed: () => _sendQueryToBackend(_textController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}