# ----------------------
# @Time  : 2022 Apr
# @Author: Yuanhong Lan
# ----------------------
import os

from enum import Enum
from typing import List

from runtime_collection.collector_util.util_coverage import ApkBriefInfo, ApkSourceCodeArgs
from runtime_collection.collector_util.util_coverage import JavaVersion
from constant.platform_constant import PlatformConstant


class Apps(Enum):
    Signal = "Signal"
    MyExpenses = "MyExpenses"
    AnkiDroid = "AnkiDroid"
    SuntimesWidget = "SuntimesWidget"
    MoneyManagerEx = "MoneyManagerEx"
    AmazeFileManager = "AmazeFileManager"
    RunnerUp = "RunnerUp"
    NewPipe = "NewPipe"
    Tachiyomi = "Tachiyomi"
    K9Mail = "K9Mail"
    AntennaPod = "AntennaPod"
    Conversations = "Conversations"
    AnyMemo = "AnyMemo"
    Timber = "Timber"
    Vanilla = "Vanilla"
    LoopHabitTracker = "LoopHabitTracker"
    BetterBatteryStats = "BetterBatteryStats"
    LBRY = "LBRY"
    DuckDuckGo = "DuckDuckGo"
    BookCatalogue = "BookCatalogue"
    CoronaWarn = "CoronaWarn"
    APhotoManager = "APhotoManager"
    ConnectBot = "ConnectBot"
    KeePassDroid = "KeePassDroid"
    Materialistic = "Materialistic"
    Swiftp = "Swiftp"
    Notes = "Notes"
    AlarmClock = "AlarmClock"
    WhoHasMyStuff = "WhoHasMyStuff"
    Firefox = "Firefox"
    Wikipedia = "Wikipedia"
    Aard2 = "Aard2"
    Diary = "Diary"
    Currencies = "Currencies"
    KindMind = "KindMind"
    CEToolbox = "CEToolbox"
    ArxivExplorer = "ArxivExplorer"
    TranslateYou = "TranslateYou"
    PasswordManager = "PasswordManager"
    WordPress = "WordPress"
    SimpleDraw = "SimpleDraw"
    SimpleTask = "SimpleTask"

ALL_APPS: List[Apps] = list(Apps)
ALL_APPS_STR = [str(item) for item in ALL_APPS]

# APP: Apps.Signal
# APP STR: "Apps.Signal"
# APP NAME: "Signal"


