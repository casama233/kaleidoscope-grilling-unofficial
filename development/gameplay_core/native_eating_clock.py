"""Elapsed seconds from the active native countdown and captured use duration.

The item_* duration queries in tested 1.26.52.3 are not seconds. Do not divide
by a version-specific400. Use the native bow-family countdown convention and
an owned start-event duration, so an offhand use doesn't borrow the main item
maximum. Offhand native-client acceptance remains a separate gate.
"""
PROPERTY='kaleidoscope_grilling:eat_native_ticks'
TICKS="q.property('"+PROPERTY+"')"
SECONDS=("(q.is_using_item && "+TICKS+" > 0 ? math.clamp(("+TICKS+
         " - (q.main_hand_item_use_duration - q.frame_alpha + 1.0)) / 20.0, 0, "+TICKS+" / 20.0) : 0)")
VARIABLE='v.kg_eat_seconds'
# An observing client does not own the eater's main-hand countdown. Server
# presentation ticks are an entity property, not a dynamic item property, so
# Bedrock replicates them with the eater's profile and selected hand.
ELAPSED_PROPERTY='kaleidoscope_grilling:eat_elapsed_ticks'
ELAPSED_TICKS="q.property('"+ELAPSED_PROPERTY+"')"
OBSERVER_SECONDS=("("+TICKS+" > 0 && q.property('kaleidoscope_grilling:eat_hand') > 0 ? "
                  "math.clamp("+ELAPSED_TICKS+" / 20.0, 0, "+TICKS+" / 20.0) : 0)")
VIEW_SECONDS='(c.is_first_person == 1 ? '+SECONDS+' : '+OBSERVER_SECONDS+')'
ASSIGNMENT=VARIABLE+' = '+VIEW_SECONDS+';'
