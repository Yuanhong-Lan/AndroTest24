# AndroTest24 Study
## 1. Overview
### 1.1 Introduction
The AndroTest24 Study is the first comprehensive statistical study of existing Android GUI testing metrics. It involves extensive experiments with 3-hour, 10-repetition tests on 42 diverse apps across 8 representative state-of-the-art testing approaches from diverse categories with typical testing methodologies. It examines the statistical significance, correlation, and variation of the testing metrics while applying them for comparative evaluation.

### 1.2 Publication
For more details about our study, please refer to our ASE 2024 paper "Navigating Mobile Testing Evaluation: A Comprehensive Statistical Analysis of Android GUI Testing Metrics".

### 1.3 Artifacts
This repository provides the corresponding artifacts, including:<br />① The **AndroTest24 App Benchmark**, consisting of 42 active open-source apps that are achieved from the integration of more than ten previous open-source benchmarks.<br />② The **Study Data** of our study, organized by our Research Questions.<br />③ The **SATE (Statistical Android Testing Evaluation) Framework**, to promote effective statistical mobile testing evaluation.

<br/>

## 2. Artifact-① **AndroTest24 App Benchmark**
### 2.1 APK File
A zip file containing all the 42 APK files of the AndroTest24 App Benchmark can be achieved from [GoogleDrive](https://drive.google.com/drive/folders/19efppfJEJ-z463v9BRsldv190CMDEog_?usp=drive_link).

### 2.2 App Source
The 42 apps and their sources are listed below:<br />_(Note: Some app links may be later broken due to some issues, e.g., the project has stopped)_

| **App** | **Source** |
| --- | --- |
| Signal | [https://github.com/signalapp/Signal-Android](https://github.com/signalapp/Signal-Android) |
| WordPress | [https://github.com/wordpress-mobile/WordPress-Android](https://github.com/wordpress-mobile/WordPress-Android) |
| CoronaWarn | [https://github.com/corona-warn-app/cwa-app-android](https://github.com/corona-warn-app/cwa-app-android) |
| Tachiyomi | [https://github.com/tachiyomiorg/tachiyomi](https://github.com/tachiyomiorg/tachiyomi) |
| DuckDuckGo | [https://github.com/duckduckgo/Android](https://github.com/duckduckgo/Android) |
| K9Mail | [https://github.com/thundernest/k-9](https://github.com/thundernest/k-9) |
| Firefox | [https://github.com/mozilla-mobile/fenix](https://github.com/mozilla-mobile/fenix) |
| Wikipedia | [https://github.com/wikimedia/apps-android-wikipedia](https://github.com/wikimedia/apps-android-wikipedia) |
| MyExpenses | [https://github.com/mtotschnig/MyExpenses](https://github.com/mtotschnig/MyExpenses) |
| AnkiDroid | [https://github.com/ankidroid/Anki-Android](https://github.com/ankidroid/Anki-Android) |
| SuntimesWidget | [https://github.com/forrestguice/SuntimesWidget](https://github.com/forrestguice/SuntimesWidget) |
| Conversations | [https://github.com/iNPUTmice/Conversations](https://github.com/iNPUTmice/Conversations) |
| NewPipe | [https://github.com/TeamNewPipe/NewPipe](https://github.com/TeamNewPipe/NewPipe) |
| AmazeFileManager | [https://github.com/TeamAmaze/AmazeFileManager](https://github.com/TeamAmaze/AmazeFileManager) |
| MoneyManagerEx | [https://github.com/moneymanagerex/android-money-manager-ex](https://github.com/moneymanagerex/android-money-manager-ex) |
| BookCatalogue | [https://github.com/eleybourn/Book-Catalogue](https://github.com/eleybourn/Book-Catalogue) |
| AntennaPod | [https://github.com/AntennaPod/AntennaPod](https://github.com/AntennaPod/AntennaPod) |
| LBRY | [https://github.com/lbryio/lbry-android](https://github.com/lbryio/lbry-android) |
| ConnectBot | [https://github.com/connectbot/connectbot](https://github.com/connectbot/connectbot) |
| RunnerUp | [https://github.com/jonasoreland/runnerup](https://github.com/jonasoreland/runnerup) |
| Timber | [https://github.com/naman14/Timber](https://github.com/naman14/Timber) |
| APhotoManager | [https://github.com/k3b/APhotoManager](https://github.com/k3b/APhotoManager) |
| BetterBatteryStats | [https://github.com/asksven/BetterBatteryStats](https://github.com/asksven/BetterBatteryStats) |
| Vanilla | [https://github.com/vanilla-music/vanilla](https://github.com/vanilla-music/vanilla) |
| AnyMemo | [https://github.com/helloworld1/AnyMemo](https://github.com/helloworld1/AnyMemo) |
| SimpleTask | [https://github.com/mpcjanssen/simpletask-android](https://github.com/mpcjanssen/simpletask-android) |
| LoopHabitTracker | [https://github.com/iSoron/uhabits](https://github.com/iSoron/uhabits) |
| TranslateYou | [https://github.com/Bnyro/TranslateYou](https://github.com/Bnyro/TranslateYou) |
| KeePassDroid | [https://github.com/bpellin/keepassdroid](https://github.com/bpellin/keepassdroid) |
| Materialistic | [https://github.com/hidroh/materialistic](https://github.com/hidroh/materialistic) |
| AlarmClock | [https://github.com/yuriykulikov/AlarmClock](https://github.com/yuriykulikov/AlarmClock) |
| Currencies | [https://github.com/sal0max/currencies](https://github.com/sal0max/currencies) |
| Notes | [https://github.com/SecUSo/privacy-friendly-notes](https://github.com/SecUSo/privacy-friendly-notes) |
| PasswordManager | [https://github.com/ishantchauhan710/PasswordManager](https://github.com/ishantchauhan710/PasswordManager) |
| Swiftp | [https://github.com/ppareit/swiftp](https://github.com/ppareit/swiftp) |
| Aard2 | [https://github.com/itkach/aard2-android](https://github.com/itkach/aard2-android) |
| Diary | [https://github.com/billthefarmer/diary](https://github.com/billthefarmer/diary) |
| ArxivExplorer | [https://github.com/GarrettBeatty/arXiv-eXplorer](https://github.com/GarrettBeatty/arXiv-eXplorer) |
| SimpleDraw | [https://github.com/SimpleMobileTools/Simple-Draw](https://github.com/SimpleMobileTools/Simple-Draw) |
| KindMind | [https://codeberg.org/fswb/kindmind](https://codeberg.org/fswb/kindmind) |
| CEToolbox | [https://github.com/cetoolbox/cetoolbox](https://github.com/cetoolbox/cetoolbox) |
| WhoHasMyStuff | [https://gitlab.com/stovocor/whohasmystuff](https://gitlab.com/stovocor/whohasmystuff) |


<br/>

## 3. Artifact-② Study Data
### 3.1 The Original Statistics Table
The original statistics tables of our study are provided under `/Study_Data`.<br />They are organized according to our Research Questions and have been renamed for better understandability.

### 3.2 Involved Testing Approaches
#### (1) Random-Based
Monkey

- Tool: https://developer.android.com/studio/test/other-testing-tools/monkey
- Parameters: `--ignore-crashes --ignore-timeouts --ignore-security-exceptions -v --throttle 200`
#### (2) Model-Based
Stoat

- Paper: [ESEC/FSE’17] Guided, stochastic model-based GUI testing of Android apps
- Tool: https://github.com/tingsu/Stoat

APE

- Paper: [ICSE’19] Practical GUI Testing of Android Applications via Model Abstraction and Refinement
- Tool: https://github.com/tianxiaogu/ape
#### (3) Systematic
ComboDroid

- Paper: [ICSE’20] ComboDroid: Generating High-Quality Test Inputs for Android Apps via Use Case Combinations
- Tool: https://github.com/skull591/ComboDroid-Artifact
#### (4) Machine-Learning-Based
**(4.1) Supervised-Learning-Based**<br />Humanoid

- Paper: [ASE’19] Humanoid: A Deep Learning-based Approach to Automated Black-box Android App Testing
- Tool: https://github.com/yzygitzh/Humanoid

**(4.2) Tabular-RL-Based**<br />Q-testing

- Paper: [ISSTA’20] Reinforcement Learning Based Curiosity-Driven Testing of Android Applications
- Tool: https://github.com/anlalalu/Q-testing

**(4.3) Deep-RL-Based**<br />ARES

- Paper: [TOSEM’22] Deep Reinforcement Learning for Black-box Testing of Android Apps
- Tool: https://github.com/H2SO4T/ARES

DQT

- Paper: [ICSE’24] Deeply Reinforcing Android GUI Testing with Deep Reinforcement Learning
- Tool: https://github.com/Yuanhong-Lan/DQT

### 3.3 Emulator Settings
#### Basic Settings

- Hardware: Google Pixel 2
- Resolution: 1080*1920
- Android Version: Android 9.0 (API Level 28)
- Google Sevice: Google APIs
#### Storage

- RAM: 4GB
- VM Heap: 2GB
- Internal Storage: 8GB
- SD Card: 1GB

<br/>