APK_BRIEF_INFO_DICT = {
    Apps.Signal: ApkBriefInfo("Signal-6.3.3-debug.apk", 84, 904470),
    Apps.CoronaWarn: ApkBriefInfo("CoronaWarn-2.28.3-debug.apk", 12, 459709),
    Apps.Tachiyomi: ApkBriefInfo("Tachiyomi-0.13.6-debug.apk", 13, 412967),
    Apps.DuckDuckGo: ApkBriefInfo("DuckDuckGo-5.140.0-debug.apk", 55, 363204),
    Apps.Firefox: ApkBriefInfo("Firefox-110.0a1-nightly.apk", 17, 348086),
    Apps.MyExpenses: ApkBriefInfo("MyExpenses-r554-debug.apk", 44, 300635),
    Apps.AnkiDroid: ApkBriefInfo("AnkiDroid-2.16.2-debug.apk", 35, 259600),
    Apps.K9Mail: ApkBriefInfo("K9Mail-6.712-debug.apk", 33, 349645),
    Apps.Conversations: ApkBriefInfo("Conversations-2.10.10-debug.apk", 36, 191099),
    Apps.SuntimesWidget: ApkBriefInfo("SuntimesWidget-0.15.6-debug.apk", 32, 232988),
    Apps.NewPipe: ApkBriefInfo("NewPipe-0.23.3-debug.apk", 14, 149421),
    Apps.AmazeFileManager: ApkBriefInfo("AmazeFileManager-3.8.5-debug.apk", 10, 144944),
    Apps.MoneyManagerEx: ApkBriefInfo("MoneyManagerEx-2021.05.13-debug.apk", 50, 127964),
    Apps.BookCatalogue: ApkBriefInfo("BookCatalogue-5.3.0-5-debug.apk", 35, 117790),
    Apps.AntennaPod: ApkBriefInfo("AntennaPod-3.1.0_beta2-debug.apk", 10, 116750),
    Apps.LBRY: ApkBriefInfo("LBRY-0.17.1-debug.apk", 6, 89679),
    Apps.RunnerUp: ApkBriefInfo("RunnerUp-2.6.0.2-debug.apk", 16, 70184),
    Apps.ConnectBot: ApkBriefInfo("ConnectBot-1.9.9-debug.apk", 11, 70584),
    Apps.APhotoManager: ApkBriefInfo("APhotoManager-0.8.3.200315-debug.apk", 11, 54313),
    Apps.Timber: ApkBriefInfo("Timber-1.8-debug.apk", 9, 54691),
    Apps.BetterBatteryStats: ApkBriefInfo("BetterBatteryStats-3.4.0-debug.apk", 12, 52918),
    Apps.Vanilla: ApkBriefInfo("Vanilla-1.3.1-debug.apk", 13, 47367),
    Apps.AnyMemo: ApkBriefInfo("AnyMemo-10.11.7-debug.apk", 28, 45914),
    Apps.LoopHabitTracker: ApkBriefInfo("LoopHabitTracker-2.2.0-debug.apk", 11, 44896),
    Apps.KeePassDroid: ApkBriefInfo("KeePassDroid-2.6.8-debug.apk", 15, 38496),
    Apps.AlarmClock: ApkBriefInfo("AlarmClock-3.15.02-debug.apk", 5, 29356),
    Apps.Materialistic: ApkBriefInfo("Materialistic-3.3-debug.apk", 23, 33967),
    Apps.Notes: ApkBriefInfo("Notes-1.4.2-debug.apk", 12, 18667),
    Apps.Swiftp: ApkBriefInfo("Swiftp-3.1-debug.apk", 4, 14408),
    Apps.WhoHasMyStuff: ApkBriefInfo("WhoHasMyStuff-1.1.0-debug.apk", 7, 4533),
    Apps.Wikipedia: ApkBriefInfo("Wikipedia-2.7.50453-debug.apk", 52, 334262),
    Apps.Aard2: ApkBriefInfo("Aard2-0.54-debug.apk", 2, 11290),
    Apps.Diary: ApkBriefInfo("Diary-1.102-debug.apk", 4, 9333),
    Apps.Currencies: ApkBriefInfo("Currencies-1.20.4-debug.apk", 3, 18879),
    Apps.KindMind: ApkBriefInfo("KindMind-1.2.1_BETA-debug.apk", 5, 7652),
    Apps.CEToolbox: ApkBriefInfo("CEToolbox-1.5.0-debug.apk", 7, 6473),
    Apps.ArxivExplorer: ApkBriefInfo("ArxivExplorer-4.1.1-debug.apk", 5, 8923),
    Apps.TranslateYou: ApkBriefInfo("TranslateYou-7.1-debug.apk", 3, 43875),
    Apps.PasswordManager: ApkBriefInfo("PasswordManager-1.1-debug.apk", 4, 15477),
    Apps.WordPress: ApkBriefInfo("WordPress-23.5rc2-debug.apk", 119, 742156),
    Apps.SimpleDraw: ApkBriefInfo("SimpleDraw-6.9.6-debug.apk", 8, 8096),
    Apps.SimpleTask: ApkBriefInfo("SimpleTask-11.0.1-debug.apk", 14, 45361),
}

SORTED_APP_LIST_BY_INSTRUCTION = sorted(ALL_APPS, key=lambda x: -APK_BRIEF_INFO_DICT[x].instruction_count)
SORTED_APP_NAME_LIST_BY_INSTRUCTION = [item.value for item in SORTED_APP_LIST_BY_INSTRUCTION]

