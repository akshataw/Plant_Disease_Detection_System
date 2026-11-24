"""CPU-friendly training for the PlantVillage classifier (ADR 0014).

Same architecture and export contract as the Colab notebook (ADR 0003), but trained by feature extraction:
the frozen ImageNet MobileNetV2 backbone runs ONCE over every image, then only the classification head is
trained on the cached 1280-d features. This takes minutes on CPU instead of hours.

Run inside the backend image (TensorFlow 2.19 — same as serving):
  see ml/README.md → "Train locally on CPU"
"""
import argparse
import json
import os
import time

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import keras  # noqa: E402
import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402
import tensorflow_datasets as tfds  # noqa: E402

IMG = 224
BATCH = 64
SPLITS = {"train": "train[:80%]", "val": "train[80%:90%]", "test": "train[90%:]"}
AUTOTUNE = tf.data.AUTOTUNE


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def resize(image, label):
    # Raw 0-255 pixels; normalisation is a layer inside the model
    return tf.image.resize(image, (IMG, IMG)), label


def build_backbone():
    base = keras.applications.MobileNetV2(input_shape=(IMG, IMG, 3), include_top=False, weights="imagenet")
    base.trainable = False
    inputs = keras.Input(shape=(IMG, IMG, 3), name="image")
    x = keras.layers.Rescaling(1 / 127.5, offset=-1, name="mobilenet_preprocess")(inputs)
    x = base(x, training=False)
    features = keras.layers.GlobalAveragePooling2D(name="gap")(x)
    return inputs, features


def extract_features(extractor, ds, cache_path, total):
    """Run the frozen backbone over a split once; cache to .npz so reruns skip this step."""
    if os.path.exists(cache_path):
        data = np.load(cache_path)
        log(f"Loaded cached features {os.path.basename(cache_path)} {data['x'].shape}")
        return data["x"], data["y"]
    run = tf.function(lambda x: extractor(x, training=False))
    xs, ys, seen, start = [], [], 0, time.time()
    for images, labels in ds.map(resize, num_parallel_calls=AUTOTUNE).batch(BATCH).prefetch(AUTOTUNE):
        xs.append(run(images).numpy())
        ys.append(labels.numpy())
        seen += len(labels)
        if len(xs) % 50 == 0:
            rate = seen / (time.time() - start)
            log(f"  {os.path.basename(cache_path)}: {seen}/{total} images ({rate:.0f} img/s)")
    x, y = np.concatenate(xs), np.concatenate(ys)
    np.savez(cache_path, x=x, y=y)
    log(f"Extracted {x.shape} in {time.time() - start:.0f}s")
    return x, y


def save_reports(reports_dir, class_names, y_true, y_pred, metrics):
    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
    with open(os.path.join(reports_dir, "classification_report.txt"), "w") as f:
        f.write(report)
    with open(os.path.join(reports_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    n = len(class_names)
    cm = confusion_matrix(y_true, y_pred, normalize="true")
    fig, ax = plt.subplots(figsize=(16, 14))
    im = ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(class_names, rotation=90, fontsize=7)
    ax.set_yticklabels(class_names, fontsize=7)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Normalised confusion matrix — test accuracy {metrics['test_accuracy']:.4f}")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(os.path.join(reports_dir, "confusion_matrix.png"), dpi=110)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="/ml/.data")
    parser.add_argument("--models-out", default="/app/models")
    parser.add_argument("--reports-out", default="/ml/reports")
    parser.add_argument("--name", default="plant_disease_v1")
    parser.add_argument("--epochs", type=int, default=60)
    args = parser.parse_args()

    keras.utils.set_random_seed(42)
    tfds.disable_progress_bar()
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.reports_out, exist_ok=True)
    started = time.time()

    log("Loading PlantVillage from TFDS (first run downloads ~830 MB)…")
    builder = tfds.builder("plant_village", data_dir=args.data_dir)
    builder.download_and_prepare()
    class_names = builder.info.features["label"].names
    n_classes = len(class_names)
    splits = {k: builder.as_dataset(split=v, as_supervised=True, shuffle_files=False) for k, v in SPLITS.items()}
    sizes = {k: builder.info.splits[v].num_examples for k, v in SPLITS.items()}
    log(f"{n_classes} classes; split sizes {sizes}")

    inputs, features = build_backbone()
    extractor = keras.Model(inputs, features, name="feature_extractor")

    feats = {}
    for name, ds in splits.items():
        log(f"Extracting features: {name}")
        feats[name] = extract_features(extractor, ds, os.path.join(args.data_dir, f"features_{name}.npz"), sizes[name])
    (x_train, y_train), (x_val, y_val), (x_test, y_test) = feats["train"], feats["val"], feats["test"]
    missing = set(range(n_classes)) - set(np.unique(y_test))
    if missing:
        raise SystemExit(f"Test split is missing classes {missing}; split is not stratified enough")

    log("Training classification head on cached features")
    head_in = keras.Input(shape=(x_train.shape[1],))
    dropout = keras.layers.Dropout(0.3, name="dropout")
    dense = keras.layers.Dense(n_classes, activation="softmax", name="predictions")
    head = keras.Model(head_in, dense(dropout(head_in)))
    head.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    history = head.fit(
        x_train, y_train, validation_data=(x_val, y_val), epochs=args.epochs, batch_size=256, verbose=2,
        callbacks=[
            keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=6, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3),
        ],
    )
    test_loss, test_acc = head.evaluate(x_test, y_test, verbose=0)
    y_pred = np.argmax(head.predict(x_test, verbose=0), axis=1)
    log(f"Test accuracy {test_acc:.4f}  loss {test_loss:.4f}")

    log("Assembling end-to-end model (raw image → probabilities)")
    full_out = dense(dropout(features))  # reuse the trained head layers on top of the backbone
    model = keras.Model(inputs, full_out, name="plant_disease_mobilenetv2")

    # Verify the assembled model matches the head on real test images (small batches keep memory low)
    diff, checked = 0.0, 0
    for images, _ in splits["test"].take(256).map(resize).batch(32):
        e2e = model(images, training=False).numpy()
        ref = head(x_test[checked:checked + len(e2e)], training=False).numpy()
        diff = max(diff, float(np.max(np.abs(e2e - ref))))
        checked += len(e2e)
    log(f"End-to-end vs feature-head max prob diff on {checked} test images: {diff:.2e}")
    if diff > 1e-3:
        raise SystemExit("Assembled model does not match trained head")

    model_path = os.path.join(args.models_out, f"{args.name}.keras")
    model.save(model_path)
    with open(os.path.join(args.models_out, "class_names.json"), "w") as f:
        json.dump(class_names, f, indent=2)

    metrics = {
        "model": args.name, "backbone": "MobileNetV2 (ImageNet, frozen)", "method": "feature extraction + softmax head",
        "img_size": IMG, "num_classes": n_classes, "split": SPLITS, "split_sizes": sizes,
        "test_accuracy": round(float(test_acc), 4), "test_loss": round(float(test_loss), 4),
        "best_val_accuracy": round(float(max(history.history["val_accuracy"])), 4),
        "epochs_run": len(history.history["loss"]), "tensorflow": tf.__version__,
        "training_minutes": round((time.time() - started) / 60, 1),
    }
    report = save_reports(args.reports_out, class_names, y_test, y_pred, metrics)
    print(report)
    log(f"Saved {model_path} ({os.path.getsize(model_path) / 1e6:.1f} MB) and reports in {args.reports_out}")


if __name__ == "__main__":
    main()
