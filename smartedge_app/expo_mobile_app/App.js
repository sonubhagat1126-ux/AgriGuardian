import React, { useState, useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { 
  StyleSheet, 
  Text, 
  View, 
  ScrollView, 
  SafeAreaView, 
  TouchableOpacity, 
  Modal, 
  TextInput,
  ActivityIndicator,
  Image,
  Dimensions,
  Platform,
  StatusBar as RNStatusBar
} from 'react-native';
import { 
  MaterialCommunityIcons, 
  MaterialIcons, 
  Ionicons 
} from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Speech from 'expo-speech';
import { WebView } from 'react-native-webview';


// Theme Colors matching Flutter AppTheme
const Colors = {
  background: '#121A12',
  surface: '#1E2A1E',
  cardBackground: '#243524',
  textPrimary: '#F1F8F1',
  textSecondary: '#A5C4A5',
  textMuted: '#6B8A6B',
  primaryGreen: '#2E7D32',
  lightGreen: '#4CAF50',
  accentGreen: '#81C784',
  warning: '#FFC107',
  danger: '#E53935',
  healthy: '#4CAF50',
  divider: '#2E3E2E',
  blueAccent: '#2196F3',
  orangeAccent: '#FF9800',
};

// Mock Leaves for Scan Tab
const MOCK_LEAVES = [
  { id: 'healthy', label: 'Tomato Healthy Leaf 🌿', disease: 'Tomato_healthy', confidence: 0.96, advisory: 'आपकी टमाटर की पत्ती पूरी तरह स्वस्थ है। खेत में नमी का स्तर बनाए रखें और जैविक खाद का उपयोग करें।' },
  { id: 'early_blight', label: 'Early Blight Infected Leaf 🍂', disease: 'Tomato_Early_blight', confidence: 0.88, advisory: 'टमाटर में अगेती अंगमारी (Early Blight) रोग पाया गया है। प्रभावित पत्तियों को तुरंत तोड़ लें और कवकनाशी (Fungicide) का छिड़काव करें।' },
  { id: 'late_blight', label: 'Late Blight Infected Leaf 🦠', disease: 'Tomato_Late_blight', confidence: 0.93, advisory: 'टमाटर में पछेती अंगमारी (Late Blight) रोग पाया गया है। नमी अधिक होने से यह फैलता है। सिंचाई कम करें और तांबे युक्त कवकनाशी का छिड़काव करें।' },
];

export default function App() {
  // Navigation & Config
  const [activeTab, setActiveTab] = useState('Home');
  const [dweetName, setDweetName] = useState('10.92.177.160');
  const [tempDweetName, setTempDweetName] = useState('10.92.177.160');
  const [isSettingsVisible, setIsSettingsVisible] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const [boardIP, setBoardIP] = useState('10.92.169.254');

  // Sensor Data
  const [sensorData, setSensorData] = useState({
    temperature: 26.5,
    humidity: 62.0,
    soil_moisture: 42,
    vegetation_ndvi: null,
    satellite_soil: null,
    satellite_temp: null,
    pump_status: false,
    auto_mode: true,
    selected_field: 'none',
    saved_fields: [],
  });

  // Scan Screen State
  const [selectedLeaf, setSelectedLeaf] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [selectedSavedLand, setSelectedSavedLand] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [isSpeakingAdvisory, setIsSpeakingAdvisory] = useState(false);
  
  // Add Field Plot Modal states
  const [isAddFieldModalVisible, setIsAddFieldModalVisible] = useState(false);
  const [addFieldChoice, setAddFieldChoice] = useState('menu'); // 'menu', 'coords'
  const [addFieldName, setAddFieldName] = useState('');
  const [addFieldCrop, setAddFieldCrop] = useState('tomato');
  const [addFieldLat, setAddFieldLat] = useState('');
  const [addFieldLon, setAddFieldLon] = useState('');
  const [isSavingField, setIsSavingField] = useState(false);

  // Camera Capture & Image Picker Helpers
  const takePhoto = async () => {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      if (!permissionResult.granted) {
        alert("Camera permission is required to scan crop leaves!");
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedImage(result.assets[0].uri);
        setSelectedLeaf(null);
        setScanResult(null);
      }
    } catch (e) {
      console.warn("Camera execution error:", e);
      alert("Error starting camera.");
    }
  };

  const pickImage = async () => {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permissionResult.granted) {
        alert("Gallery permission is required to select crop leaves!");
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedImage(result.assets[0].uri);
        setSelectedLeaf(null);
        setScanResult(null);
      }
    } catch (e) {
      console.warn("Image picker error:", e);
      alert("Error selecting image.");
    }
  };

  // Voice Chat State
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatLog, setChatLog] = useState([
    { sender: 'ai', text: 'Namaste! Main aapka AI Crop Doctor hoon. Kheti se juda koi bhi sawal poochiye.' }
  ]);
  const [isAiProcessing, setIsAiProcessing] = useState(false);
  const [isSpeakingChat, setIsSpeakingChat] = useState(false);

  // Scan History list
  const [scanHistory, setScanHistory] = useState([
    { disease: 'Tomato_healthy', confidence: 0.95, timestamp: '18-07-2026 12:45' },
    { disease: 'Tomato_Early_blight', confidence: 0.88, timestamp: '17-07-2026 16:20' }
  ]);

  // Fetch telemetry from board local REST API or ntfy.sh
  const fetchData = async () => {
    try {
      const isLocalIP = dweetName.includes('.') && !dweetName.includes('ntfy');
      const url = isLocalIP
        ? (dweetName.startsWith('http') ? dweetName : `http://${dweetName}:8000/api/data`)
        : (dweetName.startsWith('http') ? `${dweetName}/json?poll=1` : `https://ntfy.sh/${dweetName}/json?poll=1`);
        
      const response = await fetch(url);
      
      if (isLocalIP) {
        // Direct local network REST response
        const payload = await response.json();
        setSensorData(prev => ({
          ...prev,
          temperature: payload.temperature ?? prev.temperature,
          humidity: payload.humidity ?? prev.humidity,
          soil_moisture: payload.soil_moisture ?? prev.soil_moisture,
          pump_status: payload.pump_status ?? payload.pump ?? prev.pump_status,
          auto_mode: payload.auto_mode ?? prev.auto_mode,
          selected_field: payload.selected_field ?? prev.selected_field ?? 'none',
          vegetation_ndvi: payload.vegetation_ndvi !== undefined ? payload.vegetation_ndvi : prev.vegetation_ndvi,
          satellite_soil: payload.satellite_soil !== undefined ? payload.satellite_soil : prev.satellite_soil,
          satellite_temp: payload.satellite_temp !== undefined ? payload.satellite_temp : prev.satellite_temp,
          saved_fields: payload.saved_fields ?? prev.saved_fields ?? [],
        }));
        if (payload.board_ip) {
          setBoardIP(payload.board_ip);
        }
        setLastUpdateTime(new Date());
        setIsOnline(true);
      } else {
        // ntfy.sh response
        const text = await response.text();
        const lines = text.trim().split('\n');
        if (lines.length > 0) {
          const lastLine = lines[lines.length - 1].trim();
          if (lastLine) {
            const packet = JSON.parse(lastLine);
            if (packet.event === 'message' && packet.message) {
              const payload = JSON.parse(packet.message);
              
              setSensorData(prev => ({
                ...prev,
                temperature: payload.temperature ?? prev.temperature,
                humidity: payload.humidity ?? prev.humidity,
                soil_moisture: payload.soil_moisture ?? prev.soil_moisture,
                pump_status: payload.pump_status ?? prev.pump_status,
                auto_mode: payload.auto_mode ?? prev.auto_mode,
                selected_field: payload.selected_field ?? prev.selected_field ?? 'none',
                vegetation_ndvi: payload.vegetation_ndvi !== undefined ? payload.vegetation_ndvi : prev.vegetation_ndvi,
                satellite_soil: payload.satellite_soil !== undefined ? payload.satellite_soil : prev.satellite_soil,
                satellite_temp: payload.satellite_temp !== undefined ? payload.satellite_temp : prev.satellite_temp,
                saved_fields: payload.saved_fields ?? prev.saved_fields ?? [],
              }));
              
              setLastUpdateTime(new Date());
              setIsOnline(true);
            }
          }
        }
      }
    } catch (error) {
      console.warn('ntfy fetch error:', error);
      setIsOnline(false);
    }
  };

  // Poll data every 300ms
  useEffect(() => {
    fetchData(); // initial fetch
    const interval = setInterval(fetchData, 300);
    return () => clearInterval(interval);
  }, [dweetName]);

  // TTS for Chatbot Q&A
  useEffect(() => {
    if (isSpeakingChat) {
      const lastMsg = chatLog[chatLog.length - 1];
      if (lastMsg && lastMsg.sender === 'ai') {
        Speech.speak(lastMsg.text, {
          language: 'hi-IN',
          onDone: () => setIsSpeakingChat(false),
          onError: () => setIsSpeakingChat(false)
        });
      }
    } else {
      Speech.stop();
    }
    return () => Speech.stop();
  }, [isSpeakingChat, chatLog]);

  // TTS for Scan Advisory
  useEffect(() => {
    if (isSpeakingAdvisory && scanResult && scanResult.advisory_hindi) {
      Speech.speak(scanResult.advisory_hindi, {
        language: 'hi-IN',
        onDone: () => setIsSpeakingAdvisory(false),
        onError: () => setIsSpeakingAdvisory(false)
      });
    } else {
      Speech.stop();
    }
    return () => Speech.stop();
  }, [isSpeakingAdvisory, scanResult]);

  // Run Disease Detection using board-side YOLO model
  const handleRunDetection = async () => {
    if (!selectedImage && !selectedLeaf) {
      alert("Please capture or select a leaf first!");
      return;
    }
    setIsScanning(true);
    setScanResult(null);
    setIsSpeakingAdvisory(false);

    try {
      const formData = new FormData();
      
      let uri = "";
      let filename = "leaf_image.jpg";
      let type = "image/jpeg";

      if (selectedImage) {
        uri = selectedImage;
        filename = selectedImage.split('/').pop() || "leaf_image.jpg";
        // Ensure proper filename extension for standard picking
        if (!filename.includes('.')) {
          filename += ".jpg";
        }
      } else {
        filename = selectedLeaf.id === 'early_blight' ? "early_blight.jpg" :
                   selectedLeaf.id === 'late_blight' ? "late_blight.jpg" : "healthy_potato.jpg";
        uri = selectedLeaf.id === 'early_blight' ? "https://raw.githubusercontent.com/datasets/image-classification/master/data/potato_early_blight.jpg" :
              selectedLeaf.id === 'late_blight' ? "https://raw.githubusercontent.com/datasets/image-classification/master/data/potato_late_blight.jpg" :
              "https://raw.githubusercontent.com/datasets/image-classification/master/data/potato_healthy.jpg";
      }

      formData.append('image', {
        uri: uri,
        name: filename,
        type: type
      });

      const targetBoardIP = boardIP || "10.92.169.254";
      const response = await fetch(`http://${dweetName}:8000/api/leaf/detect`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();
      setIsScanning(false);

      if (data.status === 'success' || data.disease) {
        const rawDisease = data.disease || 'healthy';
        const cleanDisease = rawDisease.replace(/_/g, ' ');
        const isHealthy = cleanDisease.toLowerCase().includes('healthy');

        // Dynamically request advisory details from Sarvam AI via the board endpoint!
        let advisoryHindi = "";
        let actionPlan = {
          today: isHealthy 
            ? ['खेत में नमी का निरीक्षण करें', 'स्वस्थ पत्तियों की सुरक्षा बनाए रखें']
            : ['प्रभावित पत्तियों को तुरंत काटकर नष्ट करें', 'नमी को नियंत्रित करें'],
          next_3_days: isHealthy
            ? ['सिंचाई की आवधिक निगरानी करें']
            : ['तांबा युक्त कवकनाशी (Fungicide) का छिड़काव करें', 'सिंचाई का समय कम करें'],
          next_week: isHealthy
            ? ['फसल के सामान्य विकास को रिकॉर्ड करें']
            : ['फसल में सुधार की जांच करें', 'रोग प्रतिरोधक खाद का प्रयोग करें'],
          expected_recovery: isHealthy ? 'N/A' : '10-14 Days'
        };

        try {
          const aiResponse = await fetch(`http://${dweetName}:8000/api/ai/crop-doctor`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              disease: rawDisease,
              confidence: data.confidence || 0.95
            })
          });
          const aiData = await aiResponse.json();
          if (aiData.advisory_hindi) {
            advisoryHindi = aiData.advisory_hindi;
          }
          if (aiData.action_plan) {
            actionPlan = aiData.action_plan;
          }
        } catch (aiErr) {
          console.warn("Failed to get AI advisory, using local default:", aiErr);
          advisoryHindi = selectedLeaf ? selectedLeaf.advisory : "पौधे की सुरक्षा के लिए उचित सिंचाई और जैविक दवाओं का उपयोग करें।";
        }
        
        setScanResult({
          disease_name: cleanDisease,
          confidence: data.confidence || 0.95,
          advisory_hindi: advisoryHindi || "फसल की सुरक्षा के लिए उचित सिंचाई और जैविक दवाओं का उपयोग करें।",
          is_healthy: isHealthy,
          action_plan: actionPlan
        });

        // Add to history
        setScanHistory(prev => [
          {
            disease: rawDisease,
            confidence: data.confidence || 0.95,
            timestamp: new Date().toLocaleDateString('en-GB') + ' ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})
          },
          ...prev
        ]);
      } else if (data.status === 'low_confidence') {
        const topPred = (data.top_predictions && data.top_predictions[0]) || {};
        const cleanDisease = (topPred.disease || "Unknown").replace(/_/g, ' ');
        const isHealthy = cleanDisease.toLowerCase().includes('healthy');

        setScanResult({
          disease_name: cleanDisease + " (Low Confidence ⚠️)",
          confidence: (topPred.confidence || 50) / 100.0,
          advisory_hindi: "पत्ती का चित्र स्पष्ट नहीं है। कृपया बेहतर रोशनी में तस्वीर लें, और कैमरे को पत्ती के करीब रखें।",
          is_healthy: isHealthy,
          is_low_confidence: true,
          action_plan: {
            today: ['पत्ती की साफ़ तस्वीर दोबारा खींचें', 'सुनिश्चित करें कि पत्ती कैमरे के बीच में हो'],
            next_3_days: ['बेहतर रोशनी (धूप) का उपयोग करें'],
            next_week: [],
            expected_recovery: 'N/A'
          }
        });
      } else {
        throw new Error(data.message || "Model failed to return classification.");
      }

    } catch (error) {
      console.warn("Scan upload failed:", error);
      setIsScanning(false);
      
      if (selectedImage) {
        setScanResult({
          disease_name: "Scan Error ❌",
          confidence: 0.0,
          advisory_hindi: `सर्वर से संपर्क विफल: ${error.message || error}। कृपया सुनिश्चित करें कि बोर्ड पर Flask सर्वर चालू है और दोनों डिवाइस एक ही वाई-फाई से जुड़े हैं।`,
          is_healthy: false,
          is_error: true,
          action_plan: {
            today: ['बोर्ड के IDE (App Lab) में Logs चेक करें', 'सुनिश्चित करें कि Flask सर्वर त्रुटियों के बिना चल रहा है'],
            next_3_days: ['जांचें कि बोर्ड का IP settings में सही दर्ज है'],
            next_week: [],
            expected_recovery: 'N/A'
          }
        });
      } else {
        const fallbackDisease = selectedLeaf ? selectedLeaf.disease : "Tomato_healthy";
        const fallbackAdvisory = selectedLeaf ? selectedLeaf.advisory : "ऑफ़लाइन मोड: पौधे का निरीक्षण पूरा हुआ।";
        const fallbackConfidence = selectedLeaf ? selectedLeaf.confidence : 0.95;

        setScanResult({
          disease_name: fallbackDisease.replace(/_/g, ' '),
          confidence: fallbackConfidence,
          advisory_hindi: fallbackAdvisory,
          is_healthy: fallbackDisease.toLowerCase().includes('healthy'),
          action_plan: {
            today: fallbackDisease.toLowerCase().includes('healthy')
              ? ['खेत में नमी का निरीक्षण करें', 'स्वस्थ पत्तियों की सुरक्षा बनाए रखें']
              : ['प्रभावित पत्तियों को तुरंत काटकर नष्ट करें', 'नमी को नियंत्रित करें'],
            next_3_days: fallbackDisease.toLowerCase().includes('healthy')
              ? ['सिंचाई की आवधिक निगरानी करें']
              : ['तांबा युक्त कवकनाशी (Fungicide) का छिड़काव करें', 'सिंचाई का समय कम करें'],
            next_week: fallbackDisease.toLowerCase().includes('healthy')
              ? ['फसल के सामान्य विकास को रिकॉर्ड करें']
              : ['फसल में सुधार की जांच करें', 'रोग प्रतिरोधक खाद का प्रयोग करें'],
            expected_recovery: fallbackDisease.toLowerCase().includes('healthy') ? 'N/A' : '10-14 Days'
          }
        });

        // Add to history
        setScanHistory(prev => [
          {
            disease: fallbackDisease,
            confidence: fallbackConfidence,
            timestamp: new Date().toLocaleDateString('en-GB') + ' ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})
          },
          ...prev
        ]);
      }
    }
  };

  // Save manual land plot coordinates via control API
  const handleManualSaveField = async () => {
    const latNum = parseFloat(addFieldLat);
    const lonNum = parseFloat(addFieldLon);
    
    if (!addFieldName.trim()) {
      alert("Please enter a field name.");
      return;
    }
    if (isNaN(latNum) || isNaN(lonNum)) {
      alert("Please enter valid decimal coordinates.");
      return;
    }
    
    setIsSavingField(true);
    try {
      const response = await fetch(`http://${dweetName}:8000/api/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'save_field_plot',
          value: {
            name: addFieldName.trim(),
            crop: addFieldCrop,
            boundary: [],
            lat: latNum,
            lon: lonNum
          }
        })
      });
      
      const resData = await response.json();
      if (resData.status === 'success') {
        alert(`Plot "${addFieldName}" successfully registered!`);
        // Refresh local data state immediately
        fetchData();
        // Reset states
        setAddFieldName('');
        setAddFieldLat('');
        setAddFieldLon('');
        setAddFieldChoice('menu');
        setIsAddFieldModalVisible(false);
      } else {
        alert("Failed to save: " + (resData.message || "Unknown error"));
      }
    } catch (e) {
      console.warn("Manual save plot failed:", e);
      alert("Server connection failed. Make sure server IP is correct.");
    } finally {
      setIsSavingField(false);
    }
  };

  // Live AI Chatbot Q&A connection to the board server
  const handleSendChat = async (questionText = chatQuestion) => {
    if (!questionText.trim()) return;
    
    // Add user bubble
    const userBubble = { sender: 'user', text: questionText };
    setChatLog(prev => [...prev, userBubble]);
    setChatQuestion('');
    setIsAiProcessing(true);
    setIsSpeakingChat(false);

    try {
      const targetBoardIP = boardIP || "10.92.169.254";
      const response = await fetch(`http://${dweetName}:8000/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          disease: scanResult ? scanResult.disease_name : "Tomato_healthy",
          sensor_data: {
            soil_moisture: sensorData.soil_moisture,
            temperature: sensorData.temperature,
            humidity: sensorData.humidity,
          }
        })
      });

      const data = await response.json();
      setIsAiProcessing(false);

      if (data.status === 'success' && data.reply_hindi) {
        setChatLog(prev => [...prev, { sender: 'ai', text: data.reply_hindi }]);
        setIsSpeakingChat(true);
      } else {
        throw new Error(data.message || "Failed to generate AI response.");
      }
    } catch (error) {
      console.warn("AI Chat request failed, using offline fallback:", error);
      setIsAiProcessing(false);
      
      // Display the actual connection error on screen to help diagnose the issue
      let reply = `कनेक्शन त्रुटि: ${error.message || error}। (लैपटॉप IP: ${dweetName}:8000)`;
      
      setChatLog(prev => [...prev, { sender: 'ai', text: reply }]);
      setIsSpeakingChat(true);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor={Colors.background} />
      
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>AgriGuardian 🌾</Text>
          <View style={styles.onlineBadge}>
            <View style={[styles.onlineDot, { backgroundColor: isOnline ? Colors.healthy : Colors.danger }]} />
            <Text style={styles.onlineText}>
              {isOnline ? 'Live Cloud Feed' : 'Offline / Simulation'}
            </Text>
          </View>
        </View>
        <TouchableOpacity style={styles.settingsBtn} onPress={() => setIsSettingsVisible(true)}>
          <Ionicons name="settings-sharp" size={24} color={Colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Main Tab Render Container */}
      <View style={styles.tabContentContainer}>
        {activeTab === 'Home' && renderHomeTab()}
        {activeTab === 'Map' && renderMapTab()}
        {activeTab === 'Scan' && renderScanTab()}
        {activeTab === 'Voice' && renderVoiceTab()}
        {activeTab === 'Analytics' && renderAnalyticsTab()}
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        {[
          { id: 'Home', icon: 'home-variant', label: 'Home' },
          { id: 'Map', icon: 'map-marker-radius', label: 'Map' },
          { id: 'Scan', icon: 'image-filter-center-focus', label: 'Scan' },
          { id: 'Voice', icon: 'microphone', label: 'Voice' },
          { id: 'Analytics', icon: 'chart-arc', label: 'Analytics' },
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <TouchableOpacity 
              key={tab.id} 
              style={styles.navItem} 
              onPress={() => setActiveTab(tab.id)}
            >
              <MaterialCommunityIcons 
                name={tab.icon} 
                size={24} 
                color={isActive ? Colors.lightGreen : Colors.textMuted} 
              />
              <Text style={[styles.navLabel, { color: isActive ? Colors.lightGreen : Colors.textMuted }]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Cloud Settings Modal */}
      <Modal animationType="slide" transparent={true} visible={isSettingsVisible}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Cloud Settings</Text>
            <Text style={styles.modalSubtitle}>Configure telemetry sync broker topic</Text>
            
            <TextInput
              style={styles.textInput}
              value={tempDweetName}
              onChangeText={setTempDweetName}
              placeholder="e.g. smartedge-agriguardian"
              placeholderTextColor="#556"
            />
            
            <View style={styles.modalActions}>
              <TouchableOpacity 
                style={[styles.modalBtn, styles.cancelBtn]} 
                onPress={() => {
                  setTempDweetName(dweetName);
                  setIsSettingsVisible(false);
                }}
              >
                <Text style={styles.btnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.modalBtn, styles.saveBtn]} 
                onPress={() => {
                  setDweetName(tempDweetName);
                  setIsSettingsVisible(false);
                  setIsOnline(false);
                }}
              >
                <Text style={styles.btnText}>Apply</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Add Field Plot Modal */}
      <Modal animationType="slide" transparent={true} visible={isAddFieldModalVisible}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Farm Plot</Text>
            
            {addFieldChoice === 'menu' ? (
              <View style={{ width: '100%', gap: 12, marginVertical: 16 }}>
                <Text style={[styles.modalSubtitle, { textAlign: 'center' }]}>
                  Choose how you want to add this field
                </Text>
                
                <TouchableOpacity 
                  style={[styles.modalBtn, styles.saveBtn, { width: '100%', padding: 12, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: 12 }]}
                  onPress={() => {
                    setIsAddFieldModalVisible(false);
                    setActiveTab('Map');
                  }}
                >
                  <MaterialCommunityIcons name="map-marker-radius" size={20} color="#FFF" style={{ marginRight: 8 }} />
                  <Text style={styles.btnText}>Draw Boundary on Map</Text>
                </TouchableOpacity>

                <TouchableOpacity 
                  style={[styles.modalBtn, styles.cancelBtn, { width: '100%', padding: 12, borderStyle: 'solid', borderWidth: 1, borderColor: Colors.divider, backgroundColor: Colors.surface, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: 20 }]}
                  onPress={() => {
                    setAddFieldChoice('coords');
                  }}
                >
                  <MaterialCommunityIcons name="keyboard" size={20} color={Colors.textSecondary} style={{ marginRight: 8 }} />
                  <Text style={[styles.btnText, { color: Colors.textSecondary }]}>Enter Manual Coordinates</Text>
                </TouchableOpacity>
                
                <TouchableOpacity 
                  style={[styles.modalBtn, styles.cancelBtn, { width: '100%', padding: 12 }]}
                  onPress={() => setIsAddFieldModalVisible(false)}
                >
                  <Text style={styles.btnText}>Close</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View style={{ width: '100%', marginVertical: 8 }}>
                <Text style={styles.modalSubtitle}>Register Land by GPS coordinates</Text>
                
                <Text style={[styles.cardMutedLabel, { marginTop: 8 }]}>Field Name</Text>
                <TextInput
                  style={styles.textInput}
                  value={addFieldName}
                  onChangeText={setAddFieldName}
                  placeholder="e.g. Backyard Block A"
                  placeholderTextColor="#556"
                />

                <Text style={[styles.cardMutedLabel, { marginTop: 8 }]}>Crop Type</Text>
                <View style={{ borderWidth: 1, borderColor: Colors.divider, borderRadius: 8, backgroundColor: Colors.cardBackground, marginVertical: 6, overflow: 'hidden' }}>
                  <View style={{ flexDirection: 'row', flexWrap: 'wrap', padding: 4 }}>
                    {[
                      { id: 'tomato', label: 'Tomato 🍅' },
                      { id: 'rice', label: 'Rice 🌾' },
                      { id: 'wheat', label: 'Wheat 🌾' },
                      { id: 'maize', label: 'Maize 🌽' },
                    ].map((item) => {
                      const isSel = addFieldCrop === item.id;
                      return (
                        <TouchableOpacity
                          key={item.id}
                          style={{
                            padding: 8,
                            margin: 4,
                            borderRadius: 6,
                            backgroundColor: isSel ? Colors.primaryGreen : Colors.surface,
                            borderWidth: 1,
                            borderColor: isSel ? Colors.accentGreen : Colors.divider,
                          }}
                          onPress={() => setAddFieldCrop(item.id)}
                        >
                          <Text style={{ color: isSel ? '#FFF' : Colors.textSecondary, fontSize: 12, fontWeight: 'bold' }}>{item.label}</Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </View>

                <Text style={[styles.cardMutedLabel, { marginTop: 8 }]}>Latitude (Decimal GPS)</Text>
                <TextInput
                  style={styles.textInput}
                  value={addFieldLat}
                  onChangeText={val => setAddFieldLat(val.replace(/[^0-9.-]/g, ''))}
                  placeholder="e.g. 28.5355"
                  placeholderTextColor="#556"
                  keyboardType="numeric"
                />

                <Text style={[styles.cardMutedLabel, { marginTop: 8 }]}>Longitude (Decimal GPS)</Text>
                <TextInput
                  style={styles.textInput}
                  value={addFieldLon}
                  onChangeText={val => setAddFieldLon(val.replace(/[^0-9.-]/g, ''))}
                  placeholder="e.g. 77.3910"
                  placeholderTextColor="#556"
                  keyboardType="numeric"
                />

                <View style={[styles.modalActions, { marginTop: 20 }]}>
                  <TouchableOpacity 
                    style={[styles.modalBtn, styles.cancelBtn]} 
                    onPress={() => setAddFieldChoice('menu')}
                  >
                    <Text style={styles.btnText}>Back</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={[styles.modalBtn, styles.saveBtn]} 
                    onPress={handleManualSaveField}
                    disabled={isSavingField}
                  >
                    {isSavingField ? (
                      <ActivityIndicator size="small" color="#FFF" />
                    ) : (
                      <Text style={styles.btnText}>Register Plot</Text>
                    )}
                  </TouchableOpacity>
                </View>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );

  // ================= TAB RENDERS =================

  function renderHomeTab() {
    const hasField = sensorData.selected_field && sensorData.selected_field !== 'none';

    return (
      <ScrollView contentContainerStyle={styles.scrollPadding}>
        <Text style={styles.welcomeText}>Namaste, Devansh 🌾</Text>
        <Text style={styles.subWelcomeText}>Aapke khet ka aaj ka haal</Text>

        {/* Health Score Card */}
        {hasField ? (
          <View style={styles.healthCard}>
            <View style={[styles.scoreCircle, { 
              borderColor: (sensorData.vegetation_ndvi ?? 0.65) >= 0.70 ? Colors.healthy : 
                           (sensorData.vegetation_ndvi ?? 0.65) >= 0.55 ? Colors.warning : Colors.danger 
            }]}>
              <Text style={styles.scoreText}>
                {Math.round((sensorData.vegetation_ndvi ?? 0.65) * 100)}
              </Text>
            </View>
            <View style={styles.healthDetails}>
              <Text style={styles.cardMutedLabel}>Crop Health Score</Text>
              <Text style={[styles.healthStatusText, { 
                color: (sensorData.vegetation_ndvi ?? 0.65) >= 0.70 ? Colors.healthy : 
                       (sensorData.vegetation_ndvi ?? 0.65) >= 0.55 ? Colors.orangeAccent : Colors.danger 
              }]}>
                {(sensorData.vegetation_ndvi ?? 0.65) >= 0.70 ? 'Excellent' :
                 (sensorData.vegetation_ndvi ?? 0.65) >= 0.55 ? 'Healthy' :
                 (sensorData.vegetation_ndvi ?? 0.65) >= 0.40 ? 'Moderate Stress' : 'Severe Stress'}
              </Text>
              <Text style={styles.cardMutedSubText}>
                NDVI Index: {(sensorData.vegetation_ndvi ?? 0.65).toFixed(2)} (Live VEDAS Feed)
              </Text>
            </View>
          </View>
        ) : (
          <View style={styles.noFieldBanner}>
            <MaterialCommunityIcons name="map-marker-off" size={24} color={Colors.orangeAccent} style={{ marginRight: 10 }} />
            <View style={{ flex: 1 }}>
              <Text style={styles.noFieldBannerText}>No Active Farm Plot</Text>
              <Text style={styles.noFieldBannerSubtext}>Please select a predefined field or outline custom land on the Map tab to fetch satellite health diagnostics.</Text>
            </View>
          </View>
        )}

        {/* Sensors Grid */}
        <View style={styles.sensorRow}>
          <View style={styles.sensorCard}>
            <MaterialCommunityIcons name="water" size={28} color={Colors.lightGreen} />
            <Text style={styles.sensorVal}>{sensorData.soil_moisture}%</Text>
            <Text style={styles.sensorLabel}>Moisture</Text>
          </View>
          <View style={styles.sensorCard}>
            <MaterialCommunityIcons name="thermometer" size={28} color={Colors.warning} />
            <Text style={styles.sensorVal}>{sensorData.temperature.toFixed(1)}°C</Text>
            <Text style={styles.sensorLabel}>Temperature</Text>
          </View>
          <View style={styles.sensorCard}>
            <MaterialCommunityIcons name="weather-hazy" size={28} color={Colors.accentGreen} />
            <Text style={styles.sensorVal}>{sensorData.humidity.toFixed(1)}%</Text>
            <Text style={styles.sensorLabel}>Humidity</Text>
          </View>
        </View>

        {/* VEDAS Satellite Data Row for Selected Coordinates */}
        {hasField && (
          <>
            <Text style={styles.sectionTitle}>VEDAS Satellite Data (Active Area)</Text>
            <View style={styles.satelliteStatusRow}>
              <View style={[styles.satDetailBox, { borderLeftColor: Colors.blueAccent }]}>
                <MaterialCommunityIcons name="water-percent" size={22} color={Colors.blueAccent} style={{ marginBottom: 4 }} />
                <Text style={styles.satDetailVal}>
                  {Math.round((sensorData.satellite_soil ?? 0.38) * 100)}%
                </Text>
                <Text style={styles.satDetailLabel}>Satellite Moisture</Text>
                <Text style={styles.satDetailSubtext}>{(sensorData.satellite_soil ?? 0.38).toFixed(2)} m³/m³</Text>
              </View>
              <View style={[styles.satDetailBox, { borderLeftColor: Colors.orangeAccent }]}>
                <MaterialCommunityIcons name="thermometer-lines" size={22} color={Colors.orangeAccent} style={{ marginBottom: 4 }} />
                <Text style={styles.satDetailVal}>
                  {(sensorData.satellite_temp ?? 32.2).toFixed(1)}°C
                </Text>
                <Text style={styles.satDetailLabel}>Surface Temp</Text>
                <Text style={styles.satDetailSubtext}>Land Surface</Text>
              </View>
            </View>
          </>
        )}

        {/* Weather Advisor Banner */}
        <View style={[styles.weatherBanner, { borderLeftColor: Colors.lightGreen }]}>
          <Ionicons name="partly-sunny" size={32} color={Colors.accentGreen} style={{ marginRight: 12 }} />
          <View style={{ flex: 1 }}>
            <Text style={styles.weatherTitle}>Aaj Baarish Ka Chance Kam Hai</Text>
            <Text style={styles.weatherBody}>Irrigation Suggestion: Shaam 12 min paani do</Text>
          </View>
        </View>

        {/* Alerts Section */}
        <Text style={styles.sectionTitle}>Quick Alerts</Text>
        <View style={[styles.alertTile, { borderLeftColor: Colors.warning }]}>
          <MaterialCommunityIcons name="water-alert-outline" size={20} color={Colors.warning} style={{ marginRight: 10 }} />
          <Text style={styles.alertText}>Aaj shaam irrigation ki zarurat hai</Text>
        </View>
        <View style={[styles.alertTile, { borderLeftColor: Colors.healthy }]}>
          <MaterialCommunityIcons name="check-decagram-outline" size={20} color={Colors.healthy} style={{ marginRight: 10 }} />
          <Text style={styles.alertText}>Koi disease detect nahi hua is hafte</Text>
        </View>

        {/* Quick Action Links */}
        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.actionBtn} onPress={() => setActiveTab('Scan')}>
            <Ionicons name="camera" size={24} color="#FFF" />
            <Text style={styles.actionBtnLabel}>Scan Leaf</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionBtn} onPress={() => setActiveTab('Voice')}>
            <Ionicons name="mic" size={24} color="#FFF" />
            <Text style={styles.actionBtnLabel}>Ask AI</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  }

  function renderMapTab() {
    // Clean and parse host/port from dweetName to support any input formats:
    // "10.92.177.160", "10.92.177.160:8000", "http://10.92.177.160:8000", etc.
    let host = dweetName.trim().replace(/^https?:\/\//i, ''); // strip prefix
    host = host.split('/')[0]; // strip paths
    if (!host.includes(':')) {
      host = `${host}:8000`; // append port if not present
    }
    const mapUrl = `http://${host}/?mode=map&v=15`;
    
    return (
      <View style={{ flex: 1, backgroundColor: Colors.background }}>
        <WebView 
          key={mapUrl} // Forces React to recreate the WebView if IP or URL changes
          source={{ uri: mapUrl }}
          style={{ flex: 1, backgroundColor: Colors.background }}
          javaScriptEnabled={true}
          domStorageEnabled={true}
          geolocationEnabled={true} // Enable HTML5 Geolocation inside the WebView on Android
          cacheEnabled={false} // Prevent caching of error pages
          cacheMode="LOAD_NO_CACHE" // Android: always query fresh copy from network
          startInLoadingState={true}
          onError={(syntheticEvent) => {
            const { nativeEvent } = syntheticEvent;
            console.warn('WebView error: ', nativeEvent.description, nativeEvent.code);
          }}
          onHttpError={(syntheticEvent) => {
            const { nativeEvent } = syntheticEvent;
            console.warn('WebView HTTP error: ', nativeEvent.statusCode, nativeEvent.description);
          }}
          injectedJavaScript={`
            (function() {
              var origLog = console.log;
              var origWarn = console.warn;
              var origError = console.error;
              
              console.log = function() {
                window.ReactNativeWebView.postMessage(JSON.stringify({type: 'log', data: Array.from(arguments).map(String)}));
                origLog.apply(console, arguments);
              };
              console.warn = function() {
                window.ReactNativeWebView.postMessage(JSON.stringify({type: 'warn', data: Array.from(arguments).map(String)}));
                origWarn.apply(console, arguments);
              };
              console.error = function() {
                window.ReactNativeWebView.postMessage(JSON.stringify({type: 'error', data: Array.from(arguments).map(String)}));
                origError.apply(console, arguments);
              };
              window.onerror = function(message, source, lineno, colno, error) {
                window.ReactNativeWebView.postMessage(JSON.stringify({
                  type: 'error', 
                  data: [String(message), (source || '') + ':' + lineno + ':' + colno]
                }));
                return false;
              };
            })();
            true;
          `}
          onMessage={(event) => {
            try {
              const msg = JSON.parse(event.nativeEvent.data);
              console.log(`[WebView ${msg.type.toUpperCase()}]`, msg.data.join(' '));
            } catch(e) {
              console.log('[WebView Message]', event.nativeEvent.data);
            }
          }}
          renderLoading={() => (
            <View style={styles.mapLoadingContainer}>
              <ActivityIndicator size="large" color={Colors.lightGreen} />
              <Text style={styles.mapLoadingText}>Loading Satellite Map...</Text>
            </View>
          )}
        />
      </View>
    );
  }

  function renderScanTab() {
    return (
      <ScrollView contentContainerStyle={styles.scrollPadding}>
        <Text style={styles.tabHeading}>YOLO Disease Detection</Text>
        
        {/* Real Camera Action Buttons */}
        <View style={styles.cameraActionRow}>
          <TouchableOpacity style={styles.cameraIconBtn} onPress={takePhoto}>
            <Ionicons name="camera" size={20} color="#FFF" />
            <Text style={styles.cameraIconBtnText}>Take Photo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.cameraIconBtn} onPress={pickImage}>
            <Ionicons name="images" size={20} color="#FFF" />
            <Text style={styles.cameraIconBtnText}>From Gallery</Text>
          </TouchableOpacity>
        </View>

        {/* Mock leaf selector */}
        <Text style={styles.fieldLabel}>Or select leaf sample to simulate scan:</Text>
        <View style={styles.leafSelectorRow}>
          {MOCK_LEAVES.map((leaf) => {
            const isSel = selectedLeaf?.id === leaf.id && !selectedImage;
            return (
              <TouchableOpacity 
                key={leaf.id} 
                style={[styles.leafSelectorBtn, isSel && styles.leafSelected]} 
                onPress={() => {
                  setSelectedLeaf(leaf);
                  setSelectedImage(null);
                  setScanResult(null);
                }}
              >
                <Text style={[styles.leafBtnText, { color: isSel ? '#FFF' : Colors.textSecondary }]}>
                  {leaf.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Scan Camera Area */}
        <View style={styles.cameraBox}>
          {isScanning ? (
            <View style={styles.cameraProgress}>
              <ActivityIndicator size="large" color={Colors.lightGreen} />
              <Text style={styles.cameraProgressText}>Running YOLOv11 Leaf Classification...</Text>
            </View>
          ) : selectedImage ? (
            <View style={styles.cameraPreviewBox}>
              <Image source={{ uri: selectedImage }} style={styles.capturedImagePreview} />
              <TouchableOpacity style={styles.clearImageBtn} onPress={() => setSelectedImage(null)}>
                <Ionicons name="close-circle" size={32} color={Colors.danger} />
              </TouchableOpacity>
            </View>
          ) : selectedLeaf ? (
            <View style={styles.cameraPreviewBox}>
              <Ionicons name="checkmark-circle" size={48} color={Colors.lightGreen} />
              <Text style={styles.cameraPreviewText}>{selectedLeaf.label} Ready</Text>
            </View>
          ) : (
            <View style={styles.cameraPreviewBox}>
              <Ionicons name="scan-circle" size={64} color={Colors.textMuted} />
              <Text style={styles.cameraPreviewText}>Choose a leaf sample above or capture one</Text>
            </View>
          )}
        </View>

        {/* Action Button */}
        <TouchableOpacity 
          style={[styles.scanActionBtn, (!selectedLeaf && !selectedImage) && styles.btnDisabled]} 
          onPress={handleRunDetection}
          disabled={(!selectedLeaf && !selectedImage) || isScanning}
        >
          <Text style={styles.scanActionBtnText}>Run Disease Scan ⚡</Text>
        </TouchableOpacity>

        {/* Scan Result Details */}
        {scanResult && (
          <View style={styles.resultBox}>
            <View style={styles.resultBoxHeader}>
              <View style={{ flex: 1 }}>
                <Text style={styles.resultTitle}>{scanResult.disease_name}</Text>
                <Text style={[
                  styles.severityText,
                  { color: scanResult.is_error ? Colors.danger : (scanResult.is_healthy ? Colors.healthy : (scanResult.is_low_confidence ? Colors.warning : Colors.danger)) }
                ]}>
                  {scanResult.is_error ? '❌ System Error' : (scanResult.is_healthy ? '🟢 Healthy Crop' : (scanResult.is_low_confidence ? '⚠️ Low Confidence Scan' : '🔴 Infection Detected'))}
                </Text>
              </View>
            </View>

            {/* Advisory Hindi Text */}
            <View style={styles.advisoryCard}>
              <View style={styles.advisoryHeader}>
                <Text style={styles.advisoryTitle}>AI Crop Doctor Advice (हिंदी)</Text>
                <TouchableOpacity onPress={() => setIsSpeakingAdvisory(!isSpeakingAdvisory)}>
                  <Ionicons 
                    name={isSpeakingAdvisory ? "stop-circle" : "volume-medium"} 
                    size={28} 
                    color={Colors.lightGreen} 
                  />
                </TouchableOpacity>
              </View>
              <Text style={styles.advisoryBody}>{scanResult.advisory_hindi}</Text>
              {isSpeakingAdvisory && (
                <View style={styles.audioPlayingPulse}>
                  <ActivityIndicator size="small" color={Colors.lightGreen} style={{ marginRight: 8 }} />
                  <Text style={styles.audioPlayingText}>Playing Hindi voice advice...</Text>
                </View>
              )}
            </View>

            {/* Smart Action Plan */}
            <Text style={styles.planSectionHeading}>Smart Action Plan</Text>
            
            {/* Recovery Banner */}
            {scanResult.action_plan.expected_recovery !== 'N/A' && scanResult.action_plan.expected_recovery && (
              <View style={styles.recoveryBanner}>
                <MaterialCommunityIcons name="timer-sand" size={20} color={Colors.blueAccent} style={{ marginRight: 8 }} />
                <Text style={styles.recoveryText}>Expected Recovery: {scanResult.action_plan.expected_recovery}</Text>
              </View>
            )}

            {/* Plan Lists */}
            {scanResult.action_plan.today && scanResult.action_plan.today.length > 0 && (
              <View style={[styles.planCardBlock, { borderLeftColor: Colors.healthy }]}>
                <Text style={[styles.planBlockTitle, { color: Colors.healthy }]}>Today's Action Plan</Text>
                {scanResult.action_plan.today.map((item, idx) => (
                  <View key={idx} style={styles.planCardItem}>
                    <Ionicons name="checkmark-circle" size={16} color={Colors.healthy} style={styles.planCardIcon} />
                    <Text style={styles.planCardText}>{item}</Text>
                  </View>
                ))}
              </View>
            )}

            {scanResult.action_plan.next_3_days && scanResult.action_plan.next_3_days.length > 0 && (
              <View style={[styles.planCardBlock, { borderLeftColor: Colors.warning }]}>
                <Text style={[styles.planBlockTitle, { color: Colors.warning }]}>Next 3 Days</Text>
                {scanResult.action_plan.next_3_days.map((item, idx) => (
                  <View key={idx} style={styles.planCardItem}>
                    <Ionicons name="arrow-forward-circle" size={16} color={Colors.warning} style={styles.planCardIcon} />
                    <Text style={styles.planCardText}>{item}</Text>
                  </View>
                ))}
              </View>
            )}

            {scanResult.action_plan.next_week && scanResult.action_plan.next_week.length > 0 && (
              <View style={[styles.planCardBlock, { borderLeftColor: Colors.blueAccent }]}>
                <Text style={[styles.planBlockTitle, { color: Colors.blueAccent }]}>Next Week</Text>
                {scanResult.action_plan.next_week.map((item, idx) => (
                  <View key={idx} style={styles.planCardItem}>
                    <Ionicons name="calendar" size={16} color={Colors.blueAccent} style={styles.planCardIcon} />
                    <Text style={styles.planCardText}>{item}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}
      </ScrollView>
    );
  }

  function renderVoiceTab() {
    return (
      <View style={styles.tabWrapper}>
        <Text style={styles.tabHeading}>AI Crop Doctor Chatbot</Text>
        
        {/* Suggestion Chips */}
        <View style={styles.suggestionRow}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {[
              "खाद कब देनी चाहिए?",
              "क्या आज सिंचाई करनी चाहिए?",
              "ऑर्गेनिक स्प्रे कौन सा सही है?",
              "बीमारी का कितना खतरा है?"
            ].map((chip, idx) => (
              <TouchableOpacity 
                key={idx} 
                style={styles.suggestionChip} 
                onPress={() => handleSendChat(chip)}
              >
                <Text style={styles.suggestionChipText}>{chip}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Chat Logs */}
        <ScrollView style={styles.chatScroller} contentContainerStyle={{ paddingBottom: 16 }}>
          {chatLog.map((bubble, idx) => {
            const isUser = bubble.sender === 'user';
            return (
              <View 
                key={idx} 
                style={[
                  styles.chatBubble, 
                  isUser ? styles.userBubble : styles.aiBubble
                ]}
              >
                {!isUser && (
                  <View style={styles.aiBubbleHeader}>
                    <MaterialCommunityIcons name="robot" size={16} color={Colors.lightGreen} style={{ marginRight: 6 }} />
                    <Text style={styles.aiBubbleTitle}>AI Crop Doctor</Text>
                  </View>
                )}
                <Text style={styles.chatBubbleText}>{bubble.text}</Text>
              </View>
            );
          })}
          
          {isAiProcessing && (
            <View style={styles.processingIndicator}>
              <ActivityIndicator size="small" color={Colors.lightGreen} />
              <Text style={styles.processingText}>Doctor is thinking...</Text>
            </View>
          )}
        </ScrollView>

        {/* Input Bar */}
        <View style={styles.inputBar}>
          <TouchableOpacity 
            style={[styles.micBtn, isSpeakingChat && { backgroundColor: Colors.danger }]}
            onPress={() => {
              if (isSpeakingChat) {
                setIsSpeakingChat(false);
              } else {
                handleSendChat("क्या आज सिंचाई करनी चाहिए?");
              }
            }}
          >
            <Ionicons name={isSpeakingChat ? "mic-off" : "mic"} size={22} color="#FFF" />
          </TouchableOpacity>
          <TextInput
            style={styles.chatInput}
            value={chatQuestion}
            onChangeText={setChatQuestion}
            placeholder="Ask AI Doctor (हिंदी / English)..."
            placeholderTextColor="#898"
          />
          <TouchableOpacity style={styles.sendBtn} onPress={() => handleSendChat()}>
            <Ionicons name="send" size={20} color={Colors.lightGreen} />
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  function renderAnalyticsTab() {
    const totalScans = scanHistory.length;
    const healthyScans = scanHistory.filter(item => item.disease.toLowerCase().includes('healthy')).length;
    const diseasedScans = totalScans - healthyScans;
    const savedFields = sensorData.saved_fields ?? [];

    return (
      <ScrollView contentContainerStyle={styles.scrollPadding}>
        <Text style={styles.tabHeading}>Crop Health Analytics</Text>

        {/* Stat Overview Cards */}
        <View style={styles.analyticsStatsRow}>
          <View style={[styles.statBox, { borderColor: Colors.blueAccent }]}>
            <MaterialIcons name="camera-alt" size={22} color={Colors.blueAccent} />
            <Text style={[styles.statVal, { color: Colors.blueAccent }]}>{totalScans}</Text>
            <Text style={styles.statLabel}>Total Scans</Text>
          </View>
          <View style={[styles.statBox, { borderColor: Colors.orangeAccent }]}>
            <MaterialIcons name="warning" size={22} color={Colors.orangeAccent} />
            <Text style={[styles.statVal, { color: Colors.orangeAccent }]}>{diseasedScans}</Text>
            <Text style={styles.statLabel}>Diseased</Text>
          </View>
          <View style={[styles.statBox, { borderColor: Colors.healthy }]}>
            <MaterialIcons name="check-circle" size={22} color={Colors.healthy} />
            <Text style={[styles.statVal, { color: Colors.healthy }]}>{healthyScans}</Text>
            <Text style={styles.statLabel}>Healthy</Text>
          </View>
        </View>

        {/* REGISTERED LANDS SECTION */}
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, marginBottom: 8 }}>
          <Text style={[styles.sectionTitle, { marginTop: 0, marginBottom: 0 }]}>My Registered Lands ({savedFields.length})</Text>
          {savedFields.length > 0 && (
            <TouchableOpacity 
              style={[styles.scanActionBtn, { marginTop: 0, marginBottom: 0, paddingVertical: 6, paddingHorizontal: 12, borderRadius: 8 }]}
              onPress={() => {
                setAddFieldChoice('menu');
                setIsAddFieldModalVisible(true);
              }}
            >
              <Text style={[styles.scanActionBtnText, { fontSize: 13 }]}>+ Add Plot</Text>
            </TouchableOpacity>
          )}
        </View>
        
        {savedFields.length === 0 ? (
          <View style={styles.emptyLandsCard}>
            <MaterialCommunityIcons name="map-legend" size={36} color={Colors.textMuted} />
            <Text style={styles.emptyLandsText}>No registered lands yet.</Text>
            <Text style={styles.emptyLandsSubtext}>Outline your farm plot on the map or enter coordinates manually to track satellite health metrics.</Text>
            <TouchableOpacity 
              style={[styles.scanActionBtn, { marginTop: 14, marginBottom: 0, paddingVertical: 8, width: '70%', borderRadius: 8 }]}
              onPress={() => {
                setAddFieldChoice('menu');
                setIsAddFieldModalVisible(true);
              }}
            >
              <Text style={[styles.scanActionBtnText, { fontSize: 14 }]}>Add Plot</Text>
            </TouchableOpacity>
          </View>
        ) : (
          savedFields.map((field) => {
            const ndviVal = field.vegetation_ndvi ?? 0.65;
            const healthPct = Math.round(ndviVal * 100);
            
            let healthColor = Colors.healthy;
            let statusText = 'Excellent';
            if (ndviVal < 0.40) {
              healthColor = Colors.danger;
              statusText = 'Poor';
            } else if (ndviVal < 0.60) {
              healthColor = Colors.warning;
              statusText = 'Fair';
            }

            return (
              <TouchableOpacity 
                key={field.id} 
                style={[styles.landCard, { borderLeftColor: healthColor }]}
                onPress={() => setSelectedSavedLand(field)}
              >
                <View style={styles.landCardLeft}>
                  <View style={styles.mapIconCircle}>
                    <MaterialCommunityIcons name="map-marker" size={20} color={Colors.accentGreen} />
                  </View>
                  <View style={styles.landDetails}>
                    <Text style={styles.landName}>{field.name}</Text>
                    <Text style={styles.landMeta}>
                      Saved: {field.timestamp}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.landCardRight}>
                  <View style={[styles.scoreBadge, { borderColor: healthColor }]}>
                    <Text style={[styles.scoreBadgeText, { color: healthColor }]}>{healthPct}%</Text>
                  </View>
                  <Text style={styles.scoreStatusText}>{statusText}</Text>
                </View>
              </TouchableOpacity>
            );
          })
        )}

        {/* Scan History list */}
        <Text style={styles.sectionTitle}>Scan History & Timeline</Text>
        {scanHistory.map((item, idx) => {
          const isHealthy = item.disease.toLowerCase().includes('healthy');
          const cleanName = item.disease.replace(/_/g, ' ');
          return (
            <View 
              key={idx} 
              style={[
                styles.historyCard, 
                { borderColor: isHealthy ? Colors.healthy : Colors.orangeAccent }
              ]}
            >
              <View style={[styles.historyBadge, { backgroundColor: isHealthy ? '#4CAF5022' : '#FF980022' }]}>
                <MaterialCommunityIcons 
                  name={isHealthy ? "leaf" : "bug"} 
                  size={24} 
                  color={isHealthy ? Colors.healthy : Colors.orangeAccent} 
                />
              </View>
              <View style={styles.historyDetails}>
                <Text style={styles.historyName}>{cleanName}</Text>
                <Text style={styles.historyMeta}>
                  {item.timestamp}
                </Text>
              </View>
            </View>
          );
        })}

        {/* DETAILS MODAL FOR LAND HIGHLIGHT */}
        {selectedSavedLand && (
          <Modal animationType="fade" transparent={true} visible={true}>
            <View style={styles.modalOverlay}>
              <View style={[styles.modalContent, { width: '90%' }]}>
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>{selectedSavedLand.name}</Text>
                  <TouchableOpacity onPress={() => setSelectedSavedLand(null)}>
                    <Ionicons name="close-circle" size={28} color={Colors.textSecondary} />
                  </TouchableOpacity>
                </View>
                
                <Text style={styles.modalSubtitle}>VEDAS Satellite Field Analysis</Text>
                
                <View style={styles.detailGrid}>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>NDVI Health Index</Text>
                    <Text style={[styles.detailValue, { 
                      color: selectedSavedLand.vegetation_ndvi >= 0.70 ? Colors.healthy : 
                             selectedSavedLand.vegetation_ndvi >= 0.55 ? Colors.warning : Colors.danger 
                    }]}>
                      {(selectedSavedLand.vegetation_ndvi ?? 0.65).toFixed(2)}
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Satellite Soil Moisture</Text>
                    <Text style={styles.detailValue}>{(selectedSavedLand.satellite_soil ?? 0.38).toFixed(2)} m³/m³</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Surface Temperature</Text>
                    <Text style={styles.detailValue}>{(selectedSavedLand.satellite_temp ?? 32.2).toFixed(1)} °C</Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Field Centroid GPS</Text>
                    <Text style={styles.detailValue}>
                      {selectedSavedLand.latitude.toFixed(4)}, {selectedSavedLand.longitude.toFixed(4)}
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Registration Date</Text>
                    <Text style={styles.detailValue}>{selectedSavedLand.timestamp}</Text>
                  </View>
                </View>
                
                <TouchableOpacity 
                  style={[styles.modalBtn, styles.saveBtn, { width: '100%', marginTop: 20, padding: 12, alignItems: 'center' }]} 
                  onPress={() => setSelectedSavedLand(null)}
                >
                  <Text style={styles.btnText}>Close Details</Text>
                </TouchableOpacity>
              </View>
            </View>
          </Modal>
        )}
      </ScrollView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    paddingTop: Platform.OS === 'android' ? RNStatusBar.currentHeight : 0,
  },
  header: {
    height: 70,
    backgroundColor: Colors.surface,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.textPrimary,
  },
  onlineBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  onlineText: {
    fontSize: 11,
    color: Colors.textSecondary,
  },
  settingsBtn: {
    padding: 8,
  },
  tabContentContainer: {
    flex: 1,
  },
  scrollPadding: {
    padding: 16,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.textPrimary,
  },
  subWelcomeText: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 2,
    marginBottom: 16,
  },
  healthCard: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#4CAF5044',
  },
  scoreCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 3,
    borderColor: Colors.healthy,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#4CAF5022',
  },
  scoreText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.healthy,
  },
  healthDetails: {
    marginLeft: 16,
    flex: 1,
  },
  cardMutedLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  healthStatusText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.healthy,
    marginVertical: 2,
  },
  cardMutedSubText: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  sensorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  sensorCard: {
    flex: 1,
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  sensorVal: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    marginVertical: 4,
  },
  sensorLabel: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  weatherBanner: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    marginBottom: 16,
  },
  weatherTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: Colors.textPrimary,
  },
  weatherBody: {
    fontSize: 11,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    marginTop: 8,
    marginBottom: 8,
  },
  alertTile: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 8,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderLeftWidth: 4,
    marginBottom: 8,
  },
  alertText: {
    fontSize: 12,
    color: Colors.textPrimary,
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    marginBottom: 32,
  },
  actionBtn: {
    flex: 1,
    backgroundColor: Colors.primaryGreen,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginHorizontal: 6,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  actionBtnLabel: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 14,
    marginLeft: 8,
  },
  tabWrapper: {
    flex: 1,
    padding: 16,
  },
  tabHeading: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  mapPlaceholder: {
    flex: 1,
    backgroundColor: Colors.cardBackground,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  mapText: {
    color: Colors.textSecondary,
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 12,
    marginBottom: 20,
  },
  mapIndicators: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginVertical: 16,
  },
  mapIndicatorBox: {
    alignItems: 'center',
    backgroundColor: Colors.surface,
    padding: 12,
    borderRadius: 8,
    flex: 1,
    marginHorizontal: 4,
  },
  mapIndicatorVal: {
    color: Colors.lightGreen,
    fontWeight: 'bold',
    fontSize: 15,
  },
  mapIndicatorLabel: {
    color: Colors.textMuted,
    fontSize: 10,
    marginTop: 4,
  },
  satelliteComingText: {
    color: Colors.textMuted,
    fontSize: 12,
    position: 'absolute',
    bottom: 16,
  },
  fieldLabel: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginBottom: 8,
  },
  leafSelectorRow: {
    marginBottom: 16,
  },
  leafSelectorBtn: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 8,
    padding: 12,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: '#FFF1',
  },
  leafSelected: {
    borderColor: Colors.lightGreen,
    backgroundColor: Colors.primaryGreen,
  },
  leafBtnText: {
    fontSize: 13,
  },
  cameraBox: {
    height: 180,
    backgroundColor: Colors.cardBackground,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: Colors.textMuted,
    marginBottom: 16,
  },
  cameraPreviewBox: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraPreviewText: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 10,
  },
  cameraProgress: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraProgressText: {
    color: Colors.lightGreen,
    fontSize: 12,
    marginTop: 10,
  },
  scanActionBtn: {
    backgroundColor: Colors.lightGreen,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 16,
  },
  scanActionBtnText: {
    color: '#FFF',
    fontSize: 15,
    fontWeight: 'bold',
  },
  btnDisabled: {
    backgroundColor: '#354535',
  },
  resultBox: {
    marginTop: 8,
    marginBottom: 32,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    flex: 1,
  },
  matchPercentBadge: {
    backgroundColor: '#4CAF5033',
    borderColor: Colors.healthy,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  matchPercentText: {
    color: Colors.healthy,
    fontSize: 12,
    fontWeight: 'bold',
  },
  advisoryCard: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
  },
  advisoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#FFF1',
    paddingBottom: 8,
    marginBottom: 8,
  },
  advisoryTitle: {
    color: Colors.lightGreen,
    fontWeight: 'bold',
    fontSize: 14,
  },
  advisoryBody: {
    color: Colors.textPrimary,
    fontSize: 13,
    lineHeight: 18,
  },
  audioPlayingPulse: {
    marginTop: 8,
    backgroundColor: '#4CAF5011',
    padding: 6,
    borderRadius: 4,
  },
  audioPlayingText: {
    color: Colors.accentGreen,
    fontSize: 11,
  },
  planSectionHeading: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  recoveryBanner: {
    backgroundColor: '#2196F31F',
    borderColor: Colors.blueAccent,
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  recoveryText: {
    color: Colors.textPrimary,
    fontSize: 12,
    fontWeight: 'bold',
  },
  planBlock: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
  },
  planBlockTitle: {
    fontWeight: 'bold',
    fontSize: 13,
    marginBottom: 6,
  },
  planItem: {
    color: Colors.textSecondary,
    fontSize: 12,
    lineHeight: 16,
    marginVertical: 2,
  },
  suggestionRow: {
    height: 40,
    marginBottom: 12,
  },
  suggestionChip: {
    backgroundColor: Colors.cardBackground,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    marginRight: 6,
    borderWidth: 1,
    borderColor: '#4CAF5044',
  },
  suggestionChipText: {
    color: Colors.textSecondary,
    fontSize: 11,
  },
  chatScroller: {
    flex: 1,
    marginBottom: 8,
  },
  chatBubble: {
    padding: 12,
    borderRadius: 12,
    marginVertical: 4,
    maxWidth: '85%',
  },
  userBubble: {
    backgroundColor: '#2E7D3244',
    borderColor: '#2E7D3288',
    borderWidth: 1,
    alignSelf: 'flex-end',
  },
  aiBubble: {
    backgroundColor: Colors.cardBackground,
    alignSelf: 'flex-start',
  },
  aiBubbleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#FFF1',
    paddingBottom: 4,
    marginBottom: 4,
  },
  aiBubbleTitle: {
    color: Colors.lightGreen,
    fontWeight: 'bold',
    fontSize: 11,
  },
  chatBubbleText: {
    color: Colors.textPrimary,
    fontSize: 13,
    lineHeight: 17,
  },
  processingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    padding: 12,
  },
  processingText: {
    color: Colors.textMuted,
    fontSize: 12,
    marginLeft: 8,
  },
  inputBar: {
    backgroundColor: Colors.surface,
    padding: 8,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  micBtn: {
    backgroundColor: Colors.lightGreen,
    width: 38,
    height: 38,
    borderRadius: 19,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatInput: {
    flex: 1,
    color: Colors.textPrimary,
    fontSize: 13,
    paddingHorizontal: 10,
  },
  sendBtn: {
    padding: 8,
  },
  analyticsStatsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statBox: {
    flex: 1,
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
    marginHorizontal: 4,
  },
  statVal: {
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  statLabel: {
    fontSize: 11,
    color: Colors.textMuted,
  },
  historyCard: {
    backgroundColor: Colors.cardBackground,
    borderRadius: 12,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    marginBottom: 10,
  },
  historyBadge: {
    width: 44,
    height: 44,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  historyDetails: {
    marginLeft: 12,
    flex: 1,
  },
  historyName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: Colors.textPrimary,
  },
  historyMeta: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 4,
  },
  bottomNav: {
    height: 60,
    backgroundColor: Colors.surface,
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  navItem: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  navLabel: {
    fontSize: 10,
    marginTop: 2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: Colors.surface,
    borderRadius: 16,
    padding: 20,
    width: '100%',
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  modalSubtitle: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 16,
  },
  textInput: {
    backgroundColor: Colors.cardBackground,
    color: Colors.textPrimary,
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    borderWidth: 1,
    borderColor: Colors.divider,
    marginBottom: 20,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  modalBtn: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginLeft: 10,
  },
  cancelBtn: {
    backgroundColor: 'transparent',
  },
  saveBtn: {
    backgroundColor: Colors.lightGreen,
  },
  btnText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 13,
  },
  cameraActionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingHorizontal: 6,
  },
  cameraIconBtn: {
    flex: 1,
    backgroundColor: Colors.cardBackground,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 6,
    flexDirection: 'row',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  cameraIconBtnText: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    marginLeft: 8,
    fontSize: 13,
  },
  capturedImagePreview: {
    width: '100%',
    height: '100%',
    borderRadius: 12,
    resizeMode: 'cover',
  },
  clearImageBtn: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#000c',
    borderRadius: 16,
  },
  resultBoxHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  severityText: {
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 2,
  },
  planCardBlock: {
    backgroundColor: Colors.surface,
    padding: 14,
    borderRadius: 12,
    borderLeftWidth: 4,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  planCardItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginTop: 8,
  },
  planCardIcon: {
    marginRight: 8,
    marginTop: 1,
  },
  planCardText: {
    flex: 1,
    color: Colors.textSecondary,
    fontSize: 13,
    lineHeight: 18,
  },
  mapTabHeader: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
    backgroundColor: Colors.background,
  },
  mapSubheading: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
    fontFamily: 'Inter',
  },
  mapLoadingContainer: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: Colors.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapLoadingText: {
    color: Colors.textSecondary,
    marginTop: 12,
    fontSize: 14,
  },
  landCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  landCardLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  landCardRight: {
    alignItems: 'center',
    marginLeft: 12,
  },
  mapIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#81C7841a',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  landDetails: {
    flex: 1,
  },
  landName: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    fontSize: 15,
  },
  landMeta: {
    color: Colors.textMuted,
    fontSize: 11,
    marginTop: 2,
  },
  scoreBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scoreBadgeText: {
    fontWeight: 'bold',
    fontSize: 14,
  },
  scoreStatusText: {
    color: Colors.textSecondary,
    fontSize: 10,
    marginTop: 4,
    fontWeight: '600',
  },
  emptyLandsCard: {
    backgroundColor: Colors.surface,
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: Colors.divider,
    marginBottom: 20,
    borderStyle: 'dashed',
  },
  emptyLandsText: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    fontSize: 15,
    marginTop: 12,
  },
  emptyLandsSubtext: {
    color: Colors.textMuted,
    fontSize: 12,
    textAlign: 'center',
    marginTop: 6,
    lineHeight: 18,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    marginBottom: 12,
  },
  detailGrid: {
    width: '100%',
    marginTop: 10,
    backgroundColor: Colors.cardBackground,
    borderRadius: 8,
    padding: 10,
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  detailLabel: {
    color: Colors.textSecondary,
    fontSize: 13,
  },
  detailValue: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    fontSize: 13,
  },
  satelliteStatusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  satDetailBox: {
    flex: 1,
    backgroundColor: Colors.surface,
    padding: 12,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderWidth: 1,
    borderColor: Colors.divider,
    marginHorizontal: 4,
  },
  satDetailVal: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    fontSize: 18,
    marginTop: 4,
  },
  satDetailLabel: {
    color: Colors.textSecondary,
    fontSize: 11,
    marginTop: 2,
    fontWeight: '600',
  },
  satDetailSubtext: {
    color: Colors.textMuted,
    fontSize: 9,
    marginTop: 2,
  },
  noFieldBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: Colors.orangeAccent,
    borderWidth: 1,
    borderColor: Colors.divider,
  },
  noFieldBannerText: {
    color: Colors.textPrimary,
    fontWeight: 'bold',
    fontSize: 14,
  },
  noFieldBannerSubtext: {
    color: Colors.textMuted,
    fontSize: 11,
    marginTop: 2,
    lineHeight: 16,
  },
});
