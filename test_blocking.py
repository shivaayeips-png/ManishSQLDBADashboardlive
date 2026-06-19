from collect_sql_metrics import SQLMetricsCollector

collector = SQLMetricsCollector('monitoring_config.json')
queries = collector.get_blocking_and_longrunning_queries('00670T\\MANISHPREET', 30)

print(f'Found {len(queries)} queries')
for q in queries:
    print(f"SPID {q['session_id']}: {q['query_type']} - Wait: {q['wait_time_ms']}ms - Status: {q['status']} - Blocked by: {q['blocking_session_id']}")
    print(f"  Query: {q['query_text'][:100]}")

# Made with Bob
