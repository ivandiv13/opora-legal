# opora-legal

Публичные страницы Opora: Privacy Policy, Terms of Use, Safety, Support.
Статика из markdown, хостится на GitHub Pages — так же, как `voca-legal`.

Сейчас лежит черновиком внутри репо приложения. Для публикации папку
выносим в отдельный **публичный** репозиторий `opora-legal` (Pages на
приватных репо только в платных тарифах):

```sh
cp -R legal ~/Documents/Products/opora-legal && cd ~/Documents/Products/opora-legal
git init && git add . && git commit -m "Legal and support pages"
gh repo create opora-legal --public --source=. --push
```

Потом Settings → Pages → Deploy from a branch → `main`, `/ (root)`.

## Как править

1. Правишь `src/PRIVACY.md`, `src/TERMS.md`, `src/SAFETY.md`
   (Support и главная — в конце `src/build_site.py`).
2. Значения-подстановки (`[SUPPORT_EMAIL]`, `[SUPABASE_REGION]`…) — в `CONFIG`
   наверху `src/build_site.py`. Сборка ругнётся, если что-то не заполнено.
3. `python3 -m pip install markdown && python3 src/build_site.py`
4. Коммит и пуш.

HTML генерируется — руками не править.

## Что должно совпадать с кодом

Политика описывает реальные потоки данных бэкенда (`TrueDesireBot`, `/api/app/*`).
Меняешь одно из этого — правь политику:

- модели и провайдеры (OpenRouter → Anthropic, Google; Groq для голоса);
- что уходит в LLM (имя — да; email, Apple ID, id аккаунта — нет);
- что удаляет `DELETE /api/app/me`;
- реплика согласия в онбординге — `opora/Features/Onboarding/OnboardingConsent.swift`.

## Ссылки для App Store Connect

| Поле | Значение |
|---|---|
| Privacy Policy URL | `https://ivandiv13.github.io/opora-legal/privacy/` |
| Support URL | `https://ivandiv13.github.io/opora-legal/support/` |
| License Agreement → Custom | текст из `src/TERMS.md` (или стандартный EULA Apple) |