SORTED_APP_LIST_BY_ACTIVITY = sorted(ALL_APPS, key=lambda x: (-APK_BRIEF_INFO_DICT[x].activity_count, -APK_BRIEF_INFO_DICT[x].instruction_count))
SORTED_APP_NAME_LIST_BY_ACTIVITY = [item.value for item in SORTED_APP_LIST_BY_ACTIVITY]

APK_ABSOLUTE_PATH_DICT = {key: os.path.join(PlatformConstant.APK_DIR, value.apk_file_name) for key, value in APK_BRIEF_INFO_DICT.items()}



APK_SOURCE_CODE_ARGS_DICT = {
    Apps.Signal: ApkSourceCodeArgs("org.thoughtcrime.securesms", "Signal/Signal-Android", "./app/build", JavaVersion.JAVA_11),
    Apps.MyExpenses: ApkSourceCodeArgs("org.totschnig.myexpenses.debug", "MyExpenses/MyExpenses", "./myExpenses/build", JavaVersion.JAVA_11),
    Apps.AnkiDroid: ApkSourceCodeArgs("com.ichi2.anki.debug", "AnkiDroid/Anki-Android", "./AnkiDroid/build", JavaVersion.JAVA_17),
    Apps.SuntimesWidget: ApkSourceCodeArgs("com.forrestguice.suntimeswidget", "SuntimesWidget/SuntimesWidget", "./app/build", JavaVersion.JAVA_8),
    Apps.MoneyManagerEx: ApkSourceCodeArgs("com.money.manager.ex", "MoneyManagerEx/android-money-manager-ex", "./app/build", JavaVersion.JAVA_11),
    Apps.AmazeFileManager: ApkSourceCodeArgs("com.amaze.filemanager.debug", "AmazeFileManager/AmazeFileManager", "./app/build", JavaVersion.JAVA_11),
    Apps.RunnerUp: ApkSourceCodeArgs("org.runnerup.free.debug", "RunnerUp/runnerup", "./app/build", JavaVersion.JAVA_17),
    Apps.NewPipe: ApkSourceCodeArgs("org.schabi.newpipe.debug", "NewPipe/NewPipe", "./app/build", JavaVersion.JAVA_11),
    Apps.Tachiyomi: ApkSourceCodeArgs("eu.kanade.tachiyomi.debug", "Tachiyomi/tachiyomi", "./app/build", JavaVersion.JAVA_11),
    Apps.K9Mail: ApkSourceCodeArgs("com.fsck.k9.debug", "K9Mail/k-9", "./app/k9mail/build", JavaVersion.JAVA_17),
    Apps.AntennaPod: ApkSourceCodeArgs("de.danoeh.antennapod.debug", "AntennaPod/AntennaPod", "./app/build", JavaVersion.JAVA_11),
    Apps.Conversations: ApkSourceCodeArgs("eu.siacs.conversations", "Conversations/Conversations", "./build", JavaVersion.JAVA_11),
    Apps.AnyMemo: ApkSourceCodeArgs("org.liberty.android.fantastischmemodev", "AnyMemo/AnyMemo", "./app/build", JavaVersion.JAVA_11),
    Apps.Timber: ApkSourceCodeArgs("naman14.timber", "Timber/Timber", "./app/build", JavaVersion.JAVA_8),
    Apps.Vanilla: ApkSourceCodeArgs("ch.blinkenlights.android.vanilla", "Vanilla/vanilla", "./app/build", JavaVersion.JAVA_11),
    Apps.LoopHabitTracker: ApkSourceCodeArgs("org.isoron.uhabits", "LoopHabitTracker/uhabits", "./uhabits-android/build", JavaVersion.JAVA_11),
    Apps.BetterBatteryStats: ApkSourceCodeArgs("com.asksven.betterbatterystats_xdaedition", "BetterBatteryStats/BetterBatteryStats", "./app/build", JavaVersion.JAVA_11),
    Apps.LBRY: ApkSourceCodeArgs("io.lbry.browser", "LBRY/lbry-android", "./app/build", JavaVersion.JAVA_11),
    Apps.DuckDuckGo: ApkSourceCodeArgs("com.duckduckgo.mobile.android.debug", "DuckDuckGo/Android", "./app/build", JavaVersion.JAVA_11),
    Apps.BookCatalogue: ApkSourceCodeArgs("com.eleybourn.bookcatalogue", "BookCatalogue/Book-Catalogue", "./build", JavaVersion.JAVA_11),
    Apps.CoronaWarn: ApkSourceCodeArgs("de.rki.coronawarnapp", "CoronaWarn/cwa-app-android", "./Corona-Warn-App/build", JavaVersion.JAVA_11),
    Apps.APhotoManager: ApkSourceCodeArgs("de.k3b.android.androFotoFinder.debug", "APhotoManager/APhotoManager", "./app/build", JavaVersion.JAVA_11),
    Apps.ConnectBot: ApkSourceCodeArgs("org.connectbot.debug", "ConnectBot/connectbot", "./app/build", JavaVersion.JAVA_11),
    Apps.KeePassDroid: ApkSourceCodeArgs("com.android.keepass", "KeePassDroid/keepassdroid", "./app/build", JavaVersion.JAVA_11),
    Apps.Materialistic: ApkSourceCodeArgs("io.github.hidroh.materialistic", "Materialistic/materialistic", "./app/build", JavaVersion.JAVA_11),
    Apps.Swiftp: ApkSourceCodeArgs("be.ppareit.swiftp_free", "Swiftp/swiftp", "./app/build", JavaVersion.JAVA_17),
    Apps.Notes: ApkSourceCodeArgs("org.secuso.privacyfriendlynotes", "Notes/privacy-friendly-notes", "./app/build", JavaVersion.JAVA_11),
    Apps.AlarmClock: ApkSourceCodeArgs("com.better.alarm.debug", "AlarmClock/AlarmClock", "./app/build", JavaVersion.JAVA_11),
    Apps.WhoHasMyStuff: ApkSourceCodeArgs("de.freewarepoint.whohasmystuff", "WhoHasMyStuff/whohasmystuff", "./app/build", JavaVersion.JAVA_11),
    Apps.Firefox: ApkSourceCodeArgs("org.mozilla.fenix", "Firefox/fenix", "./app/build", JavaVersion.JAVA_11),
    Apps.Wikipedia: ApkSourceCodeArgs("org.wikipedia.alpha", "Wikipedia/apps-android-wikipedia", "./app/build", JavaVersion.JAVA_17),
    Apps.Aard2: ApkSourceCodeArgs("itkach.aard2", "Aard2/aard2-android", "./build", JavaVersion.JAVA_17),
    Apps.Diary: ApkSourceCodeArgs("org.billthefarmer.diary", "Diary/diary", "./build", JavaVersion.JAVA_11),
    Apps.Currencies: ApkSourceCodeArgs("de.salomax.currencies.debug", "Currencies/currencies", "./app/build", JavaVersion.JAVA_17),
    Apps.KindMind: ApkSourceCodeArgs("com.sunyata.kindmind", "KindMind/kindmind", "./app/build", JavaVersion.JAVA_11),
    Apps.CEToolbox: ApkSourceCodeArgs("com.github.cetoolbox", "CEToolbox/cetoolbox", "./app/build", JavaVersion.JAVA_17),
    Apps.ArxivExplorer: ApkSourceCodeArgs("com.gbeatty.arxiv", "ArxivExplorer/arXiv-eXplorer", "./app/build", JavaVersion.JAVA_8),
    Apps.TranslateYou: ApkSourceCodeArgs("com.bnyro.translate.debug", "TranslateYou/TranslateYou", "./app/build", JavaVersion.JAVA_17),
    Apps.PasswordManager: ApkSourceCodeArgs("com.ishant.passwordmanager", "PasswordManager/PasswordManager", "./app/build", JavaVersion.JAVA_8),
    Apps.WordPress: ApkSourceCodeArgs("org.wordpress.android.prealpha", "WordPress/WordPress-Android", "./WordPress/build", JavaVersion.JAVA_17),
    Apps.SimpleDraw: ApkSourceCodeArgs("com.simplemobiletools.draw.pro.debug", "SimpleDraw/Simple-Draw", "./app/build", JavaVersion.JAVA_17),
    Apps.SimpleTask: ApkSourceCodeArgs("nl.mpcjanssen.simpletask.debug", "SimpleTask/simpletask-android", "./app/build", JavaVersion.JAVA_11),
}



