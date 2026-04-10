from tools_external import search_external, summarize_external_results

#results = search_external("login issues password reset")
results = search_external("problemas com pagamento")

print("\n--- RESULTADOS ---")
for r in results:
    print(r["title"], "-", r["url"])

print("\n--- RESUMO ---")
print(summarize_external_results(results))