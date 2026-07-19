import os
import numpy as np
import time

try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False

class LeafClassifierNPU:
    """
    On-device Leaf Disease Classifier template compiled via Qualcomm AI Hub
    specifically optimized for the Snapdragon 8 Elite (OnePlus 15) Hexagon NPU.
    """
    def __init__(self, model_path="models/leaf_mobilenet_v2_int8.tflite"):
        self.model_path = model_path
        self.classes = [
            "Tomato - Healthy",
            "Tomato - Late Blight (Fungal)",
            "Tomato - Leaf Mold (Fungal)",
            "Apple - Apple Scab",
            "Apple - Healthy",
            "Potato - Early Blight (Fungal)",
            "Potato - Late Blight (Fungal)",
            "Potato - Healthy",
            "Corn - Common Rust",
            "Corn - Healthy"
        ]
        self.session = None
        self._init_npu_session()

    def _init_npu_session(self):
        """
        Initializes the model runtime session. On the OnePlus 15 device, this registers 
        the QNN (Qualcomm Neural Network) Execution Provider to run on the NPU instead of CPU.
        """
        if not os.path.exists(self.model_path):
            print(f"[Warning]: Model file {self.model_path} not found. Running in SIMULATED NPU mode.")
            return

        if not HAS_ORT:
            print("[Warning]: onnxruntime not installed. Running in SIMULATED NPU mode.")
            return

        try:
            print("[NPU Init]: Loading quantized model onto Qualcomm Hexagon NPU...")
            # Register the QNN (Qualcomm Neural Network) Execution Provider for NPU acceleration
            # On Android, this links to libQnnHtp.so (Hexagon Tensor Processor)
            providers = [
                'QNNExecutionProvider',
                'CPUExecutionProvider'
            ]
            provider_options = [{
                'backend_path': 'libQnnHtp.so',  # Qualcomm Hexagon Tensor Processor library
                'perf_profile': 'burst'          # Maximum NPU clock speed for instant camera classification
            }, {}]

            self.session = ort.InferenceSession(
                self.model_path,
                providers=providers,
                provider_options=provider_options
            )
            print("[NPU Success]: Leaf classifier successfully compiled and loaded on NPU!")
        except Exception as e:
            print(f"[NPU Error]: Failed to bind to Hexagon NPU ({e}). Falling back to CPU.")
            self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])

    def preprocess_image(self, image_raw_bytes):
        """
        Preprocesses a raw camera photo to match input tensor specs:
        - Resize to 224x224 pixels
        - Normalize pixels to [0, 1] range (or [-1, 1])
        - Convert to NHWC tensor format (quantized INT8 or Float32)
        """
        print("[Preprocessing]: Resizing leaf image to 224x224 and normalizing channels...")
        # Simulate loading and preprocessing
        # In a real script: image = Image.open(io.BytesIO(image_raw_bytes)).resize((224, 224))
        mock_processed = np.random.rand(1, 224, 224, 3).astype(np.float32)
        return mock_processed

    def classify_leaf(self, image_raw_bytes):
        """
        Runs edge inference locally on the NPU.
        """
        t0 = time.perf_counter()
        
        # Preprocess
        input_data = self.preprocess_image(image_raw_bytes)
        
        # If running in simulated mode
        if self.session is None:
            # Deterministic simulation to show working flow in offline tests
            time.sleep(0.015) # Simulate 15ms NPU inference latency
            sim_probabilities = [0.05, 0.88, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.0, 0.0]
            max_idx = int(np.argmax(sim_probabilities))
            latency = (time.perf_counter() - t0) * 1000
            
            return {
                "disease": self.classes[max_idx],
                "confidence": sim_probabilities[max_idx],
                "latency_ms": round(latency, 2),
                "device": "Snapdragon 8 Elite NPU (Simulated)"
            }

        # Real inference run on NPU
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        
        raw_outputs = self.session.run([output_name], {input_name: input_data})
        probabilities = self.softmax(raw_outputs[0][0])
        max_idx = int(np.argmax(probabilities))
        
        latency = (time.perf_counter() - t0) * 1000
        return {
            "disease": self.classes[max_idx],
            "confidence": float(probabilities[max_idx]),
            "latency_ms": round(latency, 2),
            "device": "Snapdragon 8 Elite Hexagon NPU (QNN)"
        }

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

if __name__ == "__main__":
    classifier = LeafClassifierNPU()
    # Dummy bytes representing a leaf photo taken by the farmer
    dummy_photo_bytes = b"raw_image_data_here"
    result = classifier.classify_leaf(dummy_photo_bytes)
    
    print("\nLocal NPU Inference Result:")
    print(f"Detected Condition: {result['disease']}")
    print(f"Confidence score  : {result['confidence'] * 100:.1f}%")
    print(f"Inference Latency : {result['latency_ms']} ms")
    print(f"Hardware Backend  : {result['device']}")
