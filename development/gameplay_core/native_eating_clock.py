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
ASSIGNMENT=VARIABLE+' = '+SECONDS+';'
