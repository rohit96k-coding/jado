# Flutter App - Build Instructions

This folder contains the **Source Code** for the Native Android version of SAMi.

## prerequisites (Required to Build APK)
To compile this code into an `.apk` file, you must install:
1.  **Flutter SDK**: [Download Here](https://docs.flutter.dev/get-started/install/windows)
2.  **Android Studio**: To get the Android SDK and Gradle.
3.  **VS Code Flutter Extension**.

## Build Commands
Once you have installed the 2GB+ SDKs above, open this terminal and run:

1.  **Get Dependencies**:
    ```powershell
    flutter pub get
    ```

2.  **Run on Connected Phone**:
    ```powershell
    flutter run
    ```

3.  **Build APK File**:
    ```powershell
    flutter build apk --release
    ```

## ⚠️ Important Note
Installing Flutter and Android Studio takes a long time and uses ~5GB of disk space.

**Alternative (Instant):**
The **Python Web App** we built (in the main folder) already provides this exact same "Live" interface without needing to install anything. 
Just run `python main.py` and open the link on your phone.