# asserts
for app in list(Apps):
    assert app.value in str(app)
for key, value in APK_BRIEF_INFO_DICT.items():
    assert key.value in value.apk_file_name
for key, value in APK_SOURCE_CODE_ARGS_DICT.items():
    assert key.value in value.root_path
assert set(Apps) == set(APK_BRIEF_INFO_DICT.keys()) == set(APK_SOURCE_CODE_ARGS_DICT.keys())


def get_app_name_by_package_name(package_name: str) -> str:
    for app_key, app_value in APK_SOURCE_CODE_ARGS_DICT.items():
        if app_value.apk_package == package_name:
            return str(app_key.value)
    assert False

def get_app_by_package_name(package_name: str) -> Apps:
    for app_key, app_value in APK_SOURCE_CODE_ARGS_DICT.items():
        if app_value.apk_package == package_name:
            return app_key
    assert False


empirical_app_list_all = [
    Apps.Signal,
    Apps.WordPress,
    Apps.K9Mail,
    Apps.Wikipedia,
    Apps.MyExpenses,
    Apps.AnkiDroid,
    Apps.SuntimesWidget,
    Apps.AmazeFileManager,
    Apps.MoneyManagerEx,
    Apps.BookCatalogue,
    Apps.AntennaPod,
    Apps.ConnectBot,
    Apps.RunnerUp,
    Apps.Timber,
    Apps.APhotoManager,
    Apps.BetterBatteryStats,
    Apps.Vanilla,
    Apps.AnyMemo,
    Apps.SimpleTask,
    Apps.LoopHabitTracker,
    Apps.TranslateYou,
    Apps.KeePassDroid,
    Apps.Materialistic,
    Apps.AlarmClock,
    Apps.Currencies,
    Apps.Notes,
    Apps.PasswordManager,
    Apps.Swiftp,
    Apps.Aard2,
    Apps.Diary,
    Apps.ArxivExplorer,
    Apps.SimpleDraw,
    Apps.KindMind,
    Apps.CEToolbox,
    Apps.WhoHasMyStuff,
    Apps.Tachiyomi,
    Apps.Conversations,
    Apps.CoronaWarn,
    Apps.DuckDuckGo,
    Apps.Firefox,
    Apps.LBRY,
    Apps.NewPipe,
]
empirical_app_list_all_act_ge_50 = [item for item in empirical_app_list_all if APK_BRIEF_INFO_DICT[item].activity_count >= 50]
empirical_app_list_all_act_ge_35 = [item for item in empirical_app_list_all if APK_BRIEF_INFO_DICT[item].activity_count >= 35]
empirical_app_list_all_act_ge_20 = [item for item in empirical_app_list_all if APK_BRIEF_INFO_DICT[item].activity_count >= 20]
empirical_app_list_all_act_ge_10_lt_20 = [item for item in empirical_app_list_all if 10 <= APK_BRIEF_INFO_DICT[item].activity_count < 20]
empirical_app_list_all_act_lt_10 = [item for item in empirical_app_list_all if APK_BRIEF_INFO_DICT[item].activity_count < 10]

empirical_app_list_all_for_combodroid = list(
    set(empirical_app_list_all) - {
    Apps.Currencies, Apps.Diary, Apps.K9Mail, Apps.WordPress, Apps.SuntimesWidget, Apps.BetterBatteryStats, Apps.Signal,
    Apps.Firefox, Apps.Tachiyomi, Apps.CoronaWarn, Apps.DuckDuckGo, Apps.NewPipe, Apps.LBRY,
})

SORTED_TOOL_NAME_LIST = ["Monkey", "Stoat", "APE", "Combodroid", "Humanoid", "QT", "ARES", "DQT"]
