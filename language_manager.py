"""
Language Management System for Cursor-Tools Application
Centralized language switching and translation management
"""

import os
import json
from typing import Dict, Any
from config import config


class LanguageManager:
    """Centralized language management with persistent storage"""

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'tr': 'Türkçe'
    }

    DEFAULT_LANGUAGE = 'en'

    def __init__(self):
        self.current_language = self.DEFAULT_LANGUAGE
        self.language_file_path = os.path.join(config.cursor_tools_dir, "language_preference.json")

        # Initialize language data
        self._init_language_data()

        # Load saved language preference
        self._load_language_preference()

    def _init_language_data(self):
        """Initialize hardcoded language translations"""
        self.translations = {
            'en': {
                # Main Menu
                'menu.title': 'Cursor-Tools - Main Menu',
                'menu.account_info': 'Account Information',
                'menu.device_id': 'Device ID Modification',
                'menu.disable_updates': 'Disable Updates',
                'menu.reset_machine_id': 'Reset Machine ID',
                'menu.pro_features': 'Pro UI Features',
                'menu.language_settings': 'Language Settings',
                'menu.exit': 'Exit',
                'menu.select_option': 'Select an option',
                'menu.invalid_choice': 'Invalid choice. Please try again.',

                # Language Settings
                'lang.title': 'Language Settings',
                'lang.current': 'Current Language: {language}',
                'lang.select_new': 'Select new language:',
                'lang.changed_success': 'Language changed to {language} successfully!',
                'lang.change_failed': 'Failed to change language: {error}',
                'lang.no_change': 'Language unchanged.',

                # Common Actions
                'common.confirm_exit': 'Are you sure you want to exit?',
                'common.press_enter': 'Press Enter to continue',
                'common.operation_cancelled': 'Operation cancelled.',
                'common.success': 'Operation completed successfully!',
                'common.failed': 'Operation failed: {error}',
                'common.admin_required': 'Administrator privileges required.',
                'common.backup_created': 'Backup created: {path}',
                'common.file_not_found': 'File not found: {path}',
                'common.permission_denied': 'Permission denied: {path}',

                # Account Information
                'account.title': 'Account Information',
                'account.retrieving': 'Retrieving account information...',
                'account.not_found': 'Account information not found.',
                'account.display_info': 'Account Details',
                'account.user_id': 'User ID: {user_id}',
                'account.email': 'Email: {email}',
                'account.subscription': 'Subscription: {subscription}',
                'account.view_info': 'View Account Information',
                'account.return_main': 'Return to Main Menu',

                # Device ID
                'device.title': 'Device ID Modification',
                'device.current_ids': 'Current Device IDs',
                'device.modify_confirm': 'Do you want to modify device IDs?',
                'device.modification_success': 'Device IDs modified successfully!',
                'device.modification_failed': 'Device ID modification failed: {error}',
                'device.backup_registry': 'Creating registry backup...',
                'device.change_id': 'Change Device ID',
                'device.restore_backup': 'Restore Backup',
                'device.view_current': 'View Current Registry Values',
                'device.return_main': 'Return to Main Menu',

                # Update Disabling
                'update.title': 'Disable Updates',
                'update.disable_confirm': 'Do you want to disable Cursor updates?',
                'update.disabled_success': 'Updates disabled successfully!',
                'update.disable_failed': 'Failed to disable updates: {error}',
                'update.enable_confirm': 'Do you want to enable Cursor updates?',
                'update.enabled_success': 'Updates enabled successfully!',
                'update.enable_failed': 'Failed to enable updates: {error}',
                'update.disable_auto': 'Disable Cursor Auto Update',
                'update.return_main': 'Return to Main Menu',

                # Machine ID Reset
                'reset.title': 'Reset Machine ID',
                'reset.confirm': 'Do you want to reset the machine ID?',
                'reset.success': 'Machine ID reset successfully!',
                'reset.failed': 'Machine ID reset failed: {error}',
                'reset.generating_id': 'Generating new machine ID...',
                'reset.updating_files': 'Updating configuration files...',
                'reset.reset_id': 'Reset Machine ID',
                'reset.restore_backup': 'Restore Backup',
                'reset.view_current': 'View Current Machine ID Values',
                'reset.return_main': 'Return to Main Menu',

                # Pro Features
                'pro.title': 'Pro UI Features',
                'pro.apply_confirm': 'Do you want to apply Pro UI features?',
                'pro.applied_success': 'Pro UI features applied successfully!',
                'pro.apply_failed': 'Failed to apply Pro features: {error}',
                'pro.step1': 'Step 1: Backing up files',
                'pro.step2': 'Step 2: Modifying UI files',
                'pro.step3': 'Step 3: Updating database',
                'pro.step4': 'Step 4: Applying workbench modifications',
                'pro.apply_features': 'Apply Pro UI Features',
                'pro.restore_backup': 'Restore Backup',
                'pro.return_main': 'Return to Main Menu',
                'pro.admin_warning': 'This operation requires administrator privileges and will modify Cursor files.',
                'pro.continue_confirm': 'Do you want to continue with applying all Pro UI features?',
                'pro.operation_cancelled': 'Operation cancelled by user.',
                'pro.restart_cursor': 'Please restart Cursor to see the changes.',
                'pro.no_backups': 'No Pro UI Features backups found.',
                'pro.backups_info': 'Backups are automatically created when you use \'Apply All Pro UI Features\'.',
                'pro.available_backups': 'Available Pro UI Features Backups',
                'pro.select_backup': 'Select backup to restore (1-{count}) or \'c\' to cancel',
                'pro.backup_cancelled': 'Backup restoration cancelled.',
                'pro.restore_warning': 'This will restore backup: {name}',
                'pro.overwrite_warning': 'Current Pro UI Features files will be overwritten!',
                'pro.restore_confirm': 'Are you sure you want to restore this backup?',
                'pro.restore_success': 'Pro UI Features backup restored successfully!',
                'pro.restore_restart': 'Please restart Cursor to see the restored changes.',
                'pro.restore_warnings': 'Backup restoration completed with some warnings. Check the output above for details.',
                'pro.invalid_selection': 'Invalid selection. Please try again.',
                'pro.restore_failed': 'Failed to restore backup: {error}',

                # Errors and Warnings
                'error.unexpected': 'Unexpected error occurred: {error}',
                'error.file_access': 'Cannot access file: {file}',
                'error.cursor_not_found': 'Cursor installation not found.',
                'error.cursor_running': 'Please close Cursor before proceeding.',
                'warning.backup_recommended': 'It is recommended to create a backup first.',
                'warning.irreversible': 'This operation cannot be undone.',

                # Application
                'app.title': 'Cursor-Tools',
                'app.subtitle': "Cursor's Best All-in-One Tool",
                'app.version': 'Version {version}',
                'app.thank_you': 'Thank you for using Cursor-Tools!',
                'app.update_check': 'Checking for updates...',
                'app.update_available': 'Update available: {version}',
                'app.update_failed': 'Update check failed: {error}',
                'app.update_not_available': 'No updates available. You are using the latest version.',
                'app.update_downloading': 'Downloading update...',
                'app.update_installing': 'Installing update...',
                'app.update_complete': 'Update completed successfully!',
                'app.update_restart_required': 'Please restart the application to use the new version.',
            },

            'tr': {
                # Ana Menü
                'menu.title': 'Cursor-Tools - Ana Menü',
                'menu.account_info': 'Hesap Bilgileri',
                'menu.device_id': 'Cihaz ID Değişikliği',
                'menu.disable_updates': 'Güncellemeleri Devre Dışı Bırak',
                'menu.reset_machine_id': 'Makine ID Sıfırla',
                'menu.pro_features': 'Pro UI Özellikleri',
                'menu.language_settings': 'Dil Ayarları',
                'menu.exit': 'Çıkış',
                'menu.select_option': 'Bir seçenek seçin',
                'menu.invalid_choice': 'Geçersiz seçim. Lütfen tekrar deneyin.',

                # Dil Ayarları
                'lang.title': 'Dil Ayarları',
                'lang.current': 'Mevcut Dil: {language}',
                'lang.select_new': 'Yeni dil seçin:',
                'lang.changed_success': 'Dil başarıyla {language} olarak değiştirildi!',
                'lang.change_failed': 'Dil değiştirme başarısız: {error}',
                'lang.no_change': 'Dil değiştirilmedi.',

                # Ortak İşlemler
                'common.confirm_exit': 'Çıkmak istediğinizden emin misiniz?',
                'common.press_enter': 'Devam etmek için Enter tuşuna basın',
                'common.operation_cancelled': 'İşlem iptal edildi.',
                'common.success': 'İşlem başarıyla tamamlandı!',
                'common.failed': 'İşlem başarısız: {error}',
                'common.admin_required': 'Yönetici yetkileri gerekli.',
                'common.backup_created': 'Yedek oluşturuldu: {path}',
                'common.file_not_found': 'Dosya bulunamadı: {path}',
                'common.permission_denied': 'İzin reddedildi: {path}',

                # Hesap Bilgileri
                'account.title': 'Hesap Bilgileri',
                'account.retrieving': 'Hesap bilgileri alınıyor...',
                'account.not_found': 'Hesap bilgileri bulunamadı.',
                'account.display_info': 'Hesap Detayları',
                'account.user_id': 'Kullanıcı ID: {user_id}',
                'account.email': 'E-posta: {email}',
                'account.subscription': 'Abonelik: {subscription}',
                'account.view_info': 'Hesap Bilgilerini Görüntüle',
                'account.return_main': 'Ana Menüye Dön',

                # Cihaz ID
                'device.title': 'Cihaz ID Değişikliği',
                'device.current_ids': 'Mevcut Cihaz ID\'leri',
                'device.modify_confirm': 'Cihaz ID\'lerini değiştirmek istiyor musunuz?',
                'device.modification_success': 'Cihaz ID\'leri başarıyla değiştirildi!',
                'device.modification_failed': 'Cihaz ID değişikliği başarısız: {error}',
                'device.backup_registry': 'Kayıt defteri yedeği oluşturuluyor...',
                'device.change_id': 'Cihaz ID Değiştir',
                'device.restore_backup': 'Yedeği Geri Yükle',
                'device.view_current': 'Mevcut Kayıt Defteri Değerlerini Görüntüle',
                'device.return_main': 'Ana Menüye Dön',

                # Güncelleme Devre Dışı Bırakma
                'update.title': 'Güncellemeleri Devre Dışı Bırak',
                'update.disable_confirm': 'Cursor güncellemelerini devre dışı bırakmak istiyor musunuz?',
                'update.disabled_success': 'Güncellemeler başarıyla devre dışı bırakıldı!',
                'update.disable_failed': 'Güncellemeleri devre dışı bırakma başarısız: {error}',
                'update.enable_confirm': 'Cursor güncellemelerini etkinleştirmek istiyor musunuz?',
                'update.enabled_success': 'Güncellemeler başarıyla etkinleştirildi!',
                'update.enable_failed': 'Güncellemeleri etkinleştirme başarısız: {error}',
                'update.disable_auto': 'Cursor Otomatik Güncellemesini Devre Dışı Bırak',
                'update.return_main': 'Ana Menüye Dön',

                # Makine ID Sıfırlama
                'reset.title': 'Makine ID Sıfırla',
                'reset.confirm': 'Makine ID\'sini sıfırlamak istiyor musunuz?',
                'reset.success': 'Makine ID başarıyla sıfırlandı!',
                'reset.failed': 'Makine ID sıfırlama başarısız: {error}',
                'reset.generating_id': 'Yeni makine ID oluşturuluyor...',
                'reset.updating_files': 'Yapılandırma dosyaları güncelleniyor...',
                'reset.reset_id': 'Makine ID Sıfırla',
                'reset.restore_backup': 'Yedeği Geri Yükle',
                'reset.view_current': 'Mevcut Makine ID Değerlerini Görüntüle',
                'reset.return_main': 'Ana Menüye Dön',

                # Pro Özellikler
                'pro.title': 'Pro UI Özellikleri',
                'pro.apply_confirm': 'Pro UI özelliklerini uygulamak istiyor musunuz?',
                'pro.applied_success': 'Pro UI özellikleri başarıyla uygulandı!',
                'pro.apply_failed': 'Pro özellikleri uygulama başarısız: {error}',
                'pro.step1': 'Adım 1: Dosyalar yedekleniyor',
                'pro.step2': 'Adım 2: UI dosyaları değiştiriliyor',
                'pro.step3': 'Adım 3: Veritabanı güncelleniyor',
                'pro.step4': 'Adım 4: Workbench değişiklikleri uygulanıyor',
                'pro.apply_features': 'Pro UI Özelliklerini Uygula',
                'pro.restore_backup': 'Yedeği Geri Yükle',
                'pro.return_main': 'Ana Menüye Dön',
                'pro.admin_warning': 'Bu işlem yönetici yetkileri gerektirir ve Cursor dosyalarını değiştirir.',
                'pro.continue_confirm': 'Tüm Pro UI özelliklerini uygulamaya devam etmek istiyor musunuz?',
                'pro.operation_cancelled': 'İşlem kullanıcı tarafından iptal edildi.',
                'pro.restart_cursor': 'Değişiklikleri görmek için lütfen Cursor\'ı yeniden başlatın.',
                'pro.no_backups': 'Pro UI Özellikleri yedekleri bulunamadı.',
                'pro.backups_info': 'Yedekler \'Tüm Pro UI Özelliklerini Uygula\' kullandığınızda otomatik olarak oluşturulur.',
                'pro.available_backups': 'Mevcut Pro UI Özellikleri Yedekleri',
                'pro.select_backup': 'Geri yüklenecek yedeği seçin (1-{count}) veya iptal için \'c\'',
                'pro.backup_cancelled': 'Yedek geri yükleme iptal edildi.',
                'pro.restore_warning': 'Bu yedek geri yüklenecek: {name}',
                'pro.overwrite_warning': 'Mevcut Pro UI Özellikleri dosyaları üzerine yazılacak!',
                'pro.restore_confirm': 'Bu yedeği geri yüklemek istediğinizden emin misiniz?',
                'pro.restore_success': 'Pro UI Özellikleri yedeği başarıyla geri yüklendi!',
                'pro.restore_restart': 'Geri yüklenen değişiklikleri görmek için lütfen Cursor\'ı yeniden başlatın.',
                'pro.restore_warnings': 'Yedek geri yükleme bazı uyarılarla tamamlandı. Ayrıntılar için yukarıdaki çıktıyı kontrol edin.',
                'pro.invalid_selection': 'Geçersiz seçim. Lütfen tekrar deneyin.',
                'pro.restore_failed': 'Yedek geri yükleme başarısız: {error}',

                # Hatalar ve Uyarılar
                'error.unexpected': 'Beklenmeyen hata oluştu: {error}',
                'error.file_access': 'Dosyaya erişilemiyor: {file}',
                'error.cursor_not_found': 'Cursor kurulumu bulunamadı.',
                'error.cursor_running': 'Lütfen devam etmeden önce Cursor\'ı kapatın.',
                'warning.backup_recommended': 'Önce yedek oluşturmanız önerilir.',
                'warning.irreversible': 'Bu işlem geri alınamaz.',

                # Uygulama
                'app.title': '     Cursor-Tools',
                'app.subtitle': "Cursor'un En İyi Hepsi Bir Arada Aracı",
                'app.version': 'Sürüm {version}',
                'app.thank_you': 'Cursor-Tools kullandığınız için teşekkürler!',
                'app.update_check': 'Güncellemeler kontrol ediliyor...',
                'app.update_available': 'Güncelleme mevcut: {version}',
                'app.update_failed': 'Güncelleme kontrolü başarısız: {error}',
                'app.update_not_available': 'Güncelleme mevcut değil. En son sürümü kullanıyorsunuz.',
                'app.update_downloading': 'Güncelleme indiriliyor...',
                'app.update_installing': 'Güncelleme yükleniyor...',
                'app.update_complete': 'Güncelleme başarıyla tamamlandı!',
                'app.update_restart_required': 'Yeni sürümü kullanmak için lütfen uygulamayı yeniden başlatın.',
            }
        }

    def _load_language_preference(self):
        """Load saved language preference from file"""
        try:
            if os.path.exists(self.language_file_path):
                with open(self.language_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_lang = data.get('language', self.DEFAULT_LANGUAGE)
                    if saved_lang in self.SUPPORTED_LANGUAGES:
                        self.current_language = saved_lang
        except Exception:
            # If loading fails, use default language
            self.current_language = self.DEFAULT_LANGUAGE

    def _save_language_preference(self):
        """Save current language preference to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.language_file_path), exist_ok=True)

            data = {
                'language': self.current_language,
                'saved_at': str(os.path.getmtime(__file__) if os.path.exists(__file__) else 0)
            }

            with open(self.language_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception:
            # Silently fail if saving doesn't work
            pass

    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language

    def get_current_language_name(self) -> str:
        """Get current language display name"""
        return self.SUPPORTED_LANGUAGES.get(self.current_language, 'Unknown')

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()

    def set_language(self, language_code: str) -> bool:
        """Set current language and save preference"""
        if language_code not in self.SUPPORTED_LANGUAGES:
            return False

        self.current_language = language_code
        self._save_language_preference()
        return True

    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text for the given key with optional parameters"""
        try:
            # Get text from current language
            text = self.translations[self.current_language].get(key)

            # Fallback to English if not found
            if text is None:
                text = self.translations[self.DEFAULT_LANGUAGE].get(key, key)

            # Format with parameters if provided
            if kwargs:
                text = text.format(**kwargs)

            return text

        except Exception:
            # Return key if all else fails
            return key

    def get_language_menu_options(self) -> Dict[str, str]:
        """Get language options for menu display"""
        options = {}
        for i, (code, name) in enumerate(self.SUPPORTED_LANGUAGES.items(), 1):
            marker = " (Current)" if code == self.current_language else ""
            options[str(i)] = f"{name}{marker}"
        return options


class LanguageSettingsManager:
    """Manager for language settings menu and operations"""

    def __init__(self):
        self.lang = language_manager

    def run_language_settings_menu(self):
        """Run the language settings menu"""
        from ui_manager import UIManager
        ui_manager = UIManager()

        while True:
            ui_manager.clear_screen()
            ui_manager.display_header()
            ui_manager.display_language_menu()

            # Get valid choices (1, 2 for languages + 0 for exit)
            valid_choices = list(self.lang.get_language_menu_options().keys()) + ["0"]
            choice = ui_manager.get_user_choice(valid_choices=valid_choices)

            if choice is None or choice == "0":
                break

            # Handle language selection
            languages = list(self.lang.SUPPORTED_LANGUAGES.keys())
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(languages):
                    selected_lang_code = languages[choice_index]
                    selected_lang_name = self.lang.SUPPORTED_LANGUAGES[selected_lang_code]

                    if selected_lang_code == self.lang.get_current_language():
                        ui_manager.display_text('lang.no_change', "info")
                    else:
                        # Change language
                        if self.lang.set_language(selected_lang_code):
                            ui_manager.display_text('lang.changed_success', "success",
                                                  language=selected_lang_name)
                        else:
                            ui_manager.display_text('lang.change_failed', "error",
                                                  error="Unknown error")

                    ui_manager.pause()
                else:
                    ui_manager.display_text('menu.invalid_choice', "error")
                    ui_manager.pause()
            except (ValueError, IndexError):
                ui_manager.display_text('menu.invalid_choice', "error")
                ui_manager.pause()


# Global language manager instance
language_manager = LanguageManager()
