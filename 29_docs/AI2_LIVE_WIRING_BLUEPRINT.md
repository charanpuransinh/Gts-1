# GTS AI-2 LIVE WIRING RECORD

This is an implementation record, not a pre-built future architecture.

- `02_instruments/`: AI-2 owns instrument, contract and expiry identity.
- `04_indicators/`: limited indicator implementation supplied in V2.
- `06_options_engine/`: supplied V2 Options + Expiry Specialist remains canonical.
- Option market data is data input; it is not duplicated inside `02_instruments`.

Flow:
`02_instruments` -> validated instrument/contract/expiry context
-> `06_options_engine` V2 specialist.

`04_indicators` remains separate and unchanged.

The V2 specialist is not regenerated, reduced, or replaced.
No second Expiry Specialist is created.
No AI-3/AI-4/Risk/Execution/Broker logic is generated at this stage.
