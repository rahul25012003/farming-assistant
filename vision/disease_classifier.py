"""
Crop Disease Classifier using TensorFlow.
Trained on PlantVillage dataset, fine-tuned for Karnataka crops.
Includes GradCAM-style explainability.
"""
import numpy as np
import cv2
import os
import config

# Lazy import TF to speed up startup when vision isn't needed
_tf = None
_model = None


def _get_tf():
    global _tf
    if _tf is None:
        import tensorflow as tf
        _tf = tf
    return _tf


class DiseaseClassifier:
    def __init__(self):
        self.model = None
        self.input_size = config.MODEL_INPUT_SIZE
        self.class_names = config.DISEASE_CLASSES
        self._load_model()

    def _load_model(self):
        """Load the TF model. Fails gracefully if model file not found."""
        model_path = config.DISEASE_MODEL_PATH
        if not os.path.exists(model_path):
            print(f"[VISION] Model not found at {model_path}. Classification will fail.")
            print("[VISION] Download the model or train one using train_model.py")
            return

        try:
            tf = _get_tf()
            self.model = tf.keras.models.load_model(model_path)
            print(f"[VISION] Model loaded: {model_path}")
        except Exception as e:
            print(f"[VISION] Failed to load model: {e}")

    def classify(self, image_path):
        """
        Classify a crop disease from leaf image.

        Returns dict with disease name, confidence, and optional heatmap path.
        """
        if self.model is None:
            return {
                "disease": "model_not_loaded",
                "confidence": 0.0,
                "heatmap_path": None,
            }

        # Preprocess
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        processed = self._preprocess(img)

        # Predict
        tf = _get_tf()
        predictions = self.model.predict(np.expand_dims(processed, axis=0), verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        disease = self.class_names[class_idx]

        # Generate heatmap for explainability
        heatmap_path = None
        if confidence >= config.CONFIDENCE_THRESHOLD:
            try:
                heatmap_path = self._generate_gradcam(img, processed, class_idx)
            except Exception as e:
                print(f"[VISION] GradCAM failed (non-critical): {e}")

        return {
            "disease": disease,
            "confidence": confidence,
            "heatmap_path": heatmap_path,
        }

    def _preprocess(self, img):
        """Preprocess image for model input."""
        # Resize
        img_resized = cv2.resize(img, self.input_size)

        # Color correction - helps with photos taken in different lighting
        lab = cv2.cvtColor(img_resized, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        # Normalize to [0, 1]
        normalized = enhanced.astype(np.float32) / 255.0
        return normalized

    def _generate_gradcam(self, original_img, processed_img, class_idx):
        """
        Generate GradCAM-style heatmap showing which leaf regions
        triggered the classification. Helps farmers understand the diagnosis.
        """
        tf = _get_tf()

        # Find the last conv layer
        last_conv_layer = None
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv_layer = layer.name
                break

        if not last_conv_layer:
            return None

        # Build gradient model
        grad_model = tf.keras.models.Model(
            inputs=self.model.input,
            outputs=[
                self.model.get_layer(last_conv_layer).output,
                self.model.output,
            ]
        )

        # Compute gradients
        img_tensor = tf.expand_dims(processed_img, axis=0)
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_tensor)
            loss = predictions[:, class_idx]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()

        # Overlay heatmap on original image
        heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)

        # Save heatmap
        heatmap_dir = os.path.join("static", "heatmaps")
        os.makedirs(heatmap_dir, exist_ok=True)
        heatmap_path = os.path.join(heatmap_dir, f"gradcam_{id(processed_img)}.jpg")
        cv2.imwrite(heatmap_path, overlay)

        return heatmap_path
