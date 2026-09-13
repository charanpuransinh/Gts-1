
# GTS AI-1 Wiring Map

Market Source / Simulation
  -> 01_market_data.market_data_feed
  -> data_normalizer
  -> canonical Tick/Bar/OptionQuote
  -> 01_market_data.market_data_cache
  -> 24_api.api_router
  -> 24_api.api_server
  -> 20_dashboard

Common:
  27_system/config_manager -> 24_api
  23_database/db_manager -> 23_database/schema_manager
  27_system/audit_logger -> 23_database

Downstream handoff is interface-only.
AI-1 does not bypass Risk, Strategy, Signal, Execution or Broker.
