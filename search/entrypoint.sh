#!/bin/sh
set -e

# Create the search indexes:
# - "content" is filled by the frontend build (guides, glossary, tools, docs, pages, newsletter)
# - "forum" is filled by the backend (threads, replies)
apply_settings() {
    until curl -fsS http://localhost:7700/health >/dev/null 2>&1; do sleep 0.5; done

    for index in content forum; do
        curl -sS -X POST http://localhost:7700/indexes \
            -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
            -H "Content-Type: application/json" \
            --data "{\"uid\":\"${index}\",\"primaryKey\":\"id\"}" >/dev/null
    done

    curl -fsS -X PATCH http://localhost:7700/indexes/content/settings \
        -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
        -H "Content-Type: application/json" \
        --data '{
            "searchableAttributes":["title","description","body"],
            "filterableAttributes":["type"],
            "sortableAttributes":["date"],
            "rankingRules":["words","typo","proximity","type_rank:desc","attribute","sort","exactness"]
        }' >/dev/null

    curl -fsS -X PATCH http://localhost:7700/indexes/forum/settings \
        -H "Authorization: Bearer ${MEILI_MASTER_KEY}" \
        -H "Content-Type: application/json" \
        --data '{
            "searchableAttributes":["title","description","body"],
            "filterableAttributes":["thread_id"],
            "sortableAttributes":["date"],
            "rankingRules":["words","typo","proximity","type_rank:desc","attribute","sort","exactness"]
        }' >/dev/null
}

apply_settings &
exec /bin/meilisearch
