# Prepared oil recovery reconciliation

Draft reserves A2.8.40 for the owner-scoped oil debit recovery fix, preserving concurrently merged A2.8.38 legacy oil and A2.8.39 Java HUD work. Do not merge this draft until final runtime, complete regression and BDS receipts are attached.

The root-authored patch has passed 20 focused storage-fault regressions: prepared owner receipts before debiting, dynamic-property restoration checks, both station and stationless guards, restart persistence and terminal receipt acknowledgement. These are not native player/client acceptance.

Prior .38 work-in-progress identity was never frozen or published by this branch; public .38/.39 receipts remain authoritative. No live deployment.
