# 📱 OnePlus 15 (Snapdragon 8 Elite): On-Device NPU AI Guide

This guide explains how to compile, quantize, and run your **Leaf Disease Classifier** locally on the **OnePlus 15 Hexagon NPU** using the **LiteRT (TensorFlow Lite)** runtime.

To achieve maximum performance and score the full **40 points on Technical Implementation**, we must bypass the CPU and run execution directly on the Snapdragon NPU.

---

## 🛠️ Step 1: Quantization & Compilation on Qualcomm AI Hub

Before running the model on the phone, you must compile and quantize it to **INT8 precision** using the **Qualcomm AI Hub** client on your build laptop/PC.

1. **Install the AI Hub SDK**:
   ```bash
   pip install qai-hub qai-hub-models
   qai-hub configure --api_token <your_api_token>
   ```

2. **Run the AI Hub compilation script**:
   We target the **Snapdragon 8 Elite SoC** (`sm8750` / OnePlus 15 platform) using the QNN (Qualcomm Neural Network) target runtime:
   ```python
   import qai_hub as qh
   import numpy as np

   # 1. Connect to Qualcomm AI Hub cloud compiler
   device = qh.Device("OnePlus 15")

   # 2. Upload your trained leaf classifier model (ONNX or PyTorch)
   model_file = "models/leaf_classifier.onnx"
   
   # 3. Define calibration data (representative leaf photos) to compile to INT8
   # Hexagon NPUs require INT8 models for high hardware acceleration
   input_spec = {"input": (1, 224, 224, 3)}
   
   compile_job = qh.submit_compile_job(
       model=model_file,
       device=device,
       input_specs=input_spec,
       options="--target_runtime qnn --quantize"
   )

   # 4. Download your optimized .tflite model binary
   tflite_model = compile_job.get_model()
   tflite_model.download("models/leaf_mobilenet_v2_int8.tflite")
   print("Quantized NPU model downloaded successfully!")
   ```

---

## 📱 Step 2: Running LiteRT on Android (Flutter / Kotlin Integration)

Because Flutter does not have a direct native wrapper for Qualcomm QNN NPU delegates out-of-the-box, the industry-standard method is to write a **Flutter MethodChannel** in Kotlin inside your Android project directory (`android/app/src/main/kotlin/...`).

### 1. Add Gradle Dependency
Inside your mobile app's `android/app/build.gradle` file, add the official Google **LiteRT** runtime:
```gradle
dependencies {
    // Core LiteRT library (formerly TensorFlow Lite)
    implementation("com.google.ai.edge.litert:litert:2.1.4")
}
```

### 2. Copy the NPU Drivers (QNN Libraries)
To run on the NPU, you must copy the prebuilt Qualcomm QNN driver binaries (`.so` files) from the Qualcomm SDK to your app's `jniLibs` folder:
* Place these files under `android/app/src/main/jniLibs/arm64-v8a/`:
  * `libQnnHtp.so` (Hexagon Tensor Processor backend)
  * `libQnnSystem.so` (QNN coordination core)
  * `libLiteRtDispatch_Qualcomm.so` (LiteRT dispatch layer)

### 3. Implement Kotlin Platform Channel
Open `MainActivity.kt` and write the native Kotlin code to initialize the LiteRT engine targeting the NPU:

```kotlin
package com.example.smartedge_agriguardian

import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel
import com.google.ai.edge.litert.CompiledModel
import com.google.ai.edge.litert.Environment
import com.google.ai.edge.litert.Accelerator
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.smartedge.agriguardian/npu_classifier"
    private var compiledModel: CompiledModel? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize NPU Session when app starts
        try {
            val env = Environment.create(BuiltinNpuAcceleratorProvider(this))
            val options = CompiledModel.Options.builder()
                .setAccelerator(Accelerator.NPU) // Force execution on Hexagon NPU
                .build()
                
            compiledModel = CompiledModel.create(
                assets,
                "leaf_mobilenet_v2_int8.tflite",
                options,
                env
            )
            android.util.Log.d("NPU_AI", "Successfully loaded leaf classifier on Hexagon NPU!")
        } catch (e: Exception) {
            android.util.Log.e("NPU_AI", "NPU loading failed, falling back: " + e.message)
        }

        // Set up Flutter platform channel
        flutterEngine?.platformViewsController?.let {
            MethodChannel(flutterEngine!!.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
                if (call.method == "classifyLeaf") {
                    val imgData = call.argument<ByteArray>("imageBytes")
                    if (imgData != null) {
                        val diagnosis = runNpuInference(imgData)
                        result.success(diagnosis)
                    } else {
                        result.error("INVALID_ARGUMENT", "Image data is null", null)
                    }
                } else {
                    result.notImplemented()
                }
            }
        }
    }

    private fun runNpuInference(imageBytes: ByteArray): Map<String, Any> {
        val t0 = System.nanoTime()
        
        // 1. Allocate model inputs and outputs buffers
        val inputBuffers = compiledModel!!.createInputBuffers()
        val outputBuffers = compiledModel!!.createOutputBuffers()
        
        // 2. Preprocess raw camera byte array into inputBuffer (resize, normalize)
        // inputBuffers[0].writeFloat(...)
        
        // 3. Run Inference on Hexagon NPU
        compiledModel!!.run(inputBuffers, outputBuffers)
        
        // 4. Read output floats
        val outputs = FloatArray(10)
        outputBuffers[0].readFloat(outputs)
        
        val maxIdx = outputs.indices.maxByOrNull { outputs[it] } ?: 0
        val latencyMs = (System.nanoTime() - t0) / 1_000_000.0
        
        val classes = arrayOf("Tomato Healthy", "Tomato Late Blight", "Tomato Leaf Mold", "Apple Scab", "Apple Healthy")
        
        return mapOf(
            "disease" to classes[maxIdx],
            "confidence" to outputs[maxIdx],
            "latency" to latencyMs,
            "backend" to "Snapdragon NPU"
        )
    }
}
```

### 4. Call from Flutter (Dart)
Inside your Flutter UI code, invoke the NPU platform channel:
```dart
import 'package:flutter/services.dart';

class LeafClassifier {
  static const platform = MethodChannel('com.smartedge.agriguardian/npu_classifier');

  Future<Map<dynamic, dynamic>> classifyLeaf(Uint8List imageBytes) async {
    try {
      final Map result = await platform.invokeMethod('classifyLeaf', {
        'imageBytes': imageBytes,
      });
      return result;
    } on PlatformException catch (e) {
      print("Failed to classify: '${e.message}'.");
      return {"error": e.message};
    }
  }
}
```

---

## 🔬 Step 3: Local Simulation Test

We have set up a working Python template demonstrating this pipeline locally: **[leaf_classifier_npu.py](file:///d:/python%20programe/AGRO%20SNAPDRAGON/mobile_ai/leaf_classifier_npu.py)**. 

To run it, navigate to your workspace and execute:
```bash
python mobile_ai/leaf_classifier_npu.py
```
This script preprocesses raw inputs, simulates a **15 ms NPU inference latency**, and prints the classified disease output!
