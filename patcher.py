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

    print("⏳ Тройной авто-патчер WeryGram Premium запущен...")

    # ==========================================
    # 1. МОДЕРНИЗАЦИЯ ИНТЕРФЕЙСА (SettingsActivity)
    # ==========================================
    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Полностью вычищаем все старые версии кнопки и обработчиков клика
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'public static class WeryGramSettingsActivity[\s\S]*?$', '', code, flags=re.MULTILINE)

    # Создаем нативную красивую кнопку-ссылку на наше меню WeryGram
    werygram_btn = 'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.msg_settings, "WeryGram Premium"));'

    # Находим блок "Уведомлений" (Notifications), чтобы воткнуть нашу кнопку НАД ним (в самый верх списка)
    match_notif = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match_notif:
        anchor = match_notif.group(1)
        code = code.replace(anchor, f'{werygram_btn}\n        {anchor}')
        print("✅ Кнопка WeryGram успешно установлена на самый верх первого списка настроек!")
    else:
        code = code.replace("switch (item.id) {", f"{werygram_btn}\n        switch (item.id) {{")
        print("✅ Кнопка WeryGram установлена в начало списка (резервный метод).")

    # Вшиваем обработку клика: открытие нашего нового экрана настроек (как в аюграме)
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        click_logic = """case 9999: {
            presentFragment(new WeryGramSettingsActivity());
            break;
        }"""
        code = code.replace(switch_anchor, f"{switch_anchor}\n            {click_logic}")
        print("✅ Обработчик клика изменен на открытие нового экрана меню!")

    # Внедряем класс нашего кастомного экрана в самый конец файла SettingsActivity.java (перед последней скобкой)
    code = code.strip()
    if code.endswith("}"):
        werygram_menu_class = """
    public static class WeryGramSettingsActivity extends org.telegram.ui.ActionBar.BaseFragment {
        @Override
        public android.view.View createView(android.content.Context context) {
            actionBar.setBackButtonImage(R.drawable.ic_ab_back);
            actionBar.setTitle("WeryGram Premium");
            actionBar.setActionBarMenuOnItemClick(new org.telegram.ui.ActionBar.ActionBar.ActionBarMenuOnItemClick() {
                @Override
                public void onItemClick(int id) {
                    if (id == -1) {
                        finishFragment();
                    }
                }
            });

            android.widget.LinearLayout linearLayout = new android.widget.LinearLayout(context);
            linearLayout.setOrientation(android.widget.LinearLayout.VERTICAL);
            linearLayout.setBackgroundColor(org.telegram.ui.ActionBar.Theme.getColor(org.telegram.ui.ActionBar.Theme.key_windowBackgroundWhite));

            final org.telegram.ui.Cells.TextCheckCell checkCell = new org.telegram.ui.Cells.TextCheckCell(context);
            boolean isEnabled = org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false);
            checkCell.setTextAndCheck("Включить Premium (Визуально)", isEnabled, false);
            checkCell.setBackground(org.telegram.ui.ActionBar.Theme.getSelectorDrawable(true));
            
            checkCell.setOnClickListener(new android.view.View.OnClickListener() {
                @Override
                public void onClick(android.view.View v) {
                    boolean newState = !org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false);
                    org.telegram.messenger.MessagesController.getGlobalMainSettings().edit().putBoolean("visual_premium", newState).apply();
                    checkCell.setChecked(newState);
                    
                    android.widget.Toast.makeText(getParentActivity(), newState ? "WeryGram: Visual Premium АКТИВИРОВАН! 🎉" : "WeryGram: Visual Premium ОТКЛЮЧЕН", android.widget.Toast.LENGTH_SHORT).show();
                    org.telegram.messenger.UserConfig.getInstance(currentAccount).getCurrentUser();
                }
            });

            linearLayout.addView(checkCell, new android.widget.LinearLayout.LayoutParams(android.widget.LinearLayout.LayoutParams.MATCH_PARENT, android.widget.LinearLayout.LayoutParams.WRAP_CONTENT));

            fragmentView = linearLayout;
            return fragmentView;
        }
    }
"""
        code = code[:-1] + werygram_menu_class + "\n}"
        print("✅ Собственный экран под-меню WeryGramSettingsActivity успешно внедрен!")

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    # ==========================================
    # 2. АКТИВАЦИЯ ПРЕМИУМА В СИСТЕМЕ (UserConfig)
    # ==========================================
    if os.path.exists(userconfig_path):
        with open(userconfig_path, "r", encoding="utf-8") as f:
            uc_code = f.read()
        
        if "visual_premium" not in uc_code:
            uc_anchor = "public TLRPC.User getCurrentUser() {"
            if uc_anchor in uc_code:
                uc_injection = """public TLRPC.User getCurrentUser() {
        if (currentUser != null && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
            currentUser.premium = true;
            currentUser.verified = true;
        }"""
                uc_code = uc_code.replace(uc_anchor, uc_injection)
                with open(userconfig_path, "w", encoding="utf-8") as f:
                    f.write(uc_code)
                print("✅ Логика Premium + Галочка успешно внедрены в профиль аккаунта!")

    # ==========================================
    # 3. ПОДМЕНА СТАТУСА ДЛЯ ОТОБРАЖЕНИЯ (MessagesController)
    # ==========================================
    if os.path.exists(messages_path):
        with open(messages_path, "r", encoding="utf-8") as f:
            mc_code = f.read()
        
        if "visual_premium" not in mc_code:
            mc_code = re.sub(
                r'public TLRPC\.User getUser\((Long|Integer)\s+(\w+)\)\s*\{\s*return\s+(\w+)\.get\(\2\);\s*\}',
                r'''public TLRPC.User getUser(\1 \2) {
        TLRPC.User user = \3.get(\2);
        if (user != null && \2 != null && \2.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                user.premium = true;
                user.verified = true;
            }
        }
        return user;
    }''',
                mc_code
            )
            with open(messages_path, "w", encoding="utf-8") as f:
                f.write(mc_code)
            print("✅ Системный перехватчик ID запущен. Статус Premium активен глобально!")

    print("\n🎉 ВСЕ МОДУЛИ УСПЕШНО МОДИФИЦИРОВАНЫ! Проект готов к сборке.")

if __name__ == "__main__":
    patch_werygram_core()
