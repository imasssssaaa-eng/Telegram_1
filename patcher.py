import os
import re
import sys

def patch_werygram_core():
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    userconfig_path = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    messages_path = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    
    if not os.path.exists(settings_path):
        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: Файл не найден: {settings_path}")
        sys.exit(1)

    print("⏳ Тройной авто-патчер Werygram (AyuGram-style) запущен...")

    # ==========================================
    # 1. МОДЕРНИЗАЦИЯ ИНТЕРФЕЙСА (SettingsActivity)
    # ==========================================
    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Полностью вычищаем все старые версии кнопок и классов (любые старые WeryGram Activity)
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'public static class WeryGramSettingsActivity[\s\S]*?$', '', code, flags=re.MULTILINE)
    code = re.sub(r'public static class WerygramSettingsActivity[\s\S]*?$', '', code, flags=re.MULTILINE)

    # Создаем нативную красивую кнопку-ссылку с именем "Werygram"
    werygram_btn = 'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.msg_settings, "Werygram"));'

    # Находим блок "Уведомлений" (Notifications), чтобы воткнуть нашу кнопку НАД ним
    match_notif = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match_notif:
        anchor = match_notif.group(1)
        code = code.replace(anchor, f'{werygram_btn}\n        {anchor}')
        print("✅ Главная кнопка 'Werygram' установлена на самый верх!")
    else:
        code = code.replace("switch (item.id) {", f"{werygram_btn}\n        switch (item.id) {{")
        print("✅ Главная кнопка 'Werygram' установлена (резервный метод).")

    # Вшиваем обработку клика: открытие нашего нового многофункционального экрана
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        click_logic = """case 9999: {
            presentFragment(new WerygramSettingsActivity());
            break;
        }"""
        code = code.replace(switch_anchor, f"{switch_anchor}\n            {click_logic}")
        print("✅ Обработчик клика перенаправлен на WerygramSettingsActivity!")

    # Внедряем класс многофункционального списка меню в самый конец файла SettingsActivity.java
    code = code.strip()
    if code.endswith("}"):
        werygram_menu_class = """
    public static class WerygramSettingsActivity extends org.telegram.ui.ActionBar.BaseFragment {
        @Override
        public android.view.View createView(android.content.Context context) {
            actionBar.setBackButtonImage(R.drawable.ic_ab_back);
            actionBar.setTitle("Werygram");
            actionBar.setActionBarMenuOnItemClick(new org.telegram.ui.ActionBar.ActionBar.ActionBarMenuOnItemClick() {
                @Override
                public void onItemClick(int id) {
                    if (id == -1) {
                        finishFragment();
                    }
                }
            });

            // Основной скролл-контейнер для поддержки бесконечного списка функций
            android.widget.ScrollView scrollView = new android.widget.ScrollView(context);
            scrollView.setFillViewport(true);
            scrollView.setBackgroundColor(org.telegram.ui.ActionBar.Theme.getColor(org.telegram.ui.ActionBar.Theme.key_windowBackgroundWhite));

            android.widget.LinearLayout linearLayout = new android.widget.LinearLayout(context);
            linearLayout.setOrientation(android.widget.LinearLayout.VERTICAL);
            scrollView.addView(linearLayout, new android.widget.FrameLayout.LayoutParams(android.widget.FrameLayout.LayoutParams.MATCH_PARENT, android.widget.FrameLayout.LayoutParams.WRAP_CONTENT));

            // ----------------------------------------------------
            # ФУНКЦИЯ 1: Визуальный Премиум
            // ----------------------------------------------------
            final org.telegram.ui.Cells.TextCheckCell premiumCell = new org.telegram.ui.Cells.TextCheckCell(context);
            boolean isPremium = org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false);
            premiumCell.setTextAndCheck("Включить Premium (Визуально)", isPremium, true); // true = рисовать полосу снизу
            premiumCell.setBackground(org.telegram.ui.ActionBar.Theme.getSelectorDrawable(true));
            premiumCell.setOnClickListener(new android.view.View.OnClickListener() {
                @Override
                public void onClick(android.view.View v) {
                    boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false);
                    org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("visual_premium", newState).apply();
                    premiumCell.setChecked(newState);
                    org.telegram.messenger.UserConfig.getInstance(currentAccount).getCurrentUser();
                }
            });
            linearLayout.addView(premiumCell);

            // ----------------------------------------------------
            # ФУНКЦИЯ 2: Синяя галочка (Верификация)
            // ----------------------------------------------------
            final org.telegram.ui.Cells.TextCheckCell verifiedCell = new org.telegram.ui.Cells.TextCheckCell(context);
            boolean isVerified = org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_verified", false);
            verifiedCell.setTextAndCheck("Синяя галочка верификации", isVerified, true); // true = полоса снизу
            verifiedCell.setBackground(org.telegram.ui.ActionBar.Theme.getSelectorDrawable(true));
            verifiedCell.setOnClickListener(new android.view.View.OnClickListener() {
                @Override
                public void onClick(android.view.View v) {
                    boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_verified", false);
                    org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("visual_verified", newState).apply();
                    verifiedCell.setChecked(newState);
                    org.telegram.messenger.UserConfig.getInstance(currentAccount).getCurrentUser();
                }
            });
            linearLayout.addView(verifiedCell);

            // ----------------------------------------------------
            # ФУНКЦИЯ 3: Шаблон (Скрыть чтение историй)
            // ----------------------------------------------------
            final org.telegram.ui.Cells.TextCheckCell storiesCell = new org.telegram.ui.Cells.TextCheckCell(context);
            boolean isStoriesHidden = org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wg_hide_stories", false);
            storiesCell.setTextAndCheck("Не читать истории (Шаблон)", isStoriesHidden, true);
            storiesCell.setBackground(org.telegram.ui.ActionBar.Theme.getSelectorDrawable(true));
            storiesCell.setOnClickListener(new android.view.View.OnClickListener() {
                @Override
                public void onClick(android.view.View v) {
                    boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wg_hide_stories", false);
                    org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("wg_hide_stories", newState).apply();
                    storiesCell.setChecked(newState);
                }
            });
            linearLayout.addView(storiesCell);

            // ----------------------------------------------------
            # ФУНКЦИЯ 4: Шаблон (Режим невидимки)
            // ----------------------------------------------------
            final org.telegram.ui.Cells.TextCheckCell ghostCell = new org.telegram.ui.Cells.TextCheckCell(context);
            boolean isGhost = org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wg_ghost_mode", false);
            ghostCell.setTextAndCheck("Режим невидимки (Шаблон)", isGhost, false); // false = последний элемент, разделитель не нужен
            ghostCell.setBackground(org.telegram.ui.ActionBar.Theme.getSelectorDrawable(true));
            ghostCell.setOnClickListener(new android.view.View.OnClickListener() {
                @Override
                public void onClick(android.view.View v) {
                    boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("wg_ghost_mode", false);
                    org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("wg_ghost_mode", newState).apply();
                    ghostCell.setChecked(newState);
                }
            });
            linearLayout.addView(ghostCell);

            fragmentView = scrollView;
            return fragmentView;
        }
    }
"""
        code = code[:-1] + werygram_menu_class + "\n}"
        print("✅ Масштабируемый AyuGram-style список меню успешно встроен!")

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    # ==========================================
    # 2. АКТИВАЦИЯ ПРЕМИУМА И ГАЛОЧКИ В СИСТЕМЕ (UserConfig)
    # ==========================================
    if os.path.exists(userconfig_path):
        with open(userconfig_path, "r", encoding="utf-8") as f:
            uc_code = f.read()
        
        # Очищаем старые инжекты, если они были
        uc_code = re.sub(r'// WG_START.*?// WG_END', '', uc_code, flags=re.DOTALL)
        
        uc_anchor = "public TLRPC.User getCurrentUser() {"
        if uc_anchor in uc_code:
            uc_injection = """public TLRPC.User getCurrentUser() {
        // WG_START
        if (currentUser != null) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                currentUser.premium = true;
            }
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_verified", false)) {
                currentUser.verified = true;
            }
        }
        // WG_END"""
            uc_code = uc_code.replace(uc_anchor, uc_injection)
            with open(userconfig_path, "w", encoding="utf-8") as f:
                f.write(uc_code)
            print("✅ Независимая логика Premium и Галочки добавлена в UserConfig!")

    # ==========================================
    # 3. ПОДМЕНА СТАТУСА ДЛЯ ОТОБРАЖЕНИЯ (MessagesController)
    # ==========================================
    if os.path.exists(messages_path):
        with open(messages_path, "r", encoding="utf-8") as f:
            mc_code = f.read()
        
        # Очищаем старые изменения
        mc_code = re.sub(r'// WG_MC_START.*?// WG_MC_END', '', mc_code, flags=re.DOTALL)
        
        mc_code = re.sub(
            r'public TLRPC\.User getUser\((Long|Integer)\s+(\w+)\)\s*\{\s*return\s+(\w+)\.get\(\2\);\s*\}',
            r'''public TLRPC.User getUser(\1 \2) {
        TLRPC.User user = \3.get(\2);
        // WG_MC_START
        if (user != null && \2 != null && \2.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                user.premium = true;
            }
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_verified", false)) {
                user.verified = true;
            }
        }
        // WG_MC_END
        return user;
    }''',
            mc_code
        )
        with open(messages_path, "w", encoding="utf-8") as f:
            mc_code = f.write(mc_code)
        print("✅ Глобальный перехватчик ID обновлен для раздельных функций!")

    print("\n🎉 СУПЕР-ПАТЧЕР ЗАВЕРШИЛ РАБОТУ! Меню готово к наполнению функциями.")

if __name__ == "__main__":
    patch_werygram_core()
