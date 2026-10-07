# G95 QA-only binary-board rendering follow-on

Exact base: diagnostic G94 `4014645d132ec676791b2aa39752db37d84abb2e` / tree `d641b145893e802265751229df9f415a3a6e2d27`, separate from canonical `a039645fcff20dfcc80acd91b709961e119f73da` / A2.8.94-test.338.1.

The bounded G94 native result found unreadable fixed labels and data digits. FOV30 zoomed the world rather than the held board; FOV60, QA OFF and cold exit were restored. Result SHA256: `5584e81dd6b16380dab0f1c9ab5dbbf098110c0696f6699429e2f589e653939d`. It provides no decoded values, arithmetic diagnosis or client pass. Screenshots and private evidence URLs are not published here.

Reviewed patch SHA256: `0804e8cb0a6619246a17ba0c6f93b7b795ba2af4504e53c6c8ff1a927ed1f94b`. Exactly three source/test paths change: the generator, focused probe test and existing binary QA geometry. Geometry now uses explicit opaque face UVs, one thick backing, separated front/rear text planes, mirrored rear labels and disjoint ivory padding beside black strokes. It removes the stacked socket/inset layers. No new texture, controller, field, guard or production pose is introduced.

All binary expressions, old controllers/attachable, BP, arithmetic/packing/schema/storage, ordinary visuals and production frame bytes remain exact. The same default-off eight-row legend and fixed 0/1 controls from G94 apply. Focused source/payload checks are not native readability acceptance; root's next isolated screenshot must establish clear controls before interpreting data. No intermediate candidate or broad suite is required for this handoff.

Use the exact diagnostic source/archive SHA, not a same-number canonical release. Latest-main collisions and source/history reconciliation, current BSM/family gates and client acceptance remain open. No rebase, merge, Release or live deployment; `client=false`, `production_ready=false`, `pending_client_acceptance`.
